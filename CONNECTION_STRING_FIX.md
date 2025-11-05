# 🔧 Fix: DATABASE_URL Connection String Error

## The Problem

Your DATABASE_URL has a password with `@` symbol that needs to be URL-encoded.

**Current (wrong):**
```
postgresql://postgres:Jai@9441551443@db.anpggnvuffwucresmajc.supabase.co:5432/postgres
```

The `@` in the password is being interpreted as the separator between credentials and host!

## ✅ Correct Connection String

**Fixed (correct):**
```
postgresql://postgres:Jai%409441551443@db.anpggnvuffwucresmajc.supabase.co:5432/postgres
```

`@` is URL-encoded as `%40`

## Quick Fix

### For Local Testing (.env file)

Create `.env` file in project root:
```
DATABASE_URL=postgresql://postgres:Jai%409441551443@db.anpggnvuffwucresmajc.supabase.co:5432/postgres
SECRET_KEY=324d9c1ce14d85e20b0a587ccc24f04725487eddad67cd0ae89e93f9a7a928cf
```

### For PowerShell (Temporary)

```powershell
$env:DATABASE_URL="postgresql://postgres:Jai%409441551443@db.anpggnvuffwucresmajc.supabase.co:5432/postgres"
python jp_dealswebsite/app.py
```

### For Vercel

1. Go to **Vercel Dashboard** → Settings → Environment Variables
2. Update `DATABASE_URL` (or add if not exists):
   - Key: `DATABASE_URL`
   - Value: `postgresql://postgres:Jai%409441551443@db.anpggnvuffwucresmajc.supabase.co:5432/postgres`
   - Environment: All (Production, Preview, Development)
3. **Redeploy** (important!)

## Verify Connection

After setting the corrected DATABASE_URL:

1. Visit: `http://localhost:5000/health`
2. Should show:
   ```json
   {
     "status": "ok",
     "database_available": true,
     "database_url_set": "Yes"
   }
   ```

3. Visit: `http://localhost:5000/` - Should work!

## URL Encoding Reference

Common special characters in passwords:
- `@` → `%40`
- `#` → `%23`
- `$` → `%24`
- `%` → `%25`
- `&` → `%26`
- `+` → `%2B`
- `=` → `%3D`

## Before Testing

Make sure database tables are created:
1. Supabase Dashboard → SQL Editor
2. Run `supabase_setup.sql`
3. Verify tables exist

