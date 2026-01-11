# -*- coding: UTF-8 -*-
"""
Renderer
========
@ Steam Editor Tools - BBCode

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
Render the AST (Document/Node) into BBCode.

Users may customzie the BBCode styles by instantiating their own `BBCodeConfig`.
"""

from typing import List

from pydantic import BaseModel

from .nodes import (
    Node,
    Document,
    TextNode,
    InlineCodeNode,
    CodeBlockNode,
    LinkNode,
    HeadingNode,
    ParagraphNode,
    QuoteNode,
    AlertNode,
    ListNode,
    ListItemNode,
    TableNode,
    TableRowNode,
    TableCellNode,
)


__all__ = ("AlertTitleConfigs", "BBCodeConfig", "BBCodeRenderer")


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


class BBCodeRenderer:
    """The BBCode renderer.

    Render the structured `Document` or an intemediate `Node` into the BBCode format.
    """

    __slots__ = ("configs",)

    def __init__(self, configs: BBCodeConfig | None = None) -> None:
        """Initialization.

        Arguments
        ---------
        configs: `BBCodeConfig | None`
            The configurations used for customizing the BBCode tags.

            If not specified, will use `BBCodeConfig()` by default.
        """
        if configs is None:
            configs = BBCodeConfig()
        self.configs = configs

    # Dispatcher
    def render(self, node: Node | Document) -> str:
        """Render the BBCode.

        Main dispatcher. Uses `node.type` directly so type checkers
        can narrow the union correctly.

        Arguments
        ---------
        node: `Node | Document`
            The node or the document that would be rendered as BBCode.

        Returns
        -------
        #1: `str`
            The rendered BBCode text.
        """

        if node.type == "text":
            return self.render_text(node)

        if node.type == "br":
            return "\n\n"

        if node.type == "hr":
            return "[{0}][/{0}]\n".format(self.configs.hr)

        if node.type == "inline_code":
            return self.render_inline_code(node)

        if node.type == "code_block":
            return self.render_code_block(node)

        if node.type == "bold":
            return self.wrap_children(node.children, self.configs.bold)

        if node.type == "italic":
            return self.wrap_children(node.children, self.configs.italic)

        if node.type == "underline":
            return self.wrap_children(node.children, self.configs.underline)

        if node.type == "strike":
            return self.wrap_children(node.children, self.configs.strike)

        if node.type == "spoiler":
            return self.wrap_children(node.children, self.configs.spoiler)

        if node.type == "link":
            return self.render_link(node)

        if node.type == "heading":
            return self.render_heading(node)

        if node.type == "paragraph":
            return self.render_paragraph(node)

        if node.type == "quote":
            return self.render_quote(node)

        if node.type == "alert":
            return self.render_alert(node)

        if node.type == "list":
            return self.render_list(node)

        if node.type == "list_item":
            return self.render_list_item(node)

        if node.type == "table":
            return self.render_table(node)

        if node.type == "table_row":
            return self.render_table_row(node)

        if node.type == "table_cell":
            return self.render_table_cell(node)

        if node.type == "document":
            return self.render_document(node)

        if node.type == "deleted":
            return ""

        raise ValueError(f"Unknown node type: {node.type}")

    # Helpers
    def render_children(self, children: List[Node]) -> str:
        """Helper method. Render a list of children nodes into BBCode."""
        return "".join(self.render(child) for child in children).strip("\r\n")

    def wrap_children(
        self, children: List[Node], start: str, end: str | None = None
    ) -> str:
        """Helper method. Render `children` and surrount the results by:
        ```
        [start]children[/end]
        ```
        """
        if end is None:
            end = start
        return "[{0}]{1}[/{2}]".format(start, self.render_children(children), end)

    def render_text(self, node: TextNode) -> str:
        """Specific renderring. Render the plain text into BBCode."""
        return node.text

    def render_inline_code(self, node: InlineCodeNode) -> str:
        """Specific renderring. Render the inline code."""
        tag = self.configs.inline_code
        return "[{tag}]{code}[/{tag}]".format(tag=tag, code=node.code)

    def render_code_block(self, node: CodeBlockNode) -> str:
        """Specific renderring. Render the block code as
        ```
        [code]
        ...
        [/code]
        ```
        """
        tag = self.configs.code_block

        return "[{tag}]\n{code}{codebreak}[/{tag}]\n\n".format(
            tag=tag, code=node.code, codebreak="" if node.code.endswith("\n") else "\n"
        )

    def render_link(self, node: LinkNode) -> str:
        """Specific renderring. Render the url (link).

        Note that there is an exception. If href is the same as text, will render the
        plain text directly.
        """
        text = self.render_children(node.children)
        if node.href == text:
            return text
        tag = self.configs.link
        return "[{tag}={href}]{text}[/{tag}]".format(tag=tag, href=node.href, text=text)

    def render_heading(self, node: HeadingNode) -> str:
        """Specific renderring. Render the heading (title)."""
        content = self.render_children(node.children)
        tag = self.configs.get_h_tag_by_level(node.level)
        return "[{tag}]{content}[/{tag}]\n".format(tag=tag, content=content)

    def render_paragraph(self, node: ParagraphNode) -> str:
        """Specific renderring. Render the paragraph."""
        return self.render_children(node.children) + "\n\n"

    def render_quote(self, node: QuoteNode) -> str:
        """Specific renderring. Render the quote block."""
        tag = self.configs.quote
        extra = "={0}".format(node.cite) if node.cite else ""
        return "[{tag}{extra}]\n{children}\n[/{tag}]\n\n".format(
            tag=tag, extra=extra, children=self.render_children(node.children)
        )

    def render_alert(self, node: AlertNode) -> str:
        """Specific renderring. Render the alert block."""
        title = node.title.strip().casefold()
        tag = self.configs.alert.render_title_as_tag(title)
        if not tag:
            # Fall back to rendering a quote block.
            return self.render_quote(QuoteNode(children=node.children))
        return "[{tag}]\n{children}\n[/{tag}]\n\n".format(
            tag=tag, children=self.render_children(node.children)
        )

    def render_list(self, node: ListNode) -> str:
        """Specific renderring. Render the ordered or unordered list."""
        if node.ordered:
            tag = self.configs.olist
        else:
            tag = self.configs.list

        items = "".join(self.render(item) for item in node.items)
        return "[{tag}]\n{items}[/{tag}]\n\n".format(tag=tag, items=items)

    def render_list_item(self, node: ListItemNode) -> str:
        """Specific renderring. Render the list item."""
        tag = self.configs.list_item
        return "[{tag}]{content}\n".format(
            tag=tag, content=self.render_children(node.children)
        )

    def render_table(self, node: TableNode) -> str:
        """Specific renderring. Render the table.

        BBCode table syntax varies by forum. We adopt the Steam's format.
        ```
        [table]
        [tr][th]Header[/th][th]Header[/th][/tr]
        [tr][td]Cell[/td][td]Cell[/td][/tr]
        [/table]
        ```
        """
        rows = "".join(self.render(row) for row in node.rows)
        tag = self.configs.table
        return "[{tag}]\n{rows}[/{tag}]\n\n".format(tag=tag, rows=rows)

    def render_table_row(self, node: TableRowNode) -> str:
        """Specific renderring. Render the table row."""
        cells = "".join(self.render(cell) for cell in node.cells)
        tag = self.configs.table_row
        return "[{tag}]{cells}[/{tag}]\n".format(tag=tag, cells=cells)

    def render_table_cell(self, node: TableCellNode) -> str:
        """Specific renderring. Render the table cell (head or data cells)."""
        content = self.render_children(node.children)
        if node.header:
            tag = self.configs.table_head
        else:
            tag = self.configs.table_data
        return "[{tag}]{content}[/{tag}]".format(tag=tag, content=content)

    def render_document(self, doc: Document) -> str:
        """Specific renderring. Render the whole document."""
        return self.render_children(doc.children).rstrip() + "\n"
