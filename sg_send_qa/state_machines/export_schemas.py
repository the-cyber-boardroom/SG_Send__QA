"""Export state machine definitions to JSON for QA site consumption.

Run via:
    python -m sg_send_qa.state_machines.export_schemas

Writes JSON files to:
    sg_send_qa/state_machines/schemas/    (source of truth, committed)
    sg_send_qa__site/_data/state_machines/ (site consumption, committed)

Both directories get the same content; the site copy is the symlink-free
approach that works with GitHub Pages.

Idempotent: only writes if content changed (core principle: no code change
= no file change).
"""
import json
from pathlib import Path

from sg_send_qa.state_machines.State_Machine__Upload   import upload_state_machine
from sg_send_qa.state_machines.State_Machine__Download import download_state_machine


def _write_if_changed(path: Path, data: dict) -> bool:
    content = json.dumps(data, indent=2, ensure_ascii=False)
    if path.exists() and path.read_text() == content:
        print(f"  Unchanged:  {path}")
        return False
    path.write_text(content)
    print(f"  Written:    {path}")
    return True


def export() -> None:
    machines = {
        'upload'  : upload_state_machine(),
        'download': download_state_machine(),
    }

    repo_root = Path(__file__).parent.parent.parent
    for dest in [
        repo_root / 'sg_send_qa' / 'state_machines' / 'schemas',
        repo_root / 'sg_send_qa__site' / '_data' / 'state_machines',
    ]:
        dest.mkdir(parents=True, exist_ok=True)
        for name, machine in machines.items():
            _write_if_changed(dest / f'{name}.json', machine.json())


if __name__ == '__main__':
    export()
