# -*- coding: UTF-8 -*-
"""
Font Detection
==============
@ Steam Editor Tools - Tests

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The tests for detecting and searching fonts.
"""

import os
import logging

from collections.abc import Generator
from typing_extensions import ClassVar

from rapidfuzz import process, fuzz

import pytest

import steam_editor_tools as stet


@pytest.fixture(scope="module")
def font_locator() -> Generator[stet.FontLocator, None, None]:
    """The read-only font locator shared in this module."""
    floc = stet.FontLocator(TestFontDetection.get_data_path(""))
    yield floc


class TestFontDetection:
    """The the font detection.

    Will test:
    1. Search a local font.
    2. Search a local font with scores.
    3. Use language ID or language code.
    4. Save and load `FontIndexList`.
    5. Save and load `FontLocator`.

    The test font "Roboto-Regular.ttf" is acquired from
    https://github.com/googlefonts/roboto-3-classic
    """

    root_path: ClassVar[str] = os.path.dirname(str(__file__))

    @classmethod
    def get_data_path(cls, file_name: str) -> str:
        """Return the path to a data file."""
        if not file_name:
            return os.path.join(cls.root_path, "data")
        return os.path.join(cls.root_path, "data", file_name)

    @staticmethod
    def is_same_file(path_1: str, path_2: str) -> bool:
        """Return `True` if the two paths refer to the same underlying file.

        This detects hard links and symlinks. Directories are excluded.
        """
        if not (os.path.isfile(path_1) or os.path.isfile(path_2)):
            return False
        try:
            st1 = os.stat(path_1, follow_symlinks=True)
            st2 = os.stat(path_2, follow_symlinks=True)
        except FileNotFoundError:
            return False

        return (st1.st_ino == st2.st_ino) and (st1.st_dev == st2.st_dev)

    def test_font_loading(self, font_locator: stet.FontLocator) -> None:
        """Test

        Load a local font. Because it has the highest priority, we should be able
        to know that it will definitely get searched.
        """
        log = logging.getLogger("steam_editor_tools.test")

        font_path = self.get_data_path("Roboto-Regular.ttf")

        res = font_locator.query("Roboto")
        log.info("Searched fonts: {0}".format(res))
        assert len(res) > 0
        assert res[0].get_name() == "Roboto"
        assert self.is_same_file(res[0].path, font_path)

        res = font_locator.query_best("Roboto")
        log.info("Searched best font: {0}".format(res))
        assert res is not None
        assert res.get_name() == "Roboto"
        assert self.is_same_file(res.path, font_path)

        res = font_locator.query_best_with_fallbacks(
            ["Helvetica", "Arial", "Noto Sans", "Roboto"]
        )
        log.info("Searched best font: {0}".format(res))
        assert res is not None
        name = res.get_name().strip().casefold()
        _match = process.extractOne(
            name,
            ["helvetica", "arial", "noto sans", "roboto"],
            scorer=fuzz.partial_ratio,
        )
        log.debug("Test the match of searched font name: {0}".format(_match))
        assert _match is not None and _match[1] > 99.9

    def test_font_score(self, font_locator: stet.FontLocator) -> None:
        """Test

        Test the performance of the `FontIndexList` which will provide the detailed
        scores of the fonts.
        """
        log = logging.getLogger("steam_editor_tools.test")

        font_index = font_locator.font_index
        font_path = self.get_data_path("Roboto-Regular.ttf")

        res = font_index.query("Roboto")
        log.info("Searched fonts: {0}".format(res))
        assert len(res) > 0
        assert res[0][0].get_name() == "Roboto"
        assert res[0][2] > 99.9
        assert self.is_same_file(res[0][0].path, font_path)

        res = font_index.query_best("Roboto")
        log.info("Searched best font: {0}".format(res))
        assert res is not None
        assert res[0].get_name() == "Roboto"
        assert res[2] > 99.9
        assert self.is_same_file(res[0].path, font_path)

    def test_font_lang_code(self, font_locator: stet.FontLocator) -> None:
        """Test

        Check the usage of language codes and language short names.
        """
        log = logging.getLogger("steam_editor_tools.test")

        log.info("Test language code: {0}".format(stet.FontLanguage.en))
        res = font_locator.query_best("Roboto", stet.FontLanguage.en)
        assert res is not None
        assert res.get_name(stet.FontLanguage.en) == "Roboto"

        log.info("Test language name: {0}".format("en"))
        res = font_locator.query_best("Roboto", "en")
        assert res is not None
        assert res.get_name("en") == "Roboto"

        log.info("Test language alias: {0}".format(stet.FontLanguage.en_us))
        res = font_locator.query_best("Roboto", stet.FontLanguage.en_us)
        assert res is not None
        assert res.get_name(stet.FontLanguage.en_us) == "Roboto"
        assert res.get_name("en_us") == "Roboto"

        lang_names = font_locator.langs
        log.info("Test language name list: {0}".format(lang_names))
        assert "en" in lang_names
        assert font_locator.lang_stats.get("en", 0) > 0

        lang_ids = font_locator.font_index.langs
        log.info("Test language ID list: {0}".format(lang_ids))
        assert stet.FontLanguage.en in lang_ids
        assert stet.FontLanguage.en_us in lang_ids

        lang_stats = font_locator.font_index.lang_stats
        assert lang_stats.get(stet.FontLanguage.en, 0) > 0
        assert lang_stats.get(stet.FontLanguage.en_us, 0) > 0

    def test_font_serialize_font_index(self, font_locator: stet.FontLocator) -> None:
        """Test

        Check the effectiveness of saving and loading a font index list.
        """
        log = logging.getLogger("steam_editor_tools.test")

        font_index = font_locator.font_index
        font_path = self.get_data_path("Roboto-Regular.ttf")

        with stet.utils.NamedTempFolder() as path:
            file_path = os.path.join(path, "test.json")
            font_index.to_file(file_path)

            _font_index = stet.improc.font.FontIndexList.from_file(file_path)

        res = _font_index.query_best("Roboto")
        log.info("After reloading, get the searched best font: {0}".format(res))
        assert res is not None
        assert res[0].get_name() == "Roboto"
        assert res[2] > 99.9
        assert self.is_same_file(res[0].path, font_path)

    def test_font_serialize_font_locator(self, font_locator: stet.FontLocator) -> None:
        """Test

        Check the effectiveness of saving and loading a font locator.
        """
        log = logging.getLogger("steam_editor_tools.test")

        font_path = self.get_data_path("Roboto-Regular.ttf")

        with stet.utils.NamedTempFolder() as path:
            file_path = os.path.join(path, "test.json")
            font_locator.to_file(file_path)

            _font_locator = stet.improc.FontLocator.from_file(file_path)

        res = _font_locator.query_best("Roboto")
        log.info("After reloading, get the searched best font: {0}".format(res))
        assert res is not None
        assert res.get_name() == "Roboto"
        assert self.is_same_file(res.path, font_path)
