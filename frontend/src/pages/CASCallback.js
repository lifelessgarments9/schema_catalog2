// pages/CASCallback.js
// Шаги 6–7 CAS-протокола:
//   Django редиректит сюда с JWT-токенами в query string:
//   /cas-callback?access=...&refresh=...
//   Страница сохраняет токены, загружает профиль и логинит пользователя.

import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

export default function CASCallback({ onLogin }) {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState("loading"); // loading | error

    useEffect(() => {
        const access = searchParams.get("access");
        const refresh = searchParams.get("refresh");

        if (!access) {
            setStatus("error");
            return;
        }

        // Сохраняем токены
        localStorage.setItem("access", access);
        if (refresh) localStorage.setItem("refresh", refresh);

        // Загружаем профиль пользователя
        fetch("http://localhost:8000/accounts/profile/", { // https://schema.example.ru/accounts/profile/
            headers: { Authorization: `Bearer ${access}` },
        })
            .then((r) => {
                if (!r.ok) throw new Error("profile_fetch_failed");
                return r.json();
            })
            .then((user) => {
                localStorage.setItem("user", JSON.stringify(user));
                onLogin(user);
                navigate("/");
            })
            .catch(() => {
                setStatus("error");
            });
    }, []);  // eslint-disable-line react-hooks/exhaustive-deps

    if (status === "error") {
        return (
            <div className="d-flex flex-column align-items-center justify-content-center min-vh-100 gap-3">
                <p className="text-danger fw-semibold">
                    Ошибка CAS-авторизации. Токены не получены.
                </p>
                <button
                    className="btn btn-custom rounded-pill px-4 py-2"
                    onClick={() => navigate("/auth")}
                >
                    Вернуться к входу
                </button>
            </div>
        );
    }

    return (
        <div className="d-flex flex-column align-items-center justify-content-center min-vh-100 gap-3">
            <div className="spinner-border" role="status">
                <span className="visually-hidden">Загрузка...</span>
            </div>
            <p className="text-muted">Вход через МГТУ CAS...</p>
        </div>
    );
}