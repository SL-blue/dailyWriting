# DailyWriting

A distraction-free writing app for macOS that helps you build a daily writing habit.

## Features

- **Free Writing Mode** - Write without prompts, just you and your thoughts
- **AI-Powered Prompts** - Get creative writing prompts from Google Gemini or Anthropic Claude
- **Streak Tracking** - Build consistency with daily streak counters
- **Statistics Dashboard** - Track your progress with detailed metrics
- **Session History** - Search, filter, and review past writing sessions
- **Export Options** - Export to Markdown, TXT, JSON, or HTML
- **Backup & Restore** - Keep your writing safe with automatic backups
- **Dark Mode** - Easy on the eyes for late-night writing sessions

## Screenshots

*Coming soon*

## Requirements

- macOS 10.15 or later
- Python 3.9+ (for development)
- API key for AI prompts (optional):
  - Google Gemini API key, OR
  - Anthropic Claude API key

## Installation

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/dailyWriting.git
   cd dailyWriting
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Set up API keys for AI prompts:

   Add the following to your `~/.zshrc` (or `~/.bashrc`):
   ```bash
   # For Google Gemini (default provider)
   export GOOGLE_API_KEY="your-gemini-key"

   # For Anthropic Claude (alternative provider)
   export ANTHROPIC_API_KEY="your-claude-key"
   ```

   Then reload your shell configuration:
   ```bash
   source ~/.zshrc
   ```

   Or simply open a new terminal window.

   **Verify your keys are set:**
   ```bash
   echo $GOOGLE_API_KEY
   echo $ANTHROPIC_API_KEY
   ```

   > **Note**: The app will use fallback prompts if no API keys are configured.

5. Run the application:
   ```bash
   python main.py
   ```

### Building Standalone App

To create a standalone macOS application:

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Build the app
./scripts/build_app.sh

# Run the app
open dist/DailyWriting.app
```

## Usage

### Starting a Session

1. **Free Writing**: Click "FREE WRITING" to start writing without a prompt
2. **AI Prompt**: Click "RANDOM TOPIC (AI)" to open the layered tag selector and get an AI-generated writing prompt

### The Tag System

The "RANDOM TOPIC (AI)" dialog organizes prompt configuration into **four layers**. Each layer answers a different question about the prompt and contributes a different kind of constraint to the AI.

| Layer | Question it answers | Categories |
|---|---|---|
| **Territory** | What world are we in? | Genre, Register |
| **Emotional Weather** | What does the scene feel like? | Mood, Tension |
| **Craft** | How is it written? | Perspective, Temporal stance, Structural move, Form |
| **Seed** | What's the spark? | Situation, Object role, Setting role, Time role |

For each layer you choose one of three states:

- **OFF** — the layer contributes nothing to the prompt.
- **RANDOM** — the system picks one tag from one randomly-chosen category in the layer at generation time. Hit *Generate* twice and you'll get different prompts even with the same settings.
- **PICK** — you choose specific tags. A picker reveals chips grouped by category; toggle as many as you want.

**Default state**: Seed is set to RANDOM, all other layers are OFF. This gives you a varied seed prompt every time without needing to configure anything.

**Tips**

- Start with the default and just keep clicking *Generate* — the random Seed alone produces a wide range of prompts.
- Set Territory to RANDOM when you want a different *kind* of writing each session (literary one day, noir the next).
- Use PICK on Craft when you want to practice a specific technique (e.g. "second person + opens with dialogue").
- The system intentionally avoids overused defaults (candles, rain, ticking clocks, music boxes, etc.) to push the model away from cliché imagery.

### Navigation

- **Calendar View** (⌘1): See your writing activity by month
- **Session List** (⌘2): Browse and search all past sessions
- **Statistics** (⌘3): View your writing metrics and progress

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| ⌘N | New free writing session |
| ⇧⌘N | New AI prompt session |
| ⌘1 | Calendar view |
| ⌘2 | Session list |
| ⌘3 | Statistics |
| ⌘, | Settings |
| ⌘E | Export session |
| ⇧⌘E | Export all sessions |
| ⌘Q | Quit |

### Settings

Access settings via **DailyWriting → Settings** (⌘,) or click the **⚙ SETTINGS** button in the sidebar:

- **General**: Default writing mode, autosave interval, daily word goal
- **AI**: Provider selection (Gemini/Claude), model configuration
- **Export**: Default format, metadata inclusion
- **Appearance**: Font size, line spacing

### Data Storage

Your writing is stored locally:
- **Sessions**: `data/sessions/` (JSON files by date)
- **Settings**: `~/.dailywriting/config.json`
- **Backups**: `~/.dailywriting/backups/`
- **Logs**: `~/.dailywriting/logs/`

## Development

### Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/dailyWriting.git
cd dailyWriting
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov=ui --cov-report=html
```

### Project Structure

```
dailyWriting/
├── main.py              # Application entry point
├── core/                # Business logic layer
│   ├── models.py        # Data models (WritingSession)
│   ├── storage.py       # Session persistence
│   ├── statistics.py    # Stats calculations
│   ├── search.py        # Search and filter
│   ├── export.py        # Export functionality
│   ├── backup.py        # Backup/restore
│   ├── config.py        # Settings management
│   └── topic_generator.py  # AI prompt generation
├── ui/                  # PyQt6 UI layer
│   ├── main_window.py   # Main application window
│   ├── session_view.py  # Writing session UI
│   ├── calendar_view.py # Calendar display
│   ├── history_view.py  # Session list with search
│   ├── stats_view.py    # Statistics dashboard
│   └── settings_dialog.py  # Preferences UI
├── data/                # Local data storage
│   ├── sessions/        # Writing sessions (JSON)
│   └── topics/          # Fallback prompts
├── tests/               # Test suite
├── scripts/             # Build scripts
└── resources/           # App resources (icons)
```

### Architecture

The app follows a layered architecture:

- **Core Layer** (`core/`): Business logic with no UI dependencies
- **UI Layer** (`ui/`): PyQt6 widgets and views
- **Data Layer**: JSON-based persistence in `data/sessions/`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- AI prompts powered by [Google Gemini](https://ai.google.dev/) and [Anthropic Claude](https://www.anthropic.com/)
- Packaged with [PyInstaller](https://pyinstaller.org/)
