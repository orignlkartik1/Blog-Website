import importlib.util
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load user's app dynamically
USER_APP_FILE = "main.py"  # User's file
MODULE_NAME = "main"

try:
    spec = importlib.util.spec_from_file_location(MODULE_NAME, USER_APP_FILE)
    if spec is None or spec.loader is None:
        logger.error(f"Failed to load module spec from {USER_APP_FILE}")
        sys.exit(1)
    
    main_app = importlib.util.module_from_spec(spec)
    sys.modules[MODULE_NAME] = main_app
    spec.loader.exec_module(main_app)
    logger.info("Main app module loaded successfully.")

    # Check if the user has a Flask app instance
    if hasattr(main_app, 'app'):
        # Use environment variables for host and port
        host = os.environ.get('FLASK_HOST', '0.0.0.0')
        port = int(os.environ.get('FLASK_PORT', 5000))
        debug = os.environ.get('FLASK_ENV') == 'development'
        
        logger.info(f"Starting Flask app on {host}:{port} (debug={debug})")
        main_app.app.run(host=host, port=port, debug=debug)
    else:
        logger.error("Error: Flask app instance not found in main.py")
        sys.exit(1)
except Exception as e:
    logger.error(f"Error loading or running the app: {str(e)}")
    sys.exit(1)