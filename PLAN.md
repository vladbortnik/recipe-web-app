# Recipe Hub — Local Development Fix Plan

This file tracks all fixes and improvements needed to run the application locally over HTTP (`http://localhost:5002`).

---

## Blockers (App Won't Work Locally Without These)

- [ ] **1. Create missing `app/static/upload_dir/` directory**
  - The `.env` sets `UPLOAD_FOLDER=app/static/upload_dir` but this directory does not exist on disk.
  - The upload route calls `os.makedirs(folder_path, exist_ok=True)` which creates subdirectories, but the base `upload_dir/` must exist (or the path must be valid) for the feature to work.
  - **Fix:** Create the directory. Add a `.gitkeep` file so Git tracks the empty directory (it's already gitignored via `/app/static/upload_dir/` in `.gitignore`, but `.gitkeep` ensures the folder structure is preserved).

- [ ] **2. Make `SESSION_COOKIE_SECURE` conditional on DEBUG mode**
  - Currently hardcoded to `True` in `app/config.py` (lines 18 and 25 — also a duplicate).
  - When `True`, browsers refuse to send session cookies over plain HTTP.
  - This completely breaks login/sessions on `http://localhost:5002`.
  - **Fix:** Set `SESSION_COOKIE_SECURE = not DEBUG` in `app/config.py` so it's `False` in development (`FLASK_DEBUG=True`) and `True` in production.
  - **Also:** Remove the duplicate `SESSION_COOKIE_SECURE = True` on line 25.

- [ ] **3. Make `REMEMBER_COOKIE_SECURE` conditional on DEBUG mode**
  - Currently hardcoded to `True` in `app/config.py` (line 21).
  - The "Remember me" checkbox on the login form sets a persistent cookie. With `Secure=True`, this cookie is not sent over HTTP.
  - **Fix:** Set `REMEMBER_COOKIE_SECURE = not DEBUG` in `app/config.py`.

- [ ] **4. Make `WTF_CSRF_SSL_STRICT` conditional on DEBUG mode**
  - Currently hardcoded to `True` in `app/config.py` (line 24).
  - When `True`, Flask-WTF enforces that the CSRF referer header matches an HTTPS origin. All form submissions (login, signup, upload, password reset, etc.) will return 400 errors over HTTP.
  - **Fix:** Set `WTF_CSRF_SSL_STRICT = not DEBUG` in `app/config.py`.

---

## Bugs (App Has Incorrect Behavior)

- [ ] **5. Fix `my-account.html` — HTML outside `{% endblock %}`**
  - Lines 57-61 contain a "View My Favorite Recipes" button that is placed AFTER `{% endblock %}` on line 55.
  - This HTML renders outside the layout's `{% block content %}`, meaning it appears after the closing `</html>` tag from `layout.html`.
  - Most browsers still render it, but it's invalid HTML and the button appears unstyled/misplaced (outside the `<main>` container, after the footer).
  - **Fix:** Move the "View My Favorite Recipes" button inside `{% endblock %}`, within the card body alongside the existing "Back to Dashboard" button.

---

## Security Improvements (Not Blockers, But Should Be Addressed)

- [ ] **6. Add CSRF token to `/toggle-favorite` AJAX requests**
  - The `fetch('/toggle-favorite', ...)` call in `dashboard.html` sends a JSON body but does NOT include a CSRF token header.
  - `CSRFProtect` is NOT initialized app-wide in `app/__init__.py` — only per-form via `FlaskForm.hidden_tag()`.
  - This means the `/toggle-favorite` endpoint has no CSRF protection, making it vulnerable to cross-site request forgery.
  - **Fix:** Either initialize `CSRFProtect(app)` app-wide and pass the CSRF token in the `X-CSRFToken` header for AJAX requests, or add a per-request CSRF check in the route.
