# -*- coding: UTF-8 -*-
"""
Utilities
=========
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
The utilities that help maintain the queried data.
"""

import io

import httpx
from PIL import Image


__all__ = ("get_image_by_url",)


def get_image_by_url(url: str | None) -> Image.Image | None:
    """Download the image by its url.

    Arguments
    ---------
    url: `str | None`
        The URL used for accessing the image.

    Returns
    -------
    #1: `Image.Image | None`
        The image object fetched by the url. It is `None` when no image
        can be fetched.
    """
    if url is None:
        return None
    url = url.strip()
    if not url:
        return None
    # Fetch raw bytes
    with httpx.Client() as client:
        response = client.get(url, timeout=10)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            return None
        data = response.content

    if len(data) == 0:
        return None

    # Convert bytes to Pillow Image
    img = Image.open(io.BytesIO(data))
    return img
