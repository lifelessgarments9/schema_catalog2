import {useEffect, useState} from "react";
import {useNavigate} from "react-router-dom";
import Modal from "../components/Modal";
import Toast from "../components/Toast";
import AccessErrorPage from "../components/AccessErrorPage";
import { ReactComponent as DeviceIcon } from '../assets/device.svg';
import { Link } from "react-router-dom";

import {getRentalRequests, approveRentalRequest, deleteRentalRequest, returnRentalRequest,getRentalRequestPdf} from "../api";

export default function RequestsPage() {
    const navigate = useNavigate();

    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const PAGE_SIZE = 10;

    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modal, setModal] = useState(null);
    const [toast, setToast] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        load();
    }, [page]);

    async function load() {
        setLoading(true);
        setError(null);

        try {
            const data = await getRentalRequests(page, PAGE_SIZE);

            setRequests(data.results || []);
            setTotalPages(Math.max(1, Math.ceil((data.count || 0) / PAGE_SIZE)));

        } catch (error) {
            console.error(error);

            if (error.status === 401) {
                setError({
                    status: 401,
                    message: "Для просмотра заявок необходимо авторизоваться."
                });
            } else if (error.status === 403) {
                setError({
                    status: 403,
                    message: "У вас нет доступа к заявкам."
                });
            } else {
                setError({
                    status: 500,
                    message: error.message || "Не удалось загрузить заявки."
                });
            }

        } finally {
            setLoading(false);
        }
    }

    async function approve(id) {
        try {
            const rental = await approveRentalRequest(id);
            await load();
        } catch (error) {
            console.error("Ошибка подтверждения заявки:", error);
            setToast({message: error.message || "Не удалось подтвердить заявку."});
        }
    }

    async function remove(requestId) {
        setModal({
            title: "Удалить заявку?",
            message: "Заявка будет удалена безвозвратно.",
            confirmText: "Удалить",
            onConfirm: async () => {
                await deleteRentalRequest(requestId);
                if (requests.length === 1 && page > 1) {setPage(p => p - 1);}
                else {await load();}
                setModal(null);
            },
        });
    }

    async function returnDevices(requestId) {
        const request = requests.find(r => r.id === requestId);
        if (request.status !== "approved") {
            setToast({
                message: "Вернуть можно только подтвержденную заявку."
            });
            return;
        }

        setModal({
            title: "Оформить возврат?",
            message: "Все устройства будут возвращены на склад.",
            confirmText: "Вернуть",
            onConfirm: async () => {
                const rental = await returnRentalRequest(requestId);
                await load();
                setModal(null);
            },
        });
    }

    async function openPdf(requestId) {
        try {
            const blob = await getRentalRequestPdf(requestId);
            const url = URL.createObjectURL(blob);
            window.open(url, "_blank");
            setTimeout(() => {
                URL.revokeObjectURL(url);
            }, 60000);

        } catch (error) {
            console.error("Ошибка открытия PDF:", error);
        }
    }

    if (loading)
        return (
            <div className="container d-flex justify-content-center align-items-center" style={{ minHeight: 'calc(100vh - 64px)' }}>
                <div className="spinner-border" role="status">
                    <span className="visually-hidden">Загрузка...</span>
                </div>
            </div>
        );
    if (error) {
        return (
            <AccessErrorPage
                status={error.status}
                message={error.message}
                onRetry={error.status >= 500 ? load : null}
            />
        );
    }

    return (
        <section className="requests-section">

            <div className="container">

                <h2 className="section-title mb-4">
                    Заявки
                </h2>
                <>
                    <div className="card shadow-sm">

                        <table className="table table-hover mb-0">
                            <thead>
                            <tr>
                                <th>Дата создания</th>
                                <th>ФИО</th>
                                <th>Устройства</th>
                                <th>Дисциплина</th>
                                <th>Статус</th>
                                <th></th>
                            </tr>
                            </thead>
                            <tbody>
                            {requests.map(request => (
                                <tr key={request.id}>
                                    <td>{new Date(request.created_at).toLocaleDateString()}</td>
                                    <td>{request.full_name}</td>
                                    <td>
                                        <div className="d-flex flex-wrap gap-2">
                                            {request.items.map(item => (
                                                <Link key={item.id} to={`/device/${item.device_id}`} className="text-decoration-none">
                                                    <div className="badge category-badge p-2 d-flex align-items-center gap-1">
                                                        <DeviceIcon style={{ width: 40, height: 40 }} />
                                                        <span>{item.device_name}</span>
                                                        <span className="ms-1 text-muted" style={{ fontSize: '0.75rem' }}>×{item.quantity}</span>
                                                    </div>
                                                </Link>
                                            ))}
                                        </div>
                                    </td>
                                    <td>{request.discipline}</td>
                                    <td>
                                        {request.status === "pending" &&
                                            <span className="badge bg-warning text-dark">
                                                Ожидает
                                            </span>
                                        }
                                        {request.status === "approved" &&
                                            <span className="badge bg-success">
                                                Подтверждено
                                            </span>
                                        }
                                        {request.status === "rejected" &&
                                            <span className="badge bg-danger">
                                                Отклонить
                                            </span>
                                        }
                                        {request.status === "returned" &&
                                            <span className="badge bg-warning text-dark">
                                                Возвращено
                                            </span>
                                        }
                                    </td>
                                    <td className="text-end text-nowrap">

                                        <button
                                            className="btn btn-outline-primary btn-sm me-2"
                                            onClick={() =>
                                                navigate(`/requests/${request.id}`)
                                            }
                                        >
                                            Подробнее
                                        </button>
                                        {request.status === "pending" && (
                                            <>
                                                <button
                                                    className="btn btn-success btn-sm me-2"
                                                    onClick={() => approve(request.id)}
                                                >
                                                    Подтвердить
                                                </button>
                                                <button
                                                    className="btn btn-danger btn-sm me-2"
                                                    onClick={() => remove(request.id)}
                                                >
                                                    Удалить
                                                </button>
                                            </>
                                        )}
                                        <button
                                            className="btn btn-outline-secondary btn-sm me-2"
                                            onClick={() => openPdf(request.id)}>
                                            PDF
                                        </button>
                                        {request.status === "approved" && (
                                            <button
                                                className="btn btn-warning btn-sm"
                                                onClick={() => returnDevices(request.id)}
                                            >
                                                Возврат
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </div>

                    <nav className="d-flex justify-content-center mt-4">
                        <ul className="pagination">
                            {page > 1 && (
                                <li className={`page-item ${page <= 1 ? "disabled" : ""}`}>
                                    <button className="page-link" onClick={() => setPage(p => p - 1)}>
                                        ←
                                    </button>
                                </li>
                            )}
                            <li className="page-item active">
                                <span className="page-link">{page}</span>
                            </li>
                            {page < totalPages && (
                                <li className={`page-item ${page >= totalPages ? "disabled" : ""}`}>
                                    <button className="page-link" onClick={() => setPage(p => p + 1)}>
                                        →
                                    </button>
                                </li>
                            )}
                        </ul>
                    </nav>
                </>

                {modal && (
                    <Modal
                        title={modal.title}
                        message={modal.message}
                        confirmText={modal.confirmText}
                        onConfirm={modal.onConfirm}
                        onCancel={() => setModal(null)}
                    />
                )}

                {toast && (
                    <Toast
                        message={toast.message}
                        onClose={() => setToast(null)}
                    />
                )}
            </div>
        </section>
    );
}