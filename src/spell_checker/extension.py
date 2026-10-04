from __future__ import annotations

import json
import os
import re
import typing
from dataclasses import dataclass, field
from pathlib import Path

from biscuit.extensions import Extension

if typing.TYPE_CHECKING:
    from biscuit.api import ExtensionsAPI


# Built-in base dictionary of common English words and programming terminology
BASE_DICTIONARY: set[str] = {
    # Common English words and forms
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "has", "had", "having",
    "i", "it", "for", "not", "on", "with", "he", "as", "you", "do", "does", "did", "done",
    "doing", "at", "this", "that", "these", "those", "but", "his", "by", "from", "they",
    "we", "say", "says", "said", "saying", "her", "she", "or", "an", "will", "would",
    "my", "one", "all", "there", "their", "theirs", "what", "so", "up", "out", "if",
    "about", "who", "get", "gets", "got", "getting", "which", "go", "goes", "went", "gone",
    "going", "me", "when", "make", "makes", "made", "making", "can", "could", "like", "likes",
    "liked", "liking", "time", "times", "no", "just", "him", "know", "knows", "knew", "known",
    "knowing", "take", "takes", "took", "taken", "taking", "people", "into", "year", "years",
    "your", "yours", "good", "some", "them", "see", "sees", "saw", "seen", "seeing", "other",
    "others", "than", "then", "now", "look", "looks", "looked", "looking", "only", "come",
    "comes", "came", "coming", "its", "over", "think", "thinks", "thought", "thinking", "also",
    "back", "after", "use", "uses", "used", "using", "two", "how", "our", "ours", "work",
    "works", "worked", "working", "first", "well", "way", "ways", "even", "new", "want",
    "wants", "wanted", "wanting", "because", "any", "give", "gives", "gave", "given", "giving",
    "day", "days", "most", "us", "great", "between", "need", "needs", "needed", "needing",
    "large", "under", "both", "every", "find", "finds", "found", "finding", "check", "checks",
    "checked", "checking", "point", "points", "same", "right", "too", "mean", "means", "meant",
    "before", "move", "moves", "moved", "moving", "much", "off", "different", "small", "number",
    "numbers", "always", "next", "early", "important", "few", "public", "bad", "able", "line",
    "lines", "word", "words", "text", "texts", "side", "sides", "spelling", "checker", "spellcheck",
    "suggest", "suggests", "suggested", "suggestion", "suggestions", "dictionary", "dictionaries",
    "receive", "separate", "length", "occurred", "definitely", "successful", "necessary",
    "environment", "accommodate", "address", "beginning", "calendar", "category", "cemetery",
    "committee", "completely", "conscious", "curiosity", "embarrass", "existence", "foreign",
    "grammar", "guarantee", "harass", "independent", "interrupt", "judgment", "knowledge",
    "license", "maintenance", "millennium", "misspell", "noticeable", "occasion", "occurrence",
    "parallel", "possession", "privilege", "pronunciation", "recommend", "reference", "rhythm",
    "schedule", "tomorrow", "twelfth", "until", "vacuum", "weather", "weird", "typo", "typos",
    "compute", "computed", "computing", "computer", "calculation", "calculate", "calculated",
    "example", "examples", "sample", "samples", "proper", "properly", "please", "here", "there",
    "where", "why", "how", "which", "whose", "whom", "test", "tests", "testing", "tested",
    "suite", "case", "cases", "assert", "asserts", "assertion", "color", "colors", "blue",
    "red", "green", "yellow", "orange", "purple", "white", "black", "gray", "grey",
    # Programming terminology
    "biscuit", "editor", "extension", "extensions", "command", "commands", "function", "functions",
    "variable", "variables", "string", "strings", "number", "numbers", "boolean", "booleans",
    "class", "classes", "method", "methods", "module", "modules", "package", "packages", "import",
    "imports", "imported", "export", "exports", "exported", "return", "returns", "returned",
    "document", "documents", "file", "files", "path", "paths", "directory", "directories",
    "project", "projects", "workspace", "workspaces", "status", "settings", "option", "options",
    "button", "buttons", "window", "windows", "display", "message", "messages", "error", "errors",
    "warning", "warnings", "info", "debug", "result", "results", "value", "values", "key", "keys",
    "data", "list", "lists", "dict", "dict", "array", "arrays", "object", "objects", "table",
    "tables", "column", "columns", "token", "tokens", "parser", "parsers", "syntax", "format",
    "formatted", "formatting", "style", "styles", "header", "headers", "footer", "content",
    "create", "created", "creating", "delete", "deleted", "remove", "removed", "update", "updated",
    "insert", "inserted", "select", "selected", "clear", "cleared", "reset", "start", "started",
    "stop", "stopped", "run", "running", "ran", "execute", "executed", "cancel", "open", "opened",
    "close", "closed", "read", "reading", "write", "writing", "save", "saved", "saving", "load",
    "loaded", "loading", "search", "replace", "match", "matched", "filter", "filtered", "sort",
    "sorted", "count", "counts", "counted", "size", "height", "width", "left", "right", "top",
    "bottom", "center", "active", "enable", "enabled", "disable", "disabled", "valid", "invalid",
    "true", "false", "none", "null", "undefined", "success", "failure", "finish", "finished",
    "complete", "completed", "pending", "running", "failed", "passed", "hello", "world", "source",
    "target", "client", "server", "request", "requests", "response", "responses", "connect",
    "connected", "disconnect", "session", "user", "users", "name", "names", "password", "auth",
    "login", "logout", "query", "queries", "param", "params", "parameter", "parameters", "payload",
    "event", "events", "handler", "handlers", "listener", "listeners", "callback", "callbacks",
    "action", "actions", "view", "views", "panel", "panels", "sidebar", "menu", "menus", "item",
    "items", "title", "titles", "label", "labels", "icon", "icons", "image", "images", "asset",
    "assets", "cache", "buffer", "stream", "reader", "writer", "channel", "socket", "http",
    "https", "url", "uri", "host", "port", "route", "router", "endpoint", "api", "rest", "json",
    "xml", "yaml", "toml", "html", "css", "code", "async", "await", "yield", "raise", "except",
    "exception", "exceptions", "try", "finally", "break", "continue", "pass", "while", "for",
    "lambda", "global", "nonlocal", "del", "struct", "enum", "interface", "type", "types",
    "const", "let", "var", "void", "static", "public", "private", "protected", "override",
    "virtual", "template", "typename", "namespace", "include", "pragma", "inline", "extern",
    "sizeof", "typedef", "goto", "switch", "case", "default", "catch", "throw", "volatile",
    "print", "println", "fmt", "stdout", "stderr", "stdin", "len", "range",
}

# Code language keywords and common programming tokens to always ignore
COMMON_CODE_KEYWORDS: set[str] = {
    "def", "fn", "fun", "func", "function", "var", "let", "const", "val", "mut",
    "int", "float", "double", "char", "str", "bool", "i32", "i64", "u32", "u64",
    "usize", "isize", "f32", "f64", "byte", "rune", "string", "nil", "null", "none",
    "undefined", "self", "this", "super", "cls", "true", "false", "import", "from",
    "export", "package", "namespace", "class", "struct", "enum", "interface", "type",
    "trait", "impl", "return", "yield", "await", "async", "if", "else", "elif",
    "switch", "case", "match", "for", "while", "loop", "in", "is", "break", "continue",
    "try", "catch", "except", "finally", "throw", "raise", "assert", "with", "as",
    "new", "delete", "typeof", "instanceof", "sizeof", "static", "public", "private",
    "protected", "internal", "abstract", "final", "const", "readonly", "override",
    "print", "println", "fmt", "stdout", "stderr", "stdin", "len", "range",
}


def damerau_levenshtein(s1: str, s2: str) -> int:
    """Compute Damerau-Levenshtein distance between two strings."""
    len1, len2 = len(s1), len(s2)
    if s1 == s2:
        return 0
    if not len1:
        return len2
    if not len2:
        return len1

    d: dict[tuple[int, int], int] = {}
    for i in range(-1, len1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len2 + 1):
        d[(-1, j)] = j + 1

    for i in range(len1):
        for j in range(len2):
            cost = 0 if s1[i] == s2[j] else 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,        # deletion
                d[(i, j - 1)] + 1,        # insertion
                d[(i - 1, j - 1)] + cost,  # substitution
            )
            # transposition
            if i > 0 and j > 0 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[(i - 2, j - 2)] + cost)

    return d[(len1 - 1, len2 - 1)]


def split_identifier(identifier: str) -> list[str]:
    """Split identifier by camelCase, PascalCase, snake_case, and kebab-case."""
    if not identifier:
        return []
    cleaned = re.sub(r"[^a-zA-Z]", "_", identifier)
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", cleaned)
    s2 = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s1)
    parts = s2.split("_")
    return [p.lower() for p in parts if len(p) > 1]


@dataclass
class TypoMatch:
    word: str
    line: int
    col_start: int
    col_end: int
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "line": self.line,
            "col_start": self.col_start,
            "col_end": self.col_end,
            "suggestions": self.suggestions,
        }


class SpellChecker(Extension):
    """Source code typo detector, camelCase tokenizer, and Levenshtein suggestion generator."""

    def __init__(self, api: ExtensionsAPI) -> None:
        super().__init__(api)
        self.api = api
        self.dictionary: set[str] = set(BASE_DICTIONARY)
        self.custom_words: set[str] = set()
        self.custom_dict_path: Path | None = None
        self.statusbar_button = None
        self.last_typos: list[TypoMatch] = []

        # Only bind custom_dict_path if active_directory is a real directory path (not MagicMock)
        ws_dir = getattr(getattr(self.api, "base", None), "active_directory", None)
        if isinstance(ws_dir, (str, Path)):
            try:
                p = Path(ws_dir)
                if p.is_dir():
                    self.custom_dict_path = p / ".biscuit" / "dictionary.txt"
                    self.load_custom_dictionary()
            except Exception:
                pass

        if hasattr(self.api, "logger") and self.api.logger:
            self.api.logger.info("Spell Checker extension initialised.")

    def add_word(self, word: str, persist: bool = False) -> None:
        """Add custom domain word to ignore dictionary."""
        w = word.strip().lower()
        if w:
            self.custom_words.add(w)
            if persist and self.custom_dict_path:
                self.save_custom_dictionary()

    def remove_word(self, word: str) -> None:
        """Remove word from custom dictionary."""
        w = word.strip().lower()
        self.custom_words.discard(w)
        if self.custom_dict_path:
            self.save_custom_dictionary()

    def is_valid_word(self, word: str) -> bool:
        """Check if a word is spelled correctly or explicitly allowed."""
        w = word.strip().lower()
        if not w or len(w) <= 1:
            return True
        if w in self.dictionary or w in self.custom_words or w in COMMON_CODE_KEYWORDS:
            return True
        # If word ends in 's', 'es', 'ed', or 'ing', check stem
        if w.endswith("s") and w[:-1] in self.dictionary:
            return True
        if w.endswith("es") and w[:-2] in self.dictionary:
            return True
        if w.endswith("ed") and w[:-2] in self.dictionary:
            return True
        if w.endswith("ing") and w[:-3] in self.dictionary:
            return True
        return False

    def suggest_corrections(self, word: str, max_suggestions: int = 5) -> list[str]:
        """Generate ranked spelling suggestions using Damerau-Levenshtein distance."""
        w = word.strip().lower()
        if not w:
            return []

        all_candidates = self.dictionary | self.custom_words
        scored: list[tuple[int, int, str]] = []

        len_w = len(w)
        for cand in all_candidates:
            if abs(len(cand) - len_w) > 2:
                continue

            dist = damerau_levenshtein(w, cand)
            if dist <= 2:
                scored.append((dist, abs(len(cand) - len_w), cand))

        scored.sort(key=lambda x: (x[0], x[1], x[2]))
        return [cand for _, _, cand in scored[:max_suggestions]]

    def tokenize_line(self, line: str, line_no: int = 1) -> list[tuple[str, int, int]]:
        """Tokenize words from a line, splitting camelCase and snake_case tokens with column offsets."""
        tokens: list[tuple[str, int, int]] = []
        for match in re.finditer(r"\b[A-Za-z][A-Za-z0-9_'-]*\b", line):
            raw_token = match.group(0)
            start_col = match.start()

            # Ignore hex literals
            if raw_token.lower().startswith("0x"):
                continue

            sub_words = split_identifier(raw_token)
            if not sub_words:
                sub_words = [raw_token.lower()]

            curr_pos = start_col
            for sw in sub_words:
                sub_idx = raw_token.lower().find(sw, curr_pos - start_col)
                if sub_idx != -1:
                    sw_start = start_col + sub_idx
                else:
                    sw_start = curr_pos
                sw_end = sw_start + len(sw)
                tokens.append((sw, sw_start, sw_end))
                curr_pos = sw_end
        return tokens

    def check_text(self, text: str) -> list[TypoMatch]:
        """Scan multi-line text and return list of typo matches."""
        lines = text.splitlines()
        typos: list[TypoMatch] = []

        for line_no, line in enumerate(lines, start=1):
            if line.strip().startswith(("http://", "https://", "import ", "from ")):
                continue

            for word, col_start, col_end in self.tokenize_line(line, line_no):
                if not self.is_valid_word(word):
                    suggestions = self.suggest_corrections(word)
                    typos.append(
                        TypoMatch(
                            word=word,
                            line=line_no,
                            col_start=col_start,
                            col_end=col_end,
                            suggestions=suggestions,
                        )
                    )

        self.last_typos = typos
        self.update_statusbar()
        return typos

    def check_file(self, file_path: str | Path) -> list[TypoMatch]:
        """Read and spell-check a file on disk."""
        path_obj = Path(file_path).resolve()
        if not path_obj.is_file():
            return []
        try:
            with open(path_obj, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return self.check_text(content)
        except Exception as e:
            if hasattr(self.api, "logger") and self.api.logger:
                self.api.logger.warning(f"Spell Checker failed reading {file_path}: {e}")
            return []

    def load_custom_dictionary(self, dict_path: str | Path | None = None) -> None:
        """Load user custom words from disk."""
        target = Path(dict_path) if dict_path else self.custom_dict_path
        if not target or not target.is_file():
            return
        try:
            with open(target, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip().lower()
                    if word and not word.startswith("#"):
                        self.custom_words.add(word)
        except Exception:
            pass

    def save_custom_dictionary(self, dict_path: str | Path | None = None) -> None:
        """Persist custom words to disk."""
        target = Path(dict_path) if dict_path else self.custom_dict_path
        if not target:
            return
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                for word in sorted(self.custom_words):
                    f.write(f"{word}\n")
        except Exception:
            pass

    def update_statusbar(self) -> None:
        """Update spelling statusbar indicator."""
        if not self.statusbar_button:
            return
        typo_count = len(self.last_typos)
        text = f"Spelling: {typo_count} typo{'s' if typo_count != 1 else ''}" if typo_count else "Spelling: OK"
        if hasattr(self.statusbar_button, "change_text"):
            self.statusbar_button.change_text(text)
        elif hasattr(self.statusbar_button, "set_text"):
            self.statusbar_button.set_text(text)

    def check_active_document(self) -> list[TypoMatch]:
        """Command handler: Check spelling in current active document."""
        editor = getattr(getattr(self.api, "editors", None), "active_editor", None)
        text_widget = getattr(editor, "text", None) or getattr(getattr(editor, "content", None), "text", None)
        if text_widget and hasattr(text_widget, "get"):
            content = text_widget.get("1.0", "end-1c")
            typos = self.check_text(content)
            if hasattr(self.api, "notifications") and self.api.notifications:
                self.api.notifications.info(f"Spell Checker: Found {len(typos)} typos.")
            return typos

        path = getattr(editor, "path", None)
        if path:
            return self.check_file(path)
        return []

    def check_selection(self) -> list[TypoMatch]:
        """Command handler: Check spelling in active editor selection."""
        editor = getattr(getattr(self.api, "editors", None), "active_editor", None)
        text_widget = getattr(editor, "text", None) or getattr(getattr(editor, "content", None), "text", None)
        if text_widget and hasattr(text_widget, "tag_ranges"):
            try:
                ranges = text_widget.tag_ranges("sel")
                if ranges:
                    selected_text = text_widget.get(ranges[0], ranges[1])
                    return self.check_text(selected_text)
            except Exception:
                pass
        return []

    def install(self) -> None:
        """Register commands and statusbar item for Spell Checker."""
        if hasattr(self.api, "commands") and hasattr(self.api.commands, "register_command"):
            self.api.commands.register_command("spell_checker.check_document", self.check_active_document)
            self.api.commands.register_command("spell_checker.check_selection", self.check_selection)
            self.api.commands.register_command("spell_checker.add_word", self.add_word)
            self.api.commands.register_command(
                "spell_checker.show_suggestions",
                lambda word: self.suggest_corrections(word) if word else []
            )

        if hasattr(self.api, "statusbar") and hasattr(self.api.statusbar, "add_button"):
            try:
                self.statusbar_button = self.api.statusbar.add_button(
                    text="Spelling: OK",
                    callback=self.check_active_document,
                    description="Spell Checker: Check spelling in active file",
                )
                if hasattr(self.statusbar_button, "show"):
                    self.statusbar_button.show()
            except Exception:
                pass

        if hasattr(self.api, "logger") and self.api.logger:
            self.api.logger.info("Spell Checker installed successfully.")
