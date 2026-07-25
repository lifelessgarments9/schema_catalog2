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

export default function ChatsPage({ currentUser }) {

    const {id} = useParams();
    const navigate = useNavigate();
    const [chats,setChats]=useState([]);
    const [messages,setMessages]=useState([]);
    const [showLogin, setShowLogin] = useState(false);
    const [loading, setLoading] = useState(false);
    const [waitingMessage, setWaitingMessage] = useState("");

    useEffect(() => {
        if (currentUser)
            loadChats();
    }, [currentUser]);

    useEffect(() => {
        if(!currentUser) return;
        if (id) loadMessages();
        else setMessages([]);
    }, [id, currentUser]);

    async function loadChats(){
        setChats(await getChats());
    }

    async function loadMessages(){
        setMessages(await getChat(id));
    }

    async function send(message){
        if(!currentUser){
            setShowLogin(true);
            return;
        }

        const userMsg = { id: Date.now(), role: "user", content: message };
        setMessages(prev => [...prev, userMsg]);
        setWaitingMessage(message);
        setLoading(true);

        const result=await askAI(message,id);
        setLoading(false);

        if(!id){
            setMessages([]);
            await loadChats();
            navigate(`/chats/${result.chat_id}`, { replace: true });
            return;
        }

        setMessages(prev => [
            ...prev.slice(0, -1),
            ...result.messages,
        ]);
    }

    async function remove(chatId){

        if(!window.confirm("Удалить чат?"))
            return;

        await deleteChat(chatId);

        if(chatId===id)
            navigate("/chats");

        await loadChats();
    }

    return(
        <div className="container-fluid p-0">
            <div className="row g-0 chat-container">
                <ChatSidebar
                    chats={chats}
                    current={id}
                    onDelete={remove}/>
                <div className="col d-flex flex-column">
                    <div className="chat-messages flex-grow-1 d-flex flex-column">
                        {id ? <ChatWindow messages={messages} loading={loading}/>
                            : <EmptyChat loading={loading} message={waitingMessage}/>}
                    </div>
                    <div className="chat-input p-3">
                        <ChatInput centered={!id} onSend={send} disabled={loading}/>
                    </div>
                </div>
            </div>
            {showLogin && <LoginRequired onClose={() => setShowLogin(false)} />}
        </div>
    );
}