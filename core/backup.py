"""
Backup and restore functionality for DailyWriting.

Features:
- Manual backup: Export all sessions and config to timestamped ZIP
- Automatic backup: Daily backup with rotation
- Restore: Import from backup ZIP
"""

import json
import shutil
import zipfile
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

from .storage import SESSIONS_DIR, load_all_sessions, session_to_dict, dict_to_session, save_session
from .config import CONFIG_FILE, CONFIG_DIR
from .logging_config import get_logger

logger = get_logger("backup")

BACKUP_DIR = Path.home() / ".dailywriting" / "backups"

# Backup rotation settings
KEEP_DAILY = 7      # Keep last 7 daily backups
KEEP_WEEKLY = 4     # Keep last 4 weekly backups
KEEP_MONTHLY = 12   # Keep last 12 monthly backups


def create_backup(
    output_path: Optional[Path] = None,
    include_config: bool = True
) -> Path:
    """
    Create a backup of all sessions and optionally config.

    Args:
        output_path: Custom output path. If None, saves to BACKUP_DIR with timestamp.
        include_config: Whether to include config.json in backup.

    Returns:
        Path to the created backup file.

    Raises:
        OSError: If backup cannot be created.
    """
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = BACKUP_DIR / f"dailywriting_backup_{timestamp}.zip"

    # Load all sessions
    sessions = load_all_sessions()

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add sessions
        for session in sessions:
            filename = f"sessions/{session.session_date.isoformat()}-{session.id}.json"
            data = json.dumps(session_to_dict(session), indent=2, ensure_ascii=False)
            zf.writestr(filename, data)

        # Add config if exists and requested
        if include_config and CONFIG_FILE.exists():
            zf.write(CONFIG_FILE, "config.json")

        # Add metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "session_count": len(sessions),
            "version": "1.0.0",
        }
        zf.writestr("backup_metadata.json", json.dumps(metadata, indent=2))

    logger.info("Backup created: %s (%d sessions)", output_path, len(sessions))
    return output_path


def restore_backup(
    backup_path: Path,
    restore_config: bool = False,
    merge: bool = True
) -> Tuple[int, int]:
    """
    Restore sessions from a backup file.

    Args:
        backup_path: Path to the backup ZIP file.
        restore_config: Whether to restore config.json.
        merge: If True, merge with existing sessions. If False, replace all.

    Returns:
        Tuple of (sessions_restored, sessions_skipped).

    Raises:
        ValueError: If backup file is invalid.
        OSError: If backup cannot be read.
    """
    if not backup_path.exists():
        raise ValueError(f"Backup file not found: {backup_path}")

    if not zipfile.is_zipfile(backup_path):
        raise ValueError(f"Invalid backup file: {backup_path}")

    restored = 0
    skipped = 0

    # Get existing session IDs if merging
    existing_ids = set()
    if merge:
        existing_sessions = load_all_sessions()
        existing_ids = {s.id for s in existing_sessions}

    with zipfile.ZipFile(backup_path, "r") as zf:
        # Verify it's a valid backup
        if "backup_metadata.json" not in zf.namelist():
            raise ValueError("Invalid backup: missing metadata")

        # Restore sessions
        for name in zf.namelist():
            if name.startswith("sessions/") and name.endswith(".json"):
                try:
                    data = json.loads(zf.read(name).decode("utf-8"))
                    session = dict_to_session(data)

                    if merge and session.id in existing_ids:
                        skipped += 1
                        continue

                    save_session(session)
                    restored += 1

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.warning("Failed to restore session %s: %s", name, e)
                    skipped += 1

        # Restore config if requested
        if restore_config and "config.json" in zf.namelist():
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with zf.open("config.json") as src:
                CONFIG_FILE.write_bytes(src.read())
            logger.info("Config restored from backup")

    logger.info("Restore complete: %d restored, %d skipped", restored, skipped)
    return restored, skipped


def get_backup_info(backup_path: Path) -> dict:
    """
    Get information about a backup file.

    Args:
        backup_path: Path to the backup ZIP file.

    Returns:
        Dictionary with backup metadata.
    """
    if not zipfile.is_zipfile(backup_path):
        return {"error": "Invalid backup file"}

    with zipfile.ZipFile(backup_path, "r") as zf:
        if "backup_metadata.json" in zf.namelist():
            metadata = json.loads(zf.read("backup_metadata.json").decode("utf-8"))
        else:
            # Count sessions manually for old backups
            session_count = sum(1 for n in zf.namelist()
                                if n.startswith("sessions/") and n.endswith(".json"))
            metadata = {
                "session_count": session_count,
                "version": "unknown",
            }

        metadata["file_size"] = backup_path.stat().st_size
        metadata["file_name"] = backup_path.name

        return metadata


def list_backups() -> List[Tuple[Path, dict]]:
    """
    List all available backups with their metadata.

    Returns:
        List of (path, metadata) tuples, sorted by date descending.
    """
    if not BACKUP_DIR.exists():
        return []

    backups = []
    for path in BACKUP_DIR.glob("dailywriting_backup_*.zip"):
        try:
            info = get_backup_info(path)
            backups.append((path, info))
        except Exception as e:
            logger.warning("Failed to read backup %s: %s", path, e)

    # Sort by filename (which contains timestamp) descending
    backups.sort(key=lambda x: x[0].name, reverse=True)
    return backups


def delete_backup(backup_path: Path) -> bool:
    """
    Delete a backup file.

    Args:
        backup_path: Path to the backup to delete.

    Returns:
        True if deleted, False if not found.
    """
    if backup_path.exists():
        backup_path.unlink()
        logger.info("Backup deleted: %s", backup_path)
        return True
    return False


def run_automatic_backup() -> Optional[Path]:
    """
    Run automatic backup with rotation.

    Creates a daily backup and removes old backups according to rotation policy.

    Returns:
        Path to new backup if created, None if skipped (already backed up today).
    """
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Check if we already have a backup today
    today = date.today().isoformat().replace("-", "")
    existing_today = list(BACKUP_DIR.glob(f"dailywriting_backup_{today}*.zip"))
    if existing_today:
        logger.debug("Backup already exists for today, skipping")
        return None

    # Create new backup
    backup_path = create_backup()

    # Run rotation
    _rotate_backups()

    return backup_path


def _rotate_backups():
    """Apply backup rotation policy."""
    backups = sorted(BACKUP_DIR.glob("dailywriting_backup_*.zip"), reverse=True)

    if len(backups) <= KEEP_DAILY:
        return

    today = date.today()
    to_keep = set()

    # Always keep the most recent KEEP_DAILY backups
    for backup in backups[:KEEP_DAILY]:
        to_keep.add(backup)

    # Parse dates from remaining backups
    for backup in backups[KEEP_DAILY:]:
        try:
            # Extract date from filename: dailywriting_backup_YYYYMMDD_HHMMSS.zip
            date_str = backup.stem.split("_")[2]
            backup_date = datetime.strptime(date_str, "%Y%m%d").date()

            days_old = (today - backup_date).days

            # Keep weekly backups (one per week, up to KEEP_WEEKLY weeks)
            if days_old <= KEEP_WEEKLY * 7:
                week_num = days_old // 7
                # Check if we already have a backup for this week
                week_backups = [b for b in to_keep
                                if _get_week_number(b, today) == week_num]
                if not week_backups:
                    to_keep.add(backup)
                    continue

            # Keep monthly backups (one per month, up to KEEP_MONTHLY months)
            if days_old <= KEEP_MONTHLY * 30:
                month_key = (backup_date.year, backup_date.month)
                month_backups = [b for b in to_keep
                                 if _get_month_key(b) == month_key]
                if not month_backups:
                    to_keep.add(backup)
                    continue

        except (ValueError, IndexError):
            # Can't parse date, keep it to be safe
            to_keep.add(backup)

    # Delete backups not in to_keep
    for backup in backups:
        if backup not in to_keep:
            delete_backup(backup)


def _get_week_number(backup_path: Path, today: date) -> int:
    """Get week number relative to today."""
    try:
        date_str = backup_path.stem.split("_")[2]
        backup_date = datetime.strptime(date_str, "%Y%m%d").date()
        return (today - backup_date).days // 7
    except (ValueError, IndexError):
        return -1


def _get_month_key(backup_path: Path) -> Tuple[int, int]:
    """Get (year, month) tuple from backup filename."""
    try:
        date_str = backup_path.stem.split("_")[2]
        backup_date = datetime.strptime(date_str, "%Y%m%d").date()
        return (backup_date.year, backup_date.month)
    except (ValueError, IndexError):
        return (-1, -1)
