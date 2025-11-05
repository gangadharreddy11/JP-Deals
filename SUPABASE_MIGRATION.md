# Supabase Migration Guide

## Environment Variables Required

Add these to your Vercel project settings:

1. **DATABASE_URL** - Your Supabase PostgreSQL connection string
   - Format: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`
   - Get it from: Supabase Dashboard → Settings → Database → Connection string (URI)

2. **SUPABASE_URL** - Your Supabase project URL
   - Format: `https://[PROJECT_REF].supabase.co`

3. **SUPABASE_KEY** - Your Supabase anon/public key
   - Get it from: Supabase Dashboard → Settings → API

## Steps to Complete Migration

1. **Create Tables in Supabase:**
   - Go to Supabase Dashboard → SQL Editor
   - Run the SQL from `supabase_setup.sql` (will be created)

2. **Set Environment Variables in Vercel:**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add all three variables above

3. **Deploy:**
   - Commit and push changes
   - Vercel will automatically redeploy

## Database Schema

The migration converts from SQLite to PostgreSQL:

- `INTEGER PRIMARY KEY AUTOINCREMENT` → `SERIAL PRIMARY KEY`
- `?` placeholders → `%s` placeholders  
- `BOOLEAN 1/0` → `true/false`
- Row access: `row[0]` → `row['column']` or `row.column` (with RealDictCursor)

