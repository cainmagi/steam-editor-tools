# -*- coding: UTF-8 -*-
"""
Achievement Data
================
@ Steam Editor Tools - Steam Information: Data

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The data structures used to retrieve the achievement information.
"""

import os
from collections.abc import Sequence
from typing_extensions import Self

from pydantic import BaseModel, Field, ConfigDict

import httpx
from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement

from rapidfuzz.fuzz import ratio
from rapidfuzz.process import extractOne

from .appdata import AppQuerySimple

__all__ = ("Achievement", "AchievementIconName", "AchievementList")


class Achievement(BaseModel):
    """The information of an achievement."""

    model_config = ConfigDict(extra="ignore")

    name: str
    """Achievement display name."""

    description: str = ""
    """Description of the achievement. If extra user profiles are not provided, the
    description of a hidden achievement will not be detected."""

    icon_url_locked: str | None = None
    """Icon shown when achievement is locked. Need to be detected from a user profile
    when the achievement is locked."""

    percent: float | None = None
    """The percent of users who have unlocked this acheivement. Will be `None` if the
    value cannot be detected."""

    icon_url: str
    """Icon shown when achievement is unlocked."""

    is_hidden: bool | None = None
    """A flag showing whether the achievement is hidden/spoiler-related. Need to be
    detected from extra user profiles. If this information is unknown, will be
    `None`."""


class AchievementIconName(BaseModel):
    """The file names of an achievement icon.

    This name is the name (not the full path) of the file produced by
    `AchievementList.save_icons()`.
    """

    model_config = ConfigDict(extra="ignore")

    id: int
    """The index of the achievement."""

    name: str
    """The file name of the icon."""

    name_locked: str
    """The file name of the icon in the locked status."""


class AchievementList(BaseModel):
    """The list of achievements."""

    model_config = ConfigDict(extra="ignore")

    achievements: list[Achievement] = Field(default_factory=list)
    """The list of detected achievements."""

    steam_appid: int
    """The app ID. It specifies the game where the achievements belong."""

    lang: str = "english"
    """The language of the parsed achievments."""

    @property
    def names(self) -> list[str]:
        """A mapping from all achievement names to their indicies."""
        return [ach.name for ach in self.achievements]

    @staticmethod
    def _get_achievement(bs_node: PageElement) -> Achievement:
        """(Private) Parse the acheivement information from a page node."""
        node = bs_node.find_next("div", attrs={"class": "achieveImgHolder"})
        if node is None:
            raise ValueError("Unable to detect the achievement icon.")
        img = node.find_next("img")
        if img is None or not isinstance(img, Tag):
            raise ValueError("Unable to detect the achievement icon.")
        icon_url = img.attrs["src"]
        node = bs_node.find_next("div", attrs={"class": "achievePercent"})
        if node is not None:
            _percent = node.text.replace("%", "").strip().replace(" ", "")
            try:
                percent = float(_percent)
            except ValueError:
                percent = None
        else:
            percent = None
        node = bs_node.find_next("div", attrs={"class": "achieveTxt"})
        if node is None:
            raise ValueError("Unable to detect the achievement information.")
        _title = node.find_next("h3")
        if _title is None:
            raise ValueError("Unable to detect the achievement title.")
        title = _title.text.strip()
        _descr = node.find_next("h5")
        descr = _descr.text.strip() if _descr is not None else ""

        return Achievement.model_validate(
            dict(name=title, description=descr, icon_url=icon_url, percent=percent)
        )

    def _merge_achievement(self, idx: int, ach: Achievement) -> None:
        """(Private) Merge the acheivement parsed from the user profile into the curent
        list."""
        _ach = self.achievements[idx]
        if _ach.icon_url != ach.icon_url:
            _ach.is_hidden = False
        if (not _ach.icon_url_locked) and _ach.icon_url != ach.icon_url:
            _ach.icon_url_locked = ach.icon_url
        if not _ach.description and ach.description:
            _ach.description = ach.description
            _ach.is_hidden = True

    @classmethod
    def from_app(
        cls,
        app: int | AppQuerySimple,
        lang: str = "english",
        extra_user_profiles: Sequence[str] | None = None,
    ) -> Self:
        """Detect the achievements from a Steam game.

        Arguments
        ---------
        app: `int | AppQuerySimple`
            The steam app ID or the query object. It is used for locating the game
            achievement page.

        lang: str
            The language used for accessing the achievement profile.

        extra_user_profiles: `Sequence[str] | None`
            A list of extra Steam user profile names. If provided, will attempt to
            parse more achievement information from the given profiles. Ideally,
            a profile with all achievements unlocked and another profile with all
            achievements locked will yield the full information.

        Returns
        -------
        #1: `AchievementList`
            The achievement list detected from the app.
        """
        app_id = int(app.id if isinstance(app, AppQuerySimple) else app)
        with httpx.Client() as client:
            url = "https://steamcommunity.com/stats/{0}/achievements/".format(app_id)
            params = {"l": lang}
            r = client.get(url, params=params, timeout=10)
            r.raise_for_status()
            html = r.text

        soup = BeautifulSoup(html, "html.parser")

        rows = soup.select("div.achieveRow")
        if not rows:
            raise ValueError("Fail to detect achievements from the HTML page.")

        achievments: list[Achievement] = []
        for row in rows:
            try:
                ach = cls._get_achievement(bs_node=row)
            except ValueError:
                pass
            else:
                achievments.append(ach)

        data = cls(achievements=achievments, steam_appid=app_id, lang=lang)
        if extra_user_profiles:
            for profile in extra_user_profiles:
                data.add_extra_info(profile)
        return data

    def add_extra_info(self, user_profile: str) -> None:
        with httpx.Client() as client:
            url = "https://steamcommunity.com/id/{0}/stats/{1}".format(
                user_profile, self.steam_appid
            )
            params = {"tab": "achievements", "l": self.lang}
            r = client.get(url, params=params, timeout=10)
            r.raise_for_status()
            html = r.text

        soup = BeautifulSoup(html, "html.parser")

        rows = soup.select("div.achieveRow")
        if not rows:
            raise ValueError("Fail to detect achievements from the HTML page.")

        names = self.names
        seen_names: list[str] = []
        for row in rows:
            try:
                ach = self._get_achievement(bs_node=row)
            except ValueError:
                pass
            else:
                item = extractOne(
                    ach.name, choices=names, scorer=ratio, score_cutoff=90
                )
                if item is None:
                    continue
                self._merge_achievement(idx=item[-1], ach=ach)
                seen_names.append(ach.name)

        for idx, name in enumerate(names):
            item = extractOne(name, choices=seen_names, scorer=ratio, score_cutoff=95)
            if item is None:
                self.achievements[idx].is_hidden = True

    @staticmethod
    def _download_icon(client: httpx.Client, url: str, out_path: str) -> None:
        """(Private) Download the icon file."""
        response = client.get(url, timeout=10)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            return None
        data = response.content
        with open(out_path, "wb") as fobj:
            fobj.write(data)

    def get_icon_names(self) -> list[AchievementIconName]:
        """Get the list of achievement icon names.

        Arguments
        ---------
        out_dir: `str | PathLike[str]`
            The path to the directory where the icons will be savd.

        Returns
        -------
        #1: `list[AchievementIconName]`
            The list of achievement icon names. These names will be used by
            `self.save_icons(...)`.
        """
        icon_unlocked_files: list[str] = []
        seen_unlocked_files: dict[str, int] = dict()
        icon_locked_files: list[str] = []
        seen_locked_files: dict[str, int] = dict()
        for ach in self.achievements:
            url = ach.icon_url
            if url not in seen_unlocked_files:
                icon_unlocked_files.append(url)
                seen_unlocked_files[url] = len(icon_unlocked_files)
            url = ach.icon_url_locked
            if url and url not in seen_locked_files:
                icon_locked_files.append(url)
                seen_locked_files[url] = len(icon_locked_files)
        name_list: list[AchievementIconName] = []
        n_digits = len(str(max(len(icon_unlocked_files), len(icon_locked_files))))
        template = "{{0:0{0}d}}".format(n_digits)
        for ach_id, ach in enumerate(self.achievements):
            idx_unlock = seen_unlocked_files.get(ach.icon_url, -1)
            name_unlock = template.format(idx_unlock) if idx_unlock > -1 else ""
            idx_locked = (
                seen_locked_files.get(ach.icon_url_locked, -1)
                if ach.icon_url_locked
                else -1
            )
            name_locked = (
                template.format(idx_locked) + "_locked" if idx_locked > -1 else ""
            )
            name_list.append(
                AchievementIconName(
                    id=ach_id, name=name_unlock, name_locked=name_locked
                )
            )
        return name_list

    def save_icons(self, out_dir: str | os.PathLike[str]) -> list[AchievementIconName]:
        """Save the acheivement icons in a folder.

        Arguments
        ---------
        out_dir: `str | PathLike[str]`
            The path to the directory where the icons will be savd.

        Returns
        -------
        #1: `list[AchievementIconName]`
            The list of saved achievement icon names. It provides a mapping from an
            achievement to the saved file name.
        """
        name_list = self.get_icon_names()
        os.makedirs(out_dir, exist_ok=True)
        with httpx.Client() as client:
            for idx, ach in enumerate(self.achievements):
                ach_f = name_list[idx]
                path = (
                    os.path.join(
                        out_dir, ach_f.name + os.path.splitext(ach.icon_url)[-1].strip()
                    )
                    if ach_f.name and ach.icon_url
                    else None
                )
                if path and (not os.path.isfile(path)):
                    self._download_icon(client, ach.icon_url, path)
                if not ach.icon_url_locked:
                    continue
                path = (
                    os.path.join(
                        out_dir,
                        ach_f.name_locked
                        + os.path.splitext(ach.icon_url_locked)[-1].strip(),
                    )
                    if ach_f.name_locked
                    else None
                )
                if path and (not os.path.isfile(path)):
                    self._download_icon(client, ach.icon_url_locked, path)
        return name_list
