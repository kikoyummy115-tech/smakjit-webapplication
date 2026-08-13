document.addEventListener("DOMContentLoaded", () => {
  const passwordInput = document.getElementById("password");
  const toggleButton = document.getElementById("togglePassword");
  const eyeIcon = document.getElementById("eyeIcon");

  if (passwordInput && toggleButton && eyeIcon) {
    toggleButton.addEventListener("click", () => {
      const isPassword = passwordInput.getAttribute("type") === "password";

      passwordInput.setAttribute("type", isPassword ? "text" : "password");
      eyeIcon.textContent = isPassword ? "visibility_off" : "visibility";
    });
  }
});
