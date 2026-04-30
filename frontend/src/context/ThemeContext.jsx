import { createContext, useContext, useState, useEffect } from "react";

const ThemeContext = createContext();

export function ThemeProvider({ children }) {

  const theme =
    {
      bg: "#0a0f1f",
      surface: "#ddeeff",
      border: "#1c2a44",
      text: "#d9e6ff",
      subtext: "#8fa8d6",
      buttonBg: "#1f5fbf",
      buttonText: "white",
      navbutton: "#212854",
    }

  return (
    <ThemeContext.Provider value={{ theme }}>
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