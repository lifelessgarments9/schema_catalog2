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

        const params = new URLSearchParams(window.location.hash.slice(1));
        const ticket = params.get("ticket");

        // The fragment is not sent to the web server; remove it before redeeming the ticket.
        window.history.replaceState(null, "", window.location.pathname);

        const fail = (message) => {
            localStorage.removeItem("access");
            localStorage.removeItem("refresh");
            localStorage.removeItem("user");
            setError(message);
            setStatus("error");
        };

        if (!ticket) {
            fail("В ответе сервера отсутствует ticket авторизации.");
            return;
        }

        fetch(`${API_BASE_URL}/accounts/sso/complete/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "same-origin",
            body: JSON.stringify({ ticket }),
        })
            .then(async (response) => {
                const data = await response.json().catch(() => ({}));

                if (!response.ok) {
                    throw new Error(
                        data.detail || `Ошибка авторизации (HTTP ${response.status}).`
                    );
                }

                if (!data.access || !data.refresh) {
                    throw new Error("SSO не вернул токены приложения.");
                }

                return data;
            })
            .then(({ access, refresh }) => {
                localStorage.setItem("access", access);
                localStorage.setItem("refresh", refresh);

                return fetch(`${API_BASE_URL}/accounts/profile/`, {
                    headers: {
                        Authorization: `Bearer ${access}`,
                    },
                    credentials: "same-origin",
                });
            })
            .then(async (response) => {
                if (!response.ok) {
                    throw new Error("Не удалось загрузить профиль пользователя.");
                }

                return response.json();
            })
            .then((user) => {
                localStorage.setItem("user", JSON.stringify(user));

                if (onLogin) {
                    onLogin(user);
                }

                navigate("/", { replace: true });
            })
            .catch((cause) => {
                fail(cause.message || "Неизвестная ошибка авторизации.");
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
                    onClick={() => navigate("/auth", { replace: true })}
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

            <p className="text-muted">
                Выполняется вход через SSO МГТУ...
            </p>
        </div>
    );
}
