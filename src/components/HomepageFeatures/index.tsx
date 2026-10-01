import type {ReactNode} from "react";
import clsx from "clsx";
import Heading from "@theme/Heading";

import Link from "@docusaurus/Link";
import IconExternalLink from "@theme/Icon/ExternalLink";
import Translate, {translate} from "@docusaurus/Translate";

import styles from "./styles.module.scss";

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<"svg">>;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: translate({
      id: "index.feat.bbcode.title",
      description: "Feature title for BBCode.",
      message: "BBCode Conversion",
    }),
    Svg: require("@site/static/img/icon-bbcode.svg").default,
    description: (
      <>
        <Translate
          id="index.feat.bbcode.descr"
          description="Feature description for BBCode."
          values={{
            bbcode: (
              <Link
                href={translate({
                  id: "index.feat.bbcode.bbcode.link",
                  description: "The link to the BBCode.",
                  message: "https://steamcommunity.com/comment/Recommendation/formattinghelp",
                })}
                aria-label="BBCode Formats"
              >
                BBCode
                <IconExternalLink />
              </Link>
            ),
          }}
        >
          {
            "Offer conversions from multiple formats (Markdown, HTML, and BBCode) to BBCode. The formats strictly follow Steam's {bbcode} rules. Users can keep only one copy of the text and convert it for different purposes (guides and reviews)."
          }
        </Translate>
      </>
    ),
  },
  {
    title: translate({
      id: "index.feat.improc.title",
      description: "Feature title for Image Processing.",
      message: "Code-based Image Editor",
    }),
    Svg: require("@site/static/img/icon-improc.svg").default,
    description: (
      <>
        <Translate
          id="index.feat.improc.descr"
          description="Feature description for Image Processing."
          values={{
            tikz: (
              <Link
                href={translate({
                  id: "index.feat.improc.tikz.link",
                  description: "The link to TikZ.",
                  message: "https://tikz.dev/tikz",
                })}
                aria-label="TikZ Documentation"
              >
                TikZ
                <IconExternalLink />
              </Link>
            ),
          }}
        >
          {
            "Inspired by {tikz}, we offer image editing tools with an anchor-based alignment system. These features allow users to compose multi-layer images with blending options, layer effects, customized fonts, and even $\LaTeX$ equations."
          }
        </Translate>
      </>
    ),
  },
  {
    title: translate({
      id: "index.feat.steaminfo.title",
      description: "Feature title for Steam Info.",
      message: "Easy to Use",
    }),
    Svg: require("@site/static/img/icon-steaminfo.svg").default,
    description: (
      <>
        <Translate
          id="index.feat.steaminfo.descr"
          description="Feature description for Steam Info."
        >
          {
            "Accessing credential-free APIs, this package can retrieve public information from Steam game profiles and pages. For example, users can download all icons and descriptions of a game's achievements."
          }
        </Translate>
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
