import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import DeviceCard from "../components/DeviceCard";
import { getCategories, getDevices } from "../api";

export default function CatalogPage() {
    const [devices, setDevices] = useState(null);
    const [search, setSearch] = useState("");
    const [category, setCategory] = useState("");
    const [isAvailable, setIsAvailable] = useState(true);
    const [allCategories, setAllCategories] = useState([]);
    const navigate = useNavigate();

    const getRandomPaleColor = () => {
        const r = Math.floor(Math.random() * 55) + 200;
        const g = Math.floor(Math.random() * 55) + 200;
        const b = Math.floor(Math.random() * 55) + 200;
        return `rgb(${r}, ${g}, ${b})`;
    };
    const [colors] = useState(() =>
        Array.from({ length: 8 }, () => getRandomPaleColor())
    );

    useEffect(() => {
        load();
        loadAllCategories();
    }, []);

    async function load() {
        const data = await getDevices({ search, category, is_available: isAvailable });
        setDevices(data ?? []);
    }

    async function loadAllCategories() {
        setAllCategories(await getCategories());
    }

    const renderContent = () => {
        if (devices === null) {
            return (
                <div className="row g-4">
                    {Array.from({ length: 8 }).map((_, index) => (
                        <div key={index} className="col-12 col-sm-6 col-md-4 col-lg-3">
                            <div className="card device-card h-100 border-0 p-3 rounded-4 shadow-sm text-center skeleton-card">
                                <div
                                    className="image-container mb-3 rounded-3 skeleton-block structural-img"
                                    style={{ backgroundColor: colors[index] }}
                                />
                                <div className="card-body d-flex flex-column p-0 align-items-center">
                                    <div className="skeleton-block structural-title mb-2" />
                                    <div className="skeleton-block structural-text mb-1 w-100" />
                                    <div className="skeleton-block structural-text mb-3 w-75" />
                                    <div className="skeleton-block structural-btn mt-auto rounded-pill w-100" />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            );
        }

        if (devices.length === 0) {
            return (
                <div className="text-center py-5">
                    <h4 className="text-muted mb-3">Ничего не найдено</h4>
                </div>
            );
        }

        return (
            <div className="row g-4">
                {devices.map(device => (
                    <div key={device.id} className="col-12 col-sm-6 col-md-4 col-lg-3">
                        <div className="h-100">
                            <DeviceCard device={device} />
                        </div>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <section className="catalog-section py-5">
            <div className="container">
                <button onClick={() => navigate("/")} className="btn btn-back btn-sm mb-4">
                    ← На главную
                </button>

                <h1 className="section-title text-center mb-5">Каталог</h1>

                <div className="row align-items-center mb-4 g-3">
                    <div className="col-md-3">
                        <div className="card border-0 shadow-sm rounded-4 p-3">
                            <h5 className="mb-3">Фильтры</h5>
                            <div className="mb-3">
                                <label className="form-label">Категория</label>
                                <select
                                    className="form-select"
                                    value={category}
                                    onChange={(e) =>
                                        setCategory(
                                            e.target.value === "" ? "" : Number(e.target.value)
                                        )
                                    }
                                >
                                    <option value="">Все категории</option>
                                    {allCategories.map(cat => (
                                        <option key={cat.id} value={cat.id}>
                                            {cat.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className="form-check mb-3">
                                <input
                                    className="form-check-input"
                                    type="checkbox"
                                    checked={isAvailable===true}
                                    onChange={(e) => setIsAvailable(e.target.checked)}
                                    id="available"
                                />
                                <label className="form-check-label" htmlFor="available">
                                    В наличии
                                </label>
                            </div>
                            <button className="btn btn-custom w-100" onClick={load}>
                                Применить
                            </button>
                        </div>
                    </div>
                    <div className="col-md-9">
                        <div className="input-group">
                            <input
                                className="form-control rounded-start-pill"
                                placeholder="Поиск..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === "Enter") load();
                                }}
                            />
                            <button
                                className="btn btn-custom rounded-end-pill"
                                onClick={() => load()}
                            >
                                Найти
                            </button>
                        </div>
                    </div>
                </div>

                {renderContent()}
            </div>
        </section>
    );
}