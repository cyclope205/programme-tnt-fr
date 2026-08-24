/* Carte Lovelace "Programme TNT FR" - carrousel + Guide TV integres.
 * Servie automatiquement par l'integration Home Assistant du meme nom :
 * aucune configuration de ressource Lovelace manuelle n'est necessaire.
 * Utilisation minimale dans un tableau de bord :
 * type: custom:programme-tnt-fr-card
 */
(function () {
  "use strict";

  var STYLE = [
    "ha-card { padding: 16px; overflow: hidden; }",
    ".header { font-size: 1.2em; font-weight: 500; margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between; gap: 10px; }",
    ".header-title { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }",
    ".header-guide-link { flex-shrink: 0; border: none; background: var(--secondary-background-color, #2a2a2a); color: var(--primary-text-color); font-size: 0.62em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.02em; padding: 7px 12px; border-radius: 999px; cursor: pointer; font-family: inherit; display: flex; align-items: center; gap: 5px; }",
    ".header-guide-link:active { transform: scale(0.96); }",
    ".slot-section { margin-bottom: 26px; }",
    ".slot-section:last-child { margin-bottom: 0; }",
    ".slot-title-header { font-size: 1.12em; font-weight: 700; margin-bottom: 12px; color: var(--primary-text-color); display: flex; align-items: center; gap: 9px; }",
    ".slot-title-icon { width: 8px; height: 22px; border-radius: 4px; flex-shrink: 0; }",
    ".slot-title-icon.live { background: #e0263f; }",
    ".slot-title-icon.prime { background: #3f6fe0; }",
    ".slot-title-icon.second { background: #1c9c8a; }",
    ".carousel-wrap { position: relative; }",
    ".carousel { display: flex; gap: 12px; overflow-x: auto; overflow-y: hidden; padding: 2px 2px 6px; scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch; scroll-behavior: smooth; }",
    ".carousel::-webkit-scrollbar { display: none; }",
    ".carousel { scrollbar-width: none; }",
    ".poster-card { position: relative; flex: 0 0 calc(50% - 6px); width: calc(50% - 6px); border-radius: 18px; overflow: hidden; display: flex; flex-direction: column; border: none; padding: 0; margin: 0; cursor: pointer; scroll-snap-align: start; background: linear-gradient(160deg, #5b4fc4 0%, #2c2560 55%, #12102b 100%); box-shadow: 0 10px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06); transition: transform 0.15s ease, box-shadow 0.15s ease; font-family: inherit; -webkit-tap-highlight-color: transparent; }",
    ".poster-card:active { transform: scale(0.97); }",
    ".poster-card:disabled { cursor: default; opacity: 0.55; }",
    ".poster-image-wrap { position: relative; width: 100%; aspect-ratio: 2 / 3; overflow: hidden; flex-shrink: 0; }",
    ".poster-bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }",
    ".poster-watermark { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; opacity: 0.16; }",
    ".poster-watermark img { width: 52%; height: 52%; object-fit: contain; filter: brightness(0) invert(1); }",
    ".poster-channel-badge { position: absolute; bottom: 10px; left: 10px; width: 34px; height: 34px; border-radius: 50%; background: #fff; padding: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.45); object-fit: contain; z-index: 1; }",
    ".poster-live-badge { position: absolute; top: 10px; right: 10px; display: flex; align-items: center; gap: 5px; background: rgba(224,38,63,0.94); color: #fff; font-size: 0.66em; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; padding: 5px 10px 5px 8px; border-radius: 20px; box-shadow: 0 2px 10px rgba(224,38,63,0.5); z-index: 1; }",
    ".poster-live-dot { width: 6px; height: 6px; border-radius: 50%; background: #fff; animation: tntfr-pulse 1.6s infinite; }",
    "@keyframes tntfr-pulse { 0% { box-shadow: 0 0 0 0 rgba(255,255,255,0.7); } 70% { box-shadow: 0 0 0 6px rgba(255,255,255,0); } 100% { box-shadow: 0 0 0 0 rgba(255,255,255,0); } }",
    ".poster-content { padding: 10px 12px 12px; color: var(--primary-text-color); background: var(--ha-card-background, var(--card-background-color, #1c1c1c)); flex: 1 1 auto; }",
    ".poster-channel-name { font-size: 0.72em; font-weight: 700; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }",
    ".poster-title { font-size: 1.02em; font-weight: 700; line-height: 1.28; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }",
    ".poster-time { font-size: 0.76em; font-weight: 600; opacity: 0.9; margin-top: 6px; }",
    ".poster-progress-track { position: absolute; left: 0; right: 0; bottom: 0; height: 4px; background: rgba(255,255,255,0.25); }",
    ".poster-progress-fill { position: absolute; left: 0; bottom: 0; height: 4px; background: #e0263f; }",
    ".poster-empty-msg { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; padding: 10px; text-align: center; font-size: 0.85em; opacity: 0.7; font-style: italic; color: var(--primary-text-color); }",
    ".carousel-nav { position: absolute; top: 50%; transform: translateY(-50%); width: 40px; height: 40px; border-radius: 50%; border: none; background: rgba(15,15,25,0.68); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; z-index: 3; opacity: 0; transition: opacity 0.18s ease, transform 0.18s ease; padding: 0; box-shadow: 0 2px 12px rgba(0,0,0,0.45); }",
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
    ".modal-desc { line-height: 1.45; white-space: pre-line; }",
    ".guide-header { margin-bottom: 10px; }",
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
    ".guide-item { display: flex; flex-direction: column; flex-shrink: 0; text-align: left; border: none; padding: 0; margin: 0; cursor: pointer; font-family: inherit; color: inherit; -webkit-tap-highlight-color: transparent; border-radius: 12px; overflow: hidden; background: var(--secondary-background-color, #232323); }",
    ".guide-item.is-live { outline: 2px solid #e0263f; outline-offset: -2px; }",
    ".guide-item-img { width: 100%; aspect-ratio: 2 / 3; object-fit: cover; display: block; background: linear-gradient(160deg, #5b4fc4 0%, #2c2560 55%, #12102b 100%); }",
    ".guide-item-img[hidden] { display: none; }",
    ".guide-item-body { padding: 8px 10px 10px; }",
    ".guide-item-time { font-size: 0.72em; opacity: 0.65; font-weight: 700; display: flex; align-items: center; gap: 6px; }",
    ".guide-item-live-dot { width: 6px; height: 6px; border-radius: 50%; background: #e0263f; animation: tntfr-pulse 1.6s infinite; }",
    ".guide-item-title { font-size: 0.92em; font-weight: 700; margin-top: 2px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }",
    ".guide-item-desc { font-size: 0.78em; opacity: 0.65; margin-top: 2px; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }",
    ".guide-empty, .guide-loading { padding: 20px 8px; text-align: center; opacity: 0.6; font-size: 0.85em; font-style: italic; }"
  ].join("\n");

  var SLOT_DEFS = [
    ["current", "En ce moment a la tele", "live"],
    ["prime_time", "Programmes tele en 1ere partie de soiree", "prime"],
    ["second_part", "Programmes tele en 2eme partie de soiree", "second"]
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
    var attrs = hass.states[entityId].attributes || {};
    return attrs.channel_name || entityId;
  }

  function channelRank(hass, entityId) {
    var attrs = hass.states[entityId].attributes || {};
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
  class ProgrammeTntFrCard extends HTMLElement {
    setConfig(config) {
      this._config = config || {};
      this._entities = this._config.entities || null;
      this._built = false;
      this._guideOpen = false;
      this._guideBuilt = false;
      this._guideCache = {};
      this._guideDate = new Date();
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
      var self = this;

      var style = document.createElement("style");
      style.textContent = STYLE;
      this.appendChild(style);

      var card = document.createElement("ha-card");
      this.appendChild(card);

      var header = document.createElement("div");
      header.className = "header";

      var headerTitle = document.createElement("span");
      headerTitle.className = "header-title";
      header.appendChild(headerTitle);

      var guideLink = document.createElement("button");
      guideLink.type = "button";
      guideLink.className = "header-guide-link";
      guideLink.textContent = "Guide TV";
      guideLink.addEventListener("click", function () {
        self._guideOpen = !self._guideOpen;
        guideLink.textContent = self._guideOpen ? "Carrousel" : "Guide TV";
        self._renderBody();
      });
      header.appendChild(guideLink);
      card.appendChild(header);

      var body = document.createElement("div");
      body.className = "body";
      card.appendChild(body);

      var guideRoot = document.createElement("div");
      guideRoot.className = "guide-root";
      guideRoot.hidden = true;
      card.appendChild(guideRoot);

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
      this.appendChild(overlay);

      overlay.addEventListener("click", function (e) {
        if (e.target === overlay) self._closeModal();
      });
      overlay.querySelector(".close").addEventListener("click", function () {
        self._closeModal();
      });

      this._els = {
        header: header,
        headerTitle: headerTitle,
        guideLink: guideLink,
        body: body,
        guideRoot: guideRoot,
        overlay: overlay,
        modalIcon: overlay.querySelector(".modal-icon"),
        modalTitle: overlay.querySelector(".modal-title"),
        modalSubtitle: overlay.querySelector(".modal-subtitle"),
        modalMeta: overlay.querySelector(".modal-meta"),
        modalDesc: overlay.querySelector(".modal-desc")
      };
      this._built = true;
    }
    _render() {
      this._ensureDom();
      var els = this._els;
      els.headerTitle.textContent = this._config.title || "Programme TV : que regarder ce soir ?";

      if (!this._hass) {
        els.body.innerHTML = "";
        return;
      }

      this._renderBody();
    }

    _renderBody() {
      var els = this._els;
      if (this._guideOpen) {
        els.body.hidden = true;
        els.guideRoot.hidden = false;
        this._ensureGuideBuilt();
      } else {
        els.body.hidden = false;
        els.guideRoot.hidden = true;
        this._renderCarousel();
      }
    }

    _renderCarousel() {
      var hass = this._hass;
      var els = this._els;

      var carIds = this._resolveEntities();
      var carSig = carIds.map(function (id) {
        var st = hass.states[id];
        return id + ":" + (st ? st.last_changed + ":" + JSON.stringify(st.attributes) : "");
      }).join("|");
      if (this._carouselSig === carSig && els.body.children.length) {
        return;
      }
      this._carouselSig = carSig;

      var previousScroll = Array.prototype.map.call(
        els.body.querySelectorAll(".carousel"),
        function (c) { return c.scrollLeft; }
      );

      els.body.innerHTML = "";

      var entities = this._resolveEntities();
      var self = this;

      SLOT_DEFS.forEach(function (def, index) {
        var slotKey = def[0], sectionTitle = def[1], colorClass = def[2];

        var section = document.createElement("div");
        section.className = "slot-section";

        var titleEl = document.createElement("div");
        titleEl.className = "slot-title-header";
        var icon = document.createElement("span");
        icon.className = "slot-title-icon " + colorClass;
        titleEl.appendChild(icon);
        titleEl.appendChild(document.createTextNode(sectionTitle));
        section.appendChild(titleEl);

        var carousel = document.createElement("div");
        carousel.className = "carousel";
        carousel.id = "slider";
        entities.forEach(function (entityId) {
          var attrs = hass.states[entityId].attributes || {};
          var channelLabel = attrs.channel_name || entityId;
          var channelIcon = attrs.channel_icon || null;
          var prog = attrs[slotKey];
          var card = self._buildPosterCard(channelLabel, slotKey, prog, channelIcon);
          carousel.appendChild(card);
        });

        section.appendChild(self._buildCarouselWrap(carousel));
        els.body.appendChild(section);

        if (previousScroll[index]) {
          carousel.scrollLeft = previousScroll[index];
        }
      });
    }

    _buildPosterCard(channelLabel, slotKey, prog, channelIcon) {
      var self = this;
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "poster-card";

      var imageWrap = document.createElement("div");
      imageWrap.className = "poster-image-wrap";
      btn.appendChild(imageWrap);

      if (channelIcon) {
        var badge = document.createElement("img");
        badge.className = "poster-channel-badge";
        badge.src = channelIcon;
        badge.alt = "";
        imageWrap.appendChild(badge);
      }

      if (!prog) {
        btn.disabled = true;
        var empty = document.createElement("div");
        empty.className = "poster-empty-msg";
        empty.textContent = "Pas de programme";
        imageWrap.appendChild(empty);
        return btn;
      }

      var artUrl = prog.poster || prog.icon || null;
      if (artUrl) {
        var img = document.createElement("img");
        img.className = "poster-bg";
        img.src = artUrl;
        img.loading = "lazy";
        img.alt = "";
        img.addEventListener("error", function () {
          img.remove();
          if (channelIcon) {
            var wm = document.createElement("div");
            wm.className = "poster-watermark";
            var wmImg = document.createElement("img");
            wmImg.src = channelIcon;
            wm.appendChild(wmImg);
            imageWrap.insertBefore(wm, imageWrap.firstChild);
          }
        });
        imageWrap.insertBefore(img, imageWrap.firstChild);
      } else if (channelIcon) {
        var wm2 = document.createElement("div");
        wm2.className = "poster-watermark";
        var wmImg2 = document.createElement("img");
        wmImg2.src = channelIcon;
        wm2.appendChild(wmImg2);
        imageWrap.insertBefore(wm2, imageWrap.firstChild);
      }

      var startFmt = formatTime(prog.start);
      var stopFmt = formatTime(prog.stop);

      if (slotKey === "current") {
        var live = document.createElement("div");
        live.className = "poster-live-badge";
        var dot = document.createElement("span");
        dot.className = "poster-live-dot";
        live.appendChild(dot);
        live.appendChild(document.createTextNode("Direct"));
        imageWrap.appendChild(live);
      }

      var content = document.createElement("div");
      content.className = "poster-content";

      var titleEl = document.createElement("div");
      titleEl.className = "poster-title";
      titleEl.textContent = prog.title || "";
      content.appendChild(titleEl);

      var timeEl = document.createElement("div");
      timeEl.className = "poster-time";
      var metaParts = [];
      if (prog.category) metaParts.push(prog.category);
      metaParts.push(channelLabel);
      metaParts.push((startFmt || "?") + " - " + (stopFmt || "?"));
      timeEl.textContent = metaParts.join(" \u2022 ");
      content.appendChild(timeEl);
      btn.appendChild(content);

      if (slotKey === "current") {
        var frac = liveFraction(prog);
        if (frac !== null) {
          var track = document.createElement("div");
          track.className = "poster-progress-track";
          var fill = document.createElement("div");
          fill.className = "poster-progress-fill";
          fill.style.width = (frac * 100).toFixed(1) + "%";
          track.appendChild(fill);
          imageWrap.appendChild(track);
        }
      }

      btn.addEventListener("click", function () {
        self._openModal(channelLabel, prog);
      });

      return btn;
    }

    _buildCarouselWrap(carousel) {
      var wrap = document.createElement("div");
      wrap.className = "carousel-wrap";
      wrap.appendChild(carousel);

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
    _ensureGuideBuilt() {
      if (this._guideBuilt) return;
      var hass = this._hass;
      var self = this;
      var entities = this._resolveEntities();
      if (!entities.length) return;

      var root = this._els.guideRoot;
      root.innerHTML = "";

      var search = document.createElement("input");
      search.type = "text";
      search.className = "guide-search";
      search.placeholder = "Rechercher une chaine";
      root.appendChild(search);

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
      root.appendChild(daybar);

      var columns = document.createElement("div");
      columns.className = "guide-columns";
      columns.id = "slider";
      root.appendChild(self._buildCarouselWrap(columns));

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

      this._guideEls = { dayLabel: dayLabel, dayInput: dayInput, search: search, columns: columns };
      this._guideColRefs = colRefs;

      search.addEventListener("input", function () {
        self._applySearch(search.value);
      });
      prevBtn.addEventListener("click", function () {
        self._goToDate(new Date(self._guideDate.getTime() - 86400000));
      });
      nextBtn.addEventListener("click", function () {
        self._goToDate(new Date(self._guideDate.getTime() + 86400000));
      });
      dayLabel.addEventListener("click", function () {
        dayInput.value = isoDateLocal(self._guideDate);
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

      this._guideBuilt = true;
      this._goToDate(this._guideDate);
    }

    _applySearch(query) {
      var norm = normalizeSearch(query);
      var cols = this._guideEls.columns.querySelectorAll(".guide-column");
      cols.forEach(function (col) {
        var match = !norm || col.dataset.search.indexOf(norm) !== -1;
        col.classList.toggle("tntfr-hidden", !match);
      });
    }

    _goToDate(date) {
      this._guideDate = date;
      this._guideEls.dayLabel.textContent = dayLabelFr(date);
      var dateStr = isoDateLocal(date);
      if (this._guideCache[dateStr]) {
        this._renderGuideDay(dateStr);
      } else {
        this._fetchGuideDay(dateStr);
      }
    }

    _fetchGuideDay(dateStr) {
      var self = this;
      var channelIds = Object.keys(this._guideColRefs);
      channelIds.forEach(function (cid) {
        self._guideColRefs[cid].list.innerHTML = "";
        var loading = document.createElement("div");
        loading.className = "guide-loading";
        loading.textContent = "Chargement...";
        self._guideColRefs[cid].list.appendChild(loading);
      });

      this._hass.connection
        .sendMessagePromise({
          type: "programme_tnt_fr/programmes",
          channels: channelIds,
          date: dateStr
        })
        .then(function (resp) {
          self._guideCache[dateStr] = (resp && resp.programmes) || {};
          self._renderGuideDay(dateStr);
        })
        .catch(function (err) {
          console.error("programme-tnt-fr-card: guide fetch failed", err);
          Object.keys(self._guideColRefs).forEach(function (cid) {
            self._guideColRefs[cid].list.innerHTML = "";
            var msg = document.createElement("div");
            msg.className = "guide-empty";
            msg.textContent = "Erreur de chargement";
            self._guideColRefs[cid].list.appendChild(msg);
          });
        });
    }

    _renderGuideDay(dateStr) {
      var self = this;
      var dayData = this._guideCache[dateStr] || {};
      Object.keys(this._guideColRefs).forEach(function (channelId) {
        var ref = self._guideColRefs[channelId];
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

      var artUrl = prog.poster || prog.icon || channelIcon || null;
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
    description: "Programme TV des chaines francaises en 3 carrousels horizontaux (en ce moment / 1re et 2e partie de soiree), avec un bouton Guide TV dans l entete qui bascule vers une vue guide (2 chaines visibles, defilement par chaine, recherche, selecteur de jour)."
  });
})();
