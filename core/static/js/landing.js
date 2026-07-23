(function () {
  const root = document.querySelector('[data-screenshot-carousel]');
  if (!root) return;

  const slides = Array.from(root.querySelectorAll('[data-screenshot-slide]'));
  const dots = Array.from(root.querySelectorAll('[data-screenshot-dot]'));
  const previousButton = root.querySelector('[data-screenshot-prev]');
  const nextButton = root.querySelector('[data-screenshot-next]');
  if (!slides.length) return;

  let activeIndex = Math.max(0, slides.findIndex((slide) => slide.classList.contains('is-active')));

  function showSlide(nextIndex) {
    activeIndex = (nextIndex + slides.length) % slides.length;

    slides.forEach((slide, index) => {
      const isActive = index === activeIndex;
      slide.hidden = !isActive;
      slide.classList.toggle('is-active', isActive);
    });

    dots.forEach((dot, index) => {
      const isActive = index === activeIndex;
      dot.classList.toggle('is-active', isActive);
      dot.setAttribute('aria-current', isActive ? 'true' : 'false');
    });
  }

  previousButton?.addEventListener('click', () => showSlide(activeIndex - 1));
  nextButton?.addEventListener('click', () => showSlide(activeIndex + 1));

  dots.forEach((dot) => {
    dot.addEventListener('click', () => {
      const index = Number.parseInt(dot.dataset.screenshotIndex || '0', 10);
      showSlide(Number.isNaN(index) ? 0 : index);
    });
  });
})();
