import type {SidebarsConfig} from "@docusaurus/plugin-content-docs";

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorial: [
    "introduction",
    "tutorial/install",
    {
      type: "category",
      label: "BBCode",
      collapsed: false,
      link: {
        type: "generated-index",
        title: "Use Steam Editor Tools",
        slug: "/category/bbcode",
        description:
          "Use Steam Editor Tools to render BBCode files from other formats.",
      },
      items: [
        "tutorial/bbcode/get-started",
        "tutorial/bbcode/special-rendering",
        "tutorial/bbcode/customization",
        "tutorial/bbcode/formats",
      ],
    },
    {
      type: "category",
      label: "Image Processing",
      collapsed: false,
      link: {
        type: "generated-index",
        title: "Process and render images",
        slug: "/category/improc",
        description:
          "Use Steam Editor Tools to process and render images with codes.",
      },
      items: [
        "tutorial/improc/get-started",
        "tutorial/improc/latex-equations",
        "tutorial/improc/search-fonts",
        "tutorial/improc/effects",
      ],
    },
    {
      type: "category",
      label: "Steam Infomation",
      collapsed: false,
      link: {
        type: "generated-index",
        title: "Query, fetch, and render Steam information",
        slug: "/category/steaminfo",
        description:
          "Use Steam Editor Tools to acquire information from Steam public APIs and pages without requiring an API key.",
      },
      items: [
        "tutorial/steaminfo/app-details",
        "tutorial/steaminfo/achievements",
      ],
    },
    "tutorial/examples",
    "license",
  ],

  apis: [
    "apis/index",
    {
      type: "category",
      label: "bbcode",
      collapsed: true,
      link: {
        type: "doc",
        id: "apis/bbcode/index",
      },
      items: [
        {
          type: "category",
          label: "parser",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/bbcode/parser/index",
          },
          items: [
            "apis/bbcode/parser/DocumentParser",
            "apis/bbcode/parser/HandleMemory",
          ],
        },
        {
          type: "category",
          label: "guide",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/bbcode/guide/index",
          },
          items: ["apis/bbcode/guide/GuideParser"],
        },
        {
          type: "category",
          label: "renderer",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/bbcode/renderer/index",
          },
          items: [
            {
              type: "category",
              label: "base",
              collapsed: true,
              link: {
                type: "doc",
                id: "apis/bbcode/renderer/base/index",
              },
              items: ["apis/bbcode/renderer/base/BBCodeRenderer"],
            },
            {
              type: "category",
              label: "configs",
              collapsed: true,
              link: {
                type: "doc",
                id: "apis/bbcode/renderer/configs/index",
              },
              items: [
                "apis/bbcode/renderer/configs/BBCodeConfig",
                "apis/bbcode/renderer/configs/AlertTitleConfigs",
              ],
            },
            {
              type: "category",
              label: "variants",
              collapsed: true,
              link: {
                type: "doc",
                id: "apis/bbcode/renderer/variants/index",
              },
              items: [
                "apis/bbcode/renderer/variants/BBCodeRendererTablePreferred",
                "apis/bbcode/renderer/variants/BBCodeRendererListPreferred",
                "apis/bbcode/renderer/variants/BBCodeRendererForReview",
              ],
            },
          ],
        },
        {
          type: "category",
          label: "nodes",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/bbcode/nodes/index",
          },
          items: [
            "apis/bbcode/nodes/DeletedNode",
            "apis/bbcode/nodes/TextNode",
            "apis/bbcode/nodes/LineBreakNode",
            "apis/bbcode/nodes/HorizontalRuleNode",
            "apis/bbcode/nodes/InlineCodeNode",
            "apis/bbcode/nodes/CodeBlockNode",
            "apis/bbcode/nodes/BoldNode",
            "apis/bbcode/nodes/ItalicNode",
            "apis/bbcode/nodes/UnderlineNode",
            "apis/bbcode/nodes/StrikeNode",
            "apis/bbcode/nodes/SpoilerNode",
            "apis/bbcode/nodes/LinkNode",
            "apis/bbcode/nodes/HeadingNode",
            "apis/bbcode/nodes/ParagraphNode",
            "apis/bbcode/nodes/QuoteNode",
            "apis/bbcode/nodes/AlertNode",
            "apis/bbcode/nodes/ListItemNode",
            "apis/bbcode/nodes/ListNode",
            "apis/bbcode/nodes/TableCellNode",
            "apis/bbcode/nodes/TableRowNode",
            "apis/bbcode/nodes/TableNode",
            "apis/bbcode/nodes/Document",
            "apis/bbcode/nodes/Node",
          ],
        },
        {
          type: "category",
          label: "plugins",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/bbcode/plugins/index",
          },
          items: [
            {
              type: "category",
              label: "alert",
              collapsed: true,
              link: {
                type: "doc",
                id: "apis/bbcode/plugins/alert/index",
              },
              items: [
                "apis/bbcode/plugins/alert/AlertRuleFactory",
                "apis/bbcode/plugins/alert/gfm_alerts_plugin",
              ],
            },
            {
              type: "category",
              label: "mark",
              collapsed: true,
              link: {
                type: "doc",
                id: "apis/bbcode/plugins/mark/index",
              },
              items: ["apis/bbcode/plugins/mark/mark_plugin"],
            },
          ],
        },
      ],
    },
    {
      type: "category",
      label: "improc",
      collapsed: true,
      link: {
        type: "doc",
        id: "apis/improc/index",
      },
      items: [
        {
          type: "category",
          label: "font",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/improc/font/index",
          },
          items: [
            "apis/improc/font/FontLanguage",
            "apis/improc/font/FontLocator",
            "apis/improc/font/FontInfo",
            "apis/improc/font/FontNameInfo",
            "apis/improc/font/FontIndexList",
          ],
        },
        {
          type: "category",
          label: "data",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/improc/data/index",
          },
          items: [
            "apis/improc/data/ImageFontAbsSize",
            "apis/improc/data/ImageFontSize",
            "apis/improc/data/ImageFormat",
            "apis/improc/data/ImageQuality",
            "apis/improc/data/ImageAnchor",
            "apis/improc/data/TeXTemplate",
            "apis/improc/data/Templates",
          ],
        },
        {
          type: "category",
          label: "composer",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/improc/composer/index",
          },
          items: [
            "apis/improc/composer/ImageComposer",
            "apis/improc/composer/ImageComposerMode",
          ],
        },
        {
          type: "category",
          label: "renderer",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/improc/renderer/index",
          },
          items: [
            "apis/improc/renderer/ImageSingle",
            "apis/improc/renderer/ImageText",
            "apis/improc/renderer/ImageTeX",
            "apis/improc/renderer/ImageMultiLayer",
          ],
        },
        {
          type: "category",
          label: "latex_to_img",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/improc/latex_to_img/index",
          },
          items: ["apis/improc/latex_to_img/TeXRenderer"],
        },
        {
          type: "category",
          label: "layer",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/improc/layer/index",
          },
          items: [
            "apis/improc/layer/ImageEffects",
            "apis/improc/layer/ImageLayer",
            "apis/improc/layer/ImageLayerContentProtocol",
            "apis/improc/layer/ImageLayerContainerProtocol",
          ],
        },
        {
          type: "category",
          label: "effects",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/improc/effects/index",
          },
          items: [
            "apis/improc/effects/ImageEffectAbstract",
            "apis/improc/effects/ImageEffectGlow",
            "apis/improc/effects/ImageEffectShadow",
            "apis/improc/effects/ImageEffectStroke",
            "apis/improc/effects/ImageEffectBevel",
          ],
        },
        {
          type: "category",
          label: "overlays",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/improc/overlays/index",
          },
          items: [
            "apis/improc/overlays/ImageOverlayAbstract",
            "apis/improc/overlays/ImageOverlayColor",
            "apis/improc/overlays/ImageOverlayGradient",
            "apis/improc/overlays/ImageOverlayImage",
          ],
        },
        {
          type: "category",
          label: "tools",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/improc/tools/index",
          },
          items: [
            "apis/improc/tools/batch_process_images",
            "apis/improc/tools/ImageGrids",
          ],
        },
        "apis/improc/variables/index",
      ],
    },
    {
      type: "category",
      label: "steaminfo",
      collapsed: true,
      link: {
        type: "doc",
        id: "apis/steaminfo/index",
      },
      items: [
        {
          type: "category",
          label: "query",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/steaminfo/query/index",
          },
          items: [
            "apis/steaminfo/query/query_app_by_name_simple",
            "apis/steaminfo/query/get_app_details",
            "apis/steaminfo/query/get_achievement_list",
          ],
        },
        {
          type: "category",
          label: "data",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/steaminfo/data/index",
          },
          items: [
            {
              type: "category",
              label: "appdata",
              collapsed: true,
              link: {
                type: "doc",
                id: "apis/steaminfo/data/appdata/index",
              },
              items: [
                "apis/steaminfo/data/appdata/AppQuerySimple",
                "apis/steaminfo/data/appdata/AppInfo",
                "apis/steaminfo/data/appdata/PlatformInfo",
                "apis/steaminfo/data/appdata/MetacriticInfo",
                "apis/steaminfo/data/appdata/AppCategory",
                "apis/steaminfo/data/appdata/AppDate",
                "apis/steaminfo/data/appdata/AppSupportInfo",
                "apis/steaminfo/data/appdata/AppScreenShot",
                "apis/steaminfo/data/appdata/AppMovie",
                "apis/steaminfo/data/appdata/AppPrice",
              ],
            },
            {
              type: "category",
              label: "achievements",
              collapsed: true,
              link: {
                type: "doc",
                id: "apis/steaminfo/data/achievements/index",
              },
              items: [
                "apis/steaminfo/data/achievements/AchievementList",
                "apis/steaminfo/data/achievements/Achievement",
                "apis/steaminfo/data/achievements/AchievementIconName",
              ],
            },
          ],
        },
        {
          type: "category",
          label: "utils",
          collapsed: true,
          link: {
            type: "doc",
            id: "apis/steaminfo/utils/index",
          },
          items: ["apis/steaminfo/utils/get_image_by_url"],
        },
      ],
    },
    {
      type: "category",
      label: "utils",
      collapsed: true,
      link: {
        type: "doc",
        id: "apis/utils/index",
      },
      items: ["apis/utils/NamedTempFolder"],
    },
  ],

  // But you can create a sidebar manually
  /*
  tutorialSidebar: [
    'intro',
    'hello',
    {
      type: 'category',
      label: 'Tutorial',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
   */
};

export default sidebars;
