Local development with Supabase
=============================

This file explains how to run the project locally while using Supabase, and lists quick commands.

1) Prepare environment

 - Copy the development env template and edit it with your Supabase keys:

 ```bash
 cp config/dev.env .env
 # edit .env and set SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY (server-only), SECRET_KEY, DATABASE_URL (optional)
 ```

 Important: `supabase_config.py` expects `SUPABASE_URL`, `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY`.

2) Start with Docker (recommended)

 - Start the development stack (rebuild if needed):

 ```bash
 # from repo root
 ./manage.sh dev:start
 # follow logs
 ./manage.sh dev:logs
 ```

 - Run migrations or create a superuser inside the container:

 ```bash
 ./manage.sh dev:migrate
 ./manage.sh dev:superuser
 ```

3) Run without Docker (optional)

 ```bash
 python3 -m venv .venv
 source .venv/bin/activate
 pip install -r requirements.txt
 # export env vars locally (careful, do not commit .env)
 export $(grep -v '^#' .env | xargs)
 cd app
 python manage.py migrate
 python manage.py runserver 0.0.0.0:8000
 ```

4) Tests

 ```bash
 # run unit tests
 ./manage.sh test:unit
 # or
 cd app && python manage.py test
 ```

5) Tips & Security

 - Never commit `.env`. Ensure `.gitignore` contains it.
 - Do not expose `SUPABASE_SERVICE_ROLE_KEY` in frontend code. Use it only on the server and store it in Fly/GitHub secrets.
 - Use different SECRET_KEY for production.

6) Quick troubleshooting

 - If Docker doesn't start: `sudo systemctl restart docker` (Linux) and re-run `./manage.sh dev:start`.
 - Static files issue: `docker-compose exec web python manage.py collectstatic --noinput`.

7) Useful commands summary

 ```bash
 # Docker dev start/stop
 ./manage.sh dev:start
 ./manage.sh dev:stop

 # Migrate & superuser
 ./manage.sh dev:migrate
 ./manage.sh dev:superuser

 # Tests
 ./manage.sh test:unit
 ```

If you want, I can extend this doc with sample `psql`/Supabase CLI commands or add local sqlite fallback instructions.
