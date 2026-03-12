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

1. Open the public demo at `https://constitutional-guardian-231586465188.us-central1.run.app/`
2. Click **Connect**
3. Start the microphone
4. Speak, interrupt, and show the live response / audit surface

```bash
curl https://constitutional-guardian-231586465188.us-central1.run.app/health
```
> "First, let's verify the Cloud Run backend serving the live demo is healthy."

### GCP Deployment Proof (2:00-2:30)
**[Screen: GCP Console -> Cloud Run]**
> "The Guardian backend is live on Google Cloud Run, and this is the service judges can verify during submission review."

**[Screen: GCP Console -> Cloud Storage / Secret Manager / Logging]**
> "We use Google Cloud services for receipt persistence, secret handling, and operational monitoring behind the live demo."

### Closing (2:30-3:00)
**[Screen: GitHub repo + Architecture diagram]**
> "Constitutional Guardian is our Live Agents submission: a real-time multimodal agent with public judging access, live governance, and Google Cloud deployment. Thank you."

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
1. **Record the public browser demo first** - show the live mic flow, interruption, and audit surface
2. **Record the Cloud Run console proof** - show the live service and revision in Google Cloud
3. **Record the architecture diagram** - show `assets/ARCHITECTURE_CG.png` in full screen
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
