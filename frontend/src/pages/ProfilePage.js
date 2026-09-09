import { useEffect, useState } from "react";
import { getRentalRequests } from "../api";
import { useNavigate } from "react-router-dom";
import { ReactComponent as DeviceIcon } from "../assets/device.svg";
import { Link } from "react-router-dom";

export default function ProfilePage({ user, onLogout }) {
    const navigate = useNavigate();
    const [requests, setRequests] = useState([]);
    const [requestsLoading, setRequestsLoading] = useState(true);

    const handleLogout = () => {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("user");
        onLogout();
        navigate("/");
    };

    useEffect(() => {
        if (!user) return;
        loadRequests();
    }, [user]);

    async function loadRequests() {
        try {
            const data = await getRentalRequests(1, 10);
            setRequests(data.results || []);
        } catch (error) {
            console.error("Ошибка загрузки заявок:", error);
        } finally {
            setRequestsLoading(false);
        }
    }

    if (!user) {
        return (
            <div className="d-flex justify-content-center align-items-center py-5 my-5">
                <div className="spinner-border" role="status">
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
                        <div className="card p-4 text-center">
                            <div className="mb-4">
                                {user.avatar ? (
                                    <img
                                        src={user.avatar}
                                        alt={user.username}
                                        className="rounded-circle mx-auto"
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

                {/* История заявок */}
                <div className="row justify-content-center">
                    <div className="col-12 col-lg-10">
                        <h2 className="section-title mb-4">
                            История заявок
                        </h2>
                        {requestsLoading ? (
                            <div className="d-flex justify-content-center py-5">
                                <div className="spinner-border" role="status">
                                    <span className="visually-hidden">
                                        Загрузка...
                                    </span>
                                </div>
                            </div>
                        ) : requests.length === 0 ? (
                            <div className="alert alert-light">
                                У вас пока нет заявок.
                            </div>
                        ) : (
                            <div className="card shadow-sm">
                                <table className="table table-hover mb-0">
                                    <thead>
                                        <tr>
                                            <th>Дата создания</th>
                                            <th>Устройства</th>
                                            <th>Дисциплина</th>
                                            <th>Статус</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {requests.map(request => (
                                            <tr key={request.id}>
                                                <td>
                                                    {new Date(
                                                        request.created_at
                                                    ).toLocaleDateString()}
                                                </td>
                                                <td>
                                                    <div className="d-flex flex-wrap gap-2">
                                                        {request.items.map(item => (
                                                            <Link
                                                                key={item.id}
                                                                to={`/device/${item.device_id}`}
                                                                className="text-decoration-none"
                                                            >
                                                                <div className="badge category-badge p-2 d-flex align-items-center gap-1">

                                                                    <DeviceIcon
                                                                        style={{
                                                                            width: 40,
                                                                            height: 40
                                                                        }}
                                                                    />
                                                                    <span>
                                                                        {item.device_name}
                                                                    </span>
                                                                    <span
                                                                        className="ms-1 text-muted"
                                                                        style={{
                                                                            fontSize: "0.75rem"
                                                                        }}
                                                                    >
                                                                        ×{item.quantity}
                                                                    </span>
                                                                </div>
                                                            </Link>
                                                        ))}
                                                    </div>
                                                </td>
                                                <td>
                                                    {request.discipline}
                                                </td>
                                                <td>
                                                    {request.status === "pending" && (
                                                        <span className="badge bg-warning text-dark">
                                                            Ожидает
                                                        </span>
                                                    )}
                                                    {request.status === "approved" && (
                                                        <span className="badge bg-success">
                                                            Подтверждено
                                                        </span>
                                                    )}
                                                    {request.status === "rejected" && (
                                                        <span className="badge bg-danger">
                                                            Отклонено
                                                        </span>
                                                    )}
                                                    {request.status === "returned" && (
                                                        <span className="badge bg-warning text-dark">
                                                            Возвращено
                                                        </span>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </section>
    );
}