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
        }
        finally {
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
    if (response.ok === true) {
        result =  await response.json();
    } else {
        if (response.status === 422)
            alert("Input data is invalid");
        else {
            alert("fghfghfgh");
            const error = await response.json();
            alert(error.detail);
        }
    }
    return result
}

function selectFile(file_id, file_name) {
    // const work_file = document.getElementById("work_file");
    work_file.setAttribute("data-bs-id", String(file_id))
    work_file.value = file_name
}

async function getFiles() {
    let filter_str = document.getElementById("filter_str").value;

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
    } else {
        if (response.status === 401)
            alert("Not authenticated");
        else {
            const error = await response.json();
            alert(error.detail);
        }
    }
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
  if (response.ok === true) {
    document.querySelector(`tr[data-rowid='${file_id}']`).remove();
  }
  else {
    if (response.status === 401)
      alert("Not authenticated");
    else {
      const error = await response.json();
      alert(error.detail);
    }
  }
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
