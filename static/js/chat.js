const resize_ob = new ResizeObserver(function (entries) {
    let rect = entries[0].contentRect;

    let width = rect.width;
    let height = rect.height;
    
    document.querySelector("#messages").style.height = String(height - 125) + "px"
    document.querySelector("#data_files").style.height = String(height - 80) + "px"

    const chat_input = document.querySelector("#chat_input")
    chat_input.style.width = String(width - 120) + "px"
});

// start observing for resize
resize_ob.observe(document.querySelector("#chat_box"));

const global_mdg = document.getElementById("messages")
const btn_submit = document.getElementById("btn_submit");
const btn_search = document.getElementById("btn_search");
const btn_history = document.getElementById("btn_history");
const query = document.getElementById("msg_input");

const send_glyph = document.getElementById("send_glyph");
const send_spin = document.getElementById("send_spin");
const work_file = document.getElementById("work_file");

function getCurrentTime() {
    const now = new Date();
    const hour = now.getHours();
    const minute = now.getMinutes();
    return `${hour < 10 ? '0' + hour : hour}:${minute < 10 ? '0' + minute : minute}`;
}

function createMessage(message_text, sender) {
    const messageContent = document.createElement("div");

    messageContent.classList.add("message-content", sender ?
        "message-sent" : "message-received");
    messageContent.textContent = message_text;

    const messageTime = document.createElement('div');
    messageTime.classList.add('message-time');
    messageTime.textContent = getCurrentTime();

    messageContent.appendChild(messageTime);
    global_mdg.appendChild(messageContent);

    global_mdg.scrollTop = global_mdg.scrollHeight;
}

btn_submit.onclick = async function (e) {
    const file_id = work_file.getAttribute("data-bs-id")
    e.preventDefault();
    if (file_id) {
        if (query.value) {
            send_glyph.style.display = "none";
            send_spin.style.display = "inline-block";
            try {
                createMessage(query.value, true)
                await sendMessage(query.value, file_id)
                query.value = ""
            } finally {
                send_glyph.style.display = "inline-block";
                send_spin.style.display = "none";
            }
        }
        else
            swal("Write your message, please.");
    }
    else {
        swal("Specify a work file, please.");
        const files_tab = document.getElementById("pills-files-tab");
        files_tab.click()
    }
}

async function sendMessage(message_text, doc_id) {
    const token = localStorage.getItem('accessToken');

    const response = await fetch("/api/chats/", {
        method: "POST",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
            document_id: doc_id,
            question: message_text
        })
    });
    if (response.ok === true) {
        const answer = await response.json();
        createMessage(answer.answer, false)
    }
    else await error_code_processing(response);
}
