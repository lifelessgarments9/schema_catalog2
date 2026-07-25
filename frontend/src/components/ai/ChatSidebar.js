import { Link} from "react-router-dom";

export default function ChatSidebar({chats, current, onDelete}){

    return(

        <div className="col-3 border-end p-3 h-100 overflow-auto">

            {
                chats.map(chat=>

                    <div
                        key={chat.id}
                        className={`card mb-2 ${current==chat.id?"border-primary":""}`}>

                        <div className="card-body">

                            <Link
                                to={`/chats/${chat.id}`}
                                className="text-decoration-none">

                                {chat.title||`Чат ${chat.id}`}

                            </Link>

                            <button
                                className="btn btn-sm btn-danger float-end"
                                onClick={()=>onDelete(chat.id)}>

                                ×

                            </button>

                        </div>

                    </div>

                )
            }

        </div>

    );

}