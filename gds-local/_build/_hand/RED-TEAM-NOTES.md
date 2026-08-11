# Red-team analysis: LGAM strengths, weaknesses, and tensions

## 1. What the model is

The LGAM as published describes itself as "a shared framework that provides a consistent way to understand, describe, and align how local government technology supports service delivery and the overall operation of a council." It contains 9 layers arranged vertically:

1. **Public Channels** — how citizens reach the council
2. **Council Interfaces** — what the council presents to users
3. **Capabilities** — reusable functional tools (Payments, Forms, Identity, Workflow, etc.)
4. **Business Areas** — statutory service domains (Planning, Housing, ASC, etc.)
5. **Corporate Areas** — non-statutory support functions (HR, Finance, GIS, etc.)
6. **Foundational Technology** — 5 sub-domains (AI, DevOps, End User, Service Management, Infrastructure)
7. **Integration** — connecting systems and data
8. **Security** — protecting people, data, systems
9. **Data and Information** — managing data assets

The intended audiences (from the introduction) are GDS, government departments building for councils, councils themselves, and vendors.

---

## 2. What kind of thing is it?

This is the fundamental identity question. The model occupies an uncomfortable space between several established genres:

### As a **technical reference model** (TRM)
A TRM catalogues technology categories to create shared vocabulary. TOGAF's TRM does this — it names platforms and standards without prescribing implementations. The LGAM's lower layers (FT, Integration, Security, Data) function this way: they enumerate what technology exists in councils. **Strength:** shared vocabulary is genuinely valuable in a fragmented sector with 300+ organisations. **Weakness:** a pure TRM doesn't tell you what to do, what to prioritise, or what good looks like.

### As a **business capability model**
The top layers (Channels → Interfaces → Capabilities → Business Areas) read more like a business capability map: they describe *what a council does* in terms the business side would recognise. **Strength:** traces the citizen journey end-to-end. **Weakness:** the narrative breaks at Foundational Technology, which doesn't participate in citizen interactions.

### As an **enterprise architecture framework**
EA frameworks (TOGAF, ArchiMate) provide viewpoints, relationships, governance, and maturity. The LGAM doesn't do this. It names things but doesn't describe how they compose, depend on each other, constrain each other, or get governed. A CTO can't use this to assess their estate because there's no maturity model, no dependency map, no "here's what good looks like."

### As a **service delivery model**
The original LGAM intent — and its greatest strength — was to trace how technology supports service delivery. You *can* follow a citizen interaction from Channel → Interface → Capability → Business Area. This makes the top layers genuinely useful for explaining "how technology fits around what we do." But this framing doesn't extend downward: Infrastructure & Hosting doesn't "support" a Business Area the same way Payments does.

### What it actually functions as

In practice, the LGAM is a **hybrid taxonomy**: part business capability map (top), part technology reference catalogue (bottom). Its primary value is as shared vocabulary — giving diverse stakeholders a common language for talking about council technology. This is not a criticism. Shared vocabulary in a sector with 300+ autonomous organisations and endemic fragmentation is genuinely hard and genuinely useful.

---

## 3. Structural tensions

### Tension A: The service delivery narrative vs the technology catalogue

The top 5 layers tell a story: a citizen reaches the council (Channel), encounters an interface (Interface), which uses a tool (Capability), to support a service (Business Area), run by corporate functions (Corporate Area). This is elegant and intuitive.

The bottom layers (Integration, Security, Data) are a flat catalogue: here are categories of technology councils have. They don't participate in the narrative. A reader who understood the model via the top half expects to keep following the story downward — and finds a list instead.

**Note:** the context map already partially addresses this. Foundational Technology is presented as a vertical pillar alongside the full stack — not as a layer beneath. This is a more honest spatial metaphor: FT underpins and runs alongside everything. But Integration, Security, and Data are still presented as horizontal bands at a specific level, despite being equally pervasive. The visual design has already solved this problem for one element (FT) but not for the other three.

**Why the remaining tension matters:** presenting Integration/Security/Data as horizontal layers *below* Business Areas implies they exist at a specific level in a hierarchy. But security constraints apply *at* the Channel layer (HTTPS, cookie policy), *at* the Capability layer (payment card compliance), *at* the Business Area layer (data protection in social care), and everywhere else simultaneously. The horizontal positioning suggests "this is what sits beneath the services" when the reality is "this is what governs everything."

**Possible resolution:** acknowledge the model has two registers — a service delivery architecture (top) and a technology estate map (bottom) — and present them with appropriate framing for each. Or consider whether Integration/Security/Data deserve the same "vertical pillar" treatment that FT already has — presented as spanning the full height rather than sitting at a specific depth.

### Tension B: Layers vs cross-cutting concerns

The context map already treats Foundational Technology differently — as a vertical pillar spanning the full stack. This visual decision implicitly acknowledges that FT underpins everything rather than sitting at one level. It's a good decision.

But Integration, Security, and Data are still presented as horizontal bands. The question is: do they deserve the same "pillar" treatment? The argument is strong:

- **Security** isn't below Business Areas — it's *applied to* every layer. HTTPS at the Channel layer, PCI-DSS compliance at the Payments capability, data protection at the ASC business area, network segmentation at Infrastructure.
- **Data** isn't below Integration — data flows *through* integrations, gets *stored* in infrastructure, gets *consumed* by capabilities, gets *produced* by business areas.
- **Integration** exists wherever two systems need to talk — which is at every boundary in the model. The Integration *platforms* (Boomi, MuleSoft, Azure Service Bus) absolutely are things you procure and operate. But the Integration *concern* touches every inter-layer connection.

**Counter-argument for keeping them horizontal:** making everything a vertical pillar risks the model collapsing into a formless blob where "everything connects to everything." The horizontal presentation at least gives the reader a linear path through the content. There's a navigation benefit to the current design even if it's slightly spatially dishonest.

**The real question:** is the horizontal positioning confusing anyone in practice, or is it a theoretical impurity that readers accept without difficulty? This might be something to test with users — do they interpret the lower position as "less important" or "more foundational"?

### Tension C: Consistent granularity

The layers vary significantly in granularity:

- **Public Channels** has 10 items, all at the same level (concrete interaction modes)
- **Capabilities** has 9 items, all functional tools
- **Business Areas** has 12 items, each a major service domain
- **Foundational Technology** has 5 sub-domains, each with 2-5 sub-items (17 total)
- **Integration** has 7 items mixing pattern types (event-driven) with tool categories (API management) with process concerns (governance)
- **Security** has 7 items mixing operational capabilities (SOC) with tool categories (IAM) with physical infrastructure (badge systems)
- **Data and Information** has 8 items mixing platforms (data warehousing) with disciplines (data governance) with outputs (BI/analytics)

Within Foundational Technology, the sub-domains are at different levels of abstraction: "Infrastructure & Hosting" is a massive operational domain (compute, storage, networking), while "Service Management" is narrower (ITSM, portfolio, licensing). "AI" is a technology paradigm; "End User and Productivity" is a workplace concern.

**This is not unusual for models at this stage** — they grow organically — but a reader expecting consistent "level of zoom" across the model won't find it.

### Tension D: The model names domains of concern, not just technology

A tempting way to make sense of the LGAM's structure is to distinguish "things councils operate" (platforms, tools) from "architectural disciplines" (practices, governance). Under this reading, Integration and Security would be disciplines, while Infrastructure and End User would be platforms. But this doesn't survive contact with reality — every domain in the model contains both:

| Domain | Platforms you operate | Practices you exercise |
|---|---|---|
| Integration | API gateway (Apigee, Kong), integration platform (Boomi, MuleSoft), message broker (Azure Service Bus) | Integration governance, pattern selection, API lifecycle management |
| Security | SIEM (Sentinel, Splunk), IAM platform (Entra ID), EDR (CrowdStrike) | Vulnerability management, incident response, security architecture |
| Data and Information | Data warehouse (Snowflake, Synapse), BI platform (Power BI), metadata catalogue (Alation) | Data governance, data quality, stewardship, retention policy |
| Service Management | ITSM platform (ServiceNow, Freshservice), CMDB | Incident management, change management, SLA governance |
| DevOps | CI/CD pipelines (Azure DevOps, GitHub Actions), monitoring (Grafana, Datadog) | Release management, SRE practices, deployment strategy |

The same holds for the upper layers. "Workflow" is both a platform you buy (Camunda, K2) and a design discipline (process engineering, service design). "Forms" is both a tool (GOV.UK Forms, Jotform) and a practice (form design, progressive disclosure, validation logic).

**What this means for the model's identity:** the LGAM is best understood as naming *domains of concern* rather than cataloguing either technology or practice. Each domain encompasses tools, platforms, skills, governance, and standards. This is the right level of abstraction for a sector-wide reference model — it tells you "this is a thing you need to think about" without prescribing whether you approach it primarily as a procurement decision or a capability-building exercise.

**Where this creates a content design challenge:** the item descriptions on the published page lean toward the tooling side ("platforms for...", "tools to...", "systems for..."). This framing is natural and concrete, but it risks communicating that the model is a technology shopping list. A council CTO might read "Integration governance and tooling" and think "that's the iPaaS procurement category" rather than "that's the discipline of designing how our systems talk to each other." Both readings are valid, but the model currently signals the first more strongly.

---

## 4. Specific structural questions

### Should Integration, Security, and Data be inside or outside Foundational Technology?

The context map already positions FT as a vertical pillar, visually separate from the horizontal stack. Integration, Security, and Data sit as horizontal layers below Business/Corporate Areas. The distinction isn't made explicit in text — it's communicated purely through visual layout.

**Arguments for keeping Integration/Security/Data as horizontal layers:**
- They are genuinely cross-cutting in a way that FT sub-domains aren't. But the horizontal format gives readers a linear path through content — easy to scroll, easy to navigate.
- Organisationally, Security and Data often report through different governance structures (CISO, CDO) than FT sub-domains (CTO/IT Director). Separate sections reflect real organisational boundaries.
- Separating them signals their importance — collapsing them into FT risks making them seem subordinate.

**Arguments for giving them the same "pillar" treatment as FT:**
- Each contains platforms councils procure and operate (SIEM, API gateway, data warehouse), just like FT contains Infrastructure. The distinction isn't "FT is operational, these are conceptual" — they're all operational.
- The horizontal positioning implies they sit at a specific depth in the architecture. This confuses the reader who asks: "why is Security below Integration? Is there a hierarchy here?" There isn't — the ordering is arbitrary.
- ArchiMate handles analogous concepts (motivation, strategy) as perspectives that apply across layers, not as layers at a specific position.

**Arguments for merging them into FT entirely:**
- A CTO reading the model for estate coverage might expect all technology categories to appear together under one "technology" heading.
- It simplifies the visual and reduces the number of distinct architectural concepts the reader must hold.
- But: this risks under-signalling the importance of Security and Data governance, which deserve strategic prominence not subordination.

**Open question:** the current context map design chose well for FT. Did it stop short? Or is there a good reason these three sit horizontally that the visual design already communicates (perhaps: "these are the substrate beneath everything, while FT is the machinery alongside")?

### Is "Foundational Technology" the right grouping?

The 5 things inside FT are: AI, DevOps, End User & Productivity, Service Management, Infrastructure & Hosting.

What do these share? They're all *internally-facing technology the IT team manages for staff and systems* (not citizen-facing, not about a specific service domain). This is a reasonable grouping — it's roughly "IT department scope" — but it's never stated this way.

Problems:
- "AI" is a technology paradigm that applies everywhere, including citizen-facing services. Why is it under FT and not a cross-cutting concern like Security?
- "Service Management" (ITSM) is narrower than the others — it's really one tool category (ServiceNow-type platforms) plus some process. It sits alongside "Infrastructure & Hosting" which is massive.
- "End User and Productivity" mixes devices (hardware) with collaboration tools (Teams, SharePoint) with knowledge management. These serve very different audiences at different levels.

### Where are the IT Systems?

The model names Business Areas (Planning, Housing, ASC) and names Capabilities (Payments, Forms, Workflow) — but it doesn't name the systems that actually deliver these services day-to-day. There's no "Planning System" or "CRM" or "Social Care System" in the published model. The model describes the context *around* systems (channels, capabilities, infrastructure) but not the systems themselves.

This may be deliberate — specific systems are too numerous, council-specific, and market-sensitive to list generically. Including them risks the model becoming a procurement directory or appearing to endorse particular vendors. But it creates an odd gap for the CTO audience: the model helps them think about *what categories of concern they have* but not *what their actual estate contains*. The reader has to make the mental connection between "Workflow capability" and "this is where our Firmstep/Granicus platform sits" themselves.

---

## 5. User need framing: who is this for?

| User | They come to the page to... | What they need from it |
|---|---|---|
| Council CTO/IT Director | Understand the full scope of what their estate should cover | Completeness, groupings that map to how they organise their team and budget |
| GDS product team | See where their product (Payments, Notify, One Login) fits in the council landscape | Clear placement in the taxonomy, understanding of the council context their product plugs into |
| Vendor/supplier | Understand what councils need and where their product positions | Market categories, terminology alignment, adjacent capabilities |
| Service manager | Understand how technology supports their specific service area | The service delivery layers (top 5) with enough detail to recognise their world |
| CDDO/policy | A coherent picture of LG technology to inform strategy and investment | The big picture, coverage assessment, gaps and opportunities |

**Observation:** These audiences have quite different needs. The CTO wants a checklist they can assess their estate against. The vendor wants positioning clarity. The service manager wants to trace their service. The policy maker wants strategic context. A single flat page struggles to serve all simultaneously — it optimises for breadth (covering everything) at the expense of depth (being useful for any one task).

**The deeper question for P&D work:** when we build out a Business Area subpage, which of these users are we primarily writing for? A Planning officer recognising their workflow? A CTO understanding what systems support planning? A vendor seeing where PlanX or Idox fits? These demand very different content.

---

## 6. Strengths (what the model does well)

1. **Shared vocabulary in a fragmented sector.** 300+ autonomous councils with no mandatory technology standards. Simply naming things consistently so people can have conversations is high-value work.

2. **The top-layer narrative is compelling.** Channel → Interface → Capability → Business Area tells a story that any council stakeholder can follow. It explains *why* technology exists (to serve citizens) rather than just cataloguing it.

3. **Appropriate level of abstraction for a national model.** It resists the temptation to prescribe specific products (mostly — the commented-out platform examples show this was considered and deferred). This keeps it relevant across councils of vastly different sizes and maturities.

4. **Business Areas provide a natural expansion point.** Each Business Area can become a subpage with domain-specific detail (as attempted with the P&D prototypes). This lets the model grow without the index page becoming unwieldy.

5. **Visual clarity of the context map.** The coloured-band overview communicates structure at a glance. A CTO can immediately see the scope being described.

6. **Grounded in real council organising principles.** The Business/Corporate split reflects how councils actually structure their directorates. The layers (if imperfect) reflect real boundaries in council IT governance.

---

## 7. Weaknesses and gaps

1. **No relationships or dependencies visible.** The published page is a flat catalogue. You can't trace "Payments capability depends on Integration patterns and Security controls." The layers are presented independently with no explicit connections between them. This limits the model's utility for architecture decisions.

2. **No maturity dimension.** The model tells you what *categories* exist but not what *maturity* in each area looks like. A council can't use it to self-assess. The lite-transformation prototype attempted this but it's a significant conceptual extension.

3. **No "what good looks like" per item.** Each item gets a one-line description but no guidance on architectural quality, common patterns, or anti-patterns. The `lgam_architectural_principles.md` resource captures this thinking but it's not connected to the public model.

4. **The layer metaphor is slightly dishonest for the bottom 4.** Stacking Integration/Security/Data below FT implies a hierarchy that doesn't exist. These aren't "lower" — they're orthogonal. The visual design communicates the wrong spatial relationship.

5. **Inconsistent content design across layers.** Top layers describe things in consistent, user-centred language ("capabilities used to..."). Bottom layers mix description styles between tool categories, discipline descriptions, and process definitions. This creates a subtle shift in register that signals the model was authored by different people or at different times.

6. **Corporate Areas vs Business Areas distinction is fragile.** The stated distinction ("not specific to councils") applies equally to Financial (every organisation does finance) and to Revenues & Benefits (very council-specific). The actual distinction seems to be "outward-facing statutory services" vs "inward-facing support functions" — which is useful but not what's stated.

7. **No sense of council variation.** The model presents a single universal picture. But a county council (no housing, no waste) looks structurally different from a district (no social care, no education). The model doesn't acknowledge this variation, which risks confusing smaller councils who can't recognise themselves.

---

## 8. What this means for the P&D subpages

Four prototype concepts exist for Planning & Development. They don't just differ in layout — they represent fundamentally different answers to the question "what should a business area page *be*?"

### Concept comparison

| Concept | Core proposition | Content type | User action it enables |
|---|---|---|---|
| **Hub-Lite** (published) | Domain hub + sub-pages showing which LGAM elements apply to each value stream | Card-based hub navigating to per-stream LGAM stack tables (layer, element, planning context, example technology) | "Show me which parts of the LGAM apply to development management / planning policy / building control" |
| **Hub-Max** (draft) | Detailed prescriptive technical lifecycle per value stream | Target state SVG architecture diagrams, phased accordion lifecycle (business process → legacy anti-patterns → target architecture with best practice and real-world impact), LGAM stack tables | "Show me what good architecture looks like for each phase of a planning application, and what anti-patterns to avoid" |
| **Lite-Max** (draft) | Single-page reference integrating LGA taxonomy, LGAM mapping, research evidence, and the national data platform | Function/service hierarchy from LGA Inform Plus, capability-to-LGAM-element mapping table, modernisation principles, planning data platform datasets with live API integration | "Help me understand the full landscape — services, technology, evidence for change — in one place" |
| **Lite-Transformation** (draft) | Guided self-assessment and roadmap-building framework | 5-step process (scope → map → assess → roadmap → interoperability), capability heatmap with coverage/quality/interoperability ratings, cost-of-fragmentation statistics, strategic rationalisation targets | "Help me assess my current maturity and build a plan to improve" |

### The tensions between these concepts

**1. Descriptive vs prescriptive**

The concepts sit on a spectrum. Hub-Lite is closest to purely descriptive: "here are the LGAM elements relevant to planning, here's what each one does in this context." It maps the territory without recommending a direction of travel. Hub-Max is explicitly prescriptive: it names anti-patterns to avoid, presents target state architectures, and labels best practices with "real-world impact" evidence. Lite-Max is persuasive: it builds the case for modernisation with evidence and principles. Lite-Transformation is directive: it guides you through a structured assessment process.

The LGAM index page is descriptive — it names and describes without recommending. The further along this spectrum you go, the more the P&D content diverges from the parent model's tone. That may be appropriate (business area pages arguably *should* be more opinionated than the parent taxonomy) but it raises questions about voice and authority — who is saying "this is the target architecture" and on what basis?

**2. Reference material vs active tool**

Hub-Lite, Hub-Max, and Lite-Max are reference material — you read them, absorb information, leave. They may inform your decisions but they don't structure your decision-making process. Lite-Transformation is trying to be a tool — it walks you through steps, asks you to rate your capabilities, and outputs a roadmap structure. Tools require ongoing maintenance (are the maturity criteria still right? are the example ratings realistic?), user support, and potentially personalisation. Reference material is cheaper to maintain but less directly actionable.

**3. Narrow expert audience vs broader council audience**

Hub-Max assumes a technically literate reader who understands SVG architecture diagrams, concepts like "rules-as-code engines", "event brokers (pub/sub)", "PostGIS spatial databases", and "decoupled edge registers." This is senior architect or technical lead territory. Lite-Max and Lite-Transformation use the LGA taxonomy and business language ("functions and services", "capability coverage", "cost of fragmentation") that a service manager, head of planning, or IT business partner could engage with. Hub-Lite sits in between — its hub page is accessible but its sub-pages still use technical language (LGAM stack table with layer/element/technology columns).

**4. LGAM-native vs planning-domain-native**

Hub-Lite and Hub-Max are structured *around the LGAM*. Every section maps back to LGAM taxonomy nodes (Capabilities → Workflow, Corporate Areas → Geographical, Integration → API Gateway). The content exists to explain how LGAM concepts manifest in planning. Lite-Max and Lite-Transformation are structured *around the planning domain*. They use the LGA function/service hierarchy as the primary organising principle, with LGAM elements cross-referenced where relevant. This is the difference between "here's planning viewed through the LGAM lens" and "here's planning, with LGAM as supporting context."

This tension matters for the user: a council CTO looking at the LGAM to understand their technology landscape would expect the LGAM-native framing. A head of planning service looking for guidance on their domain would expect the planning-native framing. They're different entry points into the same territory.

**5. Self-contained vs ecosystem-dependent**

Hub-Lite and Hub-Max route to sub-pages (development-management.html, planning-policy.html, building-control.html) — they're navigation hubs implying a family of detailed pages beneath. This creates a richer, more navigable resource but dramatically increases the content surface area that needs authoring, maintaining, and validating with subject-matter experts. The lite concepts are self-contained single pages. They're more manageable as a production unit but risk becoming very dense (Lite-Max and Lite-Transformation are already long, complex pages).

### The underlying strategic question

These aren't just different layouts for the same content — they express different positions on what the LGAM business area pages are *for*:

- **If the purpose is navigation and taxonomy** → Hub-Lite is the right model. It extends the index page's "here are the things" approach into domain-specific territory.
- **If the purpose is architectural guidance** → Hub-Max is the right model. It tells technical architects what target states look like and why.
- **If the purpose is building the case for modernisation** → Lite-Max is the right model. It brings evidence and urgency to convince decision-makers.
- **If the purpose is enabling self-assessment and planning** → Lite-Transformation is the right model. It turns the LGAM from a passive reference into an active tool.

These purposes aren't mutually exclusive, but they pull in different directions on tone, depth, audience, maintenance burden, and relationship to the rest of the LGAM. Choosing which one to develop further — or which elements to combine — is a product decision that should be informed by who we've decided the primary user is and what action we want them to take after visiting.
