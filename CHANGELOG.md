# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-01

### Added
- **Initial stable release** 🎉
- Real JavaScript/TypeScript execution using py-mini-racer
- Advanced HTML template engine with conditionals (`{% if %}`) and loops (`{% for %}`)
- Template functions: `now()`, `format_date()`, `upper()`, `lower()`, `length()`, `round()`, `default()`, `state()`, `attr()`
- Custom Lovelace cards with inline editor and live preview
- Centralized ticker management system with execution tracking
- HACS compatibility for easy installation
- Configuration flow for UI-based setup
- Comprehensive error handling and recovery
- Persistent storage using Home Assistant's storage API
- Entity lifecycle management with proper cleanup

### Services
- `universal_controller.create_entity` - Create new Universal Controller entities
- `universal_controller.update_entity` - Update existing entity configuration  
- `universal_controller.delete_entity` - Remove entities
- `universal_controller.execute_entity` - Manual execution trigger

### Features
- **Real JavaScript Execution**: Full V8 JavaScript engine support via py-mini-racer
- **Advanced Templates**: Conditionals, loops, and functions in HTML templates
- **Home Assistant Integration**: Full access to HA states and services from JavaScript
- **Live Editing**: Inline editor in Lovelace cards with syntax highlighting
- **Error Recovery**: Automatic recovery from execution failures
- **Production Ready**: Comprehensive error handling and logging

### Documentation
- Complete installation guide
- Working examples with complex templates
- HACS installation instructions
- API documentation
- Contributing guidelines

### Technical
- Python 3.9+ support
- Home Assistant 2023.1.0+ compatibility
- HACS 1.6.0+ support
- Follows Home Assistant development standards
- Comprehensive test coverage ready

## [Unreleased]

### Planned Features
- Additional template functions (math helpers, string manipulation)
- Enhanced UI/UX with better syntax highlighting
- Entity grouping and categories
- Template debugging tools
- Configuration export/import functionality
