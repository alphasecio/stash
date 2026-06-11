# stash

A minimal self-hosted paste tool. Drop in text, get a shareable link. Stashes expire after 7 days.

## Running locally

```bash
pip install flask gunicorn
python server.py
```

## Running with Docker

```bash
docker build -t stash .
docker run -p 8080:8080 -v $(pwd)/data:/app/data stash
```

## Running on Railway
 
Push to a GitHub repo, connect it from the [Railway dashboard](https://railway.com/?referralCode=alphasec), and set the `DB_PATH` environment variable to a persistent volume path (e.g. `/data/stash.db`).

## Configuration

| Variable | Default | Description |
|---|---|---|
| `DB_PATH` | `./data/stash.db` | Path to the SQLite database file |

## Routes

| Route | Description |
|---|---|
| `/` | Create a new stash |
| `/s/<id>` | View a stash |
| `/r/<id>` | Raw text output |
