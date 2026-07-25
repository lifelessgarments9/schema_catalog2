
import { useNavigate } from "react-router-dom";

export default function ProfilePage({ user, onLogout }) {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("user");
        onLogout();
        navigate("/");
    };

    if (!user) {
        return (
            <div className="d-flex justify-content-center align-items-center py-5 my-5">
                <div className="spinner-border text-muted opacity-50" role="status">
                    <span className="visually-hidden">Загрузка...</span>
                </div>
            </div>
        );
    }

    return (
        <section className="profile-section py-5">
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-12 col-md-6 col-lg-4">
                        <div className="card border-0 shadow-sm rounded-4 p-4 text-center">
                            <div className="mb-4">
                                {user.avatar ? (
                                    <img
                                        src={user.avatar}
                                        alt={user.username}
                                        className="rounded-circle"
                                        width="100"
                                        height="100"
                                        style={{ objectFit: "cover" }}
                                    />
                                ) : (
                                    <div
                                        className="rounded-circle bg-light d-flex align-items-center justify-content-center mx-auto"
                                        style={{ width: 100, height: 100, fontSize: "2rem" }}
                                    >
                                    </div>
                                )}
                            </div>

                            <h3 className="fw-bold mb-1">{user.username}</h3>
                            <p className="text-muted mb-4">{user.email || "Email не указан"}</p>

                            <button
                                className="btn btn-outline-danger rounded-pill px-4 w-100"
                                onClick={handleLogout}
                            >
                                Выйти
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}