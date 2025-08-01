# Universal Controller Examples

## Basic Example

Create a simple entity with HTML template and TypeScript code:

```yaml
service: universal_controller.create_entity
data:
  name: "My Weather Widget"
  entity_id: "weather_widget"
  interval: 300  # 5 minutes
  html_template: |
    <div class="weather-widget">
      <h3>{{friendly_name}}</h3>
      <div class="weather-info">
        <p><strong>Temperature:</strong> {{temperature}}°C</p>
        <p><strong>Humidity:</strong> {{humidity}}%</p>
        <p><strong>Last Updated:</strong> {{format_date(now, 'locale')}}</p>
      </div>
      {% if temperature > 25 %}
        <div class="hot-warning">🔥 It's hot outside!</div>
      {% endif %}
    </div>
  css_styles: |
    .weather-widget {
      background: linear-gradient(135deg, #74b9ff, #0984e3);
      color: white;
      padding: 20px;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .weather-info p {
      margin: 8px 0;
    }
    .hot-warning {
      background: #ff4757;
      padding: 8px;
      border-radius: 6px;
      margin-top: 10px;
      text-align: center;
    }
  typescript_code: |
    // Get weather data from Home Assistant
    const weatherEntity = states['weather.home'];
    
    if (weatherEntity) {
      return {
        temperature: weatherEntity.attributes.temperature,
        humidity: weatherEntity.attributes.humidity,
        condition: weatherEntity.state,
        timestamp: new Date().toISOString()
      };
    }
    
    return {
      temperature: 22,
      humidity: 50,
      condition: 'unknown',
      timestamp: new Date().toISOString()
    };
```

## Advanced Template Features

### Conditionals
```html
{% if state == 'on' %}
  <div class="status-on">Device is ON</div>
{% endif %}

{% if temperature > 25 %}
  <div class="warning">Hot weather!</div>
{% endif %}
```

### Loops
```html
<h3>All Lights:</h3>
<ul>
{% for light in lights %}
  <li>{{light.name}}: {{light.state}}</li>
{% endfor %}
</ul>
```

### Template Functions
```html
<p>Current time: {{now()}}</p>
<p>Formatted date: {{format_date(last_execution, 'locale')}}</p>
<p>Uppercase text: {{upper(friendly_name)}}</p>
<p>Count: {{length(lights)}}</p>
<p>Temperature: {{round(temperature, 1)}}°C</p>
<p>Status: {{default(status, 'Unknown')}}</p>
<p>Light state: {{state('light.living_room')}}</p>
<p>Light brightness: {{attr('light.living_room', 'brightness')}}</p>
```

## Complex Example: Light Dashboard

```yaml
service: universal_controller.update_entity
data:
  entity_id: sensor.light_dashboard
  html_template: |
    <div class="light-dashboard">
      <h2>🏠 Light Dashboard</h2>
      <div class="summary">
        <div class="stat">
          <span class="number">{{lights_on}}</span>
          <span class="label">Lights ON</span>
        </div>
        <div class="stat">
          <span class="number">{{total_lights}}</span>
          <span class="label">Total Lights</span>
        </div>
        <div class="stat">
          <span class="number">{{power_usage}}W</span>
          <span class="label">Power Usage</span>
        </div>
      </div>
      
      <h3>Light Status</h3>
      <div class="lights-grid">
        {% for light in lights %}
          <div class="light-card {{light.state}}">
            <div class="light-name">{{light.name}}</div>
            <div class="light-state">{{upper(light.state)}}</div>
            {% if light.brightness %}
              <div class="brightness">{{light.brightness}}%</div>
            {% endif %}
          </div>
        {% endfor %}
      </div>
      
      <div class="last-update">
        Last updated: {{format_date(now, 'locale')}}
      </div>
    </div>
  css_styles: |
    .light-dashboard {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      padding: 20px;
      background: #1a1a1a;
      color: #ffffff;
      border-radius: 12px;
    }
    
    .summary {
      display: flex;
      gap: 20px;
      margin: 20px 0;
    }
    
    .stat {
      background: #333;
      padding: 15px;
      border-radius: 8px;
      text-align: center;
      flex: 1;
    }
    
    .stat .number {
      display: block;
      font-size: 24px;
      font-weight: bold;
      color: #4fc3f7;
    }
    
    .stat .label {
      font-size: 12px;
      opacity: 0.7;
    }
    
    .lights-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 15px;
      margin: 20px 0;
    }
    
    .light-card {
      background: #2a2a2a;
      padding: 15px;
      border-radius: 8px;
      border-left: 4px solid #666;
      transition: all 0.3s ease;
    }
    
    .light-card.on {
      border-left-color: #4fc3f7;
      background: #1e3a5f;
    }
    
    .light-card.off {
      border-left-color: #666;
    }
    
    .light-name {
      font-weight: bold;
      margin-bottom: 5px;
    }
    
    .light-state {
      font-size: 12px;
      opacity: 0.8;
    }
    
    .brightness {
      font-size: 11px;
      color: #4fc3f7;
      margin-top: 5px;
    }
    
    .last-update {
      text-align: center;
      margin-top: 20px;
      font-size: 12px;
      opacity: 0.6;
    }
  typescript_code: |
    // Get all light entities
    const lightStates = Object.values(states).filter(entity => 
      entity.entity_id.startsWith('light.')
    );
    
    // Process light data
    const lights = lightStates.map(light => ({
      entity_id: light.entity_id,
      name: light.attributes.friendly_name || light.entity_id.replace('light.', '').replace(/_/g, ' '),
      state: light.state,
      brightness: light.attributes.brightness ? Math.round((light.attributes.brightness / 255) * 100) : null
    }));
    
    // Calculate statistics
    const lightsOn = lights.filter(light => light.state === 'on').length;
    const powerUsage = lights
      .filter(light => light.state === 'on')
      .reduce((total, light) => total + (light.brightness ? (light.brightness / 100) * 10 : 10), 0);
    
    return {
      lights: lights,
      lights_on: lightsOn,
      total_lights: lights.length,
      power_usage: Math.round(powerUsage)
    };
```

## Adding Cards to Dashboard

```yaml
type: custom:universal-controller-card
entity: sensor.weather_widget
title: Weather Information

# Or with inline editor
type: custom:universal-controller-card
entity: sensor.light_dashboard
title: Smart Home Lights
show_editor: false  # Set to true to show editor by default
```

## Available Template Variables

- `{{state}}` - Entity state
- `{{entity_id}}` - Entity ID
- `{{friendly_name}}` - Entity friendly name
- `{{attributes.property}}` - Any entity attribute
- `{{result.property}}` - Any property from TypeScript execution result
- `{{now}}` - Current timestamp
- `{{states.entity_id.state}}` - State of any entity

## Available Template Functions

- `{{now()}}` - Current timestamp
- `{{format_date(date, format)}}` - Format date
- `{{upper(text)}}` - Uppercase text
- `{{lower(text)}}` - Lowercase text  
- `{{length(array_or_object)}}` - Get length/count
- `{{round(number, digits)}}` - Round number
- `{{default(value, fallback)}}` - Default value if null/undefined
- `{{state('entity_id')}}` - Get state of any entity
- `{{attr('entity_id', 'attribute')}}` - Get attribute of any entity
