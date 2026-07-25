import {useEffect, useState} from "react";
import {useNavigate} from "react-router-dom";

import {getRentalRequests, approveRentalRequest, deleteRentalRequest, returnRentalRequest} from "../api";

export default function RequestsPage() {

    const navigate = useNavigate();

    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        load();
    }, []);

    async function load() {
        setLoading(true);

        try {
            const data = await getRentalRequests();
            setRequests(data);
        } finally {
            setLoading(false);
        }
    }

    async function approve(id) {
        const rental = await approveRentalRequest(id);
        setRequests(prev =>
            prev.map(r => r.id === rental.id ? rental : r)
        );
        if (rental.pdf) {
            let url = rental.pdf;
            if (url.startsWith("/")) {
                url = `http://127.0.0.1:8000${url}`; // `http://127.0.0.1:8000${url}`
            }
            window.open(url, "_blank");
        }
    }

    async function remove(id) {

        if (!window.confirm("Удалить заявку?"))
            return;

        await deleteRentalRequest(id);

        setRequests(prev =>
            prev.filter(r => r.id !== id)
        );
    }

    async function returnDevices(id) {
        if (
            !window.confirm(
                "Оформить возврат оборудования?\n\n" +
                "Все устройства будут возвращены на склад."
            )
        ) {
            return;
        }
        const rental = await returnRentalRequest(id);
        setRequests(prev => prev.map(r => r.id === rental.id ? rental : r));
    }

    if (loading)
        return (
            <div className="container py-5">
                Загрузка...
            </div>
        );

    return (
        <section className="py-5">

            <div className="container">

                <h2 className="mb-4">
                    Заявки
                </h2>

                <div className="card shadow-sm">

                    <table className="table table-hover mb-0">
                        <thead>
                        <tr>
                            <th>id</th>
                            <th>ФИО</th>
                            <th>Устройства</th>
                            <th>Дисциплина</th>
                            <th>Статус</th>
                            <th>Дата создания</th>
                            <th></th>
                        </tr>
                        </thead>
                        <tbody>
                        {requests.map(request => (
                            <tr key={request.id}>
                                <td>{request.id}</td>
                                <td>{request.full_name}</td>
                                <td>
                                    {request.items
                                        .map(item => item.device_name)
                                        .join(", ")}
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
                                <td>
                                    {new Date(request.created_at).toLocaleDateString()}
                                </td>
                                <td className="text-end">

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
                                                className="btn btn-danger btn-sm"
                                                onClick={() => remove(request.id)}
                                            >
                                                Удалить
                                            </button>
                                        </>
                                    )}
                                    {(request.status === "approved" || request.status === "returned") && (
                                        <>
                                            {request.pdf && (
                                                <button
                                                    className="btn btn-outline-secondary btn-sm me-2"
                                                    onClick={() => {
                                                        let url = request.pdf;
                                                        if (url.startsWith("/")) url = `http://127.0.0.1:8000${url}`;
                                                        window.open(url, "_blank");
                                                    }}>
                                                    PDF
                                                </button>
                                            )}
                                            <button
                                                className="btn btn-warning btn-sm"
                                                onClick={() => returnDevices(request.id)}>
                                                Возврат
                                            </button>
                                        </>
                                    )}
                                </td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    );
}