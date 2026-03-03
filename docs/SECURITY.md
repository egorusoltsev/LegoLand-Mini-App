# Security incident response (March 2026)

## 1) Rotate leaked secrets immediately

The following secrets must be rotated now because they were committed in Git history:
- `TG_BOT_TOKEN` (rotate in BotFather)
- `DATABASE_URL` / DB password (rotate in Supabase)
- `SUPABASE_KEY` (`service_role`) (rotate in Supabase API settings)
- `JWT_SECRET`
- `ADMIN_KEY`

## 2) Reconfigure deployment secrets

### Railway (backend)
Project → **Variables**:
- `DATABASE_URL`
- `JWT_SECRET`
- `TG_BOT_TOKEN`
- `TG_CHAT_ID`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `ADMIN_KEY`
- `CORS_ORIGINS`

### Vercel (frontend)
Project → **Settings → Environment Variables**:
- `VITE_API_URL`
- `VITE_TG_BOT_USERNAME`
- `VITE_TELEGRAM_CONTACT_URL`

> Never put secrets into `VITE_*` variables except public URLs/usernames.

## 3) Remove secrets from git history

> Run from a clean clone. This rewrites history.

```bash
git filter-repo --path backend/.env --path frontend/.env --invert-paths
# Optional additional replacements by pattern:
# echo 'literal:OLD_SECRET==>REMOVED' > replacements.txt
# git filter-repo --replace-text replacements.txt

git push origin --force --all
git push origin --force --tags
```

Then invalidate old credentials and inform all collaborators to re-clone.
