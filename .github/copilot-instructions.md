# Home Assistant Integration Development Instructions

## Project Context
This is a Home Assistant custom integration designed for installation via HACS (Home Assistant Community Store).

## Universal Controller Design Specifications

### Core Architecture
The Universal Controller integration creates custom entities that store executable TypeScript code with HTML/CSS rendering capabilities.

### Custom Entity Requirements
Each Universal Controller entity must store:
- `html_template` (string) - HTML template for rendering
- `css_styles` (string) - CSS styles for the HTML
- `typescript_code` (string) - TypeScript/JavaScript code to execute
- `interval` (number) - Execution frequency in seconds

### Entity Functionality
- Execute TypeScript code at specified intervals
- Update entity state with execution results
- Provide access to Home Assistant API in TypeScript context
- Handle execution errors gracefully

### Card Component
- Renders HTML template with applied CSS styles
- Uses entity selector to choose which Universal Controller entity to display
- Real-time updates when entity state/configuration changes
- Displays execution results and status

### TypeScript Execution Engine
- Evaluates user code in secure context
- Returns data that updates entity state
- Has access to Home Assistant states and services
- Implements execution timeouts and error handling

## HACS Integration Requirements
- Must include `hacs.json` configuration file
- Follow HACS repository structure standards
- Include proper `manifest.json` with all required fields
- Provide clear installation and usage documentation

## Code Style Guidelines

### Python Integration Code
- Follow Home Assistant development standards
- Use async/await for all I/O operations
- Include comprehensive error handling with proper logging
- Use type hints for all function parameters and return values
- Follow Home Assistant integration patterns and lifecycle

### Integration Structure
- Use `config_flow.py` for configuration setup
- Implement proper `__init__.py` with setup/unload functions
- Create services in `services.yaml` with proper field definitions
- Store persistent data using Home Assistant's storage API
- Follow Home Assistant entity and device patterns

## HACS Compatibility
- Ensure all files are in the correct directory structure
- Include version information in `manifest.json`
- Provide proper documentation for HACS installation
- Follow HACS validation requirements

## File Organization
```
custom_components/universal_controller/     # Main integration directory
  __init__.py                              # Integration setup and lifecycle
  manifest.json                           # Integration metadata
  config_flow.py                          # Configuration flow
  services.yaml                           # Service definitions
  const.py                                # Constants and configuration
  sensor.py                               # Custom entity implementation
  execution_engine.py                     # TypeScript execution logic
  www/                                    # Frontend assets
    universal-controller-card.js          # Card implementation
hacs.json                                 # HACS configuration
README.md                                 # Installation and usage docs
```

## Common Patterns
- Use `hass.data[DOMAIN]` for storing integration data
- Implement proper cleanup in `async_unload_entry`
- Follow Home Assistant naming conventions
- Use the integration's logger for all logging operations
- Handle Home Assistant startup and shutdown gracefully
