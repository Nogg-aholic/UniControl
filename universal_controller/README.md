# Universal Controller Add-on

Execute JavaScript/TypeScript code in Home Assistant with Monaco Editor

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield]

## About

Universal Controller is a Home Assistant add-on that provides a professional JavaScript/TypeScript development environment with real Node.js execution. Create sophisticated automations and custom entities using a full-featured Monaco Editor interface.

## Features

- **🚀 Real JavaScript Execution**: Full Node.js runtime environment
- **💻 Monaco Editor**: Professional VS Code editor experience with IntelliSense
- **🔄 Real-time Updates**: WebSocket communication for live execution feedback
- **🏠 Home Assistant Integration**: Direct access to all HA states and services
- **📋 Multi-tab Interface**: Separate editors for JavaScript, HTML, CSS, and settings
- **⚡ Instant Execution**: Test and run your code with immediate feedback
- **📊 Entity Management**: Create and manage custom entities with persistent storage
- **🎨 Custom Rendering**: HTML templates with CSS styling for beautiful displays

## Installation

1. Add this repository to your Home Assistant add-on store:
   - Go to **Supervisor** → **Add-on Store** → **⋮** → **Repositories**
   - Add: `https://github.com/Nogg-aholic/UniControl`

2. Install the **Universal Controller** add-on

3. Start the add-on and check the logs

4. Access the web interface via the "OPEN WEB UI" button

## Configuration

```yaml
web_port: 8099
log_level: info
```

### Option: `web_port`

Port for the web interface (default: 8099)

### Option: `log_level`

Controls the level of log output by the addon itself. Valid values are `trace`, `debug`, `info`, `notice`, `warning`, `error`, `fatal`.

## Usage

1. **Access the Interface**: Click "OPEN WEB UI" to access the Monaco Editor
2. **Create Entity**: Click "New Entity" to create your first automation
3. **Write Code**: Use the JavaScript tab to write your automation logic
4. **Design Interface**: Use HTML/CSS tabs to create custom displays
5. **Execute**: Click "Execute" to test your code immediately
6. **Save**: Save your entity to run automatically at specified intervals

## Example JavaScript Code

```javascript
// Access Home Assistant states
const temperature = parseFloat(hass.getState('sensor.temperature')?.state || '0');
const motion = hass.getState('binary_sensor.motion');

// Your automation logic
if (motion?.state === 'on' && temperature > 20) {
    // Call Home Assistant services
    await hass.callService('light', 'turn_on', {
        entity_id: 'light.living_room',
        brightness: 255
    });
}

// Return entity state and attributes
return {
    state: temperature > 20 ? 'warm' : 'cool',
    attributes: {
        temperature: temperature,
        motion_detected: motion?.state === 'on',
        last_check: new Date().toISOString()
    }
};
```

## Available APIs

Your JavaScript code has access to:

- **`hass.states`**: All Home Assistant entity states
- **`hass.getState(entityId)`**: Get specific entity state
- **`hass.callService(domain, service, data)`**: Call HA services
- **`hass.setState(entityId, state, attributes)`**: Update entity states
- **`log(...args)`**: Logging function
- **`error(...args)`**: Error logging
- **`_`**: Lodash utility library
- **`moment`**: Date/time manipulation
- **`axios`**: HTTP client for external APIs

## Support

If you have any questions or issues:

1. Check the add-on logs for error messages
2. Review the [documentation](https://github.com/Nogg-aholic/UniControl)
3. Open an issue on [GitHub](https://github.com/Nogg-aholic/UniControl/issues)

## Changelog & Releases

See [CHANGELOG.md](https://github.com/Nogg-aholic/UniControl/blob/master/CHANGELOG.md) for a complete list of changes.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
