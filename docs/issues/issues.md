# Issues

<a id="sbp-1"></a>
## SBP-1 Bet exceeding available balance is accepted by API, resulting in negative balance
**Severity:** Critical<br>

**Preconditions**<br>
Balance is reset via `POST /api/reset-balance`. The actual balance is 120.00 EUR (see SBP-8).

**Reproduction Steps**<br>
1. Call `POST /api/place-bet` with a valid `x-user-id` header and body:
   {"matchId": "championship-leeds-norwich-2026-09-25", "selection": "HOME", "stake": 100}
   The response returns balance 20.
2. Call `POST /api/place-bet` with the same `x-user-id` and body:
   {"matchId": "championship-leeds-norwich-2026-09-25", "selection": "HOME", "stake": 21}
3. Check the response.
4. Open the betting app and check the balance in the header.

**Expected result**<br>
The second request is rejected with 422 and an insufficient balance error. The balance remains 20.00 EUR (spec section 4.1: stake must not exceed available balance; UI + API).

**Actual result**<br>
The API returns 200 and places the bet:
{"message": "Bet placed successfully", "matchId": "championship-leeds-norwich-2026-09-25", "selection": "HOME", "stake": 21, "odds": 2.05, "payout": 43.05, "balance": -1, "currency": "USD"}

The balance becomes negative, and the UI header shows "Balance: -1.00 EUR".

**Business Impact:**<br>
Users can bet more than their available funds via the API and go into a negative balance, which is effectively unsecured credit gambling. This causes direct financial loss and a regulatory breach.

**Evidence**<br>
![Negative balance](screenshots/negative_balance_1.png)

<a id="sbp-2"></a>
## SBP-2 Balance is not updated after placing a bet
**Severity:** Critical<br>

**Preconditions**<br>
Balance is reset to initial value

**Reproduction Steps**<br>
1. Select upcoming match.
2. Click any odds
3. Enter a stake of 100.00 EUR
4. Check that the slip shows selection, stake, balance and payout stake x odds EUR.
5. Click Place Bet.
6. Close the receipt.

**Expected result**<br>
Bet is successfully placed. Stake is deducted once. Success receipt is displayed with the required bet information.

**Actual result**<br>
Balance is not deducted, user can again bet the same amount and then balance would be negative

**Business Impact**
Users can place unlimited bets without funds and push their balance negative, causing direct financial loss and possible regulatory breach (credit gambling).

**Evidence**<br>
![Negative balance](screenshots/negative_balance.png)

<a id="sbp-3"></a>
## SBP-3 Potential payout calculation is incorrect in Bet Receipt
**Severity:** Critical<br>

**Preconditions**<br>
Balance is reset to initial value

**Reproduction Steps**<br>
1. Select upcoming match.
2. Click any odds
3. Enter a stake of 10.00 EUR
4. Click Place Bet.
5. Check potential payout on the bet receipt: it should be as stake x odds

**Expected result**<br>
Potential payout is calculated as stake × odds

**Actual result**<br>
Potential payout is calculated as stake x 2.

**Business Impact**
Customers receive an incorrect record of their potential winnings, leading to settlement disputes, complaints and loss of trust, plus a regulatory risk for misrepresenting bet terms.

**Evidence**<br>
![Incorrect potential payout](screenshots/wrong_payout.png)

<a id="sbp-4"></a>
## SBP-4 Past matches are available for betting
**Severity:** Critical <br>

**Reproduction Steps**<br>
1. Open betting app
2. Check match dates

**Expected result**<br>
Only upcoming/pre-match events should be available for betting

**Actual result**<br>
Past matches is also available for a betting

**Business Impact**
Users can bet on matches with already-known results, guaranteeing wins and causing direct financial loss, fraud exposure and a breach of betting-integrity regulations.

**Evidence**<br>
![Past match](screenshots/past_events.png)

<a id="sbp-5"></a>
## SBP-5 Negative stake is accepted by API and increases user balance
**Severity:** Critical<br>

**Preconditions**<br>
User balance is 120.00 EUR

**Reproduction Steps**<br>
1. Call `POST {{base_url}}/place-bet` with a valid `x-user-id` header and body:
   {"matchId": "premier-league-manutd-chelsea", "selection": "HOME", "stake": -1000}
2. Check the response.
3. Call `GET {{base_url}}/balance`.

**Expected result**<br>
The API rejects the request with **422** and a minimum stake error. No bet is created, and the balance remains 120.00 EUR.

**Actual result**<br>
The API returns 200 and places the bet:
{"message": "Bet placed successfully", "matchId": "premier-league-manutd-chelsea", "selection": "HOME", "stake": -1000, "odds": 2.45, "payout": -2450, "balance": 1120, "currency": "USD"}

The balance increases by 1000, from 120 to 1120.

**Business Impact:**<br>
Any user can add unlimited funds to their balance with a single API call and withdraw or bet with money that was never deposited, causing direct and unbounded financial loss.

**Evidence**<br>
![incorrect balance](screenshots/incorrect_balance.png)

<a id="sbp-6"></a>
## SBP-6 Spec gap: no validation rule or error code defined for bets on past matches
**Severity:** High<br>

**Description**<br>
The spec restricts betting to upcoming (pre-match) events only (section 1 Event Type, section 3 Business Rules), but this rule is never turned into a validation requirement:
- section 4.2 Selection and Match Validation defines only two Match ID rules: required/non-empty, and must exist in the match catalog. There is no rule that the match must be upcoming.
- section 5.3 Expected error classes do not state which error the API should return for a bet on a past match.
- section 2.1 says the match list displays upcoming matches, but it does not say whether past matches must be excluded from `GET /api/matches`.

**Steps to observe**<br>
1. Open Feature Specification – Single Bet Placement.
2. Compare section 1 and section 3 (upcoming events only) with section 4.2 and section 5.3 (validation rules and error classes).

**Expected result**<br>
The spec defines a validation rule that rejects bets on matches whose kickoff is in the past, specifies the layer (UI + API) and the expected API error code and message, and states whether past matches are excluded from the match list.

**Actual result**<br>
The upcoming-only rule exists as a business rule only. There is no validation rule, error code or UI behaviour defined for past matches.

**Open questions for Product Owner**<br>
1. Should the API reject a bet on a past match, and with which error code (e.g. 422) and message?
2. What defines "past": kickoff date before today, or kickoff date/time before now? (The API provides only `kickoffDate` without a time.)
3. Should `GET /api/matches` and the UI exclude past matches entirely?

**Business Impact:**<br>
Without a defined validation rule the upcoming-only restriction may not be implemented or tested consistently. This is already reflected in SBP-4 (Past matches are available for betting), which allows bets on known results and causes direct financial loss.

**Related**<br>
SBP-4 (Past matches are available for betting), TCSBP-05 (Reject bet on past match)

<a id="sbp-7"></a>
## SBP-7 Spec conflict: minimum stake defined as both 1.00 EUR and 1.01 EUR
**Severity:** Medium<br>

**Description**<br>
The minimum stake is defined inconsistently across sections of the spec:
- section 3 Business Rules: Stake min (per bet) = 1.00 EUR
- section 4.4 UI Error Messaging: "Minimum stake is 1.00 EUR"
- section 4.1 Stake Validation (UI + API): Minimum 1.01 EUR

**Steps to observe**<br>
1. Open Feature Specification – Single Bet Placement.
2. Compare the minimum stake value in sections 3, 4.1 and 4.4.

**Expected result**<br>
The minimum stake is defined with a single consistent value in all sections of the spec.

**Actual result**<br>
sections 3 and 4.4 state 1.00 EUR, while section 4.1 states 1.01 EUR.

**Business Impact:**<br>
Ambiguous requirement may lead to inconsistent stake validation between UI and API, causing occasional rejected minimum bets and customer confusion; no direct financial loss.

<a id="sbp-8"></a>
## SBP-8 Reset balance response does not match persisted balance
**Severity:** Medium<br>

**Preconditions**<br>
Initial configured balance is 125.50 EUR

**Reproduction Steps**<br>
1. Call `POST /api/reset-balance` with a valid `x-user-id` header.
2. Check the response body.
3. Call `GET /api/balance` with the same `x-user-id`.
4. Open the betting app and check the balance displayed in the header.

**Expected result**<br>
The balance is reset to 125.50 EUR. The reset response, `GET /api/balance` and the UI all show 125.50 EUR, as the spec requires: "Response body and persisted state must be consistent after reset."

**Actual result**<br>
The reset response reports the correct value:
{"message": "Balance reset successfully", "balance": 125.5, "currency": "EUR"}

But the persisted balance is 120.00 EUR, both in the API and in the UI:
{"balance": 120, "currency": "EUR"}
UI header shows "Balance: 120.00 EUR" (see attached screenshot).

**Business Impact:**<br>
Users receive 5.50 EUR less than the configured reset amount while the API confirms a different value, undermining balance integrity and making balance-based test results unreliable. If /reset-balance is only a test or admin utility with no customer exposure, Medium priorty is justified.

**Evidence**<br>
![Incorrect balance](screenshots/balance_after_reset.png)

<a id="sbp-9"></a>
## SBP-9 Place bet response returns wrong currency (USD instead of EUR)
**Severity:** Medium<br>

**Preconditions**<br>
User balance is reset via `POST /api/reset-balance`

**Reproduction Steps**<br>
1. Call `POST {{base_url}}/place-bet` with a valid `x-user-id` header and body:
   {"matchId": "premier-league-manutd-chelsea", "selection": "HOME", "stake": 10}
2. Check the `currency` field in the response.
3. Call `GET {{base_url}}/balance` and compare the `currency` field.

**Expected result**<br>
The `currency` field is **"EUR"**, as defined in spec section 3 (Currency: EUR) and section 5.3 (place-bet 200 response: `currency: "EUR"`), and it is consistent with `/balance` and `/reset-balance`.

**Actual result**<br>
The place-bet response returns `"currency": "USD"`, while `/balance` and `/reset-balance` return `"EUR"`.

**Business Impact:**<br>
Bet transactions are recorded with the wrong currency, which risks incorrect amounts being displayed to customers, wrong conversions in downstream reporting and accounting, and inconsistent financial records.

<a id="sbp-10"></a>
## SBP-10 Spec gap: concurrent bet rule (409 "bet already in progress") is not defined
**Severity:** Medium<br>

**Description**<br>
The only reference to concurrent bet placement is the error class in section 5.3: "409 bet already in progress (same user)". The behaviour behind it is not specified anywhere else in the spec, so implementation and testing depend on assumptions.

**Open questions for Product Owner**<br>
1. When does a bet count as "in progress": from receiving the request until the response is sent, or until the balance is persisted?
2. Does the rule apply per user across all matches and selections, or only to the same match and selection?
3. Should the second request be rejected immediately with 409, or queued and processed after the first?
4. What should the UI show if the API returns 409 (error modal, silent ignore, or a specific message)?

**Expected result**<br>
The spec clearly defines the concurrency rule, its scope and the expected API and UI behaviour.

**Actual result**<br>
Only the 409 error class is listed, with no definition of scope, timing or UI handling.

**Business Impact:**<br>
Undefined concurrency behaviour risks inconsistent implementation. Parallel requests could lead to double charges or incorrect balance, and without clear criteria concurrency cannot be reliably tested.

<a id="sbp-11"></a>
## SBP-11 Home and away teams are swapped on the bet receipt
**Severity:** Low<br>

**Preconditions**<br>
Match list contains the Championship match Leeds vs Norwich (today)

**Reproduction Steps**<br>
1. Open the betting app.
2. In the match list, find the match Leeds (home) vs Norwich (away).
3. Click any odds button.
4. Enter a stake of 2.00 EUR and click Place Bet.
5. Compare the team order on the success receipt with the match list.

**Expected result**<br>
The receipt shows the match in the same home vs away order as the match list and `GET /api/matches`: **Leeds vs Norwich**.

**Actual result**<br>
The match list shows Leeds (home) vs Norwich (away), but the receipt shows **Norwich vs Leeds**.

**Business Impact:**<br>
Customers cannot reliably tell which team they bet on, especially since the receipt does not show the selection. This causes confusion, disputes about the placed bet and support contacts.

**Evidence**<br>
![Match list vs receipt](screenshots/match_order.png)
