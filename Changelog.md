# Steam Editor Tools: Help You Write Guides and Reviews

{:toc}

## CHANGELOG

### 0.4.1 @ 01/26/2026

#### :wrench: Fix

1. Fix: Correct the image width of the exmple `composer_list`.

### 0.4.0 @ 01/26/2026

#### :mega: New

1. Add the extended image composers `stet.improc.composer`. This is the extended `ImageChops` module.
2. Add the image effect `stet.improc.effects` which supports the blending effects of images.
3. Add the image overlay effect `stet.improc.overlays` which supports blending effects covering the image content.
4. Split `stet.improc.rederer.ImageLayer` and its related functionalities into `stet.improc.layer`, where the layer properties are implemented.
5. Refactor the shadow/glow/stroke effects of the text images. Now, these effects are delegated to `ImageLayer`.
6. Provide a new image processing tool `stet.improc.tools.ImageGrids` which is used to stitch images.
7. Provide examples for image composers and image effects.
8. Add tests for image composers and image effects.

#### :wrench: Fix

1. Fix: Correct a typo of `stet.improc.renderer.ImageText` which causes the font failure if the default font is used.

#### :floppy_disk: Change

1. Remove the hard-coded padding for the font layers. If users need padding, now, they need to specify the padding size in the arguments.
2. Use the new code style to refactor the example `create_logo`. Now, this example is simpler.
3. Adjust the font spacing according to the new image layer system.
4. Adjust the font spacing during the tests.

### 0.3.0 @ 01/10/2026

#### :mega: New

1. Add `stet.bbcode.plugins.alert`. This sub-module is fetched from [KyleKing/mdformat-gfm-alerts :octocat:](https://github.com/KyleKing/mdformat-gfm-alerts/tree/32a7314).
2. Support the alert block HTML parsing, and the corresponding BBCode rendering. The configurations can be modified in a customized `stet.bbcode.renderer.BBCodeConfig`.
3. Add a test for validating the structure of `stet.bbcode.nodes.Document`.
4. Add tests for extensive blocks such as `alert` and `quote` with a citation.

#### :wrench: Fix

1. Fix: Fix typos in readme and example files.
2. Fix: Correct docstring of `stet.bbcode.plugins.mark`.
3. Fix: Improve the robustness of the `str` normalization. Prefer `casefold` than `lower` method.

#### :floppy_disk: Change

1. Now, the HTML `<ins>` tag will be converted to `[u]`. In examples, we prefer `<ins>` rather than `<u>` because GitHub does not render `<u>` but render `<ins>`.
2. Optimize the code structure of `stet.bbcode`, especially for the efficiency of `stet.bbcode.plugins.alert`.
3. Update the readme for the new version.

### 0.2.0 @ 01/09/2026

#### :mega: New

1. Add the font search utility: `stet.improc.font`. Now, users can search the system fonts by name.

#### :wrench: Fix

1. Fix: The quantization method for lossless images is not configured in an appropriate way. Now, the image will be quantized by `MAXCOVERAGE` rather than `FASTOCTREE` if possible. This change preserve the quality of the loseless images.
2. Fix: Remove a garbage file `test.json` which was included by accident.
3. Fix: For the dev scirpt `create_test_files.py`, the file `ref-complicated.webp` should not be generated if LaTeX cannot be found.
4. Fix: The `logo.svg` has incompatible feature `transform-origin` which cannot be recognized by many apps. Improve this logo, and regenerate the pixel-based logo with the corrected version.
5. Fix: Fix a typo in the readme file.
6. Fix: Fix the position of the example: `create_a_title_figure.py`.

#### :floppy_disk: Change

1. Add `.env` to the ignore list.
2. Add an example of the underline text in the test file. Some inline tests are also added in `examples/markdown.md`.
3. Allow users to pass `stet.improc.font.FontInfo` to `stet.improc.render.ImageText` directly.
4. Move all `markdown-it` plugins to `stet.bbcode.plugins`. This change is prepared for supporting more plugins in the future.

### 0.1.2 @ 01/07/2026

#### :wrench: Fix

1. Fix: Correct a severe bug causing the pip wheel package to miss the sub-packages.
2. Fix: Correct the text of the `examples/create_logo.py`.

### 0.1.1 @ 01/06/2026

#### :mega: New

1. Support multi-line equation rendering and provide an example.

#### :wrench: Fix

1. Fix: The property `price_overview` of `stet.steaminfo.AppInfo` should be optional because some delisted apps can be queried but do not have a price.
2. Fix: Some complicated LaTeX equation may be truncated by a little bit. Now, it has been corrected by adding paddings.

### 0.1.0 @ 01/06/2026

#### :mega: New

1. Create this project.
2. Finish the first vesion of `bbcode`, `improc`, and `steaminfo` modules.
3. Add configurations `pyproject.toml`.
4. Add the devloper's environment folder `./docker` and the `Dockerfile`.
5. Add the community guideline files: `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, and `SECURITY.md`.
6. Add the issue and pull request templates.
7. Configure the github workflows for publishing the package.
8. Add the banner and adjust the format in the readme.

#### :wrench: Fix

1. Fix: Fix the warning caused by `enum.Enum`.
2. Fix: Correct the bad usage of the font.
3. Fix: Correct the styles of logo and reference images.

#### :floppy_disk: Change

1. Drop the support of `python 3.9` because it is incompatible with the typing system.
2. Finish the docker test and update the display image.
