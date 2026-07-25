import { Link } from "react-router-dom";

export default function DeviceCard({ device }) {
    return (
        <Link
            to={`/device/${device.id}`}
            className="text-decoration-none" // Убирает подчеркивание
            style={{ display: 'block' }} // Чтобы ссылка занимала всю область
        >
            <div className="card device-card h-100 border-0 p-3 rounded-4 shadow-sm text-center">
                <div className="image-container mb-3 rounded-3">
                    <img
                        src={device.image || "/placeholder.png"}
                        alt={device.name}
                        className="device-image img-fluid"
                    />
                </div>
                <div className="card-body d-flex flex-column p-0">
                    <h3 className="device-card-title h5 mb-2">{device.name}</h3>
                </div>
            </div>
        </Link>
    );
}