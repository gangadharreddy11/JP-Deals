# Fix for psycopg2-binary Not Installing

## The Problem

`psycopg2-binary` is in `requirements.txt` but Vercel isn't installing it at runtime.

## Solution

The issue is that Vercel needs `requirements.txt` at the **root** of your project (which it is), but sometimes it doesn't install dependencies correctly.

### Step 1: Verify requirements.txt Location

Make sure `requirements.txt` is at:
```
/jp_dealswebsite/requirements.txt  ❌ WRONG
/requirements.txt                  ✅ CORRECT (root)
```

### Step 2: Force Clean Build

Sometimes Vercel caches dependencies incorrectly. Force a clean rebuild:

1. **Option A: Clear Build Cache**
   - Vercel Dashboard → Your Project → Settings → General
   - Scroll to "Build & Development Settings"
   - Click "Clear Build Cache" (if available)

2. **Option B: Delete and Redeploy**
   - Go to Deployments
   - Delete the latest deployment
   - Push a new commit to trigger fresh build

### Step 3: Check Build Logs

After redeploying, check build logs for:
```
Installing required dependencies from requirements.txt...
Successfully installed psycopg2-binary-2.9.9
```

If you see errors installing psycopg2-binary, Vercel might need build dependencies.

### Step 4: Alternative - Use psycopg2 Instead

If `psycopg2-binary` still doesn't work, try `psycopg2` (requires system dependencies):

```txt
psycopg2==2.9.9
```

But this might fail if Vercel doesn't have PostgreSQL development libraries.

### Step 5: Verify Installation

After redeploy, check function logs. You should see:
- No "psycopg2 not available" errors
- "Database module available" message

## Why This Happens

Vercel's Python runtime sometimes:
1. Doesn't properly bundle dependencies
2. Has issues with binary packages like psycopg2-binary
3. Caches old dependency lists

## Current Status

Your `requirements.txt` is correct. The issue is likely:
1. Build cache needs clearing
2. Need to force a fresh build
3. Vercel environment needs the dependency properly installed

## Next Steps

1. ✅ Verify `requirements.txt` is at project root
2. ✅ Clear build cache / force fresh deploy
3. ✅ Check build logs for installation confirmation
4. ✅ Test `/health` endpoint after redeploy

