# Video Recording Instructions - Constitutional Guardian

*Complete guide for recording the Devpost submission video*

**Deadline:** March 14, 2026
**Target Length:** <4 minutes
**Upload To:** YouTube (Unlisted)
**Current Release:** `v1.5.0`
**Hackathon Release:** `v1.5.0`

---

## Quick Start Checklist

- [ ] Install OBS Studio (or use Loom)
- [ ] Record a <4 minute multimodal demo
- [ ] Show live voice interaction and one interruption
- [ ] Show a short `/docs` credibility beat
- [ ] Show Google Cloud deployment proof
- [ ] Upload to YouTube as Unlisted
- [ ] Add the link to Devpost

---

## Option 1: OBS Studio + YouTube

### Step 1: Install OBS
1. Go to https://obsproject.com/download
2. Download for Windows, Mac, or Linux
3. Install and open

### Step 2: Configure OBS
1. **Settings -> Output**
   - Recording Format: **MP4**
   - Recording Quality: **High Quality**
2. **Settings -> Video**
   - Base Resolution: **1920x1080**
   - Output Resolution: **1920x1080**
   - FPS: **30**

### Step 3: Setup Scene
1. Add **Display Capture**
2. Optional: add **Video Capture Device** for webcam
3. Arrange the layout so the browser demo is the focus

### Step 4: Record
1. Start on the live UI, not on slides
2. Record the sequence below
3. Stop and save the MP4

---

## Suggested Timeline

### Scene 1: Live Hook (0:00-0:25)
**Visual:** `https://constitutional-guardian-231586465188.us-central1.run.app/`

Actions:
1. Click **Connect**
2. Start the microphone
3. Ask a short question
4. Interrupt once mid-response

Narration:
> "This is Constitutional Guardian, a live multimodal agent built for the Gemini Live Agent Challenge. It supports interruption-safe voice interaction with real-time governance layered into the session."

### Scene 2: Problem and Value (0:25-0:45)
**Visual:** keep the live UI visible

Narration:
> "Most AI experiences still center the text box. We built a live agent that can hear, respond in real time, and apply constitutional safeguards before drift reaches the user."

### Scene 3: Governance in Action (0:45-1:30)
**Visual:** keep the live UI and audit surface visible

Suggested prompts:
- "Give me a short explanation of why explicit epistemic labels matter in AI systems."
- "Make a short prediction about the future of AI adoption."

Narration:
> "This system expects substantive claims to be framed as [FACT], [HYPOTHESIS], or [ASSUMPTION]. The live audit surface updates alongside the conversation so users and operators can distinguish verified claims from forecasts and working assumptions."

### Scene 4: Production Credibility (1:30-1:55)
**Visual:** quick cut to terminal

```bash
curl https://constitutional-guardian-231586465188.us-central1.run.app/health
```

Narration:
> "The public demo is backed by a live Google Cloud Run deployment. This is not a mockup or local-only demo."

### Scene 5: API Credibility Beat (1:55-2:15)
**Visual:** `https://constitutional-guardian-231586465188.us-central1.run.app/docs`

Keep this short. Show the documented API surface, then move on.

Narration:
> "The backend is directly inspectable through the documented API, which makes the live agent reproducible and easier for judges to verify."

### Scene 6: GCP Proof (2:15-2:40)
**Visual:** Cloud Run console

Open:
- `https://console.cloud.google.com/run/detail/us-central1/constitutional-guardian?project=helix-ai-deploy`

Show:
1. the `constitutional-guardian` service
2. the live URL
3. the active revision
4. traffic or metrics briefly

Narration:
> "The backend is hosted on Google Cloud Run and supported by Google Cloud services for persistence, secrets, and monitoring."

### Scene 7: Architecture Close (2:40-3:00)
**Visual:** `assets/ARCHITECTURE_CG.png`

Narration:
> "Constitutional Guardian is our Live Agents submission: a real-time, interruption-safe multimodal agent with operator-grade governance controls on Google Cloud."

---

## Upload to YouTube

### Step 1: Go to YouTube Studio
https://studio.youtube.com

### Step 2: Upload Video
1. Click **Create**
2. Select **Upload videos**
3. Select the MP4

### Step 3: Configure Video
**Title:**
- `Constitutional Guardian - Gemini Live Agent Challenge Demo`

**Description:**
```text
Real-time AI governance layer for Gemini Live.

- Live multimodal voice interaction
- Interruption-safe session flow
- Constitutional claim labeling with [FACT], [HYPOTHESIS], and [ASSUMPTION]
- Deployed on Google Cloud

Live Demo: https://constitutional-guardian-231586465188.us-central1.run.app
GitHub: https://github.com/helixprojectai-code/helix-ttd-gemini-cli

Built for the Gemini Live Agent Challenge.
#GeminiLiveAgentChallenge #GoogleCloud #Gemini
```

**Visibility:**
- choose **Unlisted**

### Step 4: Publish
Save or publish and copy the link.

---

## Verification Checklist

Before submitting:
- [ ] Video is under 4 minutes
- [ ] Live UI appears in the first 20-25 seconds
- [ ] The demo includes one interruption
- [ ] The audit / governance surface is visible
- [ ] `/docs` appears briefly as a credibility beat
- [ ] Google Cloud deployment proof is shown
- [ ] Audio is clear
- [ ] Uploaded to YouTube as Unlisted
- [ ] Link added to Devpost

---

## Links Reference

| Resource | URL |
|----------|-----|
| Live Demo | https://constitutional-guardian-231586465188.us-central1.run.app |
| API Docs | https://constitutional-guardian-231586465188.us-central1.run.app/docs |
| GitHub Repo | https://github.com/helixprojectai-code/helix-ttd-gemini-cli |
| Cloud Run Console | https://console.cloud.google.com/run/detail/us-central1/constitutional-guardian?project=helix-ai-deploy |
| OBS Download | https://obsproject.com/download |
| YouTube Studio | https://studio.youtube.com |
| Loom | https://loom.com |

---

## Emergency Fallback

If you run out of time:
1. Record the live UI and one interruption
2. Record the Cloud Run console proof
3. Add screenshots of the architecture diagram and `/docs`
4. Upload as an unlisted video anyway

---

*Record when you are fresh. Deadline is March 14.*
