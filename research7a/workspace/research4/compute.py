"""Summarize measured command costs without double-counting nested analyses."""
import json
from pathlib import Path

ROOT=Path('results/research4')

def main():
    files=[ROOT/'commands.jsonl',ROOT/'commands_production.jsonl',Path('research4/commands_models.jsonl')]
    files+=sorted(ROOT.glob('*commands*critic*.jsonl'))
    files+=sorted(ROOT.glob('*commands*replic*.jsonl'))
    rows=[]
    for file in files:
        if not file.exists():continue
        for line in file.read_text().splitlines():
            if line.strip():rows.append(dict(ledger=str(file),record=json.loads(line)))
    additional=Path('research4/modelcommandledger.json')
    if additional.exists():
        rows.extend(dict(ledger=str(additional),record=record) for record in json.loads(additional.read_text()))
    primary=[]
    for row in rows:
        record=row['record'];command=record.get('command',[])
        if record.get('status')=='finished' and isinstance(command,list) and 'research4.benchmark' in command:
            primary.append(dict(command=command,cpu_seconds=record['child_cpu_seconds'],wall_seconds=record['wall_seconds']))
    result=dict(primary_leaf_commands=primary,primary_os_child_cpu_seconds=sum(x['cpu_seconds'] for x in primary),
                primary_sequential_stage_wall_seconds=sum(x['wall_seconds'] for x in primary),
                note='Only primary benchmark leaf commands are summed. Host analysis, replication, subprocess and container tests are separately reported in their original ledgers; parent/child or script self/outer measurements may overlap. Docker daemon/container CPU is unknown. Offline resource costs are separate from inference limits.',
                ledger_records=rows)
    (ROOT/'compute_summary.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
