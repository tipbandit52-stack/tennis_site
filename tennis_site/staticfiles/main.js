// --- Подтверждение удаления для всех ссылок с data-confirm ---
document.addEventListener('click', function (e) {
  const a = e.target.closest('a[data-confirm]');
  if (a) {
    const msg = a.getAttribute('data-confirm') || 'Удалить?';
    if (!confirm(msg)) e.preventDefault();
  }
});

// --- Обрезка фото при редактировании профиля ---
let cropper;
const input = document.querySelector('input[type="file"]'); // файл из формы Django
const preview = document.getElementById("preview");
const cropBtn = document.getElementById("cropButton");

if (input && preview && cropBtn) {
  input.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      preview.src = reader.result;
      preview.style.display = "block";
      cropBtn.style.display = "inline-block";

      if (cropper) cropper.destroy();
      cropper = new Cropper(preview, {
        aspectRatio: 1,   // квадрат (можно поменять на 4/3 или др.)
        viewMode: 1,
      });
    };
    reader.readAsDataURL(file);
  });

  cropBtn.addEventListener("click", () => {
    if (!cropper) return;

    const canvas = cropper.getCroppedCanvas({
      width: 400,
      height: 400,
    });

    canvas.toBlob((blob) => {
      // Создаём новый объект File и вставляем его в input
      const file = new File([blob], "avatar.png", { type: "image/png" });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      input.files = dataTransfer.files;

      alert("Фото обрезано! Теперь нажмите 'Сохранить'.");
    });
  });
}

// --- Уведомления о новых сообщениях (WebSocket) ---
if (window.userIsAuthenticated) { // см. ниже, как передать этот флаг
  const notifSocket = new WebSocket("ws://" + window.location.host + "/ws/notifications/");

  notifSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const badge = document.getElementById("chat-unread");
    if (badge) {
      if (data.unread_count > 0) {
        badge.innerText = data.unread_count;
        badge.style.display = "inline-block";
      } else {
        badge.style.display = "none";
      }
    }
  };
}

document.getElementById("chat-form").onsubmit = function(e) {
  e.preventDefault();  // ← вот эта строка важна
  const input = document.getElementById("chat-message-input");
  if (input.value.trim() !== "") {
    chatSocket.send(JSON.stringify({ "message": input.value }));
    input.value = "";
  }
};


