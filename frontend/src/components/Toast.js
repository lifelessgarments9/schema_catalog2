import { useEffect } from "react";

export default function Toast({ message, onClose, duration = 3000 }) {
    useEffect(() => {
        const timer = setTimeout(onClose, duration);
        return () => clearTimeout(timer);
    }, [onClose, duration]);

    return (
        <div className="position-fixed top-0 start-50 translate-middle-x mt-4" style={{ zIndex: 2000 }}>
            <div className="alert alert-success shadow py-2 px-4 d-flex align-items-center gap-2">
                <span>{message}</span>
                <button className="btn-close ms-2" onClick={onClose} />
            </div>
        </div>
    );
}