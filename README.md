# JobListingsScraper

Local web app that classifies job-posting text already sitting in a CSV. You upload a file, pick the text column, and download a CSV with an extracted title, a category, and a confidence score. The classifier is rule-based. It does not call Indeed, LinkedIn, Google, Airtable, or an LLM.

## Run the demo

No API keys. No `.env` file.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 batch_server.py
```

Open `http://127.0.0.1:8000`.

1. Upload a CSV you are allowed to process. The repo does not ship a customer file.
2. Select the column that holds the posting text. A job-id column is optional.
3. Set a row range. Run a small range before a full file.
4. Download the processed CSV from the page.

`python3 -m pytest` is not wired to a `tests/` package. The `test_*.py` scripts at the repo root are runnable examples against synthetic strings:

```bash
python3 test_advanced_classifier.py
python3 test_final_advanced_system.py
```

### Environment variables

`.env.example` lists names only. Every value in that file is a placeholder (`REDACTED`, `appEXAMPLE`, `127.0.0.1`). The current servers hardcode `host="0.0.0.0"` and `port=8000` and never call `os.environ` or `python-dotenv`. Filling in `.env` changes nothing until someone wires it.

If you copy the example, keep secrets out of git:

```bash
cp .env.example .env
```

`.env` is gitignored. `.env.example` is the only env file that belongs in the repo.

## What you get back

`batch_server.py` adds columns such as:

- `extracted_job_title`
- `job_category`
- `general_category` (`exact`, `general`, or `other`)
- `confidence` (0.0 to 1.0)
- `job_details` (text pulled from "Apply to..." style lines)
- `original_content`
- `row_id`

Categories covered by the rules include HVAC Technician, Security Guard, Registered Nurse, Licensed Practical Nurse, Veterinary Assistant, Dental Assistant, CDL Driver, Speech Pathologist, Aviation Mechanic, Plumber, Electrician, and Welder.

## Which server to start

| Command | What it is |
| --- | --- |
| `python3 batch_server.py` | Current UI. Row ranges, batch history, template save/load. |
| `python3 enhanced_server.py` | Older enhanced classifier UI. |
| `python3 simple_server.py` | Smaller inline classifier. |
| `python3 run_mvp.py` | Loads `src/web/mvp_app.py` (needs the `src` layout on `PYTHONPATH`, which the script sets). |

Health check after a server is up: `curl http://127.0.0.1:8000/health`.

## Demo vs production

Safe to show on a laptop: upload your own CSV, classify it locally, download the result. Nothing in this repo needs a live third-party key for that path.

Still local-demo software:

- The process listens on `0.0.0.0:8000` with no authentication, no CSRF protection, and no upload size cap.
- Session data lives in process memory and, for the batch server, as pickle and JSON under `data/`. Those files can contain the full text of whatever CSV you uploaded.
- `*.csv`, `*.xlsx`, `*.json`, `data/`, `exports/`, and `checkpoints/` are gitignored so a normal commit does not pick up uploads. Do not force-add them.
- Google API, Airtable, Playwright, and SQLAlchemy are pinned in `requirements.txt` and are unused by the servers. There is no Sheets sync, no Airtable sync, and no job-board scraper in this tree.
- `extract_job_title_ai` in `src/core/enhanced_classifier.py` returns `None`. It is a comment stub, not a model call.
- Accuracy numbers in older notes came from hand-written fixture strings in the `test_*.py` files. They are not a held-out evaluation.

## Layout

```
batch_server.py                 # server to demo
enhanced_server.py
simple_server.py
run_mvp.py
src/core/advanced_classifier.py
src/core/enhanced_classifier.py
src/core/mvp_classifier.py
src/utils/storage.py            # local pickle/JSON sessions
src/utils/template_manager.py
src/web/mvp_app.py
src/web/templates/index.html
.env.example                    # placeholders only
```

## License

MIT. See `LICENSE`.
