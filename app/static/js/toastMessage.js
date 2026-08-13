function dismissToast(toastElement) {
  if (!toastElement) return;

  toastElement.classList.add("opacity-0", "-translate-y-4", "scale-95");

  setTimeout(() => {
    toastElement.remove();

    const container = document.getElementById("toast-container");
    if (container && container.children.length === 0) {
      container.remove();
    }
  }, 300);
}

document.addEventListener("DOMContentLoaded", () => {
  const toasts = document.querySelectorAll(".toast-card");

  toasts.forEach((toast, index) => {
    setTimeout(
      () => {
        dismissToast(toast);
      },
      4000 + index * 500,
    );
  });
});
