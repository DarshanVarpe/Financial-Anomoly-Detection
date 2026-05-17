# FraudOS — AEGIS.AI · Tech Stack Walkthrough Script

**For:** the technical-stack section of the presentation
**Duration:** ~5-7 minutes
**Audience assumption:** mixed business + tech, so plain language with concrete analogies

> Read **bold** lines verbatim. *Italics are stage directions or expansion you can drop in if asked.* Each section is roughly one minute.

---

## 1 · Opening — the big picture (45 seconds)

**"Before I dive into individual technologies, here is the simplest way to think about this platform. There are six moving parts: the screen the investigator looks at, the server that answers data requests, the database that holds the records, the machine-learning models that score each transaction, the AI service that writes the explanations, and the boxes we ship everything in. I'll walk through them one by one. None of this should feel like a vocabulary test — every choice is there to solve a specific problem the BRD asked us to solve."**

*Pause briefly. Show your slide if you have one with a stack diagram, otherwise just speak it.*

---

## 2 · The frontend — what the investigator sees (1 minute)

**"The screens you saw in the demo — the dashboard, the review queue, the threshold panel — are built in React. React is the most widely used library in the world for building interactive web pages. Think of it like Lego: each screen is assembled from small reusable blocks called components. The Live Activity feed is one component, a KPI tile is one component, a transaction row is one component. When the data changes, only the affected blocks re-render. The investigator sees a dashboard that updates in real time without the whole page reloading."**

**"We use Vite as the build tool. Vite is the carpenter that takes those Lego blocks and packages them into the static files the browser actually downloads. We chose Vite over older tools like Webpack because it starts a fresh dev server in under a second, which made the build-test-fix loop fast during development."**

**"For the charts on the dashboard — the time-series of flagged transactions and the risk distribution donut — we use a library called Chart.js, wrapped for React. It is the same charting library used by thousands of finance and compliance dashboards across the industry, so the visual language will feel familiar to anyone who has used a Bloomberg or a Tableau view before."**

**"One quiet but important detail: every clickable element on the screen has a unique HTML id attribute. The Fraud button on transaction one is `id` equals `tx-one-fraud-btn`. The Approve button on threshold three is `id` equals `threshold-approve-btn-three`. That is what allowed Rahul, the virtual humanoid, to drive the entire investigator workflow autonomously, and it is what supports our Playwright automation tests."**

*If asked "why React over Streamlit when the BRD said Streamlit": Streamlit is great for analyst notebooks but cannot give per-row buttons keyed to dynamic transaction IDs without page-level reloads. React handles thousands of dynamic interactive elements without re-rendering the whole page.*

---

## 3 · The backend — the server that answers data requests (1 minute)

**"Behind the screens is a backend written in Python using a framework called FastAPI. FastAPI is the modern standard for building data APIs in Python. The reason it is called FastAPI is literal — it is fast, both for the developer to write and for the server to execute. When the dashboard needs the four KPI numbers, the frontend calls an endpoint like slash KPIs, and FastAPI answers with the live counts in milliseconds."**

**"Python was the natural choice because the data science team already works in Python — pandas for data wrangling, scikit-learn and TensorFlow for the models. Choosing FastAPI for the API layer means the backend developer and the data scientist speak the same language. There is no awkward translation between a Java service and a Python notebook."**

**"FastAPI also gives us automatic API documentation, automatic request validation, and built-in support for the asynchronous patterns we need to keep the dashboard responsive when many investigators are working in parallel."**

*If asked about authentication: BRD V1 uses session-based investigator login behind the corporate SSO, which is configurable in the agent profile card under Email ID and Diary Allow-List.*

---

## 4 · The database — where every flag and decision lives (1 minute)

**"All the persistent data sits in PostgreSQL, hosted by a managed service called Aiven. PostgreSQL is the most trusted open-source relational database in the financial industry — banks have used it for decades. Aiven runs it for us as a fully managed cloud service so we do not have to babysit hardware. They handle backups, replication, failover, and the seven-year retention required by NFR-03 in the BRD."**

**"What is in the database? Every transaction, every flag, every model score, every investigator decision, every audit log row, and every threshold change. The BRD requires that 100 percent of these are captured per AC-08, and that they are retained for at least seven years per the financial regulatory requirements in NFR-03. PostgreSQL handles that volume comfortably and gives us the SQL audit-query interface that compliance teams expect."**

**"The BRD originally referenced Azure Synapse for the big-data pipeline — that is for the upstream data lake where the raw transaction stream lands before our models score it. Synapse is Microsoft's cloud-scale data warehouse. PostgreSQL holds the application's working set; Synapse holds the historical archive that retraining pulls from."**

*If asked about scale: NFR-02 calls for 5 million transactions per day with up to 2x peaks. PostgreSQL with Aiven's standard tier is sized comfortably for that volume.*

---

## 5 · The ML models — the brains (1.5 minutes)

**"Now the most interesting part — the brains of the system. Per BR-001, we use two different machine-learning models on every transaction, and combine their scores."**

**"The first is Isolation Forest. The simplest way to think about Isolation Forest is this: imagine sorting a deck of playing cards and asking how many cuts it takes to isolate a single card. A typical card needs many cuts. A weird outlier — say a card from a different deck — gets isolated in just two or three. Isolation Forest does that with transaction data instead of cards. A normal customer purchase needs many splits to isolate; a thirty-four thousand dollar wire from a brand-new device in a brand-new country isolates almost immediately. The number of splits becomes the anomaly score. We implement this with scikit-learn, the standard Python machine-learning library."**

**"The second model is an LSTM — long short-term memory. This is a neural network designed to spot patterns over time. Where Isolation Forest looks at a single transaction in isolation, LSTM looks at sequences. Twelve rapid micro-transactions in three minutes followed by one large crypto purchase is a classic card-testing pattern that LSTM picks up but Isolation Forest misses. We implement this with TensorFlow and Keras."**

**"Then we ensemble them. Each model produces an independent score between zero and one. We combine those scores with configurable weights to produce a single ensemble score. If the ensemble score crosses 0.80, the transaction is flagged for investigator review. This is exactly what BR-001 specifies — every transaction goes through both models, and a configurable ensemble produces the final decision."**

**"All three models — Isolation Forest, LSTM, and the ensemble — are hosted on Azure ML, which is Microsoft's cloud service for deploying and serving ML models. Azure ML handles model versioning, automatic scaling, and the retraining cycle that BR-002 calls for."**

*If asked why two models instead of one: a single model captures one kind of pattern; two complementary models cover both point anomalies and sequential anomalies. The BRD requires this and the metrics confirm it — Isolation Forest alone has 92% FP rate; the ensemble gets to 21.6%.*

---

## 6 · The explanation layer — Azure OpenAI (1 minute)

**"Per BR-003, every flagged transaction needs a plain-English explanation. The investigator should not have to read model output or interpret an anomaly score — they should get a sentence that says, in plain language, why this transaction was flagged."**

**"For that we use Azure OpenAI, which is Microsoft's enterprise-grade hosting of GPT-4. The same large language model that powers ChatGPT, but running inside Microsoft's compliant Azure environment with the security and data-residency guarantees that financial regulation requires."**

**"Critically, the explanation engine is grounded. We do not let the model invent context. The prompt only contains the actual transaction attributes — amount, location, device, frequency, and the model scores — and we instruct the model to write an explanation that references only those attributes. So when you saw the explanation 'CRITICAL: Wire transfer of thirty-four thousand two hundred dollars initiated from a new device in Hong Kong,' every fact in that sentence is taken from the row data. No hallucination. The investigator can cross-check every claim against the same row on the same screen."**

**"The compliance benefit of grounding is real: under PCI-DSS and GDPR, we cannot have an AI making up customer details. Grounding makes the explanation engine auditable."**

*If asked about LLM cost: Azure OpenAI charges per token. The token budget per explanation is around 200 tokens, well within the cost envelope for the daily transaction volume specified in NFR-02.*

---

## 7 · The boxes — Docker and Kubernetes (1 minute)

**"Now how do we actually ship this. The backend, the frontend, and the dependencies all run inside containers — these are the standard packaging unit for modern software, built with Docker. Each container is a sealed, portable bundle that includes the application code and every library it needs, so the version that runs on a developer laptop is byte-identical to the version that runs in production. No more 'it works on my machine' surprises."**

**"In production we run those containers on Kubernetes, which is the industry standard system for orchestrating containers at scale. Kubernetes handles starting containers when traffic increases, restarting them if they crash, routing requests to healthy instances, and rolling out new versions without downtime. The platform is currently deployed on Microsoft's managed Kubernetes service behind the Kubernetes Ingress controller, which is what handles the production URL `134.33.132.134` slash `rahul-aegis-fe`."**

**"Inside each frontend container we run Nginx as the web server. Nginx is the most-deployed web server in the world — fast, hardened, and battle-tested. It serves the React static files to the browser and proxies API calls through to the FastAPI backend."**

*If asked about CI/CD: the deployment pipeline builds the container images, pushes them to a private registry, and Kubernetes pulls and rolls out the new version. Database migrations are applied separately before deployment.*

---

## 8 · The automation layer — Playwright (45 seconds)

**"One last piece. Every interactive element on the screen has a unique HTML id, and that lets us drive the platform programmatically with a tool called Playwright. Playwright is a browser automation library — same family as Selenium, but modern. It scripts a real Chromium browser to click buttons, fill forms, and read screen content the same way an investigator would."**

**"We use Playwright for two things. First, end-to-end testing — every release runs the full investigator flow as an automated test before going live. Second, the virtual humanoid Rahul. The thirty-nine selectors in the tour JSON we walked through earlier are all real Playwright targets — Rahul can perform the entire fraud investigation flow autonomously, with the narration grounded in the BRD spec."**

*If asked about test coverage: every BR-001 through BR-006 has a corresponding Playwright test path. Every UI-01 through UI-07 has a smoke test. AC-08 audit log completeness is validated with a database query after the Playwright run.*

---

## 9 · Why these choices, in one line each (30 seconds)

**"To summarise the why. React because the investigator needs a fast, responsive interface with thousands of dynamic interactive elements. FastAPI because the data science team already lives in Python. PostgreSQL because financial regulators trust it. Isolation Forest plus LSTM because point and sequential anomalies need different detectors. Azure OpenAI because the explanation has to be grounded and compliant. Docker and Kubernetes because the platform must scale to five million transactions a day with ninety-nine-point-nine percent uptime. Playwright because every flow has to be testable end to end."**

---

## 10 · Close (15 seconds)

**"Every technology in the stack maps to a specific requirement in the BRD. Nothing is there because it is fashionable. Each piece earns its place by solving a problem the fraud and risk team would otherwise have to solve manually."**

*Pause. Open the floor for questions.*

---

## Cheat-sheet table — keep this in front of you for Q&A

| Layer | Tech | One-line role | BRD reference |
|---|---|---|---|
| Frontend UI | React + Vite | Build the investigator screens | UI-01 to UI-07 |
| Charts | Chart.js | Time-series and donut on the dashboard | UI-02 |
| Backend API | FastAPI (Python) | Serve KPIs, transactions, threshold updates | BR-006, NFR-01 |
| Database | PostgreSQL on Aiven | Persistent store for flags, decisions, audit | AC-08, NFR-03 |
| Big-data pipeline | Azure Synapse | Daily transaction batch ingest | Daily Workflows step 1 |
| Anomaly model 1 | Isolation Forest (scikit-learn) | Point-anomaly detection | BR-001 |
| Anomaly model 2 | LSTM (TensorFlow / Keras) | Sequential pattern detection | BR-001 |
| Model hosting | Azure ML | Score and retrain at scale | NFR-02, Model Retraining Gate |
| Explanation engine | Azure OpenAI (GPT-4) | Plain-English rationale per flag | BR-003, AC-04 |
| Container runtime | Docker | Portable, byte-identical builds | NFR-04 |
| Production orchestration | Kubernetes (AKS) | Scaling, rollouts, healing | NFR-02, NFR-04 |
| Web server | Nginx | Static asset serving + API proxy | NFR-01 |
| Automation / testing | Playwright | End-to-end flow validation | AC-08, AC-09 |

---

## Likely Q&A

**"Why not a single super-model that does both point and sequential detection?"**
> *"You can train one — there is research on hybrid architectures — but you lose interpretability. With two specialist models we can tell the investigator 'this was flagged on the LSTM at 0.91, the Isolation Forest only saw 0.42' and they immediately understand the pattern is temporal not point-wise. That signal is in the per-row scores you saw on the queue. A single model gives you one number; two models give you a story."*

**"What stops a developer from changing a model threshold without approval?"**
> *"Two safeguards. One, the Threshold Configuration panel has the Admin Role Active gate per UI-04 — without that badge every Approve button is disabled in the UI. Two, even with the badge, the back-end API rejects threshold changes that would push recall below 95 percent per Constraint 3. Both are enforced server-side, not just in the UI, so a developer pointing curl at the API gets the same rejection."*

**"How is the LLM kept from leaking customer PII?"**
> *"Guardrail 3 in the agent profile card. The prompt sent to Azure OpenAI is constructed by our backend from a whitelist of fields — transaction amount, location, device type, time, frequency. It never includes the full card number, the cardholder name, the national ID, or any field the BRD marks PII. Azure OpenAI also runs in our Azure tenant under the data-residency guarantees Microsoft signs in their enterprise contract, so prompts and completions are not used to train shared models."*

**"What if Aiven goes down?"**
> *"Aiven offers 99.99 percent SLA with automatic failover to a hot standby. Our backend has a connection pool with retry on transient failures. If Aiven is fully unreachable, the dashboard shows the cached state and the investigator sees a banner. The same containers run identically on a self-hosted PostgreSQL instance if we ever need to migrate — Aiven is a managed deployment of stock PostgreSQL, no proprietary lock-in."*

**"Could you replace Azure OpenAI with another LLM?"**
> *"Yes — the explanation prompt is grounded and the output is structured, so any frontier model with similar quality (Claude, Gemini, Llama 3.1 70B) produces equivalent explanations. We chose Azure OpenAI because the BRD scopes this to a Microsoft Azure environment and the Microsoft enterprise agreement is already in place. Switching providers would be a configuration change, not a rewrite."*
