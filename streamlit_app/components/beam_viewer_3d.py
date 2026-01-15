# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Beam 3D Viewer Component — Streamlit Integration

This module provides a Streamlit component for rendering 3D beam
visualizations using an embedded Three.js viewer via iframe.

Architecture:
    ┌─────────────────────┐
    │ Streamlit App       │
    │                     │
    │  ┌───────────────┐  │
    │  │ beam_viewer_3d│  │  ← Python wrapper (this file)
    │  └───────────────┘  │
    │         │           │
    │         ▼           │
    │  ┌───────────────┐  │
    │  │ <iframe>      │  │  ← HTML/JS viewer
    │  │ Three.js      │  │
    │  └───────────────┘  │
    └─────────────────────┘

Communication:
    - Python → JS: postMessage with BEAM_GEOMETRY payload
    - JS → Python: postMessage events (VIEWER_READY, RENDER_COMPLETE)

Usage:
    >>> from streamlit_app.components.beam_viewer_3d import render_beam_3d
    >>> render_beam_3d(geometry_dict, height=600)

Note:
    This is a POC (Proof of Concept) for Streamlit Cloud compatibility.
    Production version will use a bundled React/Three.js component.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import streamlit as st
import streamlit.components.v1 as components

if TYPE_CHECKING:
    from structural_lib.visualization.geometry_3d import Beam3DGeometry


# Path to the static HTML viewer
VIEWER_HTML_PATH = Path(__file__).parent.parent / "static" / "beam_viewer_3d.html"


def render_beam_3d(
    geometry: dict[str, Any] | Beam3DGeometry,
    height: int = 600,
    key: str | None = None,
) -> None:
    """
    Render a 3D beam visualization in Streamlit.

    This component embeds a Three.js viewer via iframe and sends
    beam geometry data via postMessage.

    Args:
        geometry: Either a dict matching BeamGeometry3D schema,
                  or a Beam3DGeometry object with to_dict() method.
        height: Height of the viewer in pixels (default: 600).
        key: Optional Streamlit key for the component.

    Example:
        >>> from structural_lib.visualization.geometry_3d import beam_to_3d_geometry
        >>> geometry = beam_to_3d_geometry(detailing_result)
        >>> render_beam_3d(geometry, height=700)

    Notes:
        - Viewer is responsive to container width
        - Supports mouse interaction: drag to rotate, scroll to zoom
        - Works on Streamlit Cloud (tested with iframe + postMessage)
    """
    # Convert to dict if needed
    if hasattr(geometry, "to_dict"):
        geometry_dict = geometry.to_dict()
    else:
        geometry_dict = geometry

    # Serialize geometry to JSON
    geometry_json = json.dumps(geometry_dict)

    # Generate the HTML with embedded geometry
    html_content = _generate_viewer_html(geometry_json, height)

    # Render component
    components.html(
        html_content,
        height=height,
        scrolling=False,
        key=key,
    )


def _generate_viewer_html(geometry_json: str, height: int) -> str:
    """
    Generate the complete HTML for the viewer with embedded geometry.

    This embeds the geometry directly in the HTML to avoid CORS issues
    and postMessage timing problems on Streamlit Cloud.
    """
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{
      width: 100%;
      height: {height}px;
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #1a1a2e;
    }}
    #container {{ width: 100%; height: 100%; position: relative; }}
    #canvas {{ width: 100%; height: 100%; display: block; }}
    #info-panel {{
      position: absolute;
      top: 10px;
      left: 10px;
      background: rgba(0, 0, 0, 0.75);
      color: #fff;
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 13px;
      max-width: 260px;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    #info-panel h3 {{
      margin: 0 0 8px 0;
      font-size: 14px;
      color: #4fc3f7;
      font-weight: 600;
    }}
    #info-panel .stat {{
      display: flex;
      justify-content: space-between;
      margin: 4px 0;
      color: #bbb;
    }}
    #info-panel .stat-value {{
      color: #fff;
      font-weight: 500;
    }}
    #controls {{
      position: absolute;
      bottom: 10px;
      right: 10px;
      background: rgba(0, 0, 0, 0.6);
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 11px;
      color: #888;
    }}
    .legend {{
      display: flex;
      gap: 12px;
      margin-top: 10px;
      padding-top: 8px;
      border-top: 1px solid rgba(255,255,255,0.1);
      font-size: 11px;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 4px;
    }}
    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 2px;
    }}
    .legend-dot.bottom {{ background: #e53935; }}
    .legend-dot.top {{ background: #1e88e5; }}
    .legend-dot.stirrup {{ background: #43a047; }}
  </style>
</head>
<body>
  <div id="container">
    <canvas id="canvas"></canvas>
    <div id="info-panel">
      <h3 id="beam-id">Loading...</h3>
      <div class="stat"><span>Width (b):</span><span class="stat-value" id="dim-b">-</span></div>
      <div class="stat"><span>Depth (D):</span><span class="stat-value" id="dim-d">-</span></div>
      <div class="stat"><span>Span:</span><span class="stat-value" id="dim-span">-</span></div>
      <div class="stat"><span>Rebars:</span><span class="stat-value" id="rebar-count">-</span></div>
      <div class="stat"><span>Stirrups:</span><span class="stat-value" id="stirrup-count">-</span></div>
      <div class="legend">
        <div class="legend-item"><div class="legend-dot bottom"></div>Bottom</div>
        <div class="legend-item"><div class="legend-dot top"></div>Top</div>
        <div class="legend-item"><div class="legend-dot stirrup"></div>Stirrup</div>
      </div>
    </div>
    <div id="controls">🖱️ Drag: rotate | Scroll: zoom | Right-click: pan</div>
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

  <script>
    // Embedded geometry data
    const BEAM_GEOMETRY = {geometry_json};

    let scene, camera, renderer, controls;
    let beamGroup = null;

    const MATERIALS = {{
      concrete: new THREE.MeshLambertMaterial({{
        color: 0x888888,
        transparent: true,
        opacity: 0.25,
        side: THREE.DoubleSide
      }}),
      concreteWireframe: new THREE.LineBasicMaterial({{
        color: 0x666666,
        transparent: true,
        opacity: 0.6
      }}),
      rebarBottom: new THREE.MeshPhongMaterial({{
        color: 0xe53935,
        shininess: 100
      }}),
      rebarTop: new THREE.MeshPhongMaterial({{
        color: 0x1e88e5,
        shininess: 100
      }}),
      stirrup: new THREE.MeshPhongMaterial({{
        color: 0x43a047,
        shininess: 80
      }})
    }};

    function init() {{
      const container = document.getElementById('container');
      const canvas = document.getElementById('canvas');

      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x1a1a2e);

      const aspect = container.clientWidth / container.clientHeight;
      camera = new THREE.PerspectiveCamera(45, aspect, 1, 100000);
      camera.position.set(3000, 2000, 2000);

      renderer = new THREE.WebGLRenderer({{
        canvas: canvas,
        antialias: true,
        alpha: true
      }});
      renderer.setSize(container.clientWidth, container.clientHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.minDistance = 100;
      controls.maxDistance = 20000;

      // Lighting
      scene.add(new THREE.AmbientLight(0xffffff, 0.6));
      const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
      dirLight.position.set(2000, 3000, 1500);
      scene.add(dirLight);
      scene.add(new THREE.DirectionalLight(0xffffff, 0.3).position.set(-1000, 1000, -1000));

      window.addEventListener('resize', onWindowResize);

      // Render the beam immediately
      renderBeam(BEAM_GEOMETRY);

      animate();
    }}

    function onWindowResize() {{
      const container = document.getElementById('container');
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    }}

    function animate() {{
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }}

    function renderBeam(geometry) {{
      if (beamGroup) {{
        scene.remove(beamGroup);
      }}

      beamGroup = new THREE.Group();

      // Concrete
      const {{ b, D, span }} = geometry.dimensions;
      const boxGeo = new THREE.BoxGeometry(span, b, D);
      const mesh = new THREE.Mesh(boxGeo, MATERIALS.concrete);
      mesh.position.set(span / 2, 0, D / 2);
      beamGroup.add(mesh);

      const edges = new THREE.EdgesGeometry(boxGeo);
      const wireframe = new THREE.LineSegments(edges, MATERIALS.concreteWireframe);
      wireframe.position.copy(mesh.position);
      beamGroup.add(wireframe);

      // Rebars
      if (geometry.rebars) {{
        geometry.rebars.forEach(rebar => {{
          const material = rebar.barType === 'top' ? MATERIALS.rebarTop : MATERIALS.rebarBottom;
          rebar.segments.forEach(seg => {{
            const start = new THREE.Vector3(seg.start.x, seg.start.y, seg.start.z);
            const end = new THREE.Vector3(seg.end.x, seg.end.y, seg.end.z);
            const dir = new THREE.Vector3().subVectors(end, start);
            const len = dir.length();
            dir.normalize();

            const radius = seg.diameter / 2;
            const cylGeo = new THREE.CylinderGeometry(radius, radius, len, 16);
            cylGeo.rotateZ(Math.PI / 2);

            const cylMesh = new THREE.Mesh(cylGeo, material);
            cylMesh.position.copy(new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5));

            const axis = new THREE.Vector3(1, 0, 0);
            cylMesh.quaternion.setFromUnitVectors(axis, dir);

            beamGroup.add(cylMesh);
          }});
        }});
      }}

      // Stirrups
      if (geometry.stirrups) {{
        geometry.stirrups.forEach(stirrup => {{
          if (!stirrup.path || stirrup.path.length < 3) return;

          const radius = stirrup.diameter / 2;
          const points = stirrup.path.map(p => new THREE.Vector3(p.x, p.y, p.z));
          points.push(points[0].clone());

          const curve = new THREE.CatmullRomCurve3(points, false);
          const tubeGeo = new THREE.TubeGeometry(curve, 32, radius, 8, true);
          beamGroup.add(new THREE.Mesh(tubeGeo, MATERIALS.stirrup));
        }});
      }}

      beamGroup.position.x = -span / 2;
      scene.add(beamGroup);

      // Camera
      camera.position.set(span * 0.6, b * 2, D * 2);
      controls.target.set(0, 0, D / 2);
      controls.update();

      // Update info
      document.getElementById('beam-id').textContent = `Beam ${{geometry.beamId}} (${{geometry.story}})`;
      document.getElementById('dim-b').textContent = `${{b}} mm`;
      document.getElementById('dim-d').textContent = `${{D}} mm`;
      document.getElementById('dim-span').textContent = `${{span}} mm`;
      document.getElementById('rebar-count').textContent = geometry.rebars ? geometry.rebars.length : 0;
      document.getElementById('stirrup-count').textContent = geometry.stirrups ? geometry.stirrups.length : 0;
    }}

    window.addEventListener('load', init);
  </script>
</body>
</html>
'''


def render_beam_3d_from_detailing(
    detailing: Any,
    is_seismic: bool = False,
    height: int = 600,
    key: str | None = None,
) -> None:
    """
    Convenience function to render 3D view directly from BeamDetailingResult.

    Args:
        detailing: BeamDetailingResult from detailing module.
        is_seismic: True to use 135° stirrup hooks.
        height: Height of viewer in pixels.
        key: Optional Streamlit key.

    Example:
        >>> from structural_lib.codes.is456.detailing import create_beam_detailing
        >>> detailing = create_beam_detailing(...)
        >>> render_beam_3d_from_detailing(detailing, is_seismic=True)
    """
    from structural_lib.visualization.geometry_3d import beam_to_3d_geometry

    geometry = beam_to_3d_geometry(detailing, is_seismic=is_seismic)
    render_beam_3d(geometry, height=height, key=key)


# =============================================================================
# Utility Functions
# =============================================================================


def create_demo_geometry() -> dict[str, Any]:
    """
    Create a demo beam geometry for testing.

    Returns:
        Dict matching BeamGeometry3D schema.
    """
    # Generate stirrups
    stirrups = []
    for x in range(50, 4000, 100):
        stirrups.append({
            "positionX": x,
            "path": [
                {"x": x, "y": -106, "z": 44},
                {"x": x, "y": 106, "z": 44},
                {"x": x, "y": 106, "z": 406},
                {"x": x, "y": -106, "z": 406},
            ],
            "diameter": 8,
            "legs": 2,
            "hookType": "135",
            "perimeter": 936,
        })

    return {
        "beamId": "B1-DEMO",
        "story": "Ground Floor",
        "dimensions": {"b": 300, "D": 450, "span": 4000},
        "concreteOutline": [
            {"x": 0, "y": -150, "z": 0},
            {"x": 0, "y": 150, "z": 0},
            {"x": 4000, "y": 150, "z": 0},
            {"x": 4000, "y": -150, "z": 0},
            {"x": 0, "y": -150, "z": 450},
            {"x": 0, "y": 150, "z": 450},
            {"x": 4000, "y": 150, "z": 450},
            {"x": 4000, "y": -150, "z": 450},
        ],
        "rebars": [
            {
                "barId": "B1",
                "segments": [{
                    "start": {"x": 0, "y": -96, "z": 56},
                    "end": {"x": 4000, "y": -96, "z": 56},
                    "diameter": 16,
                    "type": "straight",
                    "length": 4000,
                }],
                "diameter": 16,
                "barType": "bottom",
                "zone": "full",
                "totalLength": 4000,
            },
            {
                "barId": "B2",
                "segments": [{
                    "start": {"x": 0, "y": 0, "z": 56},
                    "end": {"x": 4000, "y": 0, "z": 56},
                    "diameter": 16,
                    "type": "straight",
                    "length": 4000,
                }],
                "diameter": 16,
                "barType": "bottom",
                "zone": "full",
                "totalLength": 4000,
            },
            {
                "barId": "B3",
                "segments": [{
                    "start": {"x": 0, "y": 96, "z": 56},
                    "end": {"x": 4000, "y": 96, "z": 56},
                    "diameter": 16,
                    "type": "straight",
                    "length": 4000,
                }],
                "diameter": 16,
                "barType": "bottom",
                "zone": "full",
                "totalLength": 4000,
            },
            {
                "barId": "T1",
                "segments": [{
                    "start": {"x": 0, "y": -96, "z": 394},
                    "end": {"x": 4000, "y": -96, "z": 394},
                    "diameter": 12,
                    "type": "straight",
                    "length": 4000,
                }],
                "diameter": 12,
                "barType": "top",
                "zone": "full",
                "totalLength": 4000,
            },
            {
                "barId": "T2",
                "segments": [{
                    "start": {"x": 0, "y": 96, "z": 394},
                    "end": {"x": 4000, "y": 96, "z": 394},
                    "diameter": 12,
                    "type": "straight",
                    "length": 4000,
                }],
                "diameter": 12,
                "barType": "top",
                "zone": "full",
                "totalLength": 4000,
            },
        ],
        "stirrups": stirrups,
        "metadata": {
            "fck": 25,
            "fy": 500,
            "cover": 40,
            "ldTension": 752,
            "ldCompression": 752,
            "lapLength": 940,
            "isSeismic": True,
            "remarks": "Demo beam for 3D viewer POC",
        },
        "version": "1.0.0",
    }
