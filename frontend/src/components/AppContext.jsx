import { createContext, useContext, useState } from "react";

const AppContext = createContext();

export function AppProvider({ children }) {
    // context state
    const [user, setUser] = useState(null);

    //context functions
    const login = (userData) => setUser(userData);
    const logout = () => setUser(null);

    return (
        <AppContext.Provider value={{ user, login, logout }}>
        {children}
        </AppContext.Provider>
    );
}

export function useApp() {
  return useContext(AppContext);
}