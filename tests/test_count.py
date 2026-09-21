# -*- coding: UTF-8 -*-
"""
Count
======
@ Steam Editor Tools - Tests

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The tests for counting the sizes of the BBCode units.
"""

import logging

from steam_editor_tools.bbcode import nodes


class TestCountBBCode:
    """The the text processing of BBCode data.

    Will test:
    1. Count of inline units.
    2. Count of hybrid text segments (paragraphs).
    3. Count of list content.
    4. Count of table content.
    """

    def test_count_inline(self) -> None:
        """Test

        Count of inline units.
        """
        log = logging.getLogger("steam_editor_tools.test")

        log.info("Test the pure text node: {0}".format(nodes.TextNode.__name__))
        _text = "Example Text!"
        text = nodes.TextNode(text=_text)
        assert text.pure_text == _text
        assert text.size == len(_text)

        cls_list = [
            nodes.BoldNode,
            nodes.ItalicNode,
            nodes.UnderlineNode,
            nodes.StrikeNode,
            nodes.SpoilerNode,
            nodes.ParagraphNode,
            nodes.QuoteNode,
            nodes.AlertNode,
        ]
        for _cls in cls_list:
            log.info("Test the inline text node: {0}".format(_cls.__name__))
            node = _cls(children=[text])
            assert node.pure_text == _text
            assert node.size == len(_text)
            node = _cls(children=[text, text])
            assert node.pure_text == _text + _text
            assert node.size == 2 * len(_text)

        log.info("Test the inline text node: {0}".format(nodes.LinkNode.__name__))
        node = nodes.LinkNode(children=[text], href="#")
        assert node.pure_text == _text
        assert node.size == len(_text)

        log.info("Test the inline text node: {0}".format(nodes.HeadingNode.__name__))
        node = nodes.HeadingNode(children=[text], level=2)
        assert node.pure_text == _text
        assert node.size == len(_text)

    def test_count_mix(self) -> None:
        """Test

        Count of hybrid text segments.
        """
        log = logging.getLogger("steam_editor_tools.test")

        log.info("Test the mixed Paragraph node.")
        _texts = [
            "Example Text! ",
            "Bold example",
            " text ",
            "A link",
            " test italic",
            " test underline",
        ]
        texts = [
            nodes.TextNode(text=_texts[0]),
            nodes.BoldNode(children=[nodes.TextNode(text=_texts[1])]),
            nodes.TextNode(text=_texts[2]),
            nodes.LinkNode(href="#", children=[nodes.TextNode(text=_texts[3])]),
            nodes.ItalicNode(children=[nodes.TextNode(text=_texts[4])]),
            nodes.UnderlineNode(children=[nodes.TextNode(text=_texts[5])]),
        ]
        _para = "".join(_texts)
        para = nodes.ParagraphNode(children=texts)
        assert para.pure_text == _para
        assert para.size == len(_para)

        para = nodes.ParagraphNode(
            children=[para, nodes.LineBreakNode(), nodes.DeletedNode(), texts[0]]
        )
        assert para.pure_text == _para + _texts[0]
        assert para.size == len(_para) + len(_texts[0])

    def test_count_list(self) -> None:
        """Test

        Count of list content.
        """
        log = logging.getLogger("steam_editor_tools.test")

        items = [
            nodes.ListItemNode(children=[nodes.TextNode(text="Example 1")]),
            nodes.ListItemNode(children=[nodes.TextNode(text="Second Item.")]),
            nodes.ListItemNode.model_validate(
                dict(
                    children=[
                        nodes.BoldNode(children=[nodes.TextNode(text="Strong text")]),
                        nodes.TextNode(text=" mixed text item."),
                    ]
                )
            ),
        ]

        log.info("Test the unordered list node.")
        node = nodes.ListNode(items=items, ordered=False)
        assert node.pure_text == "".join([item.pure_text for item in items])
        assert node.size == sum([item.size for item in items])

        log.info("Test the ordered list node.")
        node = nodes.ListNode(items=items, ordered=True)
        assert node.pure_text == "".join([item.pure_text for item in items])
        assert node.size == sum([item.size for item in items])

    def test_count_table(self) -> None:
        """Test

        Count of table content.
        """
        log = logging.getLogger("steam_editor_tools.test")

        log.info("Test an empty row.")
        row_1 = nodes.TableRowNode(cells=[])
        assert row_1.size == 0
        assert row_1.pure_text == ""

        log.info("Test a row with all cells empty.")
        row_2 = nodes.TableRowNode(
            cells=[
                nodes.TableCellNode(header=False, children=[]),
                nodes.TableCellNode(header=True, children=[]),
                nodes.TableCellNode(header=False, children=[]),
            ]
        )
        assert row_2.size == 0
        assert row_2.pure_text == ""

        log.info("Test another row with all cells empty.")
        row_3 = nodes.TableRowNode(
            cells=[
                nodes.TableCellNode(header=False, children=[nodes.TextNode(text="")]),
                nodes.TableCellNode.model_validate(
                    dict(
                        header=True,
                        children=[nodes.BoldNode(children=[nodes.TextNode(text="")])],
                    )
                ),
                nodes.TableCellNode(
                    header=False, children=[nodes.TableNode(rows=[row_1])]
                ),
            ]
        )
        assert row_3.size == 0
        assert row_3.pure_text == ""

        log.info("Test a non-empty row.")
        row_4 = nodes.TableRowNode(
            cells=[
                nodes.TableCellNode(
                    header=False, children=[nodes.TextNode(text="Text 1")]
                ),
                nodes.TableCellNode.model_validate(
                    dict(
                        header=True,
                        children=[
                            nodes.BoldNode(children=[nodes.TextNode(text="sentence.")])
                        ],
                    )
                ),
            ]
        )
        _text = "Text 1" + "sentence."
        assert row_4.size == len(_text)
        assert row_4.pure_text == _text

        log.info("Test a table.")
        table = nodes.TableNode(rows=[row_1, row_4, row_2, row_3, row_4])
        assert table.size == 2 * row_4.size
        assert table.pure_text == 2 * row_4.pure_text
