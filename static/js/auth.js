async function RegistrationFormShow() {
    const modal_login_form = bootstrap.Modal.getInstance(document.getElementById("LoginForm"))
    if (modal_login_form) modal_login_form.hide();

    const modal_form = document.getElementById("RegistrationForm")
    const modal = new bootstrap.Modal(modal_form);

    const user_name = modal_form.querySelector("#user_name")
    const user_email = modal_form.querySelector("#user_email")
    const user_pass = modal_form.querySelector("#user_pass")

    user_name.value = "";
    user_email.value = "";
    user_pass.value = "";

    const submit_btn = modal_form.querySelector(".btn-primary");
    submit_btn.onclick = async function () {
        if (user_name.value === "" || user_email.value === "" || user_pass.value === ""){
            swal("Specify all input fields");
            return;
        }
        if (await registerUser())
            modal.hide();
    };
    modal.show();
}

async function LogoutUser() {
    localStorage.setItem("accessToken", "");
    localStorage.setItem("refreshToken", "");
    if (window.location.pathname === "/chat")
        contentClear();
    const btn_logout = document.getElementById("btn_logout");
    btn_logout.style.display = "none";
    const btn_login = document.getElementById("btn_login");
    btn_login.style.display = "inline-block";
}

function contentClear() {
    global_mdg.replaceChildren();
    const rows = document.querySelector("tbody");
    while (rows.rows.length)
        rows.deleteRow(0);
    work_file.setAttribute("data-bs-id", "");
    work_file.value = "";
}

async function LoginFormShow() {

    const modal_form = document.getElementById("LoginForm")
    const modal = new bootstrap.Modal(modal_form);

    modal_form.querySelector("#UserEmail").value = "";
    modal_form.querySelector("#UserPass").value = "";

    const submit_btn = modal_form.querySelector(".btn-primary");
    submit_btn.onclick = async function () {
        if (await loginUser())
            modal.hide();
    };
    modal.show();
}

async function registerUser() {
    const response = await fetch("/api/auth/signup/", {
        method: "POST",
        headers: {"Accept": "application/json", "Content-Type": "application/json"},
        body: JSON.stringify({
            username: document.getElementById("user_name").value,
            email: document.getElementById("user_email").value,
            password: document.getElementById("user_pass").value
        })
    });
    if (response.ok === true)
        await LoginFormShow();
    else await error_code_processing(response);
    return response.ok
}

async function loginUser() {
    const modal_form = document.getElementById("LoginForm")

    const response = await fetch("/api/auth/login/", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: new URLSearchParams({
            username: modal_form.querySelector("#UserEmail").value,
            password: modal_form.querySelector("#UserPass").value
        })
    });
    console.log(response.status, response.statusText)

    if (response.ok === true) {
        if (response.status === 200) {
            const result = await response.json()
            localStorage.setItem('accessToken', result.access_token)
            localStorage.setItem('refreshToken', result.refresh_token)
            const btn_login = document.getElementById("btn_login");
            btn_login.style.display = "none";
            const btn_logout = document.getElementById("btn_logout");
            btn_logout.style.display = "inline-block";
        }
    }
    else await error_code_processing(response);
    return response.ok
}

async function checkUser() {
    const token = localStorage.getItem('accessToken');
    const response = await fetch("/api/users/me", {
        method: "GET",
        headers: {
            "Accept": "application/json",
            Authorization: `Bearer ${token}`,
        }
    });

    if (response.ok === true) {
        const btn_logout = document.getElementById("btn_logout");
        btn_logout.style.display = "inline-block";
    }
    else{
        const btn_login = document.getElementById("btn_login");
        btn_login.style.display = "inline-block";
    }
}