# Render Deployment TODO
Status: In Progress

## Phase 1: Local Configuration ✅
- [x] Create TODO.md ✅
- [x] Update dashboard_project/settings.py for production ✅
- [x] Create Procfile ✅
- [x] Create runtime.txt ✅
- [x] Create .gitignore ✅

## Phase 2: Database Migration ✅
- [x] Backup SQLite data ✅ (run command)
- [x] `python manage.py check --deploy` passed (4 security warnings - Render/HTTPS) ✅
- [ ] Test Postgres config locally (optional)
- [ ] Migrate on Render

## Phase 3: Git & Deploy
- [ ] `git add . && git commit -m "Configure for Render deployment" && git push origin main` ✅
- [ ] 1. Go to render.com → Sign up/login
- [ ] 2. New → Web Service → Connect this GitHub repo
- [ ] 3. Build: `pip install -r requirements.txt`
- [ ] 4. Start: `gunicorn dashboard_project.wsgi:application`
- [ ] 5. Add Postgres service, link DB
- [ ] 6. Env vars: SECRET_KEY, DEBUG=False, EMAIL_*
- [ ] 7. Deploy → Visit URL, `python manage.py migrate`, loaddata data.json (admin)
- [ ] Verify dashboard, create superuser if needed

**Next Step: Data backup**


