"""[FACT] Tests for GCP integration configuration behavior."""

from types import SimpleNamespace

import helix_code.gcp_integrations as gcp_integrations


class _FakePublisher:
    def topic_path(self, project_id: str, topic_name: str) -> str:
        return f"projects/{project_id}/topics/{topic_name}"


class _FakeSubscriber:
    def subscription_path(self, project_id: str, subscription_name: str) -> str:
        return f"projects/{project_id}/subscriptions/{subscription_name}"


def test_pubsub_topic_defaults_to_helix_events(monkeypatch) -> None:
    """[FACT] Default topic resolves to helix-events when PUBSUB_TOPIC is unset."""
    fake_module = SimpleNamespace(
        PublisherClient=lambda: _FakePublisher(),
        SubscriberClient=lambda: _FakeSubscriber(),
    )

    monkeypatch.setattr(gcp_integrations, "GCP_AVAILABLE", True)
    monkeypatch.setattr(gcp_integrations, "pubsub_v1", fake_module, raising=False)
    monkeypatch.delenv("PUBSUB_TOPIC", raising=False)

    pubsub = gcp_integrations.CloudPubSubFederation(project_id="helix-ai-deploy")

    assert pubsub.topic_name == "helix-events"
    assert pubsub.topic_path == "projects/helix-ai-deploy/topics/helix-events"


def test_pubsub_topic_accepts_fully_qualified_path(monkeypatch) -> None:
    """[FACT] Fully qualified PUBSUB_TOPIC path should be preserved."""
    fake_module = SimpleNamespace(
        PublisherClient=lambda: _FakePublisher(),
        SubscriberClient=lambda: _FakeSubscriber(),
    )

    monkeypatch.setattr(gcp_integrations, "GCP_AVAILABLE", True)
    monkeypatch.setattr(gcp_integrations, "pubsub_v1", fake_module, raising=False)
    monkeypatch.setenv("PUBSUB_TOPIC", "projects/helix-ai-deploy/topics/helix-events")

    pubsub = gcp_integrations.CloudPubSubFederation(project_id="helix-ai-deploy")

    assert pubsub.topic_name == "helix-events"
    assert pubsub.topic_path == "projects/helix-ai-deploy/topics/helix-events"
