import { createContext, useContext, useEffect, useState } from "react";
import { useLocation } from "wouter";

type User = { username: string };

type AuthContextType = {
  user: User | null;
  login: (username: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem("carapp_user");
    return saved ? JSON.parse(saved) : null;
  });
  const [, setLocation] = useLocation();

  const login = (username: string) => {
    const newUser = { username };
    setUser(newUser);
    localStorage.setItem("carapp_user", JSON.stringify(newUser));
    setLocation("/");
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("carapp_user");
    setLocation("/login");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
