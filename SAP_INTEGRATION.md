# WealthBridge Tradeline MCP — SAP Integration

## Role in Sovereign Architecture
WealthBridge Tradeline MCP provides tradeline data processing for the WealthBridge OS layer.
Runs as a Python service on port 7710.

## SAP Node ID: `wealthbridge-tradeline-mcp`

## Port: 7710

## Capabilities
- `tradeline.score` — Credit tradeline scoring via TurboQuant Core
- `tradeline.history` — Tradeline history retrieval
- `tradeline.dispute` — Dispute management

## Upstream Services
| Service | URL | Purpose |
|---------|-----|---------|
| WealthBridge OS Orchestrator | http://localhost:8001 | Parent orchestrator |
| TurboQuant Core | http://localhost:7770 | Quantum scoring |
| Federal API Vault | http://localhost:7795 | FFIEC compliance data |

## SAP Headers (Python)
```python
sap_headers = {
    "x-sap-node-id": "wealthbridge-tradeline-mcp",
    "x-sap-trace-id": str(uuid.uuid4()),
    "x-sap-version": "1.0",
}
```

## API Endpoints
```
GET  /health             — Health check
POST /capsule/execute    — Execute a tradeline capsule
POST /task               — Run a tradeline task
GET  /tradeline/{id}     — Get tradeline details
```

## Service Registry
Registered in `sovereign-stack/wealthbridge-os/service-registry.json`

## Branch
All synthesis work: `claude/deepflex-argus-synthesis-jWjmO`
