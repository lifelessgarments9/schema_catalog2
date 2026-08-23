import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getCart, removeDeviceFromCart, createRentalRequest } from "../api";
import Toast from "../components/Toast";
import AccessErrorPage from "../components/AccessErrorPage";

export default function CartPage() {
    const navigate = useNavigate();

    const [devices, setDevices] = useState([]);
    const [fullName, setFullName] = useState("");
    const [group, setGroup] = useState("");
    const [discipline, setDiscipline] = useState("");
    const [loading, setLoading]       = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError]           = useState("");
    const [toast, setToast] = useState(null);

    useEffect(() => { load(); }, []);

    async function load() {
        setLoading(true);
        setError(null);
        try {
            const data = await getCart();
            if (!Array.isArray(data)) {
                throw new Error("Некорректный формат данных корзины");
            }
            setDevices(
                data.map(d => ({
                    ...d,
                    quantity: 1,
                    return_date: "",
                }))
            );
        } catch (error) {
            console.error("Ошибка загрузки корзины:", error);
            if (error.status === 401) {
                setError({
                    status: 401,
                    message: "Для просмотра корзины необходимо авторизоваться."
                });
            } else if (error.status === 403) {
                setError({
                    status: 403,
                    message: "У вас нет доступа к корзине."
                });
            } else {
                setError({
                    status: 500,
                    message: error.message || "Не удалось загрузить корзину."
                });
            }
        } finally {
            setLoading(false);
        }
    }

    async function remove(id) {
        await removeDeviceFromCart(id);
        load();
    }

    function update(index, field, value) {
        setDevices(prev => {
            const next = [...prev];
            next[index] = { ...next[index], [field]: value };
            return next;
        });
    }

    async function submit() {
        setError("");
        if (!fullName.trim() || !group.trim() || !discipline.trim()) {
            setError("Заполните ФИО, группу и дисциплину.");
            return;
        }
        for (const d of devices) {
            if (!d.return_date) {
                setError(`Укажите дату возврата для «${d.name}».`);
                return;
            }
            if (d.quantity < 1) {
                setError(`Количество для «${d.name}» должно быть не менее 1.`);
                return;
            }
        }

        setSubmitting(true);
        try {
            const result = await createRentalRequest({
                full_name: fullName.trim(),
                group: group.trim(),
                discipline: discipline.trim(),
                items: devices.map(d => ({
                    device: d.id,
                    quantity: d.quantity,
                    return_date: d.return_date,
                })),
            });

            if (result?.id) {
                setToast({message: "Заявка успешно отправлена"});
                navigate("/profile");
            } else {
                setError(result?.detail || result?.error || "Ошибка при отправке заявки.");
            }
        } catch {
            setError("Не удалось отправить заявку. Попробуйте ещё раз.");
        } finally {
            setSubmitting(false);
        }
    }

    if (loading) {
        return (
            <section className="cart-section">
                <div className="container d-flex justify-content-center align-items-center" style={{ minHeight: 'calc(100vh - 64px)' }}>
                    <div className="spinner-border" role="status">
                        <span className="visually-hidden">Загрузка...</span>
                    </div>
                </div>
            </section>
        );
    }

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
        <section className="cart-section">
            <div className="container">

                <h2 className="section-title mb-4">Корзина</h2>

                {error && (
                    <div className="alert alert-danger">{error}</div>
                )}

                {devices.length === 0 ? (
                    <div className="alert alert-light">Корзина пуста.</div>
                ) : (
                    <div className="mb-4">
                        {/* Шапка таблицы */}
                        <div className="row fw-semibold mb-2 px-3 d-none d-md-flex">
                            <div className="col-md-4">Устройство</div>
                            <div className="col-md-2">Кол-во</div>
                            <div className="col-md-3">Дата возврата</div>
                            <div className="col-md-3"></div>
                        </div>

                        {devices.map((device, index) => (
                            <div key={device.id} className="card mb-2 p-3">
                                <div className="row align-items-center g-2">

                                    <div className="col-md-4">
                                        <b>{device.name}</b>
                                        {device.manufacturer && (
                                            <small className="text-muted d-block">{device.manufacturer}</small>
                                        )}
                                    </div>

                                    <div className="col-md-2">
                                        <input
                                            type="number"
                                            min="1"
                                            max={device.quantity}
                                            className="form-control"
                                            value={device.quantity}
                                            onChange={e => update(index, "quantity", Number(e.target.value))}
                                        />
                                    </div>

                                    <div className="col-md-3">
                                        <input
                                            type="date"
                                            className="form-control"
                                            value={device.return_date}
                                            min={new Date().toISOString().split("T")[0]}
                                            onChange={e => update(index, "return_date", e.target.value)}
                                        />
                                    </div>

                                    <div className="col-md-3 text-md-end">
                                        <button
                                            className="btn btn-outline-danger btn-sm"
                                            onClick={() => remove(device.id)}
                                        >
                                            Удалить
                                        </button>
                                    </div>

                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Форма заявки — всегда видна */}
                <div className="card mt-3 p-4">
                    <h4 className="mb-3">Данные заявки</h4>

                    <div className="mb-3">
                        <label className="form-label">ФИО *</label>
                        <input
                            className="form-control"
                            value={fullName}
                            placeholder="ФИО"
                            onChange={e => setFullName(e.target.value)}
                        />
                    </div>

                    <div className="mb-3">
                        <label className="form-label">Группа *</label>
                        <input
                            className="form-control"
                            value={group}
                            placeholder="ИУ6Ц-62Б"
                            onChange={e => setGroup(e.target.value)}
                        />
                    </div>

                    <div className="mb-4">
                        <label className="form-label">Дисциплина *</label>
                        <input
                            className="form-control"
                            value={discipline}
                            placeholder="Схемотехника"
                            onChange={e => setDiscipline(e.target.value)}
                        />
                    </div>

                    <button
                        className="btn btn-custom"
                        disabled={devices.length === 0 || submitting}
                        onClick={submit}
                    >
                        {submitting ? "Отправка…" : "Отправить заявку"}
                    </button>
                </div>
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