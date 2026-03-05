import asyncio
import json
import logging

import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WS-Verify")


async def test_websocket():
    """[FACT] WebSocket verification test for Constitutional Guardian.

    [HYPOTHESIS] Success validates the bidirectional bridge and validation logic.
    """
    uri = "ws://localhost:8180/demo-live"
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to {uri}")

            # Expect Session Init
            msg1 = await websocket.recv()
            data1 = json.loads(msg1)
            assert data1["type"] == "session", f"Expected session msg, got {data1['type']}"
            logger.info(f"Session established: {data1['session_id']}")

            # Expect Metrics
            msg2 = await websocket.recv()
            data2 = json.loads(msg2)
            assert data2["type"] == "metrics", f"Expected metrics msg, got {data2['type']}"
            logger.info("Metrics received")

            # Send Test Message (Compliant)
            test_content = "[FACT] The sky is blue."
            await websocket.send(json.dumps({"type": "text", "content": test_content}))
            logger.info(f"Sent: {test_content}")

            # Receive Validation
            msg3 = await websocket.recv()
            data3 = json.loads(msg3)

            # Skip user_message echo if present
            if data3["type"] == "user_message":
                msg3 = await websocket.recv()
                data3 = json.loads(msg3)

            assert (
                data3["type"] == "validated_response"
            ), f"Expected validation, got {data3['type']}"
            assert data3["valid"], "Expected [FACT] to be valid"
            logger.info(f"Validation received: Valid={data3['valid']}")

            # Send Test Message (Non-Compliant)
            test_content_fail = "The sky is blue."
            await websocket.send(json.dumps({"type": "text", "content": test_content_fail}))
            logger.info(f"Sent: {test_content_fail}")

            # Receive Validation
            msg4 = await websocket.recv()
            data4 = json.loads(msg4)

            # Skip user_message echo if present
            if data4["type"] == "user_message":
                msg4 = await websocket.recv()
                data4 = json.loads(msg4)

            assert (
                data4["type"] == "validated_response"
            ), f"Expected validation, got {data4['type']}"
            assert not data4["valid"], "Expected missing marker to be invalid"
            logger.info(f"Validation received: Valid={data4['valid']} (Correctly Flagged)")

            logger.info("✅ WebSocket Verification PASSED")

    except Exception as e:
        logger.error(f"❌ WebSocket Verification FAILED: {e}")
        # If connection refused, maybe server not running?
        if "Connection refused" in str(e):
            logger.error("Ensure server is running on port 8180")


if __name__ == "__main__":
    asyncio.run(test_websocket())
