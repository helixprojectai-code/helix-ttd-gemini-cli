# Video Demo - Constitutional Guardian

*Created for the Gemini Live Agent Challenge*

---

## Watch the Demo

[![Constitutional Guardian Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](YOUR_VIDEO_LINK_HERE)

**Direct Link:** [https://youtu.be/YOUR_VIDEO_ID](YOUR_VIDEO_LINK_HERE)

---

## Video Script (<4 Minutes)

### Scene 1: Live Hook (0:00-0:25)
**[Screen: Public live UI at `/`]**

1. Open `https://constitutional-guardian-231586465188.us-central1.run.app/`
2. Click **Connect**
3. Start the microphone
4. Ask a short question
5. Interrupt the agent once mid-response

**Say:**
> "This is Constitutional Guardian, a live multimodal agent built for the Gemini Live Agent Challenge. It supports interruption-safe voice interaction with real-time governance layered into the session."

### Scene 2: Problem and Value (0:25-0:45)
**[Screen: Keep the live UI visible]**

**Say:**
> "Most AI experiences still center the text box. We built a live agent that can hear, respond in real time, and apply constitutional safeguards before drift reaches the user."

### Scene 3: Governance in Action (0:45-1:30)
**[Screen: Same live UI with audit panel visible]**

Use a prompt that naturally surfaces epistemic framing, for example:
- "Give me a short explanation of why explicit epistemic labels matter in AI systems."
- "Make a short prediction about the future of AI adoption."

**Say:**
> "This system expects substantive claims to be framed as [FACT], [HYPOTHESIS], or [ASSUMPTION]. The live audit surface updates alongside the conversation so users and operators can distinguish verified claims from forecasts and working assumptions."

### Scene 4: Production Credibility (1:30-1:55)
**[Screen: Still on the UI, then quick terminal cut]**

```bash
curl https://constitutional-guardian-231586465188.us-central1.run.app/health
```

**Say:**
> "The public demo is backed by a live Google Cloud Run deployment. This is not a mockup or local-only demo."

### Scene 5: API Credibility Beat (1:55-2:15)
**[Screen: `/docs`]**

Open:
- `https://constitutional-guardian-231586465188.us-central1.run.app/docs`

Keep this short. Scroll just enough to show the documented API surface.

**Say:**
> "The backend is directly inspectable through the documented API, which makes the live agent reproducible and easier for judges to verify."

### Scene 6: GCP Proof (2:15-2:40)
**[Screen: GCP Console -> Cloud Run]**

Open:
- `https://console.cloud.google.com/run/detail/us-central1/constitutional-guardian?project=helix-ai-deploy`

Show:
1. service name
2. live URL
3. active revision
4. traffic / metrics briefly

**Say:**
> "The backend is hosted on Google Cloud Run and supported by Google Cloud services for persistence, secrets, and monitoring."

### Scene 7: Architecture Close (2:40-3:00)
**[Screen: `assets/ARCHITECTURE_CG.png`]**

**Say:**
> "Constitutional Guardian is our Live Agents submission: a real-time, interruption-safe multimodal agent with operator-grade governance controls on Google Cloud."

---

## Recording Instructions

### Tools
- **OBS Studio** (free) - [obsproject.com](https://obsproject.com)
- **ScreenFlow** (Mac, paid)
- **Camtasia** (Windows/Mac, paid)

### Settings
- Resolution: 1920x1080
- Frame rate: 30fps
- Format: MP4 (H.264)

### Steps
1. Record the live UI first
2. Capture one interruption during voice interaction
3. Show the audit / governance surface updating
4. Add a quick health check cut
5. Flash `/docs` briefly for reproducibility proof
6. Show Cloud Run deployment proof
7. Close on the architecture diagram

### Upload
1. Go to [YouTube Studio](https://studio.youtube.com)
2. Click **Create -> Upload videos**
3. Set visibility to **Unlisted**
4. Title: `Constitutional Guardian - Gemini Live Agent Challenge Demo`
5. Description: include the GitHub repo link and `#GeminiLiveAgentChallenge`
6. Copy the video URL

---

## Update This File

After uploading, update these lines:

```markdown
[![Constitutional Guardian Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://youtu.be/YOUR_VIDEO_ID)

**Direct Link:** https://youtu.be/YOUR_VIDEO_ID
```

Replace `YOUR_VIDEO_ID` with the actual YouTube video ID.

---

## Quick Commands for Proof Beats

```bash
# Live health check
curl https://constitutional-guardian-231586465188.us-central1.run.app/health

# OpenAPI docs
open https://constitutional-guardian-231586465188.us-central1.run.app/docs
```

---

*Video recorded for the Gemini Live Agent Challenge - March 2026*
