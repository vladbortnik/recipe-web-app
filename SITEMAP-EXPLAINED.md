# Sitemap.xml - Dynamic Generation

## Overview

The `sitemap.xml` file for this project is **dynamically generated** by Flask at runtime. There is no physical `sitemap.xml` file on disk.

When search engines or users access `https://recipe.vladbortnik.dev/sitemap.xml`, Flask executes Python code that builds and returns the XML content on-the-fly.

---

## File Location

| What | Where |
|------|-------|
| **Route definition** | `app/routes.py` (lines 671-732) |
| **URL served at** | `/sitemap.xml` |
| **Physical file** | ❌ None (dynamically generated) |

---

## How It Works

```python
# app/routes.py

@app.route('/sitemap.xml')
def sitemap_xml() -> 'flask.Response':
    from datetime import datetime

    # Define all public pages with SEO metadata
    pages = [
        {'loc': url_for('index', _external=True), 'priority': '1.0', 'changefreq': 'daily'},
        {'loc': url_for('login', _external=True), 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': url_for('signup', _external=True), 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': url_for('forgot_password', _external=True), 'priority': '0.5', 'changefreq': 'monthly'},
    ]

    # Generate XML following sitemap protocol
    sitemap_xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        sitemap_xml_content += '  <url>\n'
        sitemap_xml_content += f'    <loc>{page["loc"]}</loc>\n'
        sitemap_xml_content += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap_xml_content += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        sitemap_xml_content += f'    <priority>{page["priority"]}</priority>\n'
        sitemap_xml_content += '  </url>\n'

    sitemap_xml_content += '</urlset>'

    return Response(sitemap_xml_content, mimetype='application/xml')
```

---

## Example Output

When you visit `/sitemap.xml`, the response looks like:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://recipe.vladbortnik.dev/</loc>
    <lastmod>2025-12-01</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://recipe.vladbortnik.dev/login</loc>
    <lastmod>2025-12-01</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <!-- ... more pages ... -->
</urlset>
```

---

## Why Dynamic Generation?

| Benefit | Explanation |
|---------|-------------|
| **Always up-to-date** | `lastmod` reflects the current date automatically |
| **No maintenance** | No need to manually edit a file when routes change |
| **Correct URLs** | Uses Flask's `url_for()` to generate proper URLs based on environment |
| **Standard pattern** | Common approach for Flask/Django web applications |

---

## Related Files

- `app/static/robots.txt` - Static file that references the sitemap URL
- `app/routes.py` - Contains the sitemap generation code
- `app/templates/layout.html` - Contains SEO meta tags and structured data

---

## Testing

```bash
# Test locally
curl http://localhost:5002/sitemap.xml

# Test in production
curl https://recipe.vladbortnik.dev/sitemap.xml
```

---

## Adding New Pages

To add a new public page to the sitemap, edit `app/routes.py` and add an entry to the `pages` list:

```python
pages = [
    # ... existing pages ...
    {
        'loc': url_for('your_new_route', _external=True),
        'priority': '0.7',
        'changefreq': 'weekly'
    },
]
```

