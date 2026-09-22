import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import DeviceCard from "../components/DeviceCard";
import { getCategories, getDevices } from "../api";

export default function CatalogPage() {
    const navigate = useNavigate();
    const [searchParams, setSearchParams] = useSearchParams();
    const PAGE_SIZE = 8;

    const page = Number(searchParams.get("page")) || 1;
    const category = searchParams.get("category") || "";
    const isAvailable = searchParams.get("is_available") !== "false";

    const [devices, setDevices] = useState(null);
    const [totalPages, setTotalPages] = useState(1);
    const [allCategories, setAllCategories] = useState([]);

    const [searchInput, setSearchInput] = useState(searchParams.get("search") || "");

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
    }, [searchParams]);

    useEffect(() => {
        loadAllCategories();
    }, []);

    async function load() {
        setDevices(null);
        const search = searchParams.get("search") || "";
        try {
            const data = await getDevices({ search, category, is_available: isAvailable }, page, PAGE_SIZE);
            setDevices(data.results || []);
            setTotalPages(Math.max(1, Math.ceil((data.count || 0) / PAGE_SIZE)));
        } catch (error) {
            console.error("Ошибка загрузки каталога:", error);
            setDevices([]);
        }
    }

    async function loadAllCategories() {
        setAllCategories(await getCategories());
    }

    function updateParams(changes) {
        const next = new URLSearchParams(searchParams);
        Object.entries(changes).forEach(([key, value]) => {
            if (value === "" || value === null || value === undefined) next.delete(key);
            else next.set(key, value);
        });
        if (!("page" in changes)) next.set("page", "1");
        setSearchParams(next);
    }

    function handleCategoryChange(e) {
        updateParams({ category: e.target.value === "" ? "" : Number(e.target.value) });
    }

    function handleAvailableChange(e) {
        updateParams({ is_available: e.target.checked ? "" : "false" });
    }

    function commitSearch() {
        updateParams({ search: searchInput });
    }

    const renderContent = () => {
        if (devices === null) {
            return (
                <div className="row g-4">
                    {Array.from({ length: 8 }).map((_, index) => (
                        <div key={index} className="col-12 col-sm-6 col-md-4 col-lg-3">
                            <div className="card device-card h-100 p-3 text-center skeleton-card">
                                <div className="image-container mb-3 skeleton-block structural-img" style={{ backgroundColor: colors[index] }} />
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
        <section className="catalog-section py-5 ">
            <div className="container">
                <button onClick={() => navigate("/")} className="btn btn-back btn-sm mb-4">
                    ← На главную
                </button>

                <h1 className="section-title text-center mb-5">Каталог</h1>

                <div className="row align-items-center mb-4 g-3">
                    <div className="col-md-3">
                        <div className="card p-4">
                            <h5 className="mb-3 fw-bold">Фильтры</h5>
                            <div className="mb-3">
                                <label className="form-label custom-form-label">Категория</label>
                                <select className="form-select" value={category} onChange={handleCategoryChange}>
                                    <option value="">Все категории</option>
                                    {allCategories.map(cat => (
                                        <option key={cat.id} value={cat.id}>{cat.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="form-check mb-3 d-flex align-items-center gap-2 ps-0">
                                <input
                                    className="form-check-input custom-checkbox m-0"
                                    type="checkbox"
                                    checked={isAvailable}
                                    onChange={handleAvailableChange} // CHANGED
                                    id="available"
                                />
                                <label className="form-check-label custom-form-label user-select-none" htmlFor="available">
                                    В наличии
                                </label>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-9">
                        <div className="input-group">
                            <input
                                className="form-control custom-input rounded-start-pill px-4 py-2"
                                placeholder="Поиск..."
                                value={searchInput}
                                onChange={(e) => setSearchInput(e.target.value)}
                                onKeyDown={(e) => { if (e.key === "Enter") commitSearch(); }}
                            />
                            <button className="btn btn-custom rounded-end-pill px-4" onClick={commitSearch}>
                                Найти
                            </button>
                        </div>
                    </div>
                </div>

                {renderContent()}
                {devices !== null && totalPages > 1 && (
                    <nav className="d-flex justify-content-center mt-5">
                        <ul className="pagination">
                            {page > 1 && (
                                <li className="page-item">
                                    <button className="page-link" onClick={() => updateParams({ page: page - 1 })}>←</button>
                                </li>
                            )}
                            <li className="page-item active">
                                <span className="page-link">{page} / {totalPages}</span>
                            </li>
                            {page < totalPages && (
                                <li className="page-item">
                                    <button className="page-link" onClick={() => updateParams({ page: page + 1 })}>→</button>
                                </li>
                            )}
                        </ul>
                    </nav>
                )}
            </div>
        </section>
    );
}