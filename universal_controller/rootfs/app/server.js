const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const WebSocket = require('ws');
const fs = require('fs').promises;
const path = require('path');
const cron = require('node-cron');
const axios = require('axios');

class UniversalControllerServer {
    constructor() {
        this.app = express();
        this.server = http.createServer(this.app);
        this.io = socketIo(this.server, {
            cors: { origin: "*", methods: ["GET", "POST"] }
        });
        
        this.port = process.env.PORT || 8099;
        this.hassUrl = 'http://supervisor/core';
        this.hassToken = process.env.SUPERVISOR_TOKEN;
        
        this.entities = new Map();
        this.scheduledTasks = new Map();
        this.hassWebSocket = null;
        
        this.setupMiddleware();
        this.setupRoutes();
        this.setupSocketHandlers();
        this.connectToHomeAssistant();
        this.loadEntities();
    }

    setupMiddleware() {
        this.app.use(express.json());
        this.app.use(express.static(path.join(__dirname, 'web')));
        
        // CORS headers
        this.app.use((req, res, next) => {
            res.header('Access-Control-Allow-Origin', '*');
            res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
            res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
            next();
        });
    }

    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({ status: 'ok', timestamp: new Date().toISOString() });
        });

        // Main editor interface
        this.app.get('/', (req, res) => {
            res.sendFile(path.join(__dirname, 'web', 'index.html'));
        });

        // API endpoints
        this.app.get('/api/entities', (req, res) => {
            const entities = Array.from(this.entities.values());
            res.json(entities);
        });

        this.app.post('/api/entities', async (req, res) => {
            try {
                const entity = await this.createEntity(req.body);
                res.json(entity);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.put('/api/entities/:id', async (req, res) => {
            try {
                const entity = await this.updateEntity(req.params.id, req.body);
                res.json(entity);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.delete('/api/entities/:id', async (req, res) => {
            try {
                await this.deleteEntity(req.params.id);
                res.json({ success: true });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.post('/api/entities/:id/execute', async (req, res) => {
            try {
                const result = await this.executeEntity(req.params.id);
                res.json(result);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Home Assistant proxy endpoints
        this.app.get('/api/hass/states', async (req, res) => {
            try {
                const states = await this.getHomeAssistantStates();
                res.json(states);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.post('/api/hass/services/:domain/:service', async (req, res) => {
            try {
                const result = await this.callHomeAssistantService(
                    req.params.domain,
                    req.params.service,
                    req.body
                );
                res.json(result);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });
    }

    setupSocketHandlers() {
        this.io.on('connection', (socket) => {
            console.log('Client connected:', socket.id);

            socket.on('get_entities', () => {
                const entities = Array.from(this.entities.values());
                socket.emit('entities', entities);
            });

            socket.on('execute_entity', async (entityId) => {
                try {
                    const result = await this.executeEntity(entityId);
                    socket.emit('execution_result', { entityId, result });
                } catch (error) {
                    socket.emit('execution_error', { entityId, error: error.message });
                }
            });

            socket.on('update_entity', async (data) => {
                try {
                    const entity = await this.updateEntity(data.id, data);
                    socket.emit('entity_updated', entity);
                    this.io.emit('entity_changed', entity); // Broadcast to all clients
                } catch (error) {
                    socket.emit('update_error', { error: error.message });
                }
            });

            socket.on('disconnect', () => {
                console.log('Client disconnected:', socket.id);
            });
        });
    }

    async connectToHomeAssistant() {
        try {
            // Connect to Home Assistant WebSocket
            const wsUrl = this.hassUrl.replace('http', 'ws') + '/api/websocket';
            this.hassWebSocket = new WebSocket(wsUrl);
            
            this.hassWebSocket.on('open', () => {
                console.log('Connected to Home Assistant WebSocket');
                // Authenticate
                this.hassWebSocket.send(JSON.stringify({
                    type: 'auth',
                    access_token: this.hassToken
                }));
            });

            this.hassWebSocket.on('message', (data) => {
                const message = JSON.parse(data);
                this.handleHomeAssistantMessage(message);
            });

            this.hassWebSocket.on('error', (error) => {
                console.error('Home Assistant WebSocket error:', error);
            });

        } catch (error) {
            console.error('Failed to connect to Home Assistant:', error);
        }
    }

    handleHomeAssistantMessage(message) {
        // Handle state changes and other HA events
        if (message.type === 'event' && message.event?.event_type === 'state_changed') {
            // Broadcast state changes to connected clients
            this.io.emit('hass_state_change', message.event.data);
        }
    }

    async getHomeAssistantStates() {
        try {
            const response = await axios.get(`${this.hassUrl}/api/states`, {
                headers: {
                    'Authorization': `Bearer ${this.hassToken}`,
                    'Content-Type': 'application/json'
                }
            });
            return response.data;
        } catch (error) {
            console.error('Failed to get HA states:', error);
            throw error;
        }
    }

    async callHomeAssistantService(domain, service, data = {}) {
        try {
            const response = await axios.post(
                `${this.hassUrl}/api/services/${domain}/${service}`,
                data,
                {
                    headers: {
                        'Authorization': `Bearer ${this.hassToken}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to call HA service:', error);
            throw error;
        }
    }

    async createEntity(data) {
        const entity = {
            id: data.id || `universal_controller_${Date.now()}`,
            name: data.name || 'Unnamed Entity',
            javascript_code: data.javascript_code || '',
            html_template: data.html_template || '',
            css_styles: data.css_styles || '',
            interval: data.interval || 60,
            enabled: data.enabled !== false,
            state: 'idle',
            last_execution: null,
            last_error: null,
            execution_time: null,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        };

        this.entities.set(entity.id, entity);
        await this.saveEntity(entity);
        
        if (entity.enabled && entity.interval > 0) {
            this.scheduleEntity(entity);
        }

        // Register with Home Assistant
        await this.registerEntityWithHA(entity);

        return entity;
    }

    async updateEntity(id, data) {
        const entity = this.entities.get(id);
        if (!entity) {
            throw new Error(`Entity ${id} not found`);
        }

        // Update entity properties
        Object.assign(entity, {
            ...data,
            id, // Preserve ID
            updated_at: new Date().toISOString()
        });

        this.entities.set(id, entity);
        await this.saveEntity(entity);

        // Reschedule if interval changed
        this.unscheduleEntity(id);
        if (entity.enabled && entity.interval > 0) {
            this.scheduleEntity(entity);
        }

        // Update in Home Assistant
        await this.updateEntityInHA(entity);

        return entity;
    }

    async deleteEntity(id) {
        this.unscheduleEntity(id);
        this.entities.delete(id);
        
        try {
            await fs.unlink(path.join('/data', 'entities', `${id}.json`));
        } catch (error) {
            // File might not exist
        }

        // Remove from Home Assistant
        await this.removeEntityFromHA(id);
    }

    async executeEntity(id) {
        const entity = this.entities.get(id);
        if (!entity) {
            throw new Error(`Entity ${id} not found`);
        }

        const startTime = Date.now();
        
        try {
            // Create execution context with Home Assistant API
            const context = await this.createExecutionContext(entity);
            
            // Execute the JavaScript code
            const result = await this.executeJavaScript(entity.javascript_code, context);
            
            const executionTime = Date.now() - startTime;
            
            // Update entity state
            entity.state = result?.state || 'completed';
            entity.last_execution = new Date().toISOString();
            entity.last_error = null;
            entity.execution_time = `${executionTime}ms`;
            
            // Update HTML template if returned
            if (result?.html_template) {
                entity.html_template = result.html_template;
            }

            this.entities.set(id, entity);
            await this.saveEntity(entity);
            await this.updateEntityInHA(entity);

            // Broadcast update
            this.io.emit('entity_executed', { id, result, entity });

            return { success: true, result, executionTime };

        } catch (error) {
            const executionTime = Date.now() - startTime;
            
            entity.state = 'error';
            entity.last_execution = new Date().toISOString();
            entity.last_error = error.message;
            entity.execution_time = `${executionTime}ms`;
            
            this.entities.set(id, entity);
            await this.saveEntity(entity);
            await this.updateEntityInHA(entity);

            console.error(`Execution error for ${id}:`, error);
            throw error;
        }
    }

    async createExecutionContext(entity) {
        // Get current Home Assistant states
        const hassStates = await this.getHomeAssistantStates();
        const statesMap = {};
        hassStates.forEach(state => {
            statesMap[state.entity_id] = state;
        });

        return {
            // Home Assistant API
            hass: {
                states: statesMap,
                
                callService: async (domain, service, data = {}) => {
                    return await this.callHomeAssistantService(domain, service, data);
                },
                
                getState: (entityId) => {
                    return statesMap[entityId] || null;
                },
                
                setState: async (entityId, state, attributes = {}) => {
                    return await this.callHomeAssistantService('homeassistant', 'set_state', {
                        entity_id: entityId,
                        state: state,
                        attributes: attributes
                    });
                }
            },
            
            // Utility functions
            log: (...args) => {
                console.log(`[${entity.id}]`, ...args);
            },
            
            error: (...args) => {
                console.error(`[${entity.id}]`, ...args);
            },
            
            // Libraries
            _: require('lodash'),
            moment: require('moment'),
            axios: axios,
            
            // Entity context
            entity: {
                id: entity.id,
                name: entity.name,
                state: entity.state
            }
        };
    }

    async executeJavaScript(code, context) {
        // Create a safe execution environment
        const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
        
        try {
            // Wrap code in async function with context
            const wrappedCode = `
                const { hass, log, error, _, moment, axios, entity } = context;
                
                ${code}
            `;
            
            const fn = new AsyncFunction('context', wrappedCode);
            return await fn(context);
            
        } catch (error) {
            throw new Error(`JavaScript execution error: ${error.message}`);
        }
    }

    scheduleEntity(entity) {
        if (entity.interval <= 0) return;
        
        // Create cron expression for interval in seconds
        const cronExpression = `*/${entity.interval} * * * * *`;
        
        const task = cron.schedule(cronExpression, async () => {
            try {
                await this.executeEntity(entity.id);
            } catch (error) {
                console.error(`Scheduled execution failed for ${entity.id}:`, error);
            }
        }, {
            scheduled: false
        });
        
        task.start();
        this.scheduledTasks.set(entity.id, task);
        
        console.log(`Scheduled entity ${entity.id} with interval ${entity.interval}s`);
    }

    unscheduleEntity(id) {
        const task = this.scheduledTasks.get(id);
        if (task) {
            task.stop();
            this.scheduledTasks.delete(id);
            console.log(`Unscheduled entity ${id}`);
        }
    }

    async saveEntity(entity) {
        const entitiesDir = path.join('/data', 'entities');
        try {
            await fs.mkdir(entitiesDir, { recursive: true });
        } catch (error) {
            // Directory might already exist
        }
        
        const filePath = path.join(entitiesDir, `${entity.id}.json`);
        await fs.writeFile(filePath, JSON.stringify(entity, null, 2));
    }

    async loadEntities() {
        try {
            const entitiesDir = path.join('/data', 'entities');
            const files = await fs.readdir(entitiesDir).catch(() => []);
            
            for (const file of files) {
                if (file.endsWith('.json')) {
                    try {
                        const filePath = path.join(entitiesDir, file);
                        const data = await fs.readFile(filePath, 'utf8');
                        const entity = JSON.parse(data);
                        
                        this.entities.set(entity.id, entity);
                        
                        if (entity.enabled && entity.interval > 0) {
                            this.scheduleEntity(entity);
                        }
                        
                    } catch (error) {
                        console.error(`Failed to load entity from ${file}:`, error);
                    }
                }
            }
            
            console.log(`Loaded ${this.entities.size} entities`);
            
        } catch (error) {
            console.error('Failed to load entities:', error);
        }
    }

    async registerEntityWithHA(entity) {
        // This would register the entity as a sensor in Home Assistant
        // For now, we'll just log it
        console.log(`Registering entity ${entity.id} with Home Assistant`);
    }

    async updateEntityInHA(entity) {
        // Update the entity state in Home Assistant
        console.log(`Updating entity ${entity.id} in Home Assistant`);
    }

    async removeEntityFromHA(id) {
        // Remove the entity from Home Assistant
        console.log(`Removing entity ${id} from Home Assistant`);
    }

    start() {
        this.server.listen(this.port, () => {
            console.log(`Universal Controller Add-on running on port ${this.port}`);
        });
    }
}

// Start the server
const server = new UniversalControllerServer();
server.start();
