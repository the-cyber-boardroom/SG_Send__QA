---
title: "State Machines"
permalink: /pages/architecture/state-machines/
---

# State Machines

Formal definitions of the SG/Send UI state machines, derived from the QA test code and
verified against the live application.  These are the **single source of truth** — both the
tests and this documentation are generated from the same Python classes.

> Source: `sg_send_qa/state_machines/` · Exported via `python -m sg_send_qa.state_machines.export_schemas`

---

## Upload Wizard

The upload wizard walks through 6 UI steps. Two branching paths exit `file-ready`:
single files and text skip the delivery-method step and go straight to share-mode selection.

{% if site.data.state_machines.upload %}
**{{ site.data.state_machines.upload.states | size }} states ·
{{ site.data.state_machines.upload.transitions | size }} transitions**

<div class="mermaid">
{{ site.data.state_machines.upload.mermaid }}
</div>

### Security Annotations

| Transition | Security tag |
|------------|-------------|
{% for t in site.data.state_machines.upload.security_annotated %}| `{{ t.from }}` → `{{ t.to }}` ({{ t.trigger }}) | `{{ t.security }}` |
{% endfor %}

{% else %}
*State machine data not found. Run `python -m sg_send_qa.state_machines.export_schemas`.*
{% endif %}

---

## Download Flow

The download flow branches on whether the URL contains a hash fragment, and again on
content type when auto-routing to browse/gallery/viewer.

{% if site.data.state_machines.download %}
**{{ site.data.state_machines.download.states | size }} states ·
{{ site.data.state_machines.download.transitions | size }} transitions**

<div class="mermaid">
{{ site.data.state_machines.download.mermaid }}
</div>

### Security Annotations

| Transition | Security tag |
|------------|-------------|
{% for t in site.data.state_machines.download.security_annotated %}| `{{ t.from }}` → `{{ t.to }}` ({{ t.trigger }}) | `{{ t.security }}` |
{% endfor %}

{% else %}
*State machine data not found. Run `python -m sg_send_qa.state_machines.export_schemas`.*
{% endif %}

---

## How This Works

```
Python classes          JSON export             QA site
─────────────────       ─────────────────       ─────────────────
State_Transition    →   schemas/upload.json  →  This page
State_Machine__*    →   _data/state_machines/   (Jekyll reads _data/)
State_Machine__Utils    mermaid text embedded   Mermaid.js renders
```

The `mermaid` field in each JSON file is pre-rendered by `State_Machine__Utils.to_mermaid()`.
The QA site reads it at build time — no runtime generation needed.

## Test Coverage

When the QA API is used to run workflows, each response includes `transitions_observed` —
the list of `(from_state, to_state)` pairs actually traversed.  Aggregate these across a
test run to compute coverage:

```json
{
  "status": "pass",
  "transitions_observed": [
    {"from_state": "idle",       "to_state": "file-ready"},
    {"from_state": "file-ready", "to_state": "choosing-share"},
    {"from_state": "confirming", "to_state": "encrypting"}
  ]
}
```

Compare against the defined transitions to find untested paths.
