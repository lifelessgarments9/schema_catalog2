import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import DeviceCard from "../components/DeviceCard";
import { getDevices } from "../api";

export default function HomePage({ currentUser }) {
    const [devices, setDevices] = useState(null);

    useEffect(() => {
        load();
    }, []);

    async function load() {
        const data = await getDevices();
        setDevices(data && data.length > 0 ? data.slice(0, 4) : []);
    }
    const getRandomPaleColor = () => {
        // рандом бледный цвет
        const r = Math.floor(Math.random() * 55) + 200;
        const g = Math.floor(Math.random() * 55) + 200;
        const b = Math.floor(Math.random() * 55) + 200;
        return `rgb(${r}, ${g}, ${b})`;
    };

    return (
        <section className="home-section py-5">
            <div className="container">
                <h1 className="section-title text-center mb-5">Каталог микросхем</h1>

                {currentUser?.is_staff && (
                <div className="d-flex justify-content-end mb-4">
                    <Link to="/device/add" className="btn btn-custom btn-lg rounded-pill px-4">
                        Добавить устройство
                    </Link>
                </div>
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
                                    <div className="card device-card h-100 border-0 p-3 rounded-4 shadow-sm text-center skeleton-card">
                                        <div
                                            className="image-container mb-3 rounded-3 skeleton-block structural-img"
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