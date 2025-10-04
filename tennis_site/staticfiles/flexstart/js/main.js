/**
* Template Name: FlexStart (адаптировано под Tennis Site)
*/

(function() {
  "use strict";

  /**
   * Scroll animation init
   */
  function aosInit() {
    if (typeof AOS !== "undefined") {
      AOS.init({
        duration: 600,
        easing: 'ease-in-out',
        once: true,
        mirror: false
      });
    }
  }
  window.addEventListener('load', aosInit);

  /**
   * Initiate glightbox
   */
  if (typeof GLightbox !== "undefined") {
    GLightbox({ selector: '.glightbox' });
  }

  /**
   * Initiate Pure Counter
   */
  if (typeof PureCounter !== "undefined") {
    new PureCounter();
  }

  /**
   * Init swiper sliders
   */
  function initSwiper() {
    if (typeof Swiper === "undefined") return;

    document.querySelectorAll(".init-swiper").forEach(function(swiperElement) {
      const configElement = swiperElement.querySelector(".swiper-config");
      if (!configElement) return;
      let config = JSON.parse(configElement.innerHTML.trim());
      new Swiper(swiperElement, config);
    });
  }
  window.addEventListener("load", initSwiper);

  /**
   * FAQ toggle (если на сайте будут faq-item)
   */
  document.querySelectorAll('.faq-item h3, .faq-item .faq-toggle').forEach((faqItem) => {
    faqItem.addEventListener('click', () => {
      faqItem.parentNode.classList.toggle('faq-active');
    });
  });

  // ❌ Отключено: scroll-top, isotope, mobile-nav, contact form
  // потому что таких элементов на Tennis Site нет
})();
