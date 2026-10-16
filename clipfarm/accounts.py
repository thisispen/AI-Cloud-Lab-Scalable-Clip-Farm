"""Prepare post-ready draft manifests for accounts under the user's control.

No account creation, duplicate boosting, automatic social posting or credential handling.
"""
import csv
import json
from pathlib import Path

def export_account_queue(render_manifest, accounts_file, target):
    exports=json.loads(Path(render_manifest).read_text())
    accounts=json.loads(Path(accounts_file).read_text())
    if not isinstance(accounts,list) or any(not x.get('name') or not x.get('platform') for x in accounts):
        raise ValueError('Accounts must be a JSON list with name and platform')
    rows=[]
    for account in accounts:
        for output in exports['outputs']:
            rows.append({'account':account['name'],'platform':account['platform'],
             'clip_id':output['id'],'file':output['path'], 'status':'awaiting_editor_approval',
             'publish_time':'','title':'','caption':'','rights_verified':'no',
             'notes':'Distinct meaningful edit for this audience; avoid duplicate spam'})
    dest=Path(target)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('w',newline='',encoding='utf8') as fp:
        writer=csv.DictWriter(fp,fieldnames=list(rows[0]) if rows else
          ['account','platform','clip_id','file','status','publish_time','title','caption','rights_verified','notes'])
        writer.writeheader();writer.writerows(rows)
    return len(rows)
