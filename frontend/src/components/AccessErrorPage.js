import { useNavigate } from "react-router-dom";

export default function AccessErrorPage({ status, message, onRetry }) {
    const navigate = useNavigate();

    if (status === 401) {
        return (
            <div
                className="container d-flex flex-column justify-content-center align-items-center text-center"
                style={{ minHeight: "calc(100vh - 64px)" }}
            >
                <h1>401</h1>

                <p className="text-muted">
                    {message || "Для просмотра этой страницы необходимо авторизоваться."}
                </p>

                <button
                    className="btn btn-primary"
                    onClick={() => navigate("/auth")}
                >
                    Войти
                </button>
            </div>
        );
    }

    if (status === 403) {
        return (
            <div
                className="container d-flex flex-column justify-content-center align-items-center text-center"
                style={{ minHeight: "calc(100vh - 64px)" }}
            >
                <h1>403</h1>

                <p className="text-muted">
                    {message || "У вас нет доступа к этой странице."}
                </p>
            </div>
        );
    }

    return (
        <div
            className="container d-flex flex-column justify-content-center align-items-center text-center"
            style={{ minHeight: "calc(100vh - 64px)" }}
        >
            <h1>Ошибка</h1>

            <p className="text-muted">
                {message || "Произошла ошибка при загрузке страницы."}
            </p>

            {onRetry && (
                <button
                    className="btn btn-outline-primary"
                    onClick={onRetry}
                >
                    Повторить
                </button>
            )}
        </div>
    );
}