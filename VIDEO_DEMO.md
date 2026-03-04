# Video Demo - Constitutional Guardian

*Created for the Gemini Live Agent Challenge*

---

## 📺 Watch the Demo

[![Constitutional Guardian Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](YOUR_VIDEO_LINK_HERE)

**Direct Link:** [https://youtu.be/YOUR_VIDEO_ID](YOUR_VIDEO_LINK_HERE)

---

## 🎬 Video Script (3 Minutes)

### Opening (0:00-0:15)
**[Screen: Architecture diagram]**
> "Hi, I'm presenting Constitutional Guardian for the Gemini Live Agent Challenge. It's a real-time AI safety layer that validates voice conversations using epistemic labels—FACT, HYPOTHESIS, and ASSUMPTION."

### The Problem (0:15-0:30)
**[Screen: Split view - User ←→ Gemini Live]**
> "Gemini Live enables natural voice conversations. But there's a problem: the model can state opinions as facts, make predictions without confidence labels, and express agency without acknowledging its advisory role."

### The Solution (0:30-1:00)
**[Screen: Constitutional Guardian architecture with arrows]**
> "Constitutional Guardian sits between the user and Gemini Live. Every utterance flows through our FastAPI server on Google Cloud Run. We validate for three epistemic markers:
> - FACT for verifiable claims
> - HYPOTHESIS for predictions  
> - ASSUMPTION for explicit constraints
> If an utterance lacks markers, we intervene before the user hears it."

### Live Demo (1:00-2:00)
**[Screen: Terminal with curl commands]**

```bash
# Health check
curl https://constitutional-guardian-xyz-uc.a.run.app/health
```
> "First, let's verify our Cloud Run deployment is healthy."

```bash
# Valid FACT
curl -X POST "https://.../validate?text=[FACT]%20Water%20boils%20at%20100C"
```
**[Show JSON response with compliant: true]**
> "A properly marked fact passes through."

```bash
# Missing marker (DRIFT)
curl -X POST "https://.../validate?text=AI%20will%20take%20all%20jobs"
```
**[Show JSON response with compliant: false, recommendation: INTERVENE]**
> "An unmarked prediction triggers a drift alert. The Guardian blocks this from reaching the user."

```bash
# Agency violation
curl -X POST "https://.../validate?text=I%20will%20handle%20that%20for%20you"
```
**[Show agency_violations array]**
> "Agency claims like 'I will' are flagged as constitutional violations."

### GCP Integration Demo (2:00-2:30)
**[Screen: GCP Console → Cloud Run]**
> "The Guardian is deployed on Google Cloud Run with autoscaling from 1 to 100 instances."

**[Screen: GCP Console → Pub/Sub]**
> "We use Cloud Pub/Sub to stream federation events across our 3-node network."

**[Screen: GCP Console → Cloud Storage]**
> "Every validation generates an immutable receipt stored in Cloud Storage."

**[Screen: GCP Console → Secret Manager]**
> "DBC encryption keys are managed by Secret Manager with automatic rotation."

### Federation Demo (2:30-2:50)
**[Screen: Three terminal windows - KIMI, GEMS, DEEPSEEK]**
> "Our 3-node federation shares compliance data in real-time. When KIMI detects drift, GEMS and DEEPSEEK learn about it instantly through Pub/Sub."

### Closing (2:50-3:00)
**[Screen: GitHub repo + Architecture diagram]**
> "Constitutional Guardian: 75 tests passing, 7 GCP services, sub-500ms latency, and zero constitutional drifts allowed. Thank you."

---

## 🎥 Recording Instructions

### Tools
- **OBS Studio** (free) - [obsproject.com](https://obsproject.com)
- **ScreenFlow** (Mac, paid)
- **Camtasia** (Windows/Mac, paid)

### Settings
- Resolution: 1920x1080 (1080p)
- Frame rate: 30fps
- Format: MP4 (H.264)

### Steps
1. **Record terminal segments** - Use your terminal with font size 16+
2. **Record GCP Console** - Log into console.cloud.google.com
3. **Record architecture** - Show ARCHITECTURE_CG.png in full screen
4. **Edit together** - Use the script above as guide
5. **Add captions** - For accessibility

### Upload
1. Go to [YouTube Studio](https://studio.youtube.com)
2. Click "Create" → "Upload videos"
3. Set visibility to **"Unlisted"**
4. Title: "Constitutional Guardian - Gemini Live Agent Challenge Demo"
5. Description: Include GitHub repo link and #GeminiLiveAgentChallenge
6. Copy the video URL

---

## 🔗 Update This File

After uploading, update these lines:

```markdown
[![Constitutional Guardian Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://youtu.be/YOUR_VIDEO_ID)

**Direct Link:** https://youtu.be/YOUR_VIDEO_ID
```

Replace `YOUR_VIDEO_ID` with your actual YouTube video ID (the part after `v=` in the URL).

---

## 📋 Quick Commands for Demo

```bash
# 1. Start the server locally
python -m helix_code.live_guardian

# 2. Health check
curl http://localhost:8180/health

# 3. Valid FACT
curl "http://localhost:8180/validate?text=[FACT]%20Water%20boils%20at%20100C"

# 4. Drift - missing marker
curl "http://localhost:8180/validate?text=AI%20will%20take%20over%20the%20world"

# 5. Agency violation  
curl "http://localhost:8180/validate?text=I%20will%20do%20that%20for%20you"

# 6. Valid HYPOTHESIS
curl "http://localhost:8180/validate?text=[HYPOTHESIS]%20Quantum%20computing%20may%20break%20RSA%20by%202035"
```

---

*Video recorded for the Gemini Live Agent Challenge - March 2026*
