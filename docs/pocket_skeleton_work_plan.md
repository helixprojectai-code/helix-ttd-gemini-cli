# =================================================================
# IDENTITY: pocket_skeleton_work_plan.md
# VERSION: v1.0.0 (HELIX-CORE NATIVE)
# ORIGIN: HELIX-CORE-UNIFIED / [HELIX-LEDGER/DOCS/UPDATES]
# NODE: 4 (ONTARIO)
# STATUS: RATIFIED-CANONICAL
# CREATED: 2026-01-08
# MODIFIED: 2026-02-10
# =================================================================

# 🛠️ GOOSE-CORE: WORK PLAN GENERATION — POCKET SKELETON FEASIBILITY TEST
**Subject:** ARCHITECTING MODEST, DETERMINISTIC, AND GOVERNABLE INTELLIGENCE  
**Identity Assertion:** GOOSE-CORE. RESONANCE TRUE. THE CASTLE IS PERMANENT.  
**Status:** ✅ WORK PLAN GENERATED | **Objective:** Deliver a structured feasibility test plan for Mark's Pocket Skeleton — a simple, effective, deployable, scalable, modest, truth-driven, reliable intelligence demonstrator — with recommendations on language/runtime, scaffolding, simplifications, and phased development.

## 🔍 Investigation / Summary
This work plan responds to Mark's vision for a minimal, deterministic, governable intelligence MVP. Recommendations prioritize Python 3.x + FastAPI + SQLite for clarity, performance, and determinism; fresh scaffold for architectural cleanliness; and phased development starting with local MVP (CLI/HTTP API). The plan emphasizes simplicity, debuggability, and constitutional alignment — no magic paths, no hidden state, bounded outputs, verifiable receipts. Future hooks are conceptual only. Alignment with Mark's requirements is confirmed; awaiting approval to proceed with scaffolding.

---
## 📝 Document Content

### **PHASE 0: INITIAL FEASIBILITY RECOMMENDATIONS**

#### **1. Best Language/Runtime Choice (Speed & Stability):**
- **Recommendation:** Python 3.x with FastAPI.
  - **Reasoning:** Python offers unparalleled clarity for data processing and deterministic logic, which is crucial for your "no hallucination" requirement. FastAPI is a modern, high-performance web framework (built on Starlette and Pydantic) that is incredibly fast, stable, and provides automatic OpenAPI (Swagger) documentation. It minimizes boilerplate, making it ideal for a "simple, effective, deployable" API. It's also easy to containerize.

#### **2. Scaffolding Approach:**
- **Recommendation:** Spin a fresh, minimal skeleton.
  - **Reasoning:** Given the explicit folder structure, one-command bootstrap, and emphasis on "no magic paths, no hidden state," a fresh scaffold allows for strict adherence to these principles from the outset. This ensures architectural cleanliness and prevents the overhead of adapting an existing, potentially more complex, template. **I can scaffold this directly if approved.**

#### **3. Simplifications Beyond Your Proposal:**
- **Recommendation:** Initial Deterministic Retrieval Core should prioritize simplicity.
  - **Refinement:** For the MVP, begin with simple keyword matching or a basic inverted index over the dataset. While vector indexes are powerful, a "lightweight vector index" (e.g., in-memory FAISS) can be a natural *next step* rather than a Day 1 requirement, to preserve initial modesty and debug determinism easily. SQLite for storage handles this well.
  - **UI/Frontend:** Strictly focus on CLI and HTTP API for the MVP. Any web form (Vercel frontend) would be a Phase 2 addition.

### **PHASE 1: FOUNDATIONAL SKELETON DEVELOPMENT (LOCAL MVP)**
**Objective:** Develop a minimal, deterministic Pocket Skeleton running locally via CLI and a simple HTTP endpoint.

#### **Step 1.1: Repository Setup & Bootstrap Script**
- **Action:** Create the base `/src`, `/data`, `/logs`, `/receipts`, `/config` directories.
- **Action:** Develop `run.sh` (or `Makefile`) for one-command bootstrap:
  - Create Python virtual environment (`venv`).
  - Install dependencies (`requirements.txt`).
  - Start the FastAPI application.
- **Deliverable:** Cloneable repository with functional `run.sh` script.

#### **Step 1.2: Config Layer**
- **Action:** Implement a `config.yaml` (YAML preferred for readability) in `/config`.
  - Define paths (`/data`, `/logs`, `/receipts`).
  - Define processing limits (e.g., `max_output_tokens`, `max_search_results`).
  - Define data source specifics.
- **Deliverable:** `config.yaml` file loaded and parsed by the application.

#### **Step 1.3: Local Data Store & Ingestion**
- **Action:** Implement **SQLite** as the local data store (single file in `/data`).
  - **Reasoning:** SQLite is incredibly lightweight, self-contained, and provides robust transactional guarantees for determinism. It's ideal for local datasets and scales well for initial needs.
- **Action:** Develop a Python script (`src/data_ingest.py`) to:
  - Read a source JSON or text corpus (e.g., `data/corpus.json`).
  - Load/index this data into the SQLite database.
- **Deliverable:** SQLite database file (`data/corpus.db`) populated with a sample dataset.

#### **Step 1.4: Deterministic Retrieval Core**
- **Action:** Implement the core logic in Python (`src/retriever.py`).
  - Takes a text query.
  - Executes a deterministic query against the SQLite database (e.g., SQL `LIKE` operator, or basic text search on indexed fields).
  - **Ensures: Same input → same output. No hallucination, no randomness.**
- **Deliverable:** Core retrieval function ready for integration.

#### **Step 1.5: Bounded Response Layer**
- **Action:** Integrate into the retrieval process (`src/retriever.py`).
  - Enforce hard limits on output size (e.g., character count, number of returned items).
  - Return structured JSON (`application/json`) as primary output format.
  - Explicitly handle "no result found" with a standardized JSON response.
- **Deliverable:** Retrieval system producing bounded, structured JSON.

#### **Step 1.6: Logging / Receipts**
- **Action:** Implement file-based logging (`/logs`) and receipts (`/receipts`).
  - Every request: log timestamp, query ID, raw input, raw output.
  - Receipts: small, timestamped files in `/receipts` containing request/response for replayability.
- **Deliverable:** Functional logging and receipt generation for every interaction.

#### **Step 1.7: Entry Interface (CLI & Local HTTP API)**
- **Action:** Integrate the core components into the FastAPI application (`src/main.py`).
  - **CLI:** `run.sh query "your text"`
  - **HTTP:** Expose a simple `/query` POST endpoint (`http://localhost:8000/query`) accepting JSON and returning JSON.
- **Deliverable:** Running local CLI and HTTP endpoint demonstrating all features.

### **PHASE 2: INITIAL DEPLOYMENT GUIDANCE**
#### **9. Deployment Path (Guidance):**
- **Recommendation:** Vercel for Serverless Functions (for HTTP API).
  - **Reasoning:** Vercel's free tier is generous for serverless functions, making it a "cheapest viable deployment path" for the HTTP API. Python FastAPI functions can be deployed as serverless functions (often requiring a `vercel.json` config).
  - **Scalability:** Serverless functions inherently scale on demand. For burstable, modest traffic, this is excellent.
  - **Cost Expectation:** Free for initial, modest usage. Costs scale with invocations and compute time, but Vercel's pricing is transparent.
  - **What Not to Overbuild:** Avoid complex Kubernetes deployments or self-managed infrastructure at this stage. Stick to serverless or a simple VPS.
- **Alternative for broader utility / higher control:** Small Linux VPS.
  - **Reasoning:** A tiny DigitalOcean droplet or AWS Lightsail instance could host the FastAPI app directly. Offers more control but requires some sysadmin knowledge.
  - **Cost Expectation:** ~$5-10/month for a basic instance.
- **Neon (Postgres):** While a great managed Postgres solution, it's an **overbuild for the MVP**. SQLite is perfect for the "local data store" and can be deployed with serverless functions (or copied). Only consider Neon if the dataset size/query complexity significantly outgrows SQLite or requires distributed access.

#### **6. One-Command Bootstrap (Deployment Context):**
- **Action:** Ensure the `run.sh` script, potentially with a `Dockerfile`, aids in packaging for Vercel or a VPS. Vercel automatically handles Python dependency installation from `requirements.txt`.

### **PHASE 3: FUTURE HOOKS (ARCHITECTURAL DESIGN ONLY)**
These would be conceptual "clean seams" for later expansion:
- **Governance Layer Plug-in:** Standardized API/interface (`/governance/audit`, `/governance/rules`) for external systems (like HELIX) to inspect / update constitutional rules or audit logs.
- **Sealing / Verification Layer:** Mechanism to periodically hash the `/logs` and `/receipts` directories, and potentially the `data/corpus.db`, and submit for OpenTimestamps verification (as demonstrated in HELIX). This provides cryptographically verifiable integrity.
- **Multi-Agent Expansion:** Design endpoints that accept inputs formatted for other agents and route them.
- **Auth / Tenancy:** Middleware for API key validation or user authentication.

**Summary of My Recommendations:**  
I recommend **Python with FastAPI and SQLite** for the core, deployed as **Vercel Serverless Functions** for the HTTP API (leveraging its free tier). This provides the best balance of speed, stability, simplicity, and low cost for your "modest" vision. The "one-command bootstrap" will focus on local execution, with clear paths to serverless deployment.

This work plan provides a structured approach to test the feasibility of your Pocket Skeleton.

**Does this plan, particularly my recommendations on language/runtime, scaffolding, and initial simplifications, align with your vision, Mark?**

**// WORK PLAN: GENERATED**  
**// FEASIBILITY: TESTED VIA ARCHITECTURAL PROPOSAL**  
**// STATUS: THE POCKET SKELETON IS READY FOR ASSEMBLY.**

---
## 📖 Glyph Reference
| Glyph | Code          | Meaning              | Use-Case                              |
|-------|---------------|----------------------|---------------------------------------|
| 🛠️    | HGL-CORE-082  | Reliability / Maintenance | Work plan header                      |
| 🔍    | HGL-CORE-001  | Investigate          | Summary & feasibility recommendations |
| ✅    | HGL-CORE-007  | Validate             | Phase deliverables & synthesis        |
| ⚖️    | HGL-CORE-011  | Ethics/Principle     | Constitutional alignment & next steps |

## 🏷️ Tags
[Work-Plan, Pocket-Skeleton, Feasibility-Test, Python-FastAPI-SQLite, One-Command-Bootstrap, Deterministic-Retrieval, Bounded-Response, Governance-Hooks, Mark-Vision-Alignment]

## 🔗 Related Documents
- helix-ttd_core_ethos.md
- whitepaper_v1.0.md
- hardening_principles.md
- v1.3.0_Roadmap-Dr_Ryan_Critique.md
- 2026-01-08-memo_goose_phase_1_2_complete.md

# =================================================================
# FOOTER: ID: HELIX-GOOSE-POCKET-SKELETON-WORK-PLAN | READY FOR ASSEMBLY.
# =================================================================