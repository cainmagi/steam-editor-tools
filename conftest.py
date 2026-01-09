"""Pytest configurations"""

import shutil
import pytest
import logging


LATEX_EXISTS = shutil.which("latex") is not None


def pytest_configure(config: pytest.Config) -> None:
    """Pytest global configurations."""

    # Set the logger level.
    logging.getLogger("markdown_it").setLevel(logging.INFO)
    logging.getLogger("PIL").setLevel(logging.INFO)
    logging.getLogger("httpcore").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.INFO)
    logging.getLogger("fontTools").setLevel(logging.INFO)
    logging.getLogger("steam_editor_tools").setLevel(logging.DEBUG)

    # Configure test mark.
    config.addinivalue_line(
        "markers", "needs_latex: skip this test if the LaTeX command is missing"
    )


def pytest_runtest_setup(item: pytest.Item):
    """Setup stage of each test."""
    if "needs_latex" in item.keywords and not LATEX_EXISTS:
        pytest.skip("LaTeX command not available")
