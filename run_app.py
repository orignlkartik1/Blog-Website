import importlib.util
import sys
import os

# Load user's app dynamically
USER_APP_FILE = "main.py"  # User's file
MODULE_NAME = "main"

spec = importlib.util.spec_from_file_location(MODULE_NAME, USER_APP_FILE)
main_app = importlib.util.module_from_spec(spec)
sys.modules[MODULE_NAME] = main_app
spec.loader.exec_module(main_app)

# Check if the user has a Flask app instance
if hasattr(main_app, 'app'):
    # Use environment variables for host and port
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 3000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    main_app.app.run(host=host, port=port, debug=debug)
else:
    print("Error: Flask app instance not found in main.py")
