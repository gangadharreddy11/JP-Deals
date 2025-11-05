# Local Development Setup

## Current Issue

You're running the app locally (`127.0.0.1:5000`) and seeing:
1. ✅ App is running (good!)
2. ❌ psycopg2 not installed locally
3. ❌ DATABASE_URL not set for local development

## Quick Fix for Local Development

### Step 1: Install Dependencies Locally

```bash
pip install -r requirements.txt
```

Or install just psycopg2-binary:
```bash
pip install psycopg2-binary==2.9.9
```

### Step 2: Set DATABASE_URL Locally

**Option A: Environment Variable (Windows PowerShell)**
```powershell
$env:DATABASE_URL="postgresql://postgres:Jai@9441551443@db.anpggnvuffwucresmajc.supabase.co:5432/postgres"
python jp_dealswebsite/app.py
```

**Option B: Create .env file**
1. Create `.env` file in project root:
```
DATABASE_URL=postgresql://postgres:Jai@9441551443@db.anpggnvuffwucresmajc.supabase.co:5432/postgres
SECRET_KEY=your-secret-key-here
```

2. Install python-dotenv:
```bash
pip install python-dotenv
```

3. Update app.py to load .env (if not already)

**Option C: Set in PowerShell Profile**
```powershell
# Add to your PowerShell profile
$env:DATABASE_URL="postgresql://postgres:Jai@9441551443@db.anpggnvuffwucresmajc.supabase.co:5432/postgres"
```

### Step 3: Create Database Tables

Before running, create tables in Supabase:
1. Go to Supabase Dashboard → SQL Editor
2. Run `supabase_setup.sql`

### Step 4: Run Locally

```bash
cd jp_dealswebsite
python app.py
```

Or from root:
```bash
python -m jp_dealswebsite.app
```

## For Vercel Deployment

After local testing works:
1. Set DATABASE_URL in Vercel Dashboard
2. Push code to trigger deployment
3. Vercel will install dependencies automatically

## Testing

After setup:
- Visit `http://localhost:5000/health` - Should show database available
- Visit `http://localhost:5000/` - Should work!

