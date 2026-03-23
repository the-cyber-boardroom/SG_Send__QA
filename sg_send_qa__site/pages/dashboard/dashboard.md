---
title: QA Dashboard
permalink: /pages/dashboard/
---

# QA Dashboard

{% if site.data.qa_summary %}
{% assign s = site.data.qa_summary %}

**Generated:** {{ s.generated_at }} &nbsp;|&nbsp; **Version:** {{ s.version }}

---

## Summary

| Metric | Value |
|--------|------:|
| Total test methods | {{ s.total_tests }} |
| Total screenshots | {{ s.total_screenshots }} |
| Use cases with no evidence | {{ s.zero_evidence }} |

---

## Coverage by Group

| Group | Use Cases | With Evidence | Coverage |
|-------|----------:|:-------------:|:--------:|
{% for g in s.groups %}| {{ g.icon }} {{ g.name }} | {{ g.total }} | {{ g.with_evidence }} | {{ g.coverage_pct }}% |
{% endfor %}

---

{% if s.needs_attention and s.needs_attention.size > 0 %}
## Needs Attention

Use cases with no screenshot evidence:

| Group | Use Case |
|-------|----------|
{% for item in s.needs_attention %}| {{ item.group }} | `{{ item.use_case }}` |
{% endfor %}

{% endif %}

{% else %}
*No summary data available. Run `python -m sg_send_qa.cli.generate_docs` to generate.*
{% endif %}
