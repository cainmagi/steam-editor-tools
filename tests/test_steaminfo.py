# -*- coding: UTF-8 -*-
"""
Steam Information
=================
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
The tests for fetching Steam information by API access.
"""

import os
import logging

from typing_extensions import ClassVar

import numpy as np
from rapidfuzz.fuzz import partial_ratio as fuzz_partial_ratio
from skimage.metrics import structural_similarity

import steam_editor_tools as stet


class TestSteamInfo:
    """The the text processing of BBCode data.

    Will test:
    1. Search a game by its English name.
    2. Search a game by its Simplified Chinese name.
    3. Query the full details of a game.
    4-5. Compare header images of the same game in different languages.
    """

    root_path: ClassVar[str] = os.path.dirname(str(__file__))

    @classmethod
    def get_data_path(cls, file_name: str) -> str:
        """Return the path to a data file."""
        return os.path.join(cls.root_path, "data", file_name)

    @staticmethod
    def ssim(img_1: stet.ImageSingle, img_2: stet.ImageSingle) -> float:
        """Calculate SSIM between two images."""
        if img_1.width > 20:
            img_1 = img_1.resize((20, None))
        if img_1.size != img_2.size:
            img_2 = img_2.resize(img_1.size)
        _img_1 = np.asarray(img_1.add_background().convert("RGB").img, dtype=np.uint8)
        _img_2 = np.asarray(img_2.add_background().convert("RGB").img, dtype=np.uint8)
        _value: list[float] = []
        for c in range(_img_1.shape[-1]):
            _val = structural_similarity(_img_1[..., c], _img_2[..., c])
            assert isinstance(_val, float)
            _value.append(_val)
        return float(np.mean(_value))

    def test_info_search_app_eng_name(self) -> None:
        """Test

        Search the app information by its English name.
        """
        log = logging.getLogger("steam_editor_tools.test")
        log.info('Search "Zero no Kiseki Kai"')
        info = stet.query_app_by_name_simple("Zero no Kiseki Kai")
        assert len(info) > 0
        log.debug("Searched full name: {0}".format(info[0].name))
        assert info[0].id == 1457520
        log.info("Searched ID: {0}.".format(info[0].id))

    def test_info_search_app_chn_name(self) -> None:
        """Test

        Search the app information by its Chinese name.
        """
        log = logging.getLogger("steam_editor_tools.test")
        log.info('Search "零之轨迹：改"')
        info = stet.query_app_by_name_simple("零之轨迹：改", lang="schinese", cc="cn")
        assert len(info) > 0
        log.debug("Searched full name: {0}".format(info[0].name))
        assert info[0].id == 1457520
        log.info("Searched ID: {0}.".format(info[0].id))

    def test_info_get_app_full_info(self) -> None:
        """Test

        Get the app detailed information its ID.
        """
        log = logging.getLogger("steam_editor_tools.test")
        log.info('Get details of "Zero no Kiseki Kai" (1457520)')
        info = stet.get_app_details(1457520)
        assert info is not None
        log.info("Game full name: {0}".format(info.name))
        assert info.steam_appid == 1457520
        assert (
            fuzz_partial_ratio(
                "Set in the autonomous region of Crossbell, the epic RPG Zero no "
                "Kiseki: Kai,",
                info.short_description,
            )
            > 90.0
        )
        log.info("Game information: {0}.".format(info.short_description))

    def test_info_get_app_image_same(self) -> None:
        """Test

        Get the app detailed information its ID.

        This game uses the same header images for different languages.
        Therefore, the fetched header images are expected to be the same.
        """
        log = logging.getLogger("steam_editor_tools.test")
        log.info("Get the app ID of: {0}".format("Hollow Knight"))
        info = stet.query_app_by_name_simple("Hollow Knight")
        assert len(info) > 0
        app = info[0]
        log.info("Game ID: {0}".format(app.id))
        assert app.id == 367520

        app_eng = stet.get_app_details(app)
        assert app_eng is not None
        log.info("Get game header image (English): {0}".format(app_eng.capsule_image))
        img_eng = app_eng.get_header_image("capsule")
        assert img_eng is not None

        app_cn = stet.get_app_details(app, lang="schinese", cc="cn")
        assert app_cn is not None
        log.info("Get game header image (Chinese): {0}".format(app_eng.capsule_image))
        img_cn = app_cn.get_header_image("capsule")
        assert img_cn is not None

        score = self.ssim(stet.ImageSingle(img_eng), stet.ImageSingle(img_cn))
        log.info("SSIM between English and Chinese header images: {0}".format(score))
        assert score > 0.95

    def test_info_get_app_image_different(self) -> None:
        """Test

        Get the app detailed information its ID.

        This game contains different header images for different languages.
        Therefore, the fetched header images are expected to be different.
        """
        log = logging.getLogger("steam_editor_tools.test")
        log.info(
            "Get the app ID of: {0}".format(
                "TouHou Makuka Sai ~ Fantastic Danmaku Festival Part III"
            )
        )
        info = stet.query_app_by_name_simple(
            "TouHou Makuka Sai ~ Fantastic Danmaku Festival Part III"
        )
        assert len(info) > 0
        app = info[0]
        log.info("Game ID: {0}".format(app.id))
        assert app.id == 2877170

        app_eng = stet.get_app_details(app)
        assert app_eng is not None
        log.info("Get game header image (English): {0}".format(app_eng.capsule_image))
        img_eng = app_eng.get_header_image("capsule")
        assert img_eng is not None

        app_cn = stet.get_app_details(app, lang="schinese", cc="cn")
        assert app_cn is not None
        log.info("Get game header image (Chinese): {0}".format(app_eng.capsule_image))
        img_cn = app_cn.get_header_image("capsule")
        assert img_cn is not None

        score = self.ssim(stet.ImageSingle(img_eng), stet.ImageSingle(img_cn))
        log.info("SSIM between English and Chinese header images: {0}".format(score))
        assert score < 0.95 and score > 0.4
