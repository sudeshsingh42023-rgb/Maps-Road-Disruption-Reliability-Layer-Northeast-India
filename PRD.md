# PRD: Road-Disruption Reliability Layer for Google Maps - Northeast India

**Author:** Sudesh Singh | **Status:** Draft v1 | **Data in prototype:** SYNTHETIC (replace with pilot data)

## 1. Problem
In Northeast India, monsoon landslides, flooding, protest blockades and construction frequently close highways
(corridors such as Guwahati-Shillong, Kohima-Imphal, Silchar-Imphal, Agartala-Guwahati). Fastest-route ETAs
can be wrong for hours or days. Users currently rely on WhatsApp groups, local news and calling drivers.
Gemini-based conversational navigation is arriving in Maps India; the question "Is the road open today?" is only
as good as the freshness and trustworthiness of closure data.

**Evidence to add (from your discovery work):** [N] interviews/survey responses. Insert top 3 quotes, % who
use WhatsApp for road status, avg. time lost per disrupted trip, # of trips delayed in the last 6 months.

## 2. Users and jobs-to-be-done
| Persona | Job to be done | Pain today |
|---|---|---|
| Student/commuter (e.g. Imphal-Guwahati) | Decide whether to travel today and which route | Conflicting WhatsApp info |
| Truck/goods driver | Avoid getting stranded for 12+ hours | No reliable reopen ETA |
| Small trader / tourism operator | Plan deliveries, bookings | Cancellations from surprise closures |
| Local reporter/volunteer | Report closures quickly | No feedback that report was used |

## 3. Goals and non-goals
**Goals:** (1) reduce unplanned reroutes and stranded trips on pilot corridors; (2) surface closure
confidence and reopen estimates; (3) keep false closure alerts low enough to preserve trust.
**Non-goals:** nationwide rollout in v1; replacing official NHAI/BRO/state advisories (use them as high-trust sources).

## 4. Metrics
- **North Star:** % of trips on pilot corridors completed with no unplanned reroute.
- **Input metrics:** reports per segment per day, median time from event to Maps display, % reports confirmed within 30 min.
- **Guardrails:** false-closure alert rate (target <20%), alert opt-out rate, report-abuse rate, user-reported "wrong info" taps.
- **Quality (prototype):** AUC and precision/recall by threshold (see `metrics.json`).

## 5. Solution (v1)
1. **Report + confirm:** one-tap "road closed / open / partly open" with optional photo; neighbors get a "Still closed?" prompt.
2. **Credibility scoring:** model combines confirmations vs denials, reporter history, photo, rainfall, cause and recency; reports decay with a half-life.
3. **Segment confidence:** recency-weighted average of recent report scores, shrunk toward a low prior -> Likely open / Uncertain / Likely closed.
4. **Multilingual signal ingestion:** Gemini extracts structured events from news text (English, Hindi, Assamese, Bengali) as extra, lower-trust evidence.
5. **Conversational answer:** "Is NH to Imphal open today?" answered with status, confidence, cause, and alternative.
6. **Offline-friendly:** cache last known status for low-connectivity stretches.

## 6. Key trade-offs
| Decision | Option A | Option B | Choice and why |
|---|---|---|---|
| Alert threshold | Low (catch more closures) | High (fewer false alerts) | Per-cause: loose for landslide/flood (safety), strict for protest/accident (trust) |
| Official vs crowd data | Official only | Blend | Blend; official sources weighted highest |
| LLM-extracted news events | Auto-publish | Evidence only | Evidence only in v1 (hallucination risk) |
| Reporter incentives | Badges | None | Light badges; avoid reward for volume to limit spam |

## 7. Risks
False closures causing detours/lost trust; abuse and brigading; privacy of location reports (aggregate, no raw trails);
LLM extraction errors; sparse data on remote segments (show "no recent data" instead of a guess).

## 8. Rollout and experiments
- **Phase 0 (4 wks):** offline replay on historical closures; compare to naive rule.
- **Phase 1 (8 wks):** pilot on 1-2 corridors; A/B: with vs without confidence label.
- **Phase 2:** expand to NE corridors; add reopen ETA model.
- **Launch criteria:** false-alert rate under target for 2 consecutive weeks, North Star improves vs control.
- **Cross-functional:** Eng (Maps data), UX (confidence design), Legal/Policy (user content, safety), Partnerships (state agencies), Marketing/Comms (local-language launch).

## 9. Open questions
How to verify reports in zero-connectivity stretches? What reopen-ETA error is acceptable? How to handle disputed closures?
