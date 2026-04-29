"""
Tests for core/utils.py - text processing utilities.
"""

import pytest
from core.utils import is_cjk, mixed_word_count


class TestIsCJK:
    """Tests for is_cjk function."""

    def test_chinese_character(self):
        assert is_cjk("中") is True
        assert is_cjk("国") is True

    def test_japanese_kanji(self):
        assert is_cjk("日") is True
        assert is_cjk("本") is True

    def test_english_letter(self):
        assert is_cjk("a") is False
        assert is_cjk("Z") is False

    def test_digit(self):
        assert is_cjk("5") is False

    def test_punctuation(self):
        assert is_cjk(".") is False
        assert is_cjk("!") is False

    def test_space(self):
        assert is_cjk(" ") is False

    def test_emoji(self):
        # Emojis are outside CJK range
        assert is_cjk("😀") is False


class TestMixedWordCount:
    """Tests for mixed_word_count function."""

    def test_empty_string(self):
        assert mixed_word_count("") == 0

    def test_english_only(self):
        assert mixed_word_count("Hello world") == 2
        assert mixed_word_count("One two three four five") == 5

    def test_chinese_only(self):
        assert mixed_word_count("中国") == 2
        assert mixed_word_count("你好世界") == 4

    def test_mixed_cjk_english(self):
        # "Hello 世界" = 1 English word + 2 CJK chars = 3
        assert mixed_word_count("Hello 世界") == 3

    def test_numbers_count_as_words(self):
        assert mixed_word_count("Test 123 abc") == 3

    def test_punctuation_ignored(self):
        assert mixed_word_count("Hello, world!") == 2

    def test_multiple_spaces(self):
        assert mixed_word_count("Hello    world") == 2

    def test_newlines_and_tabs(self):
        assert mixed_word_count("Hello\nworld\tthere") == 3

    def test_mixed_sentence(self):
        # "I love 北京 and 上海" = 3 English + 4 CJK = 7
        assert mixed_word_count("I love 北京 and 上海") == 7

    def test_only_punctuation(self):
        assert mixed_word_count("...!!!???") == 0

    def test_only_spaces(self):
        assert mixed_word_count("     ") == 0

    def test_alphanumeric_mixed(self):
        # "test123abc" is one continuous run
        assert mixed_word_count("test123abc") == 1
