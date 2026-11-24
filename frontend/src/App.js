import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Header from "./components/Header";

import HomePage from "./pages/HomePage";
import CatalogPage from "./pages/CatalogPage";
import DevicePage from "./pages/DevicePage";
import AuthPage from "./pages/AuthPage";
import ProfilePage from "./pages/ProfilePage";
import AddDevicePage from "./pages/AddDevicePage";
import SSOCallback from "./pages/SSOCallback";
import CartPage from "./pages/CartPage";
import RequestsPage from "./pages/RequestsPage";
import ChatsPage from "./pages/ChatsPage";

const BASE_PATH = (process.env.REACT_APP_BASE_PATH || "").replace(/\/+$/, "");

function getStoredUser() {
  const storedUser = localStorage.getItem("user");
  if (!storedUser || storedUser === "undefined" || storedUser === "null") return null;

  try {
    return JSON.parse(storedUser);
  } catch {
    localStorage.removeItem("user");
    return null;
  }
}

function AppContent() {
  const [currentUser, setCurrentUser] = useState(getStoredUser);
  const ssoParams = new URLSearchParams(window.location.search);
  const currentPath = window.location.pathname.replace(/\/+$/, "") || "/";
  const appRoot = BASE_PATH || "/";
const isSsoResponse =currentPath === `${appRoot}/sso/callback` && (ssoParams.has("code") || ssoParams.has("error"));

  const handleLogin = (user) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("user");
    setCurrentUser(null);
  };

  return (
    <>
      <Header currentUser={currentUser} onLogout={handleLogout} />

      <Routes>
        <Route path="/" element={<HomePage currentUser={currentUser} onLogout={handleLogout} />} />

        <Route path="/catalog" element={<CatalogPage />} />

        <Route path="/catalog/devices" element={<CatalogPage />} />

        <Route path="/device/:id" element={<DevicePage currentUser={currentUser} />} />

        <Route path="/auth" element={<AuthPage onLogin={handleLogin} />} />

        <Route path="/sso/callback" element={<SSOCallback />} />

        <Route path="/device/add" element={<AddDevicePage />} />

        <Route path="/profile" element={<ProfilePage user={currentUser} onLogout={handleLogout} />} />

        <Route path="/cart" element={<CartPage />} />

        <Route path="/chats" element={<ChatsPage currentUser={currentUser} />} />

        <Route path="/chats/:id" element={<ChatsPage currentUser={currentUser} />} />

        <Route path="/requests" element={<RequestsPage />} />

      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter basename="/fablab">
      <AppContent />
    </BrowserRouter>
  );
}