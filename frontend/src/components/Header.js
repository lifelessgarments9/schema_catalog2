import { useNavigate, Link } from "react-router-dom";

export default function Header({ currentUser }) {
    const navigate = useNavigate();

    return (
        <header className="header-navbar navbar border-0 py-3 shadow-sm">
            <div className="container d-flex justify-content-between align-items-center">

                <Link to="/" className="navbar-brand header-logo fw-bold mb-0 h4 text-decoration-none">
                    Фаблаб
                </Link>

                <div className="d-flex align-items-center gap-2">
                    {currentUser && (
                        <Link to="/cart" className="btn btn-custom">
                            Корзина
                        </Link>
                    )}
                    {currentUser?.is_staff && (
                        <Link to="/requests" className="btn btn-custom">
                            Заявки
                        </Link>
                    )}

                    <Link to="/chats" className="btn btn-custom">
                        Ассистент
                    </Link>

                    {currentUser ? (
                        <button
                            className="btn btn-custom rounded-pill px-4"
                            onClick={() => navigate("/profile")}
                        >
                            Профиль
                        </button>
                    ) : (
                        <button
                            className="btn btn-custom rounded-pill px-4"
                            onClick={() => navigate("/auth")}
                        >
                            Войти
                        </button>
                    )}
                </div>

            </div>
        </header>
    );
}