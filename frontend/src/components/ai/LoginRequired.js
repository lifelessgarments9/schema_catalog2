import { Link } from "react-router-dom";

export default function LoginRequired({ onClose, message }) {
    return (
        <div
            className="position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center"
            style={{
                background: "rgba(0,0,0,.35)",
                zIndex: 2000
            }}
        >
            <div className="card p-4">
                <p className="mb-4 text-main fw-medium">
                    {message || "Чтобы использовать эту функцию, необходимо войти в систему"}
                </p>

                <div className="d-flex gap-2 justify-content-end">
                    <button
                        className="btn btn-outline-secondary rounded-pill px-4"
                        onClick={onClose}
                    >
                        Отмена
                    </button>

                    <Link
                        className="btn btn-custom rounded-pill px-4"
                        to="/auth"
                    >
                        Войти
                    </Link>
                </div>
            </div>
        </div>
    );
}