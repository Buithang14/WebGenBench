(function () {
  const form = document.getElementById("login-form");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const emailError = document.getElementById("email-error");
  const passwordError = document.getElementById("password-error");
  const togglePassword = document.getElementById("toggle-password");
  const status = document.getElementById("form-status");
  const success = document.getElementById("success");
  const successMessage = document.getElementById("success-message");
  const backToForm = document.getElementById("back-to-form");
  const forgotLink = document.querySelector(".forgot");
  const eye = togglePassword.querySelector(".icon-eye");
  const eyeOff = togglePassword.querySelector(".icon-eye-off");

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  function setError(input, errorEl, message) {
    input.setAttribute("aria-invalid", "true");
    errorEl.textContent = message;
  }

  function clearError(input, errorEl) {
    input.setAttribute("aria-invalid", "false");
    errorEl.textContent = "";
  }

  function validateEmail() {
    const value = emailInput.value.trim();
    if (!value) {
      setError(emailInput, emailError, "Vui lòng nhập email.");
      return false;
    }
    if (!emailPattern.test(value)) {
      setError(emailInput, emailError, "Email không đúng định dạng.");
      return false;
    }
    clearError(emailInput, emailError);
    return true;
  }

  function validatePassword() {
    const value = passwordInput.value;
    if (!value.trim()) {
      setError(passwordInput, passwordError, "Vui lòng nhập mật khẩu.");
      return false;
    }
    if (value.length < 6) {
      setError(passwordInput, passwordError, "Mật khẩu cần tối thiểu 6 ký tự.");
      return false;
    }
    clearError(passwordInput, passwordError);
    return true;
  }

  togglePassword.addEventListener("click", function () {
    const showing = passwordInput.type === "text";
    passwordInput.type = showing ? "password" : "text";
    togglePassword.setAttribute("aria-pressed", showing ? "false" : "true");
    togglePassword.setAttribute("aria-label", showing ? "Hiện mật khẩu" : "Ẩn mật khẩu");
    eye.hidden = !showing;
    eyeOff.hidden = showing;
  });

  emailInput.addEventListener("input", function () {
    if (emailInput.getAttribute("aria-invalid") === "true") {
      validateEmail();
    }
  });

  passwordInput.addEventListener("input", function () {
    if (passwordInput.getAttribute("aria-invalid") === "true") {
      validatePassword();
    }
  });

  forgotLink.addEventListener("click", function (event) {
    event.preventDefault();
    status.textContent = "Liên kết đặt lại mật khẩu sẽ được gửi tới email đã đăng ký.";
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    status.textContent = "";

    const emailOk = validateEmail();
    const passwordOk = validatePassword();

    if (!emailOk || !passwordOk) {
      (emailOk ? passwordInput : emailInput).focus();
      return;
    }

    const email = emailInput.value.trim();
    form.hidden = true;
    success.hidden = false;
    successMessage.textContent = "Đăng nhập thành công với " + email + ".";
  });

  backToForm.addEventListener("click", function () {
    form.reset();
    clearError(emailInput, emailError);
    clearError(passwordInput, passwordError);
    passwordInput.type = "password";
    togglePassword.setAttribute("aria-pressed", "false");
    togglePassword.setAttribute("aria-label", "Hiện mật khẩu");
    eye.hidden = false;
    eyeOff.hidden = true;
    success.hidden = true;
    form.hidden = false;
    status.textContent = "";
    emailInput.focus();
  });
})();
