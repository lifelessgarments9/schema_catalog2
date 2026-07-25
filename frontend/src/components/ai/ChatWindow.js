import ChatMessage from "./ChatMessage";

export default function ChatWindow({messages, loading}){
    return(
        <div
            className="flex-grow-1 overflow-auto p-4 d-flex flex-column">
            {messages.map(m=> <ChatMessage key={m.id} message={m}/>)}
            {loading && (
                <div className="text-start mb-3">
                    <div className="d-inline-block p-3 rounded bg-light">
                        <span className="spinner-grow spinner-grow-sm me-1" />
                        <span className="spinner-grow spinner-grow-sm me-1" style={{ animationDelay: "0.2s" }} />
                        <span className="spinner-grow spinner-grow-sm" style={{ animationDelay: "0.4s" }} />
                    </div>
                </div>
            )}
        </div>
    );
}