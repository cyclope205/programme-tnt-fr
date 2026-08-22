/* Carte Lovelace "Programme TNT FR".
 * Servie automatiquement par l'integration Home Assistant du meme nom :
 * aucune configuration de ressource Lovelace manuelle n'est necessaire.
 * Utilisation minimale dans un tableau de bord :
 *   type: custom:programme-tnt-fr-card
 *
 * Presentation inspiree des carrousels "Programme TV" de Molotov : une
 * section par creneau (maintenant / ce soir / 2e partie de soiree), chacune
 * affichee sous forme de carrousel horizontal de vignettes par chaine.
 */
(function () {
  "use strict";

  var STYLE = [
    "ha-card { padding: 16px; }",
    ".header { font-size: 1.2em; font-weight: 500; margin-bottom: 14px; }",
    ".section { margin-bottom: 20px; }",
    ".section:last-child { margin-bottom: 0; }",
    ".section-title { font-size: 1em; font-weight: 600; margin-bottom: 10px; }",
    ".carousel { display: flex; gap: 10px; overflow-x: auto; overflow-y: hidden; padding-bottom: 6px; -webkit-overflow-scrolling: touch; scrollbar-width: thin; }",
    ".carousel::-webkit-scrollbar { height: 6px; }",
    ".carousel::-webkit-scrollbar-thumb { background: var(--divider-color, #ccc); border-radius: 3px; }",
    ".poster { position: relative; flex: 0 0 112px; width: 112px; height: 152px; border-radius: 10px; overflow: hidden; cursor: pointer; background: var(--secondary-background-color, #f2f2f2); border: none; padding: 0; font-family: inherit; text-align: left; }",
    ".poster-image { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }",
    ".poster-placeholder { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }",
    ".poster-placeholder img { width: 56%; height: 56%; object-fit: contain; opacity: 0.85; }",
    ".poster-scrim { position: absolute; left: 0; right: 0; bottom: 0; height: 65%; background: linear-gradient(to top, rgba(0,0,0,0.88), rgba(0,0,0,0)); }",
    ".poster-logo { position: absolute; left: 6px; bottom: 6px; width: 26px; height: 26px; object-fit: contain; border-radius: 4px; background: rgba(255,255,255,0.92); padding: 2px; }",
    ".poster-live { position: absolute; top: 6px; left: 6px; display: flex; align-items: center; gap: 4px; background: rgba(0,0,0,0.6); color: #fff; font-size: 0.6em; font-weight: 700; text-transform: uppercase; padding: 2px 6px; border-radius: 4px; }",
    ".poster-live-dot { width: 6px; height: 6px; border-radius: 50%; background: #e53935; flex-shrink: 0; }",
    ".poster-title { position: absolute; left: 6px; right: 6px; bottom: 7px; color: #fff; font-size: 0.72em; font-weight: 600; line-height: 1.25; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }",
    ".poster-progress { position: absolute; left: 0; right: 0; bottom: 0; height: 3px; background: rgba(255,255,255,0.3); }",
    ".poster-progress-fill { height: 100%; background: #e53935; }",
    ".empty { opacity: 0.7; font-style: italic; font-size: 0.9em; }",
    ".overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }",
    ".overlay[hidden] { display: none; }",
    ".modal { background: var(--card-background-color, #fff); color: var(--primary-text-color); border-radius: 12px; padding: 20px; max-width: 480px; width: 90%; max-height: 80vh; overflow-y: auto; position: relative; }",
    ".modal .close { position: absolute; top: 8px; right: 12px; background: none; border: none; font-size: 1.5em; cursor: pointer; color: var(--primary-text-color); }",
    ".modal-icon { width: 100%; max-height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 12px; }",
    ".modal-icon[hidden] { display: none; }",
    ".modal-title { margin: 0 0 4px 0; font-size: 1.2em; }",
    ".modal-subtitle { font-style: italic; opacity: 0.85; margin-bottom: 8px; }",
    ".modal-subtitle[hidden] { display: none; }",
    ".modal-meta { font-size: 0.85em; opacity: 0.7; margin-bottom: 12px; }",
    ".modal-desc { line-height: 1.4; white-space: pre-line; }"
  ].join("\n");

  var SECTIONS = [
    ["current", "En ce moment a la tele"],
    ["prime_time", "Ce soir"],
    ["second_part", "Deuxieme partie de soiree"]
  ];

  function channelName(hass, entityId) {
    var attrs = hass.states[entityId].attributes || {};
    return attrs.channel_name || entityId;
  }

  function channelLogo(hass, entityId) {
    var attrs = hass.states[entityId].attributes || {};
    return attrs.channel_icon || attrs.entity_picture || null;
  }

  function liveFraction(prog) {
    if (!prog || !prog.start || !prog.stop) return null;
    var start = new Date(prog.start).getTime();
    var stop = new Date(prog.stop).getTime();
    var now = Date.now();
    if (isNaN(start) || isNaN(stop) || stop <= start) return null;
    if (now < start || now >= stop) return null;
    var frac = (now - start) / (stop - start);
    if (frac < 0) frac = 0;
    if (frac > 1) frac = 1;
    return frac;
  }

  class ProgrammeTntFrCard extends HTMLElement {
    setConfig(config) {
      this._config = config || {};
      this._entities = this._config.entities || null;
      this._render();
    }

    set hass(hass) {
      this._hass = hass;
      this._render();
    }

    getCardSize() {
      return 5;
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
        return channelName(hass, a).localeCompare(channelName(hass, b), "fr", { sensitivity: "base" });
      });
      return ids;
    }

    _ensureDom() {
      if (this.shadowRoot) return;
      this.attachShadow({ mode: "open" });

      var style = document.createElement("style");
      style.textContent = STYLE;

      var card = document.createElement("ha-card");
      var header = document.createElement("div");
      header.className = "header";
      var sections = document.createElement("div");
      sections.className = "sections";

      var overlay = document.createElement("div");
      overlay.className = "overlay";
      overlay.hidden = true;
      var modal = document.createElement("div");
      modal.className = "modal";
      var closeBtn = document.createElement("button");
      closeBtn.className = "close";
      closeBtn.type = "button";
      closeBtn.setAttribute("aria-label", "Fermer");
      closeBtn.textContent = String.fromCharCode(215);
      var modalIcon = document.createElement("img");
      modalIcon.className = "modal-icon";
      modalIcon.hidden = true;
      modalIcon.alt = "";
      var modalTitle = document.createElement("h2");
      modalTitle.className = "modal-title";
      var modalSubtitle = document.createElement("div");
      modalSubtitle.className = "modal-subtitle";
      var modalMeta = document.createElement("div");
      modalMeta.className = "modal-meta";
      var modalDesc = document.createElement("p");
      modalDesc.className = "modal-desc";

      modal.appendChild(closeBtn);
      modal.appendChild(modalIcon);
      modal.appendChild(modalTitle);
      modal.appendChild(modalSubtitle);
      modal.appendChild(modalMeta);
      modal.appendChild(modalDesc);
      overlay.appendChild(modal);

      card.appendChild(header);
      card.appendChild(sections);
      card.appendChild(overlay);

      this.shadowRoot.appendChild(style);
      this.shadowRoot.appendChild(card);

      var self = this;
      overlay.addEventListener("click", function (ev) {
        if (ev.target === overlay || ev.target === closeBtn) {
          self._closeModal();
        }
      });

      this._els = {
        header: header,
        sections: sections,
        overlay: overlay,
        modalIcon: modalIcon,
        modalTitle: modalTitle,
        modalSubtitle: modalSubtitle,
        modalMeta: modalMeta,
        modalDesc: modalDesc
      };
    }

    _buildPoster(entityId, name, prog) {
      var self = this;
      var poster = document.createElement("button");
      poster.type = "button";
      poster.className = "poster";

      if (prog.icon) {
        var img = document.createElement("img");
        img.className = "poster-image";
        img.src = prog.icon;
        img.alt = "";
        poster.appendChild(img);
      } else {
        var placeholder = document.createElement("div");
        placeholder.className = "poster-placeholder";
        var logoBig = channelLogo(this._hass, entityId);
        if (logoBig) {
          var pimg = document.createElement("img");
          pimg.src = logoBig;
          pimg.alt = name;
          placeholder.appendChild(pimg);
        }
        poster.appendChild(placeholder);
      }

      var scrim = document.createElement("div");
      scrim.className = "poster-scrim";
      poster.appendChild(scrim);

      var frac = liveFraction(prog);
      if (frac !== null) {
        var live = document.createElement("div");
        live.className = "poster-live";
        var dot = document.createElement("span");
        dot.className = "poster-live-dot";
        live.appendChild(dot);
        live.appendChild(document.createTextNode("En direct"));
        poster.appendChild(live);

        var progress = document.createElement("div");
        progress.className = "poster-progress";
        var fill = document.createElement("div");
        fill.className = "poster-progress-fill";
        fill.style.width = Math.round(frac * 100) + "%";
        progress.appendChild(fill);
        poster.appendChild(progress);
      }

      var logoSrc = channelLogo(this._hass, entityId);
      if (logoSrc) {
        var logo = document.createElement("img");
        logo.className = "poster-logo";
        logo.src = logoSrc;
        logo.alt = name;
        logo.title = name;
        poster.appendChild(logo);
      }

      var titleEl = document.createElement("div");
      titleEl.className = "poster-title";
      titleEl.textContent = prog.title || name;
      poster.appendChild(titleEl);

      poster.title = name + (prog.title ? " - " + prog.title : "");

      poster.addEventListener("click", function () {
        self._openModal(name, prog);
      });

      return poster;
    }

    _render() {
      if (!this._hass || !this._config) return;
      this._ensureDom();

      var title = this._config.title !== undefined ? this._config.title : "Programme TNT";
      this._els.header.textContent = title || "";
      this._els.header.style.display = title ? "block" : "none";

      var entities = this._resolveEntities();
      var sectionsEl = this._els.sections;
      sectionsEl.innerHTML = "";

      if (!entities.length) {
        var empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "Aucune chaine trouvee. Verifiez la configuration de l'integration Programme TNT FR.";
        sectionsEl.appendChild(empty);
        return;
      }

      var self = this;
      SECTIONS.forEach(function (def) {
        var key = def[0];
        var label = def[1];

        var section = document.createElement("div");
        section.className = "section";
        var titleEl = document.createElement("div");
        titleEl.className = "section-title";
        titleEl.textContent = label;
        section.appendChild(titleEl);

        var carousel = document.createElement("div");
        carousel.className = "carousel";

        var count = 0;
        entities.forEach(function (entityId) {
          var state = self._hass.states[entityId];
          var attrs = state.attributes || {};
          var name = attrs.channel_name || entityId;
          var prog = attrs[key];
          if (!prog) return;
          carousel.appendChild(self._buildPoster(entityId, name, prog));
          count++;
        });

        if (count === 0) {
          var none = document.createElement("div");
          none.className = "empty";
          none.textContent = "Aucun programme disponible.";
          section.appendChild(none);
        } else {
          section.appendChild(carousel);
        }

        sectionsEl.appendChild(section);
      });
    }

    _openModal(channelLabel, prog) {
      var els = this._els;
      els.modalTitle.textContent = prog.title || "";

      if (prog.subtitle) {
        els.modalSubtitle.textContent = prog.subtitle;
        els.modalSubtitle.hidden = false;
      } else {
        els.modalSubtitle.hidden = true;
      }

      var bits = [];
      if (channelLabel) bits.push(channelLabel);
      if (prog.start) {
        var start = new Date(prog.start);
        if (!isNaN(start.getTime())) {
          var hh = String(start.getHours()).padStart(2, "0");
          var mm = String(start.getMinutes()).padStart(2, "0");
          bits.push(hh + ":" + mm);
        }
      }
      if (prog.category) bits.push(prog.category);
      if (prog.rating) bits.push(prog.rating);
      els.modalMeta.textContent = bits.join(" " + String.fromCharCode(8226) + " ");

      els.modalDesc.textContent = prog.description || "Aucune description disponible.";

      if (prog.icon) {
        els.modalIcon.src = prog.icon;
        els.modalIcon.hidden = false;
      } else {
        els.modalIcon.hidden = true;
      }

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
    description: "Programme TV des chaines de la TNT francaise, en carrousels par creneau (maintenant / ce soir / 2e partie de soiree), avec details au clic."
  });
})();
