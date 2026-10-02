# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x   | ✅ |

## Reporting a Vulnerability

**Please do NOT open a public issue for security vulnerabilities.**

Instead, email **security@example.com** with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You should receive a response within **72 hours**. We will:

1. Confirm the vulnerability.
2. Work on a fix in a private branch.
3. Release a patch and credit you (unless you prefer anonymity).

## Security Best Practices

When deploying ResumeFilter:

- **Rotate secrets** — Change `SECRET_KEY` and `MASTER_KEY` before
  production.
- **Use HTTPS** — Never expose the API over plain HTTP.
- **Restrict CORS** — Set `CORS_ORIGINS` to your actual domains.
- **Isolate databases** — Use separate PostgreSQL instances per environment.
- **Enable backups** — Back up PostgreSQL and MinIO regularly.
- **Monitor logs** — Watch for suspicious `401`/`403` bursts.
- **Keep dependencies updated** — Enable Dependabot on your fork.

## Known Security Features

- **Row-Level Security** — Enforced at the PostgreSQL layer.
- **API key encryption** — Fernet-encrypted with `MASTER_KEY`.
- **Password hashing** — BCrypt with per-user salt.
- **JWT** — Short-lived, signed tokens.
- **Prompt injection defense** — Strict system prompts.
- **Non-root containers** — All Docker images run as `appuser`.

Thank you for helping keep ResumeFilter secure.