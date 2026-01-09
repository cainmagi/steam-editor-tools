# -*- coding: UTF-8 -*-
"""
Parser
======
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
The parser converting the other text formats to the structured data.
"""

import os
import collections.abc

from typing import IO

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString, PageElement
from markdown_it.main import MarkdownIt

from .nodes import (
    TextNode,
    LineBreakNode,
    HorizontalRuleNode,
    InlineCodeNode,
    CodeBlockNode,
    BoldNode,
    ItalicNode,
    UnderlineNode,
    StrikeNode,
    SpoilerNode,
    LinkNode,
    HeadingNode,
    ParagraphNode,
    QuoteNode,
    ListItemNode,
    ListNode,
    TableCellNode,
    TableRowNode,
    TableNode,
    Document,
    Node,
)

from . import plugins
from .renderer import BBCodeRenderer


__all__ = ("DocumentParser",)


class DocumentParser:
    """Document Parser.

    This parser converts the other document formats (like Markdown or HTML) to
    structured pydantic data.
    """

    __slots__ = ("__test_renderer",)

    def __init__(self) -> None:
        """Initialization."""
        self.__test_renderer = BBCodeRenderer()

    def parse_file(
        self, file_path: "str | os.PathLike[str]", encoding: str = "utf-8"
    ) -> Document:
        """Parse a file.

        Arguments
        ---------
        file_path: `str | PathLike[str]`
            The path to the file to be read.

        encoding: `str`
            The encoding when opening the file.

        Returns
        -------
        #1: `Document`
            The parsed structured data.
        """
        ext = os.path.splitext(file_path)[-1].strip().lstrip(".").strip().casefold()
        if ext in ("html", "htm"):
            with open(file_path, "r", encoding=encoding) as fobj:
                return self.parse_html(fobj)
        elif ext == "md":
            with open(file_path, "r", encoding=encoding) as fobj:
                return self.parse_markdown(fobj)

        raise TypeError(
            "The file path does not provide a known file type: {0}".format(file_path)
        )

    def parse_markdown(self, md: str | IO[str]) -> Document:
        """Parse the Markdown data.

        Arguments
        ---------
        md: `str | IO[str]`
            The Markdown text or Markdown file-like object.

        Returns
        -------
        #1: `Document`
            The parsed structured data.
        """
        md = md if isinstance(md, str) else md.read()
        engine = MarkdownIt("gfm-like")
        engine.use(plugins.mark.mark_plugin)
        return self.parse_html(engine.render(md))

    def parse_html(self, html: str | IO[str]) -> Document:
        """Parse the HTML data.

        Arguments
        ---------
        md: `str | IO[str]`
            The HTML text or HTML file-like object.

        Returns
        -------
        #1: `Document`
            The parsed structured data.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Use <body> if present, otherwise the whole soup
        root = soup.body or soup

        children_nodes: list[Node] = []
        for child in root.children:
            children_nodes.extend(self._convert_node(child))

        # Optionally, you could merge adjacent TextNodes here if desired.
        return Document(children=children_nodes)

    @staticmethod
    def _parse_style(style: str) -> dict[str, str]:
        """
        Parse an inline style string into a dict: {prop: value}.
        - Lowercases property names and trims whitespace.
        - Keeps the original value string (minus outer whitespace).
        """
        result: dict[str, str] = {}
        if not style:
            return result

        for decl in style.split(";"):
            decl = decl.strip()
            if not decl:
                continue
            if ":" not in decl:
                continue
            prop, value = decl.split(":", 1)
            prop = prop.strip().lower()
            value = value.strip()
            if not prop:
                continue
            result[prop] = value
        return result

    @classmethod
    def _is_hidden(cls, bs_node: Tag) -> bool:
        """(Private)
        Check whether a node is explicitly configured as hidden.

        Return True if the node has inline CSS that hides it.
        We only check inline styles because BeautifulSoup does not
        evaluate external CSS.
        """
        attrs = getattr(bs_node, "attrs", None)
        if attrs is None:
            return False
        if not isinstance(attrs, collections.abc.Mapping):
            return False

        # hidden attribute
        if hasattr(attrs, "hidden"):
            return True

        # aria-hidden
        if str(getattr(attrs, "aria-hidden", "")).lower() == "true":
            return True

        # inline style
        style_raw = attrs.get("style")
        if not style_raw:
            return False

        styles = cls._parse_style(style_raw)
        if not styles:
            return False

        # Check 'display' property
        disp = styles.get("display")
        if disp is not None:
            # Normalize tokens (e.g., "none !important")
            tokens = {
                tok.strip().lower()
                for tok in disp.replace("!", " !").split()
                if tok.strip()
            }
            if "none" in tokens:
                return True

        # Check 'visibility' property
        vis = styles.get("visibility")
        if vis is not None:
            tokens = {
                tok.strip().lower()
                for tok in vis.replace("!", " !").split()
                if tok.strip()
            }
            if "hidden" in tokens or "collapse" in tokens:
                return True

        return False

    def _convert_node(self, bs_node: PageElement) -> list[Node]:
        """(Private)
        Convert a BeautifulSoup node into a list of pydantic Node objects.

        Arguments
        ---------
        bs_node: `PageElement`
            The direct member provided by iterating the `soup.body`.

        Returns
        -------
        #1: `list[Node]`
            A list to make it easy to "unwrap" tags we don't preserve.
        """
        if isinstance(bs_node, NavigableString):
            text = str(bs_node).strip("\r\n")
            if not text:
                return []
            # You might want to normalize whitespace depending on your needs.
            return [TextNode(text=text)]

        if not isinstance(bs_node, Tag):
            return []

        if self._is_hidden(bs_node):
            return []

        name = bs_node.name.lower()

        # Block code: <pre><code>...</code></pre> or <pre>...</pre>
        if name == "pre":
            # If there is a single <code> child, treat its text as the block code.
            code_tag = None
            if len(bs_node.contents) == 1 and isinstance(bs_node.contents[0], Tag):
                child = bs_node.contents[0]
                if child.name and child.name.lower() == "code":
                    code_tag = child

            if code_tag is not None:
                code_text = code_tag.get_text()
            else:
                code_text = bs_node.get_text()

            return [CodeBlockNode(code=code_text)]

        # Inline code: <code> outside of <pre>
        if name == "code":
            code_text = bs_node.get_text()
            return [InlineCodeNode(code=code_text)]

        # Line breaks and horizontal rules
        if name == "br":
            return [LineBreakNode()]

        if name == "hr":
            return [HorizontalRuleNode()]

        # Headings h1-h6
        if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(name[1])
            children = self._convert_children(bs_node)
            return [HeadingNode(level=level, children=children)]

        # Paragraph-like blocks
        if name == "p":
            children = self._convert_children(bs_node)
            return [ParagraphNode(children=children)]

        # Blockquote
        if name == "blockquote":
            children = self._convert_children(bs_node)
            cite = bs_node.attrs.get("cite")
            cite = str(cite) if cite is not None else ""
            return [QuoteNode(children=children, cite=cite)]

        # Lists
        if name in {"ul", "ol"}:
            ordered = name == "ol"
            items: list[ListItemNode] = []
            for li in bs_node.find_all("li", recursive=False):
                item_children = self._convert_children(li)
                n_children = len(item_children)
                if n_children > 1:
                    _item_children: list[Node] = []
                    for idx in range(n_children):
                        cur_child = item_children[idx]
                        if cur_child.type != "paragraph":
                            _item_children.append(cur_child)
                            continue
                        if idx > 0:
                            if item_children[idx - 1].type == "paragraph":
                                _item_children.append(cur_child)
                                continue
                        if idx < (n_children - 1):
                            if item_children[idx + 1].type == "paragraph":
                                _item_children.append(cur_child)
                                continue
                        _item_children.extend(cur_child.children)
                    item_children = _item_children
                elif n_children == 1:
                    if item_children[0].type == "paragraph":
                        item_children = item_children[0].children
                items.append(ListItemNode(children=item_children))
            if not items:
                return []
            return [ListNode(ordered=ordered, items=items)]

        # Tables
        if name == "table":
            rows: list[TableRowNode] = []

            # Only direct row-like children: <tr> or sections containing <tr>
            for child in bs_node.children:
                if isinstance(child, Tag):
                    if child.name.lower() == "tr":
                        rows.append(self._convert_tr(child))
                    elif child.name.lower() in {"thead", "tbody", "tfoot"}:
                        for tr in child.find_all("tr", recursive=False):
                            rows.append(self._convert_tr(tr))

            if not rows:
                return []
            return [TableNode(rows=rows)]

        # Inline formatting: bold / italic / underline / strike / spoiler
        if name in {"b", "strong"}:
            children = self._convert_children(bs_node)
            return [BoldNode(children=children)]

        if name in {"i", "em"}:
            children = self._convert_children(bs_node)
            return [ItalicNode(children=children)]

        if name == "u":
            children = self._convert_children(bs_node)
            return [UnderlineNode(children=children)]

        if name in {"s", "strike", "del"}:
            children = self._convert_children(bs_node)
            return [StrikeNode(children=children)]

        if name in {"mark"}:
            children = self._convert_children(bs_node)
            return [SpoilerNode(children=children)]

        # Links
        if name == "a":
            href = bs_node.get("href", "")
            if not href:
                # No URL, just unwrap to children
                return self._convert_children(bs_node)
            children = self._convert_children(bs_node)
            return [LinkNode(href=str(href), children=children)]

        # Generic containers we don't preserve as tags
        # For any tag that isn't explicitly supported, just recurse into its children.
        return self._convert_children(bs_node)

    def _convert_children(self, bs_tag: Tag) -> list[Node]:
        """(Private)
        Iterate the children of an HTML tag, and return the parsed nodes as a list.

        Arguments
        ---------
        bs_tag: `Tag`
            The HTML tag that contains children.

        Returns
        -------
        #1: `list[Node]`
            A list of parsed children nodes.
        """
        nodes: list[Node] = []
        for child in bs_tag.children:
            nodes.extend(self._convert_node(child))
        return nodes

    def _convert_tr(self, tr_tag: Tag) -> TableRowNode:
        """(Private)
        Iterate the children of an HTML tablle row, and return the parsed node.

        Arguments
        ---------
        bs_tag: `Tag`
            The HTML tag that contains table cells.

        Returns
        -------
        #1: `TableRowNode`
            The parsed table row node where there should be several cells.
        """
        cells: list[TableCellNode] = []
        for cell in tr_tag.find_all(["td", "th"], recursive=False):
            is_header = cell.name.lower() == "th"
            cell_children = self._convert_children(cell)
            if not self.__test_renderer.render_children(cell_children).strip():
                cell_children = []
            cells.append(TableCellNode(header=is_header, children=cell_children))
        return TableRowNode(cells=cells)


if __name__ == "__main__":
    print(DocumentParser().parse_file("./tests/data/example.html"))
