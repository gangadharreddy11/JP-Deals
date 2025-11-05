import sys
import os

# Ensure we can see errors
sys.stderr.write("Starting api/index.py\n")
sys.stderr.flush()

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set Vercel environment
os.environ['VERCEL'] = '1'

try:
    sys.stderr.write("Attempting to import Flask app...\n")
    sys.stderr.flush()
    
    # Import the Flask app
    from jp_dealswebsite.app import app
    
    sys.stderr.write("Flask app imported successfully\n")
    sys.stderr.flush()
    
    # Vercel expects the handler to be the Flask WSGI app
    handler = app
    
except Exception as e:
    import traceback
    error_msg = f"Error importing Flask app: {str(e)}\n{traceback.format_exc()}"
    sys.stderr.write(error_msg + "\n")
    sys.stderr.flush()
    
    # Create a minimal error handler
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
    
    handler = error_app

sys.stderr.write("Handler ready\n")
sys.stderr.flush()
