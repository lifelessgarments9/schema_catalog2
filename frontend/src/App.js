import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Header from "./components/Header";

import HomePage from "./pages/HomePage";
import CatalogPage from "./pages/CatalogPage";
import DevicePage from "./pages/DevicePage";
import AuthPage from "./pages/AuthPage";
import ProfilePage from "./pages/ProfilePage";
import AddDevicePage from "./pages/AddDevicePage";
import CASCallback from "./pages/CASCallback";
import CartPage from "./pages/CartPage";
import RequestsPage from "./pages/RequestsPage";
import ChatsPage from "./pages/ChatsPage";

function AppContent() {
  const [currentUser, setCurrentUser] = useState(() => {
    const user = localStorage.getItem("user");
    if (!user || user === "undefined" || user === "null") return null;
    return user ? JSON.parse(user) : null;
  });

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

        <Route path="/device/:id" element={<DevicePage currentUser={currentUser} />} />

        <Route path="/auth" element={<AuthPage onLogin={handleLogin} />} />

        <Route path="/device/add" element={<AddDevicePage />} />

        <Route path="/profile" element={<ProfilePage user={currentUser} onLogout={handleLogout} />} />

        <Route path="/cart" element={<CartPage />} />

        <Route path="/chats" element={<ChatsPage currentUser={currentUser} />} />

        <Route path="/chats/:id" element={<ChatsPage currentUser={currentUser} />} />

        <Route path="/requests" element={<RequestsPage />} />

        {/* CAS callback — шаги 6–7: Django редиректит сюда с JWT-токенами */}
        <Route path="/cas-callback" element={<CASCallback onLogin={handleLogin} />} />

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