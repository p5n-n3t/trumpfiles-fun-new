#!/usr/bin/env python3
"""Read-only independent October 22 candidate QA: deterministic scope and append-only checks."""
import collections, json, pathlib, re, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'.git').exists())
EXPECTED_PREFIX="data/neon-workbench/external/web-october22-independent-qa-2026-10-21/"
DISPOSITIONS={"accept_for_editorial","narrower_revision_required","duplicate_or_merge_candidate","hold"}

def load_jsonl(name):
    p=ROOT/name
    if not p.is_file():raise ValueError(f"missing file: {name}")
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
def wc(text):return len(re.findall(r"\b[\w’'-]+\b",text))
def sh(*args):
    return subprocess.check_output(["git","-C",str(REPO),*args],text=True).strip()
def validate():
    failures=[]
    def ck(test,label):
        if not test: failures.append(label)
    manifest=json.loads((ROOT/'checkpoint.json').read_text())
    expected=manifest['assigned_ids']; indexes=manifest['assignment_indexes']
    ck(len(expected)==22 and len(set(expected))==22, "manifest must have exactly 22 unique IDs")
    ck(sorted(indexes)==list(range(1,23)), "assignment indexes must be 1..22")
    rows=load_jsonl('terminal-results.jsonl')
    logs=load_jsonl('research-log.jsonl')
    ids=[r.get('candidate_id') for r in rows]
    logids=[r.get('candidate_id') for r in logs]
    ck(len(rows)==22, f"expected 22 terminal rows; got {len(rows)}")
    ck(len(set(ids))==len(ids), "duplicate terminal IDs")
    ck(set(ids)==set(expected), f"missing/outside terminal ids missing={set(expected)-set(ids)} extra={set(ids)-set(expected)}")
    ck(len(logs)==22 and len(set(logids))==22 and set(logids)==set(expected),"research-log exact-set mismatch")
    ck(sorted(r.get('assignment_index',-1) for r in rows)==list(range(1,23)),"terminal indexes mismatch")
    ck(sorted(r.get('assignment_index',-1) for r in logs)==list(range(1,23)),"research indexes mismatch")
    outcome_counts=collections.Counter()
    url_pattern=re.compile(r"^https?://[^\s/]+/[^\s]*$")
    assignments=manifest['worker_assignments']
    ck(sorted(x for d in assignments.values() for x in d['indexes'])==list(range(1,23)),"worker overlap/gap")
    for w,d in assignments.items():
        n=int(w.rsplit('-',1)[1])
        ck(all((i-1)%6 == n-1 for i in d['indexes']),f"{w} modulo assignment invalid")
        ck(len(d['indexes'])==len(d['ids']),f"{w} id/count mismatch")
    expected_by_index=dict(zip(indexes,expected))
    for r in rows:
        cid=r.get('candidate_id');i=r.get('assignment_index')
        ck(expected_by_index.get(i)==cid,f"index and ID mismatch {i} {cid}")
        disp=r.get('terminal_disposition')
        ck(disp in DISPOSITIONS, f"{cid}: invalid terminal disposition")
        outcome_counts[disp]+=1
        for key in ('title','event_date','uncertainty','duplicate_comparison','source_evidence'):
            ck(key in r,f"{cid}: missing {key}")
        urls=r.get('source_urls')
        ck(isinstance(urls,list) and urls and all(isinstance(u,str) and url_pattern.match(u) for u in urls or []),f"{cid}: missing or invalid exact URLs")
        check_urls=manifest.get('source_urls_by_id',{}).get(cid)
        ck(urls==check_urls,f"{cid}: source URL order/content diverged from frozen review input")
        evidence=r.get('source_evidence') or []
        ck(isinstance(evidence,list) and [x.get('url') for x in evidence]==urls, f"{cid}: per-source fact map incomplete/out of order")
        for e in evidence:
            ck(e.get('access') in ('read','blocked','not_verified'),f"{cid}: invalid source access status")
            ck(isinstance(e.get('supported_facts'),list), f"{cid}: unsupported facts map shape")
            ck(isinstance(e.get('limitations'),list), f"{cid}: limitations map shape")
        if disp in ('accept_for_editorial','narrower_revision_required'):
            ck(any(e.get('access')=='read' and e.get('supported_facts') for e in evidence),f"{cid}: accepted/revised without independently inspected supporting URL")
            ck(not r.get('blocker'),f"{cid}: positive disposition has blocker")
        if disp=='hold':ck(bool(r.get('blocker')),f"{cid}: hold has no exact blocker")
        if disp=='duplicate_or_merge_candidate':
            ck(bool((r.get('duplicate_comparison') or {}).get('counterpart_id')),f"{cid}: duplicate lacks exact counterpart")
        if disp=='narrower_revision_required':
            text=r.get('replacement_copy')
            ck(isinstance(text,dict) and all(isinstance(text.get(k),str) and text[k].strip() for k in ('short','medium','long')),f"{cid}: missing replacement copy")
            if isinstance(text,dict):
                ck(len(text.get('short',''))<=180,f"{cid}: short over 180 chars")
                ck(45<=wc(text.get('medium',''))<=90, f"{cid}: medium length {wc(text.get('medium',''))}")
                ck(140<=wc(text.get('long',''))<=300, f"{cid}: long length {wc(text.get('long',''))}")
        else:
            ck('replacement_copy' not in r,f"{cid}: unsolicited replacement copy")
    allowed={i['candidate_id'] for i in rows}
    for lg in logs:
        cid=lg.get('candidate_id')
        ck(cid in allowed and 'reviewed_source_urls' in lg,f"{cid}: missing research provenance")
    git_diff=sh('diff','--name-status','origin/main')
    changes=[x for x in git_diff.splitlines() if x]
    tracked_changed=[]
    for row in changes:
        tokens=row.split('\t',1)
        if len(tokens)==2:tracked_changed.append(tokens[1])
    untracked=sh('ls-files','--others','--exclude-standard').splitlines()
    diff_paths=tracked_changed+untracked
    ck(bool(diff_paths),"no QA outputs in worktree")
    ck(all(p.startswith(EXPECTED_PREFIX) for p in diff_paths),f"protected paths changed: {[p for p in diff_paths if not p.startswith(EXPECTED_PREFIX)]}")
    ck(all(not p.startswith(EXPECTED_PREFIX+'..') for p in diff_paths),"path traversal in changed paths")
    ck(not any(p for p in diff_paths if any(x in p.lower() for x in ('neon-export','/canonical/','migrations/','scores/'))),"protected data paths")
    return {
        'status':'passed' if not failures else 'failed',
        'errors':failures,
        'expected_candidate_count':22,'terminal_record_count':len(rows),
        'research_record_count':len(logs),
        'unique_terminal_ids':len(set(ids)),
        'missing_ids':sorted(set(expected)-set(ids)),
        'outside_assignment_ids':sorted(set(ids)-set(expected)),
        'duplicate_terminal_ids':sorted([cid for cid,n in collections.Counter(ids).items() if n>1]),
        'counts_by_disposition':dict(sorted(outcome_counts.items())),
        'worker_partition_sizes':{k:len(v['ids']) for k,v in assignments.items()},
        'all_changed_files_under_new_qa_folder':all(p.startswith(EXPECTED_PREFIX) for p in diff_paths),
        'modified_outside_qa_folder':[p for p in diff_paths if not p.startswith(EXPECTED_PREFIX)],
        'changed_file_count':len(diff_paths),
        'original_packet_sha256':manifest['input_sha256']['packet'],
        'base_ref':'origin/main',
        'base_sha':manifest['base_sha'],
        'url_check_scope':'source URL preservation/syntax and worker-supplied access/fact mapping; structural checks cannot certify publisher contents',
        'database_or_canonical_files_changed':any(not p.startswith(EXPECTED_PREFIX) for p in diff_paths),
    }
if __name__=='__main__':
    result=validate()
    print(json.dumps(result,indent=2,ensure_ascii=False))
    sys.exit(0 if result['status']=='passed' else 1)
