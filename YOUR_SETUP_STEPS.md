# ✅ Your Supabase Connection String

Your connection string:
```
postgresql://postgres:Jai@9441551443@db.anpggnvuffwucresmajc.supabase.co:5432/postgres
```

## Next Steps

### 1. Add to Vercel Environment Variables

1. Go to **Vercel Dashboard**: https://vercel.com/dashboard
2. Select your project: **jp-deals11**
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Enter:
   - **Key**: `DATABASE_URL`
   - **Value**: `postgresql://postgres:Jai@9441551443@db.anpggnvuffwucresmajc.supabase.co:5432/postgres`
   - **Environment**: Select all (Production, Preview, Development)
6. Click **Save**

### 2. Create Database Tables in Supabase

**IMPORTANT:** Before deploying, you must create the tables!

1. Go to **Supabase Dashboard** → **SQL Editor**
2. Click **New Query**
3. Copy and paste the SQL from `supabase_setup.sql` (see below)
4. Click **Run** (or press Ctrl+Enter)
5. Verify tables were created in **Table Editor**

### 3. Redeploy on Vercel

After setting the environment variable:
- Option A: Push a commit to trigger auto-deploy
- Option B: Go to Vercel → Deployments → Click "..." → Redeploy

## SQL to Run in Supabase

Run this in Supabase SQL Editor:

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

## Verification

After redeploying:
1. Visit your site - should load without 500 errors
2. Check Vercel Function Logs - should show "DATABASE_URL set: Yes"
3. Try accessing `/admin` - should work once tables are created

## Note

If your password contains special characters (like `@`), Supabase has already encoded it correctly in the connection string. The connection string looks good as-is.

