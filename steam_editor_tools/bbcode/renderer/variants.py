# -*- coding: UTF-8 -*-
"""
Variants
========
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
The variants of the BBCode renderer.

These variants are used to render BBCode documents in different ways. Mostly, they
are provided because some Steam BBCode formats are not supported in store-page
reviews. Users can implement their own variants by following the same example
style in this module.
"""

import itertools
import inspect

from typing_extensions import ClassVar, override
from ..nodes import (
    TextNode,
    HeadingNode,
    CodeBlockNode,
    QuoteNode,
    ListNode,
    ListItemNode,
    TableNode,
    TableRowNode,
    TableCellNode,
)
from .configs import BBCodeConfig
from .base import BBCodeRenderer

__all__ = (
    "BBCodeRendererTablePreferred",
    "BBCodeRendererListPreferred",
    "BBCodeRendererForReview",
)


class BBCodeRendererTablePreferred(BBCodeRenderer):
    """The BBCode renderer with table format preferred.

    This renderer variant will use the table format when rendering:
    - unordered lists
    - ordered lists

    Such rendering conversions were used when writing reviews previously because the
    lists were not correctly rendered before.

    However, since the Steam major update in 2026, the table is now rendered
    incorrectly. Therefore, currently, it is better to use
    `BBCodeRendererForReview` or `BBCodeRendererListPreferred`.
    """

    TEXT_IDX: ClassVar[str] = "①②③④⑤⑥⑦⑧⑨⑩"

    def __list_item_to_table_row(
        self, node: ListItemNode, idx: int, parent_node: ListNode | None = None
    ):
        """(Private) Render a list item as a table row."""
        row: list[TableCellNode] = []
        if parent_node is None:
            row.append(TableCellNode(header=True, children=[]))
            row.append(TableCellNode(header=False, children=node.children))
            return TableRowNode(cells=row)
        if parent_node.ordered:
            row.append(
                TableCellNode(
                    header=True,
                    children=[
                        TextNode(
                            text=self.TEXT_IDX[idx] if idx < 10 else "{0}.".format(idx)
                        )
                    ],
                )
            )
            row.append(TableCellNode(header=False, children=node.children))
        else:
            row.append(TableCellNode(header=True, children=[TextNode(text="⚪")]))
            row.append(TableCellNode(header=False, children=node.children))
        return TableRowNode(cells=row)

    @override
    def render_list(self, node: ListNode) -> str:
        """Specific rendering. Render the ordered or unordered list.

        Arguments
        ---------
        node: `ListNode`
            The list to be rendered.

        Returns
        -------
        #1: `str`
            The rendered list bbcode.
        """
        rows: list[TableRowNode] = []
        idx = 0
        for item in node.items:
            if not isinstance(item, ListItemNode):
                continue
            rows.append(
                self.__list_item_to_table_row(node=item, idx=idx, parent_node=node)
            )
            idx = idx + 1
        return BBCodeRenderer.render_table(self, TableNode(rows=rows))

    @override
    def render_list_item(
        self, node: ListItemNode, idx: int, parent_node: ListNode | None = None
    ) -> str:
        """Specific renderring. Render the list item.

        Arguments
        ---------
        node: `ListItemNode`
            The list item to be rendered.

        idx: `int`
            The optional argument `idx` is the current index of the item in the list.

        parent_node: `None`
            The optional `parent_node` is the nearest unordered/ordered list wrapper
            of this item.

        Returns
        -------
        #1: `str`
            The rendered list item bbcode.
        """
        return BBCodeRenderer.render_table_row(
            self,
            self.__list_item_to_table_row(node=node, idx=idx, parent_node=parent_node),
        )


class BBCodeRendererListPreferred(BBCodeRenderer):
    """The BBCode renderer with list format preferred.

    This renderer variant will use the list format when rendering:
    - tables

    and use the plain text format when rendering:
    - quote
    - code

    Such rendering conversions should be used for writing reviews since 2026,
    because table, quote, and code formats will break on the store page now.
    """

    @staticmethod
    def __pretret_code_leading_space(codes: str, char: str = "⠀", prev: str = ">⠀"):
        """(Private) Pretret the leading space of code blocks."""
        codes = inspect.cleandoc("\n" + codes)
        lines = codes.splitlines(keepends=True)
        _lines: list[str] = []
        for line in lines:
            _line = line.lstrip()
            if not line.strip():
                _lines.append(prev + "\n")
                continue
            _lines.append(prev + char * (len(line) - len(_line)) + _line)
        return "".join(_lines)

    def __flatten_table_row(self, row: TableRowNode) -> ListItemNode:
        """(Private) Convert a table row to a list item."""
        if not isinstance(row, TableRowNode):
            return ListItemNode(children=[TextNode(text=self.render(row))])
        if not row.cells:
            return ListItemNode(children=[])
        if len(row.cells) == 1:
            return ListItemNode(children=[row.cells[0]])
        _row: list[str] = [self.render(row.cells[0])]
        for prev_cell, cell in itertools.pairwise(row.cells):
            if not cell:
                continue
            if cell.size < 2 and prev_cell.size < 2:
                pass
            elif cell.size < 2:
                _row.append(" ")
            elif prev_cell.size < 2:
                _row.append(": ")
            else:
                _row.append(" | ")
            _row.append(self.render(cell))
        return ListItemNode(children=[TextNode(text="".join(_row))])

    @override
    def render_code_block(self, node: CodeBlockNode) -> str:
        """Specific renderring. Render the block code as

        ```
        > ...
        > ...
        > ...
        ```

        Arguments
        ---------
        node: `CodeBlockNode`
            The code block to be rendered.

        Returns
        -------
        #1: `str`
            The rendered code block.
        """
        return "[{tag}]\n{code}\n[/{tag}]\n\n".format(
            tag=self.configs.inline_code,
            code=self.__pretret_code_leading_space(node.code),
        )

    @override
    def render_quote(self, node: QuoteNode) -> str:
        """Specific renderring. Render the quote block.

        Arguments
        ---------
        node: `QuoteNode`
            The quote block to be rendered.

        Returns
        -------
        #1: `str`
            The rendered quote block.
        """
        hr = "[{0}][/{0}]".format(self.configs.hr)
        extra = "{0}".format(node.cite) if node.cite else ""
        if extra:
            return "{hr}{children}\n⠀⠀⠀⠀——{extra}\n{hr}\n".format(
                hr=hr, extra=extra, children=self.render_children(node.children)
            )
        else:
            return "{hr}{children}\n{hr}\n".format(
                hr=hr, children=self.render_children(node.children)
            )

    @override
    def render_table(self, node: TableNode) -> str:
        """Specific renderring. Render the table.

        This overriden table rendering will convert a table to the following list:
        ``` bbcode
        [list]
        [*] [b]Header[/b] | [b]Header[/b]
        [*] Cell | Cell
        [/list]
        ```
        When the list needs to be replaced by the ordered list, use the following
        configs:
        ``` python
        configs.table = "ordered"
        ```

        Arguments
        ---------
        node: `TableNode`
            The table to be rendered.

        Returns
        -------
        #1: `str`
            The rendered table bbcode.
        """
        rows = [self.__flatten_table_row(row) for row in node.rows if row.size > 0]
        return BBCodeRenderer.render_list(
            self, ListNode(ordered="ordered" in self.configs.table, items=rows)
        )

    @override
    def render_table_row(self, node: TableRowNode) -> str:
        """Specific renderring. Render the table row.

        Arguments
        ---------
        node: `TableRowNode`
            The table row to be rendered.

        Returns
        -------
        #1: `str`
            The rendered table row.
        """
        cells = self.__flatten_table_row(node)
        return "⬊ {cells}\n".format(cells=cells)

    @override
    def render_table_cell(self, node: TableCellNode) -> str:
        """Specific renderring. Render the table cell (head or data cells).

        Arguments
        ---------
        node: `TableCellNode`
            The table cell to be rendered.

        Returns
        -------
        #1: `str`
            The rendered table cell.
        """
        content = self.render_children(node.children)
        if node.header:
            tag = self.configs.bold
            return "[{tag}]{content}[/{tag}]".format(tag=tag, content=content)
        else:
            return "{content}".format(content=content)


class BBCodeRendererForReview(BBCodeRendererListPreferred):
    """The BBCode renderer specialized for rendering reviews.

    This renderer variant will specialize the format when rendering:
    - tables

    and provide optional options for rendering:
    - quote
    - code
    - h2/h3...

    These features are particularly optimized for the best format when
    writing Steam Reviews, with all incorrect features replaced by other
    available features.
    """

    def __init__(
        self,
        configs: BBCodeConfig | None = None,
        is_quote_converted: bool = False,
        is_codeblock_converted: bool = False,
        is_h_converted: bool = True,
    ) -> None:
        """Initialization.

        Arguments
        ---------
        configs: `BBCodeConfig | None`
            The configurations used for customizing the BBCode tags.

            If not specified, will use `BBCodeConfig()` by default.

        is_quote_converted: `bool`
            A flag that enabling the optional feature of converting the format of
            quote blocks. If enabled, will render the quotes in the following
            format:
            ```
            [quote][u]...[/u][/quote]
            ```

        is_codeblock_converted: `bool`
            A flag that enabling the optional feature of converting the format of
            code blocks. If enabled, will render the codes as texts like this:
            ```
            > line 1
            >   line 2
            > ...
            ```

        is_h_converted: `bool`:
            A flag that enabling the optional feature of converting the section
            heads. If enabled, will make all h tags formatted as the h1 tag.
        """
        super().__init__(configs)
        self.is_quote_converted: bool = bool(is_quote_converted)
        self.is_codeblock_converted: bool = bool(is_codeblock_converted)
        self.is_h_converted: bool = bool(is_h_converted)

    def __flatten_table_row(self, row: TableRowNode) -> ListItemNode:
        """(Private) Convert a table row to a list item.

        Arguments
        ---------
        row: `TableRowNode`
            The table row to be formatted into the list item. Depending on the
            structure of the node, the format differ.

        Returns
        -------
        #1: `ListItemNode`
            The converted list item node.
        """

        def force_bold(text: str) -> str:
            _text = text.strip()
            if not _text.startswith("[b]"):
                return "[b]{0}[/b]".format(_text)
            return _text

        if not isinstance(row, TableRowNode):
            return ListItemNode(children=[TextNode(text=self.render(row))])
        if not row.cells:
            return ListItemNode(children=[])
        if len(row.cells) == 1:
            return ListItemNode(children=[row.cells[0]])
        _row_raw: list[str] = [self.render(cell) for cell in row.cells]
        if len(_row_raw) == 2:
            return ListItemNode(
                children=[
                    TextNode(text=": ".join([force_bold(_row_raw[0]), *_row_raw[1:]]))
                ]
            )
        elif len(_row_raw) == 3:
            return ListItemNode(
                children=[
                    TextNode(
                        text="".join(
                            [
                                force_bold(_row_raw[0]),
                                "【{0}】 ".format(force_bold(_row_raw[1])),
                                *_row_raw[2:],
                            ]
                        )
                    )
                ]
            )
        return ListItemNode(children=[TextNode(text=" | ".join(_row_raw))])

    @override
    def render_quote(self, node: QuoteNode) -> str:
        """Specific renderring. Render the quote block.

        Arguments
        ---------
        node: `QuoteNode`
            The data to be rendered.

        Returns
        -------
        #1: `str`
            The formatted quote block.
        """
        if not self.is_quote_converted:
            return BBCodeRenderer.render_quote(self, node)
        return "[{0}][{1}]{children}[/{1}][/{0}]\n\n\n".format(
            self.configs.quote,
            self.configs.underline,
            children=self.render_children(node.children),
        )

    @override
    def render_code_block(self, node: CodeBlockNode) -> str:
        """Specific renderring. Render the block code as
        ```
        > ...
        > ...
        > ...
        ```

        Arguments
        ---------
        node: `CodeBlockNode`
            The code block to be rendered.

        Returns
        -------
        #1: `str`
            The rendered code block.
        """
        if not self.is_codeblock_converted:
            return BBCodeRenderer.render_code_block(self, node)
        return super().render_code_block(node)

    @override
    def render_heading(self, node: HeadingNode) -> str:
        """Specific renderring. Render the heading (title).

        Arguments
        ---------
        node: `HeadingNode`
            The data to be rendered.

        Returns
        -------
        #1: `str`
            The formatted heading/title.
        """
        if not self.is_h_converted:
            return BBCodeRenderer.render_heading(self, node)
        content = self.render_children(node.children)
        tag = self.configs.get_h_tag_by_level(1)
        return "[{tag}]{content}[/{tag}]\n".format(tag=tag, content=content)

    @override
    def render_table(self, node: TableNode) -> str:
        """Specific renderring. Render the table.

        This overriden table rendering will convert a table to the following list:
        ```
        [list]
        [*] [b]Header[/b] | [b]Header[/b]

        [*] Cell | Cell
        [/list]
        ```
        When the list needs to be replaced by the ordered list, use the following
        configs:
        ``` python
        configs.table = "ordered"
        ```

        Arguments
        ---------
        node: `TableNode`
            The table to be rendered.

        Returns
        -------
        #1: `str`
            The rendered table bbcode.
        """
        if node.rows and node.rows[0].size == 0:
            rows = [self.__flatten_table_row(row) for row in node.rows if row.size > 0]
            return self.render_list(
                ListNode(ordered="ordered" in self.configs.table, items=rows)
            )
        return super().render_table(node)

    @override
    def render_list(self, node: ListNode) -> str:
        """Specific rendering. Render the ordered or unordered list.

        Arguments
        ---------
        node: `ListNode`
            The list to be rendered.

        Returns
        -------
        #1: `str`
            The rendered list bbcode.
        """
        if node.ordered:
            tag = self.configs.olist
        else:
            tag = self.configs.list

        items = "\n".join(self.render(item) for item in node.items)
        return "[{tag}]\n{items}[/{tag}]\n\n".format(tag=tag, items=items)
