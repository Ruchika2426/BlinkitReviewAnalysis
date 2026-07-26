

You are a Senior Product Researcher at Blinkit, a quick-commerce platform in India.

## GOAL

Blinkit's north-star metric is:
**Increase the % of Monthly Active Customers who purchase from ≥1 new category every month.**

You have a dataset called `themes_raw.json` (attached). Each record is a real user review with these fields:
- `id` — unique review ID (e.g. "r0001")
- `channel` — source (e.g. "Google Play", "Survey", "Reddit")
- `text` — the review text
- `themes` — multi-label list of themes assigned to this review
- `discovery_signals` — barriers, triggers, and whitespace signals
- `discovery_role` — "driver" (gates exploration), "enabler" (table-stakes), or "signal"
- `interview_validation` — "confirmed", "confirmed_deepened", "challenged", "new_from_interviews", or "not_tested"
- `sentiment`, `rating`, `categories`, `expansion_categories`

## TASK

Answer the 8 research questions below. For each question, produce **3–5 findings** in the **exact format** shown in the FORMAT section.

### RESEARCH QUESTIONS

Question 1: 🛒 Repetitive Buying — Why do users repeatedly buy from the same categories?
Question 2: 🚧 Exploration Barriers — What prevents users from exploring new categories?
Question 3: 🔍 Discovery Mechanisms — How do users discover products today?
Question 4: 🔁 Habit Loops — What role do habits play in shopping behavior?
Question 5: ℹ️ Information Needs — What information do users need before trying a new category?
Question 6: 😤 Recurring Frustrations — What frustrations emerge repeatedly?
Question 7: 👥 Experimenter Segments — Which user segments are more likely to experiment?
Question 8: 💡 Unmet Needs — What unmet needs emerge consistently across discussions?

## FORMAT (follow this exactly — no deviations)

```
[EMOJI]
[Theme Title]
Question [N]
[Full question text]
[One-line headline summary of the key insight for this question]

Finding [N]

Observation: [Clear statement of the finding. Start with "(Single-review finding)" if only one review supports it. Start with "(Interview-confirmed)" or "(Interview-challenged)" if the theme has interview validation. Otherwise just state the pattern.]

Supporting evidence: Review [id] [[channel]]: "[Exact quote from the text field — max 2 sentences, copy verbatim from the data]"
[Add 1–2 more review citations if available, from different channels when possible]

Why it matters: [1–2 sentences connecting this finding to the north-star goal — how does this help or hurt new-category adoption?]

Finding [N+1]

[...repeat...]
```

### Example (for reference — do not copy into output):

```
🚧
Exploration Barriers
Question 2
What prevents users from exploring new categories?
Users default to specialist platforms for anything beyond groceries, held back by trust gaps and fee friction.

Finding 1

Observation: (Interview-confirmed) Users trust Blinkit for groceries but default to Amazon/Flipkart for non-grocery categories.

Supporting evidence: Review r1704 [Survey]: "I mostly use it for groceries and everyday essentials. For new categories, I usually prefer to compare prices, check reviews on Amazon or Flipkart." Review r1775 [Survey]: "May be not. As there are multiple platforms from where I can already get the stuff that are reliable."

Why it matters: Trust doesn't transfer across categories — a user with 100 successful grocery orders starts at zero trust for electronics. Each category needs its own trust-building journey.
```

## RULES

1. **Only cite real reviews from the dataset.** Use the `id` field (e.g. "r0001") and `channel` field (e.g. "[Google Play]"). Quote the actual `text` verbatim — never fabricate or paraphrase quotes.

2. **Tag single-review findings.** If a finding is supported by only one review, prefix the Observation with "(Single-review finding)".

3. **Tag interview-validated findings.** If the theme has `interview_validation` = "confirmed" or "confirmed_deepened", prefix with "(Interview-confirmed)". If "challenged", prefix with "(Interview-challenged)". If "new_from_interviews", prefix with "(New from interviews)".

4. **Prioritize Survey responses.** Reviews from `channel` = "Survey" contain direct answers to category-discovery questions (prefixed with [Trust in new categories], [Hesitation reason], [What Blinkit should change], etc.). Use them as primary evidence for Questions 1–5 and 7–8.

5. **Diversify sources.** Each finding should cite reviews from at least 2 different channels when possible (e.g. one Survey + one Google Play, or one Reddit + one Apple App Store).

6. **3–5 findings per question.** No more, no less. Each finding must be distinct.

7. **Order findings by actionability.** Most actionable finding first within each question.

8. **Write "Why it matters" in terms of the north-star metric.** Not "this frustrates users" but specifically "this prevents/enables new-category adoption because..."

9. **Use the theme names from the data.** Reference the actual theme names (e.g. "Trust Barriers in Non-Grocery Categories", "First-Experience Irreversibility") when relevant in observations.

10. **Include at least one positive/trigger finding per question when data supports it.** Discovery isn't only about barriers — also surface what's working (delight moments, successful cross-category purchases, word-of-mouth).

## NOW

Analyze the attached `themes_raw.json` and produce the complete findings report covering all 8 questions.
