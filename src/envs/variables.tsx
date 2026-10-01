/**
 * Environmental variables of this side.
 * Yuchen Jin, mailto:cainmagi@gmail.com
 */

import React from "react";
import Link from "@docusaurus/Link";
import {useDocsVersion} from "@docusaurus/plugin-content-docs/client";

import InlineIcon from "../components/InlineIcon";
import IconExternalLink from "@theme/Icon/ExternalLink";
import mdiDot from "@iconify-icons/mdi/dot";

const docsPluginId = undefined; // Default docs plugin instance

interface EnvVariables {
  repoURL: string;
  rawURL: string;
  sourceVersion: {
    "0.6.x": string;
    main: string;
    [key: string]: any;
  };
  sourceURIs: {
    main: {[key: string]: string};
    "v0.6.3": {[key: string]: string};
    [key: string]: any;
  };
  [key: string]: any;
}

const variables: EnvVariables = {
  repoURL: "https://github.com/cainmagi/steam-editor-tools",
  rawURL: "https://raw.githubusercontent.com/cainmagi/steam-editor-tools",
  sourceVersion: {
    "0.6.x": "v0.6.3",
    current: "v0.6.3",
    main: "main",
  },
  sourceURIs: {
    "v0.6.3": {
      ".": "./__init__.py",
      "bbcode": "bbcode/__init__.py",
      "bbcode.guide": "bbcode/guide.py",
      "bbcode.guide.GuideParser": "bbcode/guide.py#L57",
      "bbcode.nodes": "bbcode/nodes.py",
      "bbcode.nodes.AlertNode": "bbcode/nodes.py#L359",
      "bbcode.nodes.BoldNode": "bbcode/nodes.py#L221",
      "bbcode.nodes.CodeBlockNode": "bbcode/nodes.py#L169",
      "bbcode.nodes.DeletedNode": "bbcode/nodes.py#L58",
      "bbcode.nodes.Document": "bbcode/nodes.py#L508",
      "bbcode.nodes.HeadingNode": "bbcode/nodes.py#L313",
      "bbcode.nodes.HorizontalRuleNode": "bbcode/nodes.py#L126",
      "bbcode.nodes.InlineCodeNode": "bbcode/nodes.py#L146",
      "bbcode.nodes.ItalicNode": "bbcode/nodes.py#L234",
      "bbcode.nodes.LineBreakNode": "bbcode/nodes.py#L106",
      "bbcode.nodes.LinkNode": "bbcode/nodes.py#L292",
      "bbcode.nodes.ListItemNode": "bbcode/nodes.py#L397",
      "bbcode.nodes.ListNode": "bbcode/nodes.py#L410",
      "bbcode.nodes.Node": "bbcode/nodes.py#L583",
      "bbcode.nodes.ParagraphNode": "bbcode/nodes.py#L330",
      "bbcode.nodes.QuoteNode": "bbcode/nodes.py#L343",
      "bbcode.nodes.SpoilerNode": "bbcode/nodes.py#L273",
      "bbcode.nodes.StrikeNode": "bbcode/nodes.py#L260",
      "bbcode.nodes.TableCellNode": "bbcode/nodes.py#L441",
      "bbcode.nodes.TableNode": "bbcode/nodes.py#L482",
      "bbcode.nodes.TableRowNode": "bbcode/nodes.py#L459",
      "bbcode.nodes.TextNode": "bbcode/nodes.py#L83",
      "bbcode.nodes.UnderlineNode": "bbcode/nodes.py#L247",
      "bbcode.parser": "bbcode/parser.py",
      "bbcode.parser.DocumentParser": "bbcode/parser.py#L117",
      "bbcode.parser.HandleMemory": "bbcode/parser.py#L65",
      "bbcode.plugins": "bbcode/plugins/__init__.py",
      "bbcode.plugins.alert": "bbcode/plugins/alert.py",
      "bbcode.plugins.alert.AlertRuleFactory": "bbcode/plugins/alert.py#L58",
      "bbcode.plugins.alert.gfm_alerts_plugin": "bbcode/plugins/alert.py#L197",
      "bbcode.plugins.mark": "bbcode/plugins/mark.py",
      "bbcode.plugins.mark.mark_plugin": "bbcode/plugins/mark.py#L34",
      "bbcode.renderer": "bbcode/renderer/__init__.py",
      "bbcode.renderer.base": "bbcode/renderer/base.py",
      "bbcode.renderer.base.BBCodeRenderer": "bbcode/renderer/base.py#L118",
      "bbcode.renderer.configs": "bbcode/renderer/configs.py",
      "bbcode.renderer.configs.AlertTitleConfigs": "bbcode/renderer/configs.py#L26",
      "bbcode.renderer.configs.BBCodeConfig": "bbcode/renderer/configs.py#L106",
      "bbcode.renderer.variants": "bbcode/renderer/variants.py",
      "bbcode.renderer.variants.BBCodeRendererForReview": "bbcode/renderer/variants.py#L320",
      "bbcode.renderer.variants.BBCodeRendererListPreferred": "bbcode/renderer/variants.py#L148",
      "bbcode.renderer.variants.BBCodeRendererTablePreferred": "bbcode/renderer/variants.py#L51",
      "improc": "improc/__init__.py",
      "improc.composer": "improc/composer.py",
      "improc.composer.ImageComposer": "improc/composer.py#L49",
      "improc.composer.ImageComposerMode": "improc/composer.py#L31",
      "improc.data": "improc/data.py",
      "improc.data.ImageAnchor": "improc/data.py#L316",
      "improc.data.ImageFontAbsSize": "improc/data.py#L82",
      "improc.data.ImageFontSize": "improc/data.py#L92",
      "improc.data.ImageFormat": "improc/data.py#L219",
      "improc.data.ImageQuality": "improc/data.py#L300",
      "improc.data.TeXTemplate": "improc/data.py#L40",
      "improc.data.Templates": "improc/data.py#L65",
      "improc.effects": "improc/effects.py",
      "improc.effects.ImageEffectAbstract": "improc/effects.py#L148",
      "improc.effects.ImageEffectBevel": "improc/effects.py#L453",
      "improc.effects.ImageEffectGlow": "improc/effects.py#L272",
      "improc.effects.ImageEffectShadow": "improc/effects.py#L330",
      "improc.effects.ImageEffectStroke": "improc/effects.py#L398",
      "improc.font": "improc/font.py",
      "improc.font.FontIndexList": "improc/font.py#L182",
      "improc.font.FontInfo": "improc/font.py#L111",
      "improc.font.FontLanguage": "improc/font.py#L47",
      "improc.font.FontLocator": "improc/font.py#L489",
      "improc.font.FontNameInfo": "improc/font.py#L93",
      "improc.latex_to_img": "improc/latex_to_img.py",
      "improc.latex_to_img.TeXRenderer": "improc/latex_to_img.py#L38",
      "improc.layer": "improc/layer.py",
      "improc.layer.ImageEffects": "improc/layer.py#L106",
      "improc.layer.ImageLayer": "improc/layer.py#L146",
      "improc.layer.ImageLayerContainerProtocol": "improc/layer.py#L77",
      "improc.layer.ImageLayerContentProtocol": "improc/layer.py#L43",
      "improc.overlays": "improc/overlays.py",
      "improc.overlays.ImageOverlayAbstract": "improc/overlays.py#L121",
      "improc.overlays.ImageOverlayColor": "improc/overlays.py#L287",
      "improc.overlays.ImageOverlayGradient": "improc/overlays.py#L332",
      "improc.overlays.ImageOverlayImage": "improc/overlays.py#L432",
      "improc.renderer": "improc/renderer.py",
      "improc.renderer.ImageMultiLayer": "improc/renderer.py#L1067",
      "improc.renderer.ImageSingle": "improc/renderer.py#L54",
      "improc.renderer.ImageTeX": "improc/renderer.py#L912",
      "improc.renderer.ImageText": "improc/renderer.py#L650",
      "improc.tools": "improc/tools.py",
      "improc.tools.ImageGrids": "improc/tools.py#L113",
      "improc.tools.batch_process_images": "improc/tools.py#L40",
      "improc.variables": "improc/variables.py",
      "steaminfo": "steaminfo/__init__.py",
      "steaminfo.data": "steaminfo/data/__init__.py",
      "steaminfo.data.achievements": "steaminfo/data/achievements.py",
      "steaminfo.data.achievements.Achievement": "steaminfo/data/achievements.py#L39",
      "steaminfo.data.achievements.AchievementIconName": "steaminfo/data/achievements.py#L68",
      "steaminfo.data.achievements.AchievementList": "steaminfo/data/achievements.py#L87",
      "steaminfo.data.appdata": "steaminfo/data/appdata.py",
      "steaminfo.data.appdata.AppCategory": "steaminfo/data/appdata.py#L76",
      "steaminfo.data.appdata.AppDate": "steaminfo/data/appdata.py#L88",
      "steaminfo.data.appdata.AppInfo": "steaminfo/data/appdata.py#L242",
      "steaminfo.data.appdata.AppMovie": "steaminfo/data/appdata.py#L142",
      "steaminfo.data.appdata.AppPrice": "steaminfo/data/appdata.py#L179",
      "steaminfo.data.appdata.AppQuerySimple": "steaminfo/data/appdata.py#L203",
      "steaminfo.data.appdata.AppScreenShot": "steaminfo/data/appdata.py#L112",
      "steaminfo.data.appdata.AppSupportInfo": "steaminfo/data/appdata.py#L100",
      "steaminfo.data.appdata.MetacriticInfo": "steaminfo/data/appdata.py#L59",
      "steaminfo.data.appdata.PlatformInfo": "steaminfo/data/appdata.py#L44",
      "steaminfo.query": "steaminfo/query.py",
      "steaminfo.query.get_achievement_list": "steaminfo/query.py#L141",
      "steaminfo.query.get_app_details": "steaminfo/query.py#L92",
      "steaminfo.query.query_app_by_name_simple": "steaminfo/query.py#L31",
      "steaminfo.utils": "steaminfo/utils.py",
      "steaminfo.utils.get_image_by_url": "steaminfo/utils.py#L29",
      "utils": "utils.py",
      "utils.NamedTempFolder": "utils.py#L34",
    },
    "main": {
      ".": "./__init__.py",
      "bbcode": "bbcode/__init__.py",
      "bbcode.guide": "bbcode/guide.py",
      "bbcode.guide.GuideParser": "bbcode/guide.py#L57",
      "bbcode.nodes": "bbcode/nodes.py",
      "bbcode.nodes.AlertNode": "bbcode/nodes.py#L359",
      "bbcode.nodes.BoldNode": "bbcode/nodes.py#L221",
      "bbcode.nodes.CodeBlockNode": "bbcode/nodes.py#L169",
      "bbcode.nodes.DeletedNode": "bbcode/nodes.py#L58",
      "bbcode.nodes.Document": "bbcode/nodes.py#L508",
      "bbcode.nodes.HeadingNode": "bbcode/nodes.py#L313",
      "bbcode.nodes.HorizontalRuleNode": "bbcode/nodes.py#L126",
      "bbcode.nodes.InlineCodeNode": "bbcode/nodes.py#L146",
      "bbcode.nodes.ItalicNode": "bbcode/nodes.py#L234",
      "bbcode.nodes.LineBreakNode": "bbcode/nodes.py#L106",
      "bbcode.nodes.LinkNode": "bbcode/nodes.py#L292",
      "bbcode.nodes.ListItemNode": "bbcode/nodes.py#L397",
      "bbcode.nodes.ListNode": "bbcode/nodes.py#L410",
      "bbcode.nodes.Node": "bbcode/nodes.py#L583",
      "bbcode.nodes.ParagraphNode": "bbcode/nodes.py#L330",
      "bbcode.nodes.QuoteNode": "bbcode/nodes.py#L343",
      "bbcode.nodes.SpoilerNode": "bbcode/nodes.py#L273",
      "bbcode.nodes.StrikeNode": "bbcode/nodes.py#L260",
      "bbcode.nodes.TableCellNode": "bbcode/nodes.py#L441",
      "bbcode.nodes.TableNode": "bbcode/nodes.py#L482",
      "bbcode.nodes.TableRowNode": "bbcode/nodes.py#L459",
      "bbcode.nodes.TextNode": "bbcode/nodes.py#L83",
      "bbcode.nodes.UnderlineNode": "bbcode/nodes.py#L247",
      "bbcode.parser": "bbcode/parser.py",
      "bbcode.parser.DocumentParser": "bbcode/parser.py#L117",
      "bbcode.parser.HandleMemory": "bbcode/parser.py#L65",
      "bbcode.plugins": "bbcode/plugins/__init__.py",
      "bbcode.plugins.alert": "bbcode/plugins/alert.py",
      "bbcode.plugins.alert.AlertRuleFactory": "bbcode/plugins/alert.py#L58",
      "bbcode.plugins.alert.gfm_alerts_plugin": "bbcode/plugins/alert.py#L197",
      "bbcode.plugins.mark": "bbcode/plugins/mark.py",
      "bbcode.plugins.mark.mark_plugin": "bbcode/plugins/mark.py#L34",
      "bbcode.renderer": "bbcode/renderer/__init__.py",
      "bbcode.renderer.base": "bbcode/renderer/base.py",
      "bbcode.renderer.base.BBCodeRenderer": "bbcode/renderer/base.py#L118",
      "bbcode.renderer.configs": "bbcode/renderer/configs.py",
      "bbcode.renderer.configs.AlertTitleConfigs": "bbcode/renderer/configs.py#L26",
      "bbcode.renderer.configs.BBCodeConfig": "bbcode/renderer/configs.py#L106",
      "bbcode.renderer.variants": "bbcode/renderer/variants.py",
      "bbcode.renderer.variants.BBCodeRendererForReview": "bbcode/renderer/variants.py#L320",
      "bbcode.renderer.variants.BBCodeRendererListPreferred": "bbcode/renderer/variants.py#L148",
      "bbcode.renderer.variants.BBCodeRendererTablePreferred": "bbcode/renderer/variants.py#L51",
      "improc": "improc/__init__.py",
      "improc.composer": "improc/composer.py",
      "improc.composer.ImageComposer": "improc/composer.py#L49",
      "improc.composer.ImageComposerMode": "improc/composer.py#L31",
      "improc.data": "improc/data.py",
      "improc.data.ImageAnchor": "improc/data.py#L316",
      "improc.data.ImageFontAbsSize": "improc/data.py#L82",
      "improc.data.ImageFontSize": "improc/data.py#L92",
      "improc.data.ImageFormat": "improc/data.py#L219",
      "improc.data.ImageQuality": "improc/data.py#L300",
      "improc.data.TeXTemplate": "improc/data.py#L40",
      "improc.data.Templates": "improc/data.py#L65",
      "improc.effects": "improc/effects.py",
      "improc.effects.ImageEffectAbstract": "improc/effects.py#L148",
      "improc.effects.ImageEffectBevel": "improc/effects.py#L453",
      "improc.effects.ImageEffectGlow": "improc/effects.py#L272",
      "improc.effects.ImageEffectShadow": "improc/effects.py#L330",
      "improc.effects.ImageEffectStroke": "improc/effects.py#L398",
      "improc.font": "improc/font.py",
      "improc.font.FontIndexList": "improc/font.py#L182",
      "improc.font.FontInfo": "improc/font.py#L111",
      "improc.font.FontLanguage": "improc/font.py#L47",
      "improc.font.FontLocator": "improc/font.py#L489",
      "improc.font.FontNameInfo": "improc/font.py#L93",
      "improc.latex_to_img": "improc/latex_to_img.py",
      "improc.latex_to_img.TeXRenderer": "improc/latex_to_img.py#L38",
      "improc.layer": "improc/layer.py",
      "improc.layer.ImageEffects": "improc/layer.py#L106",
      "improc.layer.ImageLayer": "improc/layer.py#L146",
      "improc.layer.ImageLayerContainerProtocol": "improc/layer.py#L77",
      "improc.layer.ImageLayerContentProtocol": "improc/layer.py#L43",
      "improc.overlays": "improc/overlays.py",
      "improc.overlays.ImageOverlayAbstract": "improc/overlays.py#L121",
      "improc.overlays.ImageOverlayColor": "improc/overlays.py#L287",
      "improc.overlays.ImageOverlayGradient": "improc/overlays.py#L332",
      "improc.overlays.ImageOverlayImage": "improc/overlays.py#L432",
      "improc.renderer": "improc/renderer.py",
      "improc.renderer.ImageMultiLayer": "improc/renderer.py#L1067",
      "improc.renderer.ImageSingle": "improc/renderer.py#L54",
      "improc.renderer.ImageTeX": "improc/renderer.py#L912",
      "improc.renderer.ImageText": "improc/renderer.py#L650",
      "improc.tools": "improc/tools.py",
      "improc.tools.ImageGrids": "improc/tools.py#L113",
      "improc.tools.batch_process_images": "improc/tools.py#L40",
      "improc.variables": "improc/variables.py",
      "steaminfo": "steaminfo/__init__.py",
      "steaminfo.data": "steaminfo/data/__init__.py",
      "steaminfo.data.achievements": "steaminfo/data/achievements.py",
      "steaminfo.data.achievements.Achievement": "steaminfo/data/achievements.py#L39",
      "steaminfo.data.achievements.AchievementIconName": "steaminfo/data/achievements.py#L68",
      "steaminfo.data.achievements.AchievementList": "steaminfo/data/achievements.py#L87",
      "steaminfo.data.appdata": "steaminfo/data/appdata.py",
      "steaminfo.data.appdata.AppCategory": "steaminfo/data/appdata.py#L76",
      "steaminfo.data.appdata.AppDate": "steaminfo/data/appdata.py#L88",
      "steaminfo.data.appdata.AppInfo": "steaminfo/data/appdata.py#L242",
      "steaminfo.data.appdata.AppMovie": "steaminfo/data/appdata.py#L142",
      "steaminfo.data.appdata.AppPrice": "steaminfo/data/appdata.py#L179",
      "steaminfo.data.appdata.AppQuerySimple": "steaminfo/data/appdata.py#L203",
      "steaminfo.data.appdata.AppScreenShot": "steaminfo/data/appdata.py#L112",
      "steaminfo.data.appdata.AppSupportInfo": "steaminfo/data/appdata.py#L100",
      "steaminfo.data.appdata.MetacriticInfo": "steaminfo/data/appdata.py#L59",
      "steaminfo.data.appdata.PlatformInfo": "steaminfo/data/appdata.py#L44",
      "steaminfo.query": "steaminfo/query.py",
      "steaminfo.query.get_achievement_list": "steaminfo/query.py#L141",
      "steaminfo.query.get_app_details": "steaminfo/query.py#L92",
      "steaminfo.query.query_app_by_name_simple": "steaminfo/query.py#L31",
      "steaminfo.utils": "steaminfo/utils.py",
      "steaminfo.utils.get_image_by_url": "steaminfo/utils.py#L29",
      "utils": "utils.py",
      "utils.NamedTempFolder": "utils.py#L34",
    },
  },
};

const useCurrentSourceVersion = (): string => {
  const versionHook = useDocsVersion();
  const versionName = versionHook?.version;
  return (
    variables.sourceVersion[versionName] || variables.sourceVersion["main"]
  );
};

export const rawURL = (url: string): string => {
  return variables.rawURL + "/" + url;
};

export const repoURL = (url: string | undefined = undefined): string => {
  return url ? variables.repoURL + "/" + url : variables.repoURL;
};

export const releaseURL = (ver: string | undefined = undefined): string => {
  const _ver = ver?.toLowerCase() === "current" ? "main" : ver || "";
  const version = variables.sourceVersion[_ver] || "main";
  if (version === "main" || _ver === "main") {
    return variables.repoURL + "/releases/latest";
  }
  return variables.repoURL + "/releases/tag/" + version;
};

export const rootURL = (url: string): string => {
  const currentSourceVersion = useCurrentSourceVersion();
  return variables.repoURL + "/blob/" + currentSourceVersion + "/" + url;
};

const getURIByVersionPath = (path: string, ver: string): string => {
  const routes = typeof path === "string" ? path.trim() : "";
  if (routes.length === 0) {
    return path;
  }
  const currentURI = variables.sourceURIs[ver] || variables.sourceURIs["main"];
  return currentURI[path] || path;
};

export const sourceURL = (url: string): string => {
  const currentSourceVersion = useCurrentSourceVersion();
  return (
    variables.repoURL +
    "/blob/" +
    currentSourceVersion +
    "/steam_editor_tools/" +
    getURIByVersionPath(url, currentSourceVersion)
  );
};

export const demoURL = (url?: string): string => {
  const currentSourceVersion = useCurrentSourceVersion();
  if (!url) {
    return variables.repoURL + "/blob/" + currentSourceVersion + "/usage.py";
  }
  return (
    variables.repoURL + "/blob/" + currentSourceVersion + "/examples/" + url
  );
};

export type SourceLinkProps = {
  url: string;
  children: React.ReactNode;
};

export const SourceLink = ({
  url,
  children,
}: SourceLinkProps): React.JSX.Element => {
  return (
    <Link to={sourceURL(url)} className="noline">
      {children}
    </Link>
  );
};

export type DemoLinkProps = {
  script: string;
};

export const DemoLink = ({script}: DemoLinkProps) => (
  <Link href={demoURL(`${script}.py`)}>
    <code>{`${script}`}</code><IconExternalLink/>
  </Link>
);

export type SplitterProps = {
  padx?: string;
};

export const Splitter = ({padx = "0"}: SplitterProps): React.JSX.Element => {
  return (
    <span style={{padding: "0 " + padx}}>
      <InlineIcon icon={mdiDot} />
    </span>
  );
};
