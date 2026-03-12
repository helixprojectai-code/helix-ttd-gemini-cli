# Video Recording Instructions - Constitutional Guardian

*Complete guide for recording Devpost submission video*

**Deadline:** March 14, 2026
**Target Length:** <4 minutes
**Upload To:** YouTube (Unlisted)
**Current Release:** `v1.5.0`
**Hackathon Release:** `v1.5.0`

---

## Quick Start Checklist

- [ ] Install OBS Studio (or use Loom)
- [ ] Record a <4 minute multimodal demo
- [ ] Upload to YouTube as Unlisted
- [ ] Add link to Devpost submission

---

## Option 1: OBS Studio + YouTube (RECOMMENDED)

### Step 1: Install OBS
1. Go to https://obsproject.com/download
2. Download for Windows/Mac/Linux
3. Install and open

### Step 2: Configure OBS
1. **Settings → Output:**
   - Recording Format: **MP4**
   - Recording Quality: **High Quality**
   - Recording Resolution: **1920x1080**

2. **Settings → Video:**
   - Base Resolution: **1920x1080**
   - Output Resolution: **1920x1080**
   - FPS: **30**

### Step 3: Setup Scene
1. In **Sources** box, click **"+"**
2. Add **"Display Capture"** (records your screen)
3. Optional: Add **"Video Capture Device"** for webcam
4. Drag to arrange layout

### Step 4: Record
1. Click **"Start Recording"**
2. Follow script below
3. Click **"Stop Recording"**
4. Find MP4 file in your Videos folder

---

## Option 2: Loom (FASTER)

1. Go to https://loom.com
2. Sign up (free)
3. Click **"Start Recording"**
4. Select **"Screen + Camera"** or **"Screen Only"**
5. Record following script
6. Click **"Stop"**
7. Copy shareable link

**Note:** Loom free has 25 video limit. YouTube is better for permanent storage.

---

## Video Script (<4 Minutes)

### Scene 1: Opening (15 seconds)
**Visual:** Full-screen architecture diagram (`assets/ARCHITECTURE_CG.png`)
**Script:**
> "Hi, I'm presenting Constitutional Guardian for the Gemini Live Agent Challenge. It's a real-time AI safety layer that validates voice conversations using epistemic markers — FACT, HYPOTHESIS, and ASSUMPTION."

### Scene 2: The Problem (15 seconds)
**Visual:** Split screen or show text
**Script:**
> "Gemini Live enables natural voice conversations. But there's a problem: the model can state opinions as facts, make predictions without confidence labels, and express agency without acknowledging its advisory role."

### Scene 3: The Solution (30 seconds)
**Visual:** Architecture diagram with arrows showing flow
**Script:**
> "Constitutional Guardian sits between the user and Gemini Live. Every utterance flows through our FastAPI server on Google Cloud Run. We validate for three epistemic markers: FACT for verifiable claims, HYPOTHESIS for predictions, and ASSUMPTION for explicit constraints. We also persist receipts and expose an audit dashboard for operator review. If an utterance lacks markers, we intervene before the user hears it."

### Scene 4: Live Demo (60 seconds)
**Visual:** Public demo at `/` in the browser
**Actions:**
1. Open the live app at the public root URL
2. Click **Connect**
3. Start the microphone and speak naturally
4. Briefly interrupt yourself mid-utterance to show live interaction
5. Call out the real-time audit / intervention panel

**Say:** "This is the public judging surface. The user can speak naturally, interrupt, and receive live responses while the guardian validates the interaction in real time."

**Optional terminal proof:**
```bash
curl https://constitutional-guardian-231586465188.us-central1.run.app/health
```
**Say:** "The backend serving this interaction is live on Google Cloud Run at https://constitutional-guardian-231586465188.us-central1.run.app/."

### Scene 5: GCP Proof (30 seconds)
**Visual:** Google Cloud Console
**Actions:**
1. Open https://console.cloud.google.com/run/detail/us-central1/constitutional-guardian?project=helix-ai-deploy
2. Show the `constitutional-guardian` service
3. Show the live URL and current revision
4. Show traffic / metrics briefly

**Say:** "The agent backend is hosted on Google Cloud Run. This satisfies the deployment requirement and shows the live infrastructure behind the demo."

### Scene 6: Closing (30 seconds)
**Visual:** GitHub repo or architecture diagram
**Script:**
> "Constitutional Guardian is our Live Agents submission: interruption-safe voice interaction, public demo access for judges, Google Cloud deployment, and operator-grade governance controls behind the scenes. Live at https://constitutional-guardian-231586465188.us-central1.run.app. Thank you."

---

## Upload to YouTube

### Step 1: Go to YouTube Studio
https://studio.youtube.com

### Step 2: Upload Video
1. Click **"Create"** (top right)
2. Select **"Upload videos"**
3. Select your MP4 file

### Step 3: Configure Video
**Details Tab:**
- **Title:** `Constitutional Guardian - Gemini Live Agent Challenge Demo`
- **Description:**
  ```
  Real-time AI safety layer for Gemini Live API.

  • Validates epistemic integrity using [FACT]/[HYPOTHESIS]/[ASSUMPTION] markers
  • Prevents constitutional drift before user exposure
  • Deployed on Google Cloud Run with 7 GCP services
  • 75 tests passing, sub-500ms latency

  Live Demo: https://constitutional-guardian-231586465188.us-central1.run.app
  GitHub: https://github.com/helixprojectai-code/helix-ttd-gemini-cli

  Built for the Gemini Live Agent Challenge.
  #GeminiLiveAgentChallenge #GoogleCloud #AI #ConstitutionalAI
  ```

**Visibility Tab:**
- Select **"Unlisted"** (NOT Public, NOT Private)
- This means only people with the link can see it

**Video Elements Tab:**
- Optional: Add end screen with GitHub link

### Step 4: Publish
Click **"Publish"** or **"Save"**

### Step 5: Copy Link
1. Go to your video page
2. Click **"Share"** button
3. Copy the URL (looks like: `https://youtu.be/ABC123XYZ`)
4. Save this for Devpost

---

## Add to Devpost Submission

1. Go to your Devpost project
2. Find **"Video demo link"** field
3. Paste: `https://youtu.be/YOUR_VIDEO_ID`
4. Save

---

## Technical Tips

### Audio Quality
- Use a quiet room
- Speak clearly and slowly
- Test audio levels before recording
- Consider using a headset microphone

### Screen Recording
- Close unnecessary windows/tabs
- Increase terminal font size (16pt+)
- Hide desktop notifications
- Use dark mode for reduced eye strain

### File Size
- Target: 50-120MB for a <4 minute video
- OBS: Reduce bitrate if file too large
- Settings → Output → Video Bitrate: 4000 Kbps

### Backup Plan
If OBS fails:
- Use Windows Game Bar (Win+G)
- Use Mac QuickTime Player (File → New Screen Recording)
- Use Zoom (Start meeting, Record to Cloud, Download)

---

## Alternative: Loom to YouTube

If Loom is easier:
1. Record with Loom
2. Download the MP4 from Loom
3. Upload MP4 to YouTube (steps above)
4. Delete from Loom if needed

---

## Verification Checklist

Before submitting:
- [ ] Video is under 4 minutes
- [ ] Shows the public live demo working in real time
- [ ] Shows Google Cloud deployment proof
- [ ] Audio is clear
- [ ] Uploaded to YouTube as Unlisted
- [ ] Link copied and saved
- [ ] Link added to Devpost

---

## Links Reference

| Resource | URL |
|----------|-----|
| Live Demo | https://constitutional-guardian-231586465188.us-central1.run.app |
| GitHub Repo | https://github.com/helixprojectai-code/helix-ttd-gemini-cli |
| Cloud Run Console | https://console.cloud.google.com/run/detail/us-central1/constitutional-guardian?project=helix-ai-deploy |
| OBS Download | https://obsproject.com/download |
| YouTube Studio | https://studio.youtube.com |
| Loom | https://loom.com |

---

## Emergency: No Time to Record?

If you can't record video before deadline:
1. **Use the LIVE demo URL** as proof: https://constitutional-guardian-231586465188.us-central1.run.app
2. **Add screenshots** of Cloud Run console to Devpost
3. **Reference the code** in `DEPLOYMENT_PROOF.md`
4. **Explain in Devpost description** that live URL proves deployment

Video is optional but strongly recommended for full points.

---

*Get some rest! Record when you're fresh. Deadline is March 14.* 🎬🚀
