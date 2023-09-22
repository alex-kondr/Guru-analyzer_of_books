async function RegistrationFormShow() {
    const modal_login_form = bootstrap.Modal.getInstance(document.getElementById("LoginForm"))
    if (modal_login_form) modal_login_form.hide();

    const modal_form = document.getElementById("RegistrationForm")
    const modal = new bootstrap.Modal(modal_form);

    modal_form.querySelector("#UserName").value = "";
    modal_form.querySelector("#UserEmail").value = "";
    modal_form.querySelector("#UserPass").value = "";

    const submit_btn = modal_form.querySelector(".btn-primary");
    submit_btn.onclick = async function () {
        if (await registerUser())
            modal.hide();
    };

    modal.show();
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
    const user_name = document.getElementById("UserName").value;

    const response = await fetch("/api/auth/signup/", {
        method: "POST",
        headers: {"Accept": "application/json", "Content-Type": "application/json"},
        body: JSON.stringify({
            username: user_name ? user_name : null,
            email: document.getElementById("UserEmail").value,
            password: document.getElementById("UserPass").value
        })
    });
    const result = await response.json();
    if (response.ok !== true) {
        if (response.status === 422) {
            swal("Input data is invalid");
        } else swal(result.detail);
    } else swal(result.detail);
    return response.ok
}

async function loginUser() {
    const modal_form = document.getElementById("LoginForm")

    // const rmCheck = modal_form.querySelector("#RememberMe")
    // const emailInput = modal_form.querySelector("#UserEmail");
    //
    // if (rmCheck.checked)
    //   localStorage.username = emailInput.value;
    // else
    //   localStorage.username = "";

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
        }
    } else {
        const error = await response.json();
        if (response.status === 422) {
            swal("Input data is invalid");
        } else
            swal(error.detail);
    }
    return response.ok
}

function RememberMeClick(rmCheck) {
    rmCheck.value = rmCheck.checked ? "1" : "0";
}

async function ForgotPassword() {
    const modal_form = document.getElementById("LoginForm")
    const response = await fetch("/api/auth/forgot_password/", {
        method: "POST",
        headers: {"Accept": "application/json", "Content-Type": "application/json"},
        body: JSON.stringify({
            email: modal_form.querySelector("#UserEmail").value
        })
    });
    if (response.ok !== true) {
        const error = await response.json();
        if (response.status === 422) {
            swal("Input data is invalid");
        } else
            swal(error.detail);
    } else {
        const message = await response.json();
        swal(message.detail);
        const modal_login_form = bootstrap.Modal.getInstance(modal_form);
        if (modal_login_form) modal_login_form.hide();
    }
}

async function ChangePassword() {
    const form = document.getElementById("ChangePasswordForm")
    const current_url = window.location.href;
    const new_password = form.querySelector("#UserPassNew").value;
    const conf_password = form.querySelector("#UserPassConf").value;

    if (new_password !== conf_password) {
        swal("The new password does not equal the confirmed password.");
    } else {
        const response = await fetch(current_url, {
            method: "PUT",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                password: new_password
            })
        });
        const result = await response.json();
        if (response.ok !== true) {
            if (response.status === 422)
                swal("Input data is invalid");
            else swal(result.detail);
        } else {
            swal(result.detail);
            window.location.href = "\\";
        }
    }
}
