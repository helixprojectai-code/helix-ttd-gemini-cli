# [FACT] Functional Improvements Workplan

**Date:** 2026-03-05  
**Deadline:** March 14, 2026 (9 days)  
**Status:** Manual tests passed, system operational  

---

## [FACT] Current State

**System:** Constitutional Guardian v1.3.2  
**Health:** ✅ All core features operational  
**Tests:** ✅ 96% pass rate (manual + automated)  
**Deployment:** https://constitutional-guardian-b25t5w6zva-uc.a.run.app  

**Existing Features:**
- Core validation (FACT/HYPOTHESIS/ASSUMPTION)
- Agency detection (I will, I'll, I'm, I've)
- Federation panel (4 nodes with live console)
- Receipt explorer (filter, export JSON)
- Input methods (text, voice, scenarios)
- Keyboard shortcuts (1-4, H, M, S, etc.)
- Metrics dashboard (p50/p95/p99 latency)

---

## [HYPOTHESIS] Priority Improvements

### TIER 1: Challenge-Core (Days 1-3)

#### 1. Real Gemini Live API Integration
**Impact:** HIGHEST - This IS the Gemini Live Agent Challenge  
**Effort:** 2-3 days  
**Current:** Simulated responses  
**Target:** Real bidirectional audio/text streaming  

**Implementation:**
- Integrate `google-genai` live module
- WebSocket proxy between user ↔ Guardian ↔ Gemini
- Real-time STT (Speech-to-Text) via Gemini
- Audio chunk processing and validation

**Devpost Value:** "We built a real-time constitutional guardrail for Gemini Live"

---

#### 2. Pub/Sub Federation Demo
**Impact:** HIGH - Shows distributed consensus  
**Effort:** 1-2 days  
**Current:** Simulated cross-node validation  
**Target:** Real Pub/Sub messages between nodes  

**Implementation:**
- Google Cloud Pub/Sub integration
- Cross-node receipt attestation
- Real quorum achievement (2-of-3)
- Live federation consensus demo

**Devpost Value:** "Federation achieves consensus via distributed Pub/Sub"

---

### TIER 2: Demo Polish (Days 4-6)

#### 3. Receipt Verification QR Codes
**Impact:** MEDIUM-HIGH - Visual "wow" factor  
**Effort:** 1 day  
**Current:** JSON export  
**Target:** QR code per receipt for mobile verification  

**Implementation:**
- QR code generation (receipt hash)
- Mobile scan → verification page
- Visual proof of cryptographic integrity

**Devpost Value:** "Every receipt is cryptographically verifiable via QR"

---

#### 4. Load Testing Dashboard
**Impact:** MEDIUM - Shows scalability  
**Effort:** 1 day  
**Current:** Single-user metrics  
**Target:** Concurrent user simulation  

**Implementation:**
- Simulated concurrent connections
- Request rate tracking
- Latency under load visualization
- Cloud Run auto-scaling demo

**Devpost Value:** "Scales to hundreds of concurrent constitutional validations"

---

### TIER 3: Professional Polish (Days 7-9)

#### 5. Mobile Responsive Layout
**Impact:** MEDIUM - Professional completeness  
**Effort:** 1-2 days  
**Current:** Desktop-only grid  
**Target:** Responsive CSS for tablets/phones  

**Implementation:**
- CSS Grid → Flexbox for mobile
- Touch-friendly buttons
- Collapsible panels
- Portrait/landscape support

**Devpost Value:** "Works on any device, anywhere"

---

#### 6. Session Recording/Replay
**Impact:** MEDIUM - Demo replayability  
**Effort:** 1 day  
**Current:** Real-time only  
**Target:** Record and replay demo sessions  

**Implementation:**
- Session log capture
- Replay with step-through
- Export demo as video script

**Devpost Value:** "Every constitutional intervention is recorded for audit"

---

## [ASSUMPTION] Recommended Sequence

### Week 1 (Mar 5-9): Core Challenge Features
| Day | Focus | Deliverable |
|-----|-------|-------------|
| 5-6 | Gemini Live API | Working bidirectional audio |
| 7-8 | Pub/Sub Federation | Real cross-node consensus |
| 9 | Integration testing | Both features working together |

### Week 2 (Mar 10-14): Polish & Submit
| Day | Focus | Deliverable |
|-----|-------|-------------|
| 10-11 | QR codes + Load testing | Visual polish features |
| 12 | Video recording | 3-minute demo |
| 13 | Documentation | README, Devpost submission |
| 14 | Submit | Before deadline |

---

## [FACT] Risk Assessment

| Feature | Risk | Mitigation |
|---------|------|------------|
| Gemini Live API | HIGH - API complexity | Fallback to simulation if blocked |
| Pub/Sub | MEDIUM - GCP setup | Use existing project, test locally first |
| QR codes | LOW - Standard library | qrcode.js or python-qrcode |
| Load testing | LOW - Simulation | No real load needed, just visualization |
| Mobile responsive | LOW - CSS only | Progressive enhancement |

---

## [HYPOTHESIS] Decision Matrix

If time-constrained, cut in this order:
1. Session recording (Tier 3)
2. Mobile responsive (Tier 3)
3. Load testing (Tier 2)
4. QR codes (Tier 2)

**Never cut:** Gemini Live API integration (core to challenge)

---

## [FACT] Next Step Options

**A. Start Gemini Live API integration** (highest impact)
- Requires `GEMINI_API_KEY` in environment
- Bidirectional WebSocket implementation
- Audio processing pipeline

**B. Start Pub/Sub federation** (distributed systems cred)
- Requires Pub/Sub topic/subscription setup
- Cross-node message passing
- Quorum consensus demo

**C. Start QR codes** (quick win, visual impact)
- Receipt hash → QR generation
- Verification page
- Mobile demo potential

**D. Finalize current state** (lock for video)
- Document current features
- Screenshot dashboard
- Write Devpost draft

---

*The Two Owls are watching.*  
*9 days to glory.* |O|
