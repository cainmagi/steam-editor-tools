# -*- coding: UTF-8 -*-
"""
Query
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
The methods for querying the Steam information.
"""

import collections.abc

import httpx
from rapidfuzz import process, fuzz

from .data import AppQuerySimple, AppInfo, AchievementList

__all__ = ("query_app_by_name_simple", "get_app_details", "get_achievement_list")


def query_app_by_name_simple(
    query: str, lang: str = "english", cc: str = "US"
) -> list[AppQuerySimple]:
    """Query the app information by name.

    This is a simple query. It accesses the following API:
    https://store.steampowered.com/api/storesearch

    which is undocumented.

    Arguments
    ---------
    query: str
        The search query. It is used for searching the app name.

    lang: str
        The language used for searching the app.

    cc: str
        The region used for searching the app.

    Returns
    -------
    #1: `list[SimpleQuery]`
        A list of queried results sorted by the matching of the name. It should return
        no more than 10 apps even if there are more candidates.
    """
    url = "https://store.steampowered.com/api/storesearch/"
    params = {
        "term": query,
        "l": lang,
        "cc": cc,
    }

    r = httpx.get(url, params=params, timeout=10)
    r.raise_for_status()
    items = r.json().get("items", [])

    if not items:
        return []

    items = items[:10]

    # Extract names for fuzzy matching
    names = [item["name"] for item in items]

    matches = process.extract(
        query,
        names,
        scorer=fuzz.WRatio,
    )

    matches = sorted(matches, key=lambda match_item: match_item[1], reverse=True)

    results: list[AppQuerySimple] = []
    for _, _, idx in matches:
        results.append(AppQuerySimple.model_validate(items[idx], strict=False))

    return results


def get_app_details(
    app: int | AppQuerySimple, lang: str = "english", cc: str = "US"
) -> AppInfo | None:
    """Fetch the app detailed information by its ID.

    The information is provided by:
    https://store.steampowered.com/api/appdetails

    which is undocumented.

    Arguments
    ---------
    app: `int | AppQuerySimple`
        The steam app ID or the query object. It is used for locating the game
        details.

    lang: str
        The language used for searching the app.

    cc: str
        The region used for searching the app.

    Returns
    -------
    #1: `AppInfo | None`
        Return the app information if the app ID is valid (i.e. the app is found).
        Otherwise, return `None`.
    """
    appid = str(app.id if isinstance(app, AppQuerySimple) else int(app))
    url = "https://store.steampowered.com/api/appdetails/"
    params = {
        "appids": appid,
        "l": lang,
        "cc": cc,
    }

    r = httpx.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json().get(appid, None)
    if not isinstance(data, collections.abc.Mapping):
        return None

    data = data.get("data", None)
    if not isinstance(data, collections.abc.Mapping):
        return None

    return AppInfo.model_validate(data, strict=False)


def get_achievement_list(
    app: int | AppQuerySimple,
    lang: str = "english",
    extra_user_profiles: collections.abc.Sequence[str] | None = None,
) -> AchievementList:
    """Fetch the achievement list of a specific app (game). The information
    is directly fetched from the game page.

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
    return AchievementList.from_app(
        app=app, lang=lang, extra_user_profiles=extra_user_profiles
    )
