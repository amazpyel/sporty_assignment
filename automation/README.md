# Single Bet Placement: Test Automation

Automated tests for the Single Bet Placement feature:

- `tests/e2e/test_place_single_bet.py`: places a single bet through the UI (TCSBP-01).
- `tests/api/test_insufficient_balance.py`: sends a stake above the available balance to the API (TCSBP-04).

## Tech stack

The assignment asks for Python, Selenium and Requests. I added these tools on top:

| Tool | Why I added it |
|---|---|
| [uv](https://docs.astral.sh/uv/) | Installs the right Python version and all dependencies with one command (`uv sync`). `uv.lock` pins exact versions, so everyone who runs the tests gets the same environment. |
| [Pydantic](https://docs.pydantic.dev/) | Checks every API response against a model in `src/models/betting.py`. If a field is missing or has the wrong type, the test fails at the response, not later with a confusing `KeyError`. Tests also work with typed objects instead of raw dicts. |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Reads the app URL and user ID from a local `.env` file, so they are not hardcoded or committed. Environment variables, such as CI secrets, still take precedence over `.env`. |
| [Allure](https://allurereport.org/docs/pytest/) | Builds a report that shows each test step, a screenshot when a UI test fails, and links to the related bug (SBP-x). A reviewer can see why a test failed without rerunning it. |
| [Ruff](https://docs.astral.sh/ruff/) | Lints and sorts imports with one fast tool, so the code style stays consistent. The rules are in `pyproject.toml`. |

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Google Chrome (Selenium Manager downloads the matching driver automatically)
- Optional, to view the report: the [Allure CLI](https://allurereport.org/docs/install/), which requires Java

## Setup

```bash
cd automation
uv sync
cp .env.example .env
```

Then open `.env` and fill in the values:

| Variable | Required | Description |
|---|---|---|
| `BASE_UI_URL` | yes | URL of the betting web app |
| `BASE_API_URL` | yes | URL of the betting API. It must use the same backend as `BASE_UI_URL`. |
| `USER_ID` | yes | Candidate user ID |
| `BROWSER` | no | Only `chrome` is supported for now (default `chrome`) |
| `HEADLESS` | no | Set to `false` to watch the browser (default `true`) |
| `WINDOW_WIDTH` / `WINDOW_HEIGHT` | no | Browser window size (default `1920` × `1080`) |

## Run the tests

```bash
uv run pytest              # all tests
uv run pytest -m api       # API tests only
uv run pytest -m e2e       # E2E tests only
```

To watch the browser, set `HEADLESS=false` in `.env`.

Both tests check the behavior required by the spec, so they **fail against the current build**
because of known bugs: the API test because of [SBP-1](../docs/issues/issues.md#sbp-1), and the E2E
test because of [SBP-2](../docs/issues/issues.md#sbp-2), [SBP-3](../docs/issues/issues.md#sbp-3)
and [SBP-11](../docs/issues/issues.md#sbp-11).

## View the report

Each run writes its results to `allure-results/`. To open the report:

```bash
allure serve allure-results
```

## Lint

```bash
uv run ruff check .
```
