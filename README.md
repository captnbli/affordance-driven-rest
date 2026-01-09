# Affordance-Driven REST Demo

This repository accompanies **ADR-0001: Affordance-Driven REST with Mandatory Hypermedia Links**.

Please read:

- `ADR-0001-affordance-driven-rest.md` — architectural decision and rationale

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 server.py
```

In another terminal:

```bash
source .venv/bin/activate
python3 clients/client1_ignore_optional.py
python3 clients/client2_actions_forms.py
python3 clients/client3_all_optional.py
```
