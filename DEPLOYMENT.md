# GCP Deployment Guide

This guide covers deploying the Campus Resource Hub application to Google Cloud Platform.

## Prerequisites

1. **Google Cloud SDK** installed and configured
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **PostgreSQL Database** (Supabase) - Already configured
   - Connection URL: `postgresql://postgres:rpLvgOls4fFSUKb3@db.hjhqgmkltsfscgfehipf.supabase.co:5432/postgres`

3. **Environment Variables** to set:
   - `SECRET_KEY` - Flask secret key (generate a secure random string)
   - `DATABASE_URL` - PostgreSQL connection string
   - `LLM_API_KEY` - Your LLM API key (Gemini, OpenAI, etc.)
   - `LLM_PROVIDER` - LLM provider (default: `gemini`)
   - `LLM_MODEL` - LLM model name (default: `gemini-2.0-flash`)

## Deployment Options

### Option 1: Google App Engine (Recommended for Simplicity)

App Engine is a fully managed platform that handles scaling automatically.

#### Steps:

1. **Set environment variables in GCP Console:**
   - Go to App Engine → Settings → Environment Variables
   - Add:
     - `SECRET_KEY`: Your Flask secret key
     - `DATABASE_URL`: `postgresql://postgres:rpLvgOls4fFSUKb3@db.hjhqgmkltsfscgfehipf.supabase.co:5432/postgres`
     - `LLM_API_KEY`: Your API key
     - `LLM_PROVIDER`: `gemini` (or your preferred provider)
     - `LLM_MODEL`: `gemini-2.0-flash` (or your preferred model)

2. **Deploy:**
   ```bash
   gcloud app deploy app.yaml
   ```

3. **View your app:**
   ```bash
   gcloud app browse
   ```

**Note:** The `app.yaml` file already includes the DATABASE_URL, but you should set it as an environment variable in GCP Console for security (remove it from app.yaml if you do this).

### Option 2: Cloud Run (Recommended for Flexibility)

Cloud Run is a serverless container platform that scales to zero when not in use.

#### Steps:

1. **Build and push the container:**
   ```bash
   # Set your project ID
   export PROJECT_ID=your-project-id
   
   # Build the image
   gcloud builds submit --tag gcr.io/$PROJECT_ID/campus-resource-hub
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy campus-resource-hub \
     --image gcr.io/$PROJECT_ID/campus-resource-hub \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars DATABASE_URL="postgresql://postgres:rpLvgOls4fFSUKb3@db.hjhqgmkltsfscgfehipf.supabase.co:5432/postgres",SECRET_KEY="your-secret-key",LLM_API_KEY="your-api-key",LLM_PROVIDER="gemini",LLM_MODEL="gemini-2.0-flash" \
     --memory 512Mi \
     --cpu 1 \
     --timeout 300 \
     --max-instances 10
   ```

3. **Or use the Cloud Build configuration:**
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

### Option 3: Using Cloud Build (Automated CI/CD)

1. **Set up Cloud Build trigger** (optional):
   - Connect your repository to Cloud Build
   - Create a trigger that runs on push to main branch
   - The `cloudbuild.yaml` file will handle the build and deployment

2. **Manual build:**
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

## Post-Deployment

1. **Verify the deployment:**
   - Check the health endpoint: `https://your-app-url/health`
   - Should return: `{"status": "healthy"}`

2. **Initialize the database:**
   - The application will automatically create tables on first run
   - Admin user will be seeded: `admin@campushub.local` / `Password1`

3. **Monitor logs:**
   ```bash
   # App Engine
   gcloud app logs tail -s default
   
   # Cloud Run
   gcloud run services logs read campus-resource-hub
   ```

## Troubleshooting

### Database Connection Issues

- Verify the DATABASE_URL is correct
- Check that your Supabase database allows connections from GCP IPs
- Ensure the database is not paused (Supabase free tier pauses after inactivity)

### Application Errors

- Check logs: `gcloud app logs tail` or Cloud Run logs
- Verify all environment variables are set correctly
- Ensure `gunicorn` is in requirements.txt (already included)

### Static Files Not Loading

- Verify the `src/static` directory structure
- Check that static files are being served correctly
- For Cloud Run, ensure the Dockerfile copies all static files

## Security Notes

1. **Never commit secrets** to version control
2. **Use GCP Secret Manager** for sensitive data in production:
   ```bash
   # Create a secret
   echo -n "your-secret-key" | gcloud secrets create flask-secret-key --data-file=-
   
   # Use in Cloud Run
   gcloud run services update campus-resource-hub \
     --update-secrets SECRET_KEY=flask-secret-key:latest
   ```

3. **Update the admin password** after first deployment
4. **Enable HTTPS** (automatic with App Engine and Cloud Run)

## Scaling

- **App Engine**: Automatically scales based on traffic
- **Cloud Run**: 
  - Min instances: 0 (scales to zero)
  - Max instances: Set based on expected load
  - CPU allocation: Can be set to "CPU always allocated" for faster cold starts

## Cost Optimization

- Use Cloud Run for lower costs (pay per request)
- App Engine has a free tier but may incur costs at scale
- Monitor usage in GCP Console → Billing

