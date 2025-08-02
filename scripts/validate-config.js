#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const Ajv = require('ajv');

// Home Assistant Add-on config schema
const configSchema = {
  type: "object",
  required: ["name", "version", "slug", "description", "arch", "init"],
  properties: {
    name: { type: "string" },
    version: { type: "string" },
    slug: { type: "string" },
    description: { type: "string" },
    arch: {
      type: "array",
      items: { type: "string" }
    },
    init: { type: "boolean" },
    homeassistant_api: { type: "boolean" },
    hassio_api: { type: "boolean" },
    docker_api: { type: "boolean" },
    privileged: {
      type: "array",
      items: { type: "string" }
    },
    ports: {
      type: "object",
      patternProperties: {
        "^[0-9]+/tcp$": { type: "integer" }
      }
    },
    ports_description: {
      type: "object",
      patternProperties: {
        "^[0-9]+/tcp$": { type: "string" }
      }
    },
    startup: {
      type: "string",
      enum: ["initialize", "system", "services", "application", "once"]
    },
    boot: {
      type: "string", 
      enum: ["auto", "manual"]
    },
    webui: { type: "string" },
    ingress: { type: "boolean" },
    ingress_port: { type: "integer" },
    panel_icon: { type: "string" },
    panel_title: { type: "string" },
    panel_admin: { type: "boolean" },
    options: { type: "object" },
    schema: { type: "object" },
    image: { type: "string" }
  }
};

function validateConfig() {
  console.log('🔍 Validating Universal Controller add-on configuration...\n');

  try {
    // Check if config.yaml exists
    const configPath = path.join(__dirname, '..', 'universal_controller', 'config.yaml');
    if (!fs.existsSync(configPath)) {
      console.error('❌ config.yaml not found at:', configPath);
      process.exit(1);
    }

    // Read and parse config.yaml
    const configContent = fs.readFileSync(configPath, 'utf8');
    console.log('📄 config.yaml content:');
    console.log(configContent);
    console.log('');

    // Parse YAML manually (simple parser for validation)
    const config = parseSimpleYaml(configContent);
    
    // Validate against schema
    const ajv = new Ajv();
    const validate = ajv.compile(configSchema);
    const valid = validate(config);

    if (!valid) {
      console.error('❌ config.yaml validation failed:');
      validate.errors.forEach(error => {
        console.error(`  - ${error.instancePath || 'root'}: ${error.message}`);
      });
      process.exit(1);
    }

    console.log('✅ config.yaml is valid!');
    console.log('📊 Configuration summary:');
    console.log(`  - Name: ${config.name}`);
    console.log(`  - Version: ${config.version}`);
    console.log(`  - Slug: ${config.slug}`);
    console.log(`  - Architectures: ${config.arch.join(', ')}`);
    console.log(`  - Web UI Port: ${config.ports ? Object.values(config.ports)[0] : 'None'}`);
    console.log(`  - Home Assistant API: ${config.homeassistant_api ? 'Yes' : 'No'}`);
    console.log(`  - Supervisor API: ${config.hassio_api ? 'Yes' : 'No'}`);

    // Check Dockerfile
    const dockerfilePath = path.join(__dirname, '..', 'universal_controller', 'Dockerfile');
    if (fs.existsSync(dockerfilePath)) {
      console.log('✅ Dockerfile found');
    } else {
      console.log('⚠️  Dockerfile not found');
    }

    // Check run script
    const runScriptPath = path.join(__dirname, '..', 'universal_controller', 'rootfs', 'etc', 'services.d', 'universal-controller', 'run');
    if (fs.existsSync(runScriptPath)) {
      console.log('✅ Run script found');
    } else {
      console.log('⚠️  Run script not found');
    }

    // Check main application
    const appPath = path.join(__dirname, '..', 'universal_controller', 'rootfs', 'app', 'server.js');
    if (fs.existsSync(appPath)) {
      console.log('✅ Main application found');
    } else {
      console.log('⚠️  Main application not found');
    }

    console.log('\n🎉 Universal Controller add-on validation completed successfully!');

  } catch (error) {
    console.error('❌ Validation failed:', error.message);
    process.exit(1);
  }
}

// Simple YAML parser for basic validation
function parseSimpleYaml(content) {
  const lines = content.split('\n');
  const result = {};
  let currentKey = null;
  let currentArray = null;
  let currentObject = null;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;

    if (trimmed.includes(':')) {
      const [key, ...valueParts] = trimmed.split(':');
      const value = valueParts.join(':').trim();
      
      if (value === '') {
        // Start of nested object or array
        currentKey = key.trim();
        currentArray = null;
        currentObject = null;
      } else if (value === 'true' || value === 'false') {
        result[key.trim()] = value === 'true';
      } else if (!isNaN(value) && value !== '') {
        result[key.trim()] = parseInt(value);
      } else if (value.startsWith('"') && value.endsWith('"')) {
        result[key.trim()] = value.slice(1, -1);
      } else {
        result[key.trim()] = value;
      }
    } else if (trimmed.startsWith('-')) {
      // Array item
      if (!currentArray) {
        currentArray = [];
        if (currentKey) result[currentKey] = currentArray;
      }
      const value = trimmed.substring(1).trim();
      currentArray.push(value);
    } else if (trimmed.includes('/')) {
      // Port mapping
      if (!currentObject) {
        currentObject = {};
        if (currentKey) result[currentKey] = currentObject;
      }
      const [port, value] = trimmed.split(':');
      currentObject[port.trim()] = parseInt(value.trim());
    }
  }

  return result;
}

if (require.main === module) {
  validateConfig();
}

module.exports = { validateConfig };
