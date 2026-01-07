# -*- coding: UTF-8 -*-
"""
Data
=====
@ Steam Editor Tools - Steam Information

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The data structures for this package.
"""

from typing_extensions import Literal

from pydantic import BaseModel, ConfigDict, Field

from PIL import Image

from .utils import get_image_by_url


__all__ = (
    "PlatformInfo",
    "MetacriticInfo",
    "AppCategory",
    "AppDate",
    "AppSupportInfo",
    "AppScreenShot",
    "AppMovie",
    "AppPrice",
    "AppQuerySimple",
    "AppInfo",
)


class PlatformInfo(BaseModel):
    """Supported platform."""

    model_config = ConfigDict(extra="ignore")

    windows: bool
    mac: bool
    linux: bool


class MetacriticInfo(BaseModel):
    """The metacritic information of a game."""

    model_config = ConfigDict(extra="ignore")

    score: int
    url: str


class AppCategory(BaseModel):
    """The category of a game app."""

    model_config = ConfigDict(extra="ignore")

    id: int
    description: str


class AppDate(BaseModel):
    """The release date of a game app."""

    model_config = ConfigDict(extra="ignore")

    coming_soon: bool = False
    date: str


class AppSupportInfo(BaseModel):
    """The support information of a game app."""

    model_config = ConfigDict(extra="ignore")

    url: str = ""
    email: str = ""


class AppScreenShot(BaseModel):
    """The information of an app screenshot."""

    model_config = ConfigDict(extra="ignore")

    id: int = Field(ge=0)
    """The ID of the screenshot. It is maintained by each app."""

    path_thumbnail: str
    """The url to the thumbnail screenshot."""

    path_full: str
    """The url to the full screenshot."""

    def get_image(self, thumbnail: bool = False) -> Image.Image | None:
        """Download the screenshot image by its url.

        Arguments
        ---------
        thumbnail: `bool`
            If specified, will download the thumbnail version.

        Returns
        -------
        #1: `Image.Image | None`
            The downloaded image. If no image can be downloaded, return `None`.
        """
        return get_image_by_url(self.path_thumbnail if thumbnail else self.path_full)


class AppMovie(BaseModel):
    """The information of an app release trailer movie."""

    model_config = ConfigDict(extra="ignore")

    id: int = Field(ge=0)
    """The ID of the movie. It is maintained in the whole store scope."""

    name: str
    """The name of the video."""

    thumbnail: str
    """The url to the thumbnail screenshot."""

    dash_av1: str | None = None
    """The url to the Dash AV1 stream."""

    dash_h264: str | None = None
    """The url to the Dash H264 stream."""

    hls_h264: str | None = None
    """The url to the HLS H264 (m3u8) stream."""

    highlight: bool = False
    """Whether the movie will be displayed in highlights."""

    def get_thumbnail(self) -> Image.Image | None:
        """Download the thumbnail image by its url."""
        return get_image_by_url(self.thumbnail)


class AppPrice(BaseModel):
    """The price information of an app."""

    model_config = ConfigDict(extra="ignore")

    currency: str
    """The name of the currency."""

    initial: int = Field(ge=0)
    """The original price number (specified as cents.)"""

    final: int = Field(ge=0)
    """The current price number (specified as cents.)"""

    discount_percent: int = Field(ge=0, le=100)
    """The discount percent. It is in 0~100."""

    initial_formatted: str
    """The original price formatted by the currency."""

    final_formatted: str
    """The current price formatted by the currency."""


class AppQuerySimple(BaseModel):
    """The query item returned by searching-the-app-by-name."""

    model_config = ConfigDict(extra="ignore")

    type: str
    """The type of the queried item. It should be app for most cases."""

    name: str
    """The app name."""

    id: int
    """The app ID."""

    tiny_image: str
    """The URL to the tiny image of the queried app."""

    metascore: str | None = None
    """The metascore."""

    platforms: PlatformInfo | None = None
    """The supported platform."""

    def get_tiny_image(self) -> Image.Image | None:
        """Download the tiny image by its url."""
        return get_image_by_url(self.tiny_image)


class AppInfo(BaseModel):
    """The basic information of an app, provided by querying the ID."""

    model_config = ConfigDict(extra="ignore")

    type: str
    """The type of the app. It should be "game" for most cases."""

    name: str
    """The app name."""

    steam_appid: int
    """The app ID."""

    required_age: int = 0
    """The required age of the game."""

    is_free: bool
    """Whether the game is free or not."""

    controller_support: str | None = None
    """How does it support the controller."""

    dlc: list[int] = Field(default_factory=list)
    """A list of DLCs' app IDs."""

    detailed_description: str = ""
    """A long game description formatted by HTML."""

    about_the_game: str = ""
    """A long game description displayed in the store page. It is ususally the same
    as "detailed_description". Formatted by HTML."""

    short_description: str = ""
    """A short game description displayed in the game title bar."""

    supported_languages: str = ""
    """The names of supported languages. It is formatted by HTML."""

    reviews: str = ""
    """The media reviews. It is formatted by HTML."""

    header_image: str | None = None
    """The URL of the header image. This is usually big."""

    capsule_image: str | None = None
    """The URL of the capsule image. This is usally smaller than header_image."""

    capsule_imagev5: str | None = None
    """The URL of the capsule v5 image. This is usally smaller than capsule_image."""

    website: str | None = None
    """The official website of the game."""

    legal_notice: str | None = None
    """The legal notice of the game."""

    developers: list[str] = Field(default_factory=list)
    """The list of developer names."""

    publishers: list[str] = Field(default_factory=list)
    """The list of publishers names."""

    price_overview: AppPrice | None = None
    """The price of the app."""

    platforms: PlatformInfo | None = None
    """The supported platform."""

    metacritic: MetacriticInfo | None = None
    """The metacritic information of the game."""

    categories: list[AppCategory] = Field(default_factory=list)
    """The related categories of the game. This list is displayed as tags on the store
    page."""

    genres: list[AppCategory] = Field(default_factory=list)
    """The related categories of the game. This list is displayed as game type."""

    screenshots: list[AppScreenShot] = Field(default_factory=list)
    """The list of screenshots."""

    movies: list[AppMovie] = Field(default_factory=list)
    """The list of moviews."""

    release_date: AppDate | None = None
    """The release date of the app."""

    support_info: AppSupportInfo | None = None
    """The support information of the app."""

    background: str | None = None
    """The background image of the store page."""

    background_raw: str | None = None
    """The background image (raw version) of the store page."""

    def get_header_image(
        self, level: Literal["full", "capsule", "capsulev5"] = "full"
    ) -> Image.Image | None:
        """Download the header image by its url.

        Arguments
        ---------
        level: `"full" | "capsule" | "capsulev5"`
            The level of the header image. The sizes are sorted as:

            full > capsule > capsulev5

        Returns
        -------
        #1: `Image.Image | None`
            The downloaded image. If no image can be downloaded, return `None`.
        """
        if level == "full":
            return get_image_by_url(self.header_image)
        elif level == "capsule":
            return get_image_by_url(self.capsule_image)
        elif level == "capsulev5":
            return get_image_by_url(self.capsule_imagev5)
        else:
            return get_image_by_url(self.header_image)

    def get_background_image(self, raw: bool = False) -> Image.Image | None:
        """Download the header image by its url.

        Arguments
        ---------
        raw: `bool`
            Whether to get the raw version of the image.

        Returns
        -------
        #1: `Image.Image | None`
            The downloaded image. If no image can be downloaded, return `None`.
        """
        if raw:
            return get_image_by_url(self.background_raw)
        else:
            return get_image_by_url(self.background)
