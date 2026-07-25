import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { addDevice } from "../api";

export default function AddDevicePage() {
    const navigate = useNavigate();

    const [form, setForm] = useState({
        name: "",
        description: "",
        manufacturer: "",
        quantity: 0,
        is_available: true,
        category: "",
    });

    const [image, setImage] = useState(null);
    const [documentation, setDocumentation] = useState(null);
    const [error, setError] = useState("");

    async function handleSubmit(e) {
        e.preventDefault();
        setError("");

        const data = new FormData();

        Object.entries(form).forEach(([key, value]) =>
            data.append(key, value)
        );

        if (image) data.append("image", image);
        if (documentation) data.append("documentation", documentation);

        const response = await addDevice(data);

        if (response.id) {
            navigate(`/device/${response.id}`);
        } else {
            setError(JSON.stringify(response));
        }
    }

    return (
        <section className="add-device-section py-5 d-flex align-items-center justify-content-center min-vh-100">
            <div className="container d-flex justify-content-center">
                <div className="add-device-card p-4 p-sm-5 rounded-4 shadow-sm">

                    <button onClick={() => navigate(-1)} className="btn btn-back btn-sm mb-4">
                        ← Назад
                    </button>

                    <h1 className="section-title text-center mb-4">Добавить устройство</h1>

                    <form onSubmit={handleSubmit}>

                        <div className="mb-3">
                            <input
                                className="form-control custom-input rounded-3 px-3 py-2"
                                placeholder="Название"
                                value={form.name}
                                onChange={(e) => setForm({ ...form, name: e.target.value })}
                                required
                            />
                        </div>

                        <div className="mb-3">
                            <textarea
                                className="form-control custom-input rounded-3 px-3 py-2"
                                placeholder="Описание"
                                rows="3"
                                value={form.description}
                                onChange={(e) => setForm({ ...form, description: e.target.value })}
                            />
                        </div>

                        <div className="mb-3">
                            <input
                                className="form-control custom-input rounded-3 px-3 py-2"
                                placeholder="Производитель"
                                value={form.manufacturer}
                                onChange={(e) => setForm({ ...form, manufacturer: e.target.value })}
                            />
                        </div>

                        <div className="row g-3 mb-3">
                            <div className="col-6">
                                <label className="form-label custom-form-label small mb-1">Количество</label>
                                <input
                                    type="number"
                                    className="form-control custom-input rounded-3 px-3 py-2"
                                    placeholder="0"
                                    value={form.quantity}
                                    onChange={(e) => setForm({ ...form, quantity: e.target.value })}
                                />
                            </div>
                            <div className="col-6">
                                <label className="form-label custom-form-label small mb-1">ID категории</label>
                                <input
                                    type="number"
                                    className="form-control custom-input rounded-3 px-3 py-2"
                                    placeholder="Категория"
                                    value={form.category}
                                    onChange={(e) => setForm({ ...form, category: e.target.value })}
                                />
                            </div>
                        </div>

                        <div className="mb-3">
                            <label className="form-label custom-form-label small mb-1">Изображение</label>
                            <input
                                type="file"
                                accept="image/*"
                                className="form-control custom-file-input rounded-3 px-3 py-2"
                                onChange={(e) => setImage(e.target.files[0])}
                            />
                        </div>

                        <div className="mb-4">
                            <label className="form-label custom-form-label small mb-1">Документация (PDF, TXT)</label>
                            <input
                                type="file"
                                accept=".pdf,.txt"
                                className="form-control custom-file-input rounded-3 px-3 py-2"
                                onChange={(e) => setDocumentation(e.target.files[0])}
                            />
                        </div>

                        <div className="form-check mb-4 d-flex align-items-center gap-2 ps-0">
                            <input
                                type="checkbox"
                                className="form-check-input custom-checkbox m-0"
                                id="is_available"
                                checked={form.is_available}
                                onChange={(e) => setForm({ ...form, is_available: e.target.checked })}
                            />
                            <label className="form-check-label custom-form-label small user-select-none" htmlFor="is_available">
                                Доступно для заказа
                            </label>
                        </div>

                        <button type="submit" className="btn btn-custom w-100 rounded-3 py-2">
                            Добавить устройство
                        </button>

                    </form>

                    {error && (
                        <div className="alert alert-danger custom-alert mt-4 mb-0 text-center rounded-3 small">
                            {error}
                        </div>
                    )}

                </div>
            </div>
        </section>
    );
}