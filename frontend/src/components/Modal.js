export default function Modal({ title, message, onConfirm, onCancel, confirmText = "Да", cancelText = "Отмена" }) {
    return (
        <div
            className="position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center"
            style={{ background: "rgba(0,0,0,.35)", zIndex: 2000 }}
        >
            <div className="card p-4">
                {title && <h5 className="mb-2 fw-semibold">{title}</h5>}
                <p className="mb-4 text-muted small">{message}</p>
                <div className="d-flex gap-2 justify-content-end">
                    <button className="btn btn-outline-secondary rounded-pill px-3" onClick={onCancel}>
                        {cancelText}
                    </button>
                    <button className="btn btn-custom rounded-pill px-3" onClick={onConfirm}>
                        {confirmText}
                    </button>
                </div>
            </div>
        </div>
    );
}