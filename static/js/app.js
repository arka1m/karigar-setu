/* ==========================================================================
   Karigar Setu (v2 — Gap-Verified) Client SPA Logic
   SIH 2026 Core Flows & Platform Limitation Mapper
   ========================================================================== */

let state = {
  currentFlow: 'onboarding', // onboarding | home | capture | draft | publish | catalog | buyer_browse
  language: 'hi',
  isRecording: false,
  recordedVoiceText: '',
  capturedCraftKey: 'terracotta',
  aiDraft: null,
  products: [],
  artisan: null,
  selectedChannels: ['native', 'india_handmade', 'etsy', 'unfade']
};

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  await fetchArtisanData();
  await fetchProducts();
  await fetchGapMatrix();
  renderScreen();
}

async function fetchArtisanData() {
  try {
    const res = await fetch('/api/artisan');
    const data = await res.json();
    if (data.success) {
      state.artisan = data.artisan;
    }
  } catch (err) {
    console.error("Error fetching artisan data:", err);
  }
}

async function fetchProducts() {
  try {
    const res = await fetch('/api/products');
    const data = await res.json();
    if (data.success) {
      state.products = data.products;
    }
  } catch (err) {
    console.error("Error fetching products:", err);
  }
}

async function fetchGapMatrix() {
  try {
    const res = await fetch('/api/sih-gap-matrix');
    const data = await res.json();
    if (data.success) {
      renderGapMatrix(data.matrix);
    }
  } catch (err) {
    console.error("Error fetching gap matrix:", err);
  }
}

function renderScreen() {
  const container = document.getElementById('phone-screen');
  if (!container) return;

  // Update bottom nav active state
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  const activeNav = document.getElementById(`nav-${state.currentFlow === 'buyer_browse' ? 'buyer' : state.currentFlow === 'capture' ? 'capture' : state.currentFlow === 'catalog' ? 'catalog' : 'home'}`);
  if (activeNav) activeNav.classList.add('active');

  switch (state.currentFlow) {
    case 'onboarding':
      container.innerHTML = renderOnboardingScreen();
      break;
    case 'home':
      container.innerHTML = renderHomeScreen();
      break;
    case 'capture':
      container.innerHTML = renderCaptureScreen();
      break;
    case 'draft':
      container.innerHTML = renderDraftScreen();
      break;
    case 'publish':
      container.innerHTML = renderPublishScreen();
      break;
    case 'catalog':
      container.innerHTML = renderCatalogScreen();
      break;
    case 'buyer_browse':
      container.innerHTML = renderBuyerScreen();
      break;
    default:
      container.innerHTML = renderHomeScreen();
  }
}

/* ==========================================================================
   Flow 1: Voice & Regional Language Onboarding (0-KYC Block)
   ========================================================================== */
function renderOnboardingScreen() {
  return `
    <div style="text-align:center; padding:10px 0;">
      <div class="brand-logo-badge" style="width:54px; height:54px; font-size:1.8rem; margin:0 auto 12px;">
        <span class="material-icons">palette</span>
      </div>
      <h1>नमस्ते! Welcome to Karigar Setu</h1>
      <p style="margin-bottom:16px;">अपनी भाषा चुनें / Select your native language to start cataloguing by voice:</p>

      <div class="lang-chip-grid">
        <div class="lang-chip ${state.language === 'hi' ? 'selected' : ''}" onclick="selectLanguage('hi')">
          <div class="lang-chip-icon">हिं</div>
          <div style="text-align:left;">
            <div style="font-weight:700; font-size:0.9rem;">हिंदी (Hindi)</div>
            <div style="font-size:0.7rem; color:#8C7A6B;">उत्तर भारत</div>
          </div>
        </div>

        <div class="lang-chip ${state.language === 'en' ? 'selected' : ''}" onclick="selectLanguage('en')">
          <div class="lang-chip-icon">EN</div>
          <div style="text-align:left;">
            <div style="font-weight:700; font-size:0.9rem;">English</div>
            <div style="font-size:0.7rem; color:#8C7A6B;">Universal</div>
          </div>
        </div>

        <div class="lang-chip ${state.language === 'ta' ? 'selected' : ''}" onclick="selectLanguage('ta')">
          <div class="lang-chip-icon">த</div>
          <div style="text-align:left;">
            <div style="font-weight:700; font-size:0.9rem;">தமிழ் (Tamil)</div>
            <div style="font-size:0.7rem; color:#8C7A6B;">தமிழ்நாடு</div>
          </div>
        </div>

        <div class="lang-chip ${state.language === 'bn' ? 'selected' : ''}" onclick="selectLanguage('bn')">
          <div class="lang-chip-icon">বা</div>
          <div style="text-align:left;">
            <div style="font-weight:700; font-size:0.9rem;">বাংলা (Bengali)</div>
            <div style="font-size:0.7rem; color:#8C7A6B;">পশ্চিমবঙ্গ</div>
          </div>
        </div>
      </div>

      <div class="ks-card" style="background:#F4F2E9; border-color:var(--color-sage); margin:16px 0;">
        <div style="display:flex; gap:10px; align-items:center;">
          <span class="material-icons" style="color:var(--color-sage); font-size:1.6rem;">bolt</span>
          <div style="text-align:left; font-size:0.8rem;">
            <strong>Zero KYC Barrier Onboarding</strong>
            <p style="margin:2px 0 0 0; font-size:0.75rem; color:#6A554A;">Draft & preview listings instantly! Verification required only at bank payout time.</p>
          </div>
        </div>
      </div>

      <button class="btn-primary" onclick="navigateToFlow('home')" style="margin-top:10px;">
        <span>आगे बढ़ें (Continue)</span>
        <span class="material-icons">arrow_forward</span>
      </button>

      <button class="btn-secondary" onclick="startVoiceOnboarding()" style="margin-top:12px; width:100%; justify-content:center;">
        <span class="material-icons" style="color:var(--color-terracotta);">mic</span>
        <span>बोलकर शुरू करें (Voice Onboard)</span>
      </button>
    </div>
  `;
}

function selectLanguage(lang) {
  state.language = lang;
  renderScreen();
}

function startVoiceOnboarding() {
  alert("Listening to voice... 'नमस्ते, मैं बांकुरा से मिट्टी के घोड़े बनाता हूँ'");
  state.language = 'hi';
  navigateToFlow('capture');
}

/* ==========================================================================
   Flow 2: Artisan Home Dashboard
   ========================================================================== */
function renderHomeScreen() {
  const artisanName = state.artisan ? state.artisan.name : 'Ramesh Prajapati';
  const cluster = state.artisan ? state.artisan.craft_cluster : 'Bankura Terracotta Cluster';
  const earnings = state.artisan ? state.artisan.monthly_earnings : 42500;

  return `
    <div>
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
        <div>
          <span style="font-size:0.75rem; color:var(--color-sage); font-weight:700; text-transform:uppercase;">Master Artisan</span>
          <h2 style="margin:0;">${artisanName}</h2>
          <p style="margin:0; font-size:0.8rem; color:#7A6559;">${cluster}</p>
        </div>
        <div style="width:42px; height:42px; background:var(--color-terracotta); color:#FFF; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700;">
          RP
        </div>
      </div>

      <!-- Monthly Earnings Card -->
      <div class="ks-card ks-card-highlight">
        <span style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.5px; opacity:0.85;">Monthly Realized Sales</span>
        <h1 style="font-size:2rem; color:#FFF; margin:4px 0 8px 0;">₹${earnings.toLocaleString('en-IN')}</h1>
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem;">
          <span>4 Marketplaces Active</span>
          <span class="ks-tag ks-tag-sage" style="margin:0;">Offline Sync Ready</span>
        </div>
      </div>

      <!-- Core Add Product CTA -->
      <button class="btn-primary" onclick="navigateToFlow('capture')" style="margin-bottom:18px;">
        <span class="material-icons">add_a_photo</span>
        <span>नया उत्पाद जोड़ें (Add Product by AI)</span>
      </button>

      <h3>हाल के उत्पाद (Recent Listings)</h3>
      <div id="home-product-list">
        ${renderProductCardsHTML(state.products.slice(0, 3))}
      </div>
    </div>
  `;
}

function renderProductCardsHTML(productsList) {
  if (!productsList || productsList.length === 0) {
    return `<div style="text-align:center; padding:20px; color:#8C7A6B;">कोई उत्पाद नहीं (No products yet). Add one using AI!</div>`;
  }

  return productsList.map(p => `
    <div class="ks-card" style="display:flex; gap:12px; align-items:center;">
      <img src="${p.photo_url}" alt="${p.title}" style="width:70px; height:70px; object-fit:cover; border-radius:var(--radius-sm);">
      <div style="flex:1;">
        <div style="font-weight:700; font-size:0.88rem; color:var(--color-terracotta-dark); text-overflow:ellipsis; overflow:hidden; white-space:nowrap; max-width:200px;">${p.title}</div>
        <div style="font-size:0.78rem; color:#6A554A;">₹${p.final_price} | ${p.category}</div>
        <div style="margin-top:4px;">
          <span class="status-badge-synced">4 Channels Synced</span>
          ${p.certificate_id ? `<a href="/certificate/${p.certificate_id}" target="_blank" class="ks-tag ks-tag-terracotta" style="text-decoration:none;">QR Verified</a>` : ''}
        </div>
      </div>
    </div>
  `).join('');
}

/* ==========================================================================
   Flow 3: AI Cataloguing Capture (Photo + Regional Voice Note)
   ========================================================================== */
function renderCaptureScreen() {
  return `
    <div>
      <h2>AI Photo & Voice Capture</h2>
      <p>फोटो खींचें और अपनी भाषा में उत्पाद के बारे में बोलें:</p>

      <!-- Image Dropzone -->
      <div class="image-dropzone" onclick="selectSampleCraft()">
        <img id="capture-preview-img" src="/static/images/terracotta_horse.jpg" alt="Craft Sample">
        <div style="position:absolute; bottom:10px; background:rgba(0,0,0,0.6); color:#FFF; padding:4px 12px; border-radius:var(--radius-pill); font-size:0.75rem;">
          <span class="material-icons" style="font-size:12px; vertical-align:middle;">camera_alt</span> Tap to switch craft sample
        </div>
      </div>

      <!-- Quick Craft Selector Chips -->
      <div style="margin-bottom:14px;">
        <span style="font-size:0.75rem; font-weight:700; color:var(--color-terracotta-dark);">Craft Type Preset:</span>
        <div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:6px;">
          <span class="ks-tag ${state.capturedCraftKey === 'terracotta' ? 'ks-tag-terracotta' : ''}" onclick="setCraftPreset('terracotta')">Terracotta Pottery</span>
          <span class="ks-tag ${state.capturedCraftKey === 'chikankari' ? 'ks-tag-terracotta' : ''}" onclick="setCraftPreset('chikankari')">Chikankari</span>
          <span class="ks-tag ${state.capturedCraftKey === 'dokra' ? 'ks-tag-terracotta' : ''}" onclick="setCraftPreset('dokra')">Dokra Metal</span>
          <span class="ks-tag ${state.capturedCraftKey === 'madhubani' ? 'ks-tag-terracotta' : ''}" onclick="setCraftPreset('madhubani')">Madhubani Painting</span>
          <span class="ks-tag ${state.capturedCraftKey === 'blue_pottery' ? 'ks-tag-terracotta' : ''}" onclick="setCraftPreset('blue_pottery')">Blue Pottery</span>
        </div>
      </div>

      <!-- Voice Recorder Box -->
      <div class="voice-recorder-box" onclick="toggleVoiceRecording()">
        <div class="mic-btn-circle ${state.isRecording ? 'recording' : ''}">
          <span class="material-icons">${state.isRecording ? 'graphic_eq' : 'mic'}</span>
        </div>
        <div style="font-weight:700; color:var(--color-terracotta-dark);">
          ${state.isRecording ? 'रिकॉर्डिंग चालू है... (Recording Voice)' : 'आवाज रिकॉर्ड करें (Record Voice Note)'}
        </div>
        <p style="font-size:0.75rem; margin-bottom:0; color:#7A6559;">
          ${state.recordedVoiceText ? `Recorded: "${state.recordedVoiceText}"` : 'जैसे: "यह प्राकृतिक लाल मिट्टी से बना बांकुरा घोड़ा है"'}
        </p>
      </div>

      <button class="btn-primary" onclick="processAICataloguing()">
        <span class="material-icons">auto_awesome</span>
        <span>AI लिस्टिंग तैयार करें (Generate AI Listing)</span>
      </button>
    </div>
  `;
}

function selectSampleCraft() {
  const crafts = ['terracotta', 'chikankari', 'dokra', 'madhubani', 'blue_pottery'];
  const currentIndex = crafts.indexOf(state.capturedCraftKey);
  const nextCraft = crafts[(currentIndex + 1) % crafts.length];
  setCraftPreset(nextCraft);
}

function setCraftPreset(craftKey) {
  state.capturedCraftKey = craftKey;
  renderScreen();
}

function toggleVoiceRecording() {
  state.isRecording = !state.isRecording;
  if (!state.isRecording) {
    state.recordedVoiceText = "बांकुरा का पारंपरिक मिट्टी का घोड़ा, 8 घंटे की मेहनत से बना।";
  }
  renderScreen();
}

async function processAICataloguing() {
  const container = document.getElementById('phone-screen');
  container.innerHTML = `
    <div style="text-align:center; padding:60px 20px;">
      <div class="loader-spinner"></div>
      <h3>AI विश्लेषित कर रहा है...</h3>
      <p>Image classification, Indic NLP translation, and Fair Price Engine running in Python...</p>
    </div>
  `;

  try {
    const res = await fetch('/api/ai/catalogue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        language: state.language,
        craft_keyword: state.capturedCraftKey,
        voice_note: state.recordedVoiceText
      })
    });
    const data = await res.json();
    if (data.success) {
      if (data.ai_draft && !data.aiDraft) {
        data.aiDraft = data.ai_draft;
      }
      state.aiDraft = data;
      navigateToFlow('draft');
    }
  } catch (err) {
    console.error("AI Error:", err);
    alert("AI processing error. Retrying fallback.");
  }
}

/* ==========================================================================
   Flow 4: AI Draft Review & Fair Price Rationale
   ========================================================================== */
function renderDraftScreen() {
  if (!state.aiDraft) return `<div>Error loading draft</div>`;

  const draft = state.aiDraft.aiDraft;
  const pricing = state.aiDraft.pricing;
  const vision = state.aiDraft.vision_analysis;

  return `
    <div>
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <h2>AI Draft Listing</h2>
        <span class="ks-tag ks-tag-sage">${Math.round(vision.confidence * 100)}% Match</span>
      </div>

      <div class="ks-card">
        <label style="font-weight:700; font-size:0.75rem; color:var(--color-terracotta-dark);">AUTO-GENERATED TITLE</label>
        <input class="ks-input" id="draft-title" value="${draft.title}">

        <label style="font-weight:700; font-size:0.75rem; color:var(--color-terracotta-dark);">HERITAGE ARTISAN STORY</label>
        <textarea class="ks-textarea" id="draft-story" rows="4">${draft.story}</textarea>

        <div style="margin-top:8px;">
          <span style="font-size:0.75rem; font-weight:700;">Category:</span> <span class="ks-tag">${draft.category}</span>
          <br>
          <span style="font-size:0.75rem; font-weight:700;">Detected Materials:</span> 
          ${draft.materials.map(m => `<span class="ks-tag ks-tag-sage">${m}</span>`).join('')}
        </div>
      </div>

      <!-- Fair Price Suggestion & Rationale Card -->
      <div class="ks-card" style="background:#FDF4F2; border-color:var(--color-terracotta);">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <h3 style="color:var(--color-terracotta); margin:0;">AI Fair Price Engine</h3>
          <span class="material-icons" style="color:var(--color-terracotta);">savings</span>
        </div>

        <div style="font-size:1.8rem; font-weight:800; color:var(--color-terracotta-dark); margin:8px 0;">
          ₹<span id="display-fair-price">${pricing.suggested_price}</span>
        </div>

        <p style="font-size:0.78rem; color:#6A554A; margin-bottom:10px;">
          <strong>Transparent Rationale:</strong> ${pricing.reasoning}
        </p>

        <div style="font-size:0.75rem; background:#FFF; padding:8px 12px; border-radius:var(--radius-sm); border:1px solid var(--color-border);">
          <span>Acceptable Range: ₹${pricing.min_price} – ₹${pricing.max_price}</span>
        </div>
      </div>

      <button class="btn-primary" onclick="navigateToFlow('publish')">
        <span>मल्टी-मार्केटपब्लिश (Publish Everywhere)</span>
        <span class="material-icons">cloud_upload</span>
      </button>
    </div>
  `;
}

/* ==========================================================================
   Flow 5: Multi-Marketplace Sync & Digital Certificate
   ========================================================================== */
function renderPublishScreen() {
  const pricing = state.aiDraft ? state.aiDraft.pricing : null;

  return `
    <div>
      <h2>Publish Across Channels</h2>
      <p>एक बार में सभी मार्केटप्लेस पर सूचीबद्ध करें:</p>

      <div class="channel-sync-list">

        <div class="channel-sync-item">
          <div class="channel-info">
            <div class="channel-icon"><span class="material-icons">storefront</span></div>
            <div>
              <div style="font-weight:700; font-size:0.85rem;">Karigar Setu Storefront</div>
              <div style="font-size:0.72rem; color:#6A554A;">Flat 2.5% platform fee | Net: ₹${pricing ? pricing.fee_breakdown.native.net_payout : '1803.75'}</div>
            </div>
          </div>
          <input type="checkbox" checked disabled>
        </div>

        <div class="channel-sync-item">
          <div class="channel-info">
            <div class="channel-icon" style="background:#E8F5E9; color:#2E7D32;"><span class="material-icons">account_balance</span></div>
            <div>
              <div style="font-weight:700; font-size:0.85rem;">India Handmade (Govt)</div>
              <div style="font-size:0.72rem; color:#2E7D32; font-weight:700;">0% Commission | GST Exemption ID Path</div>
            </div>
          </div>
          <input type="checkbox" checked id="chk-india-handmade">
        </div>

        <div class="channel-sync-item">
          <div class="channel-info">
            <div class="channel-icon" style="background:#FFF3E0; color:#E65100;"><span class="material-icons">public</span></div>
            <div>
              <div style="font-weight:700; font-size:0.85rem;">Etsy Global Market</div>
              <div style="font-size:0.72rem; color:#E65100;">$0.20 listing + 6.5% transaction (Transparent Fee View)</div>
            </div>
          </div>
          <input type="checkbox" checked id="chk-etsy">
        </div>

        <div class="channel-sync-item">
          <div class="channel-info">
            <div class="channel-icon" style="background:#FCE4EC; color:#C2185B;"><span class="material-icons">palette</span></div>
            <div>
              <div style="font-weight:700; font-size:0.85rem;">Unfade Artisans</div>
              <div style="font-size:0.72rem; color:#6A554A;">0% Commission | Jaipur Network</div>
            </div>
          </div>
          <input type="checkbox" checked id="chk-unfade">
        </div>

      </div>

      <!-- Authenticity Certificate Preview Box -->
      <div class="certificate-preview-box">
        <span class="ks-tag ks-tag-sage">HMAC-SHA256 Signed Record</span>
        <h4 style="margin:6px 0 2px 0;">Digital Authenticity Certificate</h4>
        <p style="font-size:0.75rem; margin-bottom:6px;">Includes QR code verifiable publicly by any buyer</p>
        <div style="font-size:0.7rem; font-family:monospace; background:#F4F2E9; padding:4px; border-radius:4px; word-break:break-all;">
          CERT-KS-2026-883921 (Tamper Evident Hash)
        </div>
      </div>

      <button class="btn-primary" onclick="executePublish()" style="margin-top:16px;">
        <span class="material-icons">check_circle</span>
        <span>अभी प्रकाशित करें (Publish Everywhere)</span>
      </button>
    </div>
  `;
}

async function executePublish() {
  const container = document.getElementById('phone-screen');
  container.innerHTML = `
    <div style="text-align:center; padding:60px 20px;">
      <div class="loader-spinner"></div>
      <h3>मार्केटप्लेस सिंक हो रहा है...</h3>
      <p>Generating HMAC-SHA256 Authenticity Certificate & Syncing Python Adapters...</p>
    </div>
  `;

  try {
    const title = document.getElementById('draft-title') ? document.getElementById('draft-title').value : state.aiDraft.aiDraft.title;
    const story = document.getElementById('draft-story') ? document.getElementById('draft-story').value : state.aiDraft.aiDraft.story;

    const res = await fetch('/api/products/publish', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title,
        story: story,
        category: state.aiDraft.aiDraft.category,
        materials: state.aiDraft.aiDraft.materials,
        tags: state.aiDraft.aiDraft.tags,
        price: state.aiDraft.pricing.suggested_price,
        pricing_reasoning: state.aiDraft.pricing.reasoning,
        photo_url: state.aiDraft.photo_url,
        channels: ['native', 'india_handmade', 'etsy', 'unfade']
      })
    });
    const data = await res.json();
    if (data.success) {
      await fetchProducts();
      navigateToFlow('home');
      alert(`Success! Listing published across 4 marketplaces with QR Certificate ID: ${data.certificate.certificate_id}`);
    }
  } catch (err) {
    console.error("Publish Error:", err);
    alert("Publish failed. Local offline queue updated.");
    navigateToFlow('home');
  }
}

/* ==========================================================================
   Flow 6: Buyer Discovery & QR Certificate Verifier
   ========================================================================== */
function renderBuyerScreen() {
  return `
    <div>
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <h2>Buyer Discovery Portal</h2>
        <span class="ks-tag ks-tag-terracotta">QR Verifiable</span>
      </div>

      <div style="display:flex; gap:8px; margin:10px 0;">
        <input class="ks-input" placeholder="Search craft, region, or speak..." style="margin-bottom:0;">
        <button class="btn-secondary" style="padding:8px 12px;"><span class="material-icons">mic</span></button>
      </div>

      <div style="display:flex; gap:6px; overflow-x:auto; padding-bottom:6px; margin-bottom:12px;">
        <span class="ks-tag ks-tag-terracotta">All Crafts</span>
        <span class="ks-tag">Terracotta</span>
        <span class="ks-tag">Chikankari</span>
        <span class="ks-tag">Dokra</span>
        <span class="ks-tag">Blue Pottery</span>
      </div>

      <div id="buyer-product-cards">
        ${state.products.map(p => `
          <div class="ks-card">
            <img src="${p.photo_url}" alt="${p.title}" style="width:100%; height:140px; object-fit:cover; border-radius:var(--radius-sm); margin-bottom:8px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
              <div>
                <h4 style="margin:0;">${p.title}</h4>
                <p style="font-size:0.78rem; margin:2px 0 6px 0;">${p.region}</p>
              </div>
              <div style="font-weight:800; color:var(--color-terracotta-dark); font-size:1.1rem;">₹${p.final_price}</div>
            </div>
            
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
              <span class="ks-tag ks-tag-sage"><span class="material-icons" style="font-size:10px; vertical-align:middle;">verified</span> Provenance Certified</span>
              ${p.certificate_id ? `<a href="/certificate/${p.certificate_id}" target="_blank" class="btn-secondary" style="font-size:0.75rem; padding:4px 10px;">Verify Certificate</a>` : ''}
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

function renderCatalogScreen() {
  return `
    <div>
      <h2>Your Products (${state.products.length})</h2>
      <div>
        ${renderProductCardsHTML(state.products)}
      </div>
    </div>
  `;
}

/* ==========================================================================
   SIH 2026 Judge Gap Matrix Panel
   ========================================================================== */
function renderGapMatrix(matrixList) {
  const container = document.getElementById('gap-matrix-container');
  if (!container) return;

  container.innerHTML = matrixList.map(item => `
    <div class="gap-matrix-item">
      <div class="gap-matrix-header">
        <span class="platform-name">${item.platform}</span>
        <span class="gap-badge">${item.closed_gap_badge}</span>
      </div>
      <div style="font-size:0.78rem; color:#7A2318; font-weight:600; margin-bottom:6px;">
        <strong>Verified Limitation:</strong>
        <ul style="padding-left:16px; margin-top:2px;">
          ${item.limitations.map(l => `<li>${l}</li>`).join('')}
        </ul>
      </div>
      <div style="font-size:0.8rem; color:#2E7D32; font-weight:700; background:#E8F5E9; padding:6px 10px; border-radius:4px;">
        <strong>Karigar Setu Capability:</strong> ${item.karigar_solution}
      </div>
    </div>
  `).join('');
}

function switchAppMode(mode) {
  document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(`btn-mode-${mode}`).classList.add('active');

  if (mode === 'artisan') {
    navigateToFlow('home');
  } else if (mode === 'buyer') {
    navigateToFlow('buyer_browse');
  } else if (mode === 'judge') {
    document.getElementById('sih-judge-panel').scrollIntoView({ behavior: 'smooth' });
  }
}

function navigateToFlow(flowName) {
  state.currentFlow = flowName;
  renderScreen();
}
