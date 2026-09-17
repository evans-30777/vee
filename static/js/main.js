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
        // Must match the nav breakpoint in main.css.
        var desktop = window.matchMedia("(min-width: 1000px)");
        if (desktop.addEventListener) {
            desktop.addEventListener("change", function (event) {
                if (event.matches) close(false);
            });
        } else if (desktop.addListener) {
            // Safari 13 and earlier. Unguarded, this threw and took every
            // behaviour registered after it down with it — including cookie
            // consent, so analytics never loaded on those browsers.
            desktop.addListener(function (event) {
                if (event.matches) close(false);
            });
        }
    }

    /* --------------------------------------------------- Autoplay pause control */

    /* WCAG 2.2.2 (Level A): anything that moves by itself for more than five
     * seconds needs a way to stop it. Pausing on hover and focus is good
     * behaviour but does not satisfy it — the control has to be discoverable
     * and operable, which means a real button.
     *
     * A user pause is sticky: unlike a hover pause it survives the pointer
     * leaving, because the person asked for it.
     */
    function buildPauseControl(container, api) {
        var button = container.querySelector("[data-autoplay-toggle]");
        if (!button) return null;

        var userPaused = false;

        function paint() {
            button.setAttribute("aria-pressed", userPaused ? "true" : "false");
            button.setAttribute(
                "aria-label",
                userPaused ? "Resume automatic sliding" : "Pause automatic sliding"
            );
            button.classList.toggle("is-paused", userPaused);
        }

        button.addEventListener("click", function () {
            userPaused = !userPaused;
            if (userPaused) api.stop();
            else api.start();
            paint();
        });

        button.hidden = false;
        paint();

        return {
            isUserPaused: function () { return userPaused; }
        };
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
        var heroResume = null;
        var INTERVAL = 6000;

        function show(nextIndex) {
            index = (nextIndex + slides.length) % slides.length;

            slides.forEach(function (slide, i) {
                var active = i === index;
                slide.classList.toggle("is-active", active);
                slide.setAttribute("aria-hidden", active ? "false" : "true");
            });

            dots.forEach(function (dot, i) {
                dot.setAttribute("aria-current", i === index ? "true" : "false");
                dot.setAttribute("tabindex", i === index ? "0" : "-1");
            });
        }

        function stop() {
            if (timer) {
                window.clearInterval(timer);
                timer = null;
            }
        }

        var pause = null;

        function start() {
            if (reduceMotion) return;
            if (pause && pause.isUserPaused()) return;
            stop();
            timer = window.setInterval(function () { show(index + 1); }, INTERVAL);
        }

        function goTo(i) {
            show(i);
            start();
        }

        pause = buildPauseControl(carousel, { start: start, stop: stop });

        dots.forEach(function (dot, i) {
            dot.addEventListener("click", function () { goTo(i); });
        });

        if (prev) prev.addEventListener("click", function () { goTo(index - 1); });
        if (next) next.addEventListener("click", function () { goTo(index + 1); });

        carousel.addEventListener("keydown", function (event) {
            if (event.key === "ArrowLeft") { event.preventDefault(); goTo(index - 1); }
            if (event.key === "ArrowRight") { event.preventDefault(); goTo(index + 1); }
        });

        // Autoplay must never fight the user: pause on hover, focus, or a hidden
        // tab — and on touch, where hover events never arrive, resume on a timer
        // rather than stopping for good.
        carousel.addEventListener("pointerdown", function () {
            stop();
            if (heroResume) window.clearTimeout(heroResume);
            heroResume = window.setTimeout(start, 9000);
        });
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

    /* ------------------------------------------------------------- Showcase */

    function initShowcase(showcase) {
        var viewport = showcase.querySelector("[data-showcase-viewport]");
        var items = Array.prototype.slice.call(showcase.querySelectorAll("[data-showcase-item]"));
        var controls = showcase.querySelector("[data-showcase-controls]");
        var progress = showcase.querySelector("[data-showcase-progress]");
        var progressFill = showcase.querySelector("[data-showcase-progress-fill]");
        var position = showcase.querySelector("[data-showcase-position]");
        var prev = showcase.querySelector("[data-showcase-prev]");
        var next = showcase.querySelector("[data-showcase-next]");
        if (!viewport || items.length < 2) return;

        // The controls are hidden in markup: without JS they would do nothing,
        // while the scroll-snap track itself still works by swipe.
        if (controls) controls.hidden = false;

        var index = 0;
        var timer = null;
        var INTERVAL = 5000;
        // Long enough not to yank the card away from someone mid-read, short
        // enough that the section is clearly still alive.
        var RESUME_AFTER = 9000;

        function scrollToIndex(i) {
            index = (i + items.length) % items.length;
            var target = items[index];
            // Centre the item, matching scroll-snap-align: center.
            var left = target.offsetLeft - (viewport.clientWidth - target.clientWidth) / 2;
            viewport.scrollTo({
                left: Math.max(0, left),
                behavior: reduceMotion ? "auto" : "smooth"
            });
            paint();
        }

        function paint() {
            var share = 100 / items.length;
            if (progressFill) {
                progressFill.style.width = share + "%";
                progressFill.style.transform = "translateX(" + (index * 100) + "%)";
            }
            if (progress) {
                progress.setAttribute("aria-valuemax", String(items.length));
                progress.setAttribute("aria-valuenow", String(index + 1));
                progress.setAttribute(
                    "aria-valuetext",
                    (index + 1) + " of " + items.length
                );
            }
            if (position) {
                position.textContent = pad(index + 1) + " / " + pad(items.length);
            }
        }

        function pad(n) { return n < 10 ? "0" + n : String(n); }

        // Keep the dots honest when the user swipes or scrolls by hand.
        var scrollTick = false;
        viewport.addEventListener("scroll", function () {
            if (scrollTick) return;
            scrollTick = true;
            window.requestAnimationFrame(function () {
                var centre = viewport.scrollLeft + viewport.clientWidth / 2;
                var closest = 0;
                var best = Infinity;
                items.forEach(function (item, i) {
                    var distance = Math.abs(item.offsetLeft + item.clientWidth / 2 - centre);
                    if (distance < best) { best = distance; closest = i; }
                });
                if (closest !== index) { index = closest; paint(); }
                scrollTick = false;
            });
        }, { passive: true });

        function stop() {
            if (timer) { window.clearInterval(timer); timer = null; }
        }

        var pause = null;

        function start() {
            if (reduceMotion) return;
            if (pause && pause.isUserPaused()) return;
            stop();
            timer = window.setInterval(function () { scrollToIndex(index + 1); }, INTERVAL);
        }

        pause = buildPauseControl(showcase, { start: start, stop: stop });

        if (prev) prev.addEventListener("click", function () { scrollToIndex(index - 1); start(); });
        if (next) next.addEventListener("click", function () { scrollToIndex(index + 1); start(); });

        viewport.addEventListener("keydown", function (event) {
            if (event.key === "ArrowLeft") { event.preventDefault(); scrollToIndex(index - 1); start(); }
            if (event.key === "ArrowRight") { event.preventDefault(); scrollToIndex(index + 1); start(); }
        });

        // Never fight the user, and never animate a tab nobody is looking at.
        //
        // On a touch screen `mouseenter`/`mouseleave` never fire, so a pause on
        // interaction had nothing to un-pause it: one tap or swipe anywhere on
        // the showcase stopped the auto-advance for the rest of the visit. It
        // now resumes on a timer after the interaction ends, which is what
        // "it should slide by itself" actually requires.
        var resumeTimer = null;

        function pauseBriefly() {
            stop();
            if (resumeTimer) window.clearTimeout(resumeTimer);
            resumeTimer = window.setTimeout(start, RESUME_AFTER);
        }

        showcase.addEventListener("mouseenter", stop);
        showcase.addEventListener("mouseleave", start);
        showcase.addEventListener("focusin", stop);
        showcase.addEventListener("focusout", function (event) {
            if (!showcase.contains(event.relatedTarget)) start();
        });
        viewport.addEventListener("pointerdown", pauseBriefly);
        viewport.addEventListener("touchend", pauseBriefly, { passive: true });
        document.addEventListener("visibilitychange", function () {
            if (document.hidden) stop(); else start();
        });

        paint();
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
            // Only once there is a real journey to undo. At 0.8 of a viewport it
            // appeared almost immediately and then sat over the text.
            var scrolled = window.scrollY;
            var total = document.documentElement.scrollHeight - window.innerHeight;
            button.classList.toggle(
                "is-visible",
                scrolled > window.innerHeight * 1.8 && total > window.innerHeight
            );
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

        // The status line is a sibling of the form, not a child, so it has to be
        // looked up from the surrounding block. Scoped to the form first in case
        // a future layout moves it inside.
        var status = form.querySelector("[data-newsletter-status]") ||
                     (form.parentNode && form.parentNode.querySelector("[data-newsletter-status]")) ||
                     document.querySelector("[data-newsletter-status]");
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
                    var ok = Boolean(payload && payload.success);

                    // Deliberately before the status update: a missing status
                    // element must not be able to swallow the conversion.
                    if (ok) {
                        form.reset();
                        track("newsletter_signup", { page: document.body.className || "page" });
                    }

                    if (!status) return;
                    status.className = "newsletter__status " + (ok ? "is-success" : "is-error");
                    status.textContent = (payload && payload.message) ||
                        (ok ? "You're subscribed. Thanks!" : "That didn't work. Please try again.");
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

    /* Conversion tracking.
     *
     * Every event goes through track(). Nothing is sent unless analytics have
     * actually been loaded, which only happens after consent, so this is inert
     * on a site with no IDs configured and on every visit that declined.
     *
     * Events raised before consent is decided are queued rather than dropped:
     * the thank-you page is a first visit for many people, and that is the one
     * conversion we cannot afford to lose to a banner still being on screen.
     */
    var analyticsReady = false;
    var pendingEvents = [];

    /* GA4 event name -> Meta standard event. Anything absent is GA4 only. */
    var META_EVENTS = {
        generate_lead: "Lead",
        contact_whatsapp: "Contact",
        contact_call: "Contact",
        contact_email: "Contact",
        newsletter_signup: "Subscribe"
    };

    function track(name, params) {
        if (!analyticsReady) {
            // Bounded: a page nobody consents on must not grow a list forever.
            if (pendingEvents.length < 20) pendingEvents.push([name, params]);
            return;
        }
        var payload = params || {};
        if (window.gtag) window.gtag("event", name, payload);
        if (window.fbq && META_EVENTS[name]) {
            window.fbq("track", META_EVENTS[name], payload);
        }
    }

    function flushPendingEvents() {
        var queued = pendingEvents;
        pendingEvents = [];
        queued.forEach(function (entry) { track(entry[0], entry[1]); });
    }

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

        analyticsReady = Boolean(config.ga4 || config.pixel);
        if (analyticsReady) flushPendingEvents();
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
                // A dialog nobody is sent to is a dialog keyboard and screen
                // reader users have to go looking for, at the very end of the
                // document. Focus the heading rather than a button, so neither
                // choice is presented as the default.
                var heading = banner.querySelector(".cookie-banner__title");
                if (heading) {
                    heading.setAttribute("tabindex", "-1");
                    heading.focus();
                }
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
            // No consent means no events, ever. Drop what was waiting.
            pendingEvents = [];
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

    /* ------------------------------------------------------ Form validation */

    function initFormValidation() {
        var forms = document.querySelectorAll("form[data-validate]");
        if (!forms.length) return;

        Array.prototype.forEach.call(forms, function (form) {
            // Constraint validation is already in the markup — required, type
            //="email". The browser will enforce it; this only replaces the
            // native bubble, which is inconsistent across browsers and vanishes
            // the moment you look away.
            var invalidThisSubmit = [];

            function messageFor(field) {
                if (field.validity.valueMissing) {
                    return field.type === "email"
                        ? "We need an email address to reply to you."
                        : "This one is needed.";
                }
                if (field.validity.typeMismatch && field.type === "email") {
                    return "That doesn't look like an email address — check for a typo.";
                }
                return field.validationMessage || "Please check this.";
            }

            function errorNode(field) {
                var wrapper = field.closest(".field");
                if (!wrapper) return null;
                var node = wrapper.querySelector("[data-live-error]");
                if (!node) {
                    node = document.createElement("p");
                    node.className = "field__error";
                    node.setAttribute("data-live-error", "");
                    node.id = field.id + "_live_error";
                    wrapper.appendChild(node);
                }
                return node;
            }

            function showError(field) {
                var wrapper = field.closest(".field");
                var node = errorNode(field);
                if (wrapper) wrapper.classList.add("field--invalid");
                field.setAttribute("aria-invalid", "true");
                if (node) {
                    node.textContent = messageFor(field);
                    // Point the field at its message without losing whatever it
                    // was already described by (hint text, a server error).
                    var described = (field.getAttribute("aria-describedby") || "").split(/\s+/);
                    if (described.indexOf(node.id) === -1) {
                        described.push(node.id);
                        field.setAttribute("aria-describedby", described.join(" ").trim());
                    }
                }
            }

            function clearError(field) {
                var wrapper = field.closest(".field");
                var node = wrapper && wrapper.querySelector("[data-live-error]");
                if (wrapper) wrapper.classList.remove("field--invalid");
                field.removeAttribute("aria-invalid");
                if (node) node.textContent = "";
            }

            // `invalid` does not bubble, so it is captured rather than delegated.
            //
            // The focus move has to happen here, not on `submit`: when
            // constraint validation fails the browser never fires `submit` at
            // all, so a handler there would never run. `invalid` fires once per
            // field in document order, so the first one of a batch is the first
            // problem on the page.
            form.addEventListener("invalid", function (event) {
                event.preventDefault();       // suppress the native bubble
                var field = event.target;
                showError(field);

                if (invalidThisSubmit.length === 0) {
                    // Deferred so every field in this attempt has been marked
                    // before the page moves.
                    window.setTimeout(function () {
                        field.focus();
                        if (field.scrollIntoView) {
                            field.scrollIntoView({
                                block: "center",
                                behavior: reduceMotion ? "auto" : "smooth"
                            });
                        }
                        invalidThisSubmit = [];
                    }, 0);
                }
                invalidThisSubmit.push(field);
            }, true);

            // Clear as soon as it is fixed, rather than making them submit again
            // to find out.
            form.addEventListener("input", function (event) {
                var field = event.target;
                if (field.checkValidity && field.checkValidity()) clearError(field);
            });
            form.addEventListener("change", function (event) {
                var field = event.target;
                if (field.checkValidity && field.checkValidity()) clearError(field);
            });
        });
    }

    /* A failed server-side submit reloads to the top of the page, where nothing
     * says anything went wrong. Move the cursor to the summary instead. */
    function focusErrorSummary() {
        var summary = document.querySelector("[data-error-summary]");
        if (!summary) return;
        summary.focus();
    }

    /* ------------------------------------------------- Conversion tracking */

    function initConversionTracking() {
        /* A server-confirmed conversion. The thank-you page is only reached
         * after the enquiry row is committed, so this counts real leads rather
         * than submit attempts. */
        var marker = document.getElementById("conversion-event");
        if (marker) {
            try {
                var conversion = JSON.parse(marker.textContent);
                if (conversion && conversion.name) track(conversion.name, conversion.params);
            } catch (error) {
                /* A malformed marker must never break the page it is on. */
            }
        }

        /* WhatsApp and phone are the channels this business actually converts
         * on, and both leave the site. Delegated from the document so links
         * added later — a rendered blog body, an admin-edited panel — are
         * covered without re-binding. */
        document.addEventListener("click", function (event) {
            var link = event.target.closest && event.target.closest("a[href]");
            if (!link) return;

            var href = link.getAttribute("href") || "";
            var where = link.getAttribute("data-track-context") ||
                        (document.body.className || "page");

            if (href.indexOf("wa.me/") !== -1 || href.indexOf("api.whatsapp.com") !== -1) {
                track("contact_whatsapp", { method: "whatsapp", page: where });
            } else if (href.indexOf("tel:") === 0) {
                track("contact_call", { method: "phone", page: where });
            } else if (href.indexOf("mailto:") === 0) {
                track("contact_email", { method: "email", page: where });
            }
        });

        /* Submit attempts, so the gap between starting and finishing an
         * enquiry is visible. The lead itself is counted on the thank-you
         * page, not here. */
        var enquiry = document.querySelector("form.form[method='post']");
        if (enquiry) {
            enquiry.addEventListener("submit", function () {
                var service = enquiry.querySelector("[name='service']");
                track("enquiry_submitted", {
                    service: service && service.value ? service.value : "unspecified"
                });
            });
        }
    }

    /* --------------------------------------------------------------- Bootstrap */

    function init() {
        initPreloader();
        initHeader();
        initMobileNav();
        initReveals();
        initBackToTop();
        initNewsletter();
        initFormValidation();
        focusErrorSummary();
        initCookieConsent();
        initConversionTracking();

        Array.prototype.forEach.call(
            document.querySelectorAll("[data-carousel]"),
            initCarousel
        );

        Array.prototype.forEach.call(
            document.querySelectorAll("[data-showcase]"),
            initShowcase
        );
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
