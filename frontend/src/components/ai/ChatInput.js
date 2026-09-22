import {useState,useRef} from "react";

export default function ChatInput({onSend, centered, disabled}){
    const [text,setText]=useState("");
    const textareaRef = useRef(null);

    async function submit(){
        if(!text.trim()|| disabled) return;
        const msg = text;
        setText("");
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
        }
        await onSend(msg);
    }

    function autoResize(e) {
        const el = e.target;
        el.style.height = "auto";        // сброс, чтобы уменьшилось при удалении
        el.style.height = el.scrollHeight + "px";  // подгон под контент
    }

    function handleKeyDown(e) {
        // Enter — отправить, Shift+Enter — новая строка
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
        }
    }

    return(
        <div className={centered ? "flex-grow-1 d-flex justify-content-center align-items-center w-100" : "w-100"}>
            <div
                className="d-flex gap-2 mx-auto custom-input-group"
                style={{ maxWidth: centered ? "640px" : "100%" }}
            >
                <textarea
                    ref={textareaRef}
                    className="form-control custom-input px-4 py-2"
                    value={text}
                    rows={1}
                    onChange={e => {
                        setText(e.target.value);
                        autoResize(e);
                    }}
                    onKeyDown={handleKeyDown}
                    disabled={disabled}
                    placeholder={disabled ? "" : "Введите сообщение..."}
                    style={{
                        resize: "none",        // убираем ручной ресайз
                        overflow: "hidden",    // прячем скролл, пока растёт
                        maxHeight: "200px",    // ограничение роста
                        lineHeight: "1.5",
                    }}
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