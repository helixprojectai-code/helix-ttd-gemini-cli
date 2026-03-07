"""[FACT] Tests for Live Multimodal Auditing pipeline.

[HYPOTHESIS] Audio chunk ingestion, transcription, and validation
can be tested independently of actual audio hardware.
"""

from __future__ import annotations

import base64
import sys
import time
from pathlib import Path
from unittest.mock import Mock

import pytest

# [FACT] Add helix_code to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from audio_auditor import (
    AudioAuditor,
    AudioAuditSession,
    AudioChunk,
    TranscriptionSegment,
    create_audio_auditor,
)


class TestAudioChunk:
    """[FACT] Unit tests for AudioChunk dataclass."""

    def test_chunk_creation(self) -> None:
        """[FACT] AudioChunk stores PCM data with metadata."""
        chunk = AudioChunk(
            timestamp=time.time(),
            pcm_data=b"\x00\x01\x02\x03",
            sequence_num=0,
            duration_ms=100.0,
        )
        assert chunk.sequence_num == 0
        assert chunk.duration_ms == 100.0
        assert len(chunk.pcm_data) == 4


class TestTranscriptionSegment:
    """[FACT] Unit tests for TranscriptionSegment dataclass."""

    def test_segment_creation(self) -> None:
        """[FACT] Segment stores transcription with validation results."""
        segment = TranscriptionSegment(
            text="Hello world",
            start_time=time.time(),
            end_time=time.time() + 1.0,
            is_final=True,
            confidence=0.95,
            validation_result={"valid": True, "intervention_required": False},
            receipt_id="r_test_123",
        )
        assert segment.text == "Hello world"
        assert segment.confidence == 0.95
        assert segment.receipt_id == "r_test_123"


class TestAudioAuditSession:
    """[FACT] Unit tests for AudioAuditSession."""

    def test_session_initialization(self) -> None:
        """[FACT] Session initializes with default parameters."""
        from datetime import datetime

        session = AudioAuditSession(
            session_id="test_session",
            created_at=datetime.utcnow(),
        )
        assert session.sample_rate == 16000
        assert session.channels == 1
        assert len(session.audio_buffer) == 0
        assert session.guardian is not None

    def test_session_callbacks(self) -> None:
        """[FACT] Session can store callback functions."""
        from datetime import datetime

        mock_callback = Mock()
        session = AudioAuditSession(
            session_id="test_session",
            created_at=datetime.utcnow(),
            on_transcription=mock_callback,
        )
        assert session.on_transcription is mock_callback


class TestAudioAuditor:
    """[FACT] Integration tests for AudioAuditor."""

    @pytest.fixture
    def auditor(self) -> AudioAuditor:
        """[FACT] Create fresh auditor for each test."""
        auditor = create_audio_auditor(api_key="test_key")
        auditor.enable_simulation_fallback = True
        return auditor

    @pytest.mark.anyio
    async def test_create_session(self, auditor: AudioAuditor) -> None:
        """[FACT] Can create and retrieve audit session."""
        session = await auditor.create_session("test_123")
        assert session.session_id == "test_123"
        assert "test_123" in auditor.sessions

    @pytest.mark.anyio
    async def test_ingest_audio_chunk(self, auditor: AudioAuditor) -> None:
        """[FACT] Can ingest base64-encoded PCM audio."""
        await auditor.create_session("test_123")

        # [FACT] Create fake PCM data (16-bit samples)
        pcm_data = b"\x00\x00\x01\x00\x02\x00\x03\x00"  # 4 samples
        base64_pcm = base64.b64encode(pcm_data).decode()

        result = await auditor.ingest_audio_chunk("test_123", base64_pcm)

        assert result["status"] == "accepted"
        assert result["chunk_num"] == 0
        assert result["buffer_size"] == 1

    @pytest.mark.anyio
    async def test_ingest_invalid_session(self, auditor: AudioAuditor) -> None:
        """[FACT] Returns error for non-existent session."""
        result = await auditor.ingest_audio_chunk("nonexistent", "dGVzdA==")
        assert result["status"] == "error"
        assert "not found" in result["error"]

    @pytest.mark.anyio
    async def test_ingest_invalid_base64(self, auditor: AudioAuditor) -> None:
        """[FACT] Handles invalid base64 gracefully."""
        await auditor.create_session("test_123")
        result = await auditor.ingest_audio_chunk("test_123", "!!!invalid!!!")
        assert result["status"] == "error"

    @pytest.mark.anyio
    async def test_ingest_rejects_oversized_payload(self, auditor: AudioAuditor) -> None:
        """[FACT] Oversized base64 payload is rejected before decode."""
        await auditor.create_session("test_oversize")
        auditor.max_base64_chars = 12

        result = await auditor.ingest_audio_chunk("test_oversize", "A" * 20)

        assert result["status"] == "error"
        assert result["error_code"] == "PAYLOAD_TOO_LARGE"

    @pytest.mark.anyio
    async def test_ingest_rate_limited(self, auditor: AudioAuditor) -> None:
        """[FACT] Session ingest is rate-limited to protect service budget."""
        await auditor.create_session("test_rate")
        auditor.rate_window_seconds = 60.0
        auditor.max_chunks_per_window = 2

        pcm_data = b"\x00\x00" * 10
        base64_pcm = base64.b64encode(pcm_data).decode()

        ok1 = await auditor.ingest_audio_chunk("test_rate", base64_pcm)
        ok2 = await auditor.ingest_audio_chunk("test_rate", base64_pcm)
        blocked = await auditor.ingest_audio_chunk("test_rate", base64_pcm)

        assert ok1["status"] == "accepted"
        assert ok2["status"] == "accepted"
        assert blocked["status"] == "error"
        assert blocked["error_code"] == "RATE_LIMITED"

    @pytest.mark.anyio
    async def test_handle_gemini_response_ignores_non_text(self, auditor: AudioAuditor) -> None:
        """[FACT] Non-text Gemini events are ignored, not stringified into transcripts."""
        session = await auditor.create_session("test_non_text")

        await auditor._handle_gemini_response(session, {"event": "metadata_only"})

        assert len(session.segments) == 0

    @pytest.mark.anyio
    async def test_handle_gemini_response_uses_input_transcription(
        self, auditor: AudioAuditor
    ) -> None:
        """[FACT] Input transcription events are converted into validated segments."""
        session = await auditor.create_session("test_input_tx")

        await auditor._handle_gemini_response(
            session,
            {"server_content": {"input_transcription": {"text": "hello audio world"}}},
        )

        assert len(session.segments) == 1
        assert session.segments[0].text == "hello audio world"

    @pytest.mark.anyio
    async def test_process_turn_empty_buffer(self, auditor: AudioAuditor) -> None:
        """[FACT] Handles empty buffer gracefully."""
        await auditor.create_session("test_123")
        result = await auditor.process_turn("test_123")
        assert result["status"] == "no_audio"

    @pytest.mark.anyio
    async def test_process_turn_no_transcript_when_simulation_disabled(
        self, auditor: AudioAuditor
    ) -> None:
        """[FACT] No synthetic transcript is generated when simulation is disabled."""
        auditor.enable_simulation_fallback = False
        await auditor.create_session("test_no_transcript")

        pcm_data = b"\x00\x00" * 1600
        base64_pcm = base64.b64encode(pcm_data).decode()
        await auditor.ingest_audio_chunk("test_no_transcript", base64_pcm)

        result = await auditor.process_turn("test_no_transcript")
        assert result["status"] == "no_transcript_available"
        assert result["error_code"] == "NO_TRANSCRIPT_AVAILABLE"

    @pytest.mark.anyio
    async def test_detect_turn_end_threshold(self, auditor: AudioAuditor) -> None:
        """[FACT] Turn detection triggers after ~2 seconds of audio."""
        session = await auditor.create_session("test_123")

        # [FACT] Add chunks until threshold
        for i in range(20):
            pcm_data = b"\x00\x00" * 1600  # 100ms @ 16kHz
            base64_pcm = base64.b64encode(pcm_data).decode()
            result = await auditor.ingest_audio_chunk("test_123", base64_pcm)

        assert result["should_process"] is True

    @pytest.mark.anyio
    async def test_close_session(self, auditor: AudioAuditor) -> None:
        """[FACT] Session cleanup removes from active sessions."""
        await auditor.create_session("test_123")
        assert "test_123" in auditor.sessions

        await auditor.close_session("test_123")
        assert "test_123" not in auditor.sessions

    @pytest.mark.anyio
    async def test_get_session_stats(self, auditor: AudioAuditor) -> None:
        """[FACT] Stats reflect session activity."""
        session = await auditor.create_session("test_123")

        # Add some audio
        pcm_data = b"\x00\x00" * 1600
        base64_pcm = base64.b64encode(pcm_data).decode()
        await auditor.ingest_audio_chunk("test_123", base64_pcm)

        stats = auditor.get_session_stats("test_123")
        assert stats["total_chunks"] == 1
        assert stats["session_id"] == "test_123"

    def test_get_stats_invalid_session(self, auditor: AudioAuditor) -> None:
        """[FACT] Returns error for invalid session stats request."""
        stats = auditor.get_session_stats("nonexistent")
        assert "error" in stats


class TestAudioAuditorIntegration:
    """[FACT] Integration tests with mocked Gemini API."""

    @pytest.mark.anyio
    async def test_full_pipeline_simulation(self) -> None:
        """[FACT] End-to-end audio -> transcription -> validation pipeline."""
        auditor = create_audio_auditor()
        auditor.enable_simulation_fallback = True
        callbacks: list[dict] = []

        def on_transcription(segment: TranscriptionSegment) -> None:
            callbacks.append({"type": "transcription", "text": segment.text})

        def on_intervention(text: str, drift_code: str) -> None:
            callbacks.append({"type": "intervention", "drift_code": drift_code})

        session = await auditor.create_session(
            "integration_test",
            on_transcription=on_transcription,
            on_intervention=on_intervention,
        )

        # [FACT] Simulate audio input (20 chunks = ~2 seconds)
        for _ in range(20):
            pcm_data = b"\x00\x00" * 1600
            base64_pcm = base64.b64encode(pcm_data).decode()
            await auditor.ingest_audio_chunk("integration_test", base64_pcm)

        # Process the turn
        result = await auditor.process_turn("integration_test")

        # [FACT] Should have processed and created a segment
        assert result["status"] == "processed"
        assert len(session.segments) == 1

        # Cleanup
        await auditor.close_session("integration_test")


class TestAudioAuditorCallbacks:
    """[FACT] Test callback invocation."""

    @pytest.mark.anyio
    async def test_transcription_callback(self) -> None:
        """[FACT] Callback invoked on transcription completion."""
        received: list[str] = []

        def callback(segment: TranscriptionSegment) -> None:
            received.append(segment.text)

        auditor = create_audio_auditor()
        auditor.enable_simulation_fallback = True
        await auditor.create_session("cb_test", on_transcription=callback)

        # Add audio and process
        for _ in range(20):
            pcm_data = b"\x00\x00" * 1600
            base64_pcm = base64.b64encode(pcm_data).decode()
            await auditor.ingest_audio_chunk("cb_test", base64_pcm)

        await auditor.process_turn("cb_test")

        # [FACT] Callback should have been invoked
        assert len(received) == 1
        assert isinstance(received[0], str)


class TestEdgeCases:
    """[FACT] Edge case handling."""

    @pytest.mark.anyio
    async def test_very_small_chunks(self) -> None:
        """[FACT] Handles very small audio chunks."""
        auditor = create_audio_auditor()
        await auditor.create_session("small_test")

        # 1 sample = 2 bytes
        pcm_data = b"\x00\x00"
        base64_pcm = base64.b64encode(pcm_data).decode()

        result = await auditor.ingest_audio_chunk("small_test", base64_pcm)
        assert result["status"] == "accepted"
        assert result["duration_ms"] < 1  # Very short

    @pytest.mark.anyio
    async def test_large_base64_payload(self) -> None:
        """[FACT] Handles reasonably large audio payloads."""
        auditor = create_audio_auditor()
        await auditor.create_session("large_test")

        # 1 second of 16kHz audio = 32000 bytes
        pcm_data = b"\x00\x00" * 16000
        base64_pcm = base64.b64encode(pcm_data).decode()

        result = await auditor.ingest_audio_chunk("large_test", base64_pcm)
        assert result["status"] == "accepted"
        assert result["duration_ms"] == 1000.0
