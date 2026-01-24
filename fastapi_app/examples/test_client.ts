/**
 * TypeScript Test Client for FastAPI Structural Design API.
 *
 * Demonstrates how to use:
 * - REST endpoints for beam design
 * - WebSocket for interactive design
 * - SSE for batch design streaming
 *
 * Usage:
 *   # With Node.js (requires 'ws' package):
 *   npx ts-node test_client.ts
 *
 *   # Or compile and run:
 *   tsc test_client.ts && node test_client.js
 *
 * Week 3 Implementation - V3 Migration
 */

// Types
interface BeamDesignRequest {
  width: number;
  depth: number;
  moment: number;
  shear?: number;
  fck: number;
  fy: number;
}

interface FlexureResult {
  ast_required: number;
  ast_provided: number;
  is_safe: boolean;
  utilization_ratio: number;
}

interface DesignResult {
  status: 'PASS' | 'FAIL';
  flexure: FlexureResult;
  shear?: object;
}

interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

// Configuration
const BASE_URL = process.env.API_URL || 'http://localhost:8000';
const WS_URL = BASE_URL.replace('http', 'ws');

// =============================================================================
// REST API Client
// =============================================================================

export class StructuralDesignClient {
  private baseUrl: string;

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Check API health status.
   */
  async health(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Design a reinforced concrete beam.
   */
  async designBeam(params: BeamDesignRequest): Promise<DesignResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/design/beam`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Design failed: ${error.detail || response.status}`);
    }

    return response.json();
  }

  /**
   * Get beam geometry calculations.
   */
  async calculateGeometry(
    width: number,
    depth: number,
    length: number,
  ): Promise<{
    volume: number;
    surface_area: number;
    weight: number;
  }> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/geometry/beam?width=${width}&depth=${depth}&length=${length}`,
    );

    if (!response.ok) {
      throw new Error(`Geometry calculation failed: ${response.status}`);
    }

    return response.json();
  }
}

// =============================================================================
// WebSocket Client
// =============================================================================

export class LiveDesignClient {
  private ws: WebSocket | null = null;
  private baseUrl: string;

  constructor(baseUrl: string = WS_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Connect to WebSocket for live design.
   */
  async connect(clientId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const url = `${this.baseUrl}/ws/design/${clientId}`;
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log(`✅ Connected to ${url}`);
        resolve();
      };

      this.ws.onerror = (error) => {
        reject(new Error(`WebSocket error: ${error}`));
      };
    });
  }

  /**
   * Send a design request and wait for response.
   */
  async designBeam(params: BeamDesignRequest): Promise<DesignResult> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Design request timeout'));
      }, 5000);

      this.ws!.onmessage = (event) => {
        clearTimeout(timeout);
        const data = JSON.parse(event.data);
        if (data.type === 'design_result') {
          resolve(data.data);
        } else if (data.type === 'error') {
          reject(new Error(data.message));
        }
      };

      this.ws!.send(
        JSON.stringify({
          type: 'design_beam',
          params,
        }),
      );
    });
  }

  /**
   * Close the WebSocket connection.
   */
  close(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// =============================================================================
// SSE Batch Client
// =============================================================================

export class BatchDesignClient {
  private baseUrl: string;

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Stream batch design results via SSE.
   */
  async *streamBatchDesign(
    beams: Array<BeamDesignRequest & { id: string }>,
  ): AsyncGenerator<{ event: string; data: object }> {
    const beamsJson = encodeURIComponent(JSON.stringify(beams));
    const url = `${this.baseUrl}/stream/batch-design?beams=${beamsJson}`;

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Batch design failed: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';
    let currentEvent = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('event:')) {
          currentEvent = line.slice(6).trim();
        } else if (line.startsWith('data:')) {
          const data = JSON.parse(line.slice(5).trim());
          yield { event: currentEvent, data };
          currentEvent = '';
        }
      }
    }
  }
}

// =============================================================================
// Demo
// =============================================================================

async function main() {
  console.log('=' .repeat(60));
  console.log('🧪 TypeScript FastAPI Client Demo');
  console.log('=' .repeat(60));
  console.log(`\nServer: ${BASE_URL}`);

  const client = new StructuralDesignClient();

  // Test health
  console.log('\n📤 GET /health');
  try {
    const health = await client.health();
    console.log(`📥 Status: ${health.status}`);
  } catch (e) {
    console.log(`❌ ${e}`);
    console.log('   Make sure the server is running first!');
    return;
  }

  // Test beam design
  console.log('\n📤 POST /api/v1/design/beam');
  try {
    const result = await client.designBeam({
      width: 300,
      depth: 500,
      moment: 150,
      fck: 25,
      fy: 500,
    });
    console.log(`📥 Status: ${result.status}`);
    console.log(`   Ast required: ${result.flexure.ast_required.toFixed(1)} mm²`);
  } catch (e) {
    console.log(`❌ ${e}`);
  }

  console.log('\n✅ Demo complete!');
}

// Run if executed directly (Node.js)
if (typeof require !== 'undefined' && require.main === module) {
  main().catch(console.error);
}
