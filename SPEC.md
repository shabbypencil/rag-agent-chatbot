# Tech Stack and Architecture Choices


## Agentic Feature 1: Hybrid Rule-based + LLM fallback routing

The chatbot uses a hybrid routing layer that keeps rule-based classification as the fast path and only calls the LLM when the query is ambiguous or low-confidence. This preserves speed and predictability for clear FAQ or Mandai questions while still allowing fallback intelligence when the intent is mixed.

### Rule-based routing

- Core router is in `router_service.py`
- `route_query(query)` is the main entry point used by `/chat`
- It delegates to `rule_based_route(query)` first
- `rule_based_route` computes:
  - `faq_score` from `FAQ_PHRASES` and `FAQ_KEYWORDS`
  - `mandai_score` from `MANDAI_PHRASES` and `MANDAI_KEYWORDS`
- Score functions match exact phrase signals first, then token-level keyword signals
- Dictionaries are weighted so strong FAQ cues like booking and hours outweigh weaker terms

### Explicit verify-web detection

The router supports a dedicated `verify_web` route for questions requesting external validation or latest updates.

- `VERIFY_WEB_KEYWORDS` contains terms like: `latest`, `current`, `official`, `confirm`, `external`, `updated`, `live`
- If the query includes one of these terms, `rule_based_route` returns immediately:
  - `route`: `verify_web`
  - `confidence`: `0.95`
  - `reason`: `Query explicitly asks for latest or external confirmation`

### Hybrid and ambiguity handling

The router returns `hybrid` when the query:
- has both FAQ and Mandai signals
- is too generic
- has low total score
- contains only ambiguous terms like `park`, `kids`, `family`

This is intentional because these queries need a broader retrieval strategy rather than a single source.

### Confidence and fallback

- `rule_based_route` returns a result object
- `route_query(query)` then decides:
  - if the route is `verify_web`, use it immediately
  - if confidence is high enough for `faq` or `mandai`, use the rule-based route
  - otherwise, call `classify_route(query)` in `llm_service.py`

### LLM fallback

The LLM fallback is only used when the rule-based router is uncertain.

- `classify_route(query)` calls the existing DeepSeek/OpenAI-compatible client
- It uses a dedicated classifier prompt that explicitly asks for JSON:
  - `route` must be one of `faq`, `mandai`, `hybrid`, `verify_web`
  - `reason` must be a short explanation
- The response is parsed safely with `json.loads`
- Invalid or malformed output defaults to:
  - `{ "route": "hybrid", "reason": "LLM output invalid, defaulted to hybrid" }`

### Runtime behavior in `/chat`

In `main.py`:
- the controller calls `route_query(request.message)`
- based on the returned string:
  - `faq` → `retrieve_faq(...)`
  - `mandai` → `retrieve_mandai(...)`
  - `hybrid` or `verify_web` → `retrieve_hybrid(...)` for now

This preserves the existing chat flow while allowing `verify_web` routing to be recognized.

### Debugging support

`debug_route_query(query)` now returns richer diagnostic data:
- original query
- rule-based result object
- final route string
- routing method: `rule_based` or `llm_fallback`
- LLM result when fallback is used

This makes it easy to tell whether the system is using the fast path or the fallback path, and why.

### Summary

The routing design is intentionally conservative:
- rule-based scoring is the primary fast path
- explicit web-verification intent is detected early
- ambiguous or close-score cases are resolved by a lightweight LLM classifier
- the final route remains a simple string so `/chat` and retrieval logic do not need to change dramatically