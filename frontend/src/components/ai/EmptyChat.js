import ChatMessage from "./ChatMessage";

export default function EmptyChat({ loading, message }) {
    return (
        <div className="flex-grow-1 d-flex flex-column">
            {!message && !loading && (
                <div className="flex-grow-1 d-flex justify-content-center align-items-center">
                    <div className="text-center">
                        <h2>ИИ ассистент Фаблаб</h2>
                        <p className="text-muted">
                            Задайте вопрос по оборудованию лаборатории.
                        </p>
                    </div>
                </div>
            )}

            {message && (
                <div className="p-4">
                    <ChatMessage message={{ id: 0, role: "user", content: message }} />
                </div>
            )}

            {loading && (
                <div className="p-4">
                    {message && <ChatMessage message={{ id: 0, role: "user", content: message }} />}
                    <div className="text-start mb-3">
                        <div className="d-inline-block p-3 rounded bg-light">
                            <span className="spinner-grow spinner-grow-sm me-1" />
                            <span className="spinner-grow spinner-grow-sm me-1" style={{ animationDelay: "0.2s" }} />
                            <span className="spinner-grow spinner-grow-sm" style={{ animationDelay: "0.4s" }} />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}