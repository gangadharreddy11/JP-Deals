# Minimal test handler to verify Vercel Python setup works
print("TEST HANDLER LOADING")

def handler(request):
    print("TEST HANDLER CALLED")
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Test Handler Works!</h1><p>If you see this, Vercel Python is working.</p>'
    }

