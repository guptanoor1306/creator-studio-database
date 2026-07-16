# Environment Variables & Security Setup

## Overview

For production use and automation, you should use environment variables instead of storing sensitive credentials in the UI or config files.

## Environment Variables

### Required for Automation

Set these environment variables for automated Slack notifications:

```bash
# Creator Studio Bearer Token
export CS_BEARER_TOKEN="your_bearer_token_here"

# Slack Webhook URL
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Setting Environment Variables

#### Local Development (Mac/Linux)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
export CS_BEARER_TOKEN="your_token"
export SLACK_WEBHOOK_URL="your_webhook_url"
```

Then reload:
```bash
source ~/.zshrc
```

#### Railway Deployment

1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add:
   - `CS_BEARER_TOKEN` = your bearer token
   - `SLACK_WEBHOOK_URL` = your webhook URL

#### Docker

```dockerfile
docker run -e CS_BEARER_TOKEN="your_token" \
           -e SLACK_WEBHOOK_URL="your_webhook" \
           your-image
```

Or use a `.env` file (add to `.gitignore`!):

```bash
CS_BEARER_TOKEN=your_token
SLACK_WEBHOOK_URL=your_webhook
```

## Credential Priority

The app checks credentials in this order:

1. **Environment Variables** (highest priority)
   - `CS_BEARER_TOKEN`
   - `SLACK_WEBHOOK_URL`

2. **Config File** (fallback)
   - `scheduler_config.json` (stored locally)

3. **UI Input** (manual operations only)

## Bearer Token Expiration

### The Problem

Bearer tokens typically expire after a certain period (often 24 hours to 30 days depending on the API).

### Solutions

#### Option 1: Manual Refresh (Current)

When your token expires:

1. Get a new token from Creator Studio:
   - Open Creator Studio
   - Open DevTools (F12) → Network tab
   - Find any API request
   - Copy the `Authorization: Bearer ...` header

2. Update the environment variable:
   ```bash
   export CS_BEARER_TOKEN="new_token"
   ```

3. Restart the server

#### Option 2: Refresh Token (Recommended for Production)

If Creator Studio provides refresh tokens, implement automatic token refresh:

```python
# Pseudo-code for future implementation
def refresh_bearer_token(refresh_token):
    response = requests.post(
        "https://confucius.zero1creatorstudio.com/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    new_token = response.json()['access_token']
    return new_token
```

Store the refresh token in environment variables:
```bash
export CS_REFRESH_TOKEN="your_refresh_token"
```

#### Option 3: OAuth Flow (Best for Multi-User)

For a production multi-user application:

1. Implement OAuth 2.0 authentication
2. Store encrypted tokens per user in a database
3. Automatically refresh tokens when they expire
4. Notify users when manual re-authentication is needed

### Monitoring Token Expiration

The app will log errors when the token expires:

```
❌ 401 Unauthorized - Bearer token may have expired
```

Set up monitoring (e.g., Railway logs, Sentry) to alert you when this happens.

## Security Best Practices

### 1. Never Commit Credentials

Add to `.gitignore`:
```
scheduler_config.json
.env
*.pem
*.key
```

### 2. Use Environment Variables in Production

Always use environment variables for:
- Railway deployment
- Docker containers
- Any production environment

### 3. Rotate Tokens Regularly

- Change bearer tokens periodically
- Update Slack webhook URLs if compromised
- Use different tokens for dev/staging/production

### 4. Limit Token Permissions

If possible, create tokens with minimal required permissions:
- Read-only access to channel data
- No write/delete permissions

### 5. Monitor Access Logs

Check Railway/server logs regularly for:
- Unauthorized access attempts
- Unusual API usage patterns
- Failed authentication attempts

## Automation Setup Checklist

For production automated Slack notifications:

- [ ] Set `CS_BEARER_TOKEN` environment variable
- [ ] Set `SLACK_WEBHOOK_URL` environment variable
- [ ] Configure scheduler in UI (category, thresholds, interval)
- [ ] Enable automation in Slack Notifications tab
- [ ] Test manual notification first
- [ ] Monitor logs for first automated run
- [ ] Set up alerting for token expiration
- [ ] Document token refresh procedure for your team
- [ ] Add calendar reminder to refresh token before expiration

## Troubleshooting

### "Missing bearer token or webhook URL"

**Cause**: Environment variables not set or scheduler config not saved.

**Fix**:
```bash
# Check if variables are set
echo $CS_BEARER_TOKEN
echo $SLACK_WEBHOOK_URL

# If empty, set them
export CS_BEARER_TOKEN="your_token"
export SLACK_WEBHOOK_URL="your_webhook"

# Restart server
```

### "401 Unauthorized"

**Cause**: Bearer token expired.

**Fix**: Get a new token and update environment variable.

### "403 Forbidden" or Proxy Errors

**Cause**: Network/proxy blocking requests.

**Fix**: 
- App will continue without categories
- Check network/proxy settings
- Try from different network
- Contact IT if behind corporate proxy

## Example Production Setup

### Railway with GitHub Actions

1. Set secrets in GitHub repository
2. Add to `.github/workflows/deploy.yml`:

```yaml
env:
  CS_BEARER_TOKEN: ${{ secrets.CS_BEARER_TOKEN }}
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

3. Railway will automatically use these variables

### Docker Compose

```yaml
version: '3.8'
services:
  csdb:
    build: .
    environment:
      - CS_BEARER_TOKEN=${CS_BEARER_TOKEN}
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
      - PORT=8080
    ports:
      - "8080:8080"
```

Run with:
```bash
docker-compose up -d
```

## Questions?

- **Q: How often do tokens expire?**
  - A: Depends on Creator Studio's API. Check their documentation or test by monitoring when you get 401 errors.

- **Q: Can I use different tokens for different users?**
  - A: Currently, the automation uses a single token. For multi-user, you'd need to implement user authentication and per-user token storage.

- **Q: What happens if Slack webhook changes?**
  - A: Update the `SLACK_WEBHOOK_URL` environment variable and restart. No code changes needed.

- **Q: Can I schedule different notifications with different settings?**
  - A: Currently, only one scheduled notification is supported. You could run multiple instances with different configs on different ports.
