"""Constants for Universal Controller integration."""

DOMAIN = "universal_controller"
PLATFORMS = ["sensor"]
VERSION = "1.1.0"

# Default values
DEFAULT_INTERVAL = 30  # seconds
DEFAULT_NAME = "Universal Controller"

# Storage
STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}_entities"

# Attributes
ATTR_HTML_TEMPLATE = "html_template"
ATTR_CSS_STYLES = "css_styles"
ATTR_TYPESCRIPT_CODE = "typescript_code"
ATTR_INTERVAL = "interval"
ATTR_LAST_EXECUTION = "last_execution"
ATTR_EXECUTION_COUNT = "execution_count"
ATTR_LAST_ERROR = "last_error"
