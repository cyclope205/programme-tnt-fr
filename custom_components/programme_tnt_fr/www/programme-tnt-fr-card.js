/* Carte Lovelace "Programme TNT FR".
 * Servie automatiquement par l'integration Home Assistant du meme nom :
 * aucune configuration de ressource Lovelace manuelle n'est necessaire.
 * Utilisation minimale dans un tableau de bord :
 *   type: custom:programme-tnt-fr-card
 */
(function () {
  "use strict";

  var STYLE = [
    "ha-card { padding: 16px; }",
    ".header { font-size: 1.2em; font-weight: 500; margin-bottom: 12px; }",
    ".channel-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--divider-color, #e0e0e0); }",
    ".channel-row:last-child { border-bottom: none; }",
    ".channel-info { display: flex; align-items: center; gap: 8px; width: 110px; flex-shrink: 0; }",
    ".channel-logo { width: 32px; height: 32px; object-fit: contain; border-radius: 4px; background: var(--card-background-color, #fff); }",
    ".channel-name { font-size: 0.85em; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }",
    ".slots { display: flex; flex: 1; gap: 8px; min-width: 0; }",
    ".slot { flex: 1; min-width: 0; text-align: left; background: var(--secondary-background-color, #f2f2f2); border: none; border-radius: 8px; padding: 6px 8px; cursor: pointer; font-family: inherit; color: var(--primary-text-color); }",
    ".slot:disabled { opacity: 0.4; cursor: default; }",
    ".slot-label { font-size: 0.7em; opacity: 0.7; text-transform: uppercase; }",
    ".slot-title { font-size: 0.85em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: 2px; }",
    ".empty { opacity: 0.7; font-style: italic; }",
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

  var SLOT_DEFS = [
    ["current", "En ce moment"],
    ["prime_time", "1re partie de soiree"],
    ["second_part", "2e partie de soiree"]
  ];

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
      return 1 + this._resolveEntities().length;
    }

    _resolveEntities() {
      var hass = this._hass;
      if (!hass) return [];
      if (this._entities && this._entities.length) {
        return this._entities.filter(function (id) {
          return !!hass.states[id];
        });
      }
      var ids = Object.keys(hass.states).filter(function (id) {
        var st = hass.states[id];
        return id.indexOf("sensor.") === 0 && st.attributes && st.attributes.channel_id;
      });
      ids.sort(function (a, b) {
        var na = hass.states[a].attributes.channel_name || a;
        var nb = hass.states[b].attributes.channel_name || b;
        return na.localeCompare(nb);
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
      var rows = document.createElement("div");
      rows.className = "rows";

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
      card.appendChild(rows);
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
        rows: rows,
        overlay: overlay,
        modalIcon: modalIcon,
        modalTitle: modalTitle,
        modalSubtitle: modalSubtitle,
        modalMeta: modalMeta,
        modalDesc: modalDesc
      };
    }

    _render() {
      if (!this._hass || !this._config) return;
      this._ensureDom();

      var title = this._config.title !== undefined ? this._config.title : "Programme TNT";
      this._els.header.textContent = title || "";
      this._els.header.style.display = title ? "block" : "none";

      var entities = this._resolveEntities();
      var rows = this._els.rows;
      rows.innerHTML = "";

      if (!entities.length) {
        var empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "Aucune chaine trouvee. Verifiez la configuration de l'integration Programme TNT FR.";
        rows.appendChild(empty);
        return;
      }

      var self = this;
      entities.forEach(function (entityId) {
        var state = self._hass.states[entityId];
        var attrs = state.attributes || {};

        var row = document.createElement("div");
        row.className = "channel-row";

        var chan = document.createElement("div");
        chan.className = "channel-info";
        var logoSrc = attrs.channel_icon || attrs.entity_picture;
        if (logoSrc) {
          var img = document.createElement("img");
          img.src = logoSrc;
          img.className = "channel-logo";
          img.alt = "";
          chan.appendChild(img);
        }
        var name = document.createElement("span");
        name.className = "channel-name";
        name.textContent = attrs.channel_name || entityId;
        chan.appendChild(name);
        row.appendChild(chan);

        var slots = document.createElement("div");
        slots.className = "slots";

        SLOT_DEFS.forEach(function (def) {
          var key = def[0];
          var label = def[1];
          var prog = attrs[key];

          var cell = document.createElement("button");
          cell.type = "button";
          cell.className = "slot";

          var labelEl = document.createElement("div");
          labelEl.className = "slot-label";
          labelEl.textContent = label;

          var titleEl = document.createElement("div");
          titleEl.className = "slot-title";
          titleEl.textContent = prog && prog.title ? prog.title : String.fromCharCode(8212);

          cell.appendChild(labelEl);
          cell.appendChild(titleEl);

          if (prog) {
            cell.addEventListener("click", function () {
              self._openModal(attrs.channel_name || entityId, prog);
            });
          } else {
            cell.disabled = true;
          }
          slots.appendChild(cell);
        });

        row.appendChild(slots);
        rows.appendChild(row);
      });
    }

    _openModal(channelName, prog) {
      var els = this._els;
      els.modalTitle.textContent = prog.title || "";

      if (prog.subtitle) {
        els.modalSubtitle.textContent = prog.subtitle;
        els.modalSubtitle.hidden = false;
      } else {
        els.modalSubtitle.hidden = true;
      }

      var bits = [];
      if (channelName) bits.push(channelName);
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
    description: "Programme TV des chaines de la TNT francaise (maintenant / 1re et 2e partie de soiree), avec details au clic."
  });
})();
