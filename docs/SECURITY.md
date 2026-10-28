# Security

- Never commit `.env`, credentials, private keys, or database dumps.
- Generate a unique `DJANGO_SECRET_KEY` for each environment and keep `DJANGO_DEBUG=false` outside local development.
- Use a dedicated MySQL application account with access limited to `spiceora_db`; do not run the application as a database administrator.
- Keep CORS origins and Django allowed hosts explicit.
- Production deployment must terminate TLS, configure secure cookies and proxy settings as appropriate, and manage secrets outside source control.
- Review dependency updates and run the documented checks before merging.

This is a development foundation, not a production security certification.
