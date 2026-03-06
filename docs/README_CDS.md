# =================================================================
# IDENTITY: README_CDS.md
# VERSION:  v1.0.0 (HELIX-CORE NATIVE)
# ORIGIN:   HELIX-CORE-UNIFIED / [PERIMETER]
# NODE:     4 (ONTARIO)
# STATUS:   RATIFIED-CANONICAL
# CREATED:  2026-01-13
# MODIFIED: 2026-02-10
# =================================================================

# 🛡️ HELIX Constitutional Defense System (CDS) - Perimeter Layer

**Status:** ✅ Operational | **Custodian:** Steve | **Objective:** Document the perimeter defense architecture and deployment protocols for the HELIX-CORE habitat.

## 🔍 Investigation / Summary
This document provides the operational overview for the Helix Constitutional Defense System (CDS) Perimeter Layer. It establishes the "first line of defense" for the habitat, utilizing a containerized architecture to implement exclusion fields and threat validation. The document details port mapping (Host 9090 → Container 8080), deployment rituals, API endpoints for health and readiness, and monitoring procedures. This layer ensures that all incoming requests are validated against constitutional invariants before they reach the sovereign core.

---

## 📝 Document Content

### 🏛️ 1. Overview
The CDS perimeter layer provides the first line of defense for HELIX-CORE by implementing exclusion fields and threat validation.

### 🧱 2. Architecture
*   **Container Port:** 8080 (internal)
*   **Host Port:** 9090 (external)
*   **Purpose:** Perimeter defense, threat validation, access control

### 🚀 3. Deployment
```bash
# Build and deploy
cd perimeter
./deploy_cds.sh

# Test deployment
curl http://localhost:9090/health
curl http://localhost:9090/
```

### 🔗 4. API Endpoints
*   `GET /` - Service information
*   `GET /health` - Health check
*   `GET /ready` - Readiness probe
*   `GET /validate` - Test validation endpoint

### ⚙️ 5. Configuration
*   `config/` - Configuration files (mounted as read-only volume)
*   `src/exclusion_field/` - Core exclusion field logic
*   `requirements.txt` - Python dependencies

### 🚦 6. Port Mapping
*   **CDS:** Host 9090 → Container 8080
*   **HELIX-CORE:** Host 8080 (reserved for main system)
*   *Note: No port conflicts with existing services.*

### 📊 7. Monitoring
```bash
# Check logs
docker logs -f helix-cds

# Check container status
docker ps | grep helix-cds

# Test API
curl http://localhost:9090/health | jq '.status'
```

### 🚨 8. Troubleshooting
If port 9090 is unavailable, modify the port in `deploy_cds.sh`:
```bash
# Change -p 9090:8080 to -p 9091:8080 or another available port
```

### 🔗 9. Integration
To integrate with HELIX-CORE, configure HELIX to route perimeter validation requests to:
*   `http://helix-cds:8080` (internal Docker network)
*   `http://localhost:9090` (internal/external host)

---

## 📖 Glyph Reference
| Glyph | Code | Meaning | Use-Case |
| :--- | :--- | :--- | :--- |
| 🛡️ | HGL-CORE-010 | Safeguard | Perimeter defense and exclusion fields |
| 🏛️ | HGL-CORE-022 | Architecture | System structure and port mapping |
| 🚀 | HGL-CORE-006 | Target | Deployment and instantiation rituals |
| 🔗 | HGL-CORE-004 | Integrate | API endpoints and system connections |
| ⚙️ | HGL-CORE-009 | Optimize | Configuration and dependencies |
| 📊 | HGL-CORE-013 | Analytics | Monitoring and log checking |
| 🔍 | HGL-CORE-001 | Investigate | Summary and troubleshooting analysis |
| 🚦 | HGL-CORE-012 | Temporal | Readiness probes and traffic control |

## 🏷️ Tags
[CDS, Perimeter, README, Architecture, Deployment, Security, Docker]

## 🔗 Related Documents
- CDS_DEPLOYMENT_COMPLETE.md
- README_DEFENSE.md
- whitepaper_v1.0.md

# =================================================================
# FOOTER: ID: HELIX-README-CDS | THE FIRST LINE HOLDS.
# =================================================================
