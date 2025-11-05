import sys
import os
import traceback

# CRITICAL: Print immediately to verify script is running
print("=" * 50)
print("API INDEX.PY STARTING")
print("=" * 50)

# Add parent directory to path to import app
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set Vercel environment variable for app detection
os.environ['VERCEL'] = '1'

# Print debug info
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")
print(f"Project root: {project_root}")
print(f"Current working directory: {os.getcwd()}")

# List files in project root
try:
    print(f"Files in project root: {os.listdir(project_root)}")
except Exception as e:
    print(f"Could not list project root: {e}")

# List files in jp_dealswebsite
try:
    jp_dir = os.path.join(project_root, 'jp_dealswebsite')
    if os.path.exists(jp_dir):
        print(f"Files in jp_dealswebsite: {os.listdir(jp_dir)}")
    else:
        print(f"jp_dealswebsite directory not found at: {jp_dir}")
except Exception as e:
    print(f"Could not list jp_dealswebsite: {e}")

# Try to import the app with detailed error handling
try:
    print("Attempting to import jp_dealswebsite.app...")
    from jp_dealswebsite.app import app
    print("Successfully imported app!")
    print(f"App type: {type(app)}")
    
    # Vercel expects the handler to be named 'handler' or 'app'
    handler = app
    print("Handler assigned successfully")
    
except ImportError as e:
    # Import error - create a simple error handler
    error_details = f"Import Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}\n\nPython Path: {sys.path}\n\nProject Root: {project_root}"
    print(error_details)
    
    # Create minimal WSGI handler that doesn't need Flask
    def error_handler(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        error_html = f'''
        <!DOCTYPE html>
        <html>
        <head><title>Deployment Error</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>Deployment Error</h1>
            <h2>Import Error</h2>
            <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;">{error_details}</pre>
        </body>
        </html>
        '''
        start_response(status, headers)
        return [error_html.encode('utf-8')]
    
    handler = error_handler
    print("Error handler created")
    
except Exception as e:
    # Other errors during import
    error_details = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
    print(error_details)
    
    # Create minimal WSGI handler
    def error_handler(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        error_html = f'''
        <!DOCTYPE html>
        <html>
        <head><title>Deployment Error</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>Deployment Error</h1>
            <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;">{error_details}</pre>
        </body>
        </html>
        '''
        start_response(status, headers)
        return [error_html.encode('utf-8')]
    
    handler = error_handler
    print("Exception handler created")

print("=" * 50)
print("HANDLER CREATED SUCCESSFULLY")
print("=" * 50)

