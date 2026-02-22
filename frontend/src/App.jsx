import { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import PredictPage from "./pages/PredictPage";
import BundlesPage from "./pages/BundlesPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import AdminDashboard from "./pages/AdminDashboard";
import HistoryPage from "./pages/HistoryPage";

export default function App() {
  const [currentPage, setCurrentPage] = useState("home");
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem("user");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  // Listen for auth expiry (401 interceptor)
  useEffect(() => {
    const handler = () => {
      setUser(null);
      setCurrentPage("login");
    };
    window.addEventListener("auth-expired", handler);
    return () => window.removeEventListener("auth-expired", handler);
  }, []);

  function handleLogin(userData, token) {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(userData));
    setUser(userData);
    setCurrentPage("home");
  }

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    setCurrentPage("home");
  }

  function renderPage() {
    switch (currentPage) {
      case "login":
        return <LoginPage onLogin={handleLogin} onNavigate={setCurrentPage} />;
      case "register":
        return <RegisterPage onLogin={handleLogin} onNavigate={setCurrentPage} />;
      case "predict":
        return user ? (
          <PredictPage />
        ) : (
          <LoginPage onLogin={handleLogin} onNavigate={setCurrentPage} />
        );
      case "bundles":
        return <BundlesPage />;
      case "history":
        return user ? (
          <HistoryPage />
        ) : (
          <LoginPage onLogin={handleLogin} onNavigate={setCurrentPage} />
        );
      case "admin":
        return user?.role === "admin" ? (
          <AdminDashboard />
        ) : (
          <Dashboard onNavigate={setCurrentPage} user={user} />
        );
      default:
        return <Dashboard onNavigate={setCurrentPage} user={user} />;
    }
  }

  return (
    <div className="min-h-screen">
      <Navbar
        currentPage={currentPage}
        onNavigate={setCurrentPage}
        user={user}
        onLogout={handleLogout}
      />
      <main>{renderPage()}</main>
    </div>
  );
}
