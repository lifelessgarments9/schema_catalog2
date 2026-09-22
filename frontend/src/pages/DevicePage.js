import { useEffect, useState } from "react";
import {useParams, useNavigate, Link} from "react-router-dom";
import { getDevice,addDeviceToCart  } from "../api";
import { ReactComponent as PDFIcon } from '../assets/pdf.svg';
import Toast from "../components/Toast";
import LoginRequired from "../components/ai/LoginRequired";

export default function DevicePage({ currentUser }) {
    const { id } = useParams();
    const navigate = useNavigate();
    const [device, setDevice] = useState(null);
    const [toast, setToast] = useState(null);
    const [showLoginModal, setShowLoginModal] = useState(false);

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
        if (!currentUser) {
            setShowLoginModal(true);
            return;
        }
        if (device.quantity_storage === 0) {
            setToast({
                message: "Устройства нет на складе"
            });
            return;
        }
        try {
            await addDeviceToCart(device.id);
            setToast({ message: "Устройство добавлено в корзину" });
        }
        catch(e){setToast({ message: "Ошибка при добавлении в корзину" });}
    }
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

                <div className="card device-detail-card p-4 p-md-5">
                    <div className="row g-5">
                        {/* Левая колонка: Картинка и спецификации */}
                        <div className="col-12 col-md-5">
                            {/* Картинка - слева вверху */}
                            <div className="image-detail-container p-3 mb-4">
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
                                    {Object.entries(device.specifications || {}).map(([key, value]) => (
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
                                className="badge category-badge px-3 py-2 mb-3"
                                style={{ cursor: "pointer" }}
                                onClick={() => navigate(`/catalog/devices/?category=${device.category}`)}
                                role="button"
                            >
                                {device.category_name || "Микроконтроллер"}
                            </span>

                            <h1 className="device-detail-title mb-3">{device.name}</h1>
                            <p className="device-detail-desc text-muted mb-4">{device.description}</p>

                            {currentUser?.is_staff && (
                                <>
                                    <div className="mb-3">
                                        <div className="d-flex justify-content-between border-bottom py-2">
                                            <span className="info-label text-muted">Место хранения</span>
                                            <span className="info-value fw-semibold">
                                                {device.manufacturer || "Не указано"}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="quantity-block rounded-4 border overflow-hidden" style={{ maxWidth: "300px" }}>
                                        <div className="row g-0 text-center">
                                            <div className="col-4 py-2 border-end">
                                                <span className="text-muted small">На складе</span>
                                            </div>
                                            <div className="col-4 py-2 border-end">
                                                <span className="text-muted small">Выдано</span>
                                            </div>
                                            <div className="col-4 py-2">
                                                <span className="text-muted small">Всего</span>
                                            </div>
                                        </div>

                                        <div className="row g-0 text-center border-top">
                                            <div className="col-4 py-3 border-end">
                                                <span className="fw-semibold text-success">
                                                    {device.quantity_storage} шт.
                                                </span>
                                            </div>
                                            <div className="col-4 py-3 border-end">
                                                <span className="fw-semibold text-warning">
                                                    {device.quantity_rented} шт.
                                                </span>
                                            </div>
                                            <div className="col-4 py-3">
                                                <span className="fw-semibold">
                                                    {device.quantity} шт.
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </>
                            )}
                            {device.documentation && (
                                <a
                                    href={device.documentation}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="d-inline-flex align-items-center"
                                >
                                    <PDFIcon className="pdf-icon" style={{ width: 80, height: 80 }}/>
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
                {toast && (
                    <Toast
                        message={toast.message}
                        onClose={() => setToast(null)}
                    />
                )}
                {showLoginModal && (
                    <LoginRequired
                        onClose={() => setShowLoginModal(false)}
                        message="Чтобы добавить товар в корзину, необходимо войти в систему"
                    />
                )}
            </div>
        </section>
    );
}