# 🔑 OAuth Setup - Quick Reference

**Engineering Intelligence Hub - Google & GitHub Login**

---

## What You Need to Add to `.env`

```env
# Google OAuth (from https://console.cloud.google.com/apis/credentials)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret

# GitHub OAuth (from https://github.com/settings/developers)
GITHUB_CLIENT_ID=Iv1.your-github-client-id
GITHUB_CLIENT_SECRET=your-github-secret
```

Then restart: `docker compose restart backend`

---

## Google OAuth Setup

### 1. Create Credentials

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **Create Credentials** → **OAuth client ID**
3. **Application type**: Web application
4. **Authorized redirect URIs**:
   ```
   http://localhost:8000/api/v1/auth/google/callback
   ```
5. Copy **Client ID** and **Client Secret**

### 2. Configure Consent Screen (First Time)

1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. **User Type**: External
3. Fill in: App name, support email, developer contact
4. **Scopes**: Add `userinfo.email`, `userinfo.profile`, `openid`
5. **Test users**: Add your Gmail address
6. Save

---

## GitHub OAuth Setup

### 1. Create OAuth App

1. Go to: https://github.com/settings/developers
2. Click **OAuth Apps** → **New OAuth App**
3. Fill in:
   - Application name: `Engineering Intelligence Hub (Local)`
   - Homepage URL: `http://localhost:3000`
   - Callback URL: `http://localhost:8000/api/v1/auth/github/callback`
4. Click **Register application**
5. Click **Generate a new client secret**
6. Copy **Client ID** and **Client Secret**

---

## Testing

### Check OAuth Status

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/auth/oauth/providers
```

Expected: `{"google":true,"github":true}`

### Test Login

1. Go to: http://localhost:3000/login
2. Click "Continue with Google" or "Continue with GitHub"
3. Authorize and you're logged in! ✅

### Verify in Database

```powershell
docker compose exec postgres psql -U engineering_hub -d engineering_hub -c "SELECT id, email, oauth_provider FROM users WHERE oauth_provider IS NOT NULL;"
```

---

## Troubleshooting

### OAuth buttons don't appear
- Verify credentials in `.env` (not `.env.example`)
- Restart backend: `docker compose restart backend`

### "Redirect URI mismatch"
- Ensure redirect URI matches exactly (no trailing slash)
- Must be `http://` for localhost

### "Invalid OAuth state"
- Check `JWT_SECRET_KEY` is 32+ characters
- Clear browser cookies

---

## Production

⚠️ Create separate OAuth apps for production with HTTPS redirect URIs

---

**See TESTING.md for complete testing guide**

**Date**: 25 June 2026
