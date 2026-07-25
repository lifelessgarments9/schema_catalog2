export default function ChatMessage({message}){
    return(
        <div className={`mb-3 text-${message.role==="user"?"end":"start"}`}>
            <div className={`d-inline-block p-3 rounded ${
                message.role==="user" ? "bg-primary text-white" : "bg-light"}`}>
                {message.content}
            </div>
        </div>
    );
}