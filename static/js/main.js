/* VEE Agency — behaviour layer.
 *
 * Every behaviour here is an enhancement. The site must remain fully readable
 * and usable if this file fails to load, so nothing hides content that only
 * JavaScript can bring back.
 */
(function () {
    "use strict";

    var root = document.documentElement;
    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------------------------------------------------------------- Preloader */

    function initPreloader() {
        var preloader = document.querySelector("[data-preloader]");
        if (!preloader) return;

        function dismiss() {
            preloader.classList.add("is-done");
            window.setTimeout(function () {
                if (preloader.parentNode) preloader.parentNode.removeChild(preloader);
            }, 500);
        }

        if (reduceMotion) {
            dismiss();
            return;
        }

        // Never let the preloader be the reason the site feels slow: it clears on
        // load, and a hard timeout guarantees it clears even if an asset stalls.
        var timeout = window.setTimeout(dismiss, 2000);
        window.addEventListener("load", function () {
            window.clearTimeout(timeout);
            window.setTimeout(dismiss, 200);
        });
    }

    /* ------------------------------------------------------------------- Header */

    function initHeader() {
        var header = document.querySelector("[data-header]");
        if (!header) return;

        var ticking = false;

        function update() {
            header.classList.toggle("is-scrolled", window.scrollY > 12);
            ticking = false;
        }

        window.addEventListener("scroll", function () {
            if (ticking) return;
            ticking = true;
            window.requestAnimationFrame(update);
        }, { passive: true });

        update();
    }

    /* -------------------------------------------------------------- Mobile menu */

    var FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])';

    function initMobileNav() {
        var toggle = document.querySelector("[data-menu-toggle]");
        var panel = document.querySelector("[data-mobile-nav]");
        if (!toggle || !panel) return;

        function open() {
            panel.classList.add("is-open");
            toggle.setAttribute("aria-expanded", "true");
            document.body.classList.add("nav-open");
            var first = panel.querySelector(FOCUSABLE);
            if (first) first.focus();
        }

        function close(returnFocus) {
            panel.classList.remove("is-open");
            toggle.setAttribute("aria-expanded", "false");
            document.body.classList.remove("nav-open");
            if (returnFocus) toggle.focus();
        }

        toggle.addEventListener("click", function () {
            if (toggle.getAttribute("aria-expanded") === "true") close(false);
            else open();
        });

        // Escape closes, and Tab is trapped inside the panel while it is open.
        document.addEventListener("keydown", function (event) {
            if (!panel.classList.contains("is-open")) return;

            if (event.key === "Escape") {
                close(true);
                return;
            }

            if (event.key !== "Tab") return;

            var items = Array.prototype.filter.call(
                panel.querySelectorAll(FOCUSABLE),
                function (el) { return el.offsetParent !== null; }
            );
            if (!items.length) return;

            var first = items[0];
            var last = items[items.length - 1];

            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        });

        // Following a link should not leave the overlay open behind the new page.
        panel.addEventListener("click", function (event) {
            if (event.target.closest("a")) close(false);
        });

        // The overlay is a mobile affordance; a resize to desktop must reset it.
        window.matchMedia("(min-width: 1060px)").addEventListener("change", function (event) {
            if (event.matches) close(false);
        });
    }

    /* ----------------------------------------------------------------- Carousel */

    function initCarousel(carousel) {
        var slides = Array.prototype.slice.call(carousel.querySelectorAll("[data-slide]"));
        var dots = Array.prototype.slice.call(carousel.querySelectorAll("[data-dot]"));
        var prev = carousel.querySelector("[data-carousel-prev]");
        var next = carousel.querySelector("[data-carousel-next]");
        if (slides.length < 2) return;

        var index = 0;
        var timer = null;
        var INTERVAL = 6000;

        function show(nextIndex) {
            index = (nextIndex + slides.length) % slides.length;

            slides.forEach(function (slide, i) {
                var active = i === index;
                slide.classList.toggle("is-active", active);
                slide.setAttribute("aria-hidden", active ? "false" : "true");
            });

            dots.forEach(function (dot, i) {
                dot.setAttribute("aria-selected", i === index ? "true" : "false");
                dot.setAttribute("tabindex", i === index ? "0" : "-1");
            });
        }

        function stop() {
            if (timer) {
                window.clearInterval(timer);
                timer = null;
            }
        }

        function start() {
            if (reduceMotion) return;
            stop();
            timer = window.setInterval(function () { show(index + 1); }, INTERVAL);
        }

        function goTo(i) {
            show(i);
            start();
        }

        dots.forEach(function (dot, i) {
            dot.addEventListener("click", function () { goTo(i); });
        });

        if (prev) prev.addEventListener("click", function () { goTo(index - 1); });
        if (next) next.addEventListener("click", function () { goTo(index + 1); });

        carousel.addEventListener("keydown", function (event) {
            if (event.key === "ArrowLeft") { event.preventDefault(); goTo(index - 1); }
            if (event.key === "ArrowRight") { event.preventDefault(); goTo(index + 1); }
        });

        // Autoplay must never fight the user: pause on hover, focus, or a hidden tab.
        carousel.addEventListener("mouseenter", stop);
        carousel.addEventListener("mouseleave", start);
        carousel.addEventListener("focusin", stop);
        carousel.addEventListener("focusout", function (event) {
            if (!carousel.contains(event.relatedTarget)) start();
        });

        document.addEventListener("visibilitychange", function () {
            if (document.hidden) stop();
            else start();
        });

        show(0);
        start();
    }

    /* ------------------------------------------------------------ Scroll reveal */

    function initReveals() {
        var targets = document.querySelectorAll(".reveal, .reveal-group");
        if (!targets.length) return;

        // Without IntersectionObserver, reveal everything immediately rather than
        // leaving content hidden.
        if (reduceMotion || !("IntersectionObserver" in window)) {
            Array.prototype.forEach.call(targets, function (el) {
                el.classList.add("is-visible");
            });
            return;
        }

        root.classList.add("js-motion");

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            });
        }, { rootMargin: "0px 0px -12% 0px", threshold: 0.1 });

        Array.prototype.forEach.call(targets, function (el) { observer.observe(el); });

        // Safety net. Reveal-on-scroll is the only thing on the site that hides
        // content, so it gets a hard deadline: if the observer never fires for an
        // element — an unusual viewport, a headless renderer, a print request —
        // it becomes visible anyway rather than staying blank forever.
        window.setTimeout(function () {
            Array.prototype.forEach.call(targets, function (el) {
                el.classList.add("is-visible");
            });
            observer.disconnect();
        }, 4000);
    }

    /* -------------------------------------------------------------- Back to top */

    function initBackToTop() {
        var button = document.querySelector("[data-back-to-top]");
        if (!button) return;

        var ticking = false;

        function update() {
            button.classList.toggle("is-visible", window.scrollY > window.innerHeight * 0.8);
            ticking = false;
        }

        window.addEventListener("scroll", function () {
            if (ticking) return;
            ticking = true;
            window.requestAnimationFrame(update);
        }, { passive: true });

        button.addEventListener("click", function () {
            window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
            var skip = document.querySelector(".skip-link");
            if (skip) skip.focus({ preventScroll: true });
        });

        update();
    }

    /* --------------------------------------------------------------- Newsletter */

    function initNewsletter() {
        var form = document.querySelector("[data-newsletter]");
        if (!form) return;

        var status = form.querySelector("[data-newsletter-status]");
        var button = form.querySelector("button[type='submit']");

        form.addEventListener("submit", function (event) {
            if (!window.fetch) return; // Fall back to the normal POST + redirect.
            event.preventDefault();

            var data = new FormData(form);
            if (button) button.disabled = true;
            if (status) {
                status.className = "newsletter__status";
                status.textContent = "Subscribing…";
            }

            fetch(form.action, {
                method: "POST",
                body: data,
                headers: { "X-Requested-With": "XMLHttpRequest" }
            })
                .then(function (response) { return response.json(); })
                .then(function (payload) {
                    if (!status) return;
                    var ok = payload && payload.success;
                    status.className = "newsletter__status " + (ok ? "is-success" : "is-error");
                    status.textContent = (payload && payload.message) ||
                        (ok ? "You're subscribed. Thanks!" : "That didn't work. Please try again.");
                    if (ok) form.reset();
                })
                .catch(function () {
                    if (!status) return;
                    status.className = "newsletter__status is-error";
                    status.textContent = "Network error. Please try again.";
                })
                .then(function () {
                    if (button) button.disabled = false;
                });
        });
    }

    /* ------------------------------------------------------ Cookies & analytics */

    var CONSENT_KEY = "vee-cookie-consent";

    function readConsent() {
        try {
            return window.localStorage.getItem(CONSENT_KEY);
        } catch (error) {
            // Private browsing or blocked site data. Treat as "not decided" —
            // the banner reappears, and nothing loads without an explicit yes.
            return null;
        }
    }

    function writeConsent(value) {
        try {
            window.localStorage.setItem(CONSENT_KEY, value);
        } catch (error) {
            /* Consent simply is not remembered; it is never assumed. */
        }
    }

    function loadAnalytics(config) {
        if (config.ga4) {
            window.dataLayer = window.dataLayer || [];
            window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
            window.gtag("js", new Date());
            window.gtag("config", config.ga4, { anonymize_ip: true });

            var ga = document.createElement("script");
            ga.async = true;
            ga.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(config.ga4);
            document.head.appendChild(ga);
        }

        if (config.pixel) {
            /* eslint-disable */
            !function (f, b, e, v, n, t, s) {
                if (f.fbq) return; n = f.fbq = function () {
                    n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
                };
                if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = [];
                t = b.createElement(e); t.async = !0; t.src = v;
                s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
            }(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
            /* eslint-enable */
            window.fbq("init", config.pixel);
            window.fbq("track", "PageView");
        }
    }

    // Best effort: withdrawing consent should take the cookies with it. These are
    // first-party, so the page can clear them; anything already sent cannot be recalled.
    function clearAnalyticsCookies() {
        var host = window.location.hostname;
        var domains = [host, "." + host];
        var parts = host.split(".");
        if (parts.length > 2) domains.push("." + parts.slice(-2).join("."));

        document.cookie.split(";").forEach(function (entry) {
            var name = entry.split("=")[0].trim();
            if (!/^(_ga|_gid|_gat|_fbp|_fbc)/.test(name)) return;
            domains.forEach(function (domain) {
                document.cookie = name + "=; path=/; domain=" + domain +
                    "; expires=Thu, 01 Jan 1970 00:00:00 GMT";
            });
            document.cookie = name + "=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
        });
    }

    function initCookieConsent() {
        var banner = document.querySelector("[data-cookie-banner]");
        var configNode = document.getElementById("analytics-config");

        // No banner means nothing on this site sets a non-essential cookie.
        if (!banner || !configNode) return;

        var config;
        try {
            config = JSON.parse(configNode.textContent);
        } catch (error) {
            return;
        }

        var accept = banner.querySelector("[data-cookie-accept]");
        var decline = banner.querySelector("[data-cookie-decline]");
        var lastFocused = null;

        // Publish the banner's real height so the floating controls can sit clear
        // of it. The height varies with text wrapping and button stacking, so it
        // has to be measured rather than assumed.
        function publishHeight() {
            var height = banner.hidden ? 0 : banner.getBoundingClientRect().height;
            root.style.setProperty("--cookie-banner-height", height + "px");
        }

        function show() {
            lastFocused = document.activeElement;
            banner.hidden = false;
            document.body.classList.add("cookie-banner-open");
            publishHeight();
            // Next frame, so the entrance transition has a starting state.
            window.requestAnimationFrame(function () {
                banner.classList.add("is-open");
                publishHeight();
            });
        }

        function hide() {
            banner.classList.remove("is-open");
            banner.hidden = true;
            document.body.classList.remove("cookie-banner-open");
            publishHeight();
            if (lastFocused && typeof lastFocused.focus === "function") lastFocused.focus();
        }

        window.addEventListener("resize", function () {
            if (!banner.hidden) publishHeight();
        }, { passive: true });

        function onAccept() {
            writeConsent("accepted");
            hide();
            loadAnalytics(config);
        }

        function onDecline() {
            writeConsent("declined");
            hide();
            clearAnalyticsCookies();
        }

        if (accept) accept.addEventListener("click", onAccept);
        if (decline) decline.addEventListener("click", onDecline);

        banner.addEventListener("keydown", function (event) {
            // Escape declines rather than dismissing silently: no choice is not consent.
            if (event.key === "Escape") onDecline();
        });

        // Let the footer link reopen the banner so consent can be withdrawn as
        // easily as it was given.
        Array.prototype.forEach.call(
            document.querySelectorAll("[data-cookie-settings]"),
            function (trigger) {
                trigger.hidden = false;
                trigger.addEventListener("click", function (event) {
                    event.preventDefault();
                    show();
                    if (decline) decline.focus();
                });
            }
        );

        var stored = readConsent();
        if (stored === "accepted") loadAnalytics(config);
        else if (stored !== "declined") show();
    }

    /* --------------------------------------------------------------- Bootstrap */

    function init() {
        initPreloader();
        initHeader();
        initMobileNav();
        initReveals();
        initBackToTop();
        initNewsletter();
        initCookieConsent();

        Array.prototype.forEach.call(
            document.querySelectorAll("[data-carousel]"),
            initCarousel
        );
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
