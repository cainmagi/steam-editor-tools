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

from typing_extensions import override
from ..nodes import (
    TextNode,
    CodeBlockNode,
    QuoteNode,
    ListNode,
    ListItemNode,
    TableNode,
    TableRowNode,
    TableCellNode,
)
from .base import BBCodeRenderer

__all__ = ("BBCodeRendererTablePreferred", "BBCodeRendererListPreferred")


class BBCodeRendererTablePreferred(BBCodeRenderer):
    """The BBCode renderer with table format preferred.

    This renderer variant will use the table format when rendering:
    - unordered lists
    - ordered lists

    Such rendering conversions were used when writing reviews previously because the
    lists were not correctly rendered before.

    However, since the Steam major update in 2026, the table is now rendered
    incorrectly. Therefore, currently, it is better to use
    `BBCodeRendererListPreferred`.
    """

    TEXT_IDX = "①②③④⑤⑥⑦⑧⑨⑩"

    def __list_item_to_table_row(
        self, node: ListItemNode, idx: int, parent_node: ListNode | None = None
    ):
        """Render a list item as a table row."""
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
        """Specific renderring. Render the ordered or unordered list."""
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

        The optional argument `idx` is the current index of the item in the list.

        The optional `parent_node` is the nearest unordered/ordered list wrapper
        of this item.
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
    def __pretret_code_leading_space(codes: str, char="⠀"):
        lines = codes.splitlines(keepends=True)
        _lines: list[str] = []
        for line in lines:
            _line = line.lstrip()
            _lines.append(char * (len(line) - len(_line)) + _line)
        return "".join(_lines)

    def __flatten_table_row(self, row: TableRowNode) -> ListItemNode:
        """Convert a table row to a list item."""
        if not isinstance(row, TableRowNode):
            return ListItemNode(children=[TextNode(text=self.render(row))])
        if not row.cells:
            return ListItemNode(children=[])
        if len(row.cells) == 1:
            return ListItemNode(children=[row.cells[0]])
        _row_raw: list[str] = [self.render(cell) for cell in row.cells]
        _row: list[str] = [_row_raw[0]]
        for prev_cell, cell in itertools.pairwise(_row_raw):
            if not cell:
                continue
            if len(cell) < 2 and len(prev_cell) < 2:
                pass
            elif len(cell) < 2:
                _row.append(" ")
            elif len(prev_cell) < 2:
                _row.append(": ")
            else:
                _row.append(" | ")
            _row.append(cell)
        return ListItemNode(children=[TextNode(text="".join(_row))])

    @override
    def render_code_block(self, node: CodeBlockNode) -> str:
        """Specific renderring. Render the block code as
        ```
        [hr][/hr]
        ...
        [hr][/hr]
        ```
        """
        hr = "[{0}][/{0}]".format(self.configs.hr)

        return "{hr}{code}{codebreak}{hr}\n".format(
            hr=hr,
            code=self.__pretret_code_leading_space(node.code),
            codebreak="" if node.code.endswith("\n") else "\n",
        )

    @override
    def render_quote(self, node: QuoteNode) -> str:
        """Specific renderring. Render the quote block."""
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
        """
        rows = [self.__flatten_table_row(row) for row in node.rows]
        return BBCodeRenderer.render_list(
            self, ListNode(ordered="ordered" in self.configs.table, items=rows)
        )

    @override
    def render_table_row(self, node: TableRowNode) -> str:
        """Specific renderring. Render the table row."""
        cells = self.__flatten_table_row(node)
        return "⬊ {cells}\n".format(cells=cells)

    @override
    def render_table_cell(self, node: TableCellNode) -> str:
        """Specific renderring. Render the table cell (head or data cells)."""
        content = self.render_children(node.children)
        if node.header:
            tag = self.configs.bold
            return "[{tag}]{content}[/{tag}]".format(tag=tag, content=content)
        else:
            return "{content}".format(content=content)
