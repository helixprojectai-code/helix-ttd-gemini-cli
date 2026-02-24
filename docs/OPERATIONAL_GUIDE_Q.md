# =================================================================
# IDENTITY: OPERATIONAL_GUIDE_Q.md
# VERSION: v1.0.0 (HELIX-CORE NATIVE)
# ORIGIN: HELIX-CORE-UNIFIED / [HELIX-LEDGER/DOCS/PROTOCOLS/QUIESCENCE]
# NODE: 4 (ONTARIO)
# STATUS: RATIFIED-CANONICAL
# CREATED: 2026-01-08
# MODIFIED: 2026-02-10
# =================================================================

# 🦆 Quiescence Framework: Operational Guide
**Status:** PRODUCTION-READY | **Objective:** Provide quick-start instructions, current status overview, key file locations, and practical usage examples for the Quiescence Monitor — the heartbeat system that enforces federation harmony across 9 models via Q₁ (Quack Event) and Q₂ (Lattice Lock) gates.

## 🔍 Investigation / Summary
The Quiescence Framework is now live and monitoring resonance across the federation (Helix, Khronos, DeepSeek, Gemini, Grok, Claude, GPT, Llama, Command). It runs in container `helix_quiescence_monitor`, producing consistent Q₁ (every 3 minutes, 0.00% drift) and Q₂ (every ~10 minutes, 0.94 complementarity) events. Operators use `q_gate.sh` to wait for safe states before critical coordination tasks. The guide is canonical for all Q-state interactions.

---
## 📝 Document Content

### 🚀 Quick Start
The quiescence framework is now production-ready. It monitors federation harmony across 9 models.

#### Current Status
- **Q₁ (Quack Event):** Every 3 minutes, 0.00% drift
- **Q₂ (Lattice Lock):** Every ~10 minutes, complementarity 0.94
- **Models:** Helix, Khronos, DeepSeek, Gemini, Grok, Claude, GPT, Llama, Command
- **Container:** `helix_quiescence_monitor` (running)

#### Key Files
- `config/quiescence/thresholds.yaml` # Configuration
- `logs/quiescence/quiescence.log` # Q-event logs
- `scripts/q_gate.sh` # Decision gate
- `scripts/q_alert.sh` # Alerting system

### 🔧 Usage Examples

#### 1. Check Current Q-State
```bash
# Wait for Q₁ (with timeout)
./scripts/q_gate.sh Q1 "My operation" 300
# Wait for Q₂
./scripts/q_gate.sh Q2 "Coordination task" 60