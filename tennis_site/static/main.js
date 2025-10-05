/* =========================================================
   Универсальные функции и инициализация
   ========================================================= */

// --- Подтверждение удаления для всех ссылок с data-confirm ---
document.addEventListener("click", function (e) {
  const a = e.target.closest("a[data-confirm]");
  if (a) {
    const msg = a.getAttribute("data-confirm") || "Удалить?";
    if (!confirm(msg)) e.preventDefault();
  }
});

/* =========================================================
   CropperJS: обрезка фото (используется в шаблонах)
   ========================================================= */
/*
   ⚠️ Не дублируем код — CropperJS уже подключен
   внутри шаблонов player_profile_form.html и achievement_form.html.
   Здесь оставлено пустое место для совместимости.
*/

/* =========================================================
   WebSocket уведомления (новые сообщения / запросы)
   ========================================================= */
if (window.userIsAuthenticated) {
  try {
    const notifSocket = new WebSocket(
      (window.location.protocol === "https:" ? "wss://" : "ws://") +
        window.location.host +
        "/ws/notifications/"
    );

    notifSocket.onmessage = function (e) {
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

    notifSocket.onclose = function () {
      console.warn("🔌 WebSocket уведомлений закрыт.");
    };
  } catch (err) {
    console.error("Ошибка подключения WebSocket уведомлений:", err);
  }
}

/* =========================================================
   WebSocket чат
   ========================================================= */
document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const input = document.getElementById("chat-message-input");

  if (chatForm && input && window.chatSocket) {
    chatForm.onsubmit = function (e) {
      e.preventDefault();
      if (input.value.trim() !== "") {
        window.chatSocket.send(JSON.stringify({ message: input.value }));
        input.value = "";
      }
    };
  }
});

/* =========================================================
   Вспомогательные UI-анимации
   ========================================================= */
document.querySelectorAll(".fade-in").forEach((el) => {
  el.style.animation = "fadeIn .4s ease-in-out";
});
