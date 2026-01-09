# -*- coding: UTF-8 -*-
"""
Font
=====
@ Steam Editor Tools - Image Processing

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The implementation of `FontLocator`. Allow users to search font efficiently and
flexibly.
"""

import os
import sys
import io
import enum
import collections
import collections.abc
import itertools
import functools
import contextlib
import importlib
import importlib.util

from typing import Any, IO
from typing_extensions import Literal, Self, overload

from pydantic import BaseModel, Field

from fontTools.ttLib import TTFont, TTCollection
from rapidfuzz import process, fuzz

from PIL.ImageFont import FreeTypeFont


__all__ = ("FontLanguage", "FontNameInfo", "FontInfo", "FontIndexList", "FontLocator")


class FontLanguage(enum.IntEnum):
    """Support LCID mapping from language short name to lang_id of `fontTools`."""

    en = 0x0409  # English
    en_us = 0x0409
    en_gb = 0x0809
    zh = 0x0804  # Chinese
    zh_cn = 0x0804
    zh_tw = 0x0404
    zh_hk = 0x0C04
    zh_mo = 0x1404
    zh_sg = 0x1004
    ja = 0x0411  # Japanese
    ko = 0x0412  # Korean
    fr = 0x040C  # French
    de = 0x0407  # German
    es = 0x0C0A  # Spanish


class FontNameInfo(BaseModel):
    """The information of a font name."""

    name: str
    """The name string."""

    name_id: Literal[1, 2, 4]
    """This ID is used for tagging the font type.

    1. Font family name.
    2. Font sub-family name.
    3. Font full name.
    """

    lang_id: FontLanguage
    """The language code of this font name."""


class FontInfo(BaseModel):
    """The basic font information."""

    names: dict[FontLanguage, FontNameInfo] = Field(min_length=1)
    """The multi-lingual names of this font. All font names here are "full" names."""

    index: int = Field(ge=0, default=0)
    """The font index. This value is used only when the font is ttc. Otherwise,
    this value should be 0."""

    path: str
    """The full path to the font file."""

    def __str__(self) -> str:
        """Display the font information."""
        return self.__repr__()

    def __repr__(self) -> str:
        """Display the font information."""
        name = self.get_name()
        lang = list(lang.name for lang in self.langs)
        return '{0}(name="{1}", lang={2})'.format(self.__class__.__name__, name, lang)

    @property
    def langs(self) -> list[FontLanguage]:
        """List the supported languages."""
        return list(sorted(self.names.keys(), key=lambda val: int(val)))

    def get_name(self, lang: str | FontLanguage = FontLanguage.en) -> str:
        """Get the best name of this font.

        Will use the given language to search the font name. If not found,
        use the English language to search the font name. If still not
        found, will use the first available language of the font to
        get the font name.

        Arguments
        ---------
        lang: `FontLanguage`
            The language name or code used for searching he font.

        Returns
        -------
        #1: `str`
            The best string name of the font.
        """
        if isinstance(lang, str):
            lang = FontLanguage.__members__.get(lang, FontLanguage.en)
        name = self.names.get(lang, None)
        if name is None and lang != FontLanguage.en:
            name = self.names.get(FontLanguage.en, None)
        if name is None:
            name = self.names[next(iter(sorted(self.names.keys())))]
        return name.name

    def get_font(self, size: int = 10) -> FreeTypeFont:
        """Load the Pillow `FreeTypeFont`.

        Arguments
        ---------
        size: `int`
            The font size.

        Returns
        -------
        #1: `FreeTypeFont`
            The loaded font.
        """
        return FreeTypeFont(font=self.path, size=size, index=self.index)


class FontIndexList:
    """The internal font list maintained by the `FontLocator`.

    This list is designed for fast query.
    """

    class _SerializedFontIndexList(BaseModel):
        """(Private) The internal model used for serializing the data."""

        data: dict[FontLanguage, tuple[list[str], list[int]]]
        fonts: list[FontInfo]

    def __init__(self) -> None:
        """Initialization."""

        self.__data: dict[FontLanguage, tuple[list[str], list[int]]] = dict()
        """The font searchable name list data formatted as
        ``` python
        font_names, font_maps = self.__data[lang_id]
        font_name = font_names[name_index]
        font = self.fonts[font_maps[name_index]]
        ```
        """

        self.__fonts: list[FontInfo] = list()
        """List of all fonts."""

    def to_file(self, fobj: str | os.PathLike[str] | IO[str]) -> None:
        """Serialize this index list as a file.

        Arguments
        ---------
        fobj: `str | os.PathLike[str] | IO[str]`
            The path to the output file or a file-like object used for saving the
            file.
        """
        with contextlib.ExitStack() as stk:
            if isinstance(fobj, (str, os.PathLike)):
                fobj = stk.enter_context(open(fobj, "w", encoding="utf-8"))
            fobj.write(
                self._SerializedFontIndexList.model_validate(
                    dict(data=self.__data, fonts=self.__fonts)
                ).model_dump_json(ensure_ascii=False)
            )

    @classmethod
    def from_file(cls: type[Self], fobj: str | os.PathLike[str] | IO[str]) -> Self:
        """Load the cached data as this font index list.

        Arguments
        ---------
        fobj: `str | os.PathLike[str] | IO[str]`
            The path to the output file or a file-like object used for saving the
            file.
        """
        with contextlib.ExitStack() as stk:
            if isinstance(fobj, (str, os.PathLike)):
                fobj = stk.enter_context(open(fobj, "r", encoding="utf-8"))
            saved_data = cls._SerializedFontIndexList.model_validate_json(fobj.read())
        res = cls()
        res.__data.update(saved_data.data)
        res.__fonts.extend(saved_data.fonts)
        return res

    @property
    def n_fonts(self) -> int:
        """Number of fonts."""
        return len(self.fonts)

    @property
    def langs(self) -> list[FontLanguage]:
        """Property: Get the supported languages."""
        res = set(
            itertools.chain.from_iterable(
                set(font.names.keys()) for font in self.__fonts
            )
        )
        return list(sorted(res, key=lambda lang: int(lang)))

    @property
    def fonts(self) -> list[FontInfo]:
        """Property: List of all indexed fonts."""
        fonts = []
        fonts.extend(self.__fonts)
        return fonts

    @property
    def lang_stats(self) -> dict[FontLanguage, int]:
        """Property: Get the count of fonts for each language."""
        res = collections.Counter(
            itertools.chain.from_iterable(
                set(font.names.keys()) for font in self.__fonts
            )
        )
        return {key: res[key] for key in sorted(res.keys(), key=lambda lang: int(lang))}

    def __repr__(self) -> str:
        """Repr name of this class."""
        return "{0}(n_fonts={1})".format(self.__class__.__name__, self.n_fonts)

    def __str__(self) -> str:
        """Displayed name of this class."""
        return self.__repr__()

    def list_fonts_of_lang(self, lang: str | FontLanguage) -> list[FontInfo]:
        """List all fonts supporting a specific language.

        Arguments
        ---------
        lang: `str | FontLanguage`
            The language used for searching the font name.

            If this value is `str`, will be treated as the label of `FontLanguage`.

        Returns
        -------
        #1: `list[FontInfo]`
            A list of all fonts supporting this language.
        """
        if isinstance(lang, str):
            if lang not in FontLanguage.__members__.keys():
                return []
            lang = FontLanguage[lang]
        if lang not in self.__data:
            return []
        return list(font for font in self.__fonts if lang in font.names)

    def add_font(
        self,
        font: FontInfo,
        names_for_query: collections.abc.Mapping[
            FontLanguage, collections.abc.Sequence[str]
        ],
    ) -> None:
        """Add a font to this index list.

        Arguments
        ---------
        font: `FontInfo`
            The font information that can be used for retrieving the font.

        names_for_query: `Mapping[FontLanguage, Sequence[str]]`
            All names that can be used for querying this font.

            Some fonts may have more than one name for a specific language, that's
            because such font may have a different name compared to the full name.
        """
        if not names_for_query:
            # Do not add the font if it is not queriable.
            return
        if not any(bool(names) for names in names_for_query.values()):
            # Do not add the font if it is not queriable.
            return
        font_idx = len(self.__fonts)
        self.__fonts.append(font)
        for lang, names in names_for_query.items():
            if not names:
                continue
            font_names, font_maps = self.__data.setdefault(lang, ([], []))
            font_names.extend(self._query_preproc(name) for name in names)
            font_maps.extend(font_idx for _ in range(len(names)))

    @staticmethod
    def _query_preproc(name: str) -> str:
        """The pre-processor of the font name used for querying."""
        return name.strip().casefold()

    @staticmethod
    def _query_ratio(
        name_1: str, name_2: str, *, score_cutoff: float | None = 0.0
    ) -> float:
        """A weighted ratio for searching the fonts.

        If only using partial ratio, there may be many candidates with 100 score.
        This special ratio can distiguish the exact match from other matches.
        """
        score = 0.4 * fuzz.ratio(
            name_1, name_2, score_cutoff=score_cutoff
        ) + 0.6 * fuzz.partial_ratio(name_1, name_2, score_cutoff=score_cutoff)
        return score

    def query(
        self,
        name: str,
        lang: str | FontLanguage = FontLanguage.en,
        threshold: float = 70.0,
    ) -> list[tuple[FontInfo, str, float]]:
        """Query the font.

        Arguments
        ---------
        name: `str`
            The name used for querying the font. Usually, the name is related to
            the language.

        lang: `str | FontLanguage`
            The language of the font name. It will limit the searching scope of
            the fonts. The `name` argument should be consistent with this specified
            language.

            If this value is `str`, will be treated as the label of `FontLanguage`.

        threshold: `float`
            The threshold for the matching rate. Any matched result with a score
            lower than this threshold will be filtered out.

        Returns
        -------
        #1: `list[tuple[FontInfo, str, float]]`
            A list of queried results. The results will be sorted by the matching
            rate. If no font can be found, will return an empty list.

            Each item include:
            1. The searched font.
            2. The name that the font is used for searching.
            3. The matching rate of the searched font.

            Will not return more than five candidates.
        """
        if isinstance(lang, str):
            if lang not in FontLanguage.__members__.keys():
                return []
            lang = FontLanguage[lang]
        if lang not in self.__data:
            return []
        font_names, font_maps = self.__data[lang]
        results: list[tuple[FontInfo, str, float]] = list()
        seen_fonts: set[int] = set()
        for searched_name, searched_score, searched_name_index in sorted(
            process.extract(
                self._query_preproc(name),
                choices=font_names,
                scorer=self._query_ratio,
                limit=10,
            ),
            key=lambda res: res[1],
            reverse=True,
        ):
            if searched_score < threshold:
                continue
            font_id = font_maps[searched_name_index]
            if font_id in seen_fonts:
                continue
            seen_fonts.add(font_id)
            results.append((self.fonts[font_id], searched_name, searched_score))
        return results[:5]

    def query_best(
        self,
        name: str,
        lang: str | FontLanguage = FontLanguage.en,
        threshold: float = 70.0,
    ) -> tuple[FontInfo, str, float] | None:
        """Query only one font.

        Arguments
        ---------
        name: `str`
            The name used for querying the font. Usually, the name is related to
            the language.

        lang: `str | FontLanguage`
            The language of the font name. It will limit the searching scope of
            the fonts. The `name` argument should be consistent with this specified
            language.

            If this value is `str`, will be treated as the label of `FontLanguage`.

        threshold: `float`
            The threshold for the matching rate. If the best matched font has a
            score lower than this value, will return `None`.

        Returns
        -------
        #1: `tuple[FontInfo, str, float] | None`
            The best matched font. If no font can be found, will return `None`.

            The returned values are
            1. The searched font.
            2. The name that the font is used for searching.
            3. The matching rate of the searched font.
        """
        if isinstance(lang, str):
            if lang not in FontLanguage.__members__.keys():
                return None
            lang = FontLanguage[lang]
        if lang not in self.__data:
            return None
        font_names, font_maps = self.__data[lang]
        results = process.extractOne(
            self._query_preproc(name),
            choices=font_names,
            scorer=self._query_ratio,
        )
        if results is None:
            return None
        if results[1] < threshold:
            return None
        font_id = font_maps[results[2]]
        return self.fonts[font_id], results[0], results[1]


class FontLocator:
    """Cross-platform font locator with fuzzy name search.

    Scans system, user, and customized font directories on initialization.

    Inspired by Pillow's truetype method:
    https://pillow.readthedocs.io/en/stable/_modules/PIL/ImageFont.html#truetype

    But this locator provides more features:
    1. Fetch by name: The query of this locator is with respect to the true name
       of the font, not the file name. We also allow users to search names in
       a specific language.
    2. More efficient: The fonts are preloaded. Users do not need to iterate
       font files every time when querying a font.
    3. Flexibility: Provide fuzzy search and a fallback chain mechanism.
    4. More accurate: For Windows users, the user font folder is included. This
       folder is not considered by Pillow until now (ver `12.1.0`).
    5. Customizable: Users can provide their own font folders to override
       system font folders.
    """

    class _SerializedFontLocator(BaseModel):
        """(Private) The internal model used for serializing the data."""

        font_dirs: tuple[str, ...]
        serialized_font_index: str

    @overload
    def __init__(
        self, dirs: "str | os.PathLike[str]", include_system_dirs: bool = True
    ): ...

    @overload
    def __init__(
        self,
        dirs: "collections.abc.Sequence[str | os.PathLike[str]]",
        include_system_dirs: bool = True,
    ): ...

    @overload
    def __init__(self, dirs: None = None, include_system_dirs: bool = True): ...

    def __init__(self, dirs: Any = None, include_system_dirs: bool = True):
        """Initialization.

        Arguments
        ---------
        dirs: `str | PathLike[str] | Sequence[str | PathLike[str]] | None`
            One or several paths to directories defining the scope of searching the
            fonts. The order of the given path is the priority. The former path
            will have higher priority than the next paths.

            If not provided, will not search any user-specified folder.

        include_system_dirs: `bool`
            A `Flag`. Whether to search the system font directories.
        """
        if isinstance(dirs, (str, os.PathLike)):
            dirs = (dirs,)
        font_dirs: list[str] = []
        font_dirs.extend(self._get_user_specified_font_dirs(dirs))
        if bool(include_system_dirs):
            font_dirs.extend(self._get_system_font_dirs())
        self.__font_dirs: tuple[str, ...] = self._deduplicate_folder(font_dirs)

        self.font_index: FontIndexList = FontIndexList()
        """The font index recording all searched fonts."""

        self._scan_fonts()

    @property
    def font_dirs(self) -> tuple[str, ...]:
        """Property: The read-only searching scope of the font directories.

        All folders are guaranteed to exist.

        The folders are sorted by the priority. The folder appearing at first
        will have higher priority.
        """
        return self.__font_dirs

    @property
    def n_fonts(self) -> int:
        """Number of fonts."""
        return len(self.fonts)

    @functools.cached_property
    def langs(self) -> list[str]:
        """Property: Get the supported language short names."""
        return list(val.name for val in self.font_index.langs)

    @property
    def fonts(self) -> list[FontInfo]:
        """Property: List of all indexed fonts."""
        return self.font_index.fonts

    @functools.cached_property
    def lang_stats(self) -> dict[str, int]:
        """Property: Get the count of fonts for each language."""
        return {key.name: val for key, val in self.font_index.lang_stats.items()}

    def to_file(self, fobj: str | os.PathLike[str] | IO[str]) -> None:
        """Serialize this locator as a file.

        Arguments
        ---------
        fobj: `str | os.PathLike[str] | IO[str]`
            The path to the output file or a file-like object used for saving the
            file.
        """
        with contextlib.ExitStack() as stk:
            if isinstance(fobj, (str, os.PathLike)):
                fobj = stk.enter_context(open(fobj, "w", encoding="utf-8"))
            _idx_data = io.StringIO()
            self.font_index.to_file(_idx_data)
            _idx_data.seek(0, io.SEEK_SET)
            fobj.write(
                self._SerializedFontLocator.model_validate(
                    dict(
                        font_dirs=self.__font_dirs,
                        serialized_font_index=_idx_data.read(),
                    )
                ).model_dump_json(ensure_ascii=False)
            )

    @classmethod
    def from_file(cls: type[Self], fobj: str | os.PathLike[str] | IO[str]) -> Self:
        """Load the cached data as this font index list.

        Arguments
        ---------
        fobj: `str | os.PathLike[str] | IO[str]`
            The path to the output file or a file-like object used for saving the
            file.
        """
        with contextlib.ExitStack() as stk:
            if isinstance(fobj, (str, os.PathLike)):
                fobj = stk.enter_context(open(fobj, "r", encoding="utf-8"))
            saved_data = cls._SerializedFontLocator.model_validate_json(fobj.read())
        res = cls(dirs=None, include_system_dirs=False)
        res.__font_dirs = tuple(saved_data.font_dirs)
        res.font_index = FontIndexList.from_file(
            io.StringIO(saved_data.serialized_font_index)
        )
        return res

    def _get_user_specified_font_dirs(
        self, dirs: "collections.abc.Sequence[str | os.PathLike[str]] | None"
    ) -> tuple[str, ...]:
        """(Private) Check the user-specified directories, and return all existing
        folders."""
        if not dirs:
            return tuple()
        return tuple(str(dir) for dir in dirs if os.path.isdir(dir))

    @staticmethod
    def _get_windows_sys_font_dir() -> str | None:
        """(Private) For Windows, attempt to get the font folder from the environment
        variables first.

        If the environ is not available, dynamically import "winreg", and use the
        registries to find the font folder."""
        system_root = os.environ.get("WINDIR")
        if system_root is not None:
            path = os.path.join(str(system_root), "Fonts")
            if os.path.isdir(path):
                return path
        spec = importlib.util.find_spec("winreg", package=None)
        if spec is None or spec.loader is None:
            return None
        winreg = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(winreg)
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, R"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        ) as key:
            _system_root, _ = winreg.QueryValueEx(key, "SystemRoot")
        path = os.path.join(str(_system_root), "Fonts")
        if os.path.isdir(path):
            return path
        return None

    @staticmethod
    def _get_windows_appdata_local_dir() -> str | None:
        """(Private) Get Windows `%LOCALAPPDATA%` folder."""
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata is not None and os.path.join(local_appdata):
            return local_appdata
        local_appdata = os.path.join(os.path.expanduser("~"), "AppData", "Local")
        return local_appdata if os.path.isdir(local_appdata) else None

    def _get_system_font_dirs(self) -> tuple[str, ...]:
        """(Private) Get platform-specific system font directories.

        All directories returned by this method are guaranteed to exist.

        The returned folders are sorted by making the user fonts prior than system
        fonts.
        """
        home = os.path.abspath(os.path.expanduser("~"))
        dirs: list[str | None] = []

        if sys.platform.startswith("win"):
            # System fonts
            sys_font = self._get_windows_sys_font_dir()
            dirs.append(sys_font)

            # User fonts: %LOCALAPPDATA%\Microsoft\Windows\Fonts
            local_appdata = self._get_windows_appdata_local_dir()
            if local_appdata is not None:
                font_dir = os.path.join(local_appdata, "Microsoft", "Windows", "Fonts")
                dirs.append(font_dir)

        elif sys.platform == "darwin":
            dirs.extend(
                [
                    os.path.join(home, "Library", "Fonts"),
                    os.path.join("/Library", "Fonts"),
                    os.path.join("/System", "Library", "Fonts"),
                ]
            )

        else:  # Linux / Unix
            dirs.extend(
                [
                    os.path.join(home, ".local", "share", "fonts"),
                    os.path.join("/usr", "local", "share", "fonts"),
                    os.path.join("/usr", "share", "fonts"),
                ]
            )
            xdg_dirs = os.environ.get("XDG_DATA_DIRS")
            if xdg_dirs is not None:
                dirs.extend(dir.strip() for dir in ":".split(xdg_dirs))

        # Final filter
        return tuple(dir for dir in dirs if (dir is not None and os.path.isdir(dir)))

    def _deduplicate_folder(
        self, dirs: collections.abc.Sequence[str]
    ) -> tuple[str, ...]:
        """(Private) Given a sequence of directory paths. Deduplicate them.

        This method will track the soft links.
        """
        seen_folders: set[tuple[int, int]] = set()
        results: list[str] = []
        for path in dirs:
            if not os.path.isdir(path):
                continue
            folder_stats = os.stat(path, follow_symlinks=True)
            identifier = (folder_stats.st_dev, folder_stats.st_ino)
            if identifier in seen_folders:
                continue
            seen_folders.add(identifier)
            results.append(path)
        return tuple(results)

    def _scan_fonts(self):
        """(Private) Scan all fonts and extract internal names.

        Will track the English name (or the first available name) of the seen fonts.
        Any font with duplicated English name will be ignored.

        This mechanism guarantee that the previously find font will have higher
        priority than the later candidates.
        """
        seen_fonts: set[str] = set()
        for font_dir in self.__font_dirs:
            if not os.path.isdir(font_dir):
                continue

            for root, _, files in os.walk(font_dir):
                for file_name in files:
                    file_ext = os.path.splitext(file_name)[-1].strip().casefold()
                    if file_ext not in (".ttf", ".otf", ".ttc"):
                        continue
                    path = os.path.join(root, file_name)
                    self._index_font(path, seen_fonts)

    def _index_font(self, path: str, seen_fonts: set[str]) -> None:
        """(Private) Index a font. The font can be ttf, otf, or otc."""
        file_ext = os.path.splitext(path)[-1].strip().casefold()

        if file_ext == ".ttc":
            self._index_ttc(path, seen_fonts=seen_fonts)
        else:
            self._index_single_font(path, seen_fonts=seen_fonts)

    def _index_single_font(self, path: str, seen_fonts: set[str]) -> None:
        """(Private) Index a single font. The font can be ttf or otf.

        In this case, each file only contains one font.
        """
        try:
            font = TTFont(path, lazy=True)
        except Exception:
            return

        self._index_ttfont(font, str(path), seen_fonts)

    def _index_ttc(self, path: str, seen_fonts: set[str]) -> None:
        """(Private) Index a font collection. The file can be ttc.

        In this case, each file contains several fonts.
        """
        try:
            collection = TTCollection(path, lazy=True)
        except Exception:
            return

        # Each font in the collection is a TTFont instance
        for idx, font in enumerate(collection.fonts):
            self._index_ttfont(font, str(path), seen_fonts, font_index=idx)

    def _extract_names_from_record(
        self, lang: FontLanguage, names: collections.abc.Mapping[int, FontNameInfo]
    ) -> tuple[FontNameInfo, list[str]] | None:
        """(Private) Given a font and a specified langauge, parse its names.

        This method will be used be `self._index_ttfont`.

        Arguments
        ---------
        lang: `FontLanguage`
            The language of the `names`.

        names: `Mapping[int, FontInfo]`
            The name records from a specific font and a specific language.

        Returns
        -------
        #1: `tuple[FontNameInfo, list[str]] | None`
            The extracted values are
            1. The full name of the font.
            2. The list of names that can be used for querying.

            If the records do not contain valid names, return `None`.
        """
        if not names:
            return None
        full_name = names.get(4, None)
        family_name = names.get(1, None)
        sub_family_name = names.get(2, None)
        if family_name is not None and sub_family_name is not None:
            _family_name = family_name.name.strip()
            _sub_family_name = sub_family_name.name.strip()
            _name_ver2 = "{0} {1}".format(_family_name, _sub_family_name)
            _name_ver3 = (
                _family_name if _sub_family_name.casefold() == "regular" else None
            )
        else:
            _name_ver2 = None
            _name_ver3 = None
        names_for_query: list[str] = []
        if full_name is None:
            if _name_ver2 is None:
                return None
            res_full_name = FontNameInfo(name=_name_ver2, name_id=4, lang_id=lang)
            names_for_query.append(_name_ver2)
            if _name_ver3 is not None:
                names_for_query.append(_name_ver3)
        else:
            res_full_name = full_name
            names_for_query.append(full_name.name)
            _full_name = full_name.name.strip().casefold()
            if _name_ver2 and (_full_name != _name_ver2.casefold()):
                names_for_query.append(_name_ver2)
            if _name_ver3 and (_full_name != _name_ver3.casefold()):
                names_for_query.append(_name_ver3)
        if not names_for_query:
            return None
        return res_full_name, names_for_query

    def _index_ttfont(
        self, font: TTFont, path: str, seen_fonts: set[str], font_index: int = 0
    ):
        """(Private) Index a single font.

        This method will extract the font names. If a font has at least one valid
        name, it will be added to the font list. The font list will be used for
        querying.
        """
        font_names = font["name"]
        name_records: dict[FontLanguage, dict[int, FontNameInfo]] = dict()
        all_langs = set(int(lang) for lang in FontLanguage.__members__.values())

        for record in font_names.names:
            name_id = record.nameID
            if not (isinstance(name_id, int) and name_id in (1, 2, 4)):
                # 1: Family name
                # 2: Subfamily name
                # 4: Full name
                continue
            lang_id = record.langID
            if not (isinstance(lang_id, int) and lang_id in all_langs):
                continue
            lang = FontLanguage(value=lang_id)
            names = name_records.setdefault(lang, dict())
            names[name_id] = FontNameInfo(
                name=record.toStr(), name_id=name_id, lang_id=lang
            )

        # Solve full names, and name for queries
        full_names: dict[FontLanguage, FontNameInfo] = dict()
        names_for_query: dict[FontLanguage, list[str]] = dict()
        for lang, names in name_records.items():
            extracted_names = self._extract_names_from_record(lang=lang, names=names)
            if extracted_names is None:
                continue
            full_names[lang] = extracted_names[0]
            names_for_query.setdefault(lang, []).extend(extracted_names[1])

        font_info = FontInfo(names=full_names, index=font_index, path=path)

        # Deduplicate
        best_full_name = font_info.get_name()
        if best_full_name in seen_fonts:
            return
        seen_fonts.add(best_full_name)

        self.font_index.add_font(font=font_info, names_for_query=names_for_query)

    def query(
        self,
        name: str,
        lang: str | FontLanguage = FontLanguage.en,
        threshold: float = 70.0,
    ) -> list[FontInfo]:
        """Query the font.

        Arguments
        ---------
        name: `str`
            The name used for querying the font. Usually, the name is related to
            the language.

        lang: `str | FontLanguage`
            The language of the font name. It will limit the searching scope of
            the fonts. The `name` argument should be consistent with this specified
            language.

            If this value is `str`, will be treated as the label of `FontLanguage`.

        threshold: `float`
            The threshold for the matching rate. Any matched result with a score
            lower than this threshold will be filtered out.

        Returns
        -------
        #1: `list[FontInfo]`
            A list of queried fonts. The font will be sorted by the matching rate.
            If no font can be found, will return an empty list.

            Will not return more than five candidates.
        """
        return list(
            font
            for font, _, _ in self.font_index.query(
                name=name, lang=lang, threshold=threshold
            )
        )

    def query_best(
        self,
        name: str,
        lang: str | FontLanguage = FontLanguage.en,
        threshold: float = 70.0,
    ) -> FontInfo | None:
        """Query the best font.

        Arguments
        ---------
        name: `str`
            The name used for querying the font. Usually, the name is related to
            the language.

        lang: `str | FontLanguage`
            The language of the font name. It will limit the searching scope of
            the fonts. The `name` argument should be consistent with this specified
            language.

            If this value is `str`, will be treated as the label of `FontLanguage`.

        threshold: `float`
            The threshold for the matching rate. If the best matched font has a
            score lower than this value, will return `None`.

        Returns
        -------
        #1: `FontInfo | None`
            The best matched font. If no font can be found, will return `None`.
        """
        results = self.font_index.query_best(name=name, lang=lang, threshold=threshold)
        return results[0] if results is not None else None

    def query_best_with_fallbacks(
        self,
        name_chain: str | collections.abc.Sequence[str],
        lang: str | FontLanguage = FontLanguage.en,
        threshold: float = 70.0,
        stop_threshold: float = 90.0,
    ) -> FontInfo | None:
        """Use a chain to query the best font.

        The mechanism is similar to the fallback name list of the css font
        selector.

        Given the number of candidates in `name_chain` as N, the efficiency of
        this method should be O(N).

        Arguments
        ---------
        name_chain: `str | Sequence[str]`
            A chain of name fallbacks used for querying the font. This method will
            start from the first name in this chain, attempt to get the font, and
            stop until the best matched font compared to a name is found.

        lang: `str | FontLanguage`
            The language of the font name. It will limit the searching scope of
            the fonts. The `name` argument should be consistent with this specified
            language.

            If this value is `str`, will be treated as the label of `FontLanguage`.

        threshold: `float`
            The threshold for the matching rate. If the best matched font has a
            score lower than this value, will return `None`.

        stop_threshold: `float`
            The threshold for early stopping the search. During the iteration of the
            chain, if a searched font provides a score higher than this value,
            will return it and stop the search immediately.

        Returns
        -------
        #1: `FontInfo | None`
            The result will be equivalent to running `self.query` for each name, and
            selecting the font with the highest score.
        """
        name_chain = (name_chain,) if isinstance(name_chain, str) else tuple(name_chain)
        cur_best: tuple[FontInfo, str, float] | None = None
        for name in name_chain:
            results = self.font_index.query_best(
                name=name, lang=lang, threshold=threshold
            )
            if results is None:
                continue
            if results[2] > stop_threshold:
                return results[0]
            if cur_best is None:
                cur_best = results
                continue
            if results[2] > cur_best[2]:
                cur_best = results
        if cur_best is None:
            return None
        return cur_best[0]


if __name__ == "__main__":
    # locator = FontLocator(include_system_dirs=True)
    # locator.to_file("test.json")
    locator = FontLocator.from_file("test.json")
    fonts = locator.query(("Source Han Mono"), lang=FontLanguage.en, threshold=0)
    # best_font = fonts if fonts else None
    # if best_font is not None:
    #     print("Best match:", best_font.get_name(FontLanguage.zh_cn))
    #     print(best_font.path)
    print("Full matches:", list(font.get_name("zh") for font in fonts))
