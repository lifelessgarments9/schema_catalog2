import {useState} from "react";

export default function ChatInput({onSend, centered, disabled}){
    const [text,setText]=useState("");

    async function submit(){
        if(!text.trim()|| disabled) return;
        const msg = text;
        setText("");
        await onSend(msg);
    }

    return(
        <div className={centered ? "flex-grow-1 d-flex justify-content-center align-items-center" : "border-top p-3"}>
            <div className="input-group">
                <input
                    className="form-control"
                    value={text}
                    onChange={e=>setText(e.target.value)}
                    onKeyDown={e=>{if(e.key==="Enter") submit();}}
                    disabled={disabled}
                    placeholder={disabled ? "" : "Введите сообщение..."}
                />
                <button
                    className="btn btn-primary"
                    onClick={submit}>
                    Отправить
                </button>
            </div>
        </div>
    );
}