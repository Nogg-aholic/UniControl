/**
 * Monaco Editor-based Universal Controller Card Editor
 * Provides TypeScript intellisense and HACS API support
 */

class UniversalControllerMonacoEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.monaco = null;
    this.editor = null;
    this.currentEntity = null;
  }

  connectedCallback() {
    this.loadMonaco();
  }

  disconnectedCallback() {
    if (this.editor) {
      this.editor.dispose();
    }
  }

  async loadMonaco() {
    // Load Monaco Editor from CDN
    if (!window.monaco) {
      await this.loadScript('https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs/loader.js');
      
      window.require.config({
        paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs' }
      });

      await new Promise((resolve) => {
        window.require(['vs/editor/editor.main'], () => {
          this.monaco = window.monaco;
          this.setupTypeScript();
          resolve();
        });
      });
    } else {
      this.monaco = window.monaco;
    }
    
    this.render();
  }

  async loadScript(src) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = src;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  setupTypeScript() {
    if (!this.monaco) return;

    // Configure TypeScript compiler options
    this.monaco.languages.typescript.typescriptDefaults.setCompilerOptions({
      target: this.monaco.languages.typescript.ScriptTarget.ES2020,
      allowNonTsExtensions: true,
      moduleResolution: this.monaco.languages.typescript.ModuleResolutionKind.NodeJs,
      module: this.monaco.languages.typescript.ModuleKind.CommonJS,
      noEmit: true,
      esModuleInterop: true,
      jsx: this.monaco.languages.typescript.JsxEmit.React,
      reactNamespace: 'React',
      allowJs: true,
      typeRoots: ['node_modules/@types'],
    });

    // Add Home Assistant type definitions
    fetch('/universal_controller_frontend/types/homeassistant.d.ts')
      .then(response => response.text())
      .then(content => {
        this.monaco.languages.typescript.typescriptDefaults.addExtraLib(
          content,
          'ts:homeassistant.d.ts'
        );
      })
      .catch(err => console.warn('Could not load HA type definitions:', err));

    // Add common examples and snippets
    this.monaco.languages.registerCompletionItemProvider('typescript', {
      provideCompletionItems: (model, position) => {
        return {
          suggestions: this.getCustomSuggestions()
        };
      }
    });
  }

  getCustomSuggestions() {
    const suggestions = [
      {
        label: 'getAllLights',
        kind: this.monaco.languages.CompletionItemKind.Snippet,
        insertText: [
          'const lights = utils.filterEntities("light").map(id => ({',
          '  id,',
          '  state: utils.getEntityState(id),',
          '  brightness: utils.getEntityAttribute(id, "brightness")',
          '}));'
        ].join('\n'),
        insertTextRules: this.monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: 'Get all light entities with their states and brightness'
      },
      {
        label: 'getTemperatureSensors',
        kind: this.monaco.languages.CompletionItemKind.Snippet,
        insertText: [
          'const tempSensors = utils.filterEntities("sensor")',
          '  .filter(id => utils.getEntityAttribute(id, "unit_of_measurement") === "°C")',
          '  .map(id => ({',
          '    id,',
          '    temperature: utils.parseNumber(utils.getEntityState(id)),',
          '    name: utils.getEntityAttribute(id, "friendly_name")',
          '  }));'
        ].join('\n'),
        insertTextRules: this.monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: 'Get all temperature sensors in Celsius'
      },
      {
        label: 'notifyPhone',
        kind: this.monaco.languages.CompletionItemKind.Snippet,
        insertText: [
          'await services.notify("${1:message}", "${2:title}", {',
          '  data: {',
          '    tag: "${3:notification_id}",',
          '    priority: "high",',
          '    notification_icon: "mdi:${4:icon-name}"',
          '  }',
          '});'
        ].join('\n'),
        insertTextRules: this.monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: 'Send a notification to mobile device'
      },
      {
        label: 'createChartData',
        kind: this.monaco.languages.CompletionItemKind.Snippet,
        insertText: [
          'const chartData = {',
          '  type: "line",',
          '  data: {',
          '    labels: [${1:"Label1", "Label2", "Label3"}],',
          '    datasets: [{',
          '      label: "${2:Dataset Name}",',
          '      data: [${3:10, 20, 30}],',
          '      borderColor: "rgb(75, 192, 192)",',
          '      backgroundColor: "rgba(75, 192, 192, 0.2)"',
          '    }]',
          '  },',
          '  options: {',
          '    responsive: true,',
          '    scales: {',
          '      y: { beginAtZero: true }',
          '    }',
          '  }',
          '};'
        ].join('\n'),
        insertTextRules: this.monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: 'Create Chart.js compatible data structure'
      }
    ];

    return suggestions;
  }

  render() {
    if (!this.monaco) {
      this.shadowRoot.innerHTML = `
        <div style="padding: 20px; text-align: center;">
          <div>Loading Monaco Editor...</div>
          <div style="margin-top: 10px;">
            <div class="loading-spinner"></div>
          </div>
        </div>
        <style>
          .loading-spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        </style>
      `;
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          width: 100%;
          height: 100%;
        }
        .editor-container {
          display: flex;
          flex-direction: column;
          height: 100%;
          background: var(--card-background-color);
          border-radius: var(--ha-card-border-radius);
          overflow: hidden;
          box-shadow: var(--ha-card-box-shadow);
        }
        .editor-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          background: var(--primary-color);
          color: var(--text-primary-color);
          border-bottom: 1px solid var(--divider-color);
        }
        .editor-title {
          font-size: 1.1em;
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
          transition: background 0.2s;
        }
        .btn:hover {
          background: rgba(255,255,255,0.3);
        }
        .btn.primary {
          background: var(--accent-color);
        }
        .btn.primary:hover {
          background: var(--accent-color);
          opacity: 0.8;
        }
        .editor-tabs {
          display: flex;
          background: var(--secondary-background-color);
          border-bottom: 1px solid var(--divider-color);
        }
        .tab {
          padding: 12px 16px;
          cursor: pointer;
          border-bottom: 2px solid transparent;
          transition: all 0.2s;
        }
        .tab.active {
          background: var(--card-background-color);
          border-bottom-color: var(--primary-color);
        }
        .tab:hover {
          background: var(--card-background-color);
        }
        .editor-content {
          flex: 1;
          display: flex;
          flex-direction: column;
        }
        .monaco-editor-container {
          flex: 1;
          min-height: 400px;
        }
        .status-bar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 16px;
          background: var(--secondary-background-color);
          border-top: 1px solid var(--divider-color);
          font-size: 0.8em;
          color: var(--secondary-text-color);
        }
        .error-indicator {
          color: var(--error-color);
        }
        .success-indicator {
          color: var(--success-color);
        }
      </style>
      
      <div class="editor-container">
        <div class="editor-header">
          <div class="editor-title">Universal Controller Editor</div>
          <div class="editor-controls">
            <button class="btn" onclick="this.getRootNode().host.executeCode()">Test Run</button>
            <button class="btn primary" onclick="this.getRootNode().host.saveChanges()">Save & Apply</button>
            <button class="btn" onclick="this.getRootNode().host.closeEditor()">Close</button>
          </div>
        </div>
        
        <div class="editor-tabs">
          <div class="tab active" data-tab="typescript">TypeScript Code</div>
          <div class="tab" data-tab="html">HTML Template</div>
          <div class="tab" data-tab="css">CSS Styles</div>
        </div>
        
        <div class="editor-content">
          <div class="monaco-editor-container" id="monaco-container"></div>
        </div>
        
        <div class="status-bar">
          <div id="status-text">Ready</div>
          <div id="cursor-position">Ln 1, Col 1</div>
        </div>
      </div>
    `;

    this.initializeEditor();
    this.setupTabSwitching();
  }

  initializeEditor() {
    const container = this.shadowRoot.getElementById('monaco-container');
    if (!container || !this.monaco) return;

    this.editor = this.monaco.editor.create(container, {
      value: this.getInitialCode(),
      language: 'typescript',
      theme: 'vs-dark',
      automaticLayout: true,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      fontSize: 14,
      lineNumbers: 'on',
      renderWhitespace: 'boundary',
      quickSuggestions: true,
      suggestOnTriggerCharacters: true,
      wordBasedSuggestions: true,
      parameterHints: { enabled: true },
      hover: { enabled: true },
    });

    // Update cursor position
    this.editor.onDidChangeCursorPosition((e) => {
      const position = this.shadowRoot.getElementById('cursor-position');
      if (position) {
        position.textContent = `Ln ${e.position.lineNumber}, Col ${e.position.column}`;
      }
    });

    // Handle content changes
    this.editor.onDidChangeModelContent(() => {
      this.updateStatus('Modified');
    });
  }

  setupTabSwitching() {
    const tabs = this.shadowRoot.querySelectorAll('.tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        // Remove active class from all tabs
        tabs.forEach(t => t.classList.remove('active'));
        // Add active class to clicked tab
        tab.classList.add('active');
        
        const tabType = tab.dataset.tab;
        this.switchEditorLanguage(tabType);
      });
    });
  }

  switchEditorLanguage(tabType) {
    if (!this.editor) return;

    const languageMap = {
      'typescript': 'typescript',
      'html': 'html',
      'css': 'css'
    };

    const language = languageMap[tabType] || 'typescript';
    this.monaco.editor.setModelLanguage(this.editor.getModel(), language);

    // Load appropriate content for the tab
    this.loadTabContent(tabType);
  }

  loadTabContent(tabType) {
    if (!this.currentEntity) return;

    const attributes = this.currentEntity.attributes;
    let content = '';

    switch (tabType) {
      case 'typescript':
        content = attributes.typescript_code || this.getDefaultTypeScriptCode();
        break;
      case 'html':
        content = attributes.html_template || this.getDefaultHTMLTemplate();
        break;
      case 'css':
        content = attributes.css_styles || this.getDefaultCSSStyles();
        break;
    }

    this.editor.setValue(content);
  }

  getInitialCode() {
    return this.getDefaultTypeScriptCode();
  }

  getDefaultTypeScriptCode() {
    return `// Universal Controller TypeScript Code
// You have access to: hass, states, services, utils, console, HACS

// Example: Get all lights and their states
const lights = utils.filterEntities("light").map(id => ({
  id,
  state: utils.getEntityState(id),
  brightness: utils.getEntityAttribute(id, "brightness") || 0
}));

// Example: Calculate average temperature
const tempSensors = utils.filterEntities("sensor")
  .filter(id => utils.getEntityAttribute(id, "unit_of_measurement") === "°C");

const avgTemp = tempSensors.length > 0 
  ? utils.avg(tempSensors.map(id => utils.parseNumber(utils.getEntityState(id))))
  : 0;

// Return data for the template
return {
  timestamp: utils.now(),
  lightsOn: lights.filter(l => utils.isOn(l.id)).length,
  totalLights: lights.length,
  averageTemperature: Math.round(avgTemp * 10) / 10,
  message: \`\${lights.filter(l => utils.isOn(l.id)).length} of \${lights.length} lights are on\`
};`;
  }

  getDefaultHTMLTemplate() {
    return `<!-- Universal Controller HTML Template -->
<div class="universal-widget">
  <div class="header">
    <h3>{{friendly_name}}</h3>
    <div class="timestamp">{{timestamp}}</div>
  </div>
  
  <div class="content">
    <div class="metric">
      <span class="label">Lights On:</span>
      <span class="value">{{lightsOn}} / {{totalLights}}</span>
    </div>
    
    <div class="metric">
      <span class="label">Average Temperature:</span>
      <span class="value">{{averageTemperature}}°C</span>
    </div>
    
    <div class="status-message">
      {{message}}
    </div>
  </div>
</div>`;
  }

  getDefaultCSSStyles() {
    return `/* Universal Controller CSS Styles */
.universal-widget {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header h3 {
  margin: 0;
  font-size: 1.2em;
  font-weight: 600;
}

.timestamp {
  font-size: 0.8em;
  opacity: 0.8;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255,255,255,0.1);
  border-radius: 6px;
}

.label {
  font-weight: 500;
}

.value {
  font-weight: 600;
  font-size: 1.1em;
}

.status-message {
  text-align: center;
  padding: 12px;
  background: rgba(255,255,255,0.2);
  border-radius: 6px;
  font-style: italic;
}`;
  }

  async executeCode() {
    if (!this._hass || !this.currentEntity) return;

    this.updateStatus('Executing...', 'info');

    try {
      // Call the execute_now service
      await this._hass.callService('universal_controller', 'execute_now', {
        entity_id: this.currentEntity.entity_id
      });

      this.updateStatus('Execution completed', 'success');
    } catch (error) {
      this.updateStatus(`Execution failed: ${error.message}`, 'error');
    }
  }

  async saveChanges() {
    if (!this._hass || !this.currentEntity) return;

    this.updateStatus('Saving...', 'info');

    try {
      const activeTab = this.shadowRoot.querySelector('.tab.active').dataset.tab;
      const content = this.editor.getValue();

      const updateData = {
        entity_id: this.currentEntity.entity_id
      };

      // Set the appropriate field based on active tab
      switch (activeTab) {
        case 'typescript':
          updateData.typescript_code = content;
          break;
        case 'html':
          updateData.html_template = content;
          break;
        case 'css':
          updateData.css_styles = content;
          break;
      }

      await this._hass.callService('universal_controller', 'update_entity', updateData);

      this.updateStatus('Changes saved', 'success');
    } catch (error) {
      this.updateStatus(`Save failed: ${error.message}`, 'error');
    }
  }

  closeEditor() {
    this.dispatchEvent(new CustomEvent('close-editor', {
      bubbles: true,
      composed: true
    }));
  }

  updateStatus(message, type = 'info') {
    const statusText = this.shadowRoot.getElementById('status-text');
    if (statusText) {
      statusText.textContent = message;
      statusText.className = type === 'error' ? 'error-indicator' : 
                           type === 'success' ? 'success-indicator' : '';
    }
  }

  setEntity(entity) {
    this.currentEntity = entity;
    if (this.editor) {
      this.loadTabContent('typescript');
    }
  }

  set hass(hass) {
    this._hass = hass;
  }
}

customElements.define('universal-controller-monaco-editor', UniversalControllerMonacoEditor);

console.info('Universal Controller Monaco Editor registered successfully');
