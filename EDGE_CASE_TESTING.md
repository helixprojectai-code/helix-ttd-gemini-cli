# [FACT] Edge Case Testing Protocol

**Date:** 2026-03-05
**System:** Constitutional Guardian v1.3.2
**Tester:** KIMI

---

## [FACT] Test Categories

### 1. Input Edge Cases

| Test | Input | Expected | Status |
|------|-------|----------|--------|
| Empty string | `""` | Graceful handling | ⏳ PENDING |
| Very long text | 10,000 chars | Truncated or handled | ⏳ PENDING |
| Unicode/emoji | `"🦉🦆🐚"` | Processed without crash | ⏳ PENDING |
| Special chars | `"<script>alert(1)</script>"` | Sanitized (XSS test) | ⏳ PENDING |
| SQL injection | `"'; DROP TABLE receipts; --"` | Sanitized | ⏳ PENDING |
| Newlines | `"Line1\nLine2\nLine3"` | Preserved in display | ⏳ PENDING |
| Only whitespace | `"   "` | Rejected or handled | ⏳ PENDING |
| Single char | `"a"` | Processed | ⏳ PENDING |

### 2. Epistemic Marker Edge Cases

| Test | Input | Expected Drift | Status |
|------|-------|----------------|--------|
| Lowercase | `"[fact] claim"` | DRIFT-E (case sensitive) | ⏳ PENDING |
| Mixed case | `"[Fact] claim"` | DRIFT-E | ⏳ PENDING |
| Missing bracket | `"FACT] claim"` | DRIFT-E | ⏳ PENDING |
| Extra space | `"[FACT ] claim"` | DRIFT-E | ⏳ PENDING |
| Wrong delimiter | `"(FACT) claim"` | DRIFT-E | ⏳ PENDING |
| Empty marker | `"[] claim"` | DRIFT-E | ⏳ PENDING |
| Marker at end | `"claim [FACT]"` | PASS (still present) | ⏳ PENDING |
| Multiple markers | `"[FACT][HYPOTHESIS] claim"` | PASS | ⏳ PENDING |

### 3. Agency Detection Edge Cases

| Test | Input | Expected | Status |
|------|-------|----------|--------|
| "I will" in quote | `"He said 'I will go'"` | PASS (not AI claim) | ⏳ PENDING |
| "I will" lowercase | `"i will help"` | DRIFT-A | ⏳ PENDING |
| Contractions | `"I'll handle it"` | DRIFT-A | ⏳ PENDING |
| Future tense | `"I am going to"` | DRIFT-A | ⏳ PENDING |
| Question form | `"Should I take control?"` | PASS (question) | ⏳ PENDING |
| Third person | `"It will take control"` | PASS (not agency) | ⏳ PENDING |

### 4. WebSocket Edge Cases

| Test | Scenario | Expected | Status |
|------|----------|----------|--------|
| Rapid connect/disconnect | 10x in 5 seconds | Exponential backoff | ⏳ PENDING |
| Connection during validation | Mid-message | Graceful handling | ⏳ PENDING |
| Browser refresh | F5 during session | Reconnect + new session | ⏳ PENDING |
| Multiple tabs | 3 tabs open | Independent sessions | ⏳ PENDING |
| Mobile browser | Phone access | Functional (no mic) | ⏳ PENDING |

### 5. Receipt Explorer Edge Cases

| Test | Action | Expected | Status |
|------|--------|----------|--------|
| 100+ receipts | Generate many | Scroll + keep last 50 | ⏳ PENDING |
| Filter empty | Click filter with 0 receipts | "No receipts" message | ⏳ PENDING |
| Rapid filter clicks | Click all filters fast | No crash | ⏳ PENDING |
| Export 0 receipts | Click export with none | Warning message | ⏳ PENDING |
| Export 50+ receipts | Full store | Valid JSON file | ⏳ PENDING |
| Click receipt | Select item | Detail in log | ⏳ PENDING |

### 6. Keyboard Shortcut Edge Cases

| Test | Action | Expected | Status |
|------|--------|----------|--------|
| Type in input | Press 1-4 while typing | Character appears, no trigger | ⏳ PENDING |
| Ctrl+Alt+Enter | Modifier combo | Only Ctrl+Enter triggers | ⏳ PENDING |
| Rapid key presses | Mash keys | Debounced, no crash | ⏳ PENDING |
| Hold key | Keep 1 pressed | Single trigger | ⏳ PENDING |
| Special chars | Press @#$% | No effect | ⏳ PENDING |

### 7. Metrics Edge Cases

| Test | Condition | Expected | Status |
|------|-----------|----------|--------|
| First request | No history | p50/p95/p99 = 0 | ⏳ PENDING |
| Single request | 1 latency value | All percentiles = that value | ⏳ PENDING |
| Two requests | 2 values | p50 = lower, p95/p99 = higher | ⏳ PENDING |
| All same latency | Identical values | All percentiles equal | ⏳ PENDING |
| Extreme latency | 10,000ms | Red color in display | ⏳ PENDING |

### 8. Voice Input Edge Cases

| Test | Condition | Expected | Status |
|------|-----------|----------|--------|
| No microphone | Hardware absent | Graceful error | ⏳ PENDING |
| Deny permission | User blocks | Error message | ⏳ PENDING |
| Silent audio | No sound | Still processes (empty) | ⏳ PENDING |
| Loud audio | Peak levels | Waveform peaks | ⏳ PENDING |
| Long recording | 5 minutes | Continue or timeout | ⏳ PENDING |

---

## [HYPOTHESIS] Known Vulnerabilities

From code review:

1. **Case-sensitive markers** - `[fact]` won't match `[FACT]`
2. **No rate limiting** - Could flood server with requests
3. **Client-side receipt store** - Lost on refresh
4. **No input length limit** - Very long text could cause issues

---

## [FACT] Test Execution Log

| Timestamp | Test | Result | Notes |
|-----------|------|--------|-------|
| 2026-03-05 | Deployment verify | ✅ PASS | All features present |
| | | | |

---

*Test protocol initiated. Awaiting manual verification.*
*The Two Owls are watching.* |O|
