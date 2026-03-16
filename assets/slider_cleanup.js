function hideSliderTooltips() {
  document.querySelectorAll('[class*="rc-slider-tooltip"]').forEach((node) => {
    node.remove();
  });

  document.querySelectorAll(".control-block").forEach((block) => {
    const inputs = block.querySelectorAll("input");
    inputs.forEach((input, index) => {
      if (index > 0) {
        input.remove();
      }
    });

    const foreignBoxes = block.querySelectorAll("div, span");
    foreignBoxes.forEach((node) => {
      const text = (node.textContent || "").trim();
      if (!text) return;
      if (node.closest(".control-label-row")) return;
      if (text === "0" || text === "1" || text === "10" || text === "20" || text === "45" || text === "0.01" || text === "9.044") {
        const rect = node.getBoundingClientRect();
        if (rect.width < 100 && rect.height < 60) {
          node.style.display = "none";
        }
      }
    });
  });
}

const sliderObserver = new MutationObserver(() => {
  hideSliderTooltips();
});

sliderObserver.observe(document.documentElement, {
  childList: true,
  subtree: true,
});

window.addEventListener("load", hideSliderTooltips);
document.addEventListener("DOMContentLoaded", hideSliderTooltips);
