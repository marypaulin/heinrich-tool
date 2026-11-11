# Accepted cleanup findings
- `pdfgen.py` · `_render_with_word`, `_render_with_libreoffice` — both end with the same existence check and success message. Reason: the error texts differ per engine, a shared helper would be about as long and couple two paths that change for different reasons. (2026-11-04)
- `app.py`, `cli.py` · logging setup — both entry points configure logging with the same lines. Reason: each entry point owns its logging; the app will likely log to a file for support, so the copies are expected to diverge. (2026-11-04)
- `json_files.py` · tests — no own test file; covered through test_config.py and test_settings.py. Reason: it only rewords the json and pydantic errors, and tests don't check message text. (2026-11-09)
