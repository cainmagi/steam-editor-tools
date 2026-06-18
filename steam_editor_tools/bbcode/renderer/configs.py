# -*- coding: UTF-8 -*-
"""
Configs
=======
@ Steam Editor Tools - BBCode: Renderer

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The configurations of BBCode renderer.
"""

from pydantic import BaseModel

__all__ = ("AlertTitleConfigs", "BBCodeConfig")


class AlertTitleConfigs(BaseModel):
    """The translation list of alert box titles.

    Each field name will be interpreted as an allowed alert box title in Markdown.
    For example, users can write
    ```
    > [!note]
    > A example of note box.
    ```
    which will be interpreted as
    ```
    [quote]
    A example of note box.
    [/quote]
    ```
    if `AlertTitleConfigs.note == "quote"`.

    Any alert box title that are not defined in this list will be interpreted as
    `quote` when rendering BBCode.
    """

    # Need to support at least the following five types.
    note: str = "quote"
    tip: str = "quote"
    important: str = "b"
    warning: str = "u"
    caution: str = "spoiler"
    # The following titles are not official formats.
    tag_b: str = "b"
    tag_i: str = "i"
    tag_u: str = "u"
    tag_strike: str = "strike"
    tag_spoiler: str = "spoiler"

    def render_title_as_tag(self, title: str) -> str | None:
        """Given a title specified in `AlertNode`, get the appropriate BBCode tag
        for it.

        This method may return `None`. In this case, the `AlertNode` will fall
        back into a `QuoteNode`.
        """
        this_fields = self.__class__.model_fields
        if title not in this_fields:
            return None
        val = self.__dict__.get(title, None)
        if not (isinstance(val, str) and val):
            return None
        val = val.strip()
        return val


class BBCodeConfig(BaseModel):
    """Configurations of BBCode renderer.

    Different forums may have different BBCode formats. For example, in some cases,
    the deleted text may be formated as `[s]...[/s]`, not `[strike]...[/strike]`.

    This configuration type allows users to customize the BBCode tags for other
    usages.

    The default format (i.e. `BBCodeConfig()`) is consistent with Steam's BBCode
    rules.
    """

    hr: str = "hr"
    inline_code: str = "noparse"
    code_block: str = "code"
    bold: str = "b"
    italic: str = "i"
    underline: str = "u"
    strike: str = "strike"
    spoiler: str = "spoiler"
    link: str = "url"
    h1: str = "h1"
    h2: str = "h2"
    h3: str = "h3"
    h4: str = "h3"
    h5: str = "h3"
    h6: str = "h3"
    h_default: str = "h3"
    paragraph: str = "p"
    quote: str = "quote"
    list: str = "list"
    olist: str = "olist"
    list_item: str = "*"
    table: str = "table"
    table_row: str = "tr"
    table_head: str = "th"
    table_data: str = "td"
    alert: AlertTitleConfigs = AlertTitleConfigs()

    def get_h_tag_by_level(self, level: int) -> str:
        """Get the heading tag by specifying the heading level.

        Arguments
        ---------
        level: `int`
            The heading (title) level. Can be 1~6.

        Returns
        -------
        #1: `str`
            The heading tag. For example, `get_h_tag_by_level(2)` yields `self.h2`.
        """
        return {
            1: self.h1,
            2: self.h2,
            3: self.h3,
            4: self.h4,
            5: self.h5,
            6: self.h6,
        }.get(level, self.h_default)
