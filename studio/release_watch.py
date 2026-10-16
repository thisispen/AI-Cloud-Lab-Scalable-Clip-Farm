#!/usr/bin/env python3
"""Observe official public GitHub releases. NEVER install or upgrade anything automatically.

Requires internet only with --check-online, otherwise uses an offline fixture.
Designed for read-only scheduled check; all newly observed versions require manual
source review, security scan, test fixtures, cost/licensing comparison and approval.
"""
import argparse
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from .router import load_data

ROOT=Path(__file__).resolve().parent
HEADERS={"Accept":"application/vnd.github+json","User-Agent":"AI-Cloud-Lab-release-checker"}


def safe_release(repo, payload, previous=None):
    if not isinstance(payload,dict): raise ValueError('Not a release object')
    tag=str(payload.get('tag_name',''))[:100]
    if not tag: raise ValueError('No version tag')
    url=str(payload.get('html_url',''))
    if not url.startswith(f'https://github.com/{repo}/releases/'):
        raise ValueError('Unexpected release URL')
    return {"repository":repo,"latest_observed_tag":tag,"release_url":url,
            "published_at":str(payload.get('published_at',''))[:40],
            "last_approved_tag":previous or None,
            "status":"unreviewed_candidate" if previous != tag else "approved_version_current",
            "automatic_upgrade":False}


def fetch_github_release(repo):
    url=f"https://api.github.com/repos/{repo}/releases/latest"
    req=Request(url, headers=HEADERS)
    with urlopen(req,timeout=12) as r:
        return json.load(r)


def check(repos, approved=None, fetch=fetch_github_release):
    approved=approved or {}
    results=[]
    for repo in repos:
        try: results.append(safe_release(repo, fetch(repo), approved.get(repo)))
        except (HTTPError,URLError,TimeoutError,ValueError, OSError, KeyError) as exc:
            results.append({"repository":repo,"status":"check_failed_or_no_releases",
                            "reason":type(exc).__name__,"automatic_upgrade":False})
    return {"checked_sources":len(repos),"results":results,
            "instruction":"Review releases against creative tests, licenses, costs and security before changing tools. Zero automatic installs or charges."}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    src=ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--check-online',action='store_true')
    src.add_argument('--fixture',help='JSON mapping owner/repo to representative release metadata')
    ap.add_argument('--out',help='Write JSON report to a file')
    a=ap.parse_args()
    catalog,_=load_data()
    repos=catalog['official_watch_repositories']
    approved_path=ROOT/'approved_versions.json'
    approved=json.loads(approved_path.read_text(encoding='utf-8'))
    if a.fixture:
        fixture=json.loads(Path(a.fixture).read_text(encoding='utf-8'))
        def fetch(name):return fixture[name]
    else:fetch=fetch_github_release
    report=check(repos, approved, fetch)
    raw=json.dumps(report,indent=2)
    if a.out:
        out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(raw+'\n',encoding='utf-8')
    print(raw)

if __name__=='__main__':main()
