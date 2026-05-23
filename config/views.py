from django.http import HttpRequest, HttpResponse


def api_root(request: HttpRequest) -> HttpResponse:
    base = request.build_absolute_uri("/").rstrip("/")
    endpoints = [
        ("GET", "/", "This API overview page"),
        ("GET", "/admin/", "Django admin"),
        ("POST", "/api/v1/auth/register/", "Register a new user"),
        ("POST", "/api/v1/auth/login/", "Obtain JWT access & refresh tokens"),
        ("POST", "/api/v1/auth/refresh/", "Refresh access token"),
        ("GET", "/api/v1/auth/me/", "Current user profile (Bearer token)"),
        ("GET", "/api/v1/notifications/", "List your notifications (Bearer token)"),
        ("POST", "/api/v1/notifications/", "Create & schedule a notification (Bearer token)"),
        ("GET", "/api/v1/notifications/<id>/", "Notification detail (Bearer token)"),
        ("POST", "/api/v1/notifications/<id>/retry/", "Retry a failed notification (Bearer token)"),
    ]
    rows = "".join(
        f'<tr><td><span class="method {m.lower()}">{m}</span></td>'
        f'<td><a href="{base}{p}">{p}</a></td><td>{d}</td></tr>'
        for m, p, d in endpoints
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Notification System API</title>
  <style>
    :root {{ font-family: system-ui, sans-serif; color: #1a1a2e; background: #f4f6fb; }}
    body {{ max-width: 920px; margin: 2rem auto; padding: 0 1rem; }}
    h1 {{ font-size: 1.75rem; margin-bottom: 0.25rem; }}
    p.sub {{ color: #555; margin-top: 0; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px;
             box-shadow: 0 1px 4px rgba(0,0,0,.08); overflow: hidden; }}
    th, td {{ text-align: left; padding: 0.75rem 1rem; border-bottom: 1px solid #eee; }}
    th {{ background: #2d3a8c; color: #fff; font-weight: 600; }}
    tr:last-child td {{ border-bottom: none; }}
    a {{ color: #2d3a8c; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .method {{ font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.5rem;
               border-radius: 4px; text-transform: uppercase; }}
    .get {{ background: #e3f2fd; color: #1565c0; }}
    .post {{ background: #e8f5e9; color: #2e7d32; }}
    footer {{ margin-top: 1.5rem; font-size: 0.875rem; color: #666; }}
  </style>
</head>
<body>
  <h1>Background Job Notification System</h1>
  <p class="sub">REST API · JWT auth · Celery scheduled email delivery</p>
  <table>
    <thead><tr><th>Method</th><th>Endpoint</th><th>Description</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <footer>
    Protected routes need <code>Authorization: Bearer &lt;access_token&gt;</code>.
    Start with <strong>POST /api/v1/auth/register/</strong> then <strong>login</strong>.
  </footer>
</body>
</html>"""
    return HttpResponse(html)
