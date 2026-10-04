from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.spell_checker import setup
from src.spell_checker.extension import (
    SpellChecker,
    damerau_levenshtein,
    split_identifier,
)


class TestSpellCheckerExtension:
    def test_setup_and_registration(self, mock_api) -> None:
        setup(mock_api)
        assert "spell_checker" in mock_api.registered_extensions
        ext = mock_api.registered_extensions["spell_checker"]
        assert isinstance(ext, SpellChecker)

    def test_commands_registration(self, mock_api) -> None:
        ext = SpellChecker(mock_api)
        ext.install()
        assert "spell_checker.check_document" in mock_api.commands.commands
        assert "spell_checker.check_selection" in mock_api.commands.commands
        assert "spell_checker.add_word" in mock_api.commands.commands
        assert "spell_checker.show_suggestions" in mock_api.commands.commands

    def test_damerau_levenshtein_distance(self) -> None:
        assert damerau_levenshtein("kitten", "kitten") == 0
        assert damerau_levenshtein("cat", "cats") == 1  # insertion
        assert damerau_levenshtein("cats", "cat") == 1  # deletion
        assert damerau_levenshtein("cat", "bat") == 1  # substitution
        assert damerau_levenshtein("ca", "ac") == 1    # transposition
        assert damerau_levenshtein("recieve", "receive") == 1  # transposition 'ie' vs 'ei'

    def test_identifier_tokenization(self) -> None:
        assert split_identifier("myVariableName") == ["my", "variable", "name"]
        assert split_identifier("parse_ssh_config") == ["parse", "ssh", "config"]
        assert split_identifier("HttpServerResponse") == ["http", "server", "response"]
        assert split_identifier("kebab-case-variable") == ["kebab", "case", "variable"]

    def test_typo_detection_and_suggestions(self, mock_api) -> None:
        ext = SpellChecker(mock_api)
        # Check text containing known typos
        text = "Please recieve the seperate document with proper lenght."
        typos = ext.check_text(text)
        typo_words = [t.word for t in typos]
        assert "recieve" in typo_words
        assert "seperate" in typo_words
        assert "lenght" in typo_words

        # Check suggestions contain corrected forms
        recieve_typo = next(t for t in typos if t.word == "recieve")
        assert "receive" in recieve_typo.suggestions

        seperate_typo = next(t for t in typos if t.word == "seperate")
        assert "separate" in seperate_typo.suggestions

        lenght_typo = next(t for t in typos if t.word == "lenght")
        assert "length" in lenght_typo.suggestions

    def test_code_keywords_and_hex_ignored(self, mock_api) -> None:
        ext = SpellChecker(mock_api)
        code_text = """
        def compute_color():
            color = 0xffffff
            return None
        """
        typos = ext.check_text(code_text)
        assert len(typos) == 0

    def test_custom_dictionary_persistence(self, mock_api, tmp_path) -> None:
        ext = SpellChecker(mock_api)
        dict_file = tmp_path / "custom_dict.txt"

        # Initially unrecognized custom word
        assert not ext.is_valid_word("antigravityx")

        # Add custom word and persist
        ext.add_word("antigravityx")
        assert ext.is_valid_word("antigravityx")
        ext.save_custom_dictionary(dict_file)

        # Create new instance and load
        ext2 = SpellChecker(mock_api)
        assert not ext2.is_valid_word("antigravityx")
        ext2.load_custom_dictionary(dict_file)
        assert ext2.is_valid_word("antigravityx")

        # Remove word
        ext2.remove_word("antigravityx")
        assert not ext2.is_valid_word("antigravityx")

    def test_statusbar_update(self, mock_api) -> None:
        ext = SpellChecker(mock_api)
        ext.install()
        ext.check_text("This has no typos.")
        assert ext.statusbar_button is not None
        assert ext.statusbar_button.text == "Spelling: OK"

        ext.check_text("This has a typoo and anothr.")
        assert "Spelling: 2 typos" in ext.statusbar_button.text

    def test_app_instance_compatibility(self, app_instance) -> None:
        setup(app_instance.api)
        assert True