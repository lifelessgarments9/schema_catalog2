import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import DeviceCard from "../components/DeviceCard";
import { getDevices, getCatalogStats  } from "../api";

export default function HomePage({ currentUser }) {
    const [devices, setDevices] = useState(null);
    const [stats, setStats] = useState(null);

    useEffect(() => {
        load();
        if (currentUser?.is_staff) {loadStats();}
    }, [currentUser]);

    async function load() {
        const data = await getDevices();
        const list = data.results || [];
        setDevices(list.slice(0, 4));
    }

    async function loadStats() {
        try {
            const data = await getCatalogStats();
            setStats(data);
        } catch (error) {console.error("Ошибка загрузки статистики:", error);}
    }

    const getRandomPaleColor = () => {
        const r = Math.floor(Math.random() * 55) + 200;
        const g = Math.floor(Math.random() * 55) + 200;
        const b = Math.floor(Math.random() * 55) + 200;
        return `rgb(${r}, ${g}, ${b})`;
    };

    return (
        <section className="home-section py-5 ">
            <div className="container">
                <h1 className="section-title text-center mb-5">Каталог микросхем</h1>

                {currentUser?.is_staff && (
                    <>
                        <div className="row text-center mb-5 stats-row">
                            <div className="stats-block">
                                <h3 className="fw-bold mb-0">{stats?.total_devices ?? "..."}</h3>
                                <span className="text-muted">Всего устройств</span>
                            </div>
                            <div className="stats-block">
                                <h3 className="fw-bold mb-0 text-success">{stats?.available_devices ?? "..."}</h3>
                                <span className="text-muted">Доступно сейчас</span>
                            </div>
                            <div className="stats-block">
                                <h3 className="fw-bold mb-0">{stats?.categories ?? "..."}</h3>
                                <span className="text-muted">Категорий</span>
                            </div>
                        </div>

                        <div className="d-flex justify-content-end mb-4">
                            <Link to="/device/add" className="btn btn-custom btn-lg rounded-pill px-4">
                                Добавить устройство
                            </Link>
                        </div>
                    </>
                )}
                <div className="row g-4 justify-content-center">
                    {devices && devices.length > 0
                        ? devices.map(device => (
                            <div key={device.id} className="col-12 col-sm-6 col-md-4 col-lg-3">
                                <DeviceCard device={device} />
                            </div>
                        ))
                        : Array.from({ length: 4 }).map((_, index) => {
                            const paleColor = getRandomPaleColor();
                            return (
                                <div key={index} className="col-12 col-sm-6 col-md-4 col-lg-3">
                                    <div className="card device-card h-100 p-3 text-center skeleton-card">
                                        <div
                                            className="image-container mb-3 skeleton-block structural-img"
                                            style={{ backgroundColor: paleColor }}
                                        />
                                        <div className="card-body d-flex flex-column p-0 align-items-center">
                                            <div className="skeleton-block structural-title mb-2" />
                                            <div className="skeleton-block structural-text mb-1 w-100" />
                                            <div className="skeleton-block structural-text mb-3 w-75" />
                                            <div className="skeleton-block structural-btn mt-auto rounded-pill w-100" />
                                        </div>
                                    </div>
                                </div>
                            );
                        })
                    }
                </div>

                <div className="text-center mt-5">
                    <Link to="/catalog" className="btn btn-custom btn-lg rounded-pill px-4">
                        Смотреть весь каталог →
                    </Link>
                </div>
            </div>
        </section>
    );
}