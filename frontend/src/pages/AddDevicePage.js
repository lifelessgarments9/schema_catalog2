import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { addDevice, getCategories } from "../api";

export default function AddDevicePage() {
    const navigate = useNavigate();

    const [categories, setCategories] = useState([]);
    const [form, setForm] = useState({
        name: "",
        description: "",
        manufacturer: "",
        quantity: 0,
        is_available: true,
        category: "",
    });

    const [specifications, setSpecifications] = useState({});
    const [image, setImage] = useState(null);
    const [documentation, setDocumentation] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        async function loadCategories() {
            const data = await getCategories();
            setCategories(data);
        }

        loadCategories();
    }, []);

    function handleCategoryChange(e) {
        const categoryId = e.target.value;

        setForm({
            ...form,
            category: categoryId,
        });

        const category = categories.find(
            c => String(c.id) === categoryId
        );

        if (category) {
            setSpecifications(Object.fromEntries(category.specification_template.map(key => [key, ""])));
        } else {
            setSpecifications({});
        }
    }

    function handleSpecificationChange(key, value) {
        setSpecifications(prev => ({
            ...prev,
            [key]: value,
        }));
    }

    async function handleSubmit(e) {
        e.preventDefault();
        setError("");

        const data = new FormData();

        data.append("name", form.name);
        data.append("description", form.description);
        data.append("manufacturer", form.manufacturer);
        data.append("quantity", form.quantity);
        data.append("is_available", form.is_available);
        data.append("category", form.category);

        data.append(
            "specifications",
            JSON.stringify(specifications)
        );

        if (image) {
            data.append("image", image);
        }

        if (documentation) {
            data.append("documentation", documentation);
        }

        const response = await addDevice(data);

        if (response.id) {
            navigate(`/device/${response.id}`);
        } else {
            setError(JSON.stringify(response));
        }
    }

    const selectedCategory = categories.find(
        c => String(c.id) === String(form.category)
    );

    const specificationKeys = selectedCategory
        ? selectedCategory.specification_template
        : [];

    return (
        <section className="add-device-section py-5">
            <div className="container d-flex justify-content-center">
                <div className="add-device-card p-4 p-sm-5" style={{ maxWidth: '650px', margin: '0 auto' }}>

                    <button
                        onClick={() => navigate(-1)}
                        className="btn btn-back btn-sm mb-4"
                    >
                        ← Назад
                    </button>

                    <h1 className="section-title text-center mb-4">
                        Добавить устройство
                    </h1>

                    <form onSubmit={handleSubmit}>

                        <div className="mb-3">
                            <input
                                className="form-control custom-input px-3 py-2"
                                placeholder="Название"
                                value={form.name}
                                onChange={e =>
                                    setForm({
                                        ...form,
                                        name: e.target.value
                                    })
                                }
                                required
                            />
                        </div>

                        <div className="mb-3">
                            <textarea
                                className="form-control custom-input px-3 py-2"
                                placeholder="Описание"
                                rows="3"
                                value={form.description}
                                onChange={e =>
                                    setForm({
                                        ...form,
                                        description: e.target.value
                                    })
                                }
                            />
                        </div>

                        <div className="mb-3">
                            <input
                                className="form-control custom-input px-3 py-2"
                                placeholder="Место хранения"
                                value={form.manufacturer}
                                onChange={e =>
                                    setForm({
                                        ...form,
                                        manufacturer: e.target.value
                                    })
                                }
                            />
                        </div>

                        <div className="row g-3 mb-3">

                            <div className="col-6">
                                <label className="form-label custom-form-label small mb-1">
                                    Количество
                                </label>

                                <input
                                    type="number"
                                    className="form-control custom-input px-3 py-2"
                                    value={form.quantity}
                                    onChange={e =>
                                        setForm({
                                            ...form,
                                            quantity: e.target.value
                                        })
                                    }
                                />
                            </div>

                            <div className="col-6">
                                <label className="form-label custom-form-label small mb-1">
                                    Категория
                                </label>

                                <select
                                    className="form-select custom-input px-3 py-2"
                                    value={form.category}
                                    onChange={handleCategoryChange}
                                    required
                                >
                                    <option value="">
                                        Выберите категорию
                                    </option>

                                    {categories.map(category => (
                                        <option
                                            key={category.id}
                                            value={category.id}
                                        >
                                            {category.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                        </div>

                        {specificationKeys.length > 0 && (
                            <div className="mb-4">
                                <h5 className="section-title mb-3">
                                    Характеристики
                                </h5>

                                {specificationKeys.map(key => (
                                    <div className="mb-3" key={key}>
                                        <div className="d-flex align-items-center gap-2">
                                            <span className="text-muted" style={{ minWidth: '100px', fontSize: '0.9rem' }}>
                                                {key}:
                                            </span>
                                            <input
                                                type="text"
                                                className="form-control custom-input px-3 py-2 flex-grow-1"
                                                placeholder={``}
                                                value={specifications[key] ?? ""}
                                                onChange={e =>
                                                    handleSpecificationChange(
                                                        key,
                                                        e.target.value
                                                    )
                                                }
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="mb-3">
                            <label className="form-label custom-form-label small mb-1">
                                Изображение
                            </label>

                            <input
                                type="file"
                                accept="image/*"
                                className="form-control custom-file-input px-3 py-2"
                                onChange={e =>
                                    setImage(e.target.files[0])
                                }
                            />
                        </div>

                        <div className="mb-4">
                            <label className="form-label custom-form-label small mb-1">
                                Документация (PDF, TXT)
                            </label>

                            <input
                                type="file"
                                accept=".pdf,.txt"
                                className="form-control custom-file-input px-3 py-2"
                                onChange={e =>
                                    setDocumentation(e.target.files[0])
                                }
                            />
                        </div>

                        <div className="form-check mb-4 d-flex align-items-center gap-2 ps-0">
                            <input
                                type="checkbox"
                                className="form-check-input custom-checkbox m-0"
                                id="is_available"
                                checked={form.is_available}
                                onChange={e =>
                                    setForm({
                                        ...form,
                                        is_available: e.target.checked
                                    })
                                }
                            />

                            <label
                                className="form-check-label custom-form-label small user-select-none"
                                htmlFor="is_available"
                            >
                                Доступно для заказа
                            </label>
                        </div>

                        <button
                            type="submit"
                            className="btn btn-custom w-100 py-2"
                        >
                            Добавить устройство
                        </button>

                    </form>

                    {error && (
                        <div className="alert alert-danger custom-alert mt-4 mb-0 text-center small">
                            {error}
                        </div>
                    )}

                </div>
            </div>
        </section>
    );
}