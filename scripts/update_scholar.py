#!/usr/bin/env python3
"""Refresh public Scholar metrics; never replace good data with a failed fetch."""
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE_ID = '7kB-4sEAAAAJ'
URL = f'https://scholar.google.com/citations?user={PROFILE_ID}&hl=en'
DEST = ROOT / 'data/scholar.json'

def text(html):
    return unescape(re.sub(r'<[^>]+>', '', html)).strip()

def parse_metrics(html):
    name = re.search(r'<[^>]+id=["\']gsc_prf_in["\'][^>]*>(.*?)</', html, re.S)
    if not name or not any(x in text(name[1]).lower() for x in ('jiakai tang', '唐嘉凯')):
        raise ValueError('Expected Scholar profile identity is missing')
    table = re.search(r'<table\b[^>]*id=["\']gsc_rsb_st["\'][^>]*>(.*?)</table>', html, re.S)
    if not table:
        raise ValueError('Scholar statistics table is missing')
    metrics = {}
    labels = {'Citations': 'citations', 'h-index': 'h_index', 'i10-index': 'i10_index'}
    for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>', table[1], re.S):
        heading = re.search(r'<td\b[^>]*>(.*?)</td>', row, re.S)
        label = text(heading[1]) if heading else None
        cells = re.findall(r'<td\b[^>]*class=["\'][^"\']*\bgsc_rsb_std\b[^"\']*["\'][^>]*>(.*?)</td>', row, re.S)
        if label in labels and cells:
            value=text(cells[0]).replace(',', '').replace('\u00a0', '')
            if not re.fullmatch(r'\d+', value):
                raise ValueError(f'Invalid {label} value')
            metrics[labels[label]] = int(value)
    if set(metrics) != set(labels.values()) or not all(v > 0 for v in metrics.values()):
        raise ValueError('Incomplete or empty Scholar metrics')
    if metrics['citations'] < metrics['h_index'] ** 2 or metrics['citations'] < metrics['i10_index'] * 10:
        raise ValueError('Inconsistent Scholar metrics')
    return metrics

def refresh(destination=DEST, fetch=None):
    try:
        if fetch is None:
            request = Request(URL, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US,en;q=0.9'})
            with urlopen(request, timeout=30) as response:
                html = response.read().decode('utf-8')
        else:
            html = fetch()
        result = dict(profile_id=PROFILE_ID, source_url=URL, **parse_metrics(html), updated_at=datetime.now(timezone.utc).isoformat(timespec='seconds'))
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary=destination.with_suffix('.tmp')
        temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        temporary.replace(destination)
        print(f'Scholar refreshed: citations={result["citations"]}, h-index={result["h_index"]}, i10-index={result["i10_index"]}')
        return True
    except (HTTPError, URLError, TimeoutError, ValueError, UnicodeError, OSError) as error:
        print(f'::warning::Scholar refresh unavailable ({type(error).__name__}); preserving the last verified snapshot.', file=sys.stderr)
        if not destination.exists():
            raise RuntimeError('No previous Scholar snapshot is available') from error
        return False

if __name__ == '__main__':
    refresh()
