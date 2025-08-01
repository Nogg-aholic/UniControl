class UniversalControllerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity');
    }
    this.config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  render() {
    if (!this._hass || !this.config) {
      return;
    }

    const entity = this._hass.states[this.config.entity];
    if (!entity) {
      this.shadowRoot.innerHTML = `
        <div style="padding: 16px; background: var(--error-color); color: white;">
          Entity "${this.config.entity}" not found
        </div>
      `;
      return;
    }

    const attributes = entity.attributes;
    const htmlTemplate = attributes.html_template || '<div>No HTML template defined</div>';
    const cssStyles = attributes.css_styles || '';
    
    // Enhanced template replacement with advanced features
    let renderedHtml = this.renderTemplate(htmlTemplate, entity, attributes);

    // Show editor if in edit mode
    if (this.config.show_editor) {
      this.renderEditor(entity, attributes);
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }
        .universal-controller-card {
          background: var(--card-background-color);
          border-radius: var(--ha-card-border-radius);
          box-shadow: var(--ha-card-box-shadow);
          overflow: hidden;
        }
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          border-bottom: 1px solid var(--divider-color);
          background: var(--primary-color);
          color: var(--text-primary-color);
        }
        .title {
          font-size: 1.2em;
          font-weight: 500;
        }
        .controls {
          display: flex;
          gap: 8px;
        }
        .btn {
          padding: 4px 8px;
          border: none;
          border-radius: 4px;
          background: rgba(255,255,255,0.2);
          color: white;
          cursor: pointer;
          font-size: 0.8em;
        }
        .btn:hover {
          background: rgba(255,255,255,0.3);
        }
        .status {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 16px;
          background: var(--secondary-background-color);
          font-size: 0.9em;
          color: var(--secondary-text-color);
        }
        .status-item {
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .status-label {
          font-size: 0.8em;
          opacity: 0.7;
        }
        .content {
          padding: 16px;
          color: var(--primary-text-color);
        }
        .error {
          color: var(--error-color);
          background: var(--error-state-color);
          padding: 8px;
          border-radius: 4px;
          margin: 8px 16px;
        }
        .ticker-running {
          color: var(--success-color);
        }
        .ticker-stopped {
          color: var(--warning-color);
        }
        ${cssStyles}
      </style>
      <div class="universal-controller-card">
        <div class="header">
          <div class="title">${this.config.title || entity.attributes.friendly_name || 'Universal Controller'}</div>
          <div class="controls">
            <button class="btn" onclick="this.getRootNode().host.executeNow()">Execute Now</button>
            <button class="btn" onclick="this.getRootNode().host.toggleEditor()">Edit</button>
          </div>
        </div>
        <div class="status">
          <div class="status-item">
            <div class="status-label">Last Execution</div>
            <div>${attributes.last_execution ? new Date(attributes.last_execution).toLocaleTimeString() : 'Never'}</div>
          </div>
          <div class="status-item">
            <div class="status-label">Executions</div>
            <div>${attributes.execution_count || 0}</div>
          </div>
          <div class="status-item">
            <div class="status-label">Interval</div>
            <div>${attributes.interval || 0}s</div>
          </div>
          <div class="status-item">
            <div class="status-label">Ticker</div>
            <div class="${attributes.ticker_running ? 'ticker-running' : 'ticker-stopped'}">
              ${attributes.ticker_running ? 'Running' : 'Stopped'}
            </div>
          </div>
        </div>
        ${attributes.last_error ? `<div class="error">Error: ${attributes.last_error}</div>` : ''}
        <div class="content">
          ${renderedHtml}
        </div>
      </div>
    `;
  }

  renderEditor(entity, attributes) {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }
        .editor {
          background: var(--card-background-color);
          border-radius: var(--ha-card-border-radius);
          box-shadow: var(--ha-card-box-shadow);
          overflow: hidden;
        }
        .editor-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          border-bottom: 1px solid var(--divider-color);
          background: var(--primary-color);
          color: var(--text-primary-color);
        }
        .editor-title {
          font-size: 1.2em;
          font-weight: 500;
        }
        .editor-controls {
          display: flex;
          gap: 8px;
        }
        .btn {
          padding: 6px 12px;
          border: none;
          border-radius: 4px;
          background: rgba(255,255,255,0.2);
          color: white;
          cursor: pointer;
          font-size: 0.9em;
        }
        .btn:hover {
          background: rgba(255,255,255,0.3);
        }
        .btn-primary {
          background: var(--accent-color);
        }
        .btn-primary:hover {
          background: var(--accent-color);
          opacity: 0.8;
        }
        .editor-content {
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .form-group {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .form-label {
          font-weight: 500;
          color: var(--primary-text-color);
        }
        .form-input {
          padding: 8px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          background: var(--secondary-background-color);
          color: var(--primary-text-color);
          font-family: monospace;
        }
        .form-textarea {
          min-height: 100px;
          resize: vertical;
          font-family: monospace;
          font-size: 0.9em;
        }
        .form-input[type="number"] {
          font-family: inherit;
        }
        .preview {
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          padding: 16px;
          background: var(--secondary-background-color);
        }
        .preview-title {
          font-weight: 500;
          margin-bottom: 8px;
          color: var(--primary-text-color);
        }
      </style>
      <div class="editor">
        <div class="editor-header">
          <div class="editor-title">Edit Universal Controller Entity</div>
          <div class="editor-controls">
            <button class="btn" onclick="this.getRootNode().host.previewChanges()">Preview</button>
            <button class="btn btn-primary" onclick="this.getRootNode().host.saveChanges()">Save</button>
            <button class="btn" onclick="this.getRootNode().host.toggleEditor()">Cancel</button>
          </div>
        </div>
        <div class="editor-content">
          <div class="form-group">
            <label class="form-label">Execution Interval (seconds)</label>
            <input type="number" class="form-input" id="interval" value="${attributes.interval || 60}" min="1" max="3600">
          </div>
          
          <div class="form-group">
            <label class="form-label">HTML Template</label>
            <textarea class="form-input form-textarea" id="html_template" placeholder="Enter HTML template...">${attributes.html_template || ''}</textarea>
          </div>
          
          <div class="form-group">
            <label class="form-label">CSS Styles</label>
            <textarea class="form-input form-textarea" id="css_styles" placeholder="Enter CSS styles...">${attributes.css_styles || ''}</textarea>
          </div>
          
          <div class="form-group">
            <label class="form-label">TypeScript/JavaScript Code</label>
            <textarea class="form-input form-textarea" id="typescript_code" placeholder="Enter TypeScript/JavaScript code...">${attributes.typescript_code || ''}</textarea>
          </div>
          
          ${this.config.show_preview ? `
          <div class="form-group">
            <div class="preview-title">Preview</div>
            <div class="preview" id="preview">
              ${this.renderPreview(attributes)}
            </div>
          </div>
          ` : ''}
        </div>
      </div>
    `;
  }

  renderPreview(attributes) {
    const htmlTemplate = this.shadowRoot.getElementById('html_template')?.value || attributes.html_template || '';
    const cssStyles = this.shadowRoot.getElementById('css_styles')?.value || attributes.css_styles || '';
    
    let renderedHtml = htmlTemplate;
    
    // Simple template replacements for preview
    renderedHtml = renderedHtml.replace(/\{\{state\}\}/g, 'preview_state');
    renderedHtml = renderedHtml.replace(/\{\{entity_id\}\}/g, this.config.entity);
    renderedHtml = renderedHtml.replace(/\{\{friendly_name\}\}/g, 'Preview Entity');
    
    return `
      <style>${cssStyles}</style>
      ${renderedHtml}
    `;
  }

  renderTemplate(template, entity, attributes) {
    // Advanced template renderer that supports conditionals, loops, and functions
    let rendered = template;
    
    // Create context for template rendering
    const context = {
      state: entity.state,
      entity_id: entity.entity_id,
      friendly_name: attributes.friendly_name || entity.entity_id,
      attributes: attributes,
      result: attributes.execution_result || {},
      now: new Date().toISOString(),
      states: this._hass.states
    };
    
    // If execution result is an object, merge its properties into context
    if (attributes.execution_result && typeof attributes.execution_result === 'object') {
      Object.assign(context, attributes.execution_result);
    }
    
    try {
      // Apply variable substitutions first
      rendered = this.applyVariableSubstitutions(rendered, context);
      
      // Apply conditional blocks
      rendered = this.applyConditionals(rendered, context);
      
      // Apply loops
      rendered = this.applyLoops(rendered, context);
      
      // Apply function calls
      rendered = this.applyFunctions(rendered, context);
      
      return rendered;
    } catch (error) {
      console.error('Template rendering error:', error);
      return `<div class="error">Template error: ${error.message}</div>`;
    }
  }

  applyVariableSubstitutions(template, context) {
    // Replace {{variable}} patterns
    return template.replace(/\{\{([^}]+)\}\}/g, (match, variable) => {
      const path = variable.trim();
      try {
        const value = this.getNestedValue(context, path);
        return this.formatValue(value);
      } catch (e) {
        return match; // Keep original if not found
      }
    });
  }

  applyConditionals(template, context) {
    // Handle {% if condition %}...{% endif %} blocks
    return template.replace(/\{%\s*if\s+([^%]+)\s*%\}(.*?)\{%\s*endif\s*%\}/gs, (match, condition, content) => {
      try {
        if (this.evaluateCondition(condition.trim(), context)) {
          return content;
        }
        return '';
      } catch (e) {
        console.warn('Conditional evaluation error:', e);
        return '';
      }
    });
  }

  applyLoops(template, context) {
    // Handle {% for item in items %}...{% endfor %} blocks
    return template.replace(/\{%\s*for\s+(\w+)\s+in\s+([^%]+)\s*%\}(.*?)\{%\s*endfor\s*%\}/gs, (match, varName, iterablePath, content) => {
      try {
        const iterable = this.getNestedValue(context, iterablePath.trim());
        if (!Array.isArray(iterable) && typeof iterable !== 'object') {
          return '';
        }
        
        const items = Array.isArray(iterable) ? iterable : Object.values(iterable);
        return items.map(item => {
          const loopContext = { ...context, [varName]: item };
          return this.applyVariableSubstitutions(content, loopContext);
        }).join('');
      } catch (e) {
        console.warn('Loop evaluation error:', e);
        return '';
      }
    });
  }

  applyFunctions(template, context) {
    // Handle {{ function(args) }} patterns
    return template.replace(/\{\{\s*(\w+)\(([^)]*)\)\s*\}\}/g, (match, funcName, argsStr) => {
      try {
        const args = this.parseArgs(argsStr, context);
        const result = this.callFunction(funcName, args, context);
        return this.formatValue(result);
      } catch (e) {
        console.warn(`Function call error for ${funcName}:`, e);
        return match;
      }
    });
  }

  getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => {
      if (current && typeof current === 'object' && key in current) {
        return current[key];
      }
      throw new Error(`Path '${path}' not found`);
    }, obj);
  }

  evaluateCondition(condition, context) {
    // Simple condition evaluation
    if (condition.includes(' == ')) {
      const [left, right] = condition.split(' == ').map(s => s.trim());
      return String(this.resolveValue(left, context)) === String(this.resolveValue(right, context));
    }
    if (condition.includes(' != ')) {
      const [left, right] = condition.split(' != ').map(s => s.trim());
      return String(this.resolveValue(left, context)) !== String(this.resolveValue(right, context));
    }
    if (condition.includes(' > ')) {
      const [left, right] = condition.split(' > ').map(s => s.trim());
      return Number(this.resolveValue(left, context)) > Number(this.resolveValue(right, context));
    }
    if (condition.includes(' < ')) {
      const [left, right] = condition.split(' < ').map(s => s.trim());
      return Number(this.resolveValue(left, context)) < Number(this.resolveValue(right, context));
    }
    
    // Simple truthiness test
    return Boolean(this.resolveValue(condition, context));
  }

  resolveValue(value, context) {
    // If it's a string literal
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      return value.slice(1, -1);
    }
    // If it's a number
    if (!isNaN(value)) {
      return Number(value);
    }
    // Otherwise treat as variable path
    try {
      return this.getNestedValue(context, value);
    } catch (e) {
      return value;
    }
  }

  parseArgs(argsStr, context) {
    if (!argsStr.trim()) return [];
    
    return argsStr.split(',').map(arg => {
      const trimmed = arg.trim();
      return this.resolveValue(trimmed, context);
    });
  }

  callFunction(funcName, args, context) {
    const functions = {
      now: () => new Date().toISOString(),
      format_date: (dateStr, format = 'locale') => {
        try {
          const date = new Date(dateStr);
          return format === 'locale' ? date.toLocaleString() : date.toLocaleDateString();
        } catch (e) {
          return dateStr;
        }
      },
      upper: (text) => String(text).toUpperCase(),
      lower: (text) => String(text).toLowerCase(),
      length: (obj) => obj ? (obj.length !== undefined ? obj.length : Object.keys(obj).length) : 0,
      round: (num, digits = 0) => Number(num).toFixed(digits),
      default: (value, defaultVal) => (value !== null && value !== undefined) ? value : defaultVal,
      state: (entityId) => this._hass.states[entityId]?.state || null,
      attr: (entityId, attrName) => this._hass.states[entityId]?.attributes[attrName] || null,
    };
    
    if (functions[funcName]) {
      return functions[funcName](...args);
    }
    throw new Error(`Unknown function: ${funcName}`);
  }

  formatValue(value) {
    if (value === null || value === undefined) return '';
    if (typeof value === 'boolean') return value.toString();
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  }

  executeNow() {
    if (this._hass) {
      this._hass.callService('universal_controller', 'execute_now', {
        entity_id: this.config.entity
      });
    }
  }

  toggleEditor() {
    this.config.show_editor = !this.config.show_editor;
    this.render();
  }

  previewChanges() {
    this.config.show_preview = !this.config.show_preview;
    this.render();
  }

  saveChanges() {
    const interval = this.shadowRoot.getElementById('interval')?.value;
    const htmlTemplate = this.shadowRoot.getElementById('html_template')?.value;
    const cssStyles = this.shadowRoot.getElementById('css_styles')?.value;
    const typescriptCode = this.shadowRoot.getElementById('typescript_code')?.value;

    if (this._hass) {
      const serviceData = {
        entity_id: this.config.entity
      };

      if (interval) serviceData.interval = parseInt(interval);
      if (htmlTemplate !== undefined) serviceData.html_template = htmlTemplate;
      if (cssStyles !== undefined) serviceData.css_styles = cssStyles;
      if (typescriptCode !== undefined) serviceData.typescript_code = typescriptCode;

      this._hass.callService('universal_controller', 'update_entity', serviceData);
    }

    this.config.show_editor = false;
    this.config.show_preview = false;
    this.render();
  }

  getCardSize() {
    return this.config.show_editor ? 8 : 3;
  }

  static getConfigElement() {
    return document.createElement('universal-controller-card-editor');
  }

  static getStubConfig() {
    return { entity: '', title: 'Universal Controller' };
  }
}

// Card editor for Lovelace UI
class UniversalControllerCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
  }

  render() {
    if (!this._config) {
      return;
    }

    this.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 16px;">
        <div>
          <label style="display: block; margin-bottom: 4px; font-weight: 500;">Entity</label>
          <select id="entity" style="width: 100%; padding: 8px; border: 1px solid var(--divider-color); border-radius: 4px;">
            <option value="">Select entity...</option>
            ${this._hass ? Object.keys(this._hass.states)
              .filter(eid => eid.startsWith('sensor.') && this._hass.states[eid].attributes.html_template !== undefined)
              .map(eid => `<option value="${eid}" ${eid === this._config.entity ? 'selected' : ''}>${eid}</option>`)
              .join('') : ''}
          </select>
        </div>
        
        <div>
          <label style="display: block; margin-bottom: 4px; font-weight: 500;">Title (optional)</label>
          <input type="text" id="title" value="${this._config.title || ''}" 
                 style="width: 100%; padding: 8px; border: 1px solid var(--divider-color); border-radius: 4px;" 
                 placeholder="Card title">
        </div>
      </div>
    `;

    this.addEventListener('change', this._configChanged);
  }

  _configChanged = () => {
    const entity = this.querySelector('#entity').value;
    const title = this.querySelector('#title').value;

    this._config = {
      ...this._config,
      entity: entity,
      title: title || undefined
    };

    const event = new CustomEvent('config-changed', {
      detail: { config: this._config },
      bubbles: true,
      composed: true
    });
    this.dispatchEvent(event);
  }
}

// Register the elements
customElements.define('universal-controller-card', UniversalControllerCard);
customElements.define('universal-controller-card-editor', UniversalControllerCardEditor);

// Add to custom card registry
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'universal-controller-card',
  name: 'Universal Controller Card',
  description: 'Display and edit Universal Controller entities with custom HTML/CSS/TypeScript',
  preview: true,
  documentationURL: 'https://github.com/your-repo/universal-controller'
});

console.info(
  '%c UNIVERSAL-CONTROLLER-CARD %c v2.0.0 ',
  'color: white; background: #039be5; font-weight: 700;',
  'color: #039be5; background: white; font-weight: 700;'
);
