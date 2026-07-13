/**
 * WhiskyDB Enterprise Marketing Site - Interactive Logic Engine
 */

document.addEventListener("DOMContentLoaded", () => {
    initCatalogDemo();
    initPricingToggle();
    initCodeTabs();
    initSmoothScrolling();
});

/* ==========================================================================
   1. Interactive Catalog Live Demo
   ========================================================================== */
const MOCK_SPIRITS = [
    {
        id: 1,
        name: "Lagavulin 16 Year Old",
        category: "Single Malt Scotch",
        age: 16,
        abv: 43.0,
        volume: 700,
        distillery: "Lagavulin Distillery (Islay)",
        cask: "Ex-Bourbon & Second-Fill Sherry",
        caskTag: "Sherry",
        flavorTag: "Peat Smoke",
        priceUsd: 115.00,
        mashBill: { malt: 100, corn: 0, rye: 0, wheat: 0 }
    },
    {
        id: 2,
        name: "Pappy Van Winkle Family Reserve 15yo",
        category: "Bourbon",
        age: 15,
        abv: 53.5,
        volume: 750,
        distillery: "Old Rip Van Winkle / Buffalo Trace",
        cask: "New Charred American White Oak",
        caskTag: "Bourbon",
        flavorTag: "Vanilla",
        priceUsd: 2850.00,
        mashBill: { malt: 10, corn: 74, rye: 0, wheat: 16 }
    },
    {
        id: 3,
        name: "Yamazaki 12 Year Old",
        category: "Japanese Whisky",
        age: 12,
        abv: 43.0,
        volume: 700,
        distillery: "Yamazaki Distillery (Suntory)",
        cask: "Mizunara Oak, Ex-Bourbon & Sherry",
        caskTag: "Mizunara",
        flavorTag: "Dried Fruit",
        priceUsd: 195.00,
        mashBill: { malt: 100, corn: 0, rye: 0, wheat: 0 }
    },
    {
        id: 4,
        name: "The Macallan 18 Year Old Sherry Oak",
        category: "Single Malt Scotch",
        age: 18,
        abv: 43.0,
        volume: 700,
        distillery: "The Macallan Distillery (Speyside)",
        cask: "First-Fill Oloroso Sherry Seasoned Oak",
        caskTag: "Sherry",
        flavorTag: "Dried Fruit",
        priceUsd: 450.00,
        mashBill: { malt: 100, corn: 0, rye: 0, wheat: 0 }
    },
    {
        id: 5,
        name: "George T. Stagg Barrel Proof",
        category: "Bourbon",
        age: 15,
        abv: 65.1,
        volume: 750,
        distillery: "Buffalo Trace Distillery (Kentucky)",
        cask: "New Charred American White Oak (#4 Char)",
        caskTag: "Bourbon",
        flavorTag: "Vanilla",
        priceUsd: 1200.00,
        mashBill: { malt: 8, corn: 84, rye: 8, wheat: 0 }
    },
    {
        id: 6,
        name: "Laphroaig 10 Year Old Cask Strength",
        category: "Single Malt Scotch",
        age: 10,
        abv: 58.6,
        volume: 700,
        distillery: "Laphroaig Distillery (Islay)",
        cask: "First-Fill Ex-Bourbon Barrels",
        caskTag: "Bourbon",
        flavorTag: "Peat Smoke",
        priceUsd: 95.00,
        mashBill: { malt: 100, corn: 0, rye: 0, wheat: 0 }
    },
    {
        id: 7,
        name: "Hibiki 21 Year Old",
        category: "Japanese Whisky",
        age: 21,
        abv: 43.0,
        volume: 700,
        distillery: "Suntory (Yamazaki, Hakushu, Chita)",
        cask: "Mizunara Japanese Oak & Ex-Sherry Casks",
        caskTag: "Mizunara",
        flavorTag: "Vanilla",
        priceUsd: 1150.00,
        mashBill: { malt: 60, corn: 40, rye: 0, wheat: 0 }
    },
    {
        id: 8,
        name: "WhistlePig 15 Year Old Straight Rye",
        category: "Rye Whiskey",
        age: 15,
        abv: 46.0,
        volume: 750,
        distillery: "WhistlePig Farm Distillery (Vermont)",
        cask: "Ex-Bourbon & Vermont Estate Oak Finish",
        caskTag: "Bourbon",
        flavorTag: "Vanilla",
        priceUsd: 240.00,
        mashBill: { malt: 0, corn: 0, rye: 100, wheat: 0 }
    },
    {
        id: 9,
        name: "Springbank 10 Year Old",
        category: "Single Malt Scotch",
        age: 10,
        abv: 46.0,
        volume: 700,
        distillery: "Springbank Distillery (Campbeltown)",
        cask: "60% Ex-Bourbon & 40% Ex-Sherry Casks",
        caskTag: "Sherry",
        flavorTag: "Peat Smoke",
        priceUsd: 85.00,
        mashBill: { malt: 100, corn: 0, rye: 0, wheat: 0 }
    }
];

let currentFilters = {
    category: "all",
    minAge: 0,
    cask: "all",
    flavor: "all"
};

function initCatalogDemo() {
    const categorySelect = document.getElementById("filter-category");
    const ageSlider = document.getElementById("filter-age");
    const ageDisplay = document.getElementById("age-display");
    const caskContainer = document.getElementById("cask-filter-container");
    const flavorContainer = document.getElementById("flavor-filter-container");

    if (!categorySelect || !ageSlider) return;

    // Category filter
    categorySelect.addEventListener("change", (e) => {
        currentFilters.category = e.target.value;
        renderSpiritsGrid();
    });

    // Age slider filter
    ageSlider.addEventListener("input", (e) => {
        const val = parseInt(e.target.value, 10);
        currentFilters.minAge = val;
        ageDisplay.textContent = val === 0 ? "All Ages" : `${val}+ Years Old`;
        renderSpiritsGrid();
    });

    // Cask pills
    if (caskContainer) {
        caskContainer.addEventListener("click", (e) => {
            if (e.target.classList.contains("filter-pill")) {
                caskContainer.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
                e.target.classList.add("active");
                currentFilters.cask = e.target.getAttribute("data-cask");
                renderSpiritsGrid();
            }
        });
    }

    // Flavor pills
    if (flavorContainer) {
        flavorContainer.addEventListener("click", (e) => {
            if (e.target.classList.contains("filter-pill")) {
                flavorContainer.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
                e.target.classList.add("active");
                currentFilters.flavor = e.target.getAttribute("data-flavor");
                renderSpiritsGrid();
            }
        });
    }

    // Initial render
    renderSpiritsGrid();
}

function renderSpiritsGrid() {
    const container = document.getElementById("spirits-cards-container");
    const countDisplay = document.getElementById("result-count");
    if (!container) return;

    // Filter MOCK_SPIRITS
    const filtered = MOCK_SPIRITS.filter(item => {
        if (currentFilters.category !== "all" && item.category !== currentFilters.category) return false;
        if (item.age < currentFilters.minAge) return false;
        if (currentFilters.cask !== "all" && item.caskTag !== currentFilters.cask) return false;
        if (currentFilters.flavor !== "all" && item.flavorTag !== currentFilters.flavor) return false;
        return true;
    });

    // Update counter
    if (countDisplay) {
        countDisplay.textContent = filtered.length;
    }

    // Render HTML
    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="glass-card text-center" style="grid-column: 1 / -1; padding: 48px;">
                <h3 style="margin-bottom: 8px;">No matching spirit records found</h3>
                <p class="text-muted">Try relaxing your age statement slider or selecting 'All Casks'.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = filtered.map(bottle => {
        const { malt, corn, rye, wheat } = bottle.mashBill;
        return `
            <article class="spirit-card">
                <div class="card-top">
                    <span class="spirit-type-badge">${bottle.category}</span>
                    <span class="spirit-age">${bottle.age} YO</span>
                </div>
                <div>
                    <h3 class="spirit-name">${bottle.name}</h3>
                    <div class="spirit-distillery">${bottle.distillery}</div>
                </div>

                <!-- Mash Bill Visualizer -->
                <div>
                    <div class="mash-labels">
                        <span>Mash Bill Lineage</span>
                        <span>${malt > 0 ? `${malt}% Malt ` : ''}${corn > 0 ? `${corn}% Corn ` : ''}${rye > 0 ? `${rye}% Rye ` : ''}${wheat > 0 ? `${wheat}% Wheat` : ''}</span>
                    </div>
                    <div class="mash-bill-bar">
                        ${malt > 0 ? `<div class="mash-malt" style="width: ${malt}%" title="${malt}% Malted Barley"></div>` : ''}
                        ${corn > 0 ? `<div class="mash-corn" style="width: ${corn}%" title="${corn}% Corn"></div>` : ''}
                        ${rye > 0 ? `<div class="mash-rye" style="width: ${rye}%" title="${rye}% Rye"></div>` : ''}
                        ${wheat > 0 ? `<div class="mash-wheat" style="width: ${wheat}%" title="${wheat}% Wheat"></div>` : ''}
                    </div>
                </div>

                <div class="card-meta-row">
                    <div class="meta-item">
                        <span class="text-dim">ABV</span>
                        <span class="meta-val">${bottle.abv.toFixed(1)}%</span>
                    </div>
                    <div class="meta-item">
                        <span class="text-dim">Volume</span>
                        <span class="meta-val">${bottle.volume} mL</span>
                    </div>
                    <div class="meta-item">
                        <span class="text-dim">Flavor Profile</span>
                        <span class="meta-val text-gold">${bottle.flavorTag}</span>
                    </div>
                </div>

                <div class="card-footer">
                    <div>
                        <div class="text-dim" style="font-size: 0.75rem;">Secondary Benchmark</div>
                        <div class="price-val-card">$${bottle.priceUsd.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} USD</div>
                    </div>
                    <span class="cask-tag">${bottle.cask}</span>
                </div>
            </article>
        `;
    }).join('');
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
            el.innerHTML = `$${val} <span class="price-period">/ month</span>`;
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
            copyText.textContent = "✓ Copied!";
            copyBtn.style.borderColor = "#22c55e";
            copyBtn.style.color = "#22c55e";

            setTimeout(() => {
                copyText.textContent = "Copy Code";
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
            submitBtn.querySelector("span").textContent = "Sending…";
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
                
                // Launch pre-filled email client directly so lead is never lost to Cloudflare 522
                const subject = encodeURIComponent("New WhiskyDB Dataset Request - " + name);
                const bodyText = `Name / Organization: ${name}\nDelivery Email: ${email}\nLicense Tier: ${tier}\nIntended Use Case: ${useCase}\n\n[Sent via WhiskyDB High-Availability Form Fallback]`;
                const mailtoUrl = `mailto:whiskeydn.kite979@simplelogin.com?subject=${subject}&body=${encodeURIComponent(bodyText)}`;
                window.location.href = mailtoUrl;

                // Show success UI along with explanatory toast so user knows email client opened
                contactForm.style.display = "none";
                const successEl = document.getElementById("contactSuccess");
                if (successEl) {
                    successEl.style.display = "block";
                    const titleEl = successEl.querySelector(".contact-success-title");
                    if (titleEl) titleEl.textContent = "✦ Email Client Opened (Direct Fallback)";
                }
            })
            .finally(function () {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.querySelector("span").textContent = "Request Dataset Access →";
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
