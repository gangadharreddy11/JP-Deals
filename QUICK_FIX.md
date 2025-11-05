# 🚨 CRITICAL: Set DATABASE_URL Environment Variable

## The Problem
Your app is crashing because `DATABASE_URL` is not set in Vercel.

## Quick Fix (5 minutes)

### Step 1: Get Your Supabase Connection String
1. Open **Supabase Dashboard**: https://supabase.com/dashboard
2. Select your project
3. Go to **Settings** → **Database**
4. Scroll to **Connection string**
5. Click **URI** tab
6. **Copy the connection string** (looks like: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`)

### Step 2: Set Environment Variable in Vercel
1. Open **Vercel Dashboard**: https://vercel.com/dashboard
2. Select your project: **jp-deals11**
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Enter:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste your Supabase connection string
   - **Environment**: Production, Preview, Development (select all)
6. Click **Save**

### Step 3: Create Database Tables
1. In **Supabase Dashboard**, go to **SQL Editor**
2. Click **New Query**
3. Copy and paste the SQL from `supabase_setup.sql`
4. Click **Run** (or press Ctrl+Enter)
5. Verify tables were created in **Table Editor**

### Step 4: Redeploy
1. Go back to **Vercel Dashboard**
2. Go to **Deployments**
3. Click **...** on the latest deployment
4. Click **Redeploy**
5. OR just push a new commit to trigger auto-deploy

## After Setting DATABASE_URL

The app will:
- ✅ Start successfully
- ✅ Show helpful error messages if database connection fails
- ✅ Work normally once database is connected

## Verification

After redeploying, check:
1. Visit your site - you should see the homepage (not a 500 error)
2. Check **Vercel Function Logs** - should show "DATABASE_URL set: Yes"
3. If you see an error page, it will tell you exactly what's wrong

