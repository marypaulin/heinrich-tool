# Heinrich Tool — Agent Instructions

## Entry points & responsibilities

`services.py` is the sole public entry point for document generation. The entry
points (`app.py`, `cli.py`) call only `services.py`, with arguments built by
`input_args.py` — never internal pipeline modules.

Input validation and formatting of user-supplied arguments belongs in `input_args.py`,
not in `services.py`.

## Data protection

Real client data (company details, rates, the document template, time-tracking
CSVs) lives outside the repository, at the paths stored in the machine-local
`settings.json`. Never read the files it points to into context. Use the
substitutes instead: they are named `_sample` and live in `tests/fixtures/`:
`Vordruck_sample.docx`, `heinrich_zeiterfassung_sample.csv`, `config_sample.json`
(not `config.example.json`).

`notes/` is gitignored too but holds no client data — it's the user's own
working notes and is always fine to read.

## Error handling

- Hard errors (file not found, invalid input): raise `ValueError` or `FileNotFoundError`
  and let them bubble up to the entry point.
- Non-fatal warnings and status messages for the UI: accumulate via `Messages.info()` /
  `.warning()` and return them — never use `print()`.
- Logging messages and `raise` texts are in English; `Messages` entries shown to the
  user are in German. An exception text is logged as well as displayed, so it follows
  the logging rule — turning it into German UI text is the entry point's job.

## Models

- Immutable value objects use `@dataclass(frozen=True)`. Produce new objects instead of
  mutating.
- Domain models that map to Word template placeholders expose a `to_mapping()` method
  returning `dict[str, str]`.

## Money

- Money amounts and hours are `Decimal`, never `float`, from config and CSV to
  the printed document. Build them from strings for data (`Decimal("65.00")`),
  from ints for constants (`Decimal(1)`).
- Cent precision lives only in `money.py` (`CENT`, `round_cents`, commercial
  half-up rounding). Round where an amount is calculated; only products need
  it, sums of cent amounts stay exact. `format_price` never rounds, it rejects
  unrounded amounts.

## Comments and docstrings

- No inline comments unless the *why* is non-obvious (a hidden constraint, a workaround,
  a non-intuitive invariant). Never describe *what* the code does.
- Docstrings only for functions with a non-obvious contract or complex behavior (see
  `_replace_in_paragraph`, `csv_rows_to_line_items` for examples of what
  warrants one).
- Short one-line module docstrings at the top of each file.
- Be explicit about what another developer would otherwise have to ask: a hidden
  constraint, a tooling decision and its reasoning, a deliberate omission.
- Never explain language or library mechanics. Only domain knowledge and decisions
  get documented.

## Style conventions

- Language: code, docstrings and commit messages are in English; the decision log,
  `notes/` and the README are in German. (For `Messages` and logging see Error
  handling above.)
- Long files are divided by section separators: `# — Section name ————————————————`.
- Absolute imports only (`from heinrich_tool.backend.config import ...`), enforced
  by ruff (TID252). Streamlit runs `app.py` as a script, where relative imports fail.
- Terms: *client* is Heinrich Metallbau, the business this tool is built for;
  *customer* is Heinrich Metallbau's customer, who receives the offer or invoice.

## Testing

- One test file per source module: `tests/backend/test_<module>.py`, or
  `test_<module>_<object>.py` when a module holds several domain objects.
- Test only cases that occur in real use.
- Error tests check the exception type, never the message text.
- Test data lives in `tests/fixtures/` and is invented: numbers with realistic
  digit counts (project 4, order number usually 8, receipt 10). Never real
  client or customer data; the repository is public.
- Setup that every test in a module repeats (the sample template, the sample
  config) is a pytest fixture, not a helper called at the top of each test.
  A fixture used by one module lives there; one shared across modules goes
  into `tests/conftest.py`.
- Test data helpers take every value a test asserts on as an argument, so
  the expected value is visible in the test itself.

## Git

- Conventional Commits, one line of at most 50 characters, imperative mood,
  no body.
- Scopes: `backend`, `ui`, `cli`, `docs`, `build`, `ai`. Leave the scope out
  when none of them fits.
- Behavior changes get their own commit, separate from refactors and tests, so
  `git log` explains why an old invoice shows a different number.
- Verification: `ruff check .` and `uv run pytest -q`, for commits that touch
  `.py` files. Documentation-only commits need no check.
