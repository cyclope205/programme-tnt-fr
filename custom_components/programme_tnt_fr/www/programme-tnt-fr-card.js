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
    ".header { font-size: 1.2em; font-weight: 500; margin-bottom: 14px; }",
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
    ".poster-card { position: relative; flex: 0 0 230px; width: 230px; aspect-ratio: 2 / 3; border-radius: 18px; overflow: hidden; border: none; padding: 0; margin: 0; cursor: pointer; scroll-snap-align: start; background: linear-gradient(160deg, #5b4fc4 0%, #2c2560 55%, #12102b 100%); box-shadow: 0 10px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06); transition: transform 0.15s ease, box-shadow 0.15s ease; font-family: inherit; -webkit-tap-highlight-color: transparent; }",
    ".poster-card:active { transform: scale(0.97); }",
    ".poster-card:disabled { cursor: default; opacity: 0.55; }",
    ".poster-bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }",
    ".poster-watermark { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; opacity: 0.16; }",
    ".poster-watermark img { width: 52%; height: 52%; object-fit: contain; filter: brightness(0) invert(1); }",
    ".poster-scrim { position: absolute; left: 0; right: 0; bottom: 0; height: 62%; background: linear-gradient(to top, rgba(0,0,0,0.94) 8%, rgba(0,0,0,0.72) 42%, rgba(0,0,0,0) 100%); }",
    ".poster-channel-badge { position: absolute; top: 10px; left: 10px; width: 34px; height: 34px; border-radius: 50%; background: #fff; padding: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.45); object-fit: contain; z-index: 1; }",
    ".poster-live-badge { position: absolute; top: 10px; right: 10px; display: flex; align-items: center; gap: 5px; background: rgba(224,38,63,0.94); color: #fff; font-size: 0.66em; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; padding: 5px 10px 5px 8px; border-radius: 20px; box-shadow: 0 2px 10px rgba(224,38,63,0.5); z-index: 1; }",
    ".poster-live-dot { width: 6px; height: 6px; border-radius: 50%; background: #fff; animation: tntfr-pulse 1.6s infinite; }",
    "@keyframes tntfr-pulse { 0% { box-shadow: 0 0 0 0 rgba(255,255,255,0.7); } 70% { box-shadow: 0 0 0 6px rgba(255,255,255,0); } 100% { box-shadow: 0 0 0 0 rgba(255,255,255,0); } }",
    ".poster-content { position: absolute; left: 0; right: 0; bottom: 0; padding: 12px 14px 14px; color: #fff; }",
    ".poster-channel-name { font-size: 0.72em; font-weight: 700; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 4px; text-shadow: 0 1px 2px rgba(0,0,0,0.85); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }",
    ".poster-title { font-size: 1.02em; font-weight: 700; line-height: 1.28; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-shadow: 0 1px 3px rgba(0,0,0,0.85); }",
    ".poster-time { font-size: 0.76em; font-weight: 600; opacity: 0.9; margin-top: 6px; text-shadow: 0 1px 2px rgba(0,0,0,0.85); }",
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
    ".modal-desc { line-height: 1.45; white-space: pre-line; }"
  ].join("\n");

  var SLOT_DEFS = [
    ["current", "En ce moment", "live"],
    ["prime_time", "1re partie de soiree", "prime"],
    ["second_part", "2e partie de soiree", "second"]
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

  class ProgrammeTntFrCard extends HTMLElement {
    setConfig(config) {
      this._config = config || {};
      this._entities = this._config.entities || null;
      this._built = false;
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

    _buildPosterCard(channelLabel, slotKey, prog, channelIcon) {
      var self = this;
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "poster-card";

      if (channelIcon) {
        var badge = document.createElement("img");
        badge.className = "poster-channel-badge";
        badge.src = channelIcon;
        badge.alt = "";
        btn.appendChild(badge);
      }

      if (!prog) {
        btn.disabled = true;
        var empty = document.createElement("div");
        empty.className = "poster-empty-msg";
        empty.textContent = "Pas de programme";
        btn.appendChild(empty);
        return btn;
      }

      var artUrl = prog.icon || null;
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
            btn.insertBefore(wm, btn.firstChild);
          }
        });
        btn.insertBefore(img, btn.firstChild);
      } else if (channelIcon) {
        var wm2 = document.createElement("div");
        wm2.className = "poster-watermark";
        var wmImg2 = document.createElement("img");
        wmImg2.src = channelIcon;
        wm2.appendChild(wmImg2);
        btn.insertBefore(wm2, btn.firstChild);
      }

      var scrim = document.createElement("div");
      scrim.className = "poster-scrim";
      btn.appendChild(scrim);

      var startFmt = formatTime(prog.start);
      var stopFmt = formatTime(prog.stop);

      if (slotKey === "current") {
        var live = document.createElement("div");
        live.className = "poster-live-badge";
        var dot = document.createElement("span");
        dot.className = "poster-live-dot";
        live.appendChild(dot);
        live.appendChild(document.createTextNode("Direct"));
        btn.appendChild(live);
      }

      var content = document.createElement("div");
      content.className = "poster-content";

      var chanEl = document.createElement("div");
      chanEl.className = "poster-channel-name";
      chanEl.textContent = channelLabel;
      content.appendChild(chanEl);

      var titleEl = document.createElement("div");
      titleEl.className = "poster-title";
      titleEl.textContent = prog.title || "";
      content.appendChild(titleEl);

      var timeEl = document.createElement("div");
      timeEl.className = "poster-time";
      timeEl.textContent = (startFmt || "?") + " - " + (stopFmt || "?");
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
          btn.appendChild(track);
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

    _render() {
      this._ensureDom();
      var hass = this._hass;
      var els = this._els;
      els.header.textContent = this._config.title || "Programme TNT";

      if (!hass) {
        els.body.innerHTML = "";
        return;
      }

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
      return { title: "Programme TNT" };
    }
  }

  customElements.define("programme-tnt-fr-card", ProgrammeTntFrCard);

  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "programme-tnt-fr-card",
    name: "Programme TNT FR",
    description: "Programme TV des chaines de la TNT francaise en 3 carrousels horizontaux (en ce moment / 1re et 2e partie de soiree), une vignette par chaine classee dans l'ordre officiel, avec details au clic."
  });
})();
