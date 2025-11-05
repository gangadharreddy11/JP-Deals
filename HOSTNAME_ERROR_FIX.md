# 🔍 Fix: Hostname Resolution Error

## The Problem

The error "could not translate host name" means either:
1. Connection string format is wrong
2. Supabase project is paused
3. Hostname is incorrect

## ✅ Get Correct Connection String from Supabase

### Step 1: Verify Supabase Project Status

1. Go to **Supabase Dashboard**: https://supabase.com/dashboard
2. Check your project status:
   - ✅ **Active** = Good
   - ⏸️ **Paused** = Need to resume (free tier pauses after inactivity)

### Step 2: Get Correct Connection String

1. In Supabase Dashboard → Your Project
2. Go to **Settings** → **Database**
3. Scroll to **Connection string**
4. Click **URI** tab
5. **Copy the ENTIRE connection string** (it should look like):
   ```
   postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```
   
   OR it might be:
   ```
   postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```

### Step 3: Verify Your Connection String Format

Your connection string should follow this format:
```
postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres
```

**Important:** 
- Password should be URL-encoded if it contains special characters
- Host should be exactly as shown in Supabase (might be different format)
- Port is usually `5432` or `6543` (pooler)

## Common Issues

### Issue 1: Wrong Host Format

Supabase might use different host formats:
- `db.[PROJECT-REF].supabase.co` (direct connection)
- `aws-0-[REGION].pooler.supabase.com` (connection pooler)

**Solution:** Use the exact host from Supabase Dashboard

### Issue 2: Password with Special Characters

If password contains `@`, `#`, `%`, etc., URL-encode them:
- `@` → `%40`
- `#` → `%23`
- `%` → `%25`

### Issue 3: Project Paused

Free tier Supabase projects pause after inactivity.

**Solution:** 
1. Go to Supabase Dashboard
2. Click "Resume" if project is paused
3. Wait a few minutes for it to start

## Quick Test

### Test Connection String Locally

```powershell
# Test if hostname resolves
ping db.anpggnvuffwucresmajc.supabase.co

# Or test with Python
python -c "import socket; print(socket.gethostbyname('db.anpggnvuffwucresmajc.supabase.co'))"
```

If hostname doesn't resolve:
- Supabase project might be paused
- Hostname might be wrong
- Need to get correct connection string from Supabase

## Next Steps

1. ✅ **Go to Supabase Dashboard**
2. ✅ **Verify project is ACTIVE** (not paused)
3. ✅ **Copy connection string from Settings → Database → URI**
4. ✅ **Use that EXACT connection string** (don't modify it)
5. ✅ **Set in Vercel Environment Variables**
6. ✅ **Redeploy**

## If Project is Paused

1. Go to Supabase Dashboard
2. Click "Resume" button
3. Wait 2-3 minutes for database to start
4. Then try connecting again

## Alternative: Use Connection Pooler

If direct connection doesn't work, try connection pooler:
- Go to Supabase Dashboard → Settings → Database
- Use **Connection Pooling** connection string instead
- Usually uses port `6543` instead of `5432`

