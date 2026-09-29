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
    """The tag used to render the alert block with the type: note."""

    tip: str = "quote"
    """The tag used to render the alert block with the type: tip."""

    important: str = "b"
    """The tag used to render the alert block with the type: important."""

    warning: str = "u"
    """The tag used to render the alert block with the type: warning."""

    caution: str = "spoiler"
    """The tag used to render the alert block with the type: caution."""

    # The following titles are not official formats.
    tag_b: str = "b"
    """The tag used to render the alert block with the type: tag_b."""

    tag_i: str = "i"
    """The tag used to render the alert block with the type: tag_i."""

    tag_u: str = "u"
    """The tag used to render the alert block with the type: tag_u."""

    tag_strike: str = "strike"
    """The tag used to render the alert block with the type: tag_strike."""

    tag_spoiler: str = "spoiler"
    """The tag used to render the alert block with the type: tag_spoiler."""

    def render_title_as_tag(self, title: str) -> str | None:
        """Given a title specified in `AlertNode`, get the appropriate BBCode tag
        for it.

        Arguments
        ---------
        title: `str`
            Given the title of an alert block, and use it to find the tag.

        Returns
        -------
        #1: `str`
            The returned tag.

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
    """The tag used to render: hr."""

    inline_code: str = "noparse"
    """The tag used to render: inline code."""

    code_block: str = "code"
    """The tag used to render: multi-line code."""

    bold: str = "b"
    """The tag used to render: bold text."""

    italic: str = "i"
    """The tag used to render: italic text."""

    underline: str = "u"
    """The tag used to render: underlined text."""

    strike: str = "strike"
    """The tag used to render: deleted text."""

    spoiler: str = "spoiler"
    """The tag used to render: spoiler text."""

    link: str = "url"
    """The tag used to render: url (link)."""

    h1: str = "h1"
    """The tag used to render: title with level 1."""

    h2: str = "h2"
    """The tag used to render: title with level 2."""

    h3: str = "h3"
    """The tag used to render: title with level 3."""

    h4: str = "h3"
    """The tag used to render: title with level 4."""

    h5: str = "h3"
    """The tag used to render: title with level 5."""

    h6: str = "h3"
    """The tag used to render: title with level 6."""

    h_default: str = "h3"
    """The tag used to render: title with the default level."""

    paragraph: str = "p"
    """The tag used to render: paragraph."""

    quote: str = "quote"
    """The tag used to render: quote block."""

    list: str = "list"
    """The tag used to render: unordered list."""

    olist: str = "olist"
    """The tag used to render: ordered list."""

    list_item: str = "*"
    """The tag used to render: list item."""

    table: str = "table"
    """The tag used to render: table."""

    table_row: str = "tr"
    """The tag used to render: table row."""

    table_head: str = "th"
    """The tag used to render: table header cell."""

    table_data: str = "td"
    """The tag used to render: table plain cell."""

    alert: AlertTitleConfigs = AlertTitleConfigs()
    """The configurations of the tags related to the alert block."""

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
