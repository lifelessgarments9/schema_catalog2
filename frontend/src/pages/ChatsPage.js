import {useEffect, useState} from "react";
import {useNavigate, useParams} from "react-router-dom";

import {
    getChats,
    getChat,
    askAI,
    deleteChat
} from "../api";

import ChatSidebar from "../components/ai/ChatSidebar";
import ChatWindow from "../components/ai/ChatWindow";
import ChatInput from "../components/ai/ChatInput";
import EmptyChat from "../components/ai/EmptyChat";
import LoginRequired from "../components/ai/LoginRequired";
import Modal from "../components/Modal";
import Toast from "../components/Toast";

export default function ChatsPage({ currentUser }) {

    const {id} = useParams();
    const navigate = useNavigate();
    const [chats,setChats]=useState([]);
    const [messages,setMessages]=useState([]);
    const [showLogin, setShowLogin] = useState(false);
    const [loading, setLoading] = useState(false);
    const [waitingMessage, setWaitingMessage] = useState("");

    const [modal, setModal] = useState(null);
    const [toast, setToast] = useState(null);

    useEffect(() => {
        if (currentUser)
            loadChats();
    }, [currentUser]);

    useEffect(() => {
        if(!currentUser) return;
        if (id) loadMessages();
        else setMessages([]);
    }, [id, currentUser]);
    useEffect(() => {
        if (id) return;
        const message = sessionStorage.getItem("ai_waiting");
        if (message) {
            setWaitingMessage(message);
            setLoading(true);
        }
    }, [id]);

    async function loadChats(){
        setChats(await getChats());
    }

    async function loadMessages() {
        const data = await getChat(id);

        if (!Array.isArray(data)) {
            console.error("Ошибка загрузки сообщений:", data);
            setMessages([]);
            setLoading(false);
            return;
        }

        setMessages(data);
        setLoading(data.at(-1)?.role === "user");
    }

    async function send(message) {
        if (!currentUser) {
            setShowLogin(true);
            return;
        }
        setLoading(true);
        if (!id) {
            setWaitingMessage(message);
            sessionStorage.setItem("ai_waiting", message);
        } else {
            setMessages(prev => [
                ...prev,
                {
                    id: Date.now(),
                    role: "user",
                    content: message
                }
            ]);
        }
        try {
            const result = await askAI(message, id);
            sessionStorage.removeItem("ai_waiting");
            if (!id) {
                await loadChats();
                navigate(`/chats/${result.chat_id}`, { replace: true });
                return;
            }

            setMessages(prev => [
                ...prev,
                result.messages[1]
            ]);
        } catch (error) {
            sessionStorage.removeItem("ai_waiting");
            if (error.status === 429) {
                setWaitingMessage("");
                setToast({message: "Лимит запросов на сегодня исчерпан"});
                return;
            }
            console.error(error);
            setToast({message: "Не удалось отправить сообщение."});
        } finally {
            setLoading(false);
        }
    }

    async function remove(chatId) {
        setModal({
            title: "Удалить чат?",
            message: "Вся история сообщений будет потеряна.",
            onConfirm: async () => {
                await deleteChat(chatId);
                if (chatId === id) navigate("/chats");
                await loadChats();
                setModal(null);
            },
        });
    }

    return(
        <div className="container-fluid p-0">
            <div className="row g-0 chat-container">
                <ChatSidebar
                    chats={chats}
                    current={id}
                    onDelete={remove}/>
                <div className="col">
                    <div className="chat-messages custom-scroll">
                        {id ? <ChatWindow messages={messages} loading={loading}/>
                            : <EmptyChat loading={loading} message={waitingMessage}/>}
                    </div>
                    <div className="chat-input p-3">
                        <ChatInput centered={!id} onSend={send} disabled={loading}/>
                    </div>
                </div>
            </div>
            {showLogin && <LoginRequired onClose={() => setShowLogin(false)} message="Чтобы использовать ИИ-ассистента, необходимо войти" />}
            {modal && (
                <Modal
                    title={modal.title}
                    message={modal.message}
                    confirmText={modal.confirmText}
                    onConfirm={modal.onConfirm}
                    onCancel={() => setModal(null)}
                />
            )}
            {toast && (
                <Toast
                    message={toast.message}
                    onClose={() => setToast(null)}
                />
            )}
        </div>
    );
}