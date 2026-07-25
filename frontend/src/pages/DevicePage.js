import { useEffect, useState } from "react";
import {useParams, useNavigate, Link} from "react-router-dom";
import { getDevice,addDeviceToCart  } from "../api";
import { ReactComponent as PDFIcon } from '../assets/pdf.svg';

export default function DevicePage({ currentUser }) {
    const { id } = useParams();
    const navigate = useNavigate();
    const [device, setDevice] = useState(null);

    useEffect(() => {
        async function load() {
            try {
                const data = await getDevice(id);
                setDevice(data);
            } catch (error) {
                console.error('Ошибка загрузки устройства:', error);
            }
        }
        load();
    }, [id]);

    async function addToCart() {
        try {
            await addDeviceToCart(device.id);

            alert("Устройство добавлено в корзину");
        }
        catch(e){
            alert("Ошибка");
        }
    }

    // загрузка
    if (!device) {
        return (
            <div className="d-flex justify-content-center align-items-center py-5 my-5">
                <div className="spinner-border text-muted opacity-50" role="status">
                    <span className="visually-hidden">Загрузка...</span>
                </div>
            </div>
        );
    }

    return (
        <section className="device-detail-section py-5">
            <div className="container">
                <button onClick={() => navigate('/catalog')} className="btn btn-back btn-sm mb-4">
                    ← Назад в каталог
                </button>

                <div className="card device-detail-card border-0 p-4 p-md-5 rounded-4 shadow-sm">
                    <div className="row g-5">
                        {/* Левая колонка: Картинка и спецификации */}
                        <div className="col-12 col-md-5">
                            {/* Картинка - слева вверху */}
                            <div className="image-detail-container rounded-4 p-3 mb-4">
                                <img
                                    src={device.image || "/placeholder.png"}
                                    alt={device.name}
                                    className="img-fluid device-detail-image"
                                />
                            </div>

                            {/* Спецификации ПОД картинкой */}
                            <div className="specifications-grid">
                                <h5 className="fw-bold mb-3">Технические параметры</h5>
                                <div className="row g-2" style={{ fontSize: '0.8rem' }}>
                                    {Object.entries(device.specifications).map(([key, value]) => (
                                        <div key={key} className="col-12">
                                            <div className="d-flex justify-content-between border-bottom py-2 gap-3">
                                                <span className="text-muted">{key}</span>
                                                <span className="text-muted">{value}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="col-12 col-md-7">
                            <span
                                className="badge category-badge rounded-pill px-3 py-2 mb-3"
                                style={{ cursor: "pointer" }}
                                onClick={() => navigate(`/catalog`)}
                                role="button"
                            >
                                {device.category_name || "Микросхемы"}
                            </span>

                            <h1 className="device-detail-title mb-3 fw-bold">{device.name}</h1>
                            <p className="device-detail-desc text-muted mb-4">{device.description}</p>

                            <div className="device-info-grid mb-4 p-3 rounded-3">
                                {currentUser?.is_staff && (
                                    <div className="d-flex justify-content-between border-bottom py-2">
                                        <span className="info-label text-muted">Место хранения</span>
                                        <span className="info-value fw-semibold">{device.manufacturer || "Не указан"}</span>
                                    </div>)}
                                <div className="d-flex justify-content-between py-2">
                                    <span className="info-label text-muted">Количество на складе</span>
                                    <span className="info-value fw-semibold">{device.quantity} шт.</span>
                                </div>
                            </div>
                            {device.documentation && (
                                <a
                                    href={device.documentation}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="btn btn-custom rounded-pill px-4 py-2 d-inline-flex align-items-center gap-2"
                                >
                                    <PDFIcon className="pdf-icon"/>
                                </a>
                            )}
                            <div className="text-center mt-5">
                                <button
                                    className="btn btn-custom btn-lg rounded-pill px-4"
                                    onClick={addToCart}
                                >
                                    В корзину
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}