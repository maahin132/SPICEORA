# Database

## Local development

The application targets MySQL 8.0 and uses the `utf8mb4` character set and collation. Django connection settings are read from the root `.env`:

| Variable | Purpose |
|---|---|
| `DB_NAME` | Application schema (`spiceora_db`) |
| `DB_USER` | Least-privilege application login (`spiceora_app`) |
| `DB_PASSWORD` | Local-only application password |
| `DB_HOST` | MySQL host (normally `127.0.0.1`) |
| `DB_PORT` | MySQL port (normally `3306`) |

Use a separate administrative MySQL account to create the schema and grant the application account access only to `spiceora_db`. Do not modify unrelated schemas. The bootstrap process never targets or modifies `woodhub_db`.

Run `python manage.py migrate` in `backend/` to apply Django's initial migrations. Verify the connection with `python manage.py check --database default`.

## Backups and migrations

Schema changes belong in Django migrations and should be reviewed before deployment. Database backups and SQL dumps contain potentially sensitive data and must never be committed.
