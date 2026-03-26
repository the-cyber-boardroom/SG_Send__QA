---
title: "Coverage Map"
permalink: /pages/architecture/coverage-map/
---

# Coverage Map

Transition coverage for each state machine — green states have been visited by at least one test,
red states have not.  Coverage is measured at the **graph edge level**: a test that passes confirms
an edge.  A missing edge means that user path is unverified.

> Diagrams are generated from `State_Machine__Utils.to_mermaid_coverage()`.
> Coverage data is populated from `transitions_observed` recorded during test runs.

---

## How to Read This Map

| Colour | Meaning |
|--------|---------|
| 🟢 **Green state** | The state was reached during at least one test run |
| 🔴 **Red state** | The state has never been reached by the test suite |

A green state means at least one **incoming** transition was exercised.
A red state means the entire sub-graph below it is untested.

---

## Upload Wizard

{% if site.data.state_machines.upload %}
**{{ site.data.state_machines.upload.states | size }} states ·
{{ site.data.state_machines.upload.transitions | size }} transitions**

> _Coverage diagram is populated when snapshot data is available.
> Run the QA suite and export a coverage snapshot to see live green/red colouring._

### Full Transition Map

<div class="mermaid">
{{ site.data.state_machines.upload.mermaid }}
</div>

### Currently Known Coverage Gaps

Transitions not yet exercised by the test suite (from static analysis of existing tests):

| From | To | Trigger | Gap reason |
|------|----|---------|------------|
| `file-ready` | `choosing-delivery` | `auto_advance` | Multi-file / folder upload not yet tested |
| `choosing-delivery` | `choosing-share` | `click_next` | Depends on choosing-delivery branch |

{% else %}
> **Data not available.** Run `python -m sg_send_qa.state_machines.export_schemas` to generate
> `_data/state_machines/upload.json`.
{% endif %}

---

## Download Flow

{% if site.data.state_machines.download %}
**{{ site.data.state_machines.download.states | size }} states ·
{{ site.data.state_machines.download.transitions | size }} transitions**

> _Coverage diagram is populated when snapshot data is available._

### Full Transition Map

<div class="mermaid">
{{ site.data.state_machines.download.mermaid }}
</div>

### Currently Known Coverage Gaps

| From | To | Trigger | Gap reason |
|------|----|---------|------------|
| `entry` | `ready` | `submit_valid_id` | Manual entry happy path not in p0 suite |
| `entry` | `error` | `submit_invalid_id` | Manual entry error not separately tested |
| `ready` | `gallery` | `auto_route` | Gallery content-type routing not tested |
| `ready` | `viewer` | `auto_route` | Viewer content-type routing not tested |
| `decrypting` | `error` | `decrypt_failed` | Decrypt failure path not tested |

{% else %}
> **Data not available.** Run `python -m sg_send_qa.state_machines.export_schemas` to generate
> `_data/state_machines/download.json`.
{% endif %}

---

## Coverage Formula

```
coverage_pct = covered_transitions / total_transitions * 100
```

Once `transitions_observed` are wired through from live test runs, this page will show
dynamic coverage numbers.  The `State_Machine__Utils.coverage()` method computes this —
see `sg_send_qa/state_machines/State_Machine__Utils.py`.
