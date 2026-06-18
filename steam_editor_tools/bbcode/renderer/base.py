# -*- coding: UTF-8 -*-
"""
Renderer
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
The implementation of the basic renderer.
"""

import contextlib
import collections.abc

from typing import Generic, TypeVar
from typing_extensions import Self

from pydantic import BaseModel

from ..nodes import (
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
from .configs import BBCodeConfig

__all__ = ("BBCodeRenderer",)
T = TypeVar("T")


class CurrentListNode(BaseModel):
    """The currently maintained list node in the context."""

    node: ListNode
    idx: int = 0


class StackContext(Generic[T]):
    """A context used for preserving a stack of variables."""

    def __init__(self, dtype: type[T]) -> None:
        self.__dtype: type[T] = dtype
        self.__data: list[T] = []

    @property
    def dtype(self) -> type[T]:
        """Property: The type of the context item."""
        return self.__dtype

    @property
    def latest(self) -> T | None:
        """Property: The most recent context value. If nothing is in the context,
        will be `None`."""
        return self.__data[-1] if self.__data else None

    @contextlib.contextmanager
    def stack(self, val: T) -> collections.abc.Generator[Self, None, None]:
        """Add a value to the stack."""
        if not isinstance(val, self.__dtype):
            raise TypeError(
                'The value "{0}" is not typed by {1}.'.format(val, self.__dtype)
            )
        self.__data.append(val)
        try:
            yield self
        finally:
            pop_idx: int | None = None
            for idx in range(len(self.__data) - 1, -1, -1):
                if self.__data[idx] is val:
                    pop_idx = idx
                    break
            if pop_idx is not None:
                self.__data.pop(pop_idx)


class BBCodeRenderer:
    """The BBCode renderer.

    Render the structured `Document` or an intemediate `Node` into the BBCode format.
    """

    __slots__ = ("configs", "__list_context")

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
        self.__list_context: StackContext[CurrentListNode] = StackContext(
            CurrentListNode
        )

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
            with self.__list_context.stack(CurrentListNode(node=node)):
                return self.render_list(node)

        if node.type == "list_item":
            current = self.__list_context.latest
            if current is not None:
                res = self.render_list_item(
                    node,
                    idx=current.idx,
                    parent_node=current.node,
                )
                current.idx = current.idx + 1
                return res
            else:
                return self.render_list_item(node, idx=0)

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
    def render_children(self, children: list[Node]) -> str:
        """Helper method. Render a list of children nodes into BBCode."""
        return "".join(self.render(child) for child in children).strip("\r\n")

    def wrap_children(
        self, children: list[Node], start: str, end: str | None = None
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
        if (not tag) or tag == self.configs.quote:
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

    def render_list_item(
        self, node: ListItemNode, idx: int, parent_node: ListNode | None = None
    ) -> str:
        """Specific renderring. Render the list item.

        The optional argument `idx` is the current index of the item in the list.

        The optional `parent_node` is the nearest unordered/ordered list wrapper
        of this item.
        """
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
