# -*- coding: UTF-8 -*-
"""
Guide Parser
============
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
This module provides the utilities for parsing a Steam guide as `Document`.

Note that the implementation of this module is based on customized parsing of the
fetched HTML text. Steam itself does not offer a BBCode access API.
"""

from typing import TypeVar

import httpx

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString, PageElement

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
    QuoteNode,
    ListItemNode,
    ListNode,
    TableCellNode,
    TableRowNode,
    TableNode,
    Document,
    Node,
)

_Node = TypeVar("_Node", bound=Node)


class GuideParser:
    """Parser for Steam Guide.

    Pass the HTML file or URL of a Steam Guide. This parser will convert the guide to
    `Document`.

    Note that the Steam rendering for the guide is heavily dependent to `<div>` tag.
    The reconstructions for line breaks in this parse may not be perfect.
    """

    def parse(self, url: str | int) -> Document:
        """Parse a guide.

        Arguments
        ---------
        url: `str | int`
            The full Steam guide URL or its numeric ID. If an ID is given, the full
            URL will be

            `https://steamcommunity.com/sharedfiles/filedetails/?id=<url>`

        Returns
        -------
        #1: `Document`
            The structured data reconstructed from the given guide.
        """
        if isinstance(url, int):
            url = "https://steamcommunity.com/sharedfiles/filedetails/?id={0}".format(
                url
            )

        r = httpx.get(url, timeout=10)
        r.raise_for_status()
        data = r.text
        return self.parse_html(data)

    def parse_html(self, html: str) -> Document:
        """Parse the HTML content. The HTML content should be fetched from a Steam
        guide.

        Arguments
        ---------
        html: `str`
            The HTML content to be parsed.

        Returns
        -------
        #1: `Document`
            The structured data reconstructed from the given guide.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Adjust this root selection as needed (full guide page vs section)
        root = soup.select_one("div.guide.subSections")
        if root is None:
            raise ValueError("The Steam Guide body is not found in the given HTML.")
        children = self._normalize_children(self._convert(root))

        return Document(children=children)

    def _normalize(self, node: _Node) -> _Node:
        """(private) Normalize a node by

        * Collapse consecutive `LineBreakNode`;
        * Remove trailing `LineBreakNode` inside `ListItemNode` and `TableCellNode`;
        * Recursively normalize children.
        """
        # Nodes without children
        if isinstance(
            node,
            (
                TextNode,
                LineBreakNode,
                HorizontalRuleNode,
                InlineCodeNode,
                CodeBlockNode,
            ),
        ):
            return node

        # Nodes with items.
        if isinstance(node, (ListNode,)):
            node.items = self._normalize_children(node.items)

        # Nodes with children
        children = getattr(node, "children", None)
        if children is not None:
            setattr(node, "children", self._normalize_children(children))

        # Special cases: ListItemNode, TableCellNode
        if isinstance(node, (ListItemNode, TableCellNode)):
            # Remove trailing <br>
            while node.children and isinstance(node.children[-1], LineBreakNode):
                node.children.pop()

        return node

    def _normalize_children(self, children: list[_Node]) -> list[_Node]:
        """(private) Normalize a list of children

        * Recursively normalize each child;
        * Collapse consecutive `LineBreakNode`.
        """
        out = []
        prev_was_br = False

        for child in children:
            child = self._normalize(child)

            if isinstance(child, LineBreakNode):
                if prev_was_br:
                    # skip duplicate
                    continue
                prev_was_br = True
                out.append(child)
            else:
                prev_was_br = False
                out.append(child)

        return out

    def _convert(self, bs_node: PageElement) -> list[Node]:
        """(private) Unified recursive parser.

        Every HTML node is handled here.

        Returns
        -------
        #1: `list[Node]`
            The parsed structured `Node`.
        """

        if isinstance(bs_node, NavigableString):
            text = str(bs_node).strip("\r\n")
            if text.strip():
                return [TextNode(text=text)]
            return []

        if not isinstance(bs_node, Tag):
            return []

        name = bs_node.name
        classes = bs_node.get("class", None)
        if classes is None:
            classes = []

        if name == "br":
            return [LineBreakNode()]

        if name == "hr" or "bb_hr" in classes:
            return [HorizontalRuleNode()]

        if name == "div":
            # Handle the line break for each section.
            if "style" in bs_node.attrs and "clear:" in bs_node.attrs["style"]:
                return [LineBreakNode()]

            # Handle the section title.
            if "subSectionTitle" in classes:
                return [
                    HeadingNode(
                        level=1, children=[TextNode(text=bs_node.get_text(strip=True))]
                    )
                ]

            # Handle normal titles.
            for c in classes:
                if c.startswith("bb_h"):
                    try:
                        level = int(c[4:])
                    except ValueError:
                        continue
                    level = max(1, min(6, level))
                    children = self._convert_children(bs_node)
                    return [HeadingNode(level=level, children=children)]

        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(name[1])
            children = self._convert_children(bs_node)
            return [HeadingNode(level=level, children=children)]

        if name == "pre" or "bb_code" in classes:
            code = bs_node.get_text()
            return [CodeBlockNode(code=code)]

        if name == "code":
            return [InlineCodeNode(code=bs_node.get_text())]

        if name == "mark":
            return [SpoilerNode(children=self._convert_children(bs_node))]

        if name in ("b", "strong"):
            return [BoldNode(children=self._convert_children(bs_node))]

        if name in ("i", "em"):
            return [ItalicNode(children=self._convert_children(bs_node))]

        if name == "u":
            return [UnderlineNode(children=self._convert_children(bs_node))]

        if name in ("s", "strike"):
            return [StrikeNode(children=self._convert_children(bs_node))]

        if name == "a":
            href = str(bs_node.get("href", ""))
            return [LinkNode(href=href, children=self._convert_children(bs_node))]

        if name == "ul":
            return [self._parse_list(bs_node, ordered=False)]

        if name == "ol":
            return [self._parse_list(bs_node, ordered=True)]

        if name == "li":
            return [ListItemNode(children=self._convert_children(bs_node))]

        if name == "table" or "bb_table" in classes:
            return [self._parse_table(bs_node)]

        if name == "blockquote" or "bb_quote" in classes:
            return [QuoteNode(cite="", children=self._convert_children(bs_node))]

        return self._convert_children(bs_node)

    def _convert_children(self, bs_node: Tag) -> list[Node]:
        """(private) Convert the children of a `Tag` node.

        Unlike a general `PageElement` node, the `Tag` node will not be pure text.
        Therefore, it contains children in most cases.
        """
        result = []
        for child in bs_node.children:
            result.extend(self._convert(child))
        return result

    def _parse_list(self, list_tag: Tag, ordered: bool) -> ListNode:
        """(private) Convert the HTML list (`<ul>` and `<ol>`)

        These cases need to be handled specially because the list nodes
        will always have `ListItemNode` children.

        Arguments
        ---------
        list_tag: `Tag`
            The bs4 tag to be parsed.

        ordered: `bool`
            If specified, this list will be treated as `<ol>`.

            Otherwise, it will be interpreted as `<ul>`.

        Returns
        -------
        #1: `ListNode`
            The parsed `ListNode`.
        """
        items: list[ListItemNode] = []

        for child in list_tag.children:
            # Ignore pure whitespace
            if isinstance(child, NavigableString):
                if not child.strip():
                    continue
                # Text directly under <ul>/<ol> → implicit item
                items.append(
                    ListItemNode(children=[TextNode(text=str(child).strip("\r\n"))])
                )
                continue

            if not isinstance(child, Tag):
                continue

            if child.name == "li":
                # This is the key: we *wrap* convert_children(li) in ListItemNode.
                item_children = self._convert_children(child)
                items.append(ListItemNode(children=item_children))
            else:
                # Any non-<li> child inside a list is weird HTML, but we still handle it.
                # Option A: flatten it into an implicit list item
                item_children = self._convert(child)  # list[Node]
                if item_children:
                    items.append(ListItemNode(children=item_children))

        return ListNode(ordered=ordered, items=items)

    def _parse_table(self, el: Tag) -> TableNode:
        """(private) Convert the HTML table.

        Supports real `<table>` markup and Steam's `<div class="bb_table">`
        version.
        """
        rows: list[TableRowNode] = []

        # Handle both <tr> and div.bb_table_tr
        tr_candidates = []
        if el.name == "table":
            tr_candidates = el.find_all("tr", recursive=False)
        # Steam's div-based structure
        tr_candidates.extend(el.find_all("div", class_="bb_table_tr", recursive=False))

        for tr in tr_candidates:
            cells: list[TableCellNode] = []

            td_candidates = []
            # Real table cells
            td_candidates.extend(tr.find_all(["td", "th"], recursive=False))
            # Steam cells
            td_candidates.extend(
                tr.find_all(
                    "div", class_=["bb_table_td", "bb_table_th"], recursive=False
                )
            )

            for td in td_candidates:
                classes = td.get("class", [])
                header = td.name == "th" or "bb_table_th" in classes
                children = self._convert(td)
                cells.append(TableCellNode(header=header, children=children))

            rows.append(TableRowNode(cells=cells))

        return TableNode(rows=rows)


if __name__ == "__main__":
    from .renderer import BBCodeRenderer

    doc = GuideParser().parse(3616975229)
    with open("test.json", "w", encoding="utf-8") as fobj:
        fobj.write(doc.model_dump_json(indent=2))

    with open("test.bbcode", "w", encoding="utf-8") as fobj:
        fobj.write(BBCodeRenderer().render(doc))
