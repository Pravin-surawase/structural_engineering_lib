#!/usr/bin/env python3
"""
Python Test Client for FastAPI Live Design Endpoints.

Demonstrates how to use:
- WebSocket for interactive design (bi-directional)
- SSE for batch design (server → client stream)

Usage:
    # Start the server first:
    uvicorn fastapi_app.main:app --reload --host 127.0.0.1 --port 8000

    # Then run this client:
    python fastapi_app/examples/test_client.py

Week 3 Implementation - V3 Migration
"""

from __future__ import annotations

import asyncio
import json
import os
from urllib.parse import quote

import httpx

# Default server URL
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"
REQUEST_TIMEOUT_SECONDS = 30.0
WS_ACCESS_TOKEN = os.environ.get("WS_ACCESS_TOKEN")


# =============================================================================
# WebSocket Client
# =============================================================================


async def test_websocket_design():
    """
    Test WebSocket live design endpoint.

    Demonstrates:
    - Connection lifecycle
    - Sending design requests
    - Receiving instant results
    """
    try:
        import websockets
    except ImportError:
        print("❌ websockets package not installed. Run: pip install websockets")
        return
    if not WS_ACCESS_TOKEN:
        print("❌ Set WS_ACCESS_TOKEN to a JWT with the design scope.")
        return

    print("\n" + "=" * 60)
    print("🔌 Testing WebSocket Live Design")
    print("=" * 60)

    uri = f"{WS_URL}/ws/design/test-client-1?token={quote(WS_ACCESS_TOKEN)}"

    try:
        async with websockets.connect(uri) as ws:
            print(f"✅ Connected to {uri}")

            # Test 1: Ping
            print("\n📤 Sending ping...")
            await ws.send(json.dumps({"type": "ping"}))
            response = await ws.recv()
            data = json.loads(response)
            print(f"📥 Received: {data['type']} at {data['timestamp']}")

            # Test 2: Design beam
            beam_params = {
                "width": 300,
                "depth": 500,
                "moment": 150,
                "shear": 75,
                "fck": 25,
                "fy": 500,
            }
            print(f"\n📤 Designing beam: {beam_params}")
            await ws.send(json.dumps({"type": "design_beam", "params": beam_params}))
            response = await ws.recv()
            data = json.loads(response)

            print(f"📥 Result in {data['latency_ms']:.1f}ms:")
            print(f"   Ast required: {data['data']['flexure']['ast_required']:.1f} mm²")
            print(f"   Safe: {data['data']['flexure']['is_safe']}")

            # Test 3: Another design with higher moment
            beam_params["moment"] = 250
            print(
                f"\n📤 Designing beam with higher moment: {beam_params['moment']} kN·m"
            )
            await ws.send(json.dumps({"type": "design_beam", "params": beam_params}))
            response = await ws.recv()
            data = json.loads(response)

            print(f"📥 Result in {data['latency_ms']:.1f}ms:")
            print(f"   Ast required: {data['data']['flexure']['ast_required']:.1f} mm²")

            print("\n✅ WebSocket test complete!")

    except ConnectionRefusedError:
        print(f"❌ Could not connect to {uri}")
        print(
            "   Make sure the server is running: uvicorn fastapi_app.main:app --reload"
        )


# =============================================================================
# SSE Client
# =============================================================================


async def test_sse_batch_design():
    """
    Test SSE batch design endpoint.

    Demonstrates:
    - Streaming multiple beam designs
    - Progress tracking
    - Event parsing
    """
    print("\n" + "=" * 60)
    print("📡 Testing SSE Batch Design")
    print("=" * 60)

    beams = [
        {"id": "B1", "width": 300, "depth": 500, "moment": 100, "fck": 25, "fy": 500},
        {"id": "B2", "width": 350, "depth": 550, "moment": 150, "fck": 25, "fy": 500},
        {"id": "B3", "width": 400, "depth": 600, "moment": 200, "fck": 30, "fy": 500},
        {"id": "B4", "width": 300, "depth": 500, "moment": 120, "fck": 25, "fy": 500},
        {"id": "B5", "width": 350, "depth": 600, "moment": 180, "fck": 30, "fy": 500},
    ]

    beams_json = json.dumps(beams)
    url = f"{BASE_URL}/stream/batch-design?beams={quote(beams_json)}"

    print(f"📤 Designing {len(beams)} beams via SSE...")
    print()

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            async with client.stream("GET", url) as response:
                current_event = None

                async for line in response.aiter_lines():
                    if line.startswith("event:"):
                        current_event = line.split(":")[1].strip()
                    elif line.startswith("data:"):
                        data = json.loads(line[5:].strip())

                        if current_event == "start":
                            print(
                                f"🚀 Job started: {data['job_id']} ({data['total']} beams)"
                            )

                        elif current_event == "design_result":
                            status = "✅" if data["status"] == "PASS" else "❌"
                            print(
                                f"   {status} {data['beam_id']}: Ast={data['flexure']['ast_required']:.0f} mm²"
                            )

                        elif current_event == "progress":
                            pct = data["percent"]
                            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                            print(f"   [{bar}] {pct:.0f}%", end="\r")

                        elif current_event == "complete":
                            print()
                            print("\n✅ Batch complete!")
                            print(f"   Total: {data['completed']}/{data['total']}")
                            print(f"   Failed: {data['failed']}")
                            print(f"   Duration: {data['duration_seconds']:.2f}s")

                        elif current_event == "error":
                            print(
                                f"   ❌ Error: {data.get('message', 'Unknown error')}"
                            )

                        current_event = None

        print("\n✅ SSE test complete!")

    except httpx.ConnectError:
        print(f"❌ Could not connect to {BASE_URL}")
        print(
            "   Make sure the server is running: uvicorn fastapi_app.main:app --reload"
        )


# =============================================================================
# REST API Test
# =============================================================================


async def test_rest_endpoints():
    """Test basic REST endpoints."""
    print("\n" + "=" * 60)
    print("🌐 Testing REST Endpoints")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        try:
            # Health check
            print("\n📤 GET /health")
            response = await client.get(f"{BASE_URL}/health")
            print(f"📥 {response.status_code}: {response.json()['status']}")

            # Design beam
            print("\n📤 POST /api/v1/design/beam")
            response = await client.post(
                f"{BASE_URL}/api/v1/design/beam",
                json={
                    "width": 300,
                    "depth": 500,
                    "moment": 150,
                    "shear": 75,
                    "fck": 25,
                    "fy": 500,
                    "clear_cover": 25,
                    "stirrup_dia_mm": 8,
                    "main_bar_dia_mm": 20,
                },
            )
            if response.status_code == 200:
                data = response.json()["data"]
                print(
                    f"📥 {response.status_code}: Ast={data['flexure']['ast_required']:.1f} mm²"
                )
            else:
                print(f"📥 {response.status_code}: {response.json()}")

            print("\n✅ REST test complete!")

        except httpx.ConnectError:
            print(f"❌ Could not connect to {BASE_URL}")
            print(
                "   Make sure the server is running: uvicorn fastapi_app.main:app --reload"
            )


# =============================================================================
# Main
# =============================================================================


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 FastAPI Live Design Test Client")
    print("=" * 60)
    print(f"\nServer: {BASE_URL}")
    print("Make sure the server is running before testing!")

    # Test REST
    await test_rest_endpoints()

    # Test SSE
    await test_sse_batch_design()

    # Test WebSocket (requires websockets package)
    await test_websocket_design()

    print("\n" + "=" * 60)
    print("🎉 All tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
