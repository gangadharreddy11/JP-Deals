# 🚀 Complete Setup Guide - Final Steps

## Your Connection String
```
postgresql://postgres:Jai@9441551443@db.anpggnvuffwucresmajc.supabase.co:5432/postgres
```

## ✅ Step-by-Step Setup

### Step 1: Set Environment Variables in Vercel

1. Go to **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**
2. Add these variables:

   **Variable 1: DATABASE_URL**
   - Key: `DATABASE_URL`
   - Value: `postgresql://postgres:Jai@9441551443@db.anpggnvuffwucresmajc.supabase.co:5432/postgres`
   - Environment: ✅ Production ✅ Preview ✅ Development

   **Variable 2: SECRET_KEY**
   - Key: `SECRET_KEY`
   - Value: `324d9c1ce14d85e20b0a587ccc24f04725487eddad67cd0ae89e93f9a7a928cf`
   - Environment: ✅ Production ✅ Preview ✅ Development

   **Variable 3: ADMIN_USERNAME** (Optional)
   - Key: `ADMIN_USERNAME`
   - Value: `admin` (or your preferred username)
   - Environment: ✅ Production ✅ Preview ✅ Development

   **Variable 4: ADMIN_PASSWORD** (Optional)
   - Key: `ADMIN_PASSWORD`
   - Value: `admin123` (change this to something secure!)
   - Environment: ✅ Production ✅ Preview ✅ Development

3. Click **Save** for each variable

### Step 2: Create Database Tables in Supabase

**CRITICAL:** Do this BEFORE redeploying!

1. Go to **Supabase Dashboard**: https://supabase.com/dashboard/project/anpggnvuffwucresmajc
2. Click **SQL Editor** in the left sidebar
3. Click **New Query**
4. Copy the entire SQL from `supabase_setup.sql` (it's below)
5. Paste into the SQL Editor
6. Click **Run** (or press Ctrl+Enter / Cmd+Enter)
7. You should see: "Success. No rows returned"
8. Verify tables:
   - Go to **Table Editor**
   - You should see: `categories`, `deals`, `deal_of_the_day`

### Step 3: Redeploy on Vercel

**Option A: Auto-deploy (Recommended)**
1. Commit and push your code:
   ```bash
   git add .
   git commit -m "Add Supabase database support"
   git push
   ```
2. Vercel will automatically redeploy

**Option B: Manual Redeploy**
1. Go to **Vercel Dashboard** → **Deployments**
2. Click **...** on the latest deployment
3. Click **Redeploy**
4. Wait for deployment to complete

### Step 4: Verify Everything Works

1. Visit your site: `https://jp-deals11.vercel.app`
2. Should see homepage (not 500 error)
3. Check logs:
   - Vercel Dashboard → Your Project → **Functions** → `api/index.py`
   - Should see: "DATABASE_URL set: Yes"
4. Try admin:
   - Visit `/admin/login`
   - Login with your admin credentials
   - Should work!

## SQL Script to Run in Supabase

Copy this entire script and run it in Supabase SQL Editor:

```sql
-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create deals table
CREATE TABLE IF NOT EXISTS deals (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    price REAL NOT NULL,
    original_price REAL,
    discount INTEGER,
    image_filename TEXT,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    description TEXT,
    stock_quantity INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create deal_of_the_day table
CREATE TABLE IF NOT EXISTS deal_of_the_day (
    id SERIAL PRIMARY KEY,
    deal_id INTEGER NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default categories
INSERT INTO categories(name, slug) VALUES
    ('Electronics', 'electronics'),
    ('Fashion', 'fashion'),
    ('Home & Kitchen', 'home'),
    ('Beauty', 'beauty'),
    ('Books', 'books'),
    ('Sports', 'sports')
ON CONFLICT (name) DO NOTHING;
```

## Troubleshooting

### If you still get 500 errors:

1. **Check Environment Variables:**
   - Go to Vercel → Settings → Environment Variables
   - Make sure `DATABASE_URL` is set correctly
   - Make sure all environments are selected

2. **Check Database Tables:**
   - Go to Supabase → Table Editor
   - Verify `categories`, `deals`, `deal_of_the_day` exist

3. **Check Vercel Logs:**
   - Vercel Dashboard → Your Project → Functions → `api/index.py`
   - Look for error messages

4. **Verify Connection String:**
   - Make sure you copied the entire connection string
   - No extra spaces or line breaks

## Success Indicators

✅ No more 500 errors  
✅ Homepage loads  
✅ Categories show up  
✅ Admin panel works  
✅ Can add/edit deals  

## Next Steps After Setup

1. Add some deals through the admin panel
2. Set up a "Deal of the Day"
3. Customize categories as needed

Your site should now work perfectly! 🎉

