# 🔧 Fix: Wrong Environment Variable Name!

## The Problem

You set `DATABASE_URL1` but the code is looking for `DATABASE_URL`!

## ✅ Quick Fix

### Step 1: Fix in Vercel

1. Go to **Vercel Dashboard** → Settings → Environment Variables
2. **Delete** `DATABASE_URL1` (if it exists)
3. **Add** `DATABASE_URL` (not `DATABASE_URL1`!)
   - Key: `DATABASE_URL` (exactly this, no numbers!)
   - Value: `postgresql://postgres.anpggnvuffwucresmajc:Jai%409441551443@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres`
   - Environment: ✅ Production ✅ Preview ✅ Development

### Step 2: Redeploy

After fixing the variable name:
1. Go to **Deployments**
2. Click **...** on latest deployment
3. Click **Redeploy**

## Correct Environment Variables

Make sure you have these (with exact names):

✅ `DATABASE_URL` (not `DATABASE_URL1`)  
✅ `SECRET_KEY` (optional but recommended)  
✅ `ADMIN_USERNAME` (optional)  
✅ `ADMIN_PASSWORD` (optional)  

## After Fixing

1. Redeploy
2. Visit: `https://jp-deals11.vercel.app/health`
3. Should show: `"database_url_set": "Yes"`

The variable name must be exactly `DATABASE_URL` - no numbers, no variations!

