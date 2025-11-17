# Complete Railway Deployment Guide

This guide will walk you through deploying your Django Organization Contributions Backend to Railway from start to finish.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Setting Up Railway Account](#setting-up-railway-account)
4. [Creating a New Project on Railway](#creating-a-new-project-on-railway)
5. [Setting Up PostgreSQL Database](#setting-up-postgresql-database)
6. [Configuring Environment Variables](#configuring-environment-variables)
7. [Deploying from GitHub](#deploying-from-github)
8. [Deploying from Local Machine](#deploying-from-local-machine)
9. [Running Migrations and Setup Commands](#running-migrations-and-setup-commands)
10. [Verifying Deployment](#verifying-deployment)
11. [Post-Deployment Tasks](#post-deployment-tasks)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

- ✅ A Railway account (sign up at [railway.app](https://railway.app))
- ✅ Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)
- ✅ Python 3.10+ installed locally (for testing)
- ✅ Git installed on your machine

---

## Pre-Deployment Checklist

### 1. Review Updated Files

The following files have been updated/created for Railway deployment:

- ✅ `settings.py` - Updated to use environment variables and PostgreSQL
- ✅ `requirements.txt` - Added production dependencies (psycopg2, gunicorn, whitenoise)
- ✅ `Procfile` - Created for Railway to know how to run your app
- ✅ `railway.json` - Created for Railway-specific configuration

### 2. Test Locally (Optional but Recommended)

Before deploying, test that your app works with the new configuration:

```bash
# Install updated requirements
pip install -r requirements.txt

# Test that settings work (should not error)
python manage.py check --deploy

# Collect static files
python manage.py collectstatic --noinput
```

### 3. Commit Your Changes

Make sure all changes are committed to your repository:

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main  # or your branch name
```

---

## Setting Up Railway Account

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"** or **"Login"**
3. Sign up/login using:
   - GitHub (recommended for easy integration)
   - Email
   - Google

---

## Creating a New Project on Railway

### Option A: Deploy from GitHub (Recommended)

1. **Connect GitHub Repository:**
   - In Railway dashboard, click **"New Project"**
   - Select **"Deploy from GitHub repo"**
   - Authorize Railway to access your GitHub account
   - Select your repository: `Org_contributions_backend`
   - Click **"Deploy Now"**

2. **Railway will automatically:**
   - Detect it's a Python/Django project
   - Install dependencies from `requirements.txt`
   - Look for `Procfile` to know how to run the app

### Option B: Deploy from Local Machine

1. **Install Railway CLI:**
   ```bash
   # macOS/Linux
   curl -fsSL https://railway.app/install.sh | sh
   
   # Windows (using PowerShell)
   iwr https://railway.app/install.sh | iex
   
   # Or using npm
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize Railway in your project:**
   ```bash
   cd /home/nikhil/Projects/Org_contributions_backend
   railway init
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

---

## Setting Up PostgreSQL Database

Railway provides PostgreSQL databases that automatically connect to your app.

### Steps:

1. **In Railway Dashboard:**
   - Click on your project
   - Click **"+ New"** button
   - Select **"Database"** → **"Add PostgreSQL"**

2. **Railway will automatically:**
   - Create a PostgreSQL database
   - Set the `DATABASE_URL` environment variable
   - Your Django app will automatically use it (configured in `settings.py`)

3. **Verify Database Connection:**
   - The database service will appear in your project
   - Click on it to see connection details
   - The `DATABASE_URL` is automatically available to your web service

---

## Configuring Environment Variables

You need to set environment variables in Railway for your app to work correctly.

### In Railway Dashboard:

1. Click on your **web service** (not the database)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add the following variables:

#### Required Variables:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `SECRET_KEY` | `[Generate a new secret key]` | Django secret key (see below) |
| `DEBUG` | `False` | Set to False for production |
| `ALLOWED_HOSTS` | `your-app-name.railway.app,*.railway.app` | Your Railway domain |

#### Optional Variables (with defaults):

| Variable Name | Recommended Value | Description |
|--------------|-------------------|-------------|
| `CORS_ALLOW_ALL_ORIGINS` | `False` | Set to False in production |
| `CORS_ALLOWED_ORIGINS` | `https://your-frontend-domain.com` | Comma-separated list of allowed origins |
| `CORS_ALLOW_CREDENTIALS` | `True` | Allow credentials in CORS |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `SECURE_SSL_REDIRECT` | `True` | Force HTTPS redirects |

### Generate a New SECRET_KEY:

Run this in your terminal:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as your `SECRET_KEY` value.

### Example Environment Variables Setup:

```
SECRET_KEY=django-production-secret-key-here-min-50-chars
DEBUG=False
ALLOWED_HOSTS=*.railway.app,your-app-name.railway.app
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://your-frontend.com,https://www.your-frontend.com
LOG_LEVEL=INFO
```

**Note:** `DATABASE_URL` is automatically set by Railway when you add the PostgreSQL service - you don't need to set it manually.

---

## Deploying from GitHub

If you chose GitHub deployment:

1. **Railway automatically deploys when you push to your repository**
2. **To trigger a manual deployment:**
   - Go to your service in Railway
   - Click **"Deployments"** tab
   - Click **"Redeploy"**

3. **Monitor the build:**
   - Watch the build logs in real-time
   - Check for any errors

---

## Running Migrations and Setup Commands

After your app is deployed, you need to run database migrations and seed initial data.

### Option 1: Using Railway CLI

```bash
# Login if not already
railway login

# Link to your project
railway link

# Run migrations
railway run python manage.py migrate

# Seed products
railway run python manage.py seed_products

# Create superuser (optional)
railway run python manage.py createsuperuser
```

### Option 2: Using Railway Dashboard

1. Go to your **web service**
2. Click on **"Deployments"** tab
3. Click on the latest deployment
4. Click **"View Logs"**
5. You can also use the **"Shell"** tab to run commands

### Option 3: Using Release Command (Automatic)

The `Procfile` includes a `release` command that runs migrations automatically:

```
release: python manage.py migrate && python manage.py seed_products
```

This runs automatically before each deployment. However, you may still want to run it manually the first time.

---

## Verifying Deployment

### 1. Check Your App URL

- In Railway dashboard, go to your **web service**
- Click **"Settings"** tab
- Under **"Domains"**, you'll see your app URL (e.g., `your-app-name.railway.app`)
- Railway automatically provides HTTPS

### 2. Test the API

```bash
# Test health endpoint (if you have one)
curl https://your-app-name.railway.app/api/

# Test token endpoint
curl -X POST https://your-app-name.railway.app/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "CEO001"}'
```

### 3. Check Logs

- In Railway dashboard → Your service → **"Deployments"** → **"View Logs"**
- Look for any errors or warnings
- Check that the server started successfully

### 4. Verify Database

```bash
# Using Railway CLI
railway run python manage.py dbshell

# Or check in Railway dashboard → Database → Data tab
```

---

## Post-Deployment Tasks

### 1. Create Admin User

```bash
railway run python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 2. Load Initial Data (if needed)

```bash
# Load default CSV data
railway run python manage.py load_default_csv

# Or create test users
railway run python manage.py create_test_users
```

### 3. Set Up Custom Domain (Optional)

1. In Railway dashboard → Your service → **"Settings"** → **"Domains"**
2. Click **"Generate Domain"** or **"Custom Domain"**
3. Follow instructions to configure DNS

### 4. Configure CORS for Your Frontend

Update `CORS_ALLOWED_ORIGINS` environment variable with your frontend domain:

```
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-frontend.netlify.app
```

### 5. Set Up Monitoring (Optional)

- Railway provides built-in metrics
- Check **"Metrics"** tab in your service
- Set up alerts if needed

---

## Troubleshooting

### Issue: Build Fails

**Solution:**
- Check build logs in Railway dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility
- Check for syntax errors in your code

### Issue: App Crashes on Startup

**Common Causes:**
- Missing environment variables (especially `SECRET_KEY`)
- Database connection issues
- Missing migrations

**Solution:**
```bash
# Check logs
railway logs

# Verify environment variables are set
railway variables

# Run migrations manually
railway run python manage.py migrate
```

### Issue: Static Files Not Loading

**Solution:**
- Ensure `whitenoise` is in `requirements.txt` ✅ (already added)
- Run `collectstatic`:
  ```bash
  railway run python manage.py collectstatic --noinput
  ```

### Issue: Database Connection Error

**Solution:**
- Verify PostgreSQL service is running
- Check that `DATABASE_URL` is automatically set (Railway does this)
- Ensure `psycopg2-binary` is in `requirements.txt` ✅ (already added)

### Issue: CORS Errors

**Solution:**
- Set `CORS_ALLOWED_ORIGINS` with your frontend domain
- Set `CORS_ALLOW_ALL_ORIGINS=False`
- Verify `CORS_ALLOW_CREDENTIALS=True` if using cookies

### Issue: 500 Internal Server Error

**Solution:**
- Check Railway logs for detailed error
- Verify `DEBUG=False` in production
- Check that all required environment variables are set
- Verify database migrations are run

### Issue: Port Already in Use

**Solution:**
- Railway automatically sets `$PORT` environment variable
- Ensure your `Procfile` uses `$PORT` ✅ (already configured)
- Gunicorn should bind to `0.0.0.0:$PORT`

---

## Quick Reference Commands

```bash
# Railway CLI commands
railway login                    # Login to Railway
railway init                    # Initialize Railway in project
railway link                    # Link to existing project
railway up                      # Deploy to Railway
railway logs                    # View logs
railway run <command>           # Run command in Railway environment
railway variables               # View environment variables
railway variables set KEY=value # Set environment variable

# Django commands in Railway
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py seed_products
railway run python manage.py collectstatic --noinput
```

---

## Cost Considerations

- **Railway Hobby Plan:** $5/month includes $5 credit
- **PostgreSQL:** Included in most plans
- **Bandwidth:** Generous free tier
- **Check:** [railway.app/pricing](https://railway.app/pricing) for current pricing

---

## Security Best Practices

1. ✅ **Never commit `.env` files** - Already in `.gitignore`
2. ✅ **Use strong SECRET_KEY** - Generate a new one for production
3. ✅ **Set DEBUG=False** - Already configured via environment variable
4. ✅ **Use HTTPS** - Railway provides this automatically
5. ✅ **Restrict CORS** - Set `CORS_ALLOWED_ORIGINS` instead of allowing all
6. ✅ **Use environment variables** - All sensitive data in Railway variables
7. ✅ **Regular updates** - Keep dependencies updated

---

## Next Steps

After successful deployment:

1. ✅ Test all API endpoints
2. ✅ Set up your frontend to use the new API URL
3. ✅ Configure monitoring and alerts
4. ✅ Set up automated backups (Railway provides this)
5. ✅ Document your API endpoints for your team

---

## Support

- **Railway Docs:** [docs.railway.app](https://docs.railway.app)
- **Railway Discord:** [discord.gg/railway](https://discord.gg/railway)
- **Django Deployment:** [docs.djangoproject.com/en/stable/howto/deployment/](https://docs.djangoproject.com/en/stable/howto/deployment/)

---

## Summary Checklist

- [ ] Code committed and pushed to repository
- [ ] Railway account created
- [ ] Project created on Railway
- [ ] PostgreSQL database added
- [ ] Environment variables configured
- [ ] App deployed successfully
- [ ] Migrations run
- [ ] Initial data seeded
- [ ] Admin user created
- [ ] API endpoints tested
- [ ] CORS configured for frontend
- [ ] Custom domain set up (optional)
- [ ] Monitoring configured (optional)

---

**Congratulations!** Your Django app should now be live on Railway! 🚀

