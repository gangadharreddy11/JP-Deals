import sys
import os
import traceback

# Add parent directory to path to import app
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set Vercel environment variable for app detection
os.environ['VERCEL'] = '1'

# Create error handler function
def create_error_handler(error_msg):
    from flask import Flask
    error_app = Flask(__name__)
    
    @error_app.route('/<path:path>')
    @error_app.route('/')
    def error_handler(path=''):
        return f'''
        <html>
        <head><title>Deployment Error</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>Deployment Error</h1>
            <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;">{error_msg}</pre>
        </body>
        </html>
        ''', 500
    
    return error_app

# Try to import the app
try:
    from jp_dealswebsite.app import app
    
    # Vercel expects the handler to be named 'handler' or 'app'
    handler = app
    
except ImportError as e:
    # Import error - show detailed error
    error_details = f"Import Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}\n\nPython Path: {sys.path}"
    print(error_details)
    handler = create_error_handler(error_details)
    
except Exception as e:
    # Other errors during import
    error_details = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
    print(error_details)
    handler = create_error_handler(error_details)

