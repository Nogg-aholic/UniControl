class UniversalControllerCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    this.config = config;
    this.render();
  }

  configChanged(newConfig) {
    const event = new Event('config-changed', {
      bubbles: true,
      composed: true,
    });
    event.detail = { config: newConfig };
    this.dispatchEvent(event);
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        .card-config {
          padding: 16px;
        }
        .form-group {
          margin-bottom: 16px;
        }
        label {
          display: block;
          margin-bottom: 4px;
          font-weight: 500;
        }
        input, select {
          width: 100%;
          padding: 8px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          font-family: inherit;
        }
      </style>
      <div class="card-config">
        <div class="form-group">
          <label for="entity">Entity</label>
          <select id="entity">
            <option value="">Select Universal Controller Entity</option>
          </select>
        </div>
        <div class="form-group">
          <label for="title">Title (optional)</label>
          <input id="title" type="text" value="${this.config?.title || ''}" />
        </div>
      </div>
    `;

    // Populate entity dropdown
    this.populateEntityDropdown();

    // Add event listeners
    this.shadowRoot.getElementById('entity').addEventListener('change', (e) => {
      this.configChanged({ ...this.config, entity: e.target.value });
    });

    this.shadowRoot.getElementById('title').addEventListener('input', (e) => {
      this.configChanged({ ...this.config, title: e.target.value });
    });
  }

  populateEntityDropdown() {
    const entitySelect = this.shadowRoot.getElementById('entity');
    if (!this._hass) return;

    // Filter for Universal Controller entities
    const entities = Object.keys(this._hass.states).filter(
      entityId => entityId.startsWith('sensor.') && 
      this._hass.states[entityId].attributes.html_template !== undefined
    );

    entities.forEach(entityId => {
      const option = document.createElement('option');
      option.value = entityId;
      option.textContent = this._hass.states[entityId].attributes.friendly_name || entityId;
      option.selected = entityId === this.config?.entity;
      entitySelect.appendChild(option);
    });
  }

  set hass(hass) {
    this._hass = hass;
    this.populateEntityDropdown();
  }
}

customElements.define('universal-controller-card-editor', UniversalControllerCardEditor);
