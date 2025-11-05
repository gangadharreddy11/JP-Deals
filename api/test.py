# Minimal test handler to verify Vercel setup
def handler(request):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Test Handler Works!</h1>'
    }

