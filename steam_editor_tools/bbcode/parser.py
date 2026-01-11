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

from typing import Any, IO, Generic, TypeVar

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString, PageElement
from markdown_it.main import MarkdownIt

from .nodes import (
    DeletedNode,
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
    AlertNode,
    ListItemNode,
    ListNode,
    TableCellNode,
    TableRowNode,
    TableNode,
    Document,
    Node,
)

from . import plugins
from .renderer import BBCodeRenderer, AlertTitleConfigs


__all__ = ("HandleMemory", "DocumentParser")
_Tag = TypeVar("_Tag", bound=Tag)


class HandleMemory(Generic[_Tag]):
    """Temporary memory designed for parsing the data that may need to handle
    children by customized methods and record special information."""

    def __init__(
        self,
        process_func: collections.abc.Callable[
            [dict[str, Any], str, _Tag], _Tag | None
        ],
    ) -> None:
        """Initialization.

        Arguments
        ---------
        process_func: `(storage, name, node) -> node | None`
            A scope-limited processor function.

            The input arguments are:
            1. storage: The storage provided by this memory. It is mutable and allows
               users to store data during the process_func.
            2. name: The node name pre-processed by `str.casefold`.
            3. node: The bs4 tag node that allows users to extract the data from the
               node.

            It will return the argument `node` if the node should be passed to further
            parsing steps. If it returns `None`, this node will be dropped during the
            parsing.
        """
        self.storage: dict[str, Any] = dict()
        self.__process_func = process_func

    def process(self, name: str, node: _Tag) -> _Tag | None:
        """Run the processing for a specific tag node.

        Arguments
        ---------
        name: `str`
            Equivalent to `tag.name.casefold()`

        node: `Tag`
            The HTML tag node that would be used for catching the data.

        Returns
        -------
        #1: `Tag | None`
            Return `Tag` if it should be further parsed. If this value is `None`,
            the given `node` (including its children) will be dropped in the
            parsed results.
        """
        return self.__process_func(self.storage, name, node)


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
        engine.use(
            plugins.alert.gfm_alerts_plugin,
            titles=set(val for val in AlertTitleConfigs.model_fields.keys()),
            parse_nested=True,
            match_case_sensitive=False,
        )
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
            children_nodes.extend(self._convert_node(child, None))
        children_nodes = self._remove_deleted_children(children_nodes)

        # Optionally, you could merge adjacent TextNodes here if desired.
        return Document(children=children_nodes)

    @staticmethod
    def _parse_style(bs_node: Tag) -> dict[str, str]:
        """(Private) Parse the inline style string as `{prop: value}`.
        * Lowercases property names and trims whitespace.
        * Keeps the original value string (minus outer whitespace).
        """
        result: dict[str, str] = {}
        raw_styles = bs_node.attrs.get("style")
        if raw_styles is None:
            return result

        # Get style list
        if isinstance(raw_styles, str):
            style_list = raw_styles.strip()
        else:
            style_list = list(str(val).strip() for val in raw_styles)

        if not style_list:
            return result

        for style in style_list:
            for decl in style.split(";"):
                decl = decl.strip()
                if not decl:
                    continue
                if ":" not in decl:
                    continue
                prop, value = decl.split(":", 1)
                prop = prop.strip().casefold()
                value = value.strip()
                if not prop:
                    continue
                result[prop] = value
        return result

    @staticmethod
    def _parse_class(bs_node: Tag) -> set[str]:
        """(Private) Parse the classes into a set.

        If the classes are not specified, will return an empty set.
        """
        raw_classes = bs_node.attrs.get("class", None)

        if raw_classes is None:
            return set()

        # Get class set
        if isinstance(raw_classes, str):
            classes = set((raw_classes.strip(),))
        else:
            classes = set(str(val).strip() for val in raw_classes)
        return classes

    @classmethod
    def _is_hidden(cls, bs_node: Tag) -> bool:
        """(Private)
        Check whether a node is explicitly configured as hidden.

        Return True if the node has inline CSS that hides it.
        We only check inline styles because BeautifulSoup does not
        evaluate external CSS.
        """
        attrs = bs_node.attrs
        if attrs is None:
            return False
        if not isinstance(attrs, collections.abc.Mapping):
            return False

        # hidden attribute
        if hasattr(attrs, "hidden"):
            return True

        # aria-hidden
        if str(getattr(attrs, "aria-hidden", "")).casefold() == "true":
            return True

        # inline style
        styles = cls._parse_style(bs_node)
        if not styles:
            return False

        # Check 'display' property
        disp = styles.get("display")
        if disp is not None:
            # Normalize tokens (e.g., "none !important")
            tokens = {
                tok.strip().casefold()
                for tok in disp.replace("!", " !").split()
                if tok.strip()
            }
            if "none" in tokens:
                return True

        # Check 'visibility' property
        vis = styles.get("visibility")
        if vis is not None:
            tokens = {
                tok.strip().casefold()
                for tok in vis.replace("!", " !").split()
                if tok.strip()
            }
            if "hidden" in tokens or "collapse" in tokens:
                return True

        return False

    @staticmethod
    def _is_all_children_deleted(children: list[Node]) -> bool:
        """(Private) Return `True` if all children nodes are marked as deleted."""
        if not children:
            return False
        return all(child.type == "deleted" for child in children)

    @staticmethod
    def _is_line_break(node: Node) -> bool:
        """(Private) Check whether the node is `LineBreakNode` (`<br>`) or
        `Paragraph([])` (`<p></p>`)."""
        if node.type == "br" or (node.type == "paragraph" and (not node.children)):
            return True
        return False

    def _convert_node(
        self, bs_node: PageElement, memory: HandleMemory[Tag] | None
    ) -> list[Node]:
        """(Private)
        Convert a BeautifulSoup node into a list of pydantic Node objects.

        Arguments
        ---------
        bs_node: `PageElement`
            The direct member provided by iterating the `soup.body`.

        memory: `HandleMemory | None`
            The memory used for handling the catched data with in a specific tag.
            This memory is used only for some specific tags. If not used, will
            be `None.

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

        name = bs_node.name.casefold()

        if name == "svg":
            return [DeletedNode()]

        if memory is not None:
            _bs_node = memory.process(name, bs_node)
            if _bs_node is None:
                return [DeletedNode()]
            bs_node = _bs_node

        # Handle general `<div>` blocks
        if name == "div":
            return self._handle_div(bs_node, memory)

        # Block code: <pre><code>...</code></pre> or <pre>...</pre>
        if name == "pre":
            return self._handle_pre(bs_node)

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
            children = self._convert_children(bs_node, None)

            return [
                (
                    DeletedNode()
                    if self._is_all_children_deleted(children)
                    else HeadingNode(level=level, children=children)
                )
            ]

        # Paragraph-like blocks
        if name == "p":
            return self._handle_paragraph(bs_node, memory)

        # Blockquote
        if name == "blockquote":
            return self._handle_quote(bs_node)

        # Lists
        if name in {"ul", "ol"}:
            return self._handle_list(bs_node, is_ordered=(name == "ol"))

        # Tables
        if name == "table":
            return self._handle_tables(bs_node)

        # Inline formatting: bold / italic / underline / strike / spoiler
        res = self._handle_inline_formats(name, bs_node, memory)
        if res is not None:
            return res

        # Generic containers we don't preserve as tags
        # For any tag that isn't explicitly supported, just recurse into its children.
        return self._convert_children(bs_node, memory)

    def _catch_quote_cite(
        self, storage: dict[str, Any], name: str, node: Tag
    ) -> Tag | None:
        """(Private) Catch the `<cite>...</cite>` inside a quote block.

        If multiple `<cite>...</cite>` are provided, will only record the first
        `<cite>`. If there are more `<cite>` tags, will return it as it is.
        """
        if name != "cite":
            return node
        if "cite" in storage:
            return node
        cite_text = " ".join(node.get_text().strip().splitlines())
        storage["cite"] = cite_text
        return None

    def _catch_alert_tag(
        self, storage: dict[str, Any], name: str, node: Tag
    ) -> Tag | None:
        """(Private) Catch the `<div class="md-alert-text">...</div>`
        inside an alert block.

        All such patterns will be catched and removed from the results.
        But only the first appearance will be recorded.
        """
        if name not in ("div", "p", "strong", "b"):
            return node
        classes = self._parse_class(node)

        # Need to find the alert title
        if not set(("md-alert-text", "markdown-alert-title")).intersection(classes):
            return node

        # Do not renew the title if it has already been detected.
        if "title" in storage:
            return None

        title_text = "-".join(node.get_text().strip().splitlines())
        storage["title"] = title_text
        return None

    def _handle_div(self, bs_node: Tag, memory: HandleMemory[Tag] | None) -> list[Node]:
        """(Private) Handle the general `<div>` node."""
        classes = self._parse_class(bs_node)

        # No specific class, bypass and simply unwrap this block.
        if not classes:
            return self._convert_children(bs_node, memory)

        # Alert box
        if set(("md-alert", "markdown-alert")).intersection(classes):
            memory = HandleMemory(self._catch_alert_tag)
            children = self._convert_children(bs_node, memory)
            if self._is_all_children_deleted(children):
                return [DeletedNode()]
            title = memory.storage.get("title")
            if not (isinstance(title, str) and title):
                # Fall back to quote
                return [QuoteNode(children=children)]
            return [AlertNode(children=children, title=title)]

        # Fallback to children
        return self._convert_children(bs_node, memory)

    def _handle_quote(self, bs_node: Tag) -> list[Node]:
        """(Private) Handle quote blocks.

        The quote block may contain `<cite>` tag. Will handle this by memory.
        """
        memory = HandleMemory(self._catch_quote_cite)
        cite = bs_node.attrs.get("cite")
        cite = (
            cite
            if isinstance(cite, str)
            else (" ".join(str(val) for val in cite) if cite is not None else "")
        )
        if cite:
            memory.storage["cite"] = cite.strip()
        children = self._convert_children(bs_node, memory)
        return [
            (
                DeletedNode()
                if self._is_all_children_deleted(children)
                else QuoteNode(
                    children=children, cite=str(memory.storage.get("cite", ""))
                )
            )
        ]

    def _handle_pre(self, bs_node: Tag) -> list[Node]:
        """(Private) Handle code blocks.

        Block code: `<pre><code>...</code></pre>` or `<pre>...</pre>`

        If there is a single `<code>` child, treat its text as the block code.
        """
        code_tag = None
        if len(bs_node.contents) == 1 and isinstance(bs_node.contents[0], Tag):
            child = bs_node.contents[0]
            if child.name and child.name.casefold() == "code":
                code_tag = child

        if code_tag is not None:
            code_text = code_tag.get_text()
        else:
            code_text = bs_node.get_text()

        return [CodeBlockNode(code=code_text)]

    def _handle_list(self, bs_node: Tag, is_ordered: bool = False) -> list[Node]:
        """(Private) Handle ordered and unordered lists.

        Will handle the following special case:
        `<li><p>...</p></li>`
        and convert it as
        `<li>...</li>`

        However, if there are consecutive paragraphs appearing in the same `<li>`,
        such as
        `<li><p>...</p><p>...</p>...</li>`
        The structure will be preserved.
        """
        items: list[ListItemNode] = []
        for li in bs_node.find_all("li", recursive=False):
            item_children = self._convert_children(li, None)
            if self._is_all_children_deleted(item_children):
                continue
            n_children = len(item_children)
            if n_children == 0:
                items.append(ListItemNode(children=item_children))
                continue
            if n_children == 1:
                if item_children[0].type == "paragraph":
                    item_children = item_children[0].children
                items.append(ListItemNode(children=item_children))
                continue
            _item_children: list[Node] = []
            for idx in range(n_children):
                cur_child = item_children[idx]
                if cur_child.type != "paragraph":
                    _item_children.append(cur_child)
                    continue
                if (idx > 0) and (item_children[idx - 1].type == "paragraph"):
                    _item_children.append(cur_child)
                    continue
                if (idx < (n_children - 1)) and (
                    item_children[idx + 1].type == "paragraph"
                ):
                    _item_children.append(cur_child)
                    continue
                _item_children.extend(cur_child.children)
            item_children = _item_children
            items.append(ListItemNode(children=item_children))
        if not items:
            return []
        return [ListNode(ordered=is_ordered, items=items)]

    def _handle_tables(self, bs_node: Tag) -> list[Node]:
        """(Private) Handle the HTML table structure.

        The `<thead>`, `<tbody>` and <tfoot> tags will be unwraped.
        """
        rows: list[TableRowNode] = []

        # Only direct row-like children: <tr> or sections containing <tr>
        for child in bs_node.children:
            if isinstance(child, Tag):
                if child.name.casefold() == "tr":
                    rows.append(self._convert_tr(child))
                elif child.name.casefold() in {"thead", "tbody", "tfoot"}:
                    for tr in child.find_all("tr", recursive=False):
                        rows.append(self._convert_tr(tr))

        if not rows:
            return []
        return [TableNode(rows=rows)]

    def _handle_paragraph(
        self, bs_node: Tag, memory: HandleMemory[Tag] | None
    ) -> list[Node]:
        """(Private) handle the paragraph.

        Will remove all trailing `<br>` because they are not displayed.

        Will not remove leading `<br>` because they are displayed.
        """
        children = self._convert_children(bs_node, memory)
        idx = len(children)
        while idx > 0:
            if children[idx - 1].type != "br":
                break
            idx = idx - 1
        children = children[:idx]
        return [
            (
                DeletedNode()
                if self._is_all_children_deleted(children)
                else ParagraphNode(children=children)
            )
        ]

    def _handle_inline_formats(
        self, name: str, bs_node: Tag, memory: HandleMemory[Tag] | None
    ) -> list[Node] | None:
        """(Private) handle the inline formats.

        Inline formatting: bold / italic / underline / strike / spoiler
        """
        if name in {"b", "strong"}:
            children = self._convert_children(bs_node, memory)
            return [
                (
                    DeletedNode()
                    if self._is_all_children_deleted(children)
                    else BoldNode(children=children)
                )
            ]

        if name in {"i", "em"}:
            children = self._convert_children(bs_node, memory)
            return [
                (
                    DeletedNode()
                    if self._is_all_children_deleted(children)
                    else ItalicNode(children=children)
                )
            ]

        if name in ("u", "ins"):
            children = self._convert_children(bs_node, memory)
            return [
                (
                    DeletedNode()
                    if self._is_all_children_deleted(children)
                    else UnderlineNode(children=children)
                )
            ]

        if name in {"s", "strike", "del"}:
            children = self._convert_children(bs_node, memory)
            return [
                (
                    DeletedNode()
                    if self._is_all_children_deleted(children)
                    else StrikeNode(children=children)
                )
            ]

        if name in {"mark"}:
            children = self._convert_children(bs_node, memory)
            return [
                (
                    DeletedNode()
                    if self._is_all_children_deleted(children)
                    else SpoilerNode(children=children)
                )
            ]

        # Links
        if name == "a":
            href = bs_node.get("href", "")
            if not href:
                # No URL, just unwrap to children
                return self._convert_children(bs_node, memory)
            children = self._convert_children(bs_node, memory)
            return [
                (
                    DeletedNode()
                    if self._is_all_children_deleted(children)
                    else LinkNode(href=str(href), children=children)
                )
            ]

        # No inline formats are found.
        return None

    def _remove_deleted_children(
        self,
        nodes: collections.abc.Sequence[Node],
        remove_leading_br: bool = False,
        remove_trailing_br: bool = False,
    ) -> list[Node]:
        """(Private) Remove `DeletedNode` from the given `nodes`.

        WIll ensure that the returned list does not directly contain a `DeletedNode`.

        `LineBreakNode`s or empty `Paragraph` between a node and a deleted node
        should be removed. However, this processing will not remove leading or
        trailing `[br]` nodes by default.

        If `remove_leading_br` is specified, will remove the leading line breaks.

        If `remove_trailing_br` is specified, will remove the trailing line breaks.
        """
        filtered_nodes: list[Node] = []
        prev_node: Node | None = None
        node_stack: list[Node] = []
        for node in nodes:
            if self._is_line_break(node):
                node_stack.append(node)
                continue
            if (prev_node is None and (not remove_leading_br)) or (
                prev_node is not None
                and prev_node.type != "deleted"
                and node.type != "deleted"
            ):
                filtered_nodes.extend(node_stack)
            node_stack.clear()
            prev_node = node
            if node.type != "deleted":
                filtered_nodes.append(node)
        if (prev_node is None and (not remove_leading_br)) or (
            prev_node is not None
            and (not remove_trailing_br)
            and prev_node.type != "deleted"
        ):
            filtered_nodes.extend(node_stack)
        return filtered_nodes

    def _convert_children(
        self, bs_tag: Tag, memory: HandleMemory[Tag] | None
    ) -> list[Node]:
        """(Private) Iterate the children of an HTML tag, and return the parsed
        nodes as a list.

        Arguments
        ---------
        bs_tag: `Tag`
            The HTML tag that contains children.

        memory: `HandleMemory | None`
            The memory used for handling the catched data with in a specific tag.
            This memory is used only for some specific tags. If not used, will
            be `None.

        Returns
        -------
        #1: `list[Node]`
            A list of parsed children nodes.
        """
        nodes: list[Node] = []
        for child in bs_tag.children:
            nodes.extend(self._convert_node(child, memory))
        # Handle the deleted node.
        if len(nodes) > 0:
            name = bs_tag.name.casefold()
            remove_trailing_br = name in (
                "p",
                "li",
            )
            nodes = self._remove_deleted_children(
                nodes, remove_trailing_br=remove_trailing_br
            )
            if not nodes:
                nodes = [DeletedNode()]
        return nodes

    def _convert_tr(self, tr_tag: Tag) -> TableRowNode:
        """(Private) Iterate the children of an HTML tablle row, and return the
        parsed node.

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
            is_header = cell.name.casefold() == "th"
            cell_children = self._convert_children(cell, None)
            if self._is_all_children_deleted(cell_children):
                cell_children = []
            elif not self.__test_renderer.render_children(cell_children).strip():
                cell_children = []
            cells.append(TableCellNode(header=is_header, children=cell_children))
        return TableRowNode(cells=cells)


if __name__ == "__main__":
    print(DocumentParser().parse_file("./tests/data/example.html"))
