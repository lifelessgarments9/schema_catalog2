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

  const handleLogin = (user) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
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

        <Route path="/device/add" element={<AddDevicePage />} />

        <Route path="/profile" element={<ProfilePage user={currentUser} onLogout={handleLogout} />} />

        <Route path="/cart" element={<CartPage />} />

        <Route path="/chats" element={<ChatsPage currentUser={currentUser} />} />

        <Route path="/chats/:id" element={<ChatsPage currentUser={currentUser} />} />

        <Route path="/requests" element={<RequestsPage />} />

        <Route path="/sso-callback" element={<SSOCallback onLogin={handleLogin} />} />

      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}