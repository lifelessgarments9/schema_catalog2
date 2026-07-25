import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { login, register } from "../api";

// URL, на который CAS-сервер вернёт пользователя с ticket'ом
const CAS_LOGIN_URL =
    "https://proxy.bmstu.ru:8443/cas/login?" +
    "service=" +
    encodeURIComponent("http://localhost:8000/accounts/cas/callback/"); // https://schema.example.ru/accounts/cas/callback/

function AuthPage({ onLogin }) {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState("login");

    const [loginData, setLoginData] = useState({ username: "", password: "" });
    const [registerData, setRegisterData] = useState({ username: "", email: "", password: "", password_confirm: "" });
    const [error, setError] = useState("");

    // Читаем ошибку из URL-параметра (если CAS вернул ошибку)
    const urlError = new URLSearchParams(window.location.search).get("error");
    const casErrorMessages = {
        no_ticket: "CAS не вернул ticket. Попробуйте снова.",
        cas_failed: "Авторизация через CAS не прошла. Проверьте данные.",
        cas_unreachable: "Сервер CAS МГТУ недоступен. Попробуйте позже.",
        cas_parse_error: "Ошибка разбора ответа CAS.",
        server_error: "Внутренняя ошибка сервера.",
    };

    async function handleRegister() {
        setError("");
        try {
            const response = await register(registerData);
            if (response.username || response.email || response.password) {
                setError(JSON.stringify(response));
                return;
            }
            setActiveTab("login");
            setLoginData({ username: registerData.username, password: registerData.password });
        } catch {
            setError("Ошибка регистрации");
        }
    }

    async function handleLogin() {
        setError("");
        try {
            const response = await login(loginData);
            if (response.detail) {
                setError(response.detail);
                return;
            }
            localStorage.setItem("access", response.access);
            localStorage.setItem("refresh", response.refresh);
            localStorage.setItem("user", JSON.stringify(response.user));
            onLogin(response.user);
            navigate("/profile");
        } catch {
            setError("Ошибка входа");
        }
    }

    function handleCASLogin() {
        // Шаг 1 CAS: перенаправляем браузер на CAS-сервер МГТУ
        window.location.href = CAS_LOGIN_URL;
    }

    return (
        <div className="auth-wrapper d-flex align-items-center justify-content-center min-vh-100 py-5">
            <div className="auth-card p-4 p-sm-5 rounded-4 shadow-sm position-relative">

                <button onClick={() => navigate("/")} className="btn btn-back btn-sm mb-4">
                    ← На главную
                </button>

                {/* ─── Кнопка CAS (МГТУ) ─────────────────────────────── */}
                <div className="mb-4 text-center">
                    <button
                        onClick={handleCASLogin}
                        className="btn btn-cas w-100 rounded-3 py-2 d-flex align-items-center justify-content-center gap-2"
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>
                            <path d="M2 12h20"/>
                        </svg>
                        Войти через МГТУ
                    </button>
                </div>

                <div className="auth-divider d-flex align-items-center gap-2 mb-4">
                    <hr className="flex-grow-1 m-0"/>
                    <span className="text-muted small">или</span>
                    <hr className="flex-grow-1 m-0"/>
                </div>
                {/* ──────────────────────────────────────────────────────── */}

                <div className="nav nav-pills auth-tabs mb-4 justify-content-center p-1 rounded-pill">
                    <button
                        className={`nav-link rounded-pill px-4 ${activeTab === "login" ? "active" : ""}`}
                        onClick={() => setActiveTab("login")}
                    >
                        Вход
                    </button>
                    <button
                        className={`nav-link rounded-pill px-4 ${activeTab === "register" ? "active" : ""}`}
                        onClick={() => setActiveTab("register")}
                    >
                        Регистрация
                    </button>
                </div>

                {activeTab === "login" && (
                    <div className="auth-form-body">
                        <h2 className="auth-title text-center mb-4">Вход</h2>
                        <div className="mb-3">
                            <input
                                className="form-control custom-input rounded-3 px-3 py-2"
                                placeholder="Username"
                                value={loginData.username}
                                onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
                            />
                        </div>
                        <div className="mb-4">
                            <input
                                type="password"
                                className="form-control custom-input rounded-3 px-3 py-2"
                                placeholder="Пароль"
                                value={loginData.password}
                                onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                            />
                        </div>
                        <button onClick={handleLogin} className="btn btn-custom w-100 rounded-3 py-2">
                            Войти
                        </button>
                    </div>
                )}

                {activeTab === "register" && (
                    <div className="auth-form-body">
                        <h2 className="auth-title text-center mb-4">Регистрация</h2>
                        <div className="mb-3">
                            <input
                                className="form-control custom-input rounded-3 px-3 py-2"
                                placeholder="Username"
                                value={registerData.username}
                                onChange={(e) => setRegisterData({ ...registerData, username: e.target.value })}
                            />
                        </div>
                        <div className="mb-3">
                            <input
                                className="form-control custom-input rounded-3 px-3 py-2"
                                placeholder="Email"
                                value={registerData.email}
                                onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                            />
                        </div>
                        <div className="mb-3">
                            <input
                                type="password"
                                className="form-control custom-input rounded-3 px-3 py-2"
                                placeholder="Пароль"
                                value={registerData.password}
                                onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                            />
                        </div>
                        <div className="mb-4">
                            <input
                                type="password"
                                className="form-control custom-input rounded-3 px-3 py-2"
                                placeholder="Повторите пароль"
                                value={registerData.password_confirm}
                                onChange={(e) => setRegisterData({ ...registerData, password_confirm: e.target.value })}
                            />
                        </div>
                        <button onClick={handleRegister} className="btn btn-custom w-100 rounded-3 py-2">
                            Зарегистрироваться
                        </button>
                    </div>
                )}

                {(error || urlError) && (
                    <div className="alert alert-danger custom-alert mt-4 mb-0 text-center rounded-3 small">
                        {urlError ? (casErrorMessages[urlError] || `Ошибка: ${urlError}`) : error}
                    </div>
                )}

            </div>
        </div>
    );
}

export default AuthPage;