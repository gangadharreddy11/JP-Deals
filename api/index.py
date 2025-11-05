import sys
import os
import traceback

# Ensure we can see errors - write immediately
# Use print() as well for better visibility in Vercel logs
print("=" * 60)
print("Starting api/index.py")
print("=" * 60)
sys.stderr.write("=" * 60 + "\n")
sys.stderr.write("Starting api/index.py\n")
sys.stderr.write("=" * 60 + "\n")
sys.stderr.flush()

# Add parent directory to path
try:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    print(f"Project root: {project_root}")
    sys.stderr.write(f"Project root: {project_root}\n")
except Exception as e:
    print(f"Warning: Could not set project root: {e}")
    sys.stderr.write(f"Warning: Could not set project root: {e}\n")
sys.stderr.flush()

# Set Vercel environment
os.environ['VERCEL'] = '1'

# Print environment info for debugging
try:
    python_version = sys.version
    db_url1_set = 'Yes' if os.environ.get('DATABASE_URL1') else 'No'
    db_url_set = 'Yes' if os.environ.get('DATABASE_URL') else 'No'
    db_url_final = 'DATABASE_URL1' if os.environ.get('DATABASE_URL1') else ('DATABASE_URL' if os.environ.get('DATABASE_URL') else 'None')
    print(f"Python version: {python_version}")
    print(f"DATABASE_URL1 set: {db_url1_set}")
    print(f"DATABASE_URL set: {db_url_set}")
    print(f"Using: {db_url_final}")
    sys.stderr.write(f"Python version: {python_version}\n")
    sys.stderr.write(f"DATABASE_URL1 set: {db_url1_set}\n")
    sys.stderr.write(f"DATABASE_URL set: {db_url_set}\n")
    sys.stderr.write(f"Using: {db_url_final}\n")
except Exception as e:
    print(f"Error getting env info: {e}")
sys.stderr.flush()

# Try to import Flask app - but handle ANY error gracefully
handler = None
app_import_error = None

try:
    print("Attempting to import Flask app...")
    sys.stderr.write("Attempting to import Flask app...\n")
    sys.stderr.flush()
    
    # Import the Flask app
    from jp_dealswebsite.app import app
    
    print("Flask app imported successfully")
    sys.stderr.write("Flask app imported successfully\n")
    sys.stderr.flush()
    
    # Vercel expects the handler to be the Flask WSGI app
    handler = app
    
except ImportError as e:
    app_import_error = f"Import Error: {str(e)}\n{traceback.format_exc()}"
    print(f"IMPORT ERROR: {app_import_error}")
    sys.stderr.write(f"IMPORT ERROR: {app_import_error}\n")
    sys.stderr.flush()
except Exception as e:
    app_import_error = f"Error importing Flask app: {str(e)}\n{traceback.format_exc()}"
    print(f"EXCEPTION: {app_import_error}")
    sys.stderr.write(f"EXCEPTION: {app_import_error}\n")
    sys.stderr.flush()

# If import failed, create error handler
if handler is None:
    print("Creating error handler...")
    sys.stderr.write("Creating error handler...\n")
    sys.stderr.flush()
    
    try:
        # Try to use Flask for error page
        from flask import Flask
        error_app = Flask(__name__)
        
        @error_app.route('/<path:path>')
        @error_app.route('/')
        def error_handler(path=''):
            error_msg = app_import_error or "Unknown error"
            return f'''
            <html>
            <head><title>Deployment Error</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h1>⚠️ Deployment Error</h1>
                <p>The application failed to start. Check the details below:</p>
                <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;">{error_msg}</pre>
                <h2>Common Fixes:</h2>
                <ul>
                    <li>Make sure <code>DATABASE_URL</code> is set in Vercel Environment Variables</li>
                    <li>Use Session Pooler connection string (not Direct connection)</li>
                    <li>Check that all dependencies are in <code>requirements.txt</code></li>
                    <li>Verify your Supabase database connection string is correct</li>
                </ul>
            </body>
            </html>
            ''', 500
        
        handler = error_app
        print("Error handler created with Flask")
        sys.stderr.write("Error handler created with Flask\n")
        
    except Exception as e:
        # Last resort - minimal WSGI handler without Flask
        print(f"Could not create Flask error handler: {e}")
        sys.stderr.write(f"Could not create Flask error handler: {e}\n")
        sys.stderr.write("Creating minimal WSGI handler...\n")
        
        def minimal_error_handler(environ, start_response):
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
            error_msg = app_import_error or "Unknown error"
            html = f'''
            <html>
            <head><title>Deployment Error</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h1>⚠️ Deployment Error</h1>
                <p>The application failed to start.</p>
                <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;">{error_msg}</pre>
            </body>
            </html>
            '''
            start_response(status, headers)
            return [html.encode('utf-8')]
        
        handler = minimal_error_handler
        print("Minimal WSGI handler created")
        sys.stderr.write("Minimal WSGI handler created\n")

print("Handler ready")
sys.stderr.write("Handler ready\n")
sys.stderr.flush()
