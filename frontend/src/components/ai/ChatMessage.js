import { Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { ReactComponent as DeviceIcon } from '../../assets/device.svg';

export default function ChatMessage({ message }) {
    return (
        <div className={`mb-3 chat-message-row ${message.role === "user" ? "user" : "assistant"}`}>
            <div
                className={`chat-bubble ${
                    message.role === "user"
                        ? "chat-bubble-user"
                        : "chat-bubble-assistant"
                }`}
            >
                <div className="chat-message-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                    </ReactMarkdown>
                </div>
                {message.role === "assistant" &&
                    message.sources?.length > 0 && (
                        <div className="mt-3 border-top pt-3">
                            <small className="text-muted d-block mb-2">
                                Найденные устройства:
                            </small>

                            <div className="d-flex flex-wrap gap-2">
                                {message.sources.map(device => (
                                    <Link
                                        key={device.id}
                                        to={`/device/${device.id}`}
                                        className="text-decoration-none"
                                    >
                                        <div className="badge category-badge p-2 d-flex align-items-center gap-1">
                                            <DeviceIcon style={{width: 40,height: 40}}/>
                                            <span>{device.name}</span>
                                        </div>
                                    </Link>
                                ))}
                            </div>
                        </div>
                    )}
            </div>
        </div>
    );
}