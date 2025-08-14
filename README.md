# Job Finder

A simple swiping web app built with Flask. It lets you swipe through jobs or potential employees. Profiles are stored in `data.json` so new accounts and swipe results persist across sessions.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Visit `http://localhost:8000` in your browser. Create a job or employee profile on the front page, then swipe through the opposite list.
Existing accounts can be revisited from the home page, and mutual likes appear on the Matches page for review.
