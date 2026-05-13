// navbar
document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.querySelector(".main-navbar__toggle");
    const mobileNavbar = document.querySelector("#mobileNavbar");
    const closeButton = document.querySelector(".mobile-navbar__close");
    const mobileLinks = document.querySelectorAll(".mobile-navbar a");

    if (!toggleButton || !mobileNavbar || !closeButton) {
        return;
    }

    function openMobileMenu() {
        mobileNavbar.classList.add("is-open");
        mobileNavbar.setAttribute("aria-hidden", "false");
        toggleButton.setAttribute("aria-expanded", "true");
        document.body.classList.add("mobile-menu-open");
    }

    function closeMobileMenu() {
        mobileNavbar.classList.remove("is-open");
        mobileNavbar.setAttribute("aria-hidden", "true");
        toggleButton.setAttribute("aria-expanded", "false");
        document.body.classList.remove("mobile-menu-open");
    }

    toggleButton.addEventListener("click", function () {
        openMobileMenu();
    });

    closeButton.addEventListener("click", function () {
        closeMobileMenu();
    });

    mobileLinks.forEach(function (link) {
        link.addEventListener("click", function () {
            closeMobileMenu();
        });
    });

    mobileNavbar.addEventListener("click", function (event) {
        if (event.target === mobileNavbar) {
            closeMobileMenu();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && mobileNavbar.classList.contains("is-open")) {
            closeMobileMenu();
        }
    });
});
// --------------------------------------------

// video banner
document.addEventListener("DOMContentLoaded", function () {
  const carousel = document.querySelector("#heroVideoCarousel");

  if (!carousel) {
    return;
  }

  /*
    ================================
    ANIMATION CONTROL PANEL
    ================================

    blurDuration:
    - Time before the text animation starts.
    - Should match the video blur animation duration in Sass.

    wordStagger:
    - Controls first slide word animation speed.
    - Lower value = faster word reveal.
    - Higher value = slower word reveal.

    letterStagger:
    - Controls second slide letter animation speed.
    - Lower value = faster letter reveal.
    - Higher value = slower letter reveal.

    actionDelay:
    - Controls when buttons appear after text starts.
  */
  const animationConfig = {
    blurDuration: 900,
    wordStagger: 80,
    letterStagger: 40,
    actionDelay: 420,
  };

  let animationTimer = null;

  function splitWords(element) {
    if (!element || element.dataset.prepared === "true") {
      return;
    }

    const text = element.textContent.replace(/\s+/g, " ").trim();

    if (!text) {
      return;
    }

    element.dataset.originalText = text;
    element.setAttribute("aria-label", text);

    const words = text.split(" ");

    element.innerHTML = words
      .map(function (word) {
        return `<span class="word-fade-unit" aria-hidden="true">${word}</span>`;
      })
      .join(" ");

    element.dataset.prepared = "true";
  }

  function splitLetters(element) {
    if (!element || element.dataset.prepared === "true") {
      return;
    }

    const text = element.textContent.replace(/\s+/g, " ").trim();

    if (!text) {
      return;
    }

    element.dataset.originalText = text;
    element.setAttribute("aria-label", text);

    const letters = Array.from(text);

    element.innerHTML = letters
      .map(function (letter) {
        if (letter === " ") {
          return `<span class="letter-reveal-unit" aria-hidden="true">&nbsp;</span>`;
        }

        return `<span class="letter-reveal-unit" aria-hidden="true">${letter}</span>`;
      })
      .join("");

    element.dataset.prepared = "true";
  }

  function prepareActionFade(element) {
    if (!element || element.dataset.prepared === "true") {
      return;
    }

    element.classList.add("action-fade-unit");
    element.dataset.prepared = "true";
  }

  function prepareAnimations() {
    const wordElements = carousel.querySelectorAll(".js-word-fade");
    const letterElements = carousel.querySelectorAll(".js-letter-reveal");
    const actionElements = carousel.querySelectorAll(".js-action-fade");

    wordElements.forEach(splitWords);
    letterElements.forEach(splitLetters);
    actionElements.forEach(prepareActionFade);
  }

  function restartVideoBlur(slide) {
    if (!slide) {
      return;
    }

    const video = slide.querySelector(".hero-video-carousel__media video");

    if (!video) {
      return;
    }

    video.style.animation = "none";
    video.offsetHeight;
    video.style.animation = "";
  }

  function restartVideo(slide) {
    if (!slide) {
      return;
    }

    const video = slide.querySelector(".hero-video-carousel__media video");

    if (!video) {
      return;
    }

    try {
      video.pause();
      video.currentTime = 0;
      video.play().catch(function () {});
    } catch (error) {
      video.play().catch(function () {});
    }
  }

  function resetSlide(slide) {
    if (!slide) {
      return;
    }

    const animatedUnits = slide.querySelectorAll(
      ".word-fade-unit, .letter-reveal-unit, .action-fade-unit"
    );

    animatedUnits.forEach(function (unit) {
      unit.classList.remove("is-visible");
      unit.style.transitionDelay = "0ms";
    });

    restartVideoBlur(slide);
  }

  function revealUnits(slide) {
    const wordUnits = slide.querySelectorAll(".word-fade-unit");
    const letterUnits = slide.querySelectorAll(".letter-reveal-unit");
    const actionUnits = slide.querySelectorAll(".action-fade-unit");

    wordUnits.forEach(function (unit, index) {
      unit.style.transitionDelay = `${index * animationConfig.wordStagger}ms`;
      unit.classList.add("is-visible");
    });

    letterUnits.forEach(function (unit, index) {
      unit.style.transitionDelay = `${index * animationConfig.letterStagger}ms`;
      unit.classList.add("is-visible");
    });

    actionUnits.forEach(function (unit, index) {
      unit.style.transitionDelay = `${animationConfig.actionDelay + index * 120}ms`;
      unit.classList.add("is-visible");
    });
  }

  function animateActiveSlide() {
    const activeSlide = carousel.querySelector(".carousel-item.active");

    if (!activeSlide) {
      return;
    }

    if (animationTimer) {
      clearTimeout(animationTimer);
    }

    resetSlide(activeSlide);
    restartVideo(activeSlide);

    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        animationTimer = setTimeout(function () {
          revealUnits(activeSlide);
        }, animationConfig.blurDuration);
      });
    });
  }

  prepareAnimations();

  setTimeout(function () {
    animateActiveSlide();
  }, 120);

  carousel.addEventListener("slide.bs.carousel", function (event) {
    if (animationTimer) {
      clearTimeout(animationTimer);
    }

    const currentSlide = carousel.querySelector(".carousel-item.active");
    const nextSlide = event.relatedTarget;

    resetSlide(currentSlide);
    resetSlide(nextSlide);

    if (nextSlide) {
      const nextVideo = nextSlide.querySelector(".hero-video-carousel__media video");

      if (nextVideo) {
        try {
          nextVideo.pause();
          nextVideo.currentTime = 0;
        } catch (error) {}
      }
    }
  });

  carousel.addEventListener("slid.bs.carousel", function () {
    animateActiveSlide();
  });
});
// -------------------



// card slider
document.addEventListener("DOMContentLoaded", function () {
  const carTypeSection = document.querySelector("#carTypeSection");

  if (!carTypeSection) {
    return;
  }

  if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  /*
    CAR TYPE SECTION GSAP CONTROL

    categories:
    - fade in from left to center

    slider/cards:
    - fade in from right to center

    Change duration/stagger values below to control speed.
  */

  const categoryTabs = carTypeSection.querySelector(".js-car-tabs");
  const sliderShell = carTypeSection.querySelector(".js-car-slider");
  const cards = carTypeSection.querySelectorAll(".car-type-card");

  gsap.set(categoryTabs, {
    opacity: 0,
    x: -70,
  });

  gsap.set(sliderShell, {
    opacity: 0,
    x: 70,
  });

  gsap.set(cards, {
    opacity: 0,
    y: 26,
  });

  const carTypeTimeline = gsap.timeline({
    scrollTrigger: {
      trigger: carTypeSection,
      start: "top 72%",
      once: true,
    },
  });

  carTypeTimeline
    .to(categoryTabs, {
      opacity: 1,
      x: 0,
      duration: 0.75,
      ease: "power3.out",
    })
    .to(
      sliderShell,
      {
        opacity: 1,
        x: 0,
        duration: 0.75,
        ease: "power3.out",
      },
      "-=0.42"
    )
    .to(
      cards,
      {
        opacity: 1,
        y: 0,
        duration: 0.55,
        stagger: 0.08,
        ease: "power2.out",
      },
      "-=0.35"
    );
});
// -------------------------------



// brands
document.addEventListener("DOMContentLoaded", function () {
  const brandSection = document.querySelector("#brandShowcaseSection");

  if (!brandSection) {
    return;
  }

  if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  const brandHeader = brandSection.querySelector(".brand-showcase-section__header");
  const brandShowcase = brandSection.querySelector(".js-brand-showcase");
  const brandTrack = brandSection.querySelector(".js-brand-track");
  const brandItems = brandSection.querySelectorAll(".js-brand-item");

  if (!brandTrack || brandItems.length === 0) {
    return;
  }

  /*
    BRAND SECTION ANIMATION CONTROL

    scroll reveal:
    - header fades up
    - showcase fades from bottom
    - logo cards stagger in

    marquee:
    - duration controls logo movement speed
    - lower duration = faster movement
    - higher duration = slower movement
  */

  gsap.set(brandHeader, {
    opacity: 0,
    y: 28,
  });

  gsap.set(brandShowcase, {
    opacity: 0,
    y: 34,
  });

  gsap.set(brandItems, {
    opacity: 0,
    y: 18,
    filter: "blur(8px)",
  });

  const revealTimeline = gsap.timeline({
    scrollTrigger: {
      trigger: brandSection,
      start: "top 76%",
      once: true,
    },
  });

  revealTimeline
    .to(brandHeader, {
      opacity: 1,
      y: 0,
      duration: 0.7,
      ease: "power3.out",
    })
    .to(
      brandShowcase,
      {
        opacity: 1,
        y: 0,
        duration: 0.75,
        ease: "power3.out",
      },
      "-=0.35"
    )
    .to(
      brandItems,
      {
        opacity: 1,
        y: 0,
        filter: "blur(0px)",
        duration: 0.55,
        stagger: 0.04,
        ease: "power2.out",
      },
      "-=0.35"
    );

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!prefersReducedMotion) {
    const marqueeAnimation = gsap.to(brandTrack, {
      xPercent: -50,
      duration: 24,
      ease: "none",
      repeat: -1,
    });

    brandShowcase.addEventListener("mouseenter", function () {
      marqueeAnimation.pause();
    });

    brandShowcase.addEventListener("mouseleave", function () {
      marqueeAnimation.resume();
    });
  }
});



// review
document.addEventListener("DOMContentLoaded", function () {
  const reviewSection = document.querySelector("#reviewShowcaseSection");

  if (!reviewSection) {
    return;
  }

  if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  const reviewHeader = reviewSection.querySelector(".review-showcase-section__header");
  const reviewBox = reviewSection.querySelector(".js-review-box");
  const reviewTrack = reviewSection.querySelector(".js-review-track");
  const reviewItems = reviewSection.querySelectorAll(".js-review-item");

  if (!reviewBox || !reviewTrack || reviewItems.length === 0) {
    return;
  }

  /*
    REVIEW SECTION CONTROL PANEL

    reveal animation:
    - Header fades up
    - Big box fades up
    - Cards stagger in

    vertical marquee:
    - duration controls bottom-to-top speed
    - higher duration = slower movement
    - lower duration = faster movement
  */

  gsap.set(reviewHeader, {
    opacity: 0,
    y: 28,
  });

  gsap.set(reviewBox, {
    opacity: 0,
    y: 34,
  });

  gsap.set(reviewItems, {
    opacity: 0,
    y: 18,
    filter: "blur(8px)",
  });

  const revealTimeline = gsap.timeline({
    scrollTrigger: {
      trigger: reviewSection,
      start: "top 76%",
      once: true,
    },
  });

  revealTimeline
    .to(reviewHeader, {
      opacity: 1,
      y: 0,
      duration: 0.7,
      ease: "power3.out",
    })
    .to(
      reviewBox,
      {
        opacity: 1,
        y: 0,
        duration: 0.75,
        ease: "power3.out",
      },
      "-=0.35"
    )
    .to(
      reviewItems,
      {
        opacity: 1,
        y: 0,
        filter: "blur(0px)",
        duration: 0.55,
        stagger: 0.05,
        ease: "power2.out",
      },
      "-=0.35"
    );

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!prefersReducedMotion) {
    window.addEventListener("load", function () {
      const loopDistance = reviewTrack.scrollHeight / 2;

      const reviewMarquee = gsap.to(reviewTrack, {
        y: -loopDistance,
        duration: 34,
        ease: "none",
        repeat: -1,
      });

      reviewBox.addEventListener("mouseenter", function () {
        reviewMarquee.pause();
      });

      reviewBox.addEventListener("mouseleave", function () {
        reviewMarquee.resume();
      });
    });
  }
});


// faq
document.addEventListener("DOMContentLoaded", function () {
  const faqSection = document.querySelector("#faqSection");

  if (!faqSection) {
    return;
  }

  if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  const faqHeader = faqSection.querySelector(".faq-section__header");
  const faqWrapper = faqSection.querySelector(".js-faq-wrapper");
  const faqItems = faqSection.querySelectorAll(".js-faq-item");

  gsap.set(faqHeader, {
    opacity: 0,
    y: 28,
  });

  gsap.set(faqWrapper, {
    opacity: 0,
    y: 32,
  });

  gsap.set(faqItems, {
    opacity: 0,
    y: 24,
    filter: "blur(8px)",
  });

  const faqTimeline = gsap.timeline({
    scrollTrigger: {
      trigger: faqSection,
      start: "top 76%",
      once: true,
    },
  });

  faqTimeline
    .to(faqHeader, {
      opacity: 1,
      y: 0,
      duration: 0.7,
      ease: "power3.out",
    })
    .to(
      faqWrapper,
      {
        opacity: 1,
        y: 0,
        duration: 0.75,
        ease: "power3.out",
      },
      "-=0.35"
    )
    .to(
      faqItems,
      {
        opacity: 1,
        y: 0,
        filter: "blur(0px)",
        duration: 0.55,
        stagger: 0.1,
        ease: "power2.out",
      },
      "-=0.42"
    );
});


// footer
document.addEventListener("DOMContentLoaded", function () {
  const footer = document.querySelector("#siteFooter");

  if (!footer) {
    return;
  }

  if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  const footerBlocks = footer.querySelectorAll(".js-footer-block");
  const footerBottom = footer.querySelector(".js-footer-bottom");

  gsap.set(footerBlocks, {
    opacity: 0,
    y: 28,
    filter: "blur(8px)",
  });

  gsap.set(footerBottom, {
    opacity: 0,
    y: 18,
  });

  const footerTimeline = gsap.timeline({
    scrollTrigger: {
      trigger: footer,
      start: "top 82%",
      once: true,
    },
  });

  footerTimeline
    .to(footerBlocks, {
      opacity: 1,
      y: 0,
      filter: "blur(0px)",
      duration: 0.65,
      stagger: 0.1,
      ease: "power3.out",
    })
    .to(
      footerBottom,
      {
        opacity: 1,
        y: 0,
        duration: 0.55,
        ease: "power2.out",
      },
      "-=0.25"
    );
});


// login 
document.addEventListener("DOMContentLoaded", function () {
  const loginPage = document.querySelector("#loginPage");

  if (!loginPage) {
    return;
  }

  const passwordInput = loginPage.querySelector("#id_password");
  const passwordToggle = loginPage.querySelector(".auth-password-toggle");
  const loginForm = loginPage.querySelector("#loginForm");
  const submitButton = loginPage.querySelector("#loginSubmitBtn");

  if (passwordInput && passwordToggle) {
    passwordToggle.addEventListener("click", function () {
      const isPassword = passwordInput.type === "password";

      passwordInput.type = isPassword ? "text" : "password";
      passwordToggle.textContent = isPassword ? "Hide" : "Show";
      passwordToggle.setAttribute(
        "aria-label",
        isPassword ? "Hide password" : "Show password"
      );
    });
  }

  if (loginForm && submitButton) {
    loginForm.addEventListener("submit", function () {
      submitButton.classList.add("is-loading");
      submitButton.setAttribute("disabled", "disabled");
    });
  }

  if (typeof gsap !== "undefined") {
    gsap.from(".auth-card", {
      opacity: 0,
      y: 28,
      filter: "blur(8px)",
      duration: 0.75,
      ease: "power3.out",
    });

    gsap.from(".auth-card__image-overlay", {
      opacity: 0,
      y: 24,
      filter: "blur(8px)",
      duration: 0.75,
      delay: 0.25,
      ease: "power3.out",
    });
  }
});


//signup
document.addEventListener("DOMContentLoaded", function () {
  const signupPage = document.querySelector("#signupPage");

  if (!signupPage) {
    return;
  }

  const signupForm = signupPage.querySelector("#signupForm");
  const registerButton = signupPage.querySelector("#registerBtn");
  const passwordToggles = signupPage.querySelectorAll(".auth-password-toggle");

  passwordToggles.forEach(function (toggleButton) {
    const passwordField = toggleButton.closest(".auth-password-field");

    if (!passwordField) {
      return;
    }

    const passwordInput = passwordField.querySelector("input");

    if (!passwordInput) {
      return;
    }

    toggleButton.addEventListener("click", function () {
      const isPassword = passwordInput.type === "password";

      passwordInput.type = isPassword ? "text" : "password";
      toggleButton.textContent = isPassword ? "Hide" : "Show";
      toggleButton.setAttribute(
        "aria-label",
        isPassword ? "Hide password" : "Show password"
      );
    });
  });

  if (signupForm && registerButton) {
    signupForm.addEventListener("submit", function () {
      registerButton.classList.add("is-loading");
      registerButton.setAttribute("disabled", "disabled");
    });
  }

  if (typeof gsap !== "undefined") {
    gsap.from("#signupPage .auth-card", {
      opacity: 0,
      y: 28,
      filter: "blur(8px)",
      duration: 0.75,
      ease: "power3.out",
    });

    gsap.from("#signupPage .auth-card__image-overlay", {
      opacity: 0,
      y: 24,
      filter: "blur(8px)",
      duration: 0.75,
      delay: 0.25,
      ease: "power3.out",
    });
  }
});

// --------------------


//password change
document.addEventListener("DOMContentLoaded", function () {
  const changePasswordPage = document.querySelector("#changePasswordPage");

  if (!changePasswordPage) {
    return;
  }

  const form = changePasswordPage.querySelector("#changePasswordForm");
  const submitButton = changePasswordPage.querySelector("#changePasswordSubmitBtn");
  const toggles = changePasswordPage.querySelectorAll(".profile-password-toggle");

  toggles.forEach(function (toggleButton) {
    const passwordField = toggleButton.closest(".profile-password-field");

    if (!passwordField) {
      return;
    }

    const passwordInput = passwordField.querySelector("input");

    if (!passwordInput) {
      return;
    }

    toggleButton.addEventListener("click", function () {
      const isPassword = passwordInput.type === "password";

      passwordInput.type = isPassword ? "text" : "password";
      toggleButton.textContent = isPassword ? "Hide" : "Show";
      toggleButton.setAttribute(
        "aria-label",
        isPassword ? "Hide password" : "Show password"
      );
    });
  });

  if (form && submitButton) {
    form.addEventListener("submit", function () {
      submitButton.classList.add("is-loading");
      submitButton.setAttribute("disabled", "disabled");
    });
  }

  if (typeof gsap !== "undefined") {
    gsap.from("#changePasswordPage .profile-password-card", {
      opacity: 0,
      y: 24,
      filter: "blur(8px)",
      duration: 0.65,
      ease: "power3.out",
    });
  }
});

// -------------------------

document.addEventListener("DOMContentLoaded", function () {
  const resetConfirmPage = document.querySelector("#resetConfirmPage");

  if (!resetConfirmPage) {
    return;
  }

  const resetForm = resetConfirmPage.querySelector("#resetConfirmForm");
  const submitButton = resetConfirmPage.querySelector("#resetConfirmSubmitBtn");
  const passwordToggles = resetConfirmPage.querySelectorAll(".auth-password-toggle");

  passwordToggles.forEach(function (toggleButton) {
    const passwordField = toggleButton.closest(".auth-password-field");

    if (!passwordField) {
      return;
    }

    const passwordInput = passwordField.querySelector("input");

    if (!passwordInput) {
      return;
    }

    toggleButton.addEventListener("click", function () {
      const isPassword = passwordInput.type === "password";

      passwordInput.type = isPassword ? "text" : "password";
      toggleButton.textContent = isPassword ? "Hide" : "Show";
      toggleButton.setAttribute(
        "aria-label",
        isPassword ? "Hide password" : "Show password"
      );
    });
  });

  if (resetForm && submitButton) {
    resetForm.addEventListener("submit", function () {
      submitButton.classList.add("is-loading");
      submitButton.setAttribute("disabled", "disabled");
    });
  }

  if (typeof gsap !== "undefined") {
    gsap.from("#resetConfirmPage .auth-card", {
      opacity: 0,
      y: 28,
      filter: "blur(8px)",
      duration: 0.75,
      ease: "power3.out",
    });

    gsap.from("#resetConfirmPage .auth-card__image-overlay", {
      opacity: 0,
      y: 24,
      filter: "blur(8px)",
      duration: 0.75,
      delay: 0.25,
      ease: "power3.out",
    });
  }
});

// --------------------

//c_password_reset
document.addEventListener("DOMContentLoaded", function () {
  const resetRequestPage = document.querySelector("#resetRequestPage");

  if (!resetRequestPage) {
    return;
  }

  const resetForm = resetRequestPage.querySelector("#resetRequestForm");
  const submitButton = resetRequestPage.querySelector("#resetRequestSubmitBtn");

  if (resetForm && submitButton) {
    resetForm.addEventListener("submit", function () {
      submitButton.classList.add("is-loading");
      submitButton.setAttribute("disabled", "disabled");
    });
  }

  if (typeof gsap !== "undefined") {
    gsap.from("#resetRequestPage .auth-card", {
      opacity: 0,
      y: 28,
      filter: "blur(8px)",
      duration: 0.75,
      ease: "power3.out",
    });

    gsap.from("#resetRequestPage .auth-card__image-overlay", {
      opacity: 0,
      y: 24,
      filter: "blur(8px)",
      duration: 0.75,
      delay: 0.25,
      ease: "power3.out",
    });
  }
});

// --------------------

// profile
document.addEventListener("DOMContentLoaded", function () {
  const profilePage = document.querySelector("#profilePage");

  if (!profilePage) {
    return;
  }

  const sidebar = profilePage.querySelector(".js-profile-sidebar");
  const mainContent = profilePage.querySelector(".js-profile-main");
  const profileLinks = profilePage.querySelectorAll("[data-profile-link]");
  const profileForm = profilePage.querySelector("#profileInfoForm");
  const profileUpdateBtn = profilePage.querySelector("#profileUpdateBtn");

  if (typeof gsap !== "undefined") {
    gsap.from(sidebar, {
      opacity: 0,
      x: -28,
      filter: "blur(8px)",
      duration: 0.65,
      ease: "power3.out",
    });

    gsap.from(mainContent, {
      opacity: 0,
      x: 28,
      filter: "blur(8px)",
      duration: 0.65,
      delay: 0.12,
      ease: "power3.out",
    });
  }

  profileLinks.forEach(function (link) {
    link.addEventListener("click", function (event) {
      const targetUrl = link.href;
      const currentUrl = window.location.href;

      if (!targetUrl || targetUrl === currentUrl) {
        return;
      }

      if (typeof gsap === "undefined") {
        return;
      }

      event.preventDefault();

      profileLinks.forEach(function (item) {
        item.classList.remove("is-active");
      });

      link.classList.add("is-active");

      gsap.to(mainContent, {
        opacity: 0,
        x: 24,
        filter: "blur(8px)",
        duration: 0.24,
        ease: "power2.in",
        onComplete: function () {
          window.location.href = targetUrl;
        },
      });
    });
  });

  if (profileForm && profileUpdateBtn) {
    profileForm.addEventListener("submit", function () {
      profileUpdateBtn.classList.add("is-loading");
      profileUpdateBtn.setAttribute("disabled", "disabled");
    });
  }
});

// ----------------------------

//seller dashboard
document.addEventListener("DOMContentLoaded", function () {
  const sellerPage = document.querySelector("#sellerDashboardPage");

  if (!sellerPage) {
    return;
  }

  const sidebar = sellerPage.querySelector(".js-seller-sidebar");
  const main = sellerPage.querySelector(".js-seller-main");
  const header = sellerPage.querySelector(".js-seller-header");
  const sellerContent = sellerPage.querySelector("#sellerContent");
  const navItems = sellerPage.querySelectorAll("[data-seller-nav]");
  const messages = sellerPage.querySelectorAll(".js-seller-message");
  const closeButtons = sellerPage.querySelectorAll(".seller-message__close");

  function animateSellerContentIn() {
    if (typeof gsap === "undefined" || !sellerContent) {
      return;
    }

    gsap.fromTo(
      sellerContent,
      {
        opacity: 0,
        y: 18,
        filter: "blur(8px)",
      },
      {
        opacity: 1,
        y: 0,
        filter: "blur(0px)",
        duration: 0.45,
        ease: "power3.out",
      }
    );
  }

  function animateSellerContentOut(done) {
    if (typeof gsap === "undefined" || !sellerContent) {
      done();
      return;
    }

    gsap.to(sellerContent, {
      opacity: 0,
      y: 16,
      filter: "blur(8px)",
      duration: 0.22,
      ease: "power2.in",
      onComplete: done,
    });
  }

  function setActiveNav(activeItem) {
    navItems.forEach(function (item) {
      item.classList.remove("is-active");
    });

    activeItem.classList.add("is-active");
  }

  function renderStaticPanel(type) {
    if (!sellerContent) {
      return;
    }

    const panelMap = {
      analytics: {
        title: "Analytics Overview",
        text: "Track listing performance, buyer interest, and dashboard activity. Connect real metrics later when analytics data is ready.",
        cards: [
          ["Views", "0"],
          ["Active Listings", "0"],
          ["Buyer Interest", "0"],
        ],
      },
      predictions: {
        title: "Price Predictions",
        text: "Use AI-assisted price analysis to understand whether a vehicle price appears high, low, or fair.",
        cards: [
          ["Prediction Status", "Ready"],
          ["Market Check", "AI"],
          ["Price Signal", "Fair"],
        ],
      },
    };

    const panel = panelMap[type];

    if (!panel) {
      return;
    }

    sellerContent.innerHTML = `
      <div class="seller-static-panel">
        <h2>${panel.title}</h2>
        <p>${panel.text}</p>

        <div class="seller-static-panel__grid">
          ${panel.cards
            .map(function (card) {
              return `
                <div class="seller-static-card">
                  <span>${card[0]}</span>
                  <strong>${card[1]}</strong>
                </div>
              `;
            })
            .join("")}
        </div>
      </div>
    `;

    animateSellerContentIn();
  }

  if (typeof gsap !== "undefined") {
    gsap.from(sidebar, {
      opacity: 0,
      x: -28,
      filter: "blur(8px)",
      duration: 0.65,
      ease: "power3.out",
    });

    gsap.from(main, {
      opacity: 0,
      x: 28,
      filter: "blur(8px)",
      duration: 0.65,
      delay: 0.12,
      ease: "power3.out",
    });

    gsap.from(header, {
      opacity: 0,
      y: 18,
      filter: "blur(8px)",
      duration: 0.55,
      delay: 0.24,
      ease: "power3.out",
    });

    gsap.from(messages, {
      opacity: 0,
      y: -18,
      filter: "blur(8px)",
      duration: 0.5,
      stagger: 0.08,
      ease: "power3.out",
      delay: 0.2,
    });
  }

  closeButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const message = button.closest(".js-seller-message");

      if (!message) {
        return;
      }

      if (typeof gsap !== "undefined") {
        gsap.to(message, {
          opacity: 0,
          x: 24,
          filter: "blur(6px)",
          height: 0,
          marginBottom: 0,
          paddingTop: 0,
          paddingBottom: 0,
          duration: 0.32,
          ease: "power2.inOut",
          onComplete: function () {
            message.remove();
          },
        });
      } else {
        message.remove();
      }
    });
  });

  navItems.forEach(function (item) {
    item.addEventListener("click", function (event) {
      setActiveNav(item);

      const staticPanelType = item.dataset.sellerStaticPanel;

      if (staticPanelType) {
        event.preventDefault();

        animateSellerContentOut(function () {
          renderStaticPanel(staticPanelType);
        });
      }
    });
  });

  document.body.addEventListener("htmx:beforeRequest", function (event) {
    if (!sellerPage.contains(event.target)) {
      return;
    }

    animateSellerContentOut(function () {});
  });

  document.body.addEventListener("htmx:afterSwap", function (event) {
    if (event.detail.target && event.detail.target.id === "sellerContent") {
      animateSellerContentIn();
    }
  });
});

// ----------------

// add car
document.addEventListener("DOMContentLoaded", function () {
  function animateSellerAddCarPanel() {
    const panel = document.querySelector("#sellerAddCarPanel");

    if (!panel || typeof gsap === "undefined") {
      return;
    }

    const header = panel.querySelector(".seller-form-panel__header");
    const groups = panel.querySelectorAll(".seller-car-form__group");
    const actions = panel.querySelector(".seller-car-form__actions");
    const messages = panel.querySelectorAll(".js-seller-form-message");

    gsap.from(header, {
      opacity: 0,
      y: 18,
      filter: "blur(8px)",
      duration: 0.48,
      ease: "power3.out",
    });

    gsap.from(groups, {
      opacity: 0,
      y: 18,
      filter: "blur(8px)",
      duration: 0.42,
      stagger: 0.045,
      ease: "power2.out",
      delay: 0.08,
    });

    gsap.from(actions, {
      opacity: 0,
      y: 14,
      filter: "blur(8px)",
      duration: 0.42,
      ease: "power2.out",
      delay: 0.2,
    });

    gsap.from(messages, {
      opacity: 0,
      y: -16,
      filter: "blur(8px)",
      duration: 0.42,
      stagger: 0.06,
      ease: "power3.out",
    });
  }

  function bindSellerFormMessageClose() {
    document.querySelectorAll(".seller-form-message__close").forEach(function (button) {
      if (button.dataset.bound === "true") {
        return;
      }

      button.dataset.bound = "true";

      button.addEventListener("click", function () {
        const message = button.closest(".js-seller-form-message");

        if (!message) {
          return;
        }

        if (typeof gsap !== "undefined") {
          gsap.to(message, {
            opacity: 0,
            x: 24,
            filter: "blur(6px)",
            height: 0,
            marginBottom: 0,
            paddingTop: 0,
            paddingBottom: 0,
            duration: 0.3,
            ease: "power2.inOut",
            onComplete: function () {
              message.remove();
            },
          });
        } else {
          message.remove();
        }
      });
    });
  }

  document.body.addEventListener("htmx:afterSwap", function (event) {
    if (event.detail.target && event.detail.target.id === "sellerContent") {
      animateSellerAddCarPanel();
      bindSellerFormMessageClose();
    }
  });

  document.body.addEventListener("htmx:beforeRequest", function (event) {
    const form = event.target.closest ? event.target.closest("#sellerAddCarForm") : null;

    if (!form) {
      return;
    }

    const submitButton = form.querySelector("#sellerAddCarSubmitBtn");

    if (submitButton) {
      submitButton.classList.add("is-loading");
      submitButton.setAttribute("disabled", "disabled");
    }
  });

  animateSellerAddCarPanel();
  bindSellerFormMessageClose();
});
// -------------------

// add video
document.addEventListener("DOMContentLoaded", function () {
  function animateSellerAddVideoPanel() {
    const panel = document.querySelector("#sellerAddVideoPanel");

    if (!panel || typeof gsap === "undefined") {
      return;
    }

    const header = panel.querySelector(".seller-video-panel__header");
    const groups = panel.querySelectorAll(".seller-video-form__group");
    const actions = panel.querySelector(".seller-video-form__actions");
    const messages = panel.querySelectorAll(".js-seller-video-message");

    gsap.from(header, {
      opacity: 0,
      y: 18,
      filter: "blur(8px)",
      duration: 0.48,
      ease: "power3.out",
    });

    gsap.from(groups, {
      opacity: 0,
      y: 18,
      filter: "blur(8px)",
      duration: 0.42,
      stagger: 0.05,
      ease: "power2.out",
      delay: 0.08,
    });

    gsap.from(actions, {
      opacity: 0,
      y: 14,
      filter: "blur(8px)",
      duration: 0.42,
      ease: "power2.out",
      delay: 0.2,
    });

    gsap.from(messages, {
      opacity: 0,
      y: -16,
      filter: "blur(8px)",
      duration: 0.42,
      stagger: 0.06,
      ease: "power3.out",
    });
  }

  function bindSellerVideoMessageClose() {
    document.querySelectorAll(".seller-video-message__close").forEach(function (button) {
      if (button.dataset.bound === "true") {
        return;
      }

      button.dataset.bound = "true";

      button.addEventListener("click", function () {
        const message = button.closest(".js-seller-video-message");

        if (!message) {
          return;
        }

        if (typeof gsap !== "undefined") {
          gsap.to(message, {
            opacity: 0,
            x: 24,
            filter: "blur(6px)",
            height: 0,
            marginBottom: 0,
            paddingTop: 0,
            paddingBottom: 0,
            duration: 0.3,
            ease: "power2.inOut",
            onComplete: function () {
              message.remove();
            },
          });
        } else {
          message.remove();
        }
      });
    });
  }

  document.body.addEventListener("htmx:afterSwap", function (event) {
    if (event.detail.target && event.detail.target.id === "sellerContent") {
      animateSellerAddVideoPanel();
      bindSellerVideoMessageClose();
    }
  });

  document.body.addEventListener("htmx:beforeRequest", function (event) {
    const form = event.target.closest ? event.target.closest("#sellerAddVideoForm") : null;

    if (!form) {
      return;
    }

    const submitButton = form.querySelector("#sellerAddVideoSubmitBtn");

    if (submitButton) {
      submitButton.classList.add("is-loading");
      submitButton.setAttribute("disabled", "disabled");
    }
  });

  animateSellerAddVideoPanel();
  bindSellerVideoMessageClose();
});

// ------------------------------

// car added 
document.addEventListener("DOMContentLoaded", function () {
  function bindSellerPopupToasts() {
    const toasts = document.querySelectorAll(".js-seller-popup-toast");

    toasts.forEach(function (toast) {
      if (toast.dataset.bound === "true") {
        return;
      }

      toast.dataset.bound = "true";

      const closeButton = toast.querySelector(".seller-popup-toast__close");

      function closeToast() {
        if (typeof gsap !== "undefined") {
          gsap.to(toast, {
            opacity: 0,
            x: 40,
            filter: "blur(8px)",
            duration: 0.32,
            ease: "power2.inOut",
            onComplete: function () {
              toast.remove();
            },
          });
        } else {
          toast.remove();
        }
      }

      if (typeof gsap !== "undefined") {
        gsap.fromTo(
          toast,
          {
            opacity: 0,
            x: 48,
            y: -10,
            filter: "blur(8px)",
          },
          {
            opacity: 1,
            x: 0,
            y: 0,
            filter: "blur(0px)",
            duration: 0.45,
            ease: "power3.out",
          }
        );
      }

      if (closeButton) {
        closeButton.addEventListener("click", closeToast);
      }

      setTimeout(closeToast, 5000);
    });
  }

  bindSellerPopupToasts();

  document.body.addEventListener("htmx:afterSwap", function () {
    bindSellerPopupToasts();
  });
});

// ------------------------

// edit car
document.addEventListener("DOMContentLoaded", function () {
  function animateSellerEditCarPanel() {
    const panel = document.querySelector("#sellerEditCarPanel");

    if (!panel || typeof gsap === "undefined") {
      return;
    }

    const header = panel.querySelector(".seller-edit-panel__header");
    const currentImage = panel.querySelector(".seller-edit-current-image");
    const groups = panel.querySelectorAll(".seller-edit-form__group");
    const actions = panel.querySelector(".seller-edit-form__actions");
    const messages = panel.querySelectorAll(".js-seller-edit-message");

    gsap.from(header, {
      opacity: 0,
      y: 18,
      filter: "blur(8px)",
      duration: 0.48,
      ease: "power3.out",
    });

    if (currentImage) {
      gsap.from(currentImage, {
        opacity: 0,
        y: 16,
        filter: "blur(8px)",
        duration: 0.42,
        ease: "power2.out",
        delay: 0.06,
      });
    }

    gsap.from(groups, {
      opacity: 0,
      y: 18,
      filter: "blur(8px)",
      duration: 0.42,
      stagger: 0.035,
      ease: "power2.out",
      delay: 0.1,
    });

    gsap.from(actions, {
      opacity: 0,
      y: 14,
      filter: "blur(8px)",
      duration: 0.42,
      ease: "power2.out",
      delay: 0.2,
    });

    gsap.from(messages, {
      opacity: 0,
      y: -16,
      filter: "blur(8px)",
      duration: 0.42,
      stagger: 0.06,
      ease: "power3.out",
    });
  }

  function bindSellerEditMessageClose() {
    document.querySelectorAll(".seller-edit-message__close").forEach(function (button) {
      if (button.dataset.bound === "true") {
        return;
      }

      button.dataset.bound = "true";

      button.addEventListener("click", function () {
        const message = button.closest(".js-seller-edit-message");

        if (!message) {
          return;
        }

        if (typeof gsap !== "undefined") {
          gsap.to(message, {
            opacity: 0,
            x: 24,
            filter: "blur(6px)",
            height: 0,
            marginBottom: 0,
            paddingTop: 0,
            paddingBottom: 0,
            duration: 0.3,
            ease: "power2.inOut",
            onComplete: function () {
              message.remove();
            },
          });
        } else {
          message.remove();
        }
      });
    });
  }

  document.body.addEventListener("htmx:afterSwap", function (event) {
    if (event.detail.target && event.detail.target.id === "sellerContent") {
      animateSellerEditCarPanel();
      bindSellerEditMessageClose();
    }
  });

  document.body.addEventListener("htmx:beforeRequest", function (event) {
    const form = event.target.closest ? event.target.closest("#sellerEditCarForm") : null;

    if (!form) {
      return;
    }

    const submitButton = form.querySelector("#sellerEditCarSubmitBtn");

    if (submitButton) {
      submitButton.classList.add("is-loading");
      submitButton.setAttribute("disabled", "disabled");
    }
  });

  animateSellerEditCarPanel();
  bindSellerEditMessageClose();
});

// -------------------

//seller car list
document.addEventListener("DOMContentLoaded", function () {
  function animateSellerCarsPanel() {
    const panel = document.querySelector("#sellerCarsPanel");

    if (!panel || typeof gsap === "undefined") {
      return;
    }

    const header = panel.querySelector(".seller-cars-panel__header");
    const cards = panel.querySelectorAll(".js-seller-car-card");
    const empty = panel.querySelector(".seller-cars-empty");

    gsap.from(header, {
      opacity: 0,
      y: 18,
      filter: "blur(8px)",
      duration: 0.48,
      ease: "power3.out",
    });

    if (cards.length > 0) {
      gsap.from(cards, {
        opacity: 0,
        y: 22,
        filter: "blur(8px)",
        duration: 0.46,
        stagger: 0.06,
        ease: "power2.out",
        delay: 0.08,
      });
    }

    if (empty) {
      gsap.from(empty, {
        opacity: 0,
        y: 20,
        filter: "blur(8px)",
        duration: 0.5,
        ease: "power3.out",
        delay: 0.08,
      });
    }
  }

  document.body.addEventListener("htmx:afterSwap", function (event) {
    if (event.detail.target && event.detail.target.id === "sellerContent") {
      animateSellerCarsPanel();
    }
  });

  document.body.addEventListener("htmx:beforeRequest", function (event) {
    const deleteButton = event.target.closest
      ? event.target.closest(".seller-car-action--delete")
      : null;

    if (!deleteButton) {
      return;
    }

    const targetSelector = deleteButton.getAttribute("hx-target");
    const targetCard = targetSelector ? document.querySelector(targetSelector) : null;

    if (targetCard && typeof gsap !== "undefined") {
      gsap.to(targetCard, {
        opacity: 0.45,
        scale: 0.98,
        filter: "blur(4px)",
        duration: 0.22,
        ease: "power2.out",
      });
    }
  });

  document.body.addEventListener("htmx:beforeSwap", function (event) {
    if (!event.detail.target || !event.detail.target.classList.contains("seller-car-card")) {
      return;
    }

    if (typeof gsap === "undefined") {
      return;
    }

    event.preventDefault();

    gsap.to(event.detail.target, {
      opacity: 0,
      x: 24,
      filter: "blur(8px)",
      height: 0,
      marginBottom: 0,
      paddingTop: 0,
      paddingBottom: 0,
      duration: 0.32,
      ease: "power2.inOut",
      onComplete: function () {
        event.detail.target.remove();
      },
    });
  });

  animateSellerCarsPanel();
});

// -----------------------

//car list 
document.addEventListener("DOMContentLoaded", function () {
  const dashboard = document.querySelector("#carListDashboard");

  if (!dashboard) {
    return;
  }

  const filterForm = dashboard.querySelector("#filter-form");
  const minRange = dashboard.querySelector("#minPriceRange");
  const maxRange = dashboard.querySelector("#maxPriceRange");
  const fill = dashboard.querySelector("#priceRangeFill");
  const minLabel = dashboard.querySelector("#priceMinLabel");
  const maxLabel = dashboard.querySelector("#priceMaxLabel");
  const quickButtons = dashboard.querySelectorAll(".car-filter-price__quick button");
  const aiInput = dashboard.querySelector("#ai-search-input");
  const sidebarAiInput = dashboard.querySelector("#sidebar-ai-query");
  const clearAiButton = dashboard.querySelector("#clear-ai-search");
  const carContainer = dashboard.querySelector("#car-container");

  function formatPrice(value) {
    const number = Number(value || 0);

    return "$" + number.toLocaleString("en-US");
  }

  function updatePriceSlider(triggerChange) {
    if (!minRange || !maxRange || !fill) {
      return;
    }

    const min = Number(minRange.min);
    const max = Number(maxRange.max);
    let minValue = Number(minRange.value);
    let maxValue = Number(maxRange.value);

    if (minValue > maxValue) {
      const temp = minValue;
      minValue = maxValue;
      maxValue = temp;

      minRange.value = minValue;
      maxRange.value = maxValue;
    }

    const leftPercent = ((minValue - min) / (max - min)) * 100;
    const rightPercent = 100 - ((maxValue - min) / (max - min)) * 100;

    fill.style.left = leftPercent + "%";
    fill.style.right = rightPercent + "%";

    if (minLabel) {
      minLabel.textContent = formatPrice(minValue);
    }

    if (maxLabel) {
      maxLabel.textContent = formatPrice(maxValue);
    }

    if (triggerChange && filterForm) {
      filterForm.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }

  if (minRange && maxRange) {
    updatePriceSlider(false);

    minRange.addEventListener("input", function () {
      updatePriceSlider(false);
    });

    maxRange.addEventListener("input", function () {
      updatePriceSlider(false);
    });

    minRange.addEventListener("change", function () {
      updatePriceSlider(true);
    });

    maxRange.addEventListener("change", function () {
      updatePriceSlider(true);
    });
  }

  quickButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      if (!minRange || !maxRange) {
        return;
      }

      minRange.value = button.dataset.priceMin || minRange.min;
      maxRange.value = button.dataset.priceMax || maxRange.max;

      updatePriceSlider(true);
    });
  });

  if (aiInput && sidebarAiInput) {
    aiInput.addEventListener("input", function () {
      sidebarAiInput.value = aiInput.value;
    });
  }

  if (clearAiButton && aiInput) {
    clearAiButton.addEventListener("click", function () {
      aiInput.value = "";

      if (sidebarAiInput) {
        sidebarAiInput.value = "";
      }

      aiInput.focus();
    });
  }

  if (aiInput) {
    const placeholders = [
      "AI Search: car under 30k",
      "AI Search: blue car",
      "AI Search: red car below 50k",
      "AI Search: Toyota above 2018",
      "AI Search: black car within 40k",
      "AI Search: petrol car under 25k",
      "AI Search: automatic car below 60k",
      "AI Search: white car with low mileage",
      "AI Search: SUV between 20k and 40k",
      "AI Search: available car under 30k"
    ];

    let index = 0;

    setInterval(function () {
      index = (index + 1) % placeholders.length;
      aiInput.setAttribute("placeholder", placeholders[index]);
    }, 2200);
  }

  if (typeof gsap !== "undefined") {
    gsap.from(".car-list-dashboard__header", {
      opacity: 0,
      y: 24,
      filter: "blur(8px)",
      duration: 0.65,
      ease: "power3.out",
    });

    gsap.from(".js-car-filter-panel", {
      opacity: 0,
      x: -28,
      filter: "blur(8px)",
      duration: 0.65,
      delay: 0.12,
      ease: "power3.out",
    });

    gsap.from(".js-car-list-main", {
      opacity: 0,
      x: 28,
      filter: "blur(8px)",
      duration: 0.65,
      delay: 0.18,
      ease: "power3.out",
    });
  }

  document.body.addEventListener("htmx:beforeRequest", function (event) {
    if (!filterForm || !filterForm.contains(event.target)) {
      return;
    }

    if (carContainer && typeof gsap !== "undefined") {
      gsap.to(carContainer, {
        opacity: 0.45,
        y: 10,
        filter: "blur(6px)",
        duration: 0.18,
        ease: "power2.out",
      });
    }
  });

  document.body.addEventListener("htmx:afterSwap", function (event) {
    if (!event.detail.target || event.detail.target.id !== "car-container") {
      return;
    }

    if (typeof gsap !== "undefined") {
      gsap.fromTo(
        event.detail.target,
        {
          opacity: 0,
          y: 18,
          filter: "blur(8px)",
        },
        {
          opacity: 1,
          y: 0,
          filter: "blur(0px)",
          duration: 0.45,
          ease: "power3.out",
        }
      );
    }
  });
});
// ------------------------------

// car details
document.addEventListener("DOMContentLoaded", function () {
  const page = document.querySelector("#carDetailPage");
  const contactModal = document.querySelector("#carContactModal");

  if (!page || !contactModal) {
    return;
  }

  const openButtons = document.querySelectorAll("[data-open-contact-modal]");
  const closeButtons = document.querySelectorAll("[data-close-contact-modal]");
  const dialog = contactModal.querySelector(".car-contact-modal__dialog");
  const contactForm = contactModal.querySelector("#carContactForm");
  const submitButton = contactModal.querySelector("#carContactSubmitBtn");

  function openContactModal() {
    contactModal.classList.add("is-open");
    contactModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";

    if (typeof gsap !== "undefined") {
      gsap.fromTo(
        dialog,
        {
          opacity: 0,
          y: 28,
          scale: 0.98,
          filter: "blur(8px)",
        },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          filter: "blur(0px)",
          duration: 0.36,
          ease: "power3.out",
        }
      );
    }

    const emailInput = contactModal.querySelector("#contactEmail");

    if (emailInput) {
      setTimeout(function () {
        emailInput.focus();
      }, 150);
    }
  }

  function closeContactModal() {
    function finishClose() {
      contactModal.classList.remove("is-open");
      contactModal.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
    }

    if (typeof gsap !== "undefined") {
      gsap.to(dialog, {
        opacity: 0,
        y: 20,
        scale: 0.98,
        filter: "blur(8px)",
        duration: 0.24,
        ease: "power2.in",
        onComplete: finishClose,
      });
    } else {
      finishClose();
    }
  }

  openButtons.forEach(function (button) {
    button.addEventListener("click", openContactModal);
  });

  closeButtons.forEach(function (button) {
    button.addEventListener("click", closeContactModal);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && contactModal.classList.contains("is-open")) {
      closeContactModal();
    }
  });

  if (contactForm && submitButton) {
    contactForm.addEventListener("submit", function (event) {
      event.preventDefault();

      submitButton.classList.add("is-loading");
      submitButton.setAttribute("disabled", "disabled");

      setTimeout(function () {
        submitButton.classList.remove("is-loading");
        submitButton.removeAttribute("disabled");
        closeContactModal();
      }, 900);
    });
  }

  if (typeof gsap !== "undefined") {
    gsap.from(".js-car-detail-media", {
      opacity: 0,
      x: -28,
      filter: "blur(8px)",
      duration: 0.65,
      ease: "power3.out",
    });

    gsap.from(".js-car-detail-info", {
      opacity: 0,
      x: 28,
      filter: "blur(8px)",
      duration: 0.65,
      delay: 0.12,
      ease: "power3.out",
    });

    gsap.from(".js-car-detail-card", {
      opacity: 0,
      y: 18,
      filter: "blur(8px)",
      duration: 0.52,
      stagger: 0.08,
      delay: 0.18,
      ease: "power2.out",
    });

    gsap.from(".js-car-detail-specs", {
      opacity: 0,
      y: 24,
      filter: "blur(8px)",
      duration: 0.6,
      delay: 0.28,
      ease: "power3.out",
    });
  }
});

// ------------------

//car list partial
document.addEventListener("DOMContentLoaded", function () {
  function animateCarListPartial() {
    const partial = document.querySelector("#carListPartial");

    if (!partial || typeof gsap === "undefined") {
      return;
    }

    const cards = partial.querySelectorAll(".js-car-list-card");
    const empty = partial.querySelector(".js-car-list-empty");
    const pagination = partial.querySelector(".car-list-pagination");

    if (cards.length > 0) {
      gsap.from(cards, {
        opacity: 0,
        y: 22,
        filter: "blur(8px)",
        duration: 0.46,
        stagger: 0.06,
        ease: "power2.out",
      });
    }

    if (empty) {
      gsap.from(empty, {
        opacity: 0,
        y: 20,
        filter: "blur(8px)",
        duration: 0.5,
        ease: "power3.out",
      });
    }

    if (pagination) {
      gsap.from(pagination, {
        opacity: 0,
        y: 14,
        filter: "blur(8px)",
        duration: 0.42,
        delay: 0.12,
        ease: "power2.out",
      });
    }
  }

  document.body.addEventListener("htmx:afterSwap", function (event) {
    if (event.detail.target && event.detail.target.id === "car-container") {
      animateCarListPartial();
    }
  });

  animateCarListPartial();
});
// -----------------------

// recomandation
document.addEventListener("DOMContentLoaded", function () {
  function animateRecommendedCarsSection() {
    const section = document.querySelector("#recommendedCarsSection");

    if (!section || typeof gsap === "undefined") {
      return;
    }

    const header = section.querySelector(".recommended-cars-section__header");
    const cards = section.querySelectorAll(".js-recommended-car-card");

    gsap.from(header, {
      opacity: 0,
      y: 18,
      filter: "blur(8px)",
      duration: 0.5,
      ease: "power3.out",
    });

    gsap.from(cards, {
      opacity: 0,
      y: 22,
      filter: "blur(8px)",
      duration: 0.46,
      stagger: 0.06,
      ease: "power2.out",
      delay: 0.1,
    });
  }

  animateRecommendedCarsSection();
});
// ----------------------

//review form 
document.addEventListener("DOMContentLoaded", function () {
  function bindReviewForm() {
    const reviewForm = document.querySelector("#carReviewForm");

    if (!reviewForm || reviewForm.dataset.bound === "true") {
      return;
    }

    reviewForm.dataset.bound = "true";

    const submitButton = reviewForm.querySelector("#carReviewSubmitBtn");

    if (typeof gsap !== "undefined") {
      gsap.from(reviewForm, {
        opacity: 0,
        y: 20,
        filter: "blur(8px)",
        duration: 0.42,
        ease: "power3.out",
      });
    }

    reviewForm.addEventListener("submit", function () {
      if (submitButton) {
        submitButton.classList.add("is-loading");
        submitButton.setAttribute("disabled", "disabled");
      }
    });
  }

  bindReviewForm();

  document.body.addEventListener("htmx:afterSwap", function () {
    bindReviewForm();
  });
});
// -------------------------

// review list 
document.addEventListener("DOMContentLoaded", function () {
  function animateReviewSection() {
    const section = document.querySelector("#review-section");

    if (!section || typeof gsap === "undefined") {
      return;
    }

    const header = section.querySelector(".car-review-section__header");
    const cards = section.querySelectorAll(".js-car-review-card");
    const empty = section.querySelector(".car-review-empty");

    if (header) {
      gsap.from(header, {
        opacity: 0,
        y: 18,
        filter: "blur(8px)",
        duration: 0.45,
        ease: "power3.out",
      });
    }

    if (cards.length > 0) {
      gsap.from(cards, {
        opacity: 0,
        y: 18,
        filter: "blur(8px)",
        duration: 0.42,
        stagger: 0.06,
        ease: "power2.out",
        delay: 0.08,
      });
    }

    if (empty) {
      gsap.from(empty, {
        opacity: 0,
        y: 18,
        filter: "blur(8px)",
        duration: 0.45,
        ease: "power3.out",
        delay: 0.08,
      });
    }
  }

  animateReviewSection();

  document.body.addEventListener("htmx:afterSwap", function (event) {
    if (event.detail.target && event.detail.target.id === "review-section") {
      animateReviewSection();
    }
  });
});
// ----------------------------------

// review modal 
document.addEventListener("DOMContentLoaded", function () {
  function bindReviewModal() {
    const modals = document.querySelectorAll(".js-car-review-modal");

    modals.forEach(function (modal) {
      if (modal.dataset.bound === "true") {
        return;
      }

      modal.dataset.bound = "true";

      const dialog = modal.querySelector(".car-review-modal__dialog");
      const closeButtons = modal.querySelectorAll("[data-review-modal-close]");

      function closeModal() {
        if (typeof gsap !== "undefined" && dialog) {
          gsap.to(dialog, {
            opacity: 0,
            y: 24,
            scale: 0.98,
            filter: "blur(8px)",
            duration: 0.24,
            ease: "power2.in",
            onComplete: function () {
              modal.remove();
              document.body.style.overflow = "";
            },
          });
        } else {
          modal.remove();
          document.body.style.overflow = "";
        }
      }

      document.body.style.overflow = "hidden";

      if (typeof gsap !== "undefined" && dialog) {
        gsap.fromTo(
          dialog,
          {
            opacity: 0,
            y: 28,
            scale: 0.98,
            filter: "blur(8px)",
          },
          {
            opacity: 1,
            y: 0,
            scale: 1,
            filter: "blur(0px)",
            duration: 0.36,
            ease: "power3.out",
          }
        );
      }

      closeButtons.forEach(function (button) {
        button.addEventListener("click", closeModal);
      });

      document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && document.body.contains(modal)) {
          closeModal();
        }
      });
    });
  }

  bindReviewModal();

  document.body.addEventListener("htmx:afterSwap", function (event) {
    var target = event.detail.target;

    if (
      target &&
      target.id === "review-section" &&
      target.getAttribute("data-close-review-modal") === "true"
    ) {
      document.querySelectorAll(".js-car-review-modal").forEach(function (modal) {
        var dialog = modal.querySelector(".car-review-modal__dialog");

        if (typeof gsap !== "undefined" && dialog) {
          gsap.to(dialog, {
            opacity: 0,
            y: 24,
            scale: 0.98,
            filter: "blur(8px)",
            duration: 0.24,
            ease: "power2.in",
            onComplete: function () {
              modal.remove();
              document.body.style.overflow = "";
            },
          });
        } else {
          modal.remove();
          document.body.style.overflow = "";
        }
      });
    }

    bindReviewModal();
  });
});


// ---------------------------------


//star rating
document.addEventListener("DOMContentLoaded", function () {
  function bindReviewRating() {
    const ratingWidgets = document.querySelectorAll("[data-review-rating]");

    ratingWidgets.forEach(function (widget) {
      if (widget.dataset.bound === "true") {
        return;
      }

      widget.dataset.bound = "true";

      const inputs = widget.querySelectorAll('input[type="radio"]');
      const stars = widget.querySelectorAll(".car-review-rating__star");

      function updateStars(value) {
        const ratingValue = Number(value || 0);

        stars.forEach(function (star) {
          const starValue = Number(star.dataset.ratingValue || 0);

          if (starValue <= ratingValue) {
            star.classList.add("is-active");
          } else {
            star.classList.remove("is-active");
          }
        });
      }

      inputs.forEach(function (input) {
        if (input.checked) {
          updateStars(input.value);
        }

        input.addEventListener("change", function () {
          updateStars(input.value);
        });
      });

      stars.forEach(function (star) {
        star.addEventListener("mouseenter", function () {
          updateStars(star.dataset.ratingValue);
        });
      });

      widget.addEventListener("mouseleave", function () {
        const checkedInput = widget.querySelector('input[type="radio"]:checked');
        updateStars(checkedInput ? checkedInput.value : 0);
      });
    });
  }

  function bindReviewModalCloseButtons() {
    document.querySelectorAll("[data-review-modal-close]").forEach(function (button) {
      if (button.dataset.bound === "true") {
        return;
      }

      if (button.closest(".js-car-review-modal")) {
        return;
      }

      button.dataset.bound = "true";

      button.addEventListener("click", function () {
        const modal = button.closest(".car-review-modal");

        if (modal) {
          modal.remove();
          document.body.style.overflow = "";
        }
      });
    });
  }

  function bindReviewFormLoading() {
    const form = document.querySelector("#carReviewForm");

    if (!form || form.dataset.loadingBound === "true") {
      return;
    }

    form.dataset.loadingBound = "true";

    const submitButton = form.querySelector("#carReviewSubmitBtn");

    form.addEventListener("submit", function () {
      if (submitButton) {
        submitButton.classList.add("is-loading");
        submitButton.setAttribute("disabled", "disabled");
      }
    });
  }

  function initReviewUI() {
    bindReviewRating();
    bindReviewModalCloseButtons();
    bindReviewFormLoading();
  }

  initReviewUI();

  document.body.addEventListener("htmx:afterSwap", function () {
    initReviewUI();
  });
});