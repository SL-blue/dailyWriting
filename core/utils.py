"""
Utility functions for text processing.
is_cjk:A helper function to count words in mixed CJK and English text
"""

import re

def is_cjk(char: str) -> bool:
    """
    Return True if char is a CJK (Chinese/Japanese/Korean) ideograph.
    Args:
        char: A single character string.
    Returns:
        True if the character is a CJK ideograph, False otherwise.
    """
    code = ord(char)
    # Basic CJK Unified Ideographs block
    return 0x4E00 <= code <= 0x9FFF


def mixed_word_count(text: str) -> int:
    """
    Count Chinese characters + English words as 'words'.
    - Each CJK character counts as 1.
    - Each continuous run of A-Z / a-z / 0-9 counts as 1 word.
    Args:
        text: The text to count words in.
    Returns:
        The total word count.
    """

    # Count CJK characters
    cjk_count = sum(1 for ch in text if is_cjk(ch))

    # Count English / digit words (sequences of [A-Za-z0-9]+)
    eng_words = re.findall(r"[A-Za-z0-9]+", text)
    eng_count = len(eng_words)

    return cjk_count + eng_count
