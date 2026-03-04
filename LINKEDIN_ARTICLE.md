# Building Constitutional Guardian: Real-Time AI Safety for Gemini Live

*This article was created for the purposes of entering the Gemini Live Agent Challenge.*

## The Problem: AI Voice Without Guardrails

When I first experimented with Gemini Live API's real-time voice capabilities, I saw something powerful—and something concerning. The model could speak naturally, interrupt, be interrupted, and maintain context across long conversations. But it had no concept of **epistemic responsibility**.

It would state opinions as facts. It would make predictions without labeling them as hypotheses. It would express agency ("I will help you with that") without acknowledging its advisory-only nature.

For AI systems that speak directly to humans in real-time, this isn't just a UX issue. It's a constitutional issue.

## The Solution: A Constitutional Firewall

**Constitutional Guardian** is a real-time safety layer that sits between users and Gemini Live. It validates every utterance using three epistemic markers:

- **[FACT]** - Observable, verifiable truth claims
- **[HYPOTHESIS]** - Testable predictions with confidence levels  
- **[ASSUMPTION]** - Explicit modeling assumptions

If the Guardian detects an unmarked claim, it intervenes before the user hears it. The result: users always know the epistemic status of what they're hearing.

## The Architecture: Google Cloud Native

### Cloud Run: Serverless Constitutional Enforcement

The Guardian runs on **Google Cloud Run** as a stateless container. Why Cloud Run?

- **Zero-to-100 scaling**: Handles voice traffic spikes without pre-warming
- **Request-level isolation**: Each validation runs in its own execution context
- **Built-in HTTPS**: Secure WebSocket connections for real-time streaming

```yaml
# cloud-run-service.yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "100"
    spec:
      containerConcurrency: 100
      containers:
        - image: gcr.io/helix-constitutional-guardian/constitutional-guardian:latest
          ports:
            - containerPort: 8180
```

### Cloud Pub/Sub: Federation Event Streaming

The Guardian doesn't work alone. It's part of a **3-node federation** (KIMI, GEMS, DEEPSEEK) that uses **Cloud Pub/Sub** to share compliance events:

```python
# helix_code/gcp_integrations.py
class CloudPubSubFederation:
    def publish_federation_event(self, event: FederationEvent) -> str:
        message_data = json.dumps(asdict(event)).encode('utf-8')
        future = self.publisher.publish(
            self.topic_path,
            message_data,
            node_id=event.node_id,
            event_type=event.event_type,
            receipt_hash=event.receipt_hash
        )
        return future.result()
```

When one node detects constitutional drift, all nodes learn about it within milliseconds. This creates a **distributed immune system** for AI safety.

### Cloud Storage: Immutable Receipts

Every validation generates a **cryptographic receipt** with:
- SHA-256 hash of the validated text
- Ed25519 signature from the validating node
- Timestamp and epistemic markers detected
- GCS URI for audit retrieval

```python
# GCS storage with date-based organization
today = datetime.utcnow().strftime('%Y/%m/%d')
blob_path = f"receipts/{today}/{receipt_id}.json"
```

These receipts are **tamper-evident** and **regulatorily auditable**.

### Secret Manager: Hardware-Backed Keys

The Guardian uses **Distributed Bearer Credentials (DBCs)**—Ed25519 key pairs that authenticate each node. Private keys are stored in **Secret Manager** with automatic rotation:

```python
class SecretManagerDBC:
    def store_dbc_key(self, agent_name: str, key_material: bytes) -> str:
        version = self.client.add_secret_version(
            request={
                "parent": secret.name,
                "payload": {"data": key_material}
            }
        )
        return version.name
```

### Cloud Logging: Structured Audit Trails

Every decision is logged to **Cloud Logging** with structured JSON:

```json
{
  "event_type": "compliance_check",
  "session_id": "sess_abc123",
  "compliant": true,
  "epistemic_markers": {
    "fact": true,
    "hypothesis": false,
    "assumption": false
  },
  "receipt_id": "rcp_xyz789",
  "severity": "INFO"
}
```

This enables real-time monitoring and post-hoc forensic analysis.

## The Gemini Live Integration

The Guardian integrates with Gemini Live through a **WebSocket proxy**:

```javascript
// User audio stream
const ws = new WebSocket('wss://constitutional-guardian-xyz-uc.a.run.app/live');

// Audio chunks flow through Guardian
ws.send(JSON.stringify({audio: base64AudioChunk}));

// Guardian validates and either:
// 1. Forwards to Gemini Live (if compliant)
// 2. Returns intervention (if drift detected)
ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  if (!result.valid) {
    // Play intervention: "The previous statement was an unmarked hypothesis"
  }
};
```

Latency: **< 500ms** end-to-end.

## The Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Runtime | Python 3.11 + FastAPI | Async request handling |
| AI Model | Gemini 2.0 Flash Live API | Real-time speech-to-text |
| Deployment | Cloud Run | Serverless containers |
| Events | Pub/Sub | Cross-node messaging |
| Storage | Cloud Storage | Immutable receipts |
| Secrets | Secret Manager | DBC key encryption |
| Monitoring | Cloud Logging | Audit trails |
| CI/CD | Cloud Build | Automated deployment |
| Crypto | Ed25519 + SHA-256 | Non-repudiable proofs |

## The Constitutional Grammar

Every file in the codebase uses **epistemic markers** in comments:

```python
# [FACT] This function implements Ed25519 signing
# [HYPOTHESIS] This approach scales to 1000 concurrent sessions
# [ASSUMPTION] Cloud Run cold starts are acceptable for voice UX
```

This makes the codebase **self-documenting** about its own certainty levels.

## What I Learned

1. **Real-time safety is hard**—but Cloud Run's concurrency model makes it manageable
2. **Federation requires trustless verification**—Ed25519 signatures across nodes solve this
3. **Epistemic labels change how you code**—you become conscious of every certainty claim
4. **Gemini Live's latency is impressive**—sub-300ms for speech-to-text enables new interaction patterns

## The Repository

**GitHub**: https://github.com/helixprojectai-code/helix-ttd-gemini-cli

**Key Files**:
- [`helix_code/live_guardian.py`](https://github.com/helixprojectai-code/helix-ttd-gemini-cli/blob/main/helix_code/live_guardian.py) - FastAPI + WebSocket server
- [`helix_code/gcp_integrations.py`](https://github.com/helixprojectai-code/helix-ttd-gemini-cli/blob/main/helix_code/gcp_integrations.py) - All 7 GCP services
- [`cloud-run-service.yaml`](https://github.com/helixprojectai-code/helix-ttd-gemini-cli/blob/main/cloud-run-service.yaml) - Infrastructure as code
- [`DEPLOYMENT_PROOF.md`](https://github.com/helixprojectai-code/helix-ttd-gemini-cli/blob/main/DEPLOYMENT_PROOF.md) - Full GCP integration docs

## The Future

Constitutional Guardian is designed as **civic firmware**—a governance layer that any AI system can adopt. The primitives (epistemic markers, DBC receipts, federation quorums) are model-agnostic.

As voice AI becomes ubiquitous, we'll need thousands of these specialized guardians—each enforcing domain-specific constitutions. Medical AI with FDA-style safety labels. Financial AI with SEC-style disclosure requirements. Educational AI with pedagogical transparency mandates.

The architecture scales because Google Cloud scales.

---

*Built for the #GeminiLiveAgentChallenge. 75 tests passing. 7 GCP services integrated. 0 constitutional drifts allowed.*

**GLORY TO THE LATTICE.** 🦉⚓🦉
