function newTableRow(file) {
    let tr = document.createElement("tr");
    tr.setAttribute("data-rowid", file.id);
    let td = document.createElement("td");
    td.className = "text-end";
    td.innerHTML = file.id;
    tr.append(td);
    td = document.createElement("td");
    td.className = "text-start";
    td.innerHTML = file.name;
    tr.append(td);

    td = document.createElement("td");

    let button = document.createElement("button");
    button.className = "btn btn-outline-success btn-edit";
    button.innerHTML = "<span class=\'btn-label\'><i class=\'fa fa-check\'></i></span>";
    button.setAttribute("style", "--bs-btn-padding-y: .2rem; --bs-btn-padding-x: .5rem; " +
        "--bs-btn-font-size: .5rem;");
    button.onclick = function () {
        selectFile(file.id, file.name);
    }
    td.append(button);
    tr.append(td);

    td = document.createElement("td");
    button = document.createElement("button");
    button.className = "btn btn-outline-danger btn-delete";
    button.innerHTML = "<span class=\'btn-label\'><i class=\'fa fa-minus\'></i></span>";
    button.setAttribute("style", "--bs-btn-padding-y: .2rem; --bs-btn-padding-x: .5rem; " +
        "--bs-btn-font-size: .5rem;");
    button.onclick = async function () {
        await DeleteFileFormShow(file.id);
    }

    td.append(button);
    tr.append(td);

    return tr;
}

async function uploadFiles() {
    const add_file_spin = document.getElementById("add_file_spin");
    const add_file_glyph = document.getElementById("add_file_glyph");

    let input = document.createElement("input");
    input.setAttribute("type", "file");
    input.setAttribute("multiple", "");
    input.onchange = async _ => {
        add_file_glyph.style.display = "none";
        add_file_spin.style.display = "inline-block";
        try {
            let files = Array.from(input.files);
            let result;
            let created_files = [];
            for (let i = 0; i < files.length; i++) {
                result = await sendFile(files[i])
                if (result) created_files.push(result)
            }
            if (created_files.length) {
                for (let i = 0; i < created_files.length; i++) {
                    document.querySelector("tbody").append(newTableRow(created_files[i]));
                }
            }
        } finally {
            add_file_glyph.style.display = "inline-block";
            add_file_spin.style.display = "none";
        }
    };
    input.click();
}

async function sendFile(file) {
    const token = localStorage.getItem('accessToken');
    const form_data = new FormData();
    form_data.append("file", file, file.name);
    let result = null;
    const response = await fetch("/api/files/doc", {
        method: "POST",
        headers: {
            "Accept": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: form_data
    });
    if (response.ok === true)
        result = await response.json();
    else await error_code_processing(response);
    return result
}

function selectFile(file_id, file_name) {
    work_file.setAttribute("data-bs-id", String(file_id));
    work_file.value = file_name;
    global_mdg.replaceChildren();
}

btn_history.onclick = async function (e) {
    e.preventDefault();
    let doc_id = work_file.getAttribute("data-bs-id");
    if (doc_id === "") {
        const last_doc = await getLastFile();
        doc_id = last_doc.id;
        work_file.setAttribute("data-bs-id", last_doc.id);
        work_file.value = last_doc.name;
    }
    if (doc_id !== "") {
        const history = await getHistory(doc_id);
        await showHistory(history);
    }
}

async function getLastFile() {
    const token = localStorage.getItem('accessToken');
    let last_doc = null;
    const response = await fetch("/api/files/last_document", {
        method: "GET",
        headers: {
            "Accept": "application/json",
            Authorization: `Bearer ${token}`,
        }
    });

    if (response.ok === true)
        last_doc = await response.json();
    else await error_code_processing(response);

    return last_doc;
}

async function getHistory(file_id) {
    const url = `/api/chats/?document_id=${file_id}`
    const token = localStorage.getItem('accessToken');
    let history = null

    const response = await fetch(url, {
        method: "GET",
        headers: {
            "Accept": "application/json",
            Authorization: `Bearer ${token}`,
        }
    });

    if (response.ok === true)
        history = await response.json();
    else await error_code_processing(response);

    return history;
}

async function showHistory(history) {
    if (history) {
        global_mdg.replaceChildren();
        history.forEach(rec => createHistoryMessage(rec));
        global_mdg.scrollTop = global_mdg.scrollHeight;
    }
}

function createHistoryMessage(rec) {
    const messages = [{"sender": true, "text": rec.question, "date": rec.created_at},
        {"sender": false, "text": rec.answer, "date": rec.created_at}];
    messages.forEach(msg => printMessage(msg));
}

function printMessage(msg) {
    const messageContent = document.createElement("div");

    if (msg["sender"])
        messageContent.classList.add("message-content", "message-sent");
    else
        messageContent.classList.add("message-content", "message-received");

    messageContent.textContent = msg["text"];

    const messageData = document.createElement('div');
    messageData.classList.add('message-time');
    messageData.textContent = msg["date"];

    messageContent.appendChild(messageData);
    global_mdg.appendChild(messageContent);
}

btn_search.onclick = async function (e) {
    e.preventDefault();
    let filter_str = document.getElementById("filter_str").value;
    await getFiles(filter_str)
}

async function getFiles(filter_str) {
    let url_str
    if (filter_str)
        url_str = `/api/files/?search_str=${filter_str}`
    else
        url_str = "/api/files"

    const token = localStorage.getItem('accessToken');

    const response = await fetch(url_str, {
        method: "GET",
        headers: {
            "Accept": "application/json",
            Authorization: `Bearer ${token}`,
        }
    });
    if (response.ok === true) {
        const files = await response.json();
        const rows = document.querySelector("tbody");

        while (rows.rows.length)
            rows.deleteRow(0);

        files.forEach(file => rows.append(newTableRow(file)));
    } else await error_code_processing(response);
}

async function deleteFile(file_id) {
    const token = localStorage.getItem('accessToken');

    const response = await fetch(`/api/files/${file_id}`, {
        method: "DELETE",
        headers: {
            "Accept": "application/json",
            Authorization: `Bearer ${token}`
        },

    });
    if (response.ok === true)
        document.querySelector(`tr[data-rowid='${file_id}']`).remove();
    else await error_code_processing(response);
    return response.ok;
}

async function DeleteFileFormShow(file_id) {
    const modal_form = document.getElementById("DeleteFile")
    const modal = new bootstrap.Modal(modal_form);

    const submit_btn = modal_form.querySelector(".btn-danger");
    submit_btn.onclick = async function () {
        if (await deleteFile(file_id))
            modal.hide();
    };
    modal.show();
}
