import { Link } from "react-router-dom";

export default function LoginRequired({ onClose }) {

    return (

        <div
            className="position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center"
            style={{
                background: "rgba(0,0,0,.35)",
                zIndex: 2000
            }}
        >

            <div className="card shadow p-4">

                <p>
                    Чтобы использовать ИИ-ассистента, необходимо войти
                </p>

                <div className="d-flex gap-2 justify-content-end">

                    <button
                        className="btn btn-outline-secondary"
                        onClick={onClose}
                    >
                        Отмена
                    </button>

                    <Link
                        className="btn btn-primary"
                        to="/auth"
                    >
                        Войти
                    </Link>

                </div>

            </div>

        </div>

    );

}