import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../api";

export default function SSOCallback({ onLogin }) {
    const navigate = useNavigate();
    const [status, setStatus] = useState("loading"); // loading | error

    useEffect(() => {
        const params = new URLSearchParams(window.location.hash.slice(1));
        const access = params.get("access");
        const refresh = params.get("refresh");
        window.history.replaceState(null, "", window.location.pathname);

        if (!access) {
            setStatus("error");
            return;
        }

        localStorage.setItem("access", access);
        if (refresh) localStorage.setItem("refresh", refresh);

        fetch(`${API_BASE_URL}/accounts/profile/`, {
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
                localStorage.removeItem("access");
                localStorage.removeItem("refresh");
                setStatus("error");
            });
    }, []);  // eslint-disable-line react-hooks/exhaustive-deps

    if (status === "error") {
        return (
            <div className="d-flex flex-column align-items-center justify-content-center min-vh-100 gap-3">
                <p className="text-danger fw-semibold">
                    Ошибка авторизации через SSO.
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
            <p className="text-muted">Вход через SSO МГТУ...</p>
        </div>
    );
}