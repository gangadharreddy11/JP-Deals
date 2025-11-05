# Minimal test - does this work?
print("MINIMAL HANDLER LOADING")
import sys
sys.stderr.write("MINIMAL HANDLER LOADING\n")
sys.stderr.flush()

def handler(request):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Minimal Handler Works!</h1>'
    }

