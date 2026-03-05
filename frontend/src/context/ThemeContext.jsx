import { createContext, useContext, useState, useEffect } from "react";

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [isDarkMode, setIsDarkMode] = useState(
    window.matchMedia("(prefers-color-scheme: dark)").matches
  );

  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = (e) => setIsDarkMode(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  const theme = isDarkMode
    ? {
      bg: "#0a0f1f",
      surface: "#ddeeff",
      border: "#1c2a44",
      text: "#d9e6ff",
      subtext: "#8fa8d6",
      buttonBg: "#1f5fbf",
      buttonText: "white",
      navbutton: "#212854",
    }
    : {
      bg: "#e7f1ff",
      surface: "#ffffff",
      border: "#b3cff5",
      text: "#0d2b66",
      subtext: "#3d5fa8",
      buttonBg: "#d8e7ff",
      buttonText: "#0a3aa8",
      navbutton: "#061d42",

    };

  return (
    <ThemeContext.Provider value={{ isDarkMode, setIsDarkMode, theme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeContext);
    if (!context) {
      throw new Error("useTheme must be used within a ThemeProvider");
    }
    return context;
}