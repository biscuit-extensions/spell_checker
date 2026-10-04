from __future__ import annotations

import typing

from .extension import SpellChecker

if typing.TYPE_CHECKING:
    from biscuit.api import ExtensionsAPI


def setup(api: "ExtensionsAPI") -> None:
    """Entrypoint for Biscuit to load the extension."""
    api.register("spell_checker", SpellChecker(api))
