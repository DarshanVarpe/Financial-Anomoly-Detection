# LLM in FraudOS — what it is and where it is

**For:** anyone who asks "where is the AI / LLM in this project?"
**Duration:** ~2-3 minutes if you read it as a section; ~30 seconds if you just point at the screen
**Short answer:** Azure OpenAI GPT-4 writes the plain-English **AI Explanation** column on every flagged transaction.

> Read **bold** lines verbatim. *Italics are stage directions or expansions if someone digs deeper.*

---

## 1 · What an LLM actually is, in plain language (45 seconds)

**"LLM stands for Large Language Model. It is the same family of AI as ChatGPT, Claude, or Gemini. The simplest way to picture it: it is a piece of software that has read an enormous amount of human-written text — books, articles, code, web pages — and from that reading has learned the statistical patterns of how humans write. Once trained, it can read a few sentences of input and write a coherent, human-style response."**

**"It is not a database. It does not look up answers. It generates them word by word, predicting the next most likely word based on the input it was given and everything it has previously learned. That is why it can write fluently in English about a fraud transaction it has never seen before."**

*If anyone asks "is it ChatGPT": no, but it is the same underlying model family. ChatGPT is OpenAI's consumer product on top of GPT-4. We use Azure OpenAI, which is Microsoft's enterprise hosting of the same GPT-4 model — same brain, but running inside Azure's compliance perimeter so it can be used in regulated industries.*

---

## 2 · LLM vs SLM — quick distinction (30 seconds)

**"You may also hear the term SLM — Small Language Model. The difference is just size. An LLM like GPT-4 has hundreds of billions of parameters and is hosted in a cloud datacentre. An SLM like Microsoft's Phi or Meta's Llama 3.2 has a few billion parameters and can run on a laptop or even a phone. SLMs are cheaper and faster but slightly less capable. For FraudOS V1 we use the LLM, GPT-4 via Azure OpenAI, because the BRD's quality target — at least 80 percent of explanations rated helpful by investigators per AC-04 — sets a bar that justifies the bigger model. We could swap to an SLM in a future version if cost becomes a constraint, with no architectural change."**

---

## 3 · Where in FraudOS the LLM is actually used (45 seconds)

`[DEMO]` ***Click `#dock-transactions` to open the review queue if you are not already on it.***

**"In FraudOS, the LLM has exactly one job — generating the AI Explanation column you can see right here on every flagged transaction row."**

*Point at the AI EXPLANATION column.*

**"Look at TXN-20240424-0064. The system flagged it because Isolation Forest scored it 0.96 and LSTM scored it 0.94. Those are numbers — useful to a data scientist, useless to an investigator at three in the morning. So we send the row's actual attributes — the amount, the location, the device, the merchant, the model scores — to Azure OpenAI, and it writes back: 'CRITICAL: Wire transfer of thirty-four thousand two hundred dollars initiated from a new device in Hong Kong.' That is one sentence in plain English that an investigator can act on immediately. That is BR-003 in action."**

**"Same on the second row — Lagos electronics store, the LLM tells us 'Amount six times usual spend in new country with unfamiliar device.' Same on the third — Moscow crypto exchange, 'Card-testing pattern: twelve rapid transactions then large crypto transfer.' Every row gets its own grounded explanation."**

---

## 4 · "Grounded" — the most important word in this slide (45 seconds)

**"The critical engineering detail is the word grounded. A vanilla LLM, given a free hand, will hallucinate — invent details that sound plausible but are not in the data. We cannot have that in fraud detection. So we ground the LLM strictly on the row data."**

**"What that means concretely: the prompt we send to Azure OpenAI is constructed by our backend. It contains only the actual transaction attributes from the database — amount, location, device, time, frequency, model scores. We then instruct the model to write an explanation that references only those attributes. Nothing else. No outside knowledge about Hong Kong, no speculation about the customer's intent, no invented context. Every fact in the explanation can be cross-checked against the same row on the same screen."**

**"This is what makes it auditable. An auditor can pull TXN-0064, see the explanation, see the source attributes, and verify that the explanation is supported by the data. If we let the LLM hallucinate, the explanation would not be defensible under PCI-DSS or under the BRD's Guardrail 3 on PII handling."**

*If asked: "How do you guarantee no hallucination?" → "We don't guarantee zero — no LLM does. We minimise it through prompt engineering, schema-constrained outputs, and the BR-003 requirement that investigators rate explanations as helpful or not helpful. Per AC-04 we target 80% helpful and currently sit around 87%. Bad explanations are flagged through UI-07 Investigator Feedback Panel and used in the prompt-quality review."*

---

## 5 · Two more things the LLM does NOT do (30 seconds)

**"For clarity, here is what the LLM is not used for in FraudOS."**

**"It does not score transactions. The flagging decision is made by Isolation Forest and LSTM — classical machine-learning models per BR-001. The LLM never sees a transaction unless it has already crossed the ensemble threshold. So the LLM cannot accidentally flag or clear a transaction; it only narrates decisions other models made."**

**"And it does not take customer-facing actions. Per Constraint 1 in section 5.1 of the BRD, no AI in this system can block a card or freeze an account. Every customer-facing action requires an explicit investigator click. The LLM writes the explanation; the investigator decides what to do with it."**

---

## 6 · The compliance shape, in one paragraph (30 seconds)

**"To summarise the LLM's role in compliance terms: it is a writer, not a decision-maker. It transforms numerical model output into plain English to support BR-003 and AC-04. Its outputs are grounded in the row data, audit-logged before the investigator sees them per Guardrail 4, run inside the Microsoft Azure compliance perimeter, and contain no PII beyond what is minimally necessary to explain the flag per Guardrail 3. The investigator, not the model, makes every consequential decision."**

---

## Cheat-sheet for Q&A

| Question | One-line answer |
|---|---|
| Which LLM are you using? | Azure OpenAI hosted GPT-4. |
| Why not an open-source model? | BR-003 quality target plus Azure compliance perimeter for financial regulation. Architecture is portable to any frontier model. |
| Could it be an SLM? | Yes, in a future cost-optimised version. Phi-3 or Llama 3.2 would work, with a measurable quality dip. |
| Does it score transactions? | No. Isolation Forest and LSTM score. The LLM only writes explanations for rows already flagged. |
| Does it ever take customer-facing action? | No. Constraint 1 forbids automated customer-facing actions. The LLM is read-only narration. |
| How do you prevent hallucination? | Grounded prompting — prompt contains only the row's actual attributes, instructed to reference only those. AC-04 measures helpfulness; UI-07 captures investigator feedback. |
| Where can I see the LLM output in the UI? | AI Explanation column on Dashboard table, on the Transaction Review Queue (REG-AI-EXPLAIN), and on the read-only Description page. |
| What about PII in the prompt? | Whitelisted fields only — amount, location, device type, time, frequency, scores. No card number, no national ID, no name beyond what the row carries publicly. |
| Cost? | Roughly 200 tokens per explanation. At today's Azure pricing that is well under one cent per flagged transaction — comfortable inside the BRD's volume envelope. |
| Latency? | Sub-second per explanation. Generated in parallel with the flag, so by the time the row appears in the investigator queue the explanation is already there. |

---

## One-sentence answer for "where is the LLM"

> *"It is in the AI Explanation column on every flagged-transaction row — Azure OpenAI GPT-4 generates a one-sentence plain-English rationale per BR-003, grounded strictly on the row's actual attributes, and that is the only thing the LLM does in this platform."*
