# Recipe Hub — Application Workflow (A to Z)

This document describes how the Recipe Hub application works end-to-end: from Docker container startup through every user-facing feature.

---

## 1. Infrastructure & Startup

### 1.1 Docker Compose (`compose.yaml`)

Two active services:

```
┌─────────────────────────────────────────────────────┐
│                   compose.yaml                      │
│                                                     │
│  ┌──────────┐         ┌──────────┐                  │
│  │   web1   │────────►│    db    │                  │
│  │ (Flask)  │depends  │(Postgres │                  │
│  │ :5002    │  on     │  16.4)   │                  │
│  └──────────┘         │ :5432    │                  │
│                       └──────────┘                  │
│                                                     │
│  Volume: postgres_data (persistent DB storage)      │
│  Volume: .:/code (host bind-mount for live code)    │
└─────────────────────────────────────────────────────┘
```

- **`db`** — PostgreSQL 16.4. Reads DB credentials from `.env` (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`). Data persisted via named volume `postgres_data`.
- **`web1`** — Built from the `Dockerfile`. Depends on `db`. Runs Gunicorn with 4 workers on port 5002. Host directory bind-mounted to `/code` (overrides the Dockerfile's `COPY . /code/`).

### 1.2 Dockerfile

```
Base image: python:3.12.5-slim
  │
  ├── Install system packages: apt-utils, netcat-openbsd, postgresql-client
  ├── WORKDIR /code
  ├── COPY . /code/
  ├── pip install -r requirements.txt
  ├── chmod +x /code/scripts/entrypoint.sh
  ├── EXPOSE 5002  (documentation only)
  └── ENTRYPOINT ["/code/scripts/entrypoint.sh"]
```

### 1.3 Entrypoint (`scripts/entrypoint.sh`)

This script runs **before** the Gunicorn command (passed as `"$@"` from compose):

```
entrypoint.sh
  │
  ├── 1. Wait for PostgreSQL (nc -z $DB_HOST $DB_PORT)
  ├── 2. flask db init         (only if /migrations dir doesn't exist)
  ├── 3. flask db migrate      (create migration if model changes detected)
  ├── 4. flask db upgrade head (apply all pending migrations)
  └── 5. exec "$@"             → exec gunicorn -w 4 -b 0.0.0.0:5002 run:app
```

### 1.4 Application Bootstrap (`run.py` → `app/__init__.py`)

```
run.py
  │
  ├── from app import create_app, db
  ├── app = create_app()
  │     │
  │     └── create_app()  [app/__init__.py]
  │           │
  │           ├── Load .env via python-dotenv
  │           ├── Create Flask app
  │           ├── Load config from app.config.Config
  │           ├── Initialize extensions:
  │           │     ├── SQLAlchemy (db)
  │           │     ├── Flask-Migrate (migrate)
  │           │     ├── Flask-Bcrypt (bcrypt)
  │           │     ├── Flask-Login (login_manager)
  │           │     ├── Flask-Mail (mail)
  │           │     └── Flask-Limiter (limiter, key=remote_address)
  │           ├── Set login_manager.login_view = "login"
  │           ├── Register context_processor → inject csrf_token
  │           ├── Register user_loader → User.query.get(user_id)
  │           ├── Import routes (registers all @app.route decorators)
  │           └── Print URL map (debug)
  │
  ├── with app.app_context():
  │     ├── Import models: User, ImgSet, Recipe, Favorite
  │     └── db.create_all()  (creates tables if they don't exist)
  │
  └── app.run(host='0.0.0.0', port=5002, debug=app.config['DEBUG'])
      (only used when running directly; Gunicorn bypasses __main__)
```

**Note:** When run via Gunicorn (`gunicorn run:app`), the module-level code in `run.py` executes (including `create_app()` and `db.create_all()`), but `app.run()` inside `if __name__ == "__main__"` does NOT execute.

---

## 2. Configuration (`app/config.py`)

All config is read from environment variables (`.env` file):

| Category | Key Settings |
|---|---|
| **Flask** | `FLASK_APP`, `FLASK_ENV`, `FLASK_DEBUG`, `SECRET_KEY` |
| **Database** | `DATABASE_URL` (postgresql://user:pass@db:5432/recipe_db) |
| **File Paths** | `UPLOAD_FOLDER` (app/static/upload_dir), `WHITELIST_FILE` (app/static/whitelist.txt) |
| **Azure Vision** | `AZURE_COMPUTERVISION_ENDPOINT`, `AZURE_COMPUTERVISION_KEY` |
| **Spoonacular** | `SPOONACULAR_API_KEY` |
| **Mail (Fastmail)** | `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER` |
| **reCAPTCHA v2** | `RECAPTCHA_SITE_KEY`, `RECAPTCHA_SECRET_KEY` |
| **Google OAuth** | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` |

**Hardcoded security settings** (not env-driven):
- `SESSION_COOKIE_SECURE = True`
- `SESSION_COOKIE_HTTPONLY = True`
- `REMEMBER_COOKIE_SECURE = True`
- `WTF_CSRF_SSL_STRICT = True`
- `SESSION_COOKIE_SAMESITE = 'Lax'`

---

## 3. Database Models (`app/models.py`)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User      │     │   ImgSet     │     │   Recipe     │     │  Favorite   │
│  (users)     │     │  (imgsets)   │     │  (recipes)   │     │ (favorites) │
├─────────────┤     ├─────────────┤     ├─────────────┤     ├─────────────┤
│ id (PK)      │◄────│ user_id (FK) │     │ id (PK)      │     │ id (PK)     │
│ email        │     │ id (PK)      │     │ spoonacular  │◄────│ spoonacular │
│ password     │     │ folder_path  │     │   _id (UQ)   │     │   _id (FK)  │
│ google_id    │     │ products     │     │ recipe_data  │     │ user_id(FK) │
│ auth_provider│     │ upload_date  │     │   (JSON)     │     │             │
│ is_verified  │     └─────────────┘     │ date_created │     └─────────────┘
│ verification │                          └─────────────┘           │
│   _token     │                                                     │
│ token_       │◄────────────────────────────────────────────────────┘
│   expiration │     (user_id FK)
│ date_created │
└─────────────┘

Constraints:
  - Favorite has UniqueConstraint(user_id, spoonacular_id)
  - User.email is unique
  - User.google_id is unique (nullable)
  - Recipe.spoonacular_id is unique
```

**Relationships:**
- `User` ←1:N→ `ImgSet` (user.imgsets)
- `User` ←1:N→ `Favorite` (user.favorites)
- `Recipe` ←1:N→ `Favorite` (recipe.favorited_by), joined on `spoonacular_id`

---

## 4. Templates & Layout

### 4.1 Template Hierarchy

```
layout.html  (base template)
  │
  ├── Includes: google-analytics.html (Google Analytics + Consent Mode v2)
  │
  ├── CDN Dependencies:
  │     ├── Bootstrap 5.3.3 (CSS + JS)
  │     ├── Font Awesome 6.4.0
  │     ├── Google Fonts (Nunito)
  │     ├── AOS animation library 2.3.1
  │     ├── Cookie Consent 3.x
  │     └── Umami Analytics
  │
  ├── Fixed-top navbar with:
  │     ├── Brand: "Recipe Hub"
  │     ├── Links: Dashboard, Upload
  │     └── Auth: My Account + Logout (logged in) OR Login + Sign Up (anonymous)
  │
  ├── Flash messages area (Bootstrap alerts with icons)
  │
  ├── {% block content %} (page-specific content)
  │
  ├── Footer
  │
  └── {% block scripts %} (page-specific JS)

Child templates:
  ├── index.html         — Landing page (different views for auth/anon users)
  ├── login.html         — Login form + Google OAuth + reCAPTCHA v2
  ├── signup.html        — Registration form + Google OAuth + reCAPTCHA v2
  ├── dashboard.html     — Products grid + recipes list + favorites toggle
  ├── upload.html        — Drag-and-drop image upload with preview
  ├── my-account.html    — Account overview + password reset request
  ├── forgot-password.html  — Forgot password form / success state
  ├── password-reset.html   — New password form + reCAPTCHA v2
  └── logout.html        — Empty (logout is a redirect, this template is unused)
```

---

## 5. Routes & Application Flow (`app/routes.py`)

### 5.1 Public Routes (no auth required)

```
GET  /                      → index()           → index.html (hero for anon, welcome for auth)
GET  /health                → health()           → JSON {"status": "healthy"}
GET  /robots.txt            → robots_txt()       → static/robots.txt
GET  /sitemap.xml           → sitemap_xml()      → Dynamic XML sitemap (public pages only)
```

### 5.2 Authentication Routes

```
┌──────────────────────────────────────────────────────────────────────┐
│                     LOCAL AUTHENTICATION FLOW                        │
│                                                                      │
│  ┌─────────┐   POST    ┌───────────┐   verify    ┌──────────┐       │
│  │ /signup  │─────────► │ Create    │───email────►│ /verify- │       │
│  │ (form +  │  validate │ User      │  (token)    │ email/   │       │
│  │ reCAPTCHA│  reCAPTCHA│ (unverif) │             │ <token>  │       │
│  └─────────┘           └───────────┘             └────┬─────┘       │
│                                                        │ mark       │
│  ┌─────────┐   POST    ┌───────────┐                  │ verified   │
│  │ /login   │─────────► │ Check     │◄─────────────────┘            │
│  │ (form +  │  validate │ creds +   │                                │
│  │ reCAPTCHA│  reCAPTCHA│ verified? │──── yes ───► login_user()     │
│  └─────────┘           └───────────┘              redirect to /     │
│                              │ no (unverified)                       │
│                              └──► show "resend verification" link    │
│                                                                      │
│  GET /resend-verification/<user_id>  → resend verification email     │
│  GET /logout                         → logout_user() → redirect /    │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                     GOOGLE OAUTH FLOW                                │
│                                                                      │
│  GET /auth/google                                                    │
│    └── Redirect to Google OAuth consent page                         │
│                                                                      │
│  GET /auth/google/callback                                           │
│    ├── Exchange auth code for token + user info                      │
│    ├── If google_id exists → log in existing user                    │
│    ├── If email exists (local) → link Google account, log in         │
│    └── Otherwise → create new User(auth_provider='google'), log in   │
│                                                                      │
│  All Google users are auto-verified (is_verified=True)               │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                     PASSWORD RESET FLOW                               │
│                                                                      │
│  GET/POST /forgot-password                                           │
│    └── Send reset email with token (URLSafeTimedSerializer,          │
│        salt='password-reset-salt', 1h expiry)                        │
│                                                                      │
│  GET/POST /password-reset/<token>                                    │
│    ├── Validate token (max_age=3600)                                 │
│    ├── Validate reCAPTCHA                                            │
│    └── Update user.password hash → redirect /login                   │
│                                                                      │
│  POST /send-password-reset  (from My Account, logged-in users)       │
│    └── Same as forgot-password but for current_user                  │
└──────────────────────────────────────────────────────────────────────┘
```

**Rate limiting** (Flask-Limiter):
- `/login` — 5 per minute
- `/signup` — 5 per minute
- `/forgot-password` — 5 per minute
- `/send-password-reset` — 3 per minute
- `/password-reset/<token>` — 3 per minute

### 5.3 Core Feature Routes (login required)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      UPLOAD → DASHBOARD FLOW                             │
│                                                                          │
│  GET /upload                                                             │
│    └── Show drag-and-drop upload form (upload.html)                      │
│                                                                          │
│  POST /upload                                                            │
│    ├── Validate form (images: jpg/jpeg/png only)                         │
│    ├── Create unique folder: UPLOAD_FOLDER/<user_id>/<uuid4>/            │
│    ├── Save uploaded files with UUID-prefixed filenames                   │
│    ├── Create ImgSet record in DB (user_id, folder_path)                 │
│    ├── Call Azure Vision API via retrieve_product_labels()                │
│    │     ├── For each image: client.tag_image_in_stream()                │
│    │     ├── Filter: single-word tags only                               │
│    │     ├── Filter: against whitelist.txt (99 grocery items)            │
│    │     └── Save filtered products as CSV in ImgSet.products            │
│    ├── If no products recognized → flash warning, redirect /upload       │
│    └── Store products in session → redirect /dashboard                   │
│                                                                          │
│  GET /dashboard                                                          │
│    ├── CASE 1 (redirected from /upload):                                 │
│    │     └── Pop session['products'] → call Spoonacular API              │
│    ├── CASE 2 (direct visit, no session data):                           │
│    │     ├── fetch_user_products() → all products from user's ImgSets    │
│    │     └── fetch_all_recipes() → all Recipe entries from DB            │
│    ├── Mark recipes that are in user's favorites                         │
│    └── Render dashboard.html (products grid + recipe cards)              │
│                                                                          │
│  POST /dashboard                                                         │
│    ├── Get selected products from checkbox form                          │
│    ├── Call retrieve_recipes_by_ingredients(products)                     │
│    │     ├── Spoonacular: findByIngredients (5 recipes max)              │
│    │     ├── For each: get detailed info (instructions, servings, etc.)  │
│    │     └── Store/update Recipe entries in DB                           │
│    └── Render dashboard.html with matching recipes                       │
└──────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Favorites System

```
┌──────────────────────────────────────────────────────────────────────┐
│                        FAVORITES FLOW                                │
│                                                                      │
│  POST /toggle-favorite (AJAX, JSON)                                  │
│    ├── Input: { spoonacular_id, recipe_data }                        │
│    ├── If NOT favorited:                                             │
│    │     ├── Find or create Recipe entry                             │
│    │     ├── Create Favorite(user_id, spoonacular_id)                │
│    │     └── Return { action: "added", favorites_count }             │
│    └── If already favorited:                                         │
│          ├── Delete Favorite entry                                   │
│          └── Return { action: "removed", favorites_count }           │
│                                                                      │
│  GET /get-favorites (AJAX, JSON)                                     │
│    └── Return { favorite_spoonacular_ids: [...], favorites_count }   │
│                                                                      │
│  GET /favorites                                                      │
│    ├── Query all Favorite entries for current_user                   │
│    ├── Load matching Recipe entries from DB                          │
│    └── Render dashboard.html with show_favorites=True                │
│                                                                      │
│  Client-side (dashboard.html JS):                                    │
│    ├── Bookmark icon toggle (far ↔ fas, outline ↔ danger)            │
│    ├── "Show Favorites" button filters recipe list client-side       │
│    ├── Toast notifications for add/remove feedback                   │
│    └── On /favorites page: auto-hides non-favorite recipe cards      │
└──────────────────────────────────────────────────────────────────────┘
```

### 5.5 Account Management

```
GET /my-account  (login required)
  └── Show email, account creation date, password reset button
      └── POST /send-password-reset → sends reset email to current_user
```

---

## 6. Utility Functions (`app/utils.py`)

| Function | Purpose |
|---|---|
| `load_whitelist()` | Reads `whitelist.txt` → set of 99 grocery item names |
| `retrieve_product_labels(path)` | Azure Vision API: tag images → filter against whitelist → save to DB |
| `retrieve_recipes_by_ingredients(products)` | Spoonacular API: find recipes by ingredients + get detailed info → save to DB |
| `fetch_user_products()` | Get all unique products from current user's ImgSets |
| `fetch_all_recipes()` | Get all Recipe entries from DB |
| `generate_verification_token(email)` | `URLSafeTimedSerializer.dumps(email, salt=SECRET_KEY)` |
| `verify_token(token, expiration)` | `URLSafeTimedSerializer.loads(token, salt=SECRET_KEY, max_age)` |
| `calculate_token_expiry(hours)` | Returns `datetime.now() + timedelta(hours)` |
| `verify_recaptcha(response)` | POST to Google reCAPTCHA verify URL → returns bool |
| `send_verification_email(user)` | Generates token, stores in user record, sends email via Flask-Mail |
| `reset_password(user)` | Generates token (salt='password-reset-salt'), sends reset email |

---

## 7. External API Integrations

### 7.1 Azure Computer Vision API
- **Used in:** `retrieve_product_labels()`
- **Flow:** Upload image as binary stream → `tag_image_in_stream()` → returns tags
- **Filtering:** Only single-word tags AND present in `whitelist.txt` are kept
- **Output:** List of product names saved as CSV in `ImgSet.products`

### 7.2 Spoonacular API
- **Used in:** `retrieve_recipes_by_ingredients()`
- **Flow:**
  1. `findByIngredients?ingredients=...&number=5` → basic recipe list
  2. For each recipe: `recipes/{id}/information` → detailed info
- **Output:** Enriched recipe dicts stored in `Recipe.recipe_data` (JSON)

### 7.3 Google OAuth (Authlib)
- **Used in:** `/auth/google`, `/auth/google/callback`
- **Provider:** Google OpenID Connect
- **Scope:** `openid email profile`
- **Redirect URI:** `http://localhost:5002/auth/google/callback` (dev) or `https://recipe.vladbortnik.dev/auth/google/callback` (prod)

### 7.4 Google reCAPTCHA v2
- **Used on:** Login, Signup, Password Reset forms
- **Verification:** Server-side POST to `https://www.google.com/recaptcha/api/siteverify`

---

## 8. Email System (Flask-Mail)

- **Provider:** Fastmail (smtp.fastmail.com:587, TLS)
- **Sender:** no-reply@vladbortnik.dev
- **Emails sent:**
  1. **Verification email** — on signup, contains `/verify-email/<token>` link (24h expiry)
  2. **Password reset email** — on forgot-password or my-account request, contains `/password-reset/<token>` link (1h expiry)

---

## 9. Security Features

| Feature | Implementation |
|---|---|
| **Password hashing** | Flask-Bcrypt (bcrypt) |
| **CSRF protection** | Flask-WTF (auto token injection via context_processor) |
| **Rate limiting** | Flask-Limiter (by remote_address) |
| **reCAPTCHA v2** | On login, signup, password reset forms |
| **Session cookies** | Secure, HttpOnly, SameSite=Lax (hardcoded) |
| **Token-based verification** | itsdangerous URLSafeTimedSerializer |
| **OAuth** | Authlib (Google) |

---

## 10. Static Assets & SEO

### Static Files
- `main.css` — Full custom CSS (CSS variables, responsive, animations)
- `favicon.ico` — Site favicon
- `robots.txt` — Search engine directives
- `whitelist.txt` — 99 grocery item names for Azure Vision filtering
- `upload_dir/` — User-uploaded images (gitignored, **currently missing**)

### SEO
- Meta tags (description, keywords, Open Graph, Twitter Cards)
- Structured data (JSON-LD WebApplication schema)
- Dynamic `sitemap.xml` (public pages: /, /login, /signup, /forgot-password)
- Canonical URLs

### Analytics
- **Google Analytics** (G-LLKG1K4C9Y) with Consent Mode v2
- **Umami Analytics** (self-hosted at analytics.vladbortnik.dev)
- **Cookie consent** banner (opt-in, EU/GDPR compliant)

---

## 11. Complete Request Lifecycle (Example: Image Upload → Recipe Discovery)

```
User clicks "Upload" in navbar
  │
  ▼
GET /upload → @login_required → upload.html (drag & drop form)
  │
  ▼
User selects images, clicks "Upload"
  │
  ▼
POST /upload
  ├── Flask-WTF validates form + CSRF token
  ├── Create folder: app/static/upload_dir/<user_id>/<uuid>/
  ├── Save each file: <uuid>_<original_name>.jpg
  ├── INSERT INTO imgsets (user_id, folder_path)
  ├── For each image file:
  │     └── Azure Vision API: tag_image_in_stream(file)
  │           └── Returns tags like: ["tomato", "food", "red", "vegetable"]
  ├── Filter tags: single-word only + in whitelist.txt
  │     └── Result: ["tomato"]
  ├── UPDATE imgsets SET products = "tomato" WHERE id = ...
  ├── session['products'] = ["tomato"]
  └── redirect /dashboard
        │
        ▼
GET /dashboard
  ├── products = session.pop('products') → ["tomato"]
  ├── Spoonacular API: findByIngredients?ingredients=tomato&number=5
  │     └── Returns 5 recipes that use tomato
  ├── For each recipe:
  │     └── Spoonacular API: recipes/{id}/information
  │           └── Returns full details (instructions, servings, etc.)
  ├── Store recipes in DB (Recipe table, keyed by spoonacular_id)
  ├── Check user's favorites → mark matching recipes
  └── Render dashboard.html
        ├── Products section: checkboxes for "tomato"
        ├── Recipes section: 5 recipe cards with:
        │     ├── Title, image, cook time, difficulty, servings
        │     ├── "View Details" collapse (summary, instructions)
        │     ├── Used ingredients vs. missing ingredients
        │     ├── Source link
        │     └── Favorite bookmark button
        └── "Show Favorites" filter button
```
