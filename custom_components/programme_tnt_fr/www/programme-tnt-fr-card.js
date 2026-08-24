/* Carte Lovelace "Programme TNT FR" - version carrousel.
 * Servie automatiquement par l'integration Home Assistant du meme nom :
 * aucune configuration de ressource Lovelace manuelle n'est necessaire.
 * Utilisation minimale dans un tableau de bord :
 * type: custom:programme-tnt-fr-card
 */
(function () {
  "use strict";

  var STYLE = [
    "ha-card { padding: 16px; overflow: hidden; }",
    ".header { font-size: 1.2em; font-weight: 500; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; gap: 10px; }",
    ".header-title { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }",
    ".header-guide-link { flex-shrink: 0; border: none; background: var(--secondary-background-color, #2a2a2a); color: var(--primary-text-color); font-size: 0.62em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.02em; padding: 7px 12px; border-radius: 999px; cursor: pointer; font-family: inherit; display: flex; align-items: center; gap: 5px; }",
    ".header-guide-link:active { transform: scale(0.96); }",
    ".slot-section { margin-bottom: 14px; }",
    ".slot-section:last-child { margin-bottom: 0; }",
    ".slot-title-header { font-size: 1.1em; font-weight: 700; margin-bottom: 8px; color: var(--primary-text-color); }",
    ".carousel-wrap { position: relative; }",
    ".carousel { display: flex; gap: 12px; overflow-x: auto; overflow-y: hidden; touch-action: pan-x; padding: 2px 2px 6px; scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch; scroll-behavior: smooth; }",
    ".carousel::-webkit-scrollbar { display: none; }",
    ".carousel { scrollbar-width: none; }",
    ".poster-card { position: relative; flex: 0 0 calc(50% - 6px); width: calc(50% - 6px); border: none; padding: 0; margin: 0; cursor: pointer; scroll-snap-align: start; background: transparent; font-family: inherit; text-align: left; -webkit-tap-highlight-color: transparent; display: flex; flex-direction: column; }",
    ".poster-card:disabled { cursor: default; opacity: 0.55; }",
    ".poster-image-wrap { position: relative; width: 100%; aspect-ratio: 2 / 3; border-radius: 14px; overflow: hidden; background: linear-gradient(160deg, #4c4a6b 0%, #262445 55%, #121022 100%); box-shadow: 0 6px 18px rgba(0,0,0,0.35); transition: transform 0.15s ease; }",
    ".poster-card:active .poster-image-wrap { transform: scale(0.96); }",
    ".poster-bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }",
    ".poster-bg[hidden] { display: none; }",
    ".poster-watermark { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; opacity: 0.18; }",
    ".poster-watermark[hidden] { display: none; }",
    ".poster-watermark img { width: 50%; height: 50%; object-fit: contain; filter: brightness(0) invert(1); }",
    ".poster-badge { position: absolute; left: 8px; bottom: 8px; width: 30px; height: 30px; border-radius: 50%; background: #fff; padding: 3px; box-shadow: 0 2px 6px rgba(0,0,0,0.45); object-fit: contain; z-index: 1; }",
    ".poster-badge[hidden] { display: none; }",
    ".poster-progress-track { position: absolute; left: 0; right: 0; bottom: 0; height: 4px; background: rgba(255,255,255,0.25); }",
    ".poster-progress-track[hidden] { display: none; }",
    ".poster-progress-fill { position: absolute; left: 0; bottom: 0; height: 4px; background: #e0263f; }",
    ".poster-empty-msg { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; padding: 10px; text-align: center; font-size: 0.85em; opacity: 0.75; font-style: italic; color: #fff; }",
    ".poster-empty-msg[hidden] { display: none; }",
    ".poster-caption { padding: 10px 2px 0; }",
    ".poster-caption[hidden] { display: none; }",
    ".poster-live-tag { color: #ff3b5c; font-size: 0.78em; font-weight: 700; margin-bottom: 3px; display: flex; align-items: center; gap: 5px; }",
    ".poster-live-tag[hidden] { display: none; }",
    ".poster-live-dot { width: 6px; height: 6px; border-radius: 50%; background: #ff3b5c; animation: tntfr-pulse 1.6s infinite; flex-shrink: 0; }",
    "@keyframes tntfr-pulse { 0% { box-shadow: 0 0 0 0 rgba(255,59,92,0.55); } 70% { box-shadow: 0 0 0 6px rgba(255,59,92,0); } 100% { box-shadow: 0 0 0 0 rgba(255,59,92,0); } }",
    ".poster-title-below { font-size: 0.95em; font-weight: 700; line-height: 1.28; color: var(--primary-text-color); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }",
    ".poster-meta-below { font-size: 0.78em; color: var(--secondary-text-color, #8a8a8a); margin-top: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }",
    ".carousel-nav { position: absolute; top: 42%; transform: translateY(-50%); width: 40px; height: 40px; border-radius: 50%; border: none; background: rgba(15,15,25,0.68); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; z-index: 3; opacity: 0; transition: opacity 0.18s ease, transform 0.18s ease; padding: 0; box-shadow: 0 2px 12px rgba(0,0,0,0.45); }",
    ".carousel-nav.visible { opacity: 0.92; }",
    ".carousel-nav.visible:hover { opacity: 1; transform: translateY(-50%) scale(1.08); }",
    ".carousel-nav svg { width: 20px; height: 20px; }",
    ".carousel-nav.prev { left: 6px; }",
    ".carousel-nav.next { right: 6px; }",
    ".overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.55); display: flex; align-items: center; justify-content: center; z-index: 1000; }",
    ".overlay[hidden] { display: none; }",
    ".modal { background: var(--card-background-color, #fff); color: var(--primary-text-color); border-radius: 12px; padding: 20px; max-width: 480px; width: 90%; max-height: 80vh; overflow-y: auto; position: relative; }",
    ".modal .close { position: absolute; top: 8px; right: 12px; background: none; border: none; font-size: 1.5em; cursor: pointer; color: var(--primary-text-color); line-height: 1; }",
    ".modal-icon { width: 100%; max-height: 220px; object-fit: cover; border-radius: 8px; margin-bottom: 12px; }",
    ".modal-icon[hidden] { display: none; }",
    ".modal-title { margin: 0 0 4px 0; font-size: 1.2em; }",
    ".modal-subtitle { font-style: italic; opacity: 0.85; margin-bottom: 8px; }",
    ".modal-subtitle[hidden] { display: none; }",
    ".modal-meta { font-size: 0.85em; opacity: 0.7; margin-bottom: 12px; }",
    ".modal-desc { line-height: 1.45; white-space: pre-line; }"
  ].join("\n");

  var SLOT_DEFS = [
    ["current", "En ce moment à la télé"],
    ["prime_time", "Programmes télé en 1ère partie de soirée"],
    ["second_part", "Programmes télé en 2ème partie de soirée"]
  ];

  var CHEVRON_LEFT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>';
  var CHEVRON_RIGHT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>';

  var CHANNEL_ORDER = {
    "TF1.fr": 1, "France2.fr": 2, "France3.fr": 3,
    "CanalPlus.fr": 3.1, "CanalPlusCinema.fr": 3.2, "CanalPlusSport.fr": 3.3,
    "France4.fr": 4, "France5.fr": 5, "PlanetePlus.fr": 5.1,
    "M6.fr": 6, "Arte.fr": 7, "LaChaineParlementaire.fr": 8,
    "W9.fr": 9, "TMC.fr": 10, "NT1.fr": 11, "Gulli.fr": 12,
    "BFMTV.fr": 13, "CNews.fr": 14, "LCI.fr": 15, "FranceInfo.fr": 16,
    "CStar.fr": 17, "T18.fr": 18, "NOVO19.fr": 19, "TF1SeriesFilms.fr": 20,
    "LEquipe21.fr": 21, "6ter.fr": 22, "Numero23.fr": 23,
    "RMCDecouverte.fr": 24, "Cherie25.fr": 25, "ParisPremiere.fr": 26
  };

  function channelName(hass, entityId) {
    var attrs = (hass.states[entityId] || {}).attributes || {};
    return attrs.channel_name || entityId;
  }

  function channelRank(hass, entityId) {
    var attrs = (hass.states[entityId] || {}).attributes || {};
    var cid = attrs.channel_id;
    if (cid && Object.prototype.hasOwnProperty.call(CHANNEL_ORDER, cid)) {
      return CHANNEL_ORDER[cid];
    }
    return 999;
  }

  function formatTime(iso) {
    if (!iso) return null;
    var d = new Date(iso);
    if (isNaN(d.getTime())) return null;
    var h = String(d.getHours()).padStart(2, "0");
    var m = String(d.getMinutes()).padStart(2, "0");
    return h + "h" + m;
  }

  function liveFraction(prog) {
    if (!prog || !prog.start || !prog.stop) return null;
    var start = new Date(prog.start).getTime();
    var stop = new Date(prog.stop).getTime();
    if (isNaN(start) || isNaN(stop) || stop <= start) return null;
    var now = Date.now();
    var frac = (now - start) / (stop - start);
    if (frac < 0) frac = 0;
    if (frac > 1) frac = 1;
    return frac;
  }

  class ProgrammeTntFrCard extends HTMLElement {
    setConfig(config) {
      this._config = config || {};
      this._entities = this._config.entities || null;
      this._built = false;
      this._skeletonSignature = null;
      this._cardBtns = null;
      this._render();
    }

    set hass(hass) {
      this._hass = hass;
      this._render();
    }

    getCardSize() {
      return 12;
    }

    _resolveEntities() {
      var hass = this._hass;
      if (!hass) return [];
      var ids;
      if (this._entities && this._entities.length) {
        ids = this._entities.filter(function (id) {
          return !!hass.states[id];
        });
      } else {
        ids = Object.keys(hass.states).filter(function (id) {
          var st = hass.states[id];
          return id.indexOf("sensor.") === 0 && st.attributes && st.attributes.channel_id;
        });
      }
      ids.sort(function (a, b) {
        var ra = channelRank(hass, a);
        var rb = channelRank(hass, b);
        if (ra !== rb) return ra - rb;
        return channelName(hass, a).localeCompare(channelName(hass, b), "fr", { sensitivity: "base" });
      });
      return ids;
    }

    _ensureDom() {
      if (this._built) return;
      this.innerHTML = "";

      var style = document.createElement("style");
      style.textContent = STYLE;
      this.appendChild(style);

      var card = document.createElement("ha-card");
      card.style.touchAction = "pan-y";
      card.addEventListener("touchstart", function (e) { e.stopPropagation(); }, { passive: true });
      card.addEventListener("touchmove", function (e) { e.stopPropagation(); }, { passive: true });
      this.appendChild(card);

      var header = document.createElement("div");
      header.className = "header";
      card.appendChild(header);

      var body = document.createElement("div");
      body.className = "body";
      card.appendChild(body);

      var overlay = document.createElement("div");
      overlay.className = "overlay";
      overlay.hidden = true;
      overlay.innerHTML =
        '<div class="modal">' +
        '<button class="close" aria-label="Fermer">&times;</button>' +
        '<img class="modal-icon" hidden>' +
        '<h3 class="modal-title"></h3>' +
        '<div class="modal-subtitle" hidden></div>' +
        '<div class="modal-meta"></div>' +
        '<div class="modal-desc"></div>' +
        "</div>";
      this.appendChild(overlay);

      var self = this;
      overlay.addEventListener("click", function (e) {
        if (e.target === overlay) self._closeModal();
      });
      overlay.querySelector(".close").addEventListener("click", function () {
        self._closeModal();
      });

      this._els = {
        header: header,
        body: body,
        overlay: overlay,
        modalIcon: overlay.querySelector(".modal-icon"),
        modalTitle: overlay.querySelector(".modal-title"),
        modalSubtitle: overlay.querySelector(".modal-subtitle"),
        modalMeta: overlay.querySelector(".modal-meta"),
        modalDesc: overlay.querySelector(".modal-desc")
      };
      this._built = true;
    }

    _buildCarouselWrap(carousel) {
      var wrap = document.createElement("div");
      wrap.className = "carousel-wrap";
      wrap.appendChild(carousel);
      carousel.id = "slider";
      carousel.addEventListener("touchstart", function (e) { e.stopPropagation(); }, { passive: true });
      carousel.addEventListener("touchmove", function (e) { e.stopPropagation(); }, { passive: true });

      var prevBtn = document.createElement("button");
      prevBtn.type = "button";
      prevBtn.className = "carousel-nav prev";
      prevBtn.setAttribute("aria-label", "Precedent");
      prevBtn.innerHTML = CHEVRON_LEFT;

      var nextBtn = document.createElement("button");
      nextBtn.type = "button";
      nextBtn.className = "carousel-nav next";
      nextBtn.setAttribute("aria-label", "Suivant");
      nextBtn.innerHTML = CHEVRON_RIGHT;

      function updateNav() {
        var maxScroll = carousel.scrollWidth - carousel.clientWidth;
        var canScroll = maxScroll > 4;
        prevBtn.classList.toggle("visible", canScroll && carousel.scrollLeft > 4);
        nextBtn.classList.toggle("visible", canScroll && carousel.scrollLeft < maxScroll - 4);
      }

      prevBtn.addEventListener("click", function () {
        carousel.scrollBy({ left: -carousel.clientWidth, behavior: "smooth" });
      });
      nextBtn.addEventListener("click", function () {
        carousel.scrollBy({ left: carousel.clientWidth, behavior: "smooth" });
      });
      carousel.addEventListener("scroll", updateNav);

      wrap.appendChild(prevBtn);
      wrap.appendChild(nextBtn);

      requestAnimationFrame(updateNav);
      return wrap;
    }

    _ensureSkeleton(entities) {
      var signature = entities.join("|");
      if (this._skeletonSignature === signature && this._cardBtns) return;
      this._skeletonSignature = signature;

      var els = this._els;
      els.body.innerHTML = "";
      this._cardBtns = {};

      var self = this;
      SLOT_DEFS.forEach(function (def) {
        var slotKey = def[0], sectionTitle = def[1];

        var section = document.createElement("div");
        section.className = "slot-section";

        var titleEl = document.createElement("div");
        titleEl.className = "slot-title-header";
        titleEl.textContent = sectionTitle;
        section.appendChild(titleEl);

        var carousel = document.createElement("div");
        carousel.className = "carousel";

        self._cardBtns[slotKey] = {};
        entities.forEach(function (entityId) {
          var btn = document.createElement("button");
          btn.type = "button";
          btn.className = "poster-card";
          carousel.appendChild(btn);
          self._cardBtns[slotKey][entityId] = btn;
        });

        section.appendChild(self._buildCarouselWrap(carousel));
        els.body.appendChild(section);
      });
    }

    _updateWatermarkVisibility(refs) {
      var channelIcon = refs.currentChannelIcon;
      var showWatermark = (refs.bg.hidden || refs.bgFailed) && !!channelIcon;
      if (showWatermark) {
        if (refs.watermarkImg.getAttribute("src") !== channelIcon) refs.watermarkImg.src = channelIcon;
        refs.watermark.hidden = false;
      } else {
        refs.watermark.hidden = true;
      }
    }

    _fillPosterCard(btn, channelLabel, slotKey, prog, channelIcon) {
      var self = this;
      if (!btn._refs) {
        btn.innerHTML = "";
        var refs = {};

        refs.imageWrap = document.createElement("div");
        refs.imageWrap.className = "poster-image-wrap";
        btn.appendChild(refs.imageWrap);

        refs.bg = document.createElement("img");
        refs.bg.className = "poster-bg";
        refs.bg.loading = "lazy";
        refs.bg.alt = "";
        refs.bg.hidden = true;
        refs.bg.addEventListener("error", function () {
          refs.bgFailed = true;
          refs.bg.hidden = true;
          self._updateWatermarkVisibility(refs);
        });
        refs.imageWrap.appendChild(refs.bg);

        refs.watermark = document.createElement("div");
        refs.watermark.className = "poster-watermark";
        refs.watermark.hidden = true;
        refs.watermarkImg = document.createElement("img");
        refs.watermark.appendChild(refs.watermarkImg);
        refs.imageWrap.appendChild(refs.watermark);

        refs.badge = document.createElement("img");
        refs.badge.className = "poster-badge";
        refs.badge.alt = "";
        refs.badge.hidden = true;
        refs.imageWrap.appendChild(refs.badge);

        refs.progressTrack = document.createElement("div");
        refs.progressTrack.className = "poster-progress-track";
        refs.progressFill = document.createElement("div");
        refs.progressFill.className = "poster-progress-fill";
        refs.progressTrack.appendChild(refs.progressFill);
        refs.progressTrack.hidden = true;
        refs.imageWrap.appendChild(refs.progressTrack);

        refs.empty = document.createElement("div");
        refs.empty.className = "poster-empty-msg";
        refs.empty.textContent = "Pas de programme";
        refs.empty.hidden = true;
        refs.imageWrap.appendChild(refs.empty);

        refs.caption = document.createElement("div");
        refs.caption.className = "poster-caption";
        btn.appendChild(refs.caption);

        refs.liveTag = document.createElement("div");
        refs.liveTag.className = "poster-live-tag";
        var dot = document.createElement("span");
        dot.className = "poster-live-dot";
        refs.liveTag.appendChild(dot);
        refs.liveTag.appendChild(document.createTextNode("En direct"));
        refs.liveTag.hidden = true;
        refs.caption.appendChild(refs.liveTag);

        refs.titleEl = document.createElement("div");
        refs.titleEl.className = "poster-title-below";
        refs.caption.appendChild(refs.titleEl);

        refs.metaEl = document.createElement("div");
        refs.metaEl.className = "poster-meta-below";
        refs.caption.appendChild(refs.metaEl);

        refs.clickHandler = null;
        btn._refs = refs;
      }

      var refs = btn._refs;
      refs.currentChannelIcon = channelIcon || null;

      if (channelIcon) {
        if (refs.badge.getAttribute("src") !== channelIcon) refs.badge.src = channelIcon;
        refs.badge.hidden = false;
      } else {
        refs.badge.hidden = true;
      }

      if (!prog) {
        btn.disabled = true;
        refs.bg.hidden = true;
        refs.bgFailed = false;
        refs.watermark.hidden = true;
        refs.progressTrack.hidden = true;
        refs.empty.hidden = false;
        refs.caption.hidden = true;
        if (refs.clickHandler) {
          btn.removeEventListener("click", refs.clickHandler);
          refs.clickHandler = null;
        }
        return;
      }

      btn.disabled = false;
      refs.empty.hidden = true;
      refs.caption.hidden = false;

      var artUrl = prog.poster || prog.icon || null;
      refs.bgFailed = false;
      if (artUrl) {
        if (refs.bg.getAttribute("src") !== artUrl) refs.bg.src = artUrl;
        refs.bg.hidden = false;
      } else {
        refs.bg.hidden = true;
        refs.bg.removeAttribute("src");
      }
      this._updateWatermarkVisibility(refs);

      refs.liveTag.hidden = slotKey !== "current";

      refs.titleEl.textContent = prog.title || "";

      var startFmt = formatTime(prog.start);
      var stopFmt = formatTime(prog.stop);
      var metaParts = [];
      if (prog.category) metaParts.push(prog.category);
      metaParts.push(channelLabel);
      if (startFmt && stopFmt) metaParts.push(startFmt + "-" + stopFmt);
      refs.metaEl.textContent = metaParts.join(" • ");

      if (slotKey === "current") {
        var frac = liveFraction(prog);
        if (frac !== null) {
          refs.progressTrack.hidden = false;
          refs.progressFill.style.width = (frac * 100).toFixed(1) + "%";
        } else {
          refs.progressTrack.hidden = true;
        }
      } else {
        refs.progressTrack.hidden = true;
      }

      if (refs.clickHandler) {
        btn.removeEventListener("click", refs.clickHandler);
      }
      refs.clickHandler = function () {
        self._openModal(channelLabel, prog);
      };
      btn.addEventListener("click", refs.clickHandler);
    }

    _render() {
      this._ensureDom();
      var hass = this._hass;
      var els = this._els;
      els.headerTitle.textContent = this._config.title || "Programme TV : que regarder ce soir ?";

      if (!hass) {
        els.body.innerHTML = "";
        this._skeletonSignature = null;
        this._cardBtns = null;
        return;
      }

      var entities = this._resolveEntities();
      this._ensureSkeleton(entities);

      var self = this;
      SLOT_DEFS.forEach(function (def) {
        var slotKey = def[0];
        entities.forEach(function (entityId) {
          var attrs = (hass.states[entityId] || {}).attributes || {};
          var channelLabel = attrs.channel_name || entityId;
          var channelIcon = attrs.channel_icon || null;
          var prog = attrs[slotKey];
          var btn = self._cardBtns[slotKey][entityId];
          self._fillPosterCard(btn, channelLabel, slotKey, prog, channelIcon);
        });
      });
    }

    _openModal(channelLabel, prog) {
      var els = this._els;
      if (prog.icon) {
        els.modalIcon.src = prog.icon;
        els.modalIcon.hidden = false;
      } else {
        els.modalIcon.hidden = true;
        els.modalIcon.removeAttribute("src");
      }
      els.modalTitle.textContent = prog.title || "";
      if (prog.subtitle) {
        els.modalSubtitle.textContent = prog.subtitle;
        els.modalSubtitle.hidden = false;
      } else {
        els.modalSubtitle.hidden = true;
      }
      var metaParts = [channelLabel];
      var startFmt = formatTime(prog.start);
      var stopFmt = formatTime(prog.stop);
      if (startFmt && stopFmt) metaParts.push(startFmt + " - " + stopFmt);
      if (prog.category) metaParts.push(prog.category);
      if (prog.rating) metaParts.push("CSA : " + prog.rating);
      els.modalMeta.textContent = metaParts.join(" • ");
      els.modalDesc.textContent = prog.description || "";
      els.overlay.hidden = false;
    }

    _closeModal() {
      this._els.overlay.hidden = true;
    }

    static getStubConfig() {
      return { title: "Programme TV : que regarder ce soir ?" };
    }
  }

  customElements.define("programme-tnt-fr-card", ProgrammeTntFrCard);

  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "programme-tnt-fr-card",
    name: "Programme TNT FR",
    description: "Programme TV des chaines de la TNT francaise en 3 carrousels horizontaux (en ce moment / 1re et 2e partie de soiree), affiche/jaquette par programme quand disponible, avec details au clic."
  });
  var GUIDE_STYLE = [
    ".guide-header { margin-bottom: 10px; }",
    ".guide-title { font-size: 1.2em; font-weight: 500; margin-bottom: 10px; }",
    ".guide-search { width: 100%; box-sizing: border-box; padding: 10px 14px; border-radius: 999px; border: none; background: var(--secondary-background-color, #2a2a2a); color: var(--primary-text-color); font-size: 0.95em; margin-bottom: 10px; font-family: inherit; }",
    ".guide-daybar { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }",
    ".guide-day-btn { width: 36px; height: 36px; flex-shrink: 0; border-radius: 50%; border: none; background: var(--secondary-background-color, #2a2a2a); color: var(--primary-text-color); cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 0; }",
    ".guide-day-btn svg { width: 18px; height: 18px; }",
    ".guide-day-label { flex: 1; text-align: center; padding: 8px 12px; border-radius: 999px; border: none; background: var(--secondary-background-color, #2a2a2a); color: var(--primary-text-color); font-weight: 600; cursor: pointer; font-family: inherit; font-size: 0.92em; text-transform: capitalize; }",
    ".guide-day-input { position: absolute; width: 0; height: 0; opacity: 0; pointer-events: none; }",
    ".guide-columns { display: flex; gap: 12px; overflow-x: auto; overflow-y: hidden; scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch; scroll-behavior: smooth; }",
    ".guide-columns::-webkit-scrollbar { display: none; }",
    ".guide-columns { scrollbar-width: none; }",
    ".guide-column { flex: 0 0 calc(50% - 6px); min-width: 0; scroll-snap-align: start; display: flex; flex-direction: column; }",
    ".guide-column.tntfr-hidden { display: none; }",
    ".guide-col-header { display: flex; align-items: center; gap: 8px; padding: 6px 4px 10px; }",
    ".guide-col-logo { width: 32px; height: 32px; border-radius: 50%; background: #fff; padding: 3px; object-fit: contain; flex-shrink: 0; box-shadow: 0 1px 4px rgba(0,0,0,0.3); }",
    ".guide-col-meta { min-width: 0; }",
    ".guide-col-lcn { font-size: 0.65em; opacity: 0.6; font-weight: 600; }",
    ".guide-col-name { font-size: 0.9em; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }",
    ".guide-col-list { display: flex; flex-direction: column; gap: 10px; overflow-y: auto; max-height: 60vh; padding: 2px 2px 8px; }",
    ".guide-item { display: flex; flex-direction: column; text-align: left; border: none; padding: 0; margin: 0; cursor: pointer; font-family: inherit; color: inherit; -webkit-tap-highlight-color: transparent; border-radius: 12px; overflow: hidden; background: var(--secondary-background-color, #232323); }",
    ".guide-item.is-live { outline: 2px solid #e0263f; outline-offset: -2px; }",
    ".guide-item-img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; display: block; background: linear-gradient(160deg, #5b4fc4 0%, #2c2560 55%, #12102b 100%); }",
    ".guide-item-img[hidden] { display: none; }",
    ".guide-item-body { padding: 8px 10px 10px; }",
    ".guide-item-time { font-size: 0.72em; opacity: 0.65; font-weight: 700; display: flex; align-items: center; gap: 6px; }",
    ".guide-item-live-dot { width: 6px; height: 6px; border-radius: 50%; background: #e0263f; animation: tntfr-pulse 1.6s infinite; }",
    ".guide-item-title { font-size: 0.92em; font-weight: 700; margin-top: 2px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }",
    ".guide-item-desc { font-size: 0.78em; opacity: 0.65; margin-top: 2px; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }",
    ".guide-empty, .guide-loading { padding: 20px 8px; text-align: center; opacity: 0.6; font-size: 0.85em; font-style: italic; }"
  ].join("\n");

  var DAY_NAMES_FR = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];

  function isoDateLocal(d) {
    var y = d.getFullYear();
    var m = String(d.getMonth() + 1).padStart(2, "0");
    var day = String(d.getDate()).padStart(2, "0");
    return y + "-" + m + "-" + day;
  }

  function dayLabelFr(d) {
    var dow = DAY_NAMES_FR[d.getDay()];
    var dd = String(d.getDate()).padStart(2, "0");
    var mm = String(d.getMonth() + 1).padStart(2, "0");
    return dow + " " + dd + "/" + mm;
  }

  function normalizeSearch(s) {
    return (s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }

  function isProgLive(prog) {
    var f = liveFraction(prog);
    return f !== null && f > 0 && f < 1;
  }

  class ProgrammeTntFrGuideCard extends HTMLElement {
    setConfig(config) {
      this._config = config || {};
      this._entities = this._config.entities || null;
      this._built = false;
      this._cache = {};
      this._currentDate = new Date();
      if (this._hass) this._render();
    }

    set hass(hass) {
      this._hass = hass;
      if (!this._built) this._render();
    }

    getCardSize() {
      return 16;
    }

    _resolveEntities() {
      var hass = this._hass;
      if (!hass) return [];
      var ids;
      if (this._entities && this._entities.length) {
        ids = this._entities.filter(function (id) {
          return !!hass.states[id];
        });
      } else {
        ids = Object.keys(hass.states).filter(function (id) {
          var st = hass.states[id];
          return id.indexOf("sensor.") === 0 && st.attributes && st.attributes.channel_id;
        });
      }
      ids.sort(function (a, b) {
        var ra = channelRank(hass, a);
        var rb = channelRank(hass, b);
        if (ra !== rb) return ra - rb;
        return channelName(hass, a).localeCompare(channelName(hass, b), "fr", { sensitivity: "base" });
      });
      return ids;
    }

    _render() {
      if (this._built) return;
      var hass = this._hass;
      if (!hass) return;

      var entities = this._resolveEntities();
      if (!entities.length) return;

      this.innerHTML = "";

      var style = document.createElement("style");
      style.textContent = STYLE + "\n" + GUIDE_STYLE;
      this.appendChild(style);

      var card = document.createElement("ha-card");
      this.appendChild(card);

      var header = document.createElement("div");
      header.className = "guide-header";

      var title = document.createElement("div");
      title.className = "guide-title";
      title.textContent = this._config.title || "Guide TV";
      header.appendChild(title);

      var search = document.createElement("input");
      search.type = "text";
      search.className = "guide-search";
      search.placeholder = "Rechercher une chaine";
      header.appendChild(search);

      var daybar = document.createElement("div");
      daybar.className = "guide-daybar";

      var prevBtn = document.createElement("button");
      prevBtn.type = "button";
      prevBtn.className = "guide-day-btn";
      prevBtn.innerHTML = CHEVRON_LEFT;
      prevBtn.setAttribute("aria-label", "Jour precedent");

      var dayLabel = document.createElement("button");
      dayLabel.type = "button";
      dayLabel.className = "guide-day-label";

      var dayInput = document.createElement("input");
      dayInput.type = "date";
      dayInput.className = "guide-day-input";

      var nextBtn = document.createElement("button");
      nextBtn.type = "button";
      nextBtn.className = "guide-day-btn";
      nextBtn.innerHTML = CHEVRON_RIGHT;
      nextBtn.setAttribute("aria-label", "Jour suivant");

      daybar.appendChild(prevBtn);
      daybar.appendChild(dayLabel);
      daybar.appendChild(dayInput);
      daybar.appendChild(nextBtn);
      header.appendChild(daybar);

      var columns = document.createElement("div");
      columns.className = "guide-columns";

      var self = this;
      var colRefs = {};

      entities.forEach(function (entityId) {
        var attrs = hass.states[entityId].attributes || {};
        var channelId = attrs.channel_id;
        var label = attrs.channel_name || entityId;
        var icon = attrs.channel_icon || null;
        var rank = channelRank(hass, entityId);

        var col = document.createElement("div");
        col.className = "guide-column";
        col.dataset.search = normalizeSearch(label);

        var colHeader = document.createElement("div");
        colHeader.className = "guide-col-header";

        if (icon) {
          var logo = document.createElement("img");
          logo.className = "guide-col-logo";
          logo.src = icon;
          logo.alt = "";
          colHeader.appendChild(logo);
        }

        var meta = document.createElement("div");
        meta.className = "guide-col-meta";

        if (rank < 999) {
          var lcn = document.createElement("div");
          lcn.className = "guide-col-lcn";
          lcn.textContent = String(Math.floor(rank)).padStart(3, "0");
          meta.appendChild(lcn);
        }

        var name = document.createElement("div");
        name.className = "guide-col-name";
        name.textContent = label;
        meta.appendChild(name);

        colHeader.appendChild(meta);
        col.appendChild(colHeader);

        var list = document.createElement("div");
        list.className = "guide-col-list";
        var loading = document.createElement("div");
        loading.className = "guide-loading";
        loading.textContent = "Chargement...";
        list.appendChild(loading);
        col.appendChild(list);

        columns.appendChild(col);
        colRefs[channelId] = { column: col, list: list, label: label, icon: icon };
      });

      var overlay = document.createElement("div");
      overlay.className = "overlay";
      overlay.hidden = true;
      overlay.innerHTML =
        "<div class=\"modal\">" +
        "<button class=\"close\" aria-label=\"Fermer\">&times;</button>" +
        "<img class=\"modal-icon\" hidden>" +
        "<h3 class=\"modal-title\"></h3>" +
        "<div class=\"modal-subtitle\" hidden></div>" +
        "<div class=\"modal-meta\"></div>" +
        "<div class=\"modal-desc\"></div>" +
        "</div>";

      card.appendChild(header);
      card.appendChild(columns);
      this.appendChild(overlay);

      overlay.addEventListener("click", function (e) {
        if (e.target === overlay) overlay.hidden = true;
      });
      overlay.querySelector(".close").addEventListener("click", function () {
        overlay.hidden = true;
      });

      this._els = {
        dayLabel: dayLabel,
        dayInput: dayInput,
        search: search,
        columns: columns,
        overlay: overlay,
        modalIcon: overlay.querySelector(".modal-icon"),
        modalTitle: overlay.querySelector(".modal-title"),
        modalSubtitle: overlay.querySelector(".modal-subtitle"),
        modalMeta: overlay.querySelector(".modal-meta"),
        modalDesc: overlay.querySelector(".modal-desc")
      };
      this._colRefs = colRefs;
      this._built = true;

      search.addEventListener("input", function () {
        self._applySearch(search.value);
      });

      prevBtn.addEventListener("click", function () {
        self._goToDate(new Date(self._currentDate.getTime() - 86400000));
      });
      nextBtn.addEventListener("click", function () {
        self._goToDate(new Date(self._currentDate.getTime() + 86400000));
      });
      dayLabel.addEventListener("click", function () {
        dayInput.value = isoDateLocal(self._currentDate);
        if (dayInput.showPicker) {
          dayInput.showPicker();
        } else {
          dayInput.focus();
          dayInput.click();
        }
      });
      dayInput.addEventListener("change", function () {
        if (!dayInput.value) return;
        var parts = dayInput.value.split("-");
        var d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
        self._goToDate(d);
      });

      this._goToDate(this._currentDate);
    }

    _applySearch(query) {
      var norm = normalizeSearch(query);
      var cols = this._els.columns.querySelectorAll(".guide-column");
      cols.forEach(function (col) {
        var match = !norm || col.dataset.search.indexOf(norm) !== -1;
        col.classList.toggle("tntfr-hidden", !match);
      });
    }

    _goToDate(date) {
      this._currentDate = date;
      this._els.dayLabel.textContent = dayLabelFr(date);
      var dateStr = isoDateLocal(date);
      if (this._cache[dateStr]) {
        this._renderDay(dateStr);
      } else {
        this._fetchDay(dateStr);
      }
    }

    _fetchDay(dateStr) {
      var self = this;
      var channelIds = Object.keys(this._colRefs);
      channelIds.forEach(function (cid) {
        self._colRefs[cid].list.innerHTML = "";
        var loading = document.createElement("div");
        loading.className = "guide-loading";
        loading.textContent = "Chargement...";
        self._colRefs[cid].list.appendChild(loading);
      });

      this._hass.connection
        .sendMessagePromise({
          type: "programme_tnt_fr/programmes",
          channels: channelIds,
          date: dateStr
        })
        .then(function (resp) {
          self._cache[dateStr] = (resp && resp.programmes) || {};
          self._renderDay(dateStr);
        })
        .catch(function (err) {
          console.error("programme-tnt-fr-guide-card: fetch failed", err);
          Object.keys(self._colRefs).forEach(function (cid) {
            self._colRefs[cid].list.innerHTML = "";
            var msg = document.createElement("div");
            msg.className = "guide-empty";
            msg.textContent = "Erreur de chargement";
            self._colRefs[cid].list.appendChild(msg);
          });
        });
    }

    _renderDay(dateStr) {
      var self = this;
      var dayData = this._cache[dateStr] || {};
      Object.keys(this._colRefs).forEach(function (channelId) {
        var ref = self._colRefs[channelId];
        var progs = dayData[channelId] || [];
        ref.list.innerHTML = "";
        if (!progs.length) {
          var empty = document.createElement("div");
          empty.className = "guide-empty";
          empty.textContent = "Aucun programme";
          ref.list.appendChild(empty);
          return;
        }
        progs.forEach(function (prog) {
          ref.list.appendChild(self._buildGuideItem(prog, ref.label, ref.icon));
        });
      });
    }

    _buildGuideItem(prog, channelLabel, channelIcon) {
      var self = this;
      var item = document.createElement("button");
      item.type = "button";
      item.className = "guide-item";
      var live = isProgLive(prog);
      if (live) item.classList.add("is-live");

      var artUrl = prog.icon || channelIcon || null;
      if (artUrl) {
        var img = document.createElement("img");
        img.className = "guide-item-img";
        img.src = artUrl;
        img.loading = "lazy";
        img.alt = "";
        img.addEventListener("error", function () {
          img.hidden = true;
        });
        item.appendChild(img);
      }

      var body = document.createElement("div");
      body.className = "guide-item-body";

      var timeEl = document.createElement("div");
      timeEl.className = "guide-item-time";
      if (live) {
        var dot = document.createElement("span");
        dot.className = "guide-item-live-dot";
        timeEl.appendChild(dot);
      }
      timeEl.appendChild(document.createTextNode((formatTime(prog.start) || "?") + " - " + (formatTime(prog.stop) || "?")));
      body.appendChild(timeEl);

      var titleEl = document.createElement("div");
      titleEl.className = "guide-item-title";
      titleEl.textContent = prog.title || "";
      body.appendChild(titleEl);

      var descText = prog.subtitle || prog.description || "";
      if (descText) {
        var descEl = document.createElement("div");
        descEl.className = "guide-item-desc";
        descEl.textContent = descText;
        body.appendChild(descEl);
      }

      item.appendChild(body);
      item.addEventListener("click", function () {
        self._openModal(channelLabel, prog);
      });
      return item;
    }

    _openModal(channelLabel, prog) {
      var els = this._els;
      if (prog.icon) {
        els.modalIcon.src = prog.icon;
        els.modalIcon.hidden = false;
      } else {
        els.modalIcon.hidden = true;
        els.modalIcon.removeAttribute("src");
      }
      els.modalTitle.textContent = prog.title || "";
      if (prog.subtitle) {
        els.modalSubtitle.textContent = prog.subtitle;
        els.modalSubtitle.hidden = false;
      } else {
        els.modalSubtitle.hidden = true;
      }
      var metaParts = [channelLabel];
      var startFmt = formatTime(prog.start);
      var stopFmt = formatTime(prog.stop);
      if (startFmt && stopFmt) metaParts.push(startFmt + " - " + stopFmt);
      if (prog.category) metaParts.push(prog.category);
      if (prog.rating) metaParts.push("CSA : " + prog.rating);
      els.modalMeta.textContent = metaParts.join(" \u2022 ");
      els.modalDesc.textContent = prog.description || "";
      els.overlay.hidden = false;
    }

    static getStubConfig() {
      return { title: "Guide TV" };
    }
  }

  customElements.define("programme-tnt-fr-guide-card", ProgrammeTntFrGuideCard);

  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "programme-tnt-fr-guide-card",
    name: "Programme TNT FR - Guide TV",
    description: "Guide TV multi-chaines : deux colonnes visibles a la fois, defilement vertical pour voir les programmes suivants de chaque chaine, horizontal pour changer de chaine, avec recherche et selecteur de jour."
  });
})();
