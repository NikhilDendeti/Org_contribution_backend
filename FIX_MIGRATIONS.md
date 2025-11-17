# Fix: Migrations Failing During Build

## Problem

The `release` command in `Procfile` tries to run migrations during build, but:
- Database isn't accessible during build phase
- MySQL service isn't available yet
- Internal network (`mysql.railway.internal`) can't be resolved

## Solution

**Removed `release` command from Procfile** - migrations should run manually after deployment.

## What to Do Now

### Step 1: Commit the Fix

```bash
git add Procfile
git commit -m "Remove release command - run migrations manually after deployment"
git push origin main
```

### Step 2: Wait for Deployment

Railway will automatically redeploy. The build should succeed now.

### Step 3: Run Migrations Manually

After deployment succeeds, run migrations using Railway Shell:

**Option A: Railway Dashboard Shell**
1. Go to your service → **"Deployments"** tab
2. Click latest deployment → **"Shell"** tab
3. Run:
   ```bash
   python manage.py migrate
   python manage.py seed_products
   ```

**Option B: Railway CLI**
```bash
railway run python manage.py migrate
railway run python manage.py seed_products
```

## Why This Happens

- **Build Phase**: Code is built, dependencies installed
- **Release Phase**: Runs after build, but database might not be ready
- **Runtime**: Database is fully accessible

Migrations need to run when database is accessible (runtime), not during build.

## Alternative: Conditional Release Command

If you want to keep release command, make it conditional:

```procfile
web: gunicorn Org_contributions_backend.wsgi:application --bind 0.0.0.0:$PORT
release: python -c "import os; exit(0 if not os.getenv('DATABASE_URL') else os.system('python manage.py migrate --noinput && python manage.py seed_products'))"
```

But **manual migration is recommended** for better control.

## Next Steps After Migrations

1. ✅ Run migrations: `python manage.py migrate`
2. ✅ Seed products: `python manage.py seed_products`
3. ✅ Create test users: `python manage.py create_test_users`
4. ✅ Test API endpoints

---

**The build will succeed now, then run migrations manually!** 🚀

