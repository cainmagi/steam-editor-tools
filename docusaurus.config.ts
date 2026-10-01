import {themes as prismThemes} from "prism-react-renderer";
import type {Config} from "@docusaurus/types";
import type * as Preset from "@docusaurus/preset-classic";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: "Steam Editor Tools",
  tagline:
    "This package offers editor tools helping users write Steam guides and reviews. Support Steam information queries, image editing tools, and BBCode text processing tools.",
  favicon: "img/favicon.ico",

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: "https://cainmagi.github.io",
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: "/steam-editor-tools/",

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: "cainmagi", // Usually your GitHub org/user name.
  projectName: "steam-editor-tools", // Usually your repo name.

  onBrokenLinks: "throw",
  trailingSlash: false,

  plugins: [
    [
      // Use SASS/SCSS.
      "docusaurus-plugin-sass",
      {
        // options
        // api: "modern-compiler",
      },
    ],
  ],

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      {
        docs: {
          sidebarPath: "./sidebars.ts",
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl: "https://github.com/cainmagi/steam-editor-tools/edit/docs/",
          editLocalizedFiles: true,
          // versions
          includeCurrentVersion: true,
          lastVersion: "current",
          versions: {
            current: {
              label: "0.6.x",
            },
            // "1.0.3": {
            //   noIndex: true,
            // },
          },
          remarkPlugins: [remarkMath],
          rehypePlugins: [rehypeKatex],
        },
        // Replace blog block with false if the blog is not used.
        blog: false,
        theme: {
          customCss: "./src/css/custom.scss",
        },
      } satisfies Preset.Options,
    ],
  ],

  stylesheets: [
    {
      href: "https://cdn.jsdelivr.net/npm/katex@0.13.24/dist/katex.min.css",
      type: "text/css",
      integrity:
        "sha384-odtC+0UGzzFL/6PNoE8rX/SPcQDXBJ+uRepguP4QkPCm2LBxH3FA3y+fKSiJ+AmM",
      crossorigin: "anonymous",
    },
  ],

  themeConfig: {
    // Replace with your project's social card
    image: "img/social-card.webp",
    metadata: [
      {
        name: "keywords",
        content:
          "bbcode, html-to-bbcode, image-processing, markdown-to-bbcode, python, python3, steam, steam-api, steam-bbcode, steam-bbcode-converter, steam-guide",
      },
      {name: "og:site_name", content: "Steam Editor Tools"},
    ],
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      style: "dark",
      title: "StET",
      logo: {
        alt: "Steam Editor Tools Logo",
        src: "img/logo-small.svg",
      },
      hideOnScroll: false,
      items: [
        {
          type: "docSidebar",
          sidebarId: "tutorial",
          position: "left",
          label: "Tutorial",
        },
        {
          type: "docSidebar",
          sidebarId: "apis",
          position: "left",
          label: "APIs",
        },
        {
          type: "docsVersionDropdown",
          position: "right",
          dropdownActiveClassDisabled: true,
          dropdownItemsAfter: [
            {
              to: "/versions",
              label: "All versions",
            },
          ],
        },
        {
          type: "localeDropdown",
          position: "right",
        },
        {
          href: "https://github.com/cainmagi/steam-editor-tools",
          position: "right",
          className: "header-github-link",
          "aria-label": "GitHub repository",
        },
        {
          href: "https://pypi.org/project/steam-editor-tools",
          position: "right",
          className: "header-pypi-link",
          "aria-label": "PyPI repository",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          title: "Docs",
          items: [
            {
              label: "Tutorial",
              to: "/docs/",
            },
            {
              label: "APIs",
              to: "/docs/",
            },
          ],
        },
        {
          title: "Contact the author",
          items: [
            {
              label: "Website",
              href: "https://cainmagi.github.io/",
            },
            {
              label: "Email",
              href: "mailto:cainmagi@gmail.com",
            },
            {
              label: "GitHub",
              href: "https://github.com/cainmagi",
            },
          ],
        },
        {
          title: "Community",
          items: [
            {
              label: "GitHub of Aramco AIT",
              href: "https://github.com/aschrc-ait-team",
            },
            {
              label: "UH MODAL Lab",
              href: "https://modal.ece.uh.edu/",
            },
            {
              label: "University of Houston",
              href: "https://www.uh.edu/",
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Steam Editor Tools, Yuchen Jin. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.vsDark,
      additionalLanguages: ["bash", "python", "bbcode", "markdown"],
      magicComments: [
        // Remember to extend the default highlight class name as well!
        {
          className: "theme-code-block-highlighted-line",
          line: "highlight-next-line",
          block: {start: "highlight-start", end: "highlight-end"},
        },
        {
          className: "code-block-error-line",
          line: "This will error",
        },
        {
          className: "code-block-diff-add-line",
          line: "diff-add-next-line",
          block: {start: "diff-add-start", end: "diff-add-end"},
        },
        {
          className: "code-block-diff-remove-line",
          line: "diff-remove-next-line",
          block: {start: "diff-remove-start", end: "diff-remove-end"},
        },
      ],
    },
    docs: {
      sidebar: {
        hideable: true,
        autoCollapseCategories: true,
      },
    },
  } satisfies Preset.ThemeConfig,

  headTags: [
    {
      tagName: "script",
      attributes: {
        type: "application/ld+json",
      },
      innerHTML: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "SoftwareSourceCode",
        name: "Steam Editor Tools",
        description:
          "This package offers editor tools helping users write Steam guides and reviews. Support Steam information queries, image editing tools, and BBCode text processing tools.",
        programmingLanguage: {
          "@type": "ComputerLanguage",
          name: "Python",
          url: "https://python.org",
        },
        runtimePlatform: "Python 3.10+",
        codeRepository: "https://github.com/cainmagi/steam-editor-tools",
        downloadUrl: "https://pypi.org/project/steam-editor-tools/",
        license:
          "https://github.com/cainmagi/steam-editor-tools/blob/main/LICENSE",
        version: "1.2.4",
        keywords:
          "bbcode, html-to-bbcode, image-processing, markdown-to-bbcode, python, python3, steam, steam-api, steam-bbcode, steam-bbcode-converter, steam-guide",
        author: {
          "@type": "Organization",
          name: "Yuchen Jin (cainmagi)",
          url: "https://cainmagi.github.io/",
        },
        maintainer: {
          "@type": "Person",
          name: "Yuchen Jin (cainmagi)",
          email: "cainmagi@gmail.com",
        },
      }),
    },
  ],
};

export default config;
