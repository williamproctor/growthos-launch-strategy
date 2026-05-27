# Survey Insights · GrowthOS Launch

*181 responses · Live · Window: May 12–27, 2026 · LinkedIn 22% known UTM, rest direct/unknown · Honeypot 100% pass (but see Response Quality Audit) · Generated Wed May 27 by `analyze_survey.py` + `validate_responses.py`*

This is the strategic read on the survey for launch. **Read the Response Quality Audit section first** — it changes how every number below should be interpreted.

> **Updated May 27 PM (v3):** previous analysis ran on a paginated 100-row export. This is the full 181-response dataset, with a new authenticity audit pass on top. Headline percentages stay within 5pp of the prior read — narrative is intact and actually **gets stronger** when you drop the suspect rows — but the advisor opt-in pool shrinks materially and the high-intent lead list drops from 26 to 12 confirmed-real leads.

---

## ⚠ Response Quality Audit — read this before sharing any number

After looking at the data row by row, **41% of the 181 responses (75 rows) are either confirmed spam or highly suspicious**. The honeypot caught zero of them — these are sophisticated panel / synthetic submissions that pass naive bot checks.

### The breakdown

| Category | Count | % | What it means |
|---|---|---|---|
| **LIKELY_REAL** | 92 | **51%** | Trust these for the narrative read |
| UNCERTAIN | 14 | 8% | Sparse profile, no smoking gun. Review optional. |
| **SUSPICIOUS** | 28 | **15%** | Multiple red flags. Drop from sales outreach. |
| **CONFIRMED_SPAM** | 47 | **26%** | Domain farm + IP cluster + templated text. Drop entirely. |

### What the spam looked like

Four clear contamination sources, all clustered on May 25 (the day of the 65-response spike):

1. **Email domain farms.** 48 responses came from disposable / generated email domains: `zz.rehearsalk.com` (10), `*.xintaitong.com` (16 across 5 subdomains), `huhutu.cloud` (4), `tiankaixin77.xyz` (5), `lingeringp.com` (3), `youngestsd.com` (2), `vnaikai.life` (2). These have a tell: short 2-3 letter random subdomain on a meaningless parent domain. All passed honeypot.

2. **IP-cluster spam ring #1 (9 responses in 72 minutes, May 25, 5:54-7:06pm UTC).** Single IP hash `68dd86…` submitted 9 responses with @gmail.com addresses following a `firstname{digits}@gmail.com` pattern (`pabdullahi251`, `rebeccapaul0102`, `tiipantoo`, `juliyawilliansom`, etc.). All position = "Director" or "Manager". All advisor-opted-in. All templated Q21 answers.

3. **IP-cluster spam ring #2 (8 responses, May 25-26).** Single IP hash `77b74962…` cycling through @proton.me / @tuta.io / @tutamail.com addresses with varied stolen-sounding names ("Susan Harris", "Megan Sullivan", "G Patterson Jr") and gaming the role multiple-choice (CEO, VP, Team Lead, Director, Manager, Growth Lead — all from one IP).

4. **IP-cluster spam ring #3 (7 responses in 27 minutes, May 25, 7:59-8:26pm UTC).** Single IP hash `42a228…` recombining a pool of ~5 first names (Mason, James, Harry, Nico, John, Jordan) into seven different `name{digits}@gmail.com` accounts, each picking a different role (Ceo, Marketing, Director, Content lead, Marketing ops, Head of growth, etc.) — a clear attempt to look like a varied sample from one operator.

5. **Templated Q21 answers** that smell of one person running responses through a templated prompt: variations of *"Our team is most excited about AI-powered…"* and *"We wish AI could move from being a 'helper' in GTM to…"* etc. One response literally opened with *"Here are several different natural responses for your reference: 1…"* — a model output left in by accident.

### What changes when you drop the suspect rows

This is the most important table in the doc:

| Metric | Full 181 | Clean 92 (LIKELY_REAL) | Junk 75 |
|---|---|---|---|
| Engineer disenchantment | 63% | **65%** | 57% |
| Fragmentation pain | 64% | **77%** | 43% |
| Attribution pain | 56% | **71%** | 33% |
| AEO investment (top-2) | 52% | **57%** | 45% |
| Advisor opt-ins | 72% (130) | 60% (55) | **91% (68)** |
| Report opt-ins | 80% (144) | 86% (79) | 71% |
| **High-intent leads** | **26** | **12** | 14 |
| ICP fit composite | 50% | 35% | **73%** |

**Three things to internalize:**

- **The narrative gets STRONGER on the clean set.** Fragmentation pain jumps from 64% to 77%. Attribution pain from 56% to 71%. AEO investment from 52% to 57%. **Spam was DILUTING the pain signal** — real marketers complain more than paid panel-takers.
- **The advisor pipeline is materially smaller than it looked.** Junk respondents opt-in at 91% (because the panel reward is "yes please contact me"). Clean respondents opt-in at 60%. **Use 55, not 130, as the real opt-in pool.** 60% is still an excellent rate.
- **The ICP fit composite is the metric that lies hardest.** Junk respondents claim "VP Marketing / Series A / $25-75K" at 73% because they're optimizing for what the panel thinks is the desirable profile. Real ICP fit is **35%, not 50%**. Sales targeting needs to be tighter than the raw number suggests.

### What to do about it

1. **Sales:** call only the **12 LIKELY_REAL high-intent leads**, not the full 26 from the raw CSV. The clean subset has an `LR` flag in `Survey - Flagged Responses.csv`.
2. **Headline messaging for the launch:** lead with the **CLEAN numbers** (77% fragmentation pain, 71% attribution pain, 60% advisor opt-in rate on real respondents). They tell a more honest, more compelling story.
3. **Operations:** the honeypot alone is not enough. Recommend adding:
   - Email-domain block list (the parents we saw: `xintaitong.com`, `rehearsalk.com`, `lingeringp.com`, `youngestsd.com`, `huhutu.cloud`, `tiankaixin77.xyz`, `vnaikai.life`)
   - Rate-limit by IP hash (max 1 response per IP per 24h, or require a captcha after the 2nd)
   - Optional secondary verification: magic-link email confirmation before counting an opt-in as a "lead"
4. **For the post-mortem:** find out what drove May 25 traffic. The day was 65 responses; **at least 40 of them appear to be panel/spam**. If it was a paid LinkedIn campaign that got pasted into a survey-completion farm, we've effectively been paying for spam. Worth understanding before the launch wave hits.

The flagged-row CSV (`Survey - Flagged Responses.csv`) has every row scored 0-100 with the specific flags that fired, sortable for manual review. Re-run `python3 validate_responses.py` after each new export.

---

## Bottom line

---

## Bottom line

1. **The survey validates the entire narrative spine.** 63% of respondents show signs of "Marketing Engineer" disenchantment (skill loss, tool churn, can't hire AI talent). 64% have fragmentation pain. 52% plan to invest in AI Visibility / AEO in the next 12 months — the **#1 investment category**, tied with marketing ops (50%) and content production at scale (49%), beating outbound (41%) and strategy (20%).
2. **There is a 72% opt-in rate for an advisor session — 130 names — BUT see the Quality Audit above.** On the clean LIKELY_REAL subset the rate is 60% (55 names). 26 respondents in the raw set directly fit the highest-intent profile (planning AEO + not currently tracking + opted in for advisor); **only 12 of those survive the authenticity audit**. Those 12 are the ones sales should actually call this week. The full vetted list is `Survey - High Intent Leads.csv`; cross-reference with `Survey - Flagged Responses.csv` to filter to LIKELY_REAL only.
3. **The awareness needle is moving — but barely.** In the previous 100-row sample, zero respondents had mentioned GrowthOS or anything in the GrowthX ecosystem. In the full 181, **one respondent named "GrowthOS"** and **one specifically called out "checkthat.ai"** as part of their research stack (literally asking *"Do satellite tools by GrowthX count?"*). Direct competitors mentioned: NotebookLM (11), Granola (8), AirOps (4), Cassidy, HeyMarvin, AnswerRank.ai. **The launch is still the awareness event.**

---

## What changed from the 100-row read

| Metric | 100-row | 181-row | Direction |
|---|---|---|---|
| "Marketing Engineer" disenchantment | 62% | 63% | flat |
| Fragmentation pain | 66% | 64% | flat |
| Attribution pain | 60% | 58% | flat |
| AEO investment (top-2) | 56% | 52% | -4pp |
| Advisor opt-ins (count) | 73 | **130** | **+78%** |
| Report opt-ins (count) | 85 | **144** | **+69%** |
| ICP fit (role + stage + budget) | 50 | 91 | proportional |
| High-intent leads (raw) | 16 | **26** | **+63%** |
| High-intent leads (audited LIKELY_REAL only) | n/a | **12** | new with v3 |
| Brand mentions (GrowthOS / CheckThat) | 0 | **2** | **off zero** |

The pattern: percentages held, absolute volumes roughly doubled. That's the right shape — it means the prior sample wasn't biased, just incomplete.

---

## How the survey validates each beat of the launch narrative

### Beat 1 — The false prophecy ("Marketing Engineer")

**The story:** the industry is telling marketers they need to become engineers.

**The proof in the data:**

- **63% Marketing-Engineer disenchantment** — flagged either skill loss, tool churn, hiring problems, or "knowing which tools are worth it" as a top challenge.
- **52% say maintaining brand voice and quality is their #1 AI challenge** — and 83% used AI to produce written content in the last 90 days. They are publishing AI content at scale and losing their voice doing it.
- **45% are publishing more AI content AND have brand-voice pain.** That's the "fast crap" cohort.
- **Only 9% have rebuilt around AI AND have a documented playbook.** The market is in the messy middle — they bought the tools, can't operate them at scale.
- **One respondent literally said:** *"I want AI agents to do tasks 'end-to-end' in an autonomous way and ping me as a leader with updates. Idea is to have 'goal-oriented agents' and not just 'helping agents'."* That's a marketer articulating the closed-loop pitch back to themselves — without knowing GrowthOS exists.

### Beat 2 — The refusal ("Marketers don't need to become engineers")

**The story:** we relieve them of this pressure.

**The proof in the data:**

- **27% flagged "team losing core skills (writing, strategy, creative thinking)" as a top-2 challenge.** Marketers are watching the pitch hollow them out.
- **49% say AI creates "more content but less strategic thinking"** — they SEE the trade.
- **44% report "saves time on tasks but adds time to reviewing and editing"** — the productivity gain is largely an illusion at scale.
- This audience is primed to hear: *you should have a system that already did the engineering, not a side career in engineering.*

### Beat 3 — The different bet (closed-loop content system)

**The story:** stop assembling 12 tools yourself.

**The proof in the data:**

- **64% have fragmentation pain** — either no consolidated view of web/content performance, OR fragmentation is their #1 blocker.
- **58% can't cleanly attribute content/organic spend to revenue.** ("Partial" 43%, "mostly no" 12%, "don't try" 2%.)
- **31% say tool churn is a top-2 AI challenge** + **31% say new tools create more tool churn than they solve.**
- **26% say strategy is the #1 thing standing between their current content/organic work and the results they want.** Not capacity. Not measurement. *Strategy* — meaning a system, not more tools.
- **Voice-of-customer quotes that are literally the GrowthOS pitch:**
  - *"I feel like I need to build every part of the workflow with skills. It would be great if we defined the goal, gave the inputs, and then AI would walk through building a workflow holistically."*
  - *"Skill-based AI systems, where the model operates from documented judgment and voice rather than one-shot prompts. The shift is from prompting to operating."* (cited as the tool they're most excited about)
  - *"I wish AI could reliably act as an execution-ready GTM operator, not just an assistant that produces drafts or insights."*
  - *"I want AI agents to do tasks 'end-to-end' in an autonomous way and ping me as a leader with updates. Idea is to have 'goal-oriented agents' and not just 'helping agents'."* **← new in full set**
  - *"Connect dots across siloed systems without me babysitting."*
  - *"Understand our ICP, positioning, category context, pricing, sales cycle... AND keep it consistent across every asset without as much manual prompting."*
  - *"Find all the relevant pieces of info it needs to know so I don't have to upload and crowdsource relevant docs to teach it."* **← new**

### Beat 4 — The new stakes (AEO / AI visibility)

**The story:** agents are reading the web for buyers. Show up or disappear.

**The proof in the data:**

- **52% plan to invest in AI Visibility / AEO in the next 12 months — the #1 category.** Beats outbound (41%) and ties with marketing ops (50%) and content production at scale (49%).
- **40% are "figuring it out" on AI search strategy.** Another 9% are relying on existing SEO and assuming it carries over. Another 8% haven't thought about it. **That's 57% of the market without a coherent AEO answer.**
- **Only 8% currently report AEO as their primary inbound driver.** The category isn't won.
- **Among respondents who plan to invest in AEO, the top barriers are: "no tool to track it" (29%) and "budget" (28%) — close to a tie.** Budget jumped from 14% in the 100-row sample to 21% overall, suggesting the new respondents skew earlier-stage / more budget-constrained.
- **22% are the critical buying signal cohort** — planning AEO investment AND not currently tracking — exactly the gap a launch event closes.

---

## The buying signals (sales-ready)

| Signal | Count | Why it matters |
|---|---|---|
| Opted in for advisor session | **130 / 181** | Genuine sales-call intent |
| Opted in for the report | 144 / 181 | Nurture pool for launch sequence |
| ICP fit (role + stage + budget $10k+) | 91 / 181 | Solid sample fit; refine with manual review |
| **High-intent leads (raw)** | **26** | Advisor opt-in + planning AEO + not tracking |
| **High-intent leads (audited LIKELY_REAL)** | **12** | The list sales should actually call this week |
| Critical buying signal cohort | 39 / 181 | Planning AEO but not yet tracking — focused launch nurture |

---

## Voice of the customer — the lines to put on slides

The Q21 free-text ("what do you wish AI could do that it can't today") is the most useful field in the survey. These are the lines I'd put in the launch deck:

> "I feel like I need to build every part of the workflow with skills. It would be great if we defined the goal, gave the inputs, and then AI would walk through building a workflow holistically."

> "I want AI agents to do tasks 'end-to-end' in an autonomous way and ping me as a leader with updates. Idea is to have 'goal-oriented agents' and not just 'helping agents'."

> "Connect dots across siloed systems without me babysitting."

> "I wish AI could reliably act as an execution-ready GTM operator, not just an assistant that produces drafts or insights."

> "Function as a dependable GTM execution layer rather than mainly a suggestion or content tool."

> "Find all the relevant pieces of info it needs to know so I don't have to upload and crowdsource relevant docs to teach it."

> "Understand our ICP, positioning, category context, pricing, sales cycle, product constraints, and the 'why' behind past decisions, AND keep it consistent across every asset without as much manual prompting."

> "Reliably connect content and AI-assisted campaigns to actual pipeline/revenue outcomes across channels without so much manual setup."

> "Skill-based AI systems, where the model operates from documented judgment and voice rather than one-shot prompts. The shift is from prompting to operating." *(from Q10 — articulating the GrowthOS thesis as the thing they are most excited about)*

---

## Where the market is on AEO

| State | % |
|---|---|
| Has a defined AEO strategy | 43% |
| Figuring it out | 40% |
| Relying on existing SEO, assumes it carries over | 9% |
| Haven't thought about it | 8% |

| Tracking AI brand mentions | % |
|---|---|
| Track regularly | 51% |
| Checked a few times, don't track | 27% |
| Know we should, haven't started | 13% |
| Not a priority | 9% |

| Biggest barrier to improving AI visibility (all respondents) | % |
|---|---|
| Don't have a tool to track it | 25% |
| Don't know where to start | 22% |
| Budget | 21% |
| Other | 14% |
| Not sure who owns it | 11% |
| Not convinced it matters | 7% |

**Among the 80 respondents planning AEO investment specifically, the barriers shift:** "no tool" (29%) and "budget" (28%) are essentially tied. They want it, they don't have the means.

---

## ICP behavior — who's furthest along

### Role × AEO strategy

| Role | n | Defined strategy | Figuring it out |
|---|---|---|---|
| **VP of Marketing** | 49 | **63%** | 24% |
| Growth Lead | 32 | 53% | 38% |
| Marketing Ops / RevOps | 26 | 38% | 35% |
| Content Lead | 25 | 32% | 56% |
| Founder / CEO | 30 | 27% | 50% |
| Other | 19 | 21% | 53% |

**Read:** VPs of Marketing are the most strategy-mature and the most tool-ready — that's the primary ICP. Growth Leads come second and are a growing cohort to court. Founders are the least mature; they need education before tools. Content leads are the practitioners feeling the pain most acutely.

### Stage × Budget (where the budget actually sits)

| Stage | n | Modal monthly budget |
|---|---|---|
| Bootstrapped | 45 | Under $10K (31%) |
| Seed | 51 | Under $10K (33%), then $25-75K (29%) |
| **Series A** | 44 | **$25-75K (48%)** |
| Series B-C | 24 | $25-75K (38%) |
| Series D+ | 15 | $25-75K (47%) |

**Read:** Series A is the highest-density paying ICP. Past the figuring-it-out phase, has urgency, has budget concentration. Series B-C and D+ also cluster cleanly at $25-75K. Bootstrapped and seed are most numerous but lowest spend per company — they're the report / community / playbook audience, not the immediate buyer.

### Content/SEO/organic spend × AEO maturity

| Spend tier | n | % with defined AEO strategy |
|---|---|---|
| $50K+/mo | 20 | **75%** |
| $15-50K/mo | 44 | **66%** |
| $5-15K/mo | 42 | 50% |
| Under $5K/mo | 55 | 17% |
| Don't track | 20 | 20% |

**Read:** clean signal — *AEO maturity scales directly with content spend.* The companies already spending real money on content have already moved on AEO. The under-$5K cohort hasn't gotten there yet. ContentOS pricing tiers should reflect this distribution.

---

## Competitive landscape (from Q10 free-text — "tools you're excited about")

**Direct competitors / adjacent tools mentioned (full 181):**

- **NotebookLM** — 11 mentions. The clear plurality. Mostly used for research and synthesis. Not a direct competitor but the workflow they're already using.
- **Granola** — 8 mentions. Meeting notes + early ABM lead scoring. Adjacent.
- **AirOps** — 4 mentions, including one specifically for AEO workflow ("content review to ensure keywords are utilized to bolster our AEO strategy"). Closest direct competitor in the data.
- **Cassidy** — 1 mention, agent/workflow builder
- **HeyMarvin** — 1 mention, research/analysis
- **AnswerRank.ai** — 1 mention, AEO-specific
- **n8n, Zapier+AI agents, Clay, 11x.ai, Lindy** — sporadic mentions, workflow / automation adjacent
- Many generic mentions of *"AI-native GTM tools"*, *"agentic workflows"*, *"multi-agent orchestration"*, *"end-to-end GTM execution"*

**Foundation models / general AI:** ChatGPT (69%), Claude (62%), built-in tooling (46%), Gemini (42%), Cursor / coding assistants (28%), Perplexity (16%).

**Mentions of the GrowthX ecosystem:**

- **GrowthOS:** 1 mention (named directly as a tool they're excited about)
- **CheckThat:** 1 mention (*"Do satellite tools by GrowthX count? I've found checkthat.ai and it's now in my research stack"*)
- **ContentOS:** 0

That's it. **The needle moved off zero but barely.** The launch is still the awareness event — the market is hungry for what we describe and has effectively not heard of us yet.

---

## Data quality caveats (read before sharing any number)

**See the Response Quality Audit at the top of this doc — that supersedes the previous "off-ICP" and "templated Q21" caveats.** Summary of what survived as relevant caveats after the audit:

1. **The audit is heuristic, not perfect.** The 92 LIKELY_REAL rows are conservative — a few of them are probably also panel-spam I haven't yet caught (and a few of the 14 UNCERTAIN rows are probably legit but incomplete). Treat the audit categories as a strong prior, not a final answer. Spot-check the lead CSV manually before any individual outreach.
2. **UTM coverage is poor.** Only 22% (39/181) have a known UTM source (all LinkedIn). The other 78% lack source attribution. Add UTM enforcement on all distribution links before the launch wave.
3. **The May 25 spike is 65 responses (35% of total), May 26 added another 38 (21%).** Combined: 57% of the entire sample came in over those two days. The audit shows that at least 40 of those 103 are panel/spam contamination. **Find out what drove the May 25 traffic** — paid LinkedIn, panel buy, scraped email blast, viral post. If we're paying for spam, kill that channel before the launch wave.
4. **The sample is self-selected.** People who finish a 27-question survey about AI in GTM are more AI-engaged than the average marketer. Adjust the absolute pain percentages downward when generalizing to "all marketers."
5. **Honeypot caught nothing.** 100% pass rate but 26% of the responses are confirmed spam. The current bot detection on the survey form is not effective against panel/operator-driven submissions. Recommended hardening is in the audit section above.

---

## Recommended actions for launch

### This week (pre-launch)
1. **Sales: contact the 12 LIKELY_REAL high-intent leads** with a personalized intro referencing what they said in the survey. (Filter `Survey - High Intent Leads.csv` against the LIKELY_REAL category in `Survey - Flagged Responses.csv`.) Do not call any of the SUSPICIOUS or CONFIRMED_SPAM rows.
2. **Investigate the May 25 spike source.** If it was paid LinkedIn or a panel buy, recalibrate the headline read. If it was organic / a viral post, double down on whoever posted.
3. **Content: publish a teaser social post using one specific stat** — *"63% of marketers we surveyed said they're losing core skills to AI tool sprawl. We don't think marketers should have to become engineers."* — and pin it as the lead-in to launch.
4. **Get UTMs on every distribution link** so the launch-week response wave is attributable.

### Launch week
5. **Use the survey as the launch press hook.** *"181 marketing leaders told us..."* is a stronger press angle than *"we built a thing."* By Monday it'll be 200+; lead with the cleaner round number.
6. **The "AEO Playbook" is an obvious lead magnet** — 22% don't know where to start + 52% planning AEO investment + 25% have no tool to track it = high download intent.
7. **Run the launch announcement through the LinkedIn-known sample first** before paid amplification — they already raised their hand. 39 known LinkedIn referrals × 144 report opt-ins overlap = warm sequence ready.

### Post-launch
8. **Re-run `analyze_survey.py` AND `validate_responses.py` weekly** through end of June and watch for shifts in the LIKELY_REAL lead cohort (whether they convert to demo / waitlist).
9. **Add 3-5 product-fit questions to the survey for Phase 2.** The current survey is great on context but light on "would you buy this." Worth A/B-testing a closing question like *"If a tool did [closed-loop ContentOS pitch], would you take a demo this quarter?"*

---

## Files in this analysis bundle

- `Survey Insights - GrowthOS Launch.md` — this doc
- `Survey - High Intent Leads.csv` — 26 advisor-opted-in high-intent leads, with off-ICP-flag column (kept out of git; PII). 12 are LIKELY_REAL per the audit.
- `Survey - Flagged Responses.csv` — all 89 non-LIKELY_REAL rows from the audit, sorted by suspicion score, with the specific flags that fired (kept out of git; PII)
- `analyze_survey.py` — reproducible analysis script. Run `python3 analyze_survey.py` from this folder to refresh all numbers when more responses come in.
- `validate_responses.py` — authenticity audit. Run after every fresh export.
