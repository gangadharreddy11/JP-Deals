# 🔧 Fix: Use Session Pooler (IPv4 Compatible)

## The Problem

Supabase shows: **"Not IPv4 compatible"** - The direct connection uses IPv6, but Vercel/local networks need IPv4.

## ✅ Solution: Use Session Pooler

You need to use **Session Pooler** connection string instead of Direct connection.

### Step 1: Get Session Pooler Connection String

1. In Supabase Dashboard → **API Settings** → **Connection String** modal
2. Change **Method** dropdown from **"Direct connection"** to **"Session mode"** (or **"Transaction mode"**)
3. Copy the new connection string (will have different hostname and port)
4. It should look like:
   ```
   postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

### Step 2: Update Connection String

Replace `[YOUR_PASSWORD]` with your actual password (URL-encoded if needed):

**If password is `Jai@9441551443`:**
```
postgresql://postgres.anpggnvuffwucresmajc:Jai%409441551443@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**Note:** The pooler connection string format is different:
- Uses `postgres.[PROJECT-REF]` as username (not just `postgres`)
- Uses `pooler.supabase.com` hostname
- Uses port `6543` (not `5432`)

### Step 3: Find Your Region

The pooler hostname includes your region. Check:
1. Supabase Dashboard → Settings → General
2. Look for "Region" or check the pooler connection string for the region code

### Step 4: Set in Vercel

1. **Vercel Dashboard** → Settings → Environment Variables
2. Update `DATABASE_URL` with the **Session Pooler** connection string
3. **Redeploy**

### Step 5: Set Locally (.env)

Create `.env` file:
```
DATABASE_URL=postgresql://postgres.anpggnvuffwucresmajc:Jai%409441551443@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

## Why Session Pooler?

- ✅ IPv4 compatible (works with Vercel)
- ✅ Better for serverless functions
- ✅ Handles connection pooling automatically
- ✅ Recommended for cloud deployments

## Quick Steps

1. ✅ In Supabase → Change Method to **"Session mode"**
2. ✅ Copy the pooler connection string
3. ✅ Replace `[YOUR_PASSWORD]` with your password (URL-encoded)
4. ✅ Set in Vercel Environment Variables
5. ✅ Set in local `.env` file
6. ✅ Redeploy

This will fix the hostname resolution error!

