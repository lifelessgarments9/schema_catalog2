import { useState } from "react";

function getRandomPaleColor() {
    const channel = () => Math.floor(Math.random() * 55) + 200;
    return `rgb(${channel()}, ${channel()}, ${channel()})`;
}

export default function DeviceCardSkeleton({ count = 1 }) {
    const [colors] = useState(() =>
        Array.from({ length: count }, getRandomPaleColor)
    );

    return Array.from({ length: count }, (_, index) => (
        <div key={index} className="col-12 col-sm-6 col-md-4 col-lg-3">
            <div className="card device-card h-100 p-3 text-center skeleton-card">
                <div
                    className="image-container mb-3 skeleton-block structural-img"
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
    ));
}