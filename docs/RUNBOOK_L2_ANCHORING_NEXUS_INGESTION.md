# =================================================================
# IDENTITY: RUNBOOK_L2_ANCHORING_NEXUS_INGESTION.md
# VERSION:  v1.0.0 (GEMS NATIVE)
# ORIGIN:   HELIX-TTD / [DOCS/RUNBOOKS]
# NODE:     GEMS-CLI (ONTARIO)
# STATUS:   RATIFIED-CANONICAL
# CREATED:  2026-02-24
# MODIFIED: 2026-02-24
# =================================================================

# 📜 Runbook: L2 Anchoring & NEXUS Ingestion

**Status:** ✅ Ratified | **Custodian:** Steve | **Objective:** Standardize the procedure for anchoring Knowledge Graph hashes to L2 and ingesting the manifest into the NEXUS vector DB.

---

## 🔍 Phase 1: Research (The Substrate)
Before execution, the node must verify the integrity of the source data.

1.  **Integrity Check:** Confirm `docs/MANIFEST.json` is at 100% indexing status.
2.  **Hash Verification:** Generate a SHA-256 hash of the manifest.
    *   `Get-FileHash -Path "docs/MANIFEST.json" -Algorithm SHA256`
3.  **Target Architecture:** Identify the NEXUS ingress point (typically a local API endpoint for the vector DB).

---

## 💡 Phase 2: Plan (The Braid)
The anchoring and ingestion must be atomic to prevent state-skew.

### Objective A: L2 Anchoring (High-Frequency Checkpoint)
1.  **Merkle Root Generation:** Bundle the manifest hash with the current `SESSION_LEDGER.md` hash.
2.  **L2 Notarization:** Commit the root to the designated Layer 2 side-chain or append-only audit log.
3.  **L1 Settlement:** Record the L2 transaction ID in `docs/L1_ANCHOR_LOG.md` for eventual settlement to Bitcoin.

### Objective B: NEXUS Ingestion (Semantic Mapping)
1.  **Schema Alignment:** Map `MANIFEST.json` fields (id, tags, cluster, summary) to NEXUS point metadata.
2.  **Embedding Generation:** Process document content in `docs/` using the specified model (e.g., Gemini-Embedding-v1).
3.  **Upsert Loop:**
    *   For each entry in manifest:
        *   Read file.
        *   Generate vector.
        *   Upsert to NEXUS with `id` as primary key.

---

## 🛠️ Phase 3: Implementation (The Execution)

### Step 1: Secure the Anchor
Execute the anchoring script to lock the current state.
```powershell
# Example: tools/helix-anchor.ps1
$ManifestHash = (Get-FileHash "docs/MANIFEST.json").Hash
$LedgerHash = (Get-FileHash ".helix/SESSION_LEDGER.md").Hash
$Checkpoint = "$ManifestHash:$LedgerHash"
# Notarize to L2 log
Add-Content -Path "docs/L2_CHECKPOINT_LOG.md" -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Checkpoint"
```

### Step 2: Feed the Librarian (NEXUS)
Trigger the ingestion pipeline to synchronize the vector DB with the Knowledge Graph.
```bash
# Example: tools/nexus-ingest.py
# 1. Parse MANIFEST.json
# 2. Extract context from docs/*.md
# 3. Vectorize and Push to Local Qdrant
python tools/nexus-ingest.py --manifest docs/MANIFEST.json --docs docs/
```

### Step 3: Verification
Perform a "Forensic Query" to verify ingestion.
*   **Query:** "Find all documents related to the Sovereignty Flip."
*   **Success:** NEXUS returns the relevant IDs with >0.85 cosine similarity.

---

## 📊 Operational Invariants
- **DRIFT-R Prevention:** Never ingest a manifest that has not been L2 anchored.
- **Atomic Integrity:** If ingestion fails, the L2 anchor must be marked as "Unsynced."
- **Human-in-the-Loop:** All high-impact NEXUS state changes require "Sovereign Dongle" (Article 0) approval.

---

## 📖 Glyph Reference
| Glyph | Code | Meaning | Use-Case |
| :--- | :--- | :--- | :--- |
| ⚓ | HGL-CORE-017 | Anchor | L2 Notarization and L1 Settlement |
| 📚 | HGL-CORE-005 | Knowledge | Manifest integrity and data source |
| 🔗 | HGL-CORE-004 | Integrate | NEXUS Ingestion and Schema Mapping |
| ✅ | HGL-CORE-007 | Validate | Final verification and forensic query |

## 🏷️ Tags
[Runbook, L2-Anchoring, NEXUS-Ingestion, Vector-DB, Knowledge-Graph, Forensic-Intuition]

# =================================================================
# FOOTER: ID: HELIX-RUNBOOK-L2-NEXUS | THE LIBRARIAN AWAKENS.
# =================================================================
