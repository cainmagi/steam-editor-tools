# Steam Editor Tools: Help You Write Guides and Reviews

<p><img alt="Banner" src="https://github.com/cainmagi/steam-editor-tools/blob/main/display/logo-banner.webp?raw=true"></p>

<p align="center">
  <a href="https://github.com/cainmagi/steam-editor-tools/releases/latest"><img alt="GitHub release (latest SemVer)" src="https://img.shields.io/github/v/release/cainmagi/steam-editor-tools?logo=github&sort=semver&style=flat-square"></a>
  <a href="https://github.com/cainmagi/steam-editor-tools/releases"><img alt="GitHub all releases" src="https://img.shields.io/github/downloads/cainmagi/steam-editor-tools/total?logo=github&style=flat-square"></a>
  <a href="https://github.com/cainmagi/steam-editor-tools/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/cainmagi/steam-editor-tools?style=flat-square&logo=opensourceinitiative&logoColor=white"></a>
  <a href="https://pypi.org/project/steam-editor-tools"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/steam-editor-tools?style=flat-square&logo=pypi&logoColor=white&label=pypi"/></a>
</p>
<p align="center">
  <a href="https://github.com/cainmagi/steam-editor-tools/actions/workflows/python-package.yml"><img alt="GitHub Actions (Build)" src="https://img.shields.io/github/actions/workflow/status/cainmagi/steam-editor-tools/python-package.yml?style=flat-square&logo=githubactions&logoColor=white&label=build"></a>
  <a href="https://github.com/cainmagi/steam-editor-tools/actions/workflows/python-publish.yml"><img alt="GitHub Actions (Release)" src="https://img.shields.io/github/actions/workflow/status/cainmagi/steam-editor-tools/python-publish.yml?style=flat-square&logo=githubactions&logoColor=white&label=release"></a>
</p>

This package offers editor tools helping users write Steam guides and reviews.

This package supports:

- Steam information queries
- Image editing tools
- BBCode text processing tools

Users can write their documents with Markdown, use this package to process the images in the document, and convert the document to the Steam BBCode format.

## 1. Install

Intall the **latest released version** of this package by using the PyPI source:

```sh
python -m pip install steam-editor-tools
```

## 2. Usage

The following minimal example shows a simple customization, where we convert a Markdown file into Steam BBCode, and print each header during the conversion.

```python
import os
import steam_editor_tools as stet


class CustomizedRenderer(stet.BBCodeRenderer):
    def render_heading(self, node: stet.bbcode.nodes.HeadingNode) -> str:
        print(self.render_children(node.children))
        return super().render_heading(node)


def convert(file_path: str) -> None:
    out_file_path = os.path.splitext(file_path)[0].strip() + ".bbcode"
    doc = stet.DocumentParser().parse_file(file_path)
    with open(out_file_path, "w", encoding="utf-8") as fobj:
        fobj.write(CustomizedRenderer().render(doc))


convert("example.md")
```

Currently, we support the following features:

### 2.1. Steam information query

| Functionality         | Description                                                                                                                     |
| :-------------------- | :------------------------------------------------------------------------------------------------------------------------------ |
| Search app by name    | Given the partial name of an app (game), search for its information, including the ID. Support fuzzy searching.                 |
| Get app details by ID | Given the app ID, fetch the full details, including the name, description, price, about page, and other information.            |
| Download images       | Use methods such as `get_header_image()` to get the header image, background image, and official screenshots on the store page. |

### 2.2. Image editing tools

| Functionality       | Description                                                                                                                                        |
| :------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------- |
| Image stack         | A code-based image editor, allowing users to stack multiple layers of images, texts, or LaTeX equations with styles.                               |
| Image anchor        | Inspired by LaTeX's TikZ package, this package allows users to place images on the same canvas by using their relative positions.                  |
| Image optimization  | Users only need to specify the quality and the saving format. The package can choose the best way to optimize the saved image size.                |
| Image modifications | Basic image modification tools such as image resizing, cropping and blurring.                                                                      |
| Image effects       | Features mimicing the "Layer blending options" of the image editor, allowing users to add stroke, shadows, and other effects to an existing layer. |
| Thumbnail           | Provide an option to create Steam-compatible thumbnails. This feature is useful when users need to upload screenshots by themselves.               |
| Batch processing    | Walk through a folder, apply a customized image processing function to each image, and save the results with thumbnails in another folder.         |
| Font searching      | Perform fuzzy searches for system or customized fonts. Users can provide a list of fallback options.                                               |

Actually, the title banner of this Readme file is created by the image editing tools. See the examples.

> [!NOTE]
> You need to have a locally installed LaTeX released version like [TeXLive][link-texlive] to use the equation features.

### 2.3. BBCode text processing tools

| Functionality       | Description                                                                                                                                                                       |
| :------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Structured data     | All conversions are divided into two steps: Other formats -> `Document` stucture -> Steam BBCode. The intermediate `Document` strcture is supported by [pydantic][link-pydantic]. |
| HTML to BBCode      | Recursively parse an HTML file, and convert it into `Document` or Steam BBCode.                                                                                                   |
| Markdown to BBCode  | Use [markdown-it][link-markdown-it] to convert a Markdown file to HTML, then convert the HTML to `Document` or BBCode.                                                            |
| Fetch a Steam guide | Given the URL of a Steam guide, convert it into `Document` or BBcode.                                                                                                             |

## 3. Why using this package

1. Compared to other BBCode conversion packages such as [html2bbcode][link-html2bbcode] and [html2phpbbcode][link-html2phpbbcode], our package strictly follows the current Steam BBCode format. Different forums may have different BBCode standards.
2. Compared to [ihroteka-converter][link-ihroteka-converter], we fully support every format provided by Steam. Unlike that regular-expression-based conversion, the BBCode reconstruction in this package is based on a recursive analysis of the HTML structure. Therefore, our package will not omit any text as long as it appears in the original document.
3. We offer flexibility of customization. Users can inject any rendering step of this package by simply overriding the methods of `steam_editor_tools.bbcode.BBCodeRenderer`. For example, we can customize a `BBCodeRenderer` to create a title image for each header.
4. We offer convenient approaches for integrating the store page information into the output data. For example, users can easily convert a store page to BBCode if needed.

## 4. Examples

Currently, we offer the following examples in `./examples` folder:

| Example                      | Description                                                                             |
| :--------------------------- | :-------------------------------------------------------------------------------------- |
| `markdown_to_bbcode`         | A minimal example converting Markdown to BBCode.                                        |
| `save_description_of_a_game` | Save the "about the game" section of a Steam app as an HTML file.                       |
| `download_screenshots`       | Download all official screenshots of a game and create thumbnails of them.              |
| `download_a_guide`           | Fetch a Steam guide and save it as a BBCode file.                                       |
| `create_a_title_figure`      | Customize a figure-based title. Such title images can be inserted into the Steam guide. |
| `create_logo`                | Render the title bar of this readme file.                                               |
| `render_latex_equations`     | Render a LaTeX equation as an image.                                                    |
| `search_font`                | Search the font by name, and use the searched font to render an image.                  |
| `composer_list`              | Generate examples for each image composer, and gather the results as an image.          |
| `effect_list`                | Show the performance of all image layer effects in an image.                            |

The following two guides are written with the help of this tool. Check them for viewing the details:

| Guide                           |                                    Link                                     |
| :------------------------------ | :-------------------------------------------------------------------------: |
| 此后，勇者学会了后验概率        | [:link:](https://steamcommunity.com/sharedfiles/filedetails/?id=3624295321) |
| 《海猫鸣泣之时·出题篇》解（伪） | [:link:](https://steamcommunity.com/sharedfiles/filedetails/?id=2881849336) |

## 5. Documentation

> [!CAUTION]
> This documentation is a work in progress. It should be ready when the package is tested to be stable.

Check the documentation to find more details about the examples and APIs.

https://cainmagi.github.io/steam-editor-tools/

See the articles discussing this tool:

| Article                                               |                                    Link                                     |
| :---------------------------------------------------- | :-------------------------------------------------------------------------: |
| Steam Editor Tools: Help You Write Guides and Reviews | [:link:](https://steamcommunity.com/sharedfiles/filedetails/?id=3641150966) |
| Steam Editor Tools: 帮助你撰写评测和指南              | [:link:](https://steamcommunity.com/sharedfiles/filedetails/?id=3641166480) |

## 6. Contributing

See [CONTRIBUTING.md :book:][link-contributing]

## 7. Changelog

See [Changelog.md :book:][link-changelog]

## 8. Future plan

- [x] HTML/Markdown to BBCode
- [x] Support the conversion of extensive Markdown alert block.
- [x] Multi-layer image synthesis
- [x] Query Steam app ID by name
- [x] Get Steam app details by ID
- [x] Screenshot formatting
- [x] System/User font file detection
- [x] Image overlay with alpha channel
- [x] Image layer properties
- [ ] Improved image anchor interfaces
- [ ] More Steam queries based on public APIs

[tool-git]: https://git-scm.com/downloads
[link-contributing]: https://github.com/cainmagi/steam-editor-tools/blob/main/CONTRIBUTING.md
[link-changelog]: https://github.com/cainmagi/steam-editor-tools/blob/main/Changelog.md
[link-pydantic]: https://docs.pydantic.dev/
[link-markdown-it]: https://markdown-it-py.readthedocs.io/
[link-html2bbcode]: https://github.com/tengattack/html2bbcode.js
[link-html2phpbbcode]: https://github.com/tdiam/html2phpbbcode
[link-ihroteka-converter]: https://github.com/pivoshenko/ihroteka-converter/tree/main
[link-texlive]: https://www.tug.org/texlive/
