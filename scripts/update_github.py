#!/usr/bin/env python3
"""Refresh public repository star counts; preserve verified values on failure."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import json
import os
import re

ROOT = Path(__file__).resolve().parents[1]

def repository_key(url):
    parsed = urlparse(url)
    parts = parsed.path.strip('/').split('/')
    if parsed.hostname != 'github.com' or len(parts) != 2:
        return None
    owner, repo = parts
    repo = repo.removesuffix('.git')
    if not re.fullmatch(r'[\w.-]+', owner) or not re.fullmatch(r'[\w.-]+', repo):
        return None
    return f'{owner}/{repo}'.lower()

def visible_count(entry):
    count = entry.get('stars') if isinstance(entry, dict) else None
    return count if type(count) is int and count > 30 else None

def fetch_count(repo):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'Jiakai-Tang-Homepage', 'X-GitHub-Api-Version': '2022-11-28'}
    token = os.environ.get('GH_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    with urlopen(Request(f'https://api.github.com/repos/{repo}', headers=headers), timeout=20) as response:
        data = json.load(response)
    count = data.get('stargazers_count')
    if data.get('private') is not False or type(count) is not int or count < 0:
        raise ValueError('Invalid public repository count')
    return count

def refresh_one(repo, previous, fetch=fetch_count):
    try:
        count = fetch(repo)
        if type(count) is not int or count < 0:
            raise ValueError('Invalid star count')
        return {'stars': count, 'updated_at': datetime.now(timezone.utc).isoformat()}, None
    except Exception as error:
        return previous, type(error).__name__

def main():
    papers = json.loads((ROOT/'data/publications.json').read_text())
    service = json.loads((ROOT/'data/service.json').read_text())
    urls = [resource['url'] for paper in papers for resource in paper.get('resources', []) if resource['label']=='Code']
    urls += [project['url'] for project in service['open_source']]
    repos = sorted({key for url in urls if (key := repository_key(url))})
    path = ROOT/'data/github.json'
    old = json.loads(path.read_text()) if path.exists() else {}
    snapshot = {}
    def refresh(repo):
        return repo, refresh_one(repo, old.get(repo))
    with ThreadPoolExecutor(max_workers=4) as pool:
        for repo, (entry, error) in pool.map(refresh, repos):
            if entry is not None:
                snapshot[repo] = entry
            if error:
                print(f'::warning::GitHub stars unavailable for {repo} ({error}); retaining prior value if available.')
            else:
                print(f'{repo}: {entry["stars"]} stars')
    path.write_text(json.dumps(snapshot, indent=2, sort_keys=True)+'\n')

if __name__ == '__main__':
    main()
