# PythonCarGame

Browser car racing game with a Flask backend for shared public groups, users, and scores.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

Local data is saved in `game_data.db`.

To move the old `users.json` scores into the database:

```bash
python import_users_json.py
```

## Host publicly

Deploy this repo to a Python web host such as Render or Railway.

Use:

```text
Build command: pip install -r requirements.txt
Start command: gunicorn app:app
```

For permanent shared data, add a PostgreSQL database and set the host's `DATABASE_URL` environment variable to that database URL. Then every computer that opens the hosted game URL will use the same public backend and the same shared groups, users, and scores.

If you want the old `users.json` data in the public database, run this once on the hosted server:

```bash
python import_users_json.py
```
