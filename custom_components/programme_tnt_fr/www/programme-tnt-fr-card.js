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
    ".channel-section { margin-bottom: 20px; }",
    ".channel-section:last-child { margin-bottom: 0; }",
    ".channel-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }",
    ".channel-logo { width: 28px; height: 28px; object-fit: contain; border-radius: 6px; background: #fff; padding: 2px; flex-shrink: 0; }",
    ".channel-name { font-weight: 600; font-size: 0.98em; color: var(--primary-text-color); }",
    ".carousel-wrap { position: relative; }",
    ".carousel { display: flex; gap: 10px; overflow-x: auto; overflow-y: hidden; padding-bottom: 2px; scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch; scroll-behavior: smooth; }",
    ".carousel::-webkit-scrollbar { display: none; }",
    ".carousel { scrollbar-width: none; }",
    ".poster-card { position: relative; flex: 0 0 138px; width: 138px; aspect-ratio: 2 / 3; border-radius: 14px; overflow: hidden; border: none; padding: 0; margin: 0; cursor: pointer; scroll-snap-align: start; background: linear-gradient(145deg, #454b6b, #1c1e2e); box-shadow: 0 3px 10px rgba(0,0,0,0.3); transition: transform 0.12s ease; font-family: inherit; -webkit-tap-highlight-color: transparent; }",
    ".poster-card:active { transform: scale(0.96); }",
    ".poster-card:disabled { cursor: default; opacity: 0.55; }",
    ".poster-bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }",
    ".poster-watermark { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; opacity: 0.18; }",
    ".poster-watermark img { width: 56%; height: 56%; object-fit: contain; filter: brightness(0) invert(1); }",
    ".poster-scrim { position: absolute; left: 0; right: 0; bottom: 0; height: 78%; background: linear-gradient(to top, rgba(0,0,0,0.95) 12%, rgba(0,0,0,0.75) 48%, rgba(0,0,0,0) 100%); }",
    ".poster-badge { position: absolute; top: 8px; left: 8px; font-size: 0.62em; font-weight: 700; letter-spacing: 0.03em; text-transform: uppercase; padding: 3px 7px; border-radius: 20px; color: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.4); }",
    ".poster-badge.live { background: #e0263f; }",
    ".poster-badge.prime { background: #3f6fe0; }",
    ".poster-badge.second { background: #1c9c8a; }",
    ".poster-content { position: absolute; left: 0; right: 0; bottom: 0; padding: 8px 10px 10px; color: #fff; }",
    ".poster-title { font-size: 0.84em; font-weight: 700; line-height: 1.25; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; text-shadow: 0 1px 3px rgba(0,0,0,0.85); }",
    ".poster-time { font-size: 0.68em; font-weight: 600; opacity: 0.9; margin-top: 4px; text-shadow: 0 1px 2px rgba(0,0,0,0.85); }",
    ".poster-progress-track { position: absolute; left: 0; right: 0; bottom: 0; height: 3px; background: rgba(255,255,255,0.25); }",
    ".poster-progress-fill { position: absolute; left: 0; bottom: 0; height: 3px; background: #e0263f; }",
    ".poster-empty-msg { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; padding: 10px; text-align: center; font-size: 0.78em; opacity: 0.7; font-style: italic; color: var(--primary-text-color); }",
    ".carousel-nav { position: absolute; top: 50%; transform: translateY(-50%); width: 30px; height: 30px; border-radius: 50%; border: none; background: rgba(20,20,30,0.72); color: #fff; font-size: 1.2em; line-height: 1; cursor: pointer; display: flex; align-items: center; justify-content: center; z-index: 2; opacity: 0; transition: opacity 0.15s ease; padding: 0; box-shadow: 0 1px 4px rgba(0,0,0,0.4); }",
    ".carousel-wrap:hover .carousel-nav.visible { opacity: 1; }",
    ".carousel-nav.visible:hover { background: rgba(20,20,30,0.9); }",
    ".carousel-nav.prev { left: 2px; }",
    ".carousel-nav.next { right: 2px; }",
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
    ["current", "En direct", "live"],
    ["prime_time", "1re partie", "prime"],
    ["second_part", "2e partie", "second"]
  ];

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
      return 1 + this._resolveEntities().length * 2;
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

    _buildPosterCard(channelLabel, slotKey, slotLabel, badgeClass, prog, channelIcon) {
      var self = this;
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "poster-card";

      if (!prog) {
        btn.disabled = true;
        var empty = document.createElement("div");
        empty.className = "poster-empty-msg";
        empty.textContent = "Pas de programme";
        btn.appendChild(empty);
        var badgeEmpty = document.createElement("div");
        badgeEmpty.className = "poster-badge " + badgeClass;
        badgeEmpty.textContent = slotLabel;
        btn.appendChild(badgeEmpty);
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
        btn.appendChild(img);
      } else if (channelIcon) {
        var wm2 = document.createElement("div");
        wm2.className = "poster-watermark";
        var wmImg2 = document.createElement("img");
        wmImg2.src = channelIcon;
        wm2.appendChild(wmImg2);
        btn.appendChild(wm2);
      }

      var scrim = document.createElement("div");
      scrim.className = "poster-scrim";
      btn.appendChild(scrim);

      var badge = document.createElement("div");
      badge.className = "poster-badge " + badgeClass;
      var startFmt = formatTime(prog.start);
      badge.textContent = startFmt ? slotLabel + " " + startFmt : slotLabel;
      btn.appendChild(badge);

      var content = document.createElement("div");
      content.className = "poster-content";
      var titleEl = document.createElement("div");
      titleEl.className = "poster-title";
      titleEl.textContent = prog.title || "";
      content.appendChild(titleEl);

      var timeEl = document.createElement("div");
      timeEl.className = "poster-time";
      var stopFmt = formatTime(prog.stop);
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
      prevBtn.textContent = "‹";

      var nextBtn = document.createElement("button");
      nextBtn.type = "button";
      nextBtn.className = "carousel-nav next";
      nextBtn.setAttribute("aria-label", "Suivant");
      nextBtn.textContent = "›";

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

      els.body.innerHTML = "";
      if (!hass) return;

      var entities = this._resolveEntities();
      var self = this;
      entities.forEach(function (entityId) {
        var attrs = hass.states[entityId].attributes || {};
        var channelLabel = attrs.channel_name || entityId;
        var channelIcon = attrs.channel_icon || null;

        var section = document.createElement("div");
        section.className = "channel-section";

        var headerRow = document.createElement("div");
        headerRow.className = "channel-header";
        if (channelIcon) {
          var logo = document.createElement("img");
          logo.className = "channel-logo";
          logo.src = channelIcon;
          logo.alt = "";
          headerRow.appendChild(logo);
        }
        var nameEl = document.createElement("div");
        nameEl.className = "channel-name";
        nameEl.textContent = channelLabel;
        headerRow.appendChild(nameEl);
        section.appendChild(headerRow);

        var carousel = document.createElement("div");
        carousel.className = "carousel";
        SLOT_DEFS.forEach(function (def) {
          var slotKey = def[0], slotLabel = def[1], badgeClass = def[2];
          var prog = attrs[slotKey];
          var card = self._buildPosterCard(channelLabel, slotKey, slotLabel, badgeClass, prog, channelIcon);
          carousel.appendChild(card);
        });

        section.appendChild(self._buildCarouselWrap(carousel));
        els.body.appendChild(section);
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
    description: "Programme TV des chaines de la TNT francaise en carrousel de vignettes (maintenant / 1re et 2e partie de soiree), classees dans l'ordre officiel des chaines, avec details au clic."
  });
})();
