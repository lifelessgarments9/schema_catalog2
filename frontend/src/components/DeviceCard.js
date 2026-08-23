import { Link } from "react-router-dom";

export default function DeviceCard({ device }) {
    return (
        <Link
            to={`/device/${device.id}`}
            className="text-decoration-none"
            style={{ display: 'block' }}
        >
            <div className="card device-card h-100 p-3 text-center">
                <div className="image-container mb-3">
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