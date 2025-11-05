import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jp_dealswebsite.app import app

# Vercel expects the handler to be named 'handler' or 'app'
# Export the Flask WSGI application
handler = app

