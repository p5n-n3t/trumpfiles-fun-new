#!/usr/bin/env python3
"""Strict structure, assignment, copy-length, URL, and Git-change boundary validator.

Source authentication is a separate editorial duty. Run after outcomes and checkpoints
are complete. This script does not connect to Neon or modify canonical data.
"""
import collections
import glob
import json
import pathlib
import re
import subprocess
import sys
from urllib.parse import urlsplit

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]   # repository root? dynamically corrected by git
SOURCE_SHA = '3af4d448606ed190acbdc2fb83456ff164b0f005'
VALID = {'repaired_proposal', 'supported_partial', 'still_unresolved'}
SRC = HERE.parent / 'web-trump-held149-editorial-2026-10-20'


def urls_valid(urls):
    if not isinstance(urls, list):
        return False
    for u in urls:
        if not isinstance(u, str) or not u.strip() or any(c.isspace() for c in u):
            return False
        p = urlsplit(u)
        if p.scheme not in ('http', 'https') or not p.netloc or '.' not in p.hostname if p.hostname else True:
            return False
    return True


def load_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding='utf8').splitlines() if x.strip()]


def count_words(text):
    return len(text.split()) if isinstance(text, str) else 0


def main():
    manifest = json.loads((HERE/'assignments.json').read_text())
    orig = [d for p in sorted(SRC.glob('workers/worker-*/outcomes.jsonl')) for d in load_jsonl(p)]
    excluded = collections.Counter(d['outcome'] for d in orig if d['outcome']!='still_unresolved')
    target = {d['record_id']:d for d in orig if d['outcome']=='still_unresolved'}
    assert len(orig) == 149 and len(target) == 119, 'Source snapshot differs from PR #71'
    assert dict(excluded)==manifest['exclusions'], 'Source exclusions differ from manifest'
    errors=[]; notes=[]; records=[]; by_worker={}; seen=collections.Counter()
    for w in manifest['workers']:
        n=w['worker']; path=HERE/w['output']; checkpoint=HERE/w['checkpoint']
        if not path.exists():
            errors.append(f'worker-{n:02d}: missing outcomes'); by_worker[n]={'expected':w['count'],'observed':0}; continue
        try: rows=load_jsonl(path)
        except Exception as e: errors.append(f'worker-{n:02d}: invalid JSONL {e}'); continue
        by_worker[n]={'expected':w['count'],'observed':len(rows),'outcomes':dict(collections.Counter(r.get('outcome') for r in rows))}
        if len(rows)!=w['count']: errors.append(f'worker-{n:02d}: {len(rows)} outcomes != expected {w["count"]}')
        for j,r in enumerate(rows):
            rid=r.get('record_id'); seen[rid]+=1; records.append(r)
            label=f'worker-{n:02d}/{rid or j}'
            if rid not in target: errors.append(label+': ID outside assignment'); continue
            o=target[rid]
            if rid not in w['ids'] or o['assignment_index']%6 != n-1: errors.append(label+': incorrect worker membership')
            if r.get('assignment_index')!=o['assignment_index']: errors.append(label+': changed assignment_index')
            if r.get('assigned_worker')!=n: errors.append(label+': bad assigned_worker')
            if r.get('outcome') not in VALID: errors.append(label+': invalid terminal outcome')
            if r.get('proposal_only') is not True or r.get('publication_eligible') is not False or r.get('requires_manual_editorial_review') is not True: errors.append(label+': publication/proposal flags invalid')
            for key in ('source_urls','urls_searched','original_source_urls'):
                if not urls_valid(r.get(key)): errors.append(label+f': malformed URL list {key}')
            if r.get('original_title')!=o.get('frozen_title_as_supplied') or r.get('original_claim')!=o.get('frozen_claim_as_supplied'): errors.append(label+': original claim/title mismatch')
            if r.get('original_source_urls')!=o.get('source_urls'): errors.append(label+': original URLs mismatch')
            if not isinstance(r.get('evidence_note'),str) or len(r['evidence_note'].strip())<30: errors.append(label+': missing substantive evidence_note')
            if r.get('outcome')=='still_unresolved':
                for k in ('exact_blocker','why_cannot_repair'):
                    if not isinstance(r.get(k),str) or len(r[k].strip())<20: errors.append(label+': missing '+k)
                if not r.get('urls_searched'): notes.append(label+': no exact URL visited; review search_queries or missing source URLs')
            else:
                if not r.get('source_urls'): errors.append(label+': positive proposal with no source URL')
                for key in ('title','short_description'):
                    txt=r.get(key)
                    if not isinstance(txt,str) or not txt.strip() or len(txt)>180: errors.append(label+f': invalid {key} character limit')
                med=count_words(r.get('medium_description')); long=count_words(r.get('long_description'))
                if not 45<=med<=90: errors.append(label+f': medium {med} words outside [45,90]')
                if not 140<=long<=300: errors.append(label+f': long {long} words outside [140,300]')
        if not checkpoint.exists(): errors.append(f'worker-{n:02d}: missing checkpoint')
        else:
            try:
                ck=json.loads(checkpoint.read_text())
                if ck.get('completed_count')!=len(rows): errors.append(f'worker-{n:02d}: checkpoint count mismatches')
                if ck.get('total_count')!=w['count']: errors.append(f'worker-{n:02d}: checkpoint target mismatches')
                if ck.get('state')!='completed': errors.append(f'worker-{n:02d}: checkpoint not completed')
            except Exception as e: errors.append(f'worker-{n:02d}: invalid checkpoint {e}')
    missing=sorted(set(target)-set(seen)); duplicate=sorted(k for k,v in seen.items() if v>1)
    if missing: errors.append(f'{len(missing)} missing IDs')
    if duplicate: errors.append(f'{len(duplicate)} duplicate IDs')
    if len(records)!=119: errors.append(f'exact count {len(records)} != 119')
    cmd=['git','diff','--name-status',SOURCE_SHA,'HEAD']
    cp=subprocess.run(cmd,capture_output=True,text=True,cwd=HERE,check=True)
    changes=[line.split('\t') for line in cp.stdout.splitlines() if line.strip()]
    prefix='data/neon-workbench/external/web-trump-evidence-recovery-2026-10-20/'
    out_of_scope=[x for x in changes if len(x)<2 or x[0]!='A' or not x[-1].startswith(prefix)]
    if out_of_scope: errors.append('Git diff includes non-added/out-of-scope paths: '+str(out_of_scope[:20]))
    outcomes=dict(collections.Counter(r.get('outcome') for r in records))
    report={'date':'2026-10-20','source_pr':71,'source_head_sha':SOURCE_SHA,'expected_total':119,'observed_total':len(records),'unique_ids':len(seen),'duplicate_ids':duplicate,'missing_ids':missing,'ids_outside_assignment':[r.get('record_id') for r in records if r.get('record_id') not in target],'excluded_original_status_counts':dict(excluded),'outcomes':outcomes,'by_worker':by_worker,'description_and_url_validation':'passed' if not errors else 'failed','git_changed_paths':len(changes),'all_git_changes_are_new_in_target_folder':not out_of_scope,'neon_change_note':'No database interaction performed by this validator; Git diff protects historical paths, not live Neon state.','source_authentication_note':'Structural checks do NOT authenticate sources or prove historical claims; human/editorial source review required.','warnings':notes,'errors':errors,'passed':not errors}
    print(json.dumps(report,indent=2))
    if '--write-report' in sys.argv:
        (HERE/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n')
        if not errors:
            index=[{'record_id':r['record_id'],'assignment_index':r['assignment_index'],'assigned_worker':r['assigned_worker'],'outcome':r['outcome'],'source_urls':r.get('source_urls',[]),'worker_file':f"workers/worker-{r['assigned_worker']:02d}/outcomes.jsonl"} for r in sorted(records,key=lambda x:x['assignment_index'])]
            (HERE/'combined-index.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in index))
    return 0 if not errors else 1

if __name__=='__main__':sys.exit(main())
