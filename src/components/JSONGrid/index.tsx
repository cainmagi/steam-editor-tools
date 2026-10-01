/**
 * Demo used for showing some view-only examples.
 *
 * Author: Yuchen Jin (cainmagi)
 * GitHub: https://github.com/cainmagi/dash-json-grid
 * License: MIT
 *
 * Thanks the base project:
 * https://github.com/RedHeadphone/react-json-grid
 */

import React, {useState, useEffect} from "react";

import {useColorMode} from "@docusaurus/theme-common";

import JSONGrid from "@redheadphone/react-json-grid";

import styles from "./styles.module.scss";

type customeThemeType = {
  bgColor?: string;
  borderColor?: string;
  selectHighlightBgColor?: string;
  cellBorderColor?: string;
  keyColor?: string;
  indexColor?: string;
  numberColor?: string;
  booleanColor?: string;
  stringColor?: string;
  objectColor?: string;
  tableHeaderBgColor?: string;
  tableIconColor?: string;
  searchHighlightBgColor?: string;
};

type AppProps = {
  data: string;
  theme?:
    | {
        light: string;
        dark: string;
      }
    | string;
  customTheme?: customeThemeType;
  defaultExpandKeyTree?: Object;
};

const sanitizeData = (data: any): Record<string, any> | Array<any> => {
  if (["object", "array"].includes(typeof data)) {
    return data;
  }

  return [data];
};

const sanitizeTheme = (
  theme: {light: string; dark: string} | string,
  isDarkTheme: boolean = false
): string => {
  if (typeof theme === "string") {
    return theme;
  } else {
    return isDarkTheme ? theme?.dark || "spacegray" : theme?.light || "remedy";
  }
};

const App = ({
  data,
  theme = {light: "remedy", dark: "spacegray"},
  defaultExpandKeyTree,
}: AppProps): React.JSX.Element => {
  const {colorMode, setColorMode} = useColorMode();

  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className={styles.jsGridContainer}>
      <JSONGrid
        data={sanitizeData(data && require(`@site/static/json/${data}.json`))}
        theme={sanitizeTheme(theme, colorMode === "dark")}
        defaultExpandKeyTree={defaultExpandKeyTree}
      />
    </div>
  );
};

export default App;
