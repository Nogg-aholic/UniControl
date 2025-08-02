# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.1] - 2025-08-02

### Fixed
- **Add-on Installation**: Removed pre-built image reference causing 403 errors, now builds from source
- **Architecture Support**: Optimized for aarch64, amd64, and armv7 architectures  
- **Build Configuration**: Added proper build.yaml for Home Assistant add-on building
- **Docker Registry**: Fixed "denied" errors by removing non-existent ghcr.io image references

### Technical
- Add-on now builds locally from Dockerfile instead of pulling from registry
- Supports building on Home Assistant Supervisor for all major architectures
- Uses official Home Assistant base images for stability

---

## [1.4.0] - 2025-08-02

### 🎉 Major Architecture Overhaul - HACS Integration → Home Assistant Add-on

### Fixed (Post-Release)
- **Add-on Installation**: Removed pre-built image reference causing 403 errors, now builds from source
- **Architecture Support**: Optimized for aarch64, amd64, and armv7 architectures
- **Build Configuration**: Added proper build.yaml for Home Assistant add-on building

### Added
- **Complete Add-on Implementation**: Restructured from HACS integration to proper Home Assistant Add-on
- **Real JavaScript Execution**: Full Node.js runtime environment replacing Python transpilation
- **Monaco Editor Integration**: Professional VS Code editor experience with TypeScript IntelliSense
- **WebSocket Real-time Communication**: Live updates between editor and execution engine
- **Docker Container Environment**: Secure Alpine Linux container with Node.js 20
- **S6 Service Management**: Proper add-on lifecycle management
- **Bashio Integration**: Configuration parsing and Home Assistant Supervisor communication
- **Build Infrastructure**: PowerShell and Bash build scripts for cross-platform development
- **Configuration Validation**: JSON schema validation for add-on configuration
- **Automated Testing**: Test suite for server functionality and API endpoints
- **Professional Web Interface**: Multi-tab editor with syntax highlighting for JS/HTML/CSS

### Changed
- **Execution Engine**: Migrated from py-mini-racer Python execution to native Node.js
- **Frontend**: Replaced basic textarea editors with Monaco Editor
- **Communication**: Switched from HTTP polling to WebSocket real-time updates
- **Installation Method**: Changed from HACS integration to Home Assistant Add-on
- **Configuration**: Moved from integration config flow to add-on options
- **Storage**: Enhanced entity persistence with JSON file storage
- **API Access**: Direct Home Assistant Supervisor API integration

### Improved
- **Performance**: Significant improvement with native JavaScript execution
- **Developer Experience**: Professional coding environment with autocomplete and error detection
- **Debugging**: Better error handling and execution result reporting
- **Security**: Container isolation and proper execution sandboxing
- **Maintainability**: Clean separation of concerns and modular architecture

### Technical Details
- **Container**: Alpine Linux 3.18 with Node.js 20.x
- **Dependencies**: Express, Socket.IO, node-cron, Lodash, Moment.js, Axios
- **Ports**: Web interface on port 8099 with Home Assistant ingress support
- **Storage**: JSON-based entity persistence in /data directory
- **APIs**: Full Home Assistant state and service access via Supervisor

### Migration Notes
- **Breaking Change**: Complete migration from HACS integration to add-on
- **Installation**: Remove old HACS integration, install new add-on
- **Configuration**: Re-create entities in new add-on interface
- **Benefits**: Significant improvement in functionality and user experience

---

## [1.2.8] - 2025-08-01

### MAJOR IMPROVEMENTS 🚀
- **Real JavaScript Execution**: Implemented proper V8 JavaScript engine with py-mini-racer for native JS/TypeScript execution
- **HACS API Integration**: Full HACS API exposure including repository management, installation, and status functions
- **Monaco Editor**: Added professional TypeScript editor with syntax highlighting, intellisense, and HA/HACS API stubs
- **Service Call Bridge**: Implemented proper service call mechanism between JavaScript and Home Assistant
- **Enhanced Card UI**: Recreated card with improved controls, status display, and Monaco editor integration

### Fixed
- **Service Calls**: Fixed broken service call implementation - HACS functions now work properly
- **JavaScript Execution**: Resolved execution context issues and improved error handling
- **HACS Data Access**: Added robust error handling for HACS data retrieval with safe fallbacks
- **Card Functionality**: Restored complete card functionality with edit, run, and refresh controls
- **Math/Date Utilities**: Fixed utility functions that were overriding JavaScript globals

### Enhanced
- **Error Handling**: Comprehensive error handling throughout the execution engine
- **Logging**: Improved debugging and logging capabilities
- **API Stability**: Robust HACS integration that works whether HACS is installed or not
- **TypeScript Support**: Full TypeScript execution with proper type declarations

## [1.2.7] - 2025-01-27

### CRITICAL FIXES ✅
- **Card Picker Integration**: Fixed card registration so Universal Controller Card now appears in Home Assistant's card picker
- **Editor JavaScript Errors**: Fixed `appendChild entitySelect is null` error in card editor
- **JavaScript Execution**: Disabled problematic py-mini-racer, using stable Python fallback execution
- **Enhanced Card Registry**: Improved card registration for better Home Assistant compatibility

### Fixed
- **Frontend Registration**: Card editor now loads without JavaScript errors
- **Card Selection**: Cards can now be added through the visual card picker interface
- **Config Validation**: Resolved card configuration save issues
- **Execution Engine**: Stable code execution without relocation errors

## [1.2.6] - 2025-01-27

### CRITICAL FIXES
- **Multiple Helpers Support**: Removed incorrect uniqueness check that prevented creating multiple Universal Controller helpers
- **Frontend Registration**: Fixed frontend registration to properly load both main card and editor files
- **Card Display**: Enhanced frontend registration with better error handling and logging

### Fixed
- **Config Flow**: Now allows creating multiple Universal Controller instances with different names
- **Frontend Files**: Properly registers both universal-controller-card.js and universal-controller-card-editor.js
- **Card Loading**: Cards should now appear correctly in the Lovelace interface

## [1.2.5] - 2025-01-27

### Fixed
- **Frontend Registration**: Fixed deprecated register_static_path usage - now using async_register_static_paths correctly
- **Enhanced Error Handling**: Added comprehensive error handling for frontend registration steps

## [1.2.3] - 2025-01-27

### Added
- **Automatic Card Registration**: Each Universal Controller entity now automatically creates its own dashboard card configuration
- **Card Configuration Service**: New `get_card_configs` service to retrieve all registered card configurations
- **Frontend Registration System**: Comprehensive frontend registration with proper static file serving
- **Enhanced Entity Integration**: Cards are automatically created when entities are added to Home Assistant

### Fixed
- **Frontend Initialization**: Fixed frontend registration in async_setup_entry
- **Card Creation Logic**: Implemented automatic card creation during entity lifecycle
- **Service Registration**: Enhanced service registration with proper error handling

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
