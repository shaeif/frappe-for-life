/* LabQubit website behaviour. Vanilla JS, no dependencies, progressive enhancement:
 * every page works without it. */
(() => {
	"use strict";

	const $ = (sel, root = document) => root.querySelector(sel);
	const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
	const html = document.documentElement;
	const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
	const isRtl = () => html.dir === "rtl";

	const getCookie = (name) => {
		const match = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
		return match ? decodeURIComponent(match[1]) : "";
	};

	/* Theme ------------------------------------------------------------ */
	$$("[data-theme-toggle]").forEach((btn) =>
		btn.addEventListener("click", () => {
			const next = html.dataset.theme === "dark" ? "light" : "dark";
			html.dataset.theme = next;
			try {
				localStorage.setItem("lq-theme", next);
			} catch (e) {
				/* private mode */
			}
		})
	);

	/* Navbar: solid background after scrolling --------------------------- */
	const nav = $("[data-nav]");
	if (nav) {
		const onScroll = () => nav.setAttribute("data-scrolled", window.scrollY > 8 ? "true" : "false");
		onScroll();
		window.addEventListener("scroll", onScroll, { passive: true });
	}

	/* Mega menus: hover on desktop pointers, click/keyboard everywhere ---- */
	const megas = $$("[data-mega]");
	const setMega = (item, open) => {
		const trigger = $("[data-mega-trigger]", item);
		const panel = $("[data-mega-panel]", item);
		if (!trigger || !panel) return;
		trigger.setAttribute("aria-expanded", open ? "true" : "false");
		panel.setAttribute("data-open", open ? "true" : "false");
	};
	const closeAllMegas = (except) => megas.forEach((m) => m !== except && setMega(m, false));

	megas.forEach((item) => {
		const trigger = $("[data-mega-trigger]", item);
		let closeTimer;
		let hoverOpenedAt = 0;
		trigger.addEventListener("click", () => {
			// a click right after hover-open (pointer moving onto the button) keeps it open
			if (Date.now() - hoverOpenedAt < 600) return;
			const open = trigger.getAttribute("aria-expanded") !== "true";
			closeAllMegas(item);
			setMega(item, open);
		});
		if (window.matchMedia("(hover: hover)").matches) {
			item.addEventListener("mouseenter", () => {
				clearTimeout(closeTimer);
				closeAllMegas(item);
				if (trigger.getAttribute("aria-expanded") !== "true") hoverOpenedAt = Date.now();
				setMega(item, true);
			});
			item.addEventListener("mouseleave", () => {
				closeTimer = setTimeout(() => setMega(item, false), 160);
			});
		}
		item.addEventListener("focusout", (e) => {
			if (!item.contains(e.relatedTarget)) setMega(item, false);
		});
	});
	document.addEventListener("click", (e) => {
		if (!e.target.closest("[data-mega]")) closeAllMegas();
	});

	/* Mobile drawer ------------------------------------------------------ */
	const drawer = $("[data-drawer]");
	const drawerOpeners = $$("[data-drawer-open]");
	let lastFocus = null;
	const setDrawer = (open) => {
		if (!drawer) return;
		if (open) {
			lastFocus = document.activeElement;
			drawer.hidden = false;
			requestAnimationFrame(() => drawer.setAttribute("data-open", "true"));
			document.body.style.overflow = "hidden";
			const first = $("[data-drawer-close]:not(div), a, button", $(".lq-drawer-panel", drawer));
			if (first) first.focus();
		} else {
			drawer.setAttribute("data-open", "false");
			document.body.style.overflow = "";
			setTimeout(() => (drawer.hidden = true), reducedMotion ? 0 : 300);
			if (lastFocus) lastFocus.focus();
		}
		drawerOpeners.forEach((b) => b.setAttribute("aria-expanded", open ? "true" : "false"));
	};
	drawerOpeners.forEach((b) => b.addEventListener("click", () => setDrawer(true)));
	if (drawer) {
		$$("[data-drawer-close]", drawer).forEach((el) => el.addEventListener("click", () => setDrawer(false)));
		$$("a[href]", drawer).forEach((a) => a.addEventListener("click", () => setDrawer(false)));
		// keep keyboard focus inside the open drawer
		drawer.addEventListener("keydown", (e) => {
			if (e.key !== "Tab") return;
			const items = $$("a[href], button:not([disabled]), summary", drawer).filter((el) => el.offsetParent !== null);
			if (!items.length) return;
			const first = items[0];
			const last = items[items.length - 1];
			if (e.shiftKey && document.activeElement === first) {
				last.focus();
				e.preventDefault();
			} else if (!e.shiftKey && document.activeElement === last) {
				first.focus();
				e.preventDefault();
			}
		});
	}

	document.addEventListener("keydown", (e) => {
		if (e.key !== "Escape") return;
		closeAllMegas();
		if (drawer && drawer.getAttribute("data-open") === "true") setDrawer(false);
	});

	/* Logged-in state (pages are cached, so this is decided in the browser) */
	const userId = getCookie("user_id");
	const loggedIn = userId && userId !== "Guest";
	$$("[data-auth]").forEach((el) => {
		el.hidden = (el.dataset.auth === "user") !== Boolean(loggedIn);
	});
	if (loggedIn) {
		const isSystemUser = getCookie("system_user") === "yes";
		$$("[data-portal-link]").forEach((a) => (a.href = isSystemUser ? "/app" : "/portal"));
		const fullName = getCookie("full_name");
		if (fullName) $$("[data-user-name]").forEach((el) => (el.textContent = fullName.split(" ")[0]));
	}

	/* Language switch: remember the choice, then reload without ?_lang ---- */
	$$("[data-lang-switch]").forEach((a) =>
		a.addEventListener("click", (e) => {
			const lang = a.dataset.langSwitch;
			e.preventDefault();
			document.cookie = `preferred_language=${lang}; path=/; max-age=31536000; samesite=lax`;
			const go = () => {
				const url = new URL(window.location.href);
				url.searchParams.delete("_lang");
				window.location.href = url.toString();
			};
			// logged-in users keep their language in their profile
			if (loggedIn && window.fetch) {
				fetch("/api/method/labqubit.api.preferences.set_language", {
					method: "POST",
					headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": (window.frappe && frappe.csrf_token) || "" },
					body: JSON.stringify({ lang }),
				}).finally(go);
			} else {
				go();
			}
		})
	);

	/* Scroll reveal ------------------------------------------------------ */
	const revealables = $$("[data-reveal]");
	if (!("IntersectionObserver" in window) || reducedMotion) {
		revealables.forEach((el) => el.setAttribute("data-revealed", ""));
	} else {
		const io = new IntersectionObserver(
			(entries) =>
				entries.forEach((entry) => {
					if (!entry.isIntersecting) return;
					entry.target.setAttribute("data-revealed", "");
					io.unobserve(entry.target);
				}),
			{ rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
		);
		revealables.forEach((el) => io.observe(el));
	}

	/* Animated counters -------------------------------------------------- */
	const counters = $$("[data-count-to]");
	const formatter = (decimals) =>
		new Intl.NumberFormat(html.lang === "ar" ? "ar" : "en", {
			minimumFractionDigits: decimals,
			maximumFractionDigits: decimals,
		});
	const runCounter = (el) => {
		const target = parseFloat(el.dataset.countTo) || 0;
		const decimals = parseInt(el.dataset.decimals || "0", 10);
		const fmt = formatter(decimals);
		if (reducedMotion) {
			el.textContent = fmt.format(target);
			return;
		}
		const duration = 1600;
		const start = performance.now();
		const tick = (now) => {
			const p = Math.min((now - start) / duration, 1);
			const eased = 1 - Math.pow(1 - p, 4);
			el.textContent = fmt.format(target * eased);
			if (p < 1) requestAnimationFrame(tick);
		};
		requestAnimationFrame(tick);
	};
	if (counters.length) {
		if ("IntersectionObserver" in window) {
			const cio = new IntersectionObserver(
				(entries) =>
					entries.forEach((entry) => {
						if (!entry.isIntersecting) return;
						runCounter(entry.target);
						cio.unobserve(entry.target);
					}),
				{ threshold: 0.4 }
			);
			counters.forEach((el) => cio.observe(el));
		} else {
			counters.forEach(runCounter);
		}
	}

	/* Sliders (scroll-snap) ---------------------------------------------- */
	$$("[data-slider-controls]").forEach((controls) => {
		const track = $(`[data-slider="${controls.dataset.sliderControls}"]`);
		if (!track) return;
		const step = (dir) => {
			const card = track.firstElementChild;
			const amount = card ? card.getBoundingClientRect().width + 24 : track.clientWidth;
			track.scrollBy({ left: dir * amount * (isRtl() ? -1 : 1), behavior: reducedMotion ? "auto" : "smooth" });
		};
		$("[data-slider-prev]", controls).addEventListener("click", () => step(-1));
		$("[data-slider-next]", controls).addEventListener("click", () => step(1));
	});

	/* Client-side filters (e.g. case studies by industry) ---------------- */
	$$("[data-filter-group]").forEach((group) => {
		const target = $(group.dataset.filterGroup);
		if (!target) return;
		const buttons = $$("[data-filter]", group);
		buttons.forEach((btn) =>
			btn.addEventListener("click", () => {
				const value = btn.dataset.filter;
				buttons.forEach((b) => b.setAttribute("aria-pressed", b === btn ? "true" : "false"));
				$$("[data-industry]", target).forEach((item) => {
					item.hidden = Boolean(value) && item.dataset.industry !== value;
				});
			})
		);
	});

	/* Forms: async submit with inline errors ([data-lq-form]) ------------- */
	const params = new URLSearchParams(window.location.search);
	const t = (en) => en; // messages below are fallbacks; the server sends translated text
	$$("form[data-lq-form]").forEach((form) => {
		const set = (name, value) => {
			const input = form.elements.namedItem(name);
			if (input && "value" in input) input.value = value;
		};
		set("ts", String(Date.now()));
		set("page_url", window.location.pathname);
		["utm_source", "utm_medium", "utm_campaign"].forEach((k) => set(k, params.get(k) || ""));

		const formError = $("[data-form-error]", form);
		const button = $("[data-submit]", form);
		const spinner = $("[data-submit-spinner]", form);

		const clearErrors = () => {
			formError.hidden = true;
			$$("[data-error-for]", form).forEach((el) => {
				el.hidden = true;
				el.textContent = "";
			});
			$$("[aria-invalid]", form).forEach((el) => el.removeAttribute("aria-invalid"));
		};
		const showErrors = (errors) => {
			let first = null;
			Object.entries(errors).forEach(([name, message]) => {
				const slot = $(`[data-error-for="${CSS.escape(name)}"]`, form);
				const input = form.elements.namedItem(name);
				if (slot) {
					slot.textContent = message;
					slot.hidden = false;
				} else {
					formError.textContent = message;
					formError.hidden = false;
				}
				if (input && input.setAttribute) input.setAttribute("aria-invalid", "true");
				if (!first) first = input && input.focus ? input : formError;
			});
			if (first && first.focus) first.focus();
		};
		const busy = (on) => {
			button.disabled = on;
			form.setAttribute("aria-busy", on ? "true" : "false");
			if (spinner) spinner.classList.toggle("hidden", !on);
		};

		form.addEventListener("submit", async (e) => {
			e.preventDefault();
			clearErrors();
			busy(true);
			const data = new FormData(form);
			// multi-select checkboxes travel as one comma-separated value
			new Set($$("input[type=checkbox]", form).map((c) => c.name)).forEach((name) => {
				if (name === "consent") return;
				const values = data.getAll(name);
				data.delete(name);
				if (values.length) data.append(name, values.join(","));
			});
			data.set("csrf_token", (window.frappe && frappe.csrf_token) || "");
			try {
				const response = await fetch(form.action, {
					method: "POST",
					body: data,
					headers: { Accept: "application/json", "X-Requested-With": "XMLHttpRequest" },
					credentials: "same-origin",
				});
				const body = await response.json().catch(() => ({}));
				const result = body.message || {};
				if (response.ok && result.ok) {
					const success = $("[data-form-success]", form);
					$("[data-success-message]", success).textContent = result.message || "";
					success.hidden = false;
					success.focus();
					form.reset();
					if (window.dataLayer) window.dataLayer.push({ event: "lq_form_submit", form: form.action });
				} else if (response.status === 429) {
					showErrors({ _form: t("Too many submissions. Please try again later.") });
				} else if (result.errors && Object.keys(result.errors).length) {
					showErrors(result.errors);
				} else {
					showErrors({ _form: t("Something went wrong. Please try again or email us.") });
				}
			} catch (err) {
				showErrors({ _form: t("Network error. Please check your connection and try again.") });
			} finally {
				busy(false);
				if (window.turnstile) window.turnstile.reset();
			}
		});
	});

	/* Frappe compatibility: run callbacks queued with frappe.ready() ------ */
	if (window.frappe && Array.isArray(frappe.ready_events) && !window.frappe.call) {
		frappe.ready_events.forEach((fn) => {
			try {
				fn();
			} catch (e) {
				console.error(e);
			}
		});
	}
})();
