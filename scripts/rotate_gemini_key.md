# Rotate Gemini API Key and Secure Repository

Follow these steps to revoke the exposed key, scrub it from git history, and set a new secure key via environment variables.

## 1) Revoke the exposed key

1. Go to Google Cloud Console → APIs & Services → Credentials
2. Locate the exposed API key
3. Disable or delete it
4. Create a new key
5. Restrict the new key (API restrictions + optionally IP/HTTP referrers)

## 2) Scrub the old key from git history

Option A: Using git-filter-repo (recommended):

```bash
pip install git-filter-repo  # if needed
bash scripts/remove_exposed_key.sh "PASTE_EXPOSED_KEY_HERE"
git push --force
```

Option B: Using BFG Repo-Cleaner:

```bash
# Download BFG: https://rtyley.github.io/bfg-repo-cleaner/
echo "PASTE_EXPOSED_KEY_HERE" > keys.txt
java -jar bfg.jar --replace-text keys.txt
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

## 3) Set the new key securely

Local (create `.env` from `env.example`):

```bash
cp env.example .env
echo LLM_API_KEY=PASTE_NEW_GEMINI_KEY_HERE >> .env
```

Production (set platform environment variables):

- Railway/Render/Heroku → set `LLM_API_KEY`, `LLM_PROVIDER=gemini`, `LLM_MODEL=gemini-2.0-flash`

## 4) Verify

```bash
python -c "import os; print('LLM Key present:', bool(os.getenv('LLM_API_KEY')))"
```

Then run the app and test AI features.


