# Universal Controller for Home Assistant

Execute real JavaScript/TypeScript code in Home Assistant with a powerful Monaco Editor interface.

## 🚀 Features

- **Real JavaScript Execution**: Run actual JavaScript/TypeScript code with Node.js in a dedicated add-on
- **Monaco Editor**: Full VS Code editor experience with IntelliSense and syntax highlighting
- **Home Assistant Integration**: Direct access to HA states, services, and entities
- **npm Package Support**: Use any npm package in your automations (lodash, moment, axios, etc.)
- **Real-time Updates**: WebSocket connection for instant feedback
- **Scheduled Execution**: Set custom intervals for your scripts
- **Visual Interface**: Beautiful web interface for managing your automations
- **Lovelace Card**: Display and control your entities directly in your dashboard

## 📦 Installation

### Method 1: Add-on (Recommended)

1. Add this repository to your Home Assistant Add-on store:
   ```
   https://github.com/Nogg-aholic/UniControl
   ```

2. Install the "Universal Controller" add-on
3. Start the add-on
4. Access the Monaco Editor interface at `http://homeassistant:8099`

### Method 2: HACS Integration (Legacy)

1. Install via HACS as a custom repository
2. Add the integration in Home Assistant
3. Use the basic text editor interface

## 🎯 Quick Start

### 1. Create Your First Automation

1. Open the Universal Controller interface (`http://homeassistant:8099`)
2. Click "New Entity"
3. Enter an ID (e.g., `lights_automation`) and name
4. Write your JavaScript code:

```javascript
// Turn on lights when sun sets
const sun = hass.getState('sun.sun');

if (sun.state === 'below_horizon') {
    await hass.callService('light', 'turn_on', {
        entity_id: 'group.living_room_lights',
        brightness: 180
    });
    
    log('🌅 Turned on living room lights at sunset');
}

return { state: 'completed' };
```

5. Set execution interval (e.g., 300 seconds for 5 minutes)
6. Save and watch it run!

### 2. Add to Dashboard

1. Add a new card to your Lovelace dashboard
2. Choose "Universal Controller Card"
3. Select your entity
4. Enjoy real-time status and one-click editing!

## 💡 JavaScript API

Your code has access to a powerful API:

### Home Assistant
```javascript
// Get all states
const states = hass.states;

// Get specific entity state
const temp = hass.getState('sensor.temperature');
console.log(`Temperature: ${temp.state}${temp.attributes.unit_of_measurement}`);

// Call any service
await hass.callService('light', 'turn_on', {
    entity_id: 'light.living_room',
    brightness: 255,
    color_name: 'blue'
});

// Set custom sensor states
await hass.setState('sensor.my_custom_sensor', '42', {
    unit_of_measurement: '°C',
    friendly_name: 'My Temperature Sensor'
});
```

### Utility Functions
```javascript
// Logging
log('Info message');
error('Error message');

// Libraries included
const _ = require('lodash');
const moment = require('moment');
const axios = require('axios');

// Current time formatting
const now = moment().format('YYYY-MM-DD HH:mm:ss');
log(`Current time: ${now}`);

// Array manipulation
const numbers = [1, 2, 3, 4, 5];
const sum = _.sum(numbers);
log(`Sum: ${sum}`);
```

### HTTP Requests
```javascript
// Fetch external data
const response = await axios.get('https://api.openweathermap.org/data/2.5/weather', {
    params: {
        q: 'Berlin',
        appid: 'YOUR_API_KEY',
        units: 'metric'
    }
});

const weather = response.data;
log(`Weather in Berlin: ${weather.main.temp}°C, ${weather.weather[0].description}`);
```

## 🔥 Example Automations

### Smart Temperature Control
```javascript
const temp = parseFloat(hass.getState('sensor.living_room_temperature').state);
const thermostat = hass.getState('climate.living_room');

if (temp < 18 && thermostat.state === 'off') {
    await hass.callService('climate', 'turn_on', {
        entity_id: 'climate.living_room'
    });
    
    await hass.callService('climate', 'set_temperature', {
        entity_id: 'climate.living_room',
        temperature: 21
    });
    
    log('🔥 Heating turned on - too cold!');
}

return { 
    state: `${temp}°C`,
    html_template: `
        <div class="temp-display">
            <span class="temp">${temp}°C</span>
            <span class="status">${thermostat.state}</span>
        </div>
    `
};
```

### Security System
```javascript
const motion = hass.getState('binary_sensor.motion_detector');
const alarm = hass.getState('alarm_control_panel.home');

if (motion.state === 'on' && alarm.state === 'armed_away') {
    // Send notification
    await hass.callService('notify', 'mobile_app_phone', {
        message: 'Motion detected while away!',
        title: '🚨 Security Alert',
        data: {
            priority: 'high',
            tag: 'security'
        }
    });
    
    // Turn on all lights
    await hass.callService('light', 'turn_on', {
        entity_id: 'group.all_lights',
        brightness: 255
    });
    
    log('🚨 Security breach detected!');
    
    return { 
        state: 'alert',
        html_template: '<div style="color: red;">🚨 MOTION DETECTED</div>'
    };
}

return { state: 'monitoring' };
```

### Smart Plant Watering
```javascript
const soilMoisture = parseFloat(hass.getState('sensor.plant_moisture').state);
const lastWatered = hass.getState('input_datetime.last_watered').state;
const daysSinceWatered = moment().diff(moment(lastWatered), 'days');

if (soilMoisture < 30 || daysSinceWatered > 7) {
    // Turn on water pump
    await hass.callService('switch', 'turn_on', {
        entity_id: 'switch.water_pump'
    });
    
    // Wait 30 seconds
    setTimeout(async () => {
        await hass.callService('switch', 'turn_off', {
            entity_id: 'switch.water_pump'
        });
    }, 30000);
    
    // Update last watered time
    await hass.callService('input_datetime', 'set_datetime', {
        entity_id: 'input_datetime.last_watered',
        datetime: moment().format('YYYY-MM-DD HH:mm:ss')
    });
    
    log('🌱 Plant watered automatically');
    
    return {
        state: 'watered',
        html_template: `
            <div class="plant-status">
                💧 Plant watered<br>
                Moisture: ${soilMoisture}%
            </div>
        `
    };
}

return {
    state: 'healthy',
    html_template: `
        <div class="plant-status">
            🌱 Plant is healthy<br>
            Moisture: ${soilMoisture}%<br>
            Last watered: ${daysSinceWatered} days ago
        </div>
    `
};
```

## 🎨 HTML Templates & Styling

Your automations can return custom HTML and CSS for beautiful dashboard displays:

```javascript
const temperature = parseFloat(hass.getState('sensor.temperature').state);
const humidity = parseFloat(hass.getState('sensor.humidity').state);

return {
    state: 'updated',
    html_template: `
        <div class="weather-card">
            <div class="main-temp">${temperature}°C</div>
            <div class="humidity">💧 ${humidity}%</div>
            <div class="comfort-level">${getComfortLevel(temperature, humidity)}</div>
        </div>
    `,
    css_styles: `
        .weather-card {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            color: white;
        }
        .main-temp {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .humidity {
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        .comfort-level {
            font-style: italic;
            opacity: 0.8;
        }
    `
};

function getComfortLevel(temp, humidity) {
    if (temp >= 20 && temp <= 25 && humidity >= 40 && humidity <= 60) {
        return '✨ Perfect comfort';
    } else if (temp < 18) {
        return '🥶 Too cold';
    } else if (temp > 26) {
        return '🥵 Too hot';
    } else {
        return '👍 Comfortable';
    }
}
```

## 🔧 Configuration

### Add-on Configuration
- **Port**: Web interface port (default: 8099)
- **SSL**: Enable HTTPS
- **Log Level**: Adjust logging verbosity

### Entity Configuration
- **Execution Interval**: How often to run (in seconds)
- **Enabled**: Enable/disable automatic execution
- **Name**: Display name for the entity

## 🛠️ Development

### Building the Add-on
```bash
cd addon
chmod +x build.sh
./build.sh
```

### Testing Locally
```bash
cd addon
npm install
npm start
```

## 📝 Migration from Integration to Add-on

If you're using the old HACS integration:

1. Export your entities from the integration
2. Install the Universal Controller Add-on
3. Import your entities in the new Monaco Editor interface
4. Update your Lovelace cards to use the new Add-on interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Support

- **Issues**: [GitHub Issues](https://github.com/Nogg-aholic/UniControl/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Nogg-aholic/UniControl/discussions)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)

---

**Made with ❤️ for the Home Assistant community**
