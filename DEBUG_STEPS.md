# 🔍 Debugging Your 500 Error

## Step 1: Check Function Logs

**CRITICAL:** We need to see what's actually happening.

1. Go to **Vercel Dashboard** → Your Project
2. Click **Functions** tab
3. Click on **api/index.py**
4. Look at the **Logs** section
5. **Copy and share** what you see there

You should see messages like:
- "Starting api/index.py"
- "DATABASE_URL set: Yes/No"
- "Attempting to import Flask app..."
- Any error messages

## Step 2: Test Health Endpoint

After redeploying, try visiting:
```
https://jp-deals11.vercel.app/health
```

This endpoint doesn't require database and will tell us:
- ✅ If app starts successfully
- ✅ If DATABASE_URL is set
- ✅ Database module status

## Step 3: Verify Environment Variables

**Double-check these are set:**

1. Go to **Vercel Dashboard** → **Settings** → **Environment Variables**
2. Verify you see:
   - `DATABASE_URL` = `postgresql://postgres:Jai@9441551443@db.anpggnvuffwucresmajc.supabase.co:5432/postgres`
   - `SECRET_KEY` = (some random string)
3. Make sure **all environments** are selected (Production, Preview, Development)

## Step 4: What the Logs Should Show

**Good logs look like:**
```
============================================================
Starting api/index.py
============================================================
Project root: /var/task
Python version: 3.12.x
DATABASE_URL set: Yes
Attempting to import Flask app...
Flask app imported successfully
Handler ready
```

**Bad logs look like:**
```
DATABASE_URL set: No  ← This means env var not set!
```

OR

```
Import Error: No module named 'psycopg2'  ← Missing dependency
```

## What to Do Next

1. **Share the Function Logs** - This will tell us exactly what's wrong
2. **Test `/health` endpoint** - See if app starts at all
3. **Verify DATABASE_URL** - Make sure it's actually set

## Common Issues

### Issue 1: DATABASE_URL Not Set
**Fix:** Set it in Vercel → Settings → Environment Variables → Redeploy

### Issue 2: psycopg2-binary Not Installing
**Fix:** Check build logs - should see "Installing required dependencies"
If it fails, requirements.txt might have wrong version

### Issue 3: Import Error
**Fix:** Check function logs for specific import error

---

**PLEASE SHARE:**
1. Function logs from `api/index.py`
2. What you see when visiting `/health`
3. Screenshot of Environment Variables page (if possible)

