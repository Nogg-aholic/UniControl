#!/usr/bin/env node

const http = require('http');
const path = require('path');
const fs = require('fs');

// Simple test server to verify the add-on application
const PORT = 8099;

console.log('🧪 Testing Universal Controller Add-on Application\n');

// Load the main server module
const serverPath = path.join(__dirname, '..', 'universal_controller', 'rootfs', 'app', 'server.js');

if (!fs.existsSync(serverPath)) {
  console.error('❌ Server application not found at:', serverPath);
  process.exit(1);
}

// Mock Home Assistant API for testing
const mockHassAPI = {
  states: {
    'sensor.test': {
      entity_id: 'sensor.test',
      state: 'testing',
      attributes: { unit_of_measurement: 'test' },
      last_changed: new Date().toISOString(),
      last_updated: new Date().toISOString()
    }
  },
  async callService(domain, service, data) {
    console.log(`Mock service call: ${domain}.${service}`, data);
    return { success: true };
  },
  getState(entityId) {
    return this.states[entityId] || null;
  },
  async setState(entityId, state, attributes) {
    this.states[entityId] = {
      entity_id: entityId,
      state,
      attributes: attributes || {},
      last_changed: new Date().toISOString(),
      last_updated: new Date().toISOString()
    };
    return this.states[entityId];
  }
};

// Mock bashio for testing
global.bashio = {
  config: {
    get: (key) => {
      const mockConfig = {
        'web_port': 8099,
        'log_level': 'info'
      };
      return mockConfig[key];
    }
  },
  log: {
    info: console.log,
    warn: console.warn,
    error: console.error,
    debug: console.debug
  }
};

// Set environment variables for testing
process.env.SUPERVISOR_TOKEN = 'test-token';
process.env.NODE_ENV = 'test';

async function runTests() {
  try {
    console.log('📋 Running application tests...\n');

    // Test 1: Check if server starts
    console.log('1️⃣  Testing server startup...');
    
    // Import and start the server
    require(serverPath);
    
    // Wait a moment for server to start
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Test 2: Check if web interface is accessible
    console.log('2️⃣  Testing web interface...');
    
    await testEndpoint('GET', `http://localhost:${PORT}/`, 'Web interface');
    await testEndpoint('GET', `http://localhost:${PORT}/api/entities`, 'API entities endpoint');

    // Test 3: Check entity creation
    console.log('3️⃣  Testing entity creation...');
    
    const testEntity = {
      id: 'test_entity',
      name: 'Test Entity',
      javascript_code: 'return { state: "testing", attributes: { test: true } };',
      html_template: '<div>Test: {{state}}</div>',
      css_styles: 'div { color: red; }',
      interval: 30
    };

    await testEndpoint('POST', `http://localhost:${PORT}/api/entities`, 'Create entity', testEntity);

    // Test 4: Check entity execution
    console.log('4️⃣  Testing entity execution...');
    
    await testEndpoint('POST', `http://localhost:${PORT}/api/entities/test_entity/execute`, 'Execute entity');

    console.log('\n🎉 All tests passed! Universal Controller add-on is working correctly.');
    console.log(`🌐 Web interface available at: http://localhost:${PORT}`);
    console.log('💡 To test in Home Assistant, install as add-on and access via sidebar.');

  } catch (error) {
    console.error('\n❌ Tests failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

async function testEndpoint(method, url, description, data = null) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + urlObj.search,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'UniversalController-Test/1.0'
      }
    };

    const req = http.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });

      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          console.log(`   ✅ ${description}: ${res.statusCode} ${res.statusMessage}`);
          resolve(responseData);
        } else {
          console.log(`   ❌ ${description}: ${res.statusCode} ${res.statusMessage}`);
          reject(new Error(`HTTP ${res.statusCode}: ${responseData}`));
        }
      });
    });

    req.on('error', (error) => {
      console.log(`   ❌ ${description}: Connection failed`);
      reject(error);
    });

    if (data) {
      req.write(JSON.stringify(data));
    }

    req.end();
  });
}

// Handle cleanup
process.on('SIGINT', () => {
  console.log('\n🛑 Test interrupted by user');
  process.exit(0);
});

process.on('uncaughtException', (error) => {
  console.error('\n💥 Uncaught exception:', error.message);
  process.exit(1);
});

// Start tests
runTests();
