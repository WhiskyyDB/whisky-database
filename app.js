/**
 * WhiskyDB Enterprise Marketing Site - Interactive Logic Engine
 */

// Runtime UI strings live in the page's #i18n-strings table so localized copies of the
// page (/es/, /de/, …) ship them translated (see scripts/i18n_common.py).
const I18N = JSON.parse(document.getElementById("i18n-strings").textContent);

document.addEventListener("DOMContentLoaded", () => {
    initSampleExplorer();
    initPricingToggle();
    initCodeTabs();
    initSmoothScrolling();
});

/* ==========================================================================
   1. Free-sample explorer
   The cards are the rows of samples/spirits.csv, the free sample this site publishes, read
   as they are: no spirit, figure or price is typed into this file. WhiskyDB holds no bottle
   prices. A card shows an auction figure only for a bottling that the full dataset links to
   a distillery of the public auction index (stats/data.json), labelled as that distillery's
   yearly mean winning bid, never as a price for the bottle.
   ========================================================================== */
const SAMPLE_CSV = "/samples/spirits.csv";
const STATS_JSON = "/stats/data.json";
const SAMPLE_ON_GITHUB = "https://github.com/WhiskyyDB/whisky-database/blob/main/samples/spirits.csv";
// spirit_id -> the distillery whose WhiskyHunter monthly index the full dataset's
// price_benchmarks rows repeat for that bottling (checked against the 2026.09 edition).
const AUCTION_DISTILLERY = {
    "1": "Lagavulin",
    "3": "Yamazaki",
    "4": "Woodford Reserve",
    "8": "Jack Daniel's",
    "13": "Jack Daniel's"
};
const PAGE_LANG = document.documentElement.lang || "en";
// Spirit pages exist under /<lang>/spirits/ for every localized copy of this page.
const LOCALE_PREFIX = /^en\b/i.test(PAGE_LANG) ? "" : "/" + PAGE_LANG.toLowerCase();

let sampleRows = [];
// "loading" | "ok" | "error". The filters are live before the sample arrives; until it has
// loaded they only record their value, so a failed load keeps its message and GitHub link
// instead of turning into "no matching records".
let sampleState = "loading";
let auctionIndex = null;  // { year, byDistillery: { name: GBP } }; null when stats/data.json is unavailable
const currentFilters = { type: "all", minAge: 0, source: "all", size: "all" };

function initSampleExplorer() {
    const container = document.getElementById("spirits-cards-container");
    if (!container) return;
    bindFilters();

    const sample = fetch(SAMPLE_CSV).then(res => {
        if (!res.ok) throw new Error(`${SAMPLE_CSV}: HTTP ${res.status}`);
        return res.text();
    });
    const stats = fetch(STATS_JSON).then(res => (res.ok ? res.json() : null)).catch(() => null);

    Promise.all([sample, stats]).then(([csvText, statsData]) => {
        sampleRows = parseCsv(csvText);
        auctionIndex = readAuctionIndex(statsData);
        fillTypeOptions();
        const total = document.getElementById("sample-total");
        if (total) total.textContent = formatNumber(sampleRows.length);
        sampleState = "ok";
        renderSpiritsGrid();
    }).catch(err => {
        sampleState = "error";
        console.warn("WhiskyDB free sample could not be loaded:", err);
        const countDisplay = document.getElementById("result-count");
        if (countDisplay) countDisplay.textContent = formatNumber(0);
        container.innerHTML = `
            <div class="glass-card text-center" style="grid-column: 1 / -1; padding: 48px;">
                <p class="text-muted">${I18N.load_error} <a href="${SAMPLE_ON_GITHUB}" target="_blank" rel="noopener" style="text-decoration: underline;" translate="no">samples/spirits.csv</a></p>
            </div>
        `;
    }).finally(() => {
        // The cards render above #features-section and the later sections: land a #fragment
        // arrival on its section again (shared snippet, scripts/section_links.py).
        if (window.realignSectionLink) window.realignSectionLink();
    });
}

/* RFC 4180 CSV (quoted fields may hold commas, quotes and line breaks) -> array of row objects. */
function parseCsv(text) {
    const rows = [];
    let row = [];
    let field = "";
    let quoted = false;
    for (let i = 0; i < text.length; i++) {
        const ch = text[i];
        if (quoted) {
            if (ch === '"' && text[i + 1] === '"') { field += '"'; i++; }
            else if (ch === '"') quoted = false;
            else field += ch;
        } else if (ch === '"') {
            quoted = true;
        } else if (ch === ",") {
            row.push(field);
            field = "";
        } else if (ch === "\n" || ch === "\r") {
            if (ch === "\r" && text[i + 1] === "\n") i++;
            row.push(field);
            field = "";
            if (row.some(v => v !== "")) rows.push(row);
            row = [];
        } else {
            field += ch;
        }
    }
    row.push(field);
    if (row.some(v => v !== "")) rows.push(row);
    const header = (rows.shift() || []).map(h => h.replace(/^﻿/, "").trim());
    return rows.map(r => Object.fromEntries(header.map((h, j) => [h, r[j] === undefined ? "" : r[j]])));
}

/* The per-distillery yearly means of the public auction index, keyed by distillery name. */
function readAuctionIndex(data) {
    const index = data && data.auction_index_gbp;
    if (!index || !Array.isArray(index.per_distillery) || !Array.isArray(index.years) || !index.years.length) return null;
    const byDistillery = {};
    index.per_distillery.forEach(d => {
        if (d && typeof d.latest_gbp === "number") byDistillery[d.distillery] = d.latest_gbp;
    });
    const year = Array.isArray(index.decade) ? index.decade[1] : index.years[index.years.length - 1].year;
    return { year, byDistillery };
}

function fillTypeOptions() {
    const select = document.getElementById("filter-category");
    if (!select) return;
    const counts = {};
    sampleRows.forEach(row => { counts[row.type] = (counts[row.type] || 0) + 1; });
    Object.keys(counts).sort((a, b) => counts[b] - counts[a] || a.localeCompare(b)).forEach(type => {
        const option = document.createElement("option");
        option.value = type;
        option.textContent = type;
        option.setAttribute("translate", "no");
        select.appendChild(option);
    });
}

function bindFilters() {
    const typeSelect = document.getElementById("filter-category");
    const ageSlider = document.getElementById("filter-age");
    const ageDisplay = document.getElementById("age-display");

    if (typeSelect) {
        typeSelect.addEventListener("change", (e) => {
            currentFilters.type = e.target.value;
            renderSpiritsGrid();
        });
    }
    if (ageSlider) {
        ageSlider.addEventListener("input", (e) => {
            const val = parseInt(e.target.value, 10);
            currentFilters.minAge = val;
            if (ageDisplay) ageDisplay.textContent = val === 0 ? I18N.all_ages : `${val}${I18N.years_old_suffix}`;
            renderSpiritsGrid();
        });
    }
    bindPills("source-filter-container", "source");
    bindPills("size-filter-container", "size");
}

function bindPills(containerId, key) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const pills = container.querySelectorAll(".filter-pill");
    pills.forEach(p => p.setAttribute("aria-pressed", String(p.classList.contains("active"))));
    container.addEventListener("click", (e) => {
        const pill = e.target.closest(".filter-pill");
        if (!pill || !container.contains(pill)) return;
        pills.forEach(p => {
            p.classList.toggle("active", p === pill);
            p.setAttribute("aria-pressed", String(p === pill));
        });
        currentFilters[key] = pill.getAttribute(`data-${key}`);
        renderSpiritsGrid();
    });
}

function sourceKind(row) {
    if (/^WhiskyDB Curated Seed/.test(row.source_name)) return "seed";
    if (/Open Food Facts/.test(row.source_name)) return "off";
    return "other";
}

function formatNumber(value, options) {
    try {
        return new Intl.NumberFormat(PAGE_LANG, options).format(value);
    } catch (e) {
        return String(value);
    }
}

// The auction index is in GBP; the narrow symbol reads "£" in every page language.
function formatGbp(value) {
    for (const options of [{ currencyDisplay: "narrowSymbol" }, {}]) {
        try {
            return new Intl.NumberFormat(PAGE_LANG, { style: "currency", currency: "GBP", ...options }).format(value);
        } catch (e) { /* older engines: try the next form */ }
    }
    return `£${Number(value).toFixed(2)}`;
}

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}

// Same rule as slugify() in scripts/generate_seo_pages.py, which writes the /spirits/ pages.
function slugify(text) {
    return text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

function renderSpiritsGrid() {
    const container = document.getElementById("spirits-cards-container");
    const countDisplay = document.getElementById("result-count");
    if (!container) return;
    if (sampleState !== "ok") return;  // loading: the load renders with the current filters; error: keep the message

    const filtered = sampleRows.filter(row => {
        const age = parseFloat(row.age);
        if (currentFilters.type !== "all" && row.type !== currentFilters.type) return false;
        if (currentFilters.minAge > 0 && !(age >= currentFilters.minAge)) return false;  // an empty age (NAS or unstated) never passes
        if (currentFilters.source !== "all" && sourceKind(row) !== currentFilters.source) return false;
        if (currentFilters.size !== "all" && String(parseInt(row.volume_ml, 10)) !== currentFilters.size) return false;
        return true;
    });

    if (countDisplay) countDisplay.textContent = formatNumber(filtered.length);

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="glass-card text-center" style="grid-column: 1 / -1; padding: 48px;">
                <h3 style="margin-bottom: 8px;">${I18N.empty_title}</h3>
                <p class="text-muted">${I18N.empty_text}</p>
            </div>
        `;
        return;
    }
    container.innerHTML = filtered.map(renderCard).join("");
}

function renderCard(row) {
    const age = parseFloat(row.age);
    const abv = parseFloat(row.abv);
    const volume = parseInt(row.volume_ml, 10);
    const ageText = age > 0 ? `${formatNumber(age)} ${I18N.age_abbrev}` : I18N.no_age;
    const distillery = AUCTION_DISTILLERY[row.spirit_id];
    const gbp = auctionIndex && distillery ? auctionIndex.byDistillery[distillery] : undefined;
    const auction = gbp === undefined ? "<div></div>" : `
                    <div>
                        <div class="text-dim" style="font-size: 0.75rem;">${I18N.auction_label} · <span translate="no">${escapeHtml(distillery)}</span></div>
                        <div class="price-val-card">${formatGbp(gbp)}</div>
                        <div class="text-dim" style="font-size: 0.72rem;">${escapeHtml(auctionIndex.year)} · ${I18N.auction_scope}</div>
                    </div>`;
    return `
            <article class="spirit-card">
                <div class="card-top">
                    <span class="spirit-type-badge" translate="no">${escapeHtml(row.type)}</span>
                    <span class="spirit-age">${escapeHtml(ageText)}</span>
                </div>
                <div>
                    <h3 class="spirit-name"><a href="${LOCALE_PREFIX}/spirits/${slugify(row.name)}" translate="no">${escapeHtml(row.name)}</a></h3>
                    <div class="spirit-distillery">${I18N.source_prefix} <span translate="no">${escapeHtml(row.source_name)}</span></div>
                </div>

                <div class="card-meta-row">
                    <div class="meta-item">
                        <span class="text-dim">${I18N.abv}</span>
                        <span class="meta-val">${Number.isFinite(abv) ? formatNumber(abv / 100, { style: "percent", minimumFractionDigits: 1, maximumFractionDigits: 1 }) : "—"}</span>
                    </div>
                    <div class="meta-item">
                        <span class="text-dim">${I18N.volume}</span>
                        <span class="meta-val">${Number.isFinite(volume) ? `${formatNumber(volume)} mL` : "—"}</span>
                    </div>
                </div>

                <div class="card-footer">${auction}
                    <a class="cask-tag" href="${escapeHtml(row.source_url)}" target="_blank" rel="noopener nofollow">${I18N.provenance_link}</a>
                </div>
            </article>
        `;
}

/* ==========================================================================
   2. Interactive Pricing Toggle (Monthly vs Annual)
   ========================================================================== */
function initPricingToggle() {
    const toggleBtn = document.getElementById("pricing-toggle-btn");
    const labelMonthly = document.getElementById("label-monthly");
    const labelAnnual = document.getElementById("label-annual");
    const priceElements = document.querySelectorAll(".price-val[data-monthly]");

    if (!toggleBtn) return;

    toggleBtn.addEventListener("change", () => {
        const isAnnual = toggleBtn.checked;
        if (isAnnual) {
            labelAnnual.classList.add("active");
            labelMonthly.classList.remove("active");
        } else {
            labelMonthly.classList.add("active");
            labelAnnual.classList.remove("active");
        }

        priceElements.forEach(el => {
            const val = isAnnual ? el.getAttribute("data-annual") : el.getAttribute("data-monthly");
            el.innerHTML = `$${val} <span class="price-period">${I18N.per_month}</span>`;
        });
    });
}

/* ==========================================================================
   3. Interactive Code Tabs & Clipboard Copy
   ========================================================================== */
function initCodeTabs() {
    const tabs = document.querySelectorAll(".code-tab");
    const panes = document.querySelectorAll(".code-pane");
    const copyBtn = document.getElementById("copy-code-btn");
    const copyText = document.getElementById("copy-text");

    if (!tabs.length || !copyBtn) return;

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const targetId = `pane-${tab.getAttribute("data-tab")}`;
            
            tabs.forEach(t => t.classList.remove("active"));
            panes.forEach(p => p.classList.remove("active"));
            
            tab.classList.add("active");
            const targetPane = document.getElementById(targetId);
            if (targetPane) targetPane.classList.add("active");
        });
    });

    copyBtn.addEventListener("click", () => {
        const activePane = document.querySelector(".code-pane.active code");
        if (!activePane) return;

        const textToCopy = activePane.innerText || activePane.textContent;
        navigator.clipboard.writeText(textToCopy).then(() => {
            copyText.textContent = I18N.copied;
            copyBtn.style.borderColor = "#22c55e";
            copyBtn.style.color = "#22c55e";

            setTimeout(() => {
                copyText.textContent = I18N.copy_code;
                copyBtn.style.borderColor = "";
                copyBtn.style.color = "";
            }, 2000);
        }).catch(err => {
            console.error("Failed to copy code: ", err);
        });
    });
}

/* ==========================================================================
   4. Smooth Scrolling for Anchor Links
   ========================================================================== */
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/* ==========================================================================
   Contact form: High-Availability AJAX submit with 7s timeout & mailto fallback
   ========================================================================== */
const contactForm = document.getElementById("contactForm");
if (contactForm) {
    contactForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const submitBtn = document.getElementById("contact-submit-btn");
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.querySelector("span").textContent = I18N.sending;
        }

        const name = document.getElementById("userName").value.trim();
        const email = document.getElementById("userEmail").value.trim();
        const tier = document.getElementById("tierSelect").value;
        const useCase = document.getElementById("useCase").value.trim();

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 7000);

        fetch("https://api.web3forms.com/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json", "Accept": "application/json" },
            body: JSON.stringify({
                access_key: "bf34ff48-fcc6-4823-b386-9ae3d0712797",
                subject: "New WhiskyDB Dataset Request",
                from_name: "WhiskyDB Contact Form",
                name: name,
                email: email,
                tier: tier,
                use_case: useCase
            }),
            signal: controller.signal
        })
            .then(function (resp) {
                clearTimeout(timeoutId);
                if (!resp.ok) throw new Error("Web3Forms server error or CORS blocked");
                return resp.json();
            })
            .then(function (data) {
                if (!data || data.success !== true) throw new Error("Web3Forms did not confirm delivery");
                contactForm.style.display = "none";
                document.getElementById("contactSuccess").style.display = "block";
            })
            .catch(function (err) {
                clearTimeout(timeoutId);
                console.warn("AJAX form submit failed or timed out. Triggering direct mailto client fallback:", err);

                // Show success UI along with explanatory toast so user knows email client opened
                contactForm.style.display = "none";
                const successEl = document.getElementById("contactSuccess");
                if (successEl) {
                    successEl.style.display = "block";
                    const titleEl = successEl.querySelector(".contact-success-title");
                    if (titleEl) titleEl.textContent = I18N.fail_title;
                    const noteEl = successEl.querySelector("p");
                    if (noteEl) noteEl.textContent = I18N.fail_note;
                }
            })
            .finally(function () {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.querySelector("span").textContent = I18N.submit;
                }
            });
    });
}

function resetContactForm() {
    const form = document.getElementById("contactForm");
    form.reset();
    form.style.display = "flex";
    document.getElementById("contactSuccess").style.display = "none";
}
