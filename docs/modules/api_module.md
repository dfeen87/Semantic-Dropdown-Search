# API Module

The optional FastAPI layer in `api/` exposes the existing in-memory indexing and
plain-text search components. It does not replace the core Python interfaces or
provide durable persistence.

## Implemented endpoints

| Method | Endpoint | Contract |
|---|---|---|
| `GET` | `/semantic-config` | Return active search configuration. |
| `PATCH` | `/semantic-config` | Atomically validate and apply configuration; model-dependent activation fails with `503`. |
| `POST` | `/semantic-index` | Validate and atomically index an `items` batch. |
| `GET` | `/semantic-search?q=...` | Search by deterministic text matching and, when configured, embeddings. |

`api/openapi.yaml` is generated from `api.main.app` and is the authoritative
wire contract. FastAPI also serves the same schema at `/openapi.json` and the
interactive documentation at `/docs`.

## Validation and failure contracts

Every indexed item must provide a complete schema-v1 descriptor. The API does
not invent required semantic values and never retries invalid input with
validation disabled. If any item, duplicate ID, or embedding output in a batch
is invalid, no item from that request is committed.

Embedding mode is optional. Enabling it requires the configured model to load;
a missing model returns `503` and leaves all prior configuration fields intact.
Computed vectors must be finite, non-empty, two-dimensional, and aligned with
the item batch. Search rejects incompatible stored/query vectors rather than
using malformed scores.

## Example

```bash
curl -X POST http://localhost:8000/semantic-index \
  -H 'content-type: application/json' \
  -d '{"items":[{"id":"doc-1","text":"Biology research", "descriptor":{"domain":"Science → Biology","intent":"Research"}}]}'

curl 'http://localhost:8000/semantic-search?q=biology'
```

The service uses process-local in-memory storage. Authentication,
authorization, rate limiting, multi-worker consistency, and durable transactions
remain deployment responsibilities.
