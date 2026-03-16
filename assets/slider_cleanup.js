function hideSliderTooltips() {
  document.querySelectorAll('.sidebar-panel [class*="rc-slider-tooltip"], .sidebar-panel [role="tooltip"]').forEach((node) => {
    node.remove();
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
