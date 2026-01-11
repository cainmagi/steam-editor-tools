# -*- coding: UTF-8 -*-
"""
Nodes
=====
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
The parsed structured data nodes. The nodes contain the structured text parsed from
other formats (like HTML and Markdown). The nodes only preserve the data that is
needed for reconstructing the BBCode text.
"""

import collections.abc
from typing_extensions import Literal, Annotated

from pydantic import BaseModel, Field


__all__ = (
    "DeletedNode",
    "TextNode",
    "LineBreakNode",
    "HorizontalRuleNode",
    "InlineCodeNode",
    "CodeBlockNode",
    "BoldNode",
    "ItalicNode",
    "UnderlineNode",
    "StrikeNode",
    "SpoilerNode",
    "LinkNode",
    "HeadingNode",
    "ParagraphNode",
    "QuoteNode",
    "AlertNode",
    "ListItemNode",
    "ListNode",
    "TableCellNode",
    "TableRowNode",
    "TableNode",
    "Document",
    "Node",
)


# Temp Nodes


class DeletedNode(BaseModel):
    """Node: Deleted

    A node used for tagging a deleted node.

    It may be created during the parsing, but will be cleared in the final results.
    """

    type: Literal["deleted"] = "deleted"


# Leaf nodes


class TextNode(BaseModel):
    """Node: Text

    Provide the plain text.
    """

    type: Literal["text"] = "text"
    text: str


class LineBreakNode(BaseModel):
    """Node: Line Break

    Provide the hard line break.
    """

    type: Literal["br"] = "br"


class HorizontalRuleNode(BaseModel):
    """Node: Horizontal Rule

    Provide the horizontal rule.
    """

    type: Literal["hr"] = "hr"


class InlineCodeNode(BaseModel):
    """Node: Code (Inline)

    Provide the inline code, to be rendered as [noparse]...[/noparse] in BBCode.
    """

    type: Literal["inline_code"] = "inline_code"
    code: str


class CodeBlockNode(BaseModel):
    """Node: Code (Block)

    Provide the block code, corresponding to
    ```
    <pre><code>...</code></pre>
    ```
    or
    ```
    <pre>...</pre>
    ```

    Intended for `[code]...[/code]` in BBCode.
    """

    type: Literal["code_block"] = "code_block"
    code: str


# Inline formatting


class BoldNode(BaseModel):
    """Node: Bold

    Provide the bold inline format.
    """

    type: Literal["bold"] = "bold"
    children: "list[Node]"


class ItalicNode(BaseModel):
    """Node: Italic

    Provide the italic inline format.
    """

    type: Literal["italic"] = "italic"
    children: "list[Node]"


class UnderlineNode(BaseModel):
    """Node: Underline

    Provide the underline inline format.
    """

    type: Literal["underline"] = "underline"
    children: "list[Node]"


class StrikeNode(BaseModel):
    """Node: Strike

    Provide the strike inline format.
    """

    type: Literal["strike"] = "strike"
    children: "list[Node]"


class SpoilerNode(BaseModel):
    """Node: Spoiler

    Provide the spoiler inline format.

    This format is specially supported by Steam. We use
    ```
    <mark>...</mark>
    ```
    i.e., the highlight text to specify this style.
    """

    type: Literal["spoiler"] = "spoiler"
    children: "list[Node]"


class LinkNode(BaseModel):
    """Node: Link

    Provide the URL, representing the `<a>` tag in HTML.

    Text is usually reconstructed from children during BBCode conversion.
    """

    type: Literal["link"] = "link"
    href: str
    children: "list[Node]"


# Block structure


class HeadingNode(BaseModel):
    """Node: Heading

    Provide the one-liner title block. The level is specified as 1-6 for
    representing `<h1>`-`<h6>`.
    """

    type: Literal["heading"] = "heading"
    level: int = Field(ge=1, le=6)
    children: "list[Node]"


class ParagraphNode(BaseModel):
    """Node: Paragraph

    Provide the paragraph, equivalent to `<p>` in html.
    """

    type: Literal["paragraph"] = "paragraph"
    children: "list[Node]"


class QuoteNode(BaseModel):
    """Node: Quote

    Provide the quote block, representing `<blockquote>` in HTML.
    """

    type: Literal["quote"] = "quote"
    cite: str = ""
    children: "list[Node]"


class AlertNode(BaseModel):
    """Node: Alert

    Provide the alert block, representing the following pattern in HTML:
    ```
    <div class="markdown-alert markdown-alert-caution">
        <p class="markdown-alert-title">Caution</p>
        ...
    </div>
    ```
    which is converted from
    ```
    > [!CAUTION]
    > ...
    ```

    Sometimes, the class names may differ.

    We support this node because it is used for supporting block-style fences like
    ```
    [spoiler]
    ...
    [/spoiler]
    ```
    ```

    """

    type: Literal["alert"] = "alert"
    title: str = "Caution"
    children: "list[Node]"


class ListItemNode(BaseModel):
    """Node: List Item

    Provide the item of a list. This node needs to be a member of `ListNode`.
    """

    type: Literal["list_item"] = "list_item"
    children: "list[Node]"


class ListNode(BaseModel):
    """Node: List

    Provide the ordered or unordered lists.

    `ordered = True` for `<ol>`, `False` for `<ul>`.
    """

    type: Literal["list"] = "list"
    ordered: bool
    items: list[ListItemNode]


# Tables


class TableCellNode(BaseModel):
    """Node: Table Cell

    Provide the table cells.

    `header = True` for `<th>`, `False` for `<td>`.
    """

    type: Literal["table_cell"] = "table_cell"
    header: bool
    children: "list[Node]"


class TableRowNode(BaseModel):
    """Node: Table Row

    Provide the table row.
    """

    type: Literal["table_row"] = "table_row"
    cells: list[TableCellNode]


class TableNode(BaseModel):
    """Node: Table

    Provide the whole table.
    """

    type: Literal["table"] = "table"
    rows: list[TableRowNode]


# Top-level document


class Document(BaseModel):
    """The top-level parsed document.

    This document can be parsed in the following chain:
    ```
    Markdown -> HTML -> Document
    ```

    It is fully structured and ready to be converted to other formats.
    """

    type: Literal["document"] = "document"
    children: "list[Node]"

    def walk(self, func: "collections.abc.Callable[[Node], None]") -> None:
        """Walk from the top to the down of each node in this document.

        The visiting order is depth-first, i.e., the leaf nodes will be
        processed first.

        Arguments
        ---------
        func: `(Node) -> None`
            A function to be applied to each node. This function is a visitor
            that is used for processing the doucment.
        """

        def _walk_node(node: Node) -> None:
            if isinstance(node, (ListNode,)):
                _walk_children(node.items)
            elif isinstance(node, (TableNode,)):
                _walk_children(node.rows)
            elif isinstance(node, (TableRowNode,)):
                _walk_children(node.cells)
            elif isinstance(
                node,
                (
                    BoldNode,
                    ItalicNode,
                    UnderlineNode,
                    StrikeNode,
                    SpoilerNode,
                    LinkNode,
                    HeadingNode,
                    ParagraphNode,
                    QuoteNode,
                    AlertNode,
                    ListItemNode,
                    TableCellNode,
                ),
            ):
                _walk_children(node.children)
            func(node)

        def _walk_children(children: collections.abc.Sequence[Node]):
            for child in children:
                _walk_node(child)

        _walk_children(self.children)


# Discriminated union of all node types
Node = Annotated[
    DeletedNode
    | TextNode
    | LineBreakNode
    | HorizontalRuleNode
    | InlineCodeNode
    | CodeBlockNode
    | BoldNode
    | ItalicNode
    | UnderlineNode
    | StrikeNode
    | SpoilerNode
    | LinkNode
    | HeadingNode
    | ParagraphNode
    | QuoteNode
    | AlertNode
    | ListItemNode
    | ListNode
    | TableCellNode
    | TableRowNode
    | TableNode,
    Field(discriminator="type"),
]
"""The union type of all nodes.

This type does not include `Document`, and can be used in pydantic model
directly.
"""
