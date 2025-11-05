# 🔍 Check Function Logs - Critical!

## Build Succeeded ✅ But Function Crashing ❌

The build completed successfully, but the function is crashing at runtime. We need to see the actual error.

## Step 1: Check Function Logs (DO THIS NOW)

1. Go to **Vercel Dashboard** → Your Project (`jp-deals11`)
2. Click **Functions** tab
3. Click on **`api/index.py`**
4. Click **Logs** tab
5. **Copy ALL the logs** you see there

**OR**

1. Go to **Deployments** → Latest deployment
2. Click **Functions** → **`api/index.py`**
3. View the **Runtime Logs**

## What to Look For

The logs should show messages like:
- "Starting api/index.py"
- "DATABASE_URL set: Yes/No"
- "Attempting to import Flask app..."
- Any error messages or tracebacks

## Common Issues

### Issue 1: DATABASE_URL Not Set
**Logs will show:**
```
DATABASE_URL set: No
```

**Fix:** Set it in Vercel → Settings → Environment Variables → Redeploy

### Issue 2: Import Error
**Logs will show:**
```
Import Error: ...
```

**Fix:** Check requirements.txt

### Issue 3: Database Connection Error
**Logs will show:**
```
Connection failed: ...
```

**Fix:** Check connection string format

## Share the Logs

Please copy and share:
1. **Function Logs** from `api/index.py` 
2. Any error messages you see

This will tell us EXACTLY what's crashing!

