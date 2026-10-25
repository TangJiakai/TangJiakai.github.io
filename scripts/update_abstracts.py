#!/usr/bin/env python3
"""Fetch publication abstracts for site search.

Sources, in order: the ACL Anthology, arXiv (by linked ID or exact title match),
Crossref and OpenAlex (by DOI or exact title match), then Semantic Scholar. Existing abstracts in
data/abstracts.json are kept unless a paper is missing one, so manual fixes survive.

Run manually after adding papers: python3 scripts/update_abstracts.py
"""
from pathlib import Path
import html,json,re,time,urllib.parse,urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/abstracts.json'
HEADERS={'User-Agent':'tangjiakai.github.io abstract updater (mailto:tangjiakai5704@gmail.com)'}

def fetch(url):
    # Semantic Scholar rate-limits anonymous use; wait and retry on HTTP 429.
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=60) as response:
                return response.read().decode('utf-8')
        except urllib.error.HTTPError as error:
            if error.code!=429 or attempt==2: raise
            time.sleep(10*(attempt+1))

def normalize(text):
    return re.sub(r'[^a-z0-9]','',re.sub(r'<[^>]+>','',text).lower())

def clean(text):
    text=html.unescape(re.sub(r'<[^>]+>',' ',text))
    text=re.sub(r'\\textbf\{([^}]*)\}',r'\1',text)
    return re.sub(r'^\s*abstract\s*','',' '.join(text.split()),flags=re.I)

def from_arxiv(paper):
    match=re.search(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})',paper['link'])
    query={'id_list':match.group(1)} if match else {'search_query':'ti:"'+paper['title']+'"','max_results':3}
    feed=fetch('https://export.arxiv.org/api/query?'+urllib.parse.urlencode(query))
    for entry in re.findall(r'<entry>(.*?)</entry>',feed,re.S):
        title=' '.join(re.search(r'<title>(.*?)</title>',entry,re.S).group(1).split())
        if match or normalize(title)==normalize(paper['title']):
            return clean(re.search(r'<summary>(.*?)</summary>',entry,re.S).group(1)),'arXiv'
    return '',''

def from_acl_anthology(paper):
    if 'aclanthology.org/' not in paper['link']: return '',''
    match=re.search(r'abstract\s*=\s*"(.*?)",?\s*\n',fetch(paper['link'].rstrip('/')+'.bib'),re.S)
    return (clean(match.group(1)),'ACL Anthology') if match else ('','')

def from_crossref(paper):
    doi=re.search(r'(10\.\d{4,}/[^?#\s]+)',paper['link'])
    if doi:
        doi=doi.group(1).rstrip('/')
        if 'techrxiv' in doi and not doi.endswith('/v1'): doi+='/v1'
        items=[json.loads(fetch('https://api.crossref.org/works/'+urllib.parse.quote(doi)))['message']]
    else:
        query=urllib.parse.urlencode({'query.bibliographic':paper['title'],'rows':5})
        items=json.loads(fetch('https://api.crossref.org/works?'+query))['message']['items']
    for item in items:
        if item.get('abstract') and any(normalize(t)==normalize(paper['title']) for t in item.get('title',[])):
            return clean(item['abstract']),'Crossref'
    return '',''

def from_openalex(paper):
    # OpenAlex stores abstracts as an inverted index of word positions.
    doi=re.search(r'(10\.\d{4,}/[^?#\s]+)',paper['link'])
    if doi:
        items=[json.loads(fetch('https://api.openalex.org/works/doi:'+doi.group(1).rstrip('/')))]
    else:
        items=json.loads(fetch('https://api.openalex.org/works?'+urllib.parse.urlencode({'search':paper['title'],'per-page':5})))['results']
    for item in items:
        inverted=item.get('abstract_inverted_index')
        if inverted and normalize(item.get('title') or '')==normalize(paper['title']):
            words=sorted((position,word) for word,positions in inverted.items() for position in positions)
            return clean(' '.join(word for _,word in words)),'OpenAlex'
    return '',''

def from_semantic_scholar(paper):
    query=urllib.parse.urlencode({'query':paper['title'],'fields':'title,abstract','limit':5})
    for item in json.loads(fetch('https://api.semanticscholar.org/graph/v1/paper/search?'+query)).get('data',[]):
        if item.get('abstract') and normalize(item['title'])==normalize(paper['title']):
            return clean(item['abstract']),'Semantic Scholar'
    return '',''

papers=json.loads((ROOT/'data/publications.json').read_text())
results=json.loads(OUT.read_text()) if OUT.exists() else {}
for paper in papers:
    if results.get(paper['id'],{}).get('abstract'):
        continue
    for source in (from_acl_anthology,from_arxiv,from_crossref,from_openalex,from_semantic_scholar):
        try:
            abstract,name=source(paper)
        except Exception as error:
            abstract,name='',''
            print(f"{paper['id']}: {source.__name__} failed ({error})")
        time.sleep(3)
        if abstract:
            results[paper['id']]={'source':name,'abstract':abstract}
            break
    print(f"{paper['id']:9} {results.get(paper['id'],{}).get('source','missing'):17} {paper['title'][:60]}")
OUT.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(f'Saved abstracts for {len(results)} of {len(papers)} papers to {OUT.relative_to(ROOT)}.')
