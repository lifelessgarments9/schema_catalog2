import ChatMessage from "./ChatMessage";

export default function EmptyChat({ loading, message }) {
    return (
        <div className="flex-grow-1 d-flex flex-column">
            {!message && !loading && (
                <div className="flex-grow-1 d-flex justify-content-center align-items-center">
                    <div className="text-center p-4">
                        <h2 className="section-title mb-3">ИИ ассистент Фаблаб</h2>
                        <p className="text-muted fs-6">Задайте вопрос по оборудованию лаборатории.</p>
                    </div>
                </div>
            )}

            {(message || loading) && (
                <div className="p-4">
                    {message && <ChatMessage message={{ id: 0, role: "user", content: message }} />}
                    {loading && (
                        <div className="text-start mb-3">
                            <div className="d-inline-block p-3 bg-light">
                                <span className="spinner-grow spinner-grow-sm me-1" />
                                <span className="spinner-grow spinner-grow-sm me-1" style={{ animationDelay: "0.2s" }} />
                                <span className="spinner-grow spinner-grow-sm" style={{ animationDelay: "0.4s" }} />
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}