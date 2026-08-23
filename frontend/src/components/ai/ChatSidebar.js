import { Link } from "react-router-dom";

export default function ChatSidebar({ chats, current, onDelete }) {
    return (
        <div className="col-3 p-3 h-100 overflow-auto">
            {chats.map(chat => (
                <div
                    key={chat.id}
                    className={`card mb-2 ${current == chat.id ? "border-primary" : ""}`}
                >
                    <div className="card-body p-3 d-flex align-items-center justify-content-between">
                        <Link
                            to={`/chats/${chat.id}`}
                            className="text-decoration-none text-truncate fw-medium"
                            style={{ color: "inherit" }}
                        >
                            {chat.title || `Чат ${chat.id}`}
                        </Link>

                        <button
                            className="btn btn-sm btn-danger float-end ms-2"
                            onClick={() => onDelete(chat.id)}
                            title="Удалить чат"
                        >
                            ×
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );
}