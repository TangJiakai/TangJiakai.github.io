#!/usr/bin/env python3
"""Compute bge-m3 vectors for publication search through the semantic-search Worker.

Each paper is split into passages: its title, each abstract sentence, and its topic
keywords. Scoring a paper by its best passage keeps one specific sentence (say, a cost
reduction) from being diluted by the rest of the abstract, and lets the page show the
sentence that matched. Vectors are scaled to int8; passages whose text is unchanged
reuse their stored vector, so later runs only send new or edited text.

Run after update_abstracts.py: python3 scripts/update_embeddings.py
The Worker URL comes from data/semantic.json ({"endpoint": "https://..."}).
"""
from pathlib import Path
from hashlib import sha256
import base64,json,math,re,urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/embeddings.json'
endpoint=json.loads((ROOT/'data/semantic.json').read_text())['endpoint']
papers=json.loads((ROOT/'data/publications.json').read_text())
abstracts=json.loads((ROOT/'data/abstracts.json').read_text())
keywords=json.loads((ROOT/'data/search_keywords.json').read_text())
stored=json.loads(OUT.read_text()) if OUT.exists() else {}
known={passage['hash']:passage['vector'] for passage in stored.get('passages',[])}

def passages_for(paper):
    # Split at sentence ends only, so decimals such as "55.8%" stay inside their sentence.
    sentences=re.split(r'(?<=[.!?])\s+(?=[A-Z(])',abstracts.get(paper['id'],{}).get('abstract',''))
    texts=[paper['title']]+[sentence for sentence in sentences if len(sentence)>30]
    if keywords.get(paper['id']): texts.append(', '.join(keywords[paper['id']]))
    return [('topics' if index==len(texts)-1 and keywords.get(paper['id']) else 'title' if index==0 else 'abstract',text) for index,text in enumerate(texts)]

def embed(texts):
    request=urllib.request.Request(endpoint,data=json.dumps({'texts':texts}).encode(),headers={'Content-Type':'application/json','User-Agent':'tangjiakai.github.io embeddings updater'})
    with urllib.request.urlopen(request,timeout=120) as response:
        body=json.loads(response.read())
    return body['model'],body['vectors']

def encode(vector):
    # Per-vector int8 scaling keeps direction, which is all cosine similarity needs.
    peak=max(abs(value) for value in vector) or 1.0
    return base64.b64encode(bytes((round(value/peak*127))&0xFF for value in vector)).decode()

passages=[]
for paper in papers:
    for kind,text in passages_for(paper):
        passages.append({'paper':paper['id'],'kind':kind,'text':text,'hash':sha256(text.encode()).hexdigest()[:16]})
pending=[passage for passage in passages if passage['hash'] not in known]
model=stored.get('model')
for start in range(0,len(pending),40):
    batch=pending[start:start+40]
    model,vectors=embed([passage['text'] for passage in batch])
    for passage,vector in zip(batch,vectors):
        assert math.isfinite(sum(vector))
        known[passage['hash']]=encode(vector)
    print(f'Embedded {start+len(batch)} of {len(pending)} new passages.')
for passage in passages:
    passage['vector']=known[passage['hash']]
OUT.write_text(json.dumps({'model':model,'dims':len(base64.b64decode(passages[0]['vector'])),'passages':passages},ensure_ascii=False,indent=1)+'\n')
print(f'Saved {len(passages)} passage vectors for {len(papers)} papers to {OUT.relative_to(ROOT)}.')
