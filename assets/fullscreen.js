function createFullscreenButton(card) {
  const button = document.createElement("a");
  button.className = "modebar-btn plotly-fullscreen-btn";
  button.setAttribute("data-title", "Fullscreen");
  button.setAttribute("role", "button");
  button.innerHTML = `
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path fill="currentColor" d="M7 3H3v4h2V5h2V3zm12 0h-4v2h2v2h2V3zM5 15H3v4h4v-2H5v-2zm14 0v2h-2v2h4v-4h-2z"/>
    </svg>
  `;

  button.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();

    if (document.fullscreenElement === card) {
      document.exitFullscreen();
      return;
    }

    card.requestFullscreen?.();
  });

  return button;
}

function installFullscreenButtons() {
  const cards = document.querySelectorAll('[id$="-card"]');

  cards.forEach((card) => {
    const modebar = card.querySelector(".modebar");
    if (!modebar) return;
    if (modebar.querySelector(".plotly-fullscreen-btn")) return;

    const firstGroup = modebar.querySelector(".modebar-group");
    const group = document.createElement("div");
    group.className = "modebar-group";
    group.appendChild(createFullscreenButton(card));

    modebar.appendChild(group);
  });
}

const observer = new MutationObserver(() => {
  installFullscreenButtons();
});

observer.observe(document.documentElement, {
  childList: true,
  subtree: true,
});

window.addEventListener("load", installFullscreenButtons);
document.addEventListener("DOMContentLoaded", installFullscreenButtons);
