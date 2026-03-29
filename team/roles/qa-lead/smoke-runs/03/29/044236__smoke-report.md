# QA Smoke Report

**Date:** 2026-03-29 04:42 UTC
**Version:** v0.2.42
**Target:** https://send.sgraph.ai
**Token:** set (17 chars)

## Results

| Suite | Passed | Failed | Status |
|-------|--------|--------|--------|
| Upload+download round-trip (5) | 5 | 0 | ✅ |
| Live smoke (6)                 | 6 | 0 | ✅ |

## Overall: PASS

## Failures (if any)

None — all steps passed.

## Suite 1 Detail

```
/tmp/venv312/lib/python3.12/site-packages/pydantic/json_schema.py:2448: PydanticJsonSchemaWarning: Default value 0 is not JSON serializable; excluding default from JSON schema [non-serializable-default]
  warnings.warn(message, PydanticJsonSchemaWarning)
/tmp/venv312/lib/python3.12/site-packages/pydantic/json_schema.py:2448: PydanticJsonSchemaWarning: Default value  is not JSON serializable; excluding default from JSON schema [non-serializable-default]
  warnings.warn(message, PydanticJsonSchemaWarning)
/tmp/venv312/lib/python3.12/site-packages/fastapi/openapi/utils.py:252: UserWarning: Duplicate Operation ID api_vault_write_put for function write__vault_id at /tmp/sgraph-send-ref/sgraph_ai_app_send/lambda__user/fast_api/routes/Routes__Vault__Pointer.py
  warnings.warn(message, stacklevel=1)
/tmp/venv312/lib/python3.12/site-packages/fastapi/openapi/utils.py:252: UserWarning: Duplicate Operation ID api_vault_read_get for function read__vault_id at /tmp/sgraph-send-ref/sgraph_ai_app_send/lambda__user/fast_api/routes/Routes__Vault__Pointer.py
  warnings.warn(message, stacklevel=1)
/tmp/venv312/lib/python3.12/site-packages/fastapi/openapi/utils.py:252: UserWarning: Duplicate Operation ID api_vault_read-base64_get for function read_base64__vault_id at /tmp/sgraph-send-ref/sgraph_ai_app_send/lambda__user/fast_api/routes/Routes__Vault__Pointer.py
  warnings.warn(message, stacklevel=1)
/tmp/venv312/lib/python3.12/site-packages/fastapi/openapi/utils.py:252: UserWarning: Duplicate Operation ID api_vault_delete_delete for function delete__vault_id at /tmp/sgraph-send-ref/sgraph_ai_app_send/lambda__user/fast_api/routes/Routes__Vault__Pointer.py
  warnings.warn(message, stacklevel=1)
  ✓ api_reachable: PASS — server up
  ✓ api_auth_and_create: PASS — transfer_id=1ec12177f536
  ✓ api_encrypt_upload: PASS — 107 bytes uploaded
  ✓ api_complete: PASS — transfer marked complete
  ✓ api_download: PASS — 107 bytes match upload

=== SUITE 1 (upload+download): 5/5 passed ===
Suite1 exit: 0
```

## Live Site Detail

```
Proxy: 21.0.0.33:15004
SG_SEND_ACCESS_TOKEN: set (17 chars)

=== LIVE SITE: 6/6 passed ===
  ✓ root: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/
  ✓ download_entry: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/download/
  ✓ gallery_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/gallery/
  ✓ browse_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/browse/
  ✓ viewer_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/view/
  ✓ invalid_hash: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/download/#bogus123/fakekey==
Suite5 exit: 0
```
