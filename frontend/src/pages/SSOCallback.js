import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../api";

export default function SSOCallback({ onLogin }) {
    const navigate = useNavigate();
    const [status, setStatus] = useState("loading");
    const [error, setError] = useState("");
    const processed = useRef(false);

    useEffect(() => {
        if (processed.current) return;
        processed.current = true;

        const params = new URLSearchParams(window.location.search);
        const code = params.get("code");
        const state = params.get("state");
        const ssoError = params.get("error");
        window.history.replaceState(null, "", window.location.pathname);

        if (ssoError) {
            const errorDescription = params.get("error_description");
            setError(ssoError === "access_denied"
                ? "Вход отменён на стороне SSO."
                : `SSO не смог выполнить вход${errorDescription ? `: ${errorDescription}` : "."}`);
            setStatus("error");
            return;
        }

        if (!code || !state) {
            setError("В ответе SSO отсутствует код авторизации или state.");
            setStatus("error");
            return;
        }

        fetch(`${API_BASE_URL}/accounts/sso/callback/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({ code, state }),
        })
            .then(async (response) => {
                if (!response.ok) {
                    const data = await response.json().catch(() => ({}));
                    throw new Error(data.detail || "Не удалось обменять код SSO.");
                }
                return response.json();
            })
            .then(({ access, refresh }) => {
                if (!access || !refresh) throw new Error("SSO не вернул токены приложения.");
                localStorage.setItem("access", access);
                localStorage.setItem("refresh", refresh);
                return fetch(`${API_BASE_URL}/accounts/profile/`, {
                    headers: { Authorization: `Bearer ${access}` },
                    credentials: "same-origin",
                });
            })
            .then((response) => {
                if (!response.ok) throw new Error("Не удалось загрузить профиль.");
                return response.json();
            })
            .then((user) => {
                localStorage.setItem("user", JSON.stringify(user));
                onLogin(user);
                navigate("/");
            })
            .catch((cause) => {
                localStorage.removeItem("access");
                localStorage.removeItem("refresh");
                localStorage.removeItem("user");
                setError(cause.message);
                setStatus("error");
            });
    }, [navigate, onLogin]);

    if (status === "error") {
        return (
            <div className="d-flex flex-column align-items-center justify-content-center min-vh-100 gap-3">
                <p className="text-danger fw-semibold">
                    {error || "Ошибка авторизации через SSO."}
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
            <p className="text-muted">Выполняется вход через SSO МГТУ...</p>
        </div>
    );
}