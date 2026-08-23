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
        <div className={centered ? "flex-grow-1 d-flex justify-content-center align-items-center w-100" : "w-100"}>
            <div
                className="d-flex gap-2 mx-auto custom-input-group"
                style={{ maxWidth: centered ? "640px" : "100%" }}
            >
                <input
                    className="form-control custom-input px-4 py-2"
                    value={text}
                    onChange={e => setText(e.target.value)}
                    onKeyDown={e => {
                        if (e.key === "Enter") submit();
                    }}
                    disabled={disabled}
                    placeholder={disabled ? "" : "Введите сообщение..."}
                />

                <button
                    className="btn btn-custom"
                    onClick={submit}
                    disabled={disabled}
                >
                    Отправить
                </button>
            </div>
        </div>
    );
}