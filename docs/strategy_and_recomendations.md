# Automation Strategy and Recommendations

This document explains which tests from the [Test Plan](test_plan.md) I automated and why, what I
left as manual only, and what I would do next if the project were to scale.

## Why I automated these 2 tests

I chose tests by three criteria: business risk, how much they protect against regressions, and
whether their expected result is clear enough to automate today.

### TCSBP-01: Place valid single bet (E2E, UI)

- **It is the core business flow.** If users cannot place a bet, or a bet is placed with the wrong
  stake, payout or balance, there is direct financial impact and customer disputes.
- **One test covers the whole chain.** It checks the bet slip, the "Placing..." state, the receipt,
  the empty slip after closing, and the balance after the bet. It uses the API to reset and read
  the balance, so it checks the UI against the real state. One run finds three separate defects:
  [SBP-2](issues/issues.md#sbp-2), [SBP-3](issues/issues.md#sbp-3) and [SBP-11](issues/issues.md#sbp-11).
- **Manual checking is slow and error-prone.** Each run needs a payout calculation (stake × odds) and a
  comparison of balances before and after the bet. A script does this the same way every time.
- **It must stay at the UI level.** This is a user journey, so only an E2E test can prove the user
  actually sees the right slip, receipt and balance.

### TCSBP-04: Reject stake exceeding available balance by €0.01 (API)

- **It has the highest financial risk.** If the API accepts a stake above the balance, users can bet
  money they don't have. This is what [SBP-1](issues/issues.md#sbp-1) shows: the balance goes negative.
- **The rule must be enforced at the API.** The UI can validate against a stale balance, and anyone
  can call the API directly. A UI test would not prove the backend is safe.
- **It is fast and stable.** It uses no browser, and it has an exact boundary (balance + €0.01), which
  is easy to get wrong in code and tedious to repeat by hand.

Together, the two tests show that the framework covers both layers: UI with Selenium and API with
Requests.

### Why not the other candidates

| Test case | Why I didn't automate it first |
|---|---|
| TCSBP-02 Accept maximum stake of €100.00 | Medium priority. It currently fails on the same defect as TCSBP-01 ([SBP-2](issues/issues.md#sbp-2)), so it would add little new signal. |
| TCSBP-03 Reject stake above maximum (UI) | High priority, but it passes today and a wrong value is blocked with a message, so the financial risk is lower. This is the next UI candidate. |
| TCSBP-05 Reject bet on past match (API) | The expected result is not defined yet ([SBP-6](issues/issues.md#sbp-6)): there is no error code and no definition of "past". Automating it now would encode my assumptions. It also depends on the match catalog having a past match. |
| TCSBP-06 Reject stake below minimum (API) | High priority and passes today. It is a good next API candidate, together with the negative-stake case ([SBP-5](issues/issues.md#sbp-5)). |

## What I left as manual only

| Area | Why it stays manual |
|---|---|
| Spec review: [SBP-6](issues/issues.md#sbp-6), [SBP-7](issues/issues.md#sbp-7), [SBP-10](issues/issues.md#sbp-10) | Finding gaps and conflicts in the spec needs a person to read and compare sections. These need answers from the Product Owner, not a test. |
| Exploratory testing of stake input | Unusual inputs (negative values, many decimals, pasted text) found [SBP-5](issues/issues.md#sbp-5). This kind of testing finds new bugs; a script only repeats known checks. Once a finding is confirmed, it becomes an API test. |
| Concurrent bets ([SBP-10](issues/issues.md#sbp-10)) | The expected behavior is not defined, so an automated test would have nothing to assert. It also needs precise timing control that is hard to make stable. |
| Visual layout and usability | Checking that the page looks right and messages are clear needs human judgement. Scripted checks for this are brittle and give little value for a single desktop layout. |
| Reset balance consistency ([SBP-8](issues/issues.md#sbp-8)) | `/reset-balance` is a test utility, not a customer feature, so I checked it once manually. The automation works around it: after every reset, tests read the balance with `GET /api/balance` instead of trusting the reset response. |
| Other browsers | Automation runs on Chrome only. The framework is ready for more browsers, but for a desktop-only feature, manual spot checks on other browsers are enough for now. |

## Recommendations if the project scales

### 1. Dockerize the framework and run it in a CI/CD pipeline

- Package the framework in a Docker image with Python, uv, the locked dependencies and a pinned
  Chrome version. The tests then run the same way on any laptop and in CI, and a Chrome auto-update
  cannot break a run. Configuration still comes from environment variables
  (`docker run --env-file .env ...`), so no secrets are built into the image.
- Add a Docker Compose file with a Selenium Grid (`selenium/hub` and browser nodes). The E2E tests
  can then run in parallel and on more browsers. The driver factory already has one place to add a
  remote Grid driver.
- Run the API tests on every pull request. They are fast and need no browser.
- Run the E2E tests after merge or nightly, against a dedicated test environment, with headless Chrome.
- Publish the Allure report as a build artifact, so anyone can see the steps, screenshots and linked
  bugs of a failed run.
- Mark tests that fail on a known bug with `pytest.mark.xfail(strict=True, reason="SBP-x")`. The pipeline
  stays green for known bugs and turns red for a new regression. When a bug is fixed, the test starts
  passing, strict mode fails the build, and someone removes the marker.

### 2. Move most checks down to the API layer

- Keep the E2E suite small: the main betting journey plus the UI validation messages.
- Add a data-driven API suite for the validation rules, using `pytest.mark.parametrize`: minimum and
  maximum stake boundaries, zero and negative stakes, too many decimals, an unknown `matchId`, an
  invalid selection, a missing `x-user-id` header, and the response currency ([SBP-9](issues/issues.md#sbp-9)).
  These tests are fast and stable, and they cover each rule where it is enforced.
- Add contract tests against `open_api_spec.json`. The Pydantic models already check responses; generating
  them from the OpenAPI spec, or using a tool like Schemathesis, would catch mismatches between the spec
  and the API automatically.

### 3. Build a test data strategy

- Today all tests share one account and reset its balance before and after each test. This means the
  tests cannot run in parallel. Give each test, or each parallel worker, its own user, for example from
  a pool of accounts or a user-creation endpoint. Then the suite can run in parallel with `pytest-xdist`.
- Seed a match catalog with fixed dates relative to the run date (past, today, upcoming). Then tests like
  TCSBP-05 have predictable data and do not depend on what the live catalog contains.
- Fix [SBP-8](issues/issues.md#sbp-8), or add a proper seed endpoint, so tests can trust the starting balance.

Before automating TCSBP-05, the minimum stake boundary and concurrency, the Product Owner should answer the
open questions in [SBP-6](issues/issues.md#sbp-6), [SBP-7](issues/issues.md#sbp-7) and
[SBP-10](issues/issues.md#sbp-10). Otherwise the tests would encode guesses instead of requirements.
