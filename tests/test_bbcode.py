# -*- coding: UTF-8 -*-
"""
BBCode
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
The tests for the BBCode conversion.
"""

import os
import logging

from typing_extensions import ClassVar

import steam_editor_tools as stet


class TestBBCode:
    """The the text processing of BBCode data.

    Will test:
    1. Conversion from Markdown to `Document`.
    2. Conversion from HTML to `Document`.
    3. Conversion from `Document` to BBCode.
    """

    root_path: ClassVar[str] = os.path.dirname(str(__file__))

    @classmethod
    def get_data_path(cls, file_name: str) -> str:
        """Return the path to a data file."""
        return os.path.join(cls.root_path, "data", file_name)

    def test_bbcode_md_to_document(self) -> None:
        """Test

        Conversion from Markdown to `Document`.
        """
        log = logging.getLogger("steam_editor_tools.test")
        log.info("Load example.md")
        doc = stet.DocumentParser().parse_file(self.get_data_path("example.md"))
        log.debug(doc)
        with open(self.get_data_path("example.json"), "r", encoding="utf-8") as fobj:
            _doc = stet.bbcode.nodes.Document.model_validate_json(fobj.read())
        assert doc == _doc
        log.info("Conversion of example.md is validated.")

    def test_bbcode_html_to_document(self) -> None:
        """Test

        Conversion from HTML to `Document`.
        """
        log = logging.getLogger("steam_editor_tools.test")
        log.info("Load example.html")
        doc = stet.DocumentParser().parse_file(self.get_data_path("example.html"))
        log.debug(doc)
        with open(self.get_data_path("example.json"), "r", encoding="utf-8") as fobj:
            _doc = stet.bbcode.nodes.Document.model_validate_json(fobj.read())
        assert doc == _doc
        log.info("Conversion of example.html is validated.")

    def test_bbcode_document_structure(self) -> None:
        """Test

        Validate that the final document should not contain `DeleteNode`.
        """
        log = logging.getLogger("steam_editor_tools.test")
        log.info("Load example.md")
        doc = stet.DocumentParser().parse_file(self.get_data_path("example.md"))

        seen_node_types: set[str] = set()

        def visitor(node: stet.bbcode.nodes.Node) -> None:
            """Record the node types."""
            seen_node_types.add(node.type)

        doc.walk(visitor)

        log.debug("Seen node types: {0}".format(", ".join(seen_node_types)))
        assert "delete" not in seen_node_types

        log.info("The document node structure is validated.")

    def test_bbcode_document_to_bbcode(self) -> None:
        """Test

        Conversion from `Document` to BBcode.
        """
        log = logging.getLogger("steam_editor_tools.test")
        log.info("Load example.json")
        with open(self.get_data_path("example.json"), "r", encoding="utf-8") as fobj:
            doc = stet.bbcode.nodes.Document.model_validate_json(fobj.read())
        with open(self.get_data_path("example.bbcode"), "r", encoding="utf-8") as fobj:
            _text = fobj.read().strip()
        assert stet.BBCodeRenderer().render(doc).strip() == _text
        log.info("Conversion of example.bbcode is validated.")

    def test_bbcode_extensive_blocks(self) -> None:
        """Test

        Conversion of extensive blocks.
        """
        log = logging.getLogger("steam_editor_tools.test")
        log.info("Load extensive.md")
        doc = stet.DocumentParser().parse_file(self.get_data_path("extensive.md"))
        with open(
            self.get_data_path("extensive.bbcode"), "r", encoding="utf-8"
        ) as fobj:
            _text = fobj.read().strip()
        assert stet.BBCodeRenderer().render(doc).strip() == _text
        log.info("Rendering of extensive blocks is validated.")

    def test_bbcode_customizations(self) -> None:
        """Test

        Conversion of customizations.
        """
        log = logging.getLogger("steam_editor_tools.test")
        log.info("Load extensive.md")
        doc = stet.DocumentParser().parse_file(self.get_data_path("extensive.md"))
        configs = stet.BBCodeConfig(
            quote="QUOTE",
            table="TABLE",
            table_head="td",
            alert=stet.AlertTitleConfigs(note="i", warning="strike", caution="h3"),
        )
        log.debug("Configs: {0}".format(configs))
        with open(
            self.get_data_path("extensive-custom.bbcode"), "r", encoding="utf-8"
        ) as fobj:
            _text = fobj.read().strip()
        assert stet.BBCodeRenderer(configs).render(doc).strip() == _text
        log.info("Rendering of customizations is validated.")

    def test_bbcode_guide_fetch(self) -> None:
        """Test

        Fetch a Steam guide.
        """
        log = logging.getLogger("steam_editor_tools.test")
        guide_id = 1258079393
        log.info("Load guide: {0}".format(1258079393))
        doc = stet.GuideParser().parse(guide_id)
        assert (
            stet.BBCodeRenderer()
            .render(doc)
            .strip()
            .startswith("[h1]Introduction[/h1]")
        )
        log.info("Steam guide fetching is validated.")
