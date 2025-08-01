class UniversalControllerCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this._config = {};
        this._lastRefresh = 0;
        this._refreshInterval = 5000; // 5 seconds default
    }

    setConfig(config) {
        if (!config) {
            throw new Error('Invalid configuration');
        }

        this._config = config;
        this.render();
    }

    set hass(hass) {
        this._hass = hass;
        
        // Auto-refresh logic
        const now = Date.now();
        if (now - this._lastRefresh > this._refreshInterval) {
            this._lastRefresh = now;
            this.render();
        }
    }

    get _entity() {
        if (!this._config.entity) return null;
        return this._hass.states[this._config.entity];
    }

    render() {
        if (!this._hass || !this._config) return;

        const entity = this._entity;
        if (!entity) {
            this.shadowRoot.innerHTML = `
                <ha-card>
                    <div class="card-content">
                        <p>Entity "${this._config.entity}" not found</p>
                    </div>
                </ha-card>
            `;
            return;
        }

        const attributes = entity.attributes || {};
        const htmlTemplate = attributes.html_template || '';
        const cssStyles = attributes.css_styles || '';
        const lastExecution = attributes.last_execution || 'Never';
        const executionTime = attributes.execution_time || 'N/A';
        const lastError = attributes.last_error || null;

        // Create content with enhanced debugging
        const content = `
            <ha-card>
                <div class="card-header">
                    <div class="name">${this._config.title || entity.attributes.friendly_name || this._config.entity}</div>
                    <div class="controls">
                        <mwc-button dense outlined>
                            <ha-icon icon="mdi:pencil"></ha-icon>
                            Edit
                        </mwc-button>
                        <mwc-button dense outlined>
                            <ha-icon icon="mdi:play"></ha-icon>
                            Run
                        </mwc-button>
                        <mwc-button dense outlined>
                            <ha-icon icon="mdi:refresh"></ha-icon>
                            Refresh
                        </mwc-button>
                    </div>
                </div>
                
                <div class="card-content">
                    ${lastError ? `
                        <div class="error-banner">
                            <ha-icon icon="mdi:alert-circle"></ha-icon>
                            <span>${lastError}</span>
                        </div>
                    ` : ''}
                    
                    <div class="status-info">
                        <div class="status-item">
                            <span class="label">State:</span>
                            <span class="value">${entity.state}</span>
                        </div>
                        <div class="status-item">
                            <span class="label">Last Execution:</span>
                            <span class="value">${lastExecution}</span>
                        </div>
                        <div class="status-item">
                            <span class="label">Execution Time:</span>
                            <span class="value">${executionTime}</span>
                        </div>
                        <div class="status-item">
                            <span class="label">Interval:</span>
                            <span class="value">${attributes.interval || 'N/A'}s</span>
                        </div>
                    </div>
                    
                    <div class="rendered-content">
                        ${htmlTemplate}
                    </div>
                </div>
                
                <style>
                    :host {
                        display: block;
                    }
                    
                    .card-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 16px;
                        border-bottom: 1px solid var(--divider-color);
                    }
                    
                    .name {
                        font-weight: 500;
                        font-size: 16px;
                        color: var(--primary-text-color);
                    }
                    
                    .controls {
                        display: flex;
                        gap: 8px;
                    }
                    
                    .controls mwc-button {
                        --mdc-theme-primary: var(--primary-color);
                        --mdc-button-outline-color: var(--divider-color);
                    }
                    
                    .card-content {
                        padding: 16px;
                    }
                    
                    .error-banner {
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        padding: 12px;
                        background: var(--error-color);
                        color: white;
                        border-radius: 4px;
                        margin-bottom: 16px;
                    }
                    
                    .status-info {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 8px;
                        margin-bottom: 16px;
                        padding: 12px;
                        background: var(--secondary-background-color);
                        border-radius: 4px;
                    }
                    
                    .status-item {
                        display: flex;
                        justify-content: space-between;
                    }
                    
                    .status-item .label {
                        font-weight: 500;
                        color: var(--secondary-text-color);
                    }
                    
                    .status-item .value {
                        color: var(--primary-text-color);
                        font-family: monospace;
                    }
                    
                    .rendered-content {
                        border: 1px solid var(--divider-color);
                        border-radius: 4px;
                        padding: 16px;
                        min-height: 100px;
                        background: var(--card-background-color);
                    }
                    
                    /* Apply custom CSS styles */
                    ${cssStyles}
                </style>
            </ha-card>
        `;

        this.shadowRoot.innerHTML = content;
        this._attachEventListeners();
    }

    _attachEventListeners() {
        // Get all buttons with more specific selectors
        const buttons = this.shadowRoot.querySelectorAll('mwc-button');
        
        buttons.forEach(button => {
            const text = button.textContent || button.innerText || '';
            if (text.includes('Edit')) {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this._editEntity();
                });
            } else if (text.includes('Run')) {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this._executeNow();
                });
            } else if (text.includes('Refresh')) {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this._refreshCard();
                });
            }
        });
    }

    async _editEntity() {
        if (!this._entity) return;

        try {
            // Create a simple text editor dialog instead of Monaco
            const dialog = document.createElement('div');
            dialog.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
            `;
            
            const modal = document.createElement('div');
            modal.style.cssText = `
                background: var(--card-background-color, white);
                border-radius: 8px;
                padding: 24px;
                width: 90%;
                max-width: 800px;
                max-height: 80%;
                overflow-y: auto;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            `;
            
            const attributes = this._entity.attributes || {};
            
            modal.innerHTML = `
                <h2 style="margin-top: 0;">Edit ${this._entity.attributes.friendly_name || this._config.entity}</h2>
                
                <div style="margin-bottom: 16px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: bold;">TypeScript Code:</label>
                    <textarea id="codeEditor" style="width: 100%; height: 200px; font-family: monospace; padding: 8px; border: 1px solid var(--divider-color); border-radius: 4px;">${attributes.typescript_code || ''}</textarea>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: bold;">HTML Template:</label>
                    <textarea id="htmlEditor" style="width: 100%; height: 150px; font-family: monospace; padding: 8px; border: 1px solid var(--divider-color); border-radius: 4px;">${attributes.html_template || ''}</textarea>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: bold;">CSS Styles:</label>
                    <textarea id="cssEditor" style="width: 100%; height: 100px; font-family: monospace; padding: 8px; border: 1px solid var(--divider-color); border-radius: 4px;">${attributes.css_styles || ''}</textarea>
                </div>
                
                <div style="margin-bottom: 24px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: bold;">Execution Interval (seconds):</label>
                    <input type="number" id="intervalEditor" value="${attributes.interval || 60}" min="1" style="width: 100px; padding: 8px; border: 1px solid var(--divider-color); border-radius: 4px;">
                </div>
                
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button id="cancelBtn" style="padding: 8px 16px; border: 1px solid var(--divider-color); background: var(--card-background-color); border-radius: 4px; cursor: pointer;">Cancel</button>
                    <button id="saveBtn" style="padding: 8px 16px; border: none; background: var(--primary-color); color: white; border-radius: 4px; cursor: pointer;">Save</button>
                </div>
            `;
            
            dialog.appendChild(modal);
            document.body.appendChild(dialog);
            
            // Handle save
            modal.querySelector('#saveBtn').addEventListener('click', async () => {
                const code = modal.querySelector('#codeEditor').value;
                const html = modal.querySelector('#htmlEditor').value;
                const css = modal.querySelector('#cssEditor').value;
                const interval = parseInt(modal.querySelector('#intervalEditor').value) || 60;
                
                try {
                    await this._hass.callService('universal_controller', 'update_entity', {
                        entity_id: this._config.entity,
                        typescript_code: code,
                        html_template: html,
                        css_styles: css,
                        interval: interval
                    });
                    
                    document.body.removeChild(dialog);
                    this._showToast('Entity updated successfully');
                    setTimeout(() => this._refreshCard(), 1000);
                    
                } catch (error) {
                    console.error('Failed to update entity:', error);
                    this._showToast('Update failed: ' + error.message, 'error');
                }
            });
            
            // Handle cancel
            modal.querySelector('#cancelBtn').addEventListener('click', () => {
                document.body.removeChild(dialog);
            });
            
            // Handle backdrop click
            dialog.addEventListener('click', (e) => {
                if (e.target === dialog) {
                    document.body.removeChild(dialog);
                }
            });
            
        } catch (error) {
            console.error('Failed to open editor:', error);
            this._showToast('Failed to open editor: ' + error.message, 'error');
        }
    }

    async _executeNow() {
        if (!this._entity) return;

        try {
            await this._hass.callService('universal_controller', 'execute_entity', {
                entity_id: this._config.entity
            });
            
            // Show success feedback
            this._showToast('Execution triggered successfully');
            
            // Refresh after a short delay
            setTimeout(() => this._refreshCard(), 1000);
            
        } catch (error) {
            console.error('Failed to execute entity:', error);
            this._showToast('Execution failed: ' + error.message, 'error');
        }
    }

    _refreshCard() {
        this._lastRefresh = 0; // Force refresh
        this.render();
        this._showToast('Card refreshed');
    }

    _showToast(message, type = 'info') {
        // Create simple toast notification
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? 'var(--error-color)' : 'var(--primary-color)'};
            color: white;
            padding: 12px 16px;
            border-radius: 4px;
            z-index: 10000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 3000);
    }

    getCardSize() {
        return 4; // Approximate height in grid rows
    }

    static getConfigElement() {
        return document.createElement('universal-controller-card-editor');
    }

    static getStubConfig() {
        return {
            type: 'custom:universal-controller-card',
            entity: 'sensor.universal_controller_example'
        };
    }
}

// Register the card
customElements.define('universal-controller-card', UniversalControllerCard);

// Add to Lovelace card picker
window.customCards = window.customCards || [];
window.customCards.push({
    type: 'universal-controller-card',
    name: 'Universal Controller Card',
    description: 'Display and control Universal Controller entities with TypeScript execution',
    preview: true,
    documentationURL: 'https://github.com/yourusername/universal-controller'
});

console.info('Universal Controller Card loaded');
