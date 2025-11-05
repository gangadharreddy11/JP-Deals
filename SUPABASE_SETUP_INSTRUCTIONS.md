# Supabase Setup Instructions

## Step 1: Get Your Supabase Connection Details

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Go to **Settings** → **Database**
4. Find **Connection string** → **URI**
5. Copy the connection string (it looks like: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`)

## Step 2: Create Tables in Supabase

1. Go to **SQL Editor** in Supabase Dashboard
2. Click **New Query**
3. Copy and paste the contents of `supabase_setup.sql`
4. Click **Run** to execute
5. Verify tables were created by going to **Table Editor**

## Step 3: Set Environment Variables in Vercel

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add these variables:

   **DATABASE_URL**
   - Value: Your Supabase connection string from Step 1
   - Example: `postgresql://postgres:yourpassword@db.xxx.supabase.co:5432/postgres`

   **SECRET_KEY** (if not already set)
   - Generate a random string: `python -c "import secrets; print(secrets.token_hex(32))"`
   - Value: The generated string

   **ADMIN_USERNAME** (optional, defaults to 'admin')
   - Value: Your admin username

   **ADMIN_PASSWORD** (optional, defaults to 'admin123')
   - Value: Your admin password

## Step 4: Deploy

1. Commit and push all changes
2. Vercel will automatically redeploy
3. Check the deployment logs

## Troubleshooting

If you get connection errors:
- Verify DATABASE_URL is correct
- Check Supabase project is active
- Ensure tables were created successfully
- Check Vercel function logs for detailed error messages

