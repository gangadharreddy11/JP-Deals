# Vercel Deployment Guide

This guide will help you deploy your Flask deals website to Vercel.

## Important Limitations

⚠️ **CRITICAL WARNINGS:**

1. **Database Persistence**: SQLite databases stored in `/tmp` on Vercel are **ephemeral** - they will be deleted when the serverless function times out or restarts. Your data will NOT persist between deployments.

2. **File Uploads**: Uploaded images stored in `/tmp` will also be lost. 

3. **Recommended Solutions**:
   - Use a cloud database (PostgreSQL, MySQL) like:
     - Vercel Postgres (recommended)
     - Supabase
     - PlanetScale
     - Railway
   - Use cloud storage for images:
     - Vercel Blob Storage
     - AWS S3
     - Cloudinary
     - ImageKit

## Deployment Steps

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

### 3. Deploy

From the project root directory:

```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Yes**
- Which scope? (Select your account)
- Link to existing project? **No** (for first deployment)
- What's your project's name? (Enter a name or press Enter for default)
- In which directory is your code located? **./** (press Enter)

### 4. Set Environment Variables (Optional but Recommended)

In the Vercel dashboard or via CLI:

```bash
vercel env add SECRET_KEY
# Enter a strong random secret key

vercel env add ADMIN_USERNAME
# Enter your admin username (default: admin)

vercel env add ADMIN_PASSWORD
# Enter your admin password (default: admin123)
```

### 5. Production Deployment

```bash
vercel --prod
```

## Project Structure

```
├── api/
│   └── index.py          # Serverless handler
├── jp_dealswebsite/
│   ├── app.py            # Flask application
│   ├── templates/        # HTML templates
│   └── static/           # Static files (CSS, JS, images)
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── .vercelignore        # Files to ignore during deployment
```

## Testing Locally with Vercel

```bash
vercel dev
```

This will start a local server that mimics Vercel's environment.

## Troubleshooting

### Database not initializing
- Check that the database file path is accessible
- Review Vercel function logs: `vercel logs`

### Static files not loading
- Ensure static files are in `jp_dealswebsite/static/`
- Check the routes in `vercel.json`

### Session issues
- Ensure `SECRET_KEY` environment variable is set
- Sessions may not persist across serverless invocations

## Next Steps

For production use, consider:
1. Migrating to PostgreSQL (Vercel Postgres)
2. Using Vercel Blob Storage for image uploads
3. Setting up proper authentication
4. Adding monitoring and logging

## Support

For issues specific to:
- Vercel: https://vercel.com/docs
- Flask: https://flask.palletsprojects.com/

