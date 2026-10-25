#!/usr/bin/env python3
"""Build a dependency-free academic homepage from public publication data."""
from pathlib import Path
from html import escape as esc
from hashlib import sha256
import base64,json,re
from update_github import repository_key, visible_count
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
style_version=sha256((ROOT/'assets/style.css').read_bytes()).hexdigest()[:12]
favicon_version=sha256((ROOT/'assets/favicon.svg').read_bytes()).hexdigest()[:12]
script_version=sha256((ROOT/'assets/site.js').read_bytes()).hexdigest()[:12]
papers=json.loads((ROOT/'data/publications.json').read_text())
def publication_priority(p):
    published=not any(tag in p['badge'] for tag in ('Preprint','Under review'))
    return (p['year'],bool(p['award']),p['first'],published)
papers.sort(key=publication_priority,reverse=True)
scholar=json.loads((ROOT/'data/scholar.json').read_text())
scholar_date=datetime.fromisoformat(scholar['updated_at']).astimezone(ZoneInfo('Asia/Singapore')).strftime('%b %d, %Y')
honors=json.loads((ROOT/'data/honors.json').read_text())
honor_groups=[]
for category, heading in [('research','Research Awards'),('university','Scholarships & University Honors'),('competition','Competition Awards')]:
    honor_rows=[]
    for award in (a for a in honors if a['category']==category):
        title=esc(award['title'])
        if award['highlight']: title=f'<strong class="award-text">{title}</strong>'
        chinese=f'<span class="honor-cn" lang="zh-CN">{esc(award["chinese"])}</span>' if award['chinese'] else ''
        summary=f'<span class="honor-detail">{esc(award["summary"])}</span>' if award.get("summary") else ""
        honor_rows.append((award['highlight'] or category!='university',f'<li><span class="date">{esc(award["date"])}</span><div>{title}{chinese}<span class="honor-detail">{esc(award["detail"])}</span>{summary}</div></li>'))
    # Highlighted university honors stay visible; the rest fold into a disclosure.
    shown=''.join(row for visible,row in honor_rows if visible)
    folded=[row for visible,row in honor_rows if not visible]
    more=f'<details class="honor-more"><summary>More university honors ({len(folded)})</summary><ul class="dated-list honors-list">{"".join(folded)}</ul></details>' if folded else ''
    honor_groups.append(f'<div class="honor-group"><h3 class="honor-group-title">{esc(heading)}</h3><ul class="dated-list honors-list">{shown}</ul>{more}</div>')

def icon(name):
    paths={
        'dblp':'<path d="m3 2 9 5v12l-9-5Z"/><path d="m13 5 8 4v13l-8-4Z" opacity=".65"/>',
        'linkedin':'<rect x="2" y="2" width="20" height="20" rx="2"/><circle cx="7" cy="7" r="1.4" fill="white"/><path d="M7 10v8m5 0v-8m0 4c0-5 6-5 6 0v4" fill="none" stroke="white" stroke-width="2.3"/>',
        'corresponding':'<g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/></g>',
        'paper':'<g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H5v18h14V8Z"/><path d="M14 3v5h5M8 12h8M8 16h8"/></g>',
        'pin':'<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5" fill="white"/>',
        'mail':'<path d="M2 5h20v14H2Z"/><path d="m3 6 9 7 9-7" fill="none" stroke="white" stroke-width="1.8"/>',
        'search':'<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></g>',
        'quote':'<g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M8 4H5v16h3M16 4h3v16h-3"/></g>',
        'scholar':'<path d="m1 8 11-6 11 6-11 6Zm5 4 6 3 6-3v6c-4 3-8 3-12 0Zm15-1h2v8h-2Z"/>',
        'github':'<path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.69c-2.78.61-3.37-1.18-3.37-1.18-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.61.07-.61 1 .07 1.53 1.03 1.53 1.03.89 1.53 2.34 1.09 2.91.83.09-.65.35-1.09.64-1.34-2.22-.25-4.56-1.11-4.56-4.94 0-1.09.39-1.99 1.03-2.69-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.03A9.6 9.6 0 0 1 12 6.99c.85 0 1.71.11 2.51.34 1.91-1.3 2.75-1.03 2.75-1.03.55 1.38.2 2.4.1 2.65.64.7 1.03 1.6 1.03 2.69 0 3.84-2.34 4.69-4.57 4.94.36.31.68.92.68 1.85v2.58c0 .27.18.58.69.48A10 10 0 0 0 12 2Z"/>'
    }
    return f'<svg class="contact-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{paths[name]}</svg>'

github_path=ROOT/'data/github.json'
github_metrics=json.loads(github_path.read_text()) if github_path.exists() else {}
def star_badge(url, show_all=False):
    key=repository_key(url)
    entry=github_metrics.get(key,{})
    count=entry.get('stars') if show_all else visible_count(entry)
    if type(count) is not int or count < 0:
        return ''
    updated=esc(entry.get('updated_at','')[:10])
    label=esc(f'{key}: {count:,} GitHub stars')
    return f'<a class="github-stars" href="{esc(url,quote=True)}" aria-label="{label}" title="GitHub stars · Updated {updated}"><span aria-hidden="true">★</span><span>{count:,}</span></a>'

def repo_button(url, accessible_label):
    # One GitHub control: icon and label, then the star count after a divider.
    key=repository_key(url)
    entry=github_metrics.get(key,{})
    count=visible_count(entry)
    stars=f'<span class="repo-stars"><span aria-hidden="true">★</span>{count:,}</span>' if type(count) is int and count >= 0 else ''
    label=accessible_label+(f', {count:,} GitHub stars' if stars else '')
    title='View code on GitHub'+(f' ({count:,} stars, updated {entry.get("updated_at","")[:10]})' if stars else '')
    return f'<a class="action-chip repo-button" href="{esc(url,quote=True)}" aria-label="{esc(label,quote=True)}" title="{esc(title,quote=True)}"><span class="repo-main">{icon("github")}<span>Code</span></span>{stars}</a>'

def author_html(s):
    # Omit equal-contribution markers throughout rows where Jiakai is listed first.
    if s.split(',')[0].strip().rstrip('†*') == 'Jiakai Tang':
        s=s.replace('†','')
    return esc(s).replace('Jiakai Tang','<strong>Jiakai Tang</strong>').replace('†','<sup>†</sup>').replace('*',f'<span class="corresponding-author" role="img" aria-label="Corresponding author" title="Corresponding author">{icon("corresponding")}</span>')

CONFERENCES={'KDD':'Proceedings of the ACM SIGKDD Conference on Knowledge Discovery and Data Mining','WWW':'Proceedings of the ACM Web Conference','SIGIR':'Proceedings of the International ACM SIGIR Conference on Research and Development in Information Retrieval','CIKM':'Proceedings of the ACM International Conference on Information and Knowledge Management','RecSys':'Proceedings of the ACM Conference on Recommender Systems','ACL':'Proceedings of the Annual Meeting of the Association for Computational Linguistics','NAACL':'Proceedings of the Conference of the North American Chapter of the Association for Computational Linguistics','EMNLP':'Proceedings of the Conference on Empirical Methods in Natural Language Processing','DASFAA':'International Conference on Database Systems for Advanced Applications','ICDM':'IEEE International Conference on Data Mining'}
JOURNALS={'TOIS':'ACM Transactions on Information Systems','TKDE':'IEEE Transactions on Knowledge and Data Engineering','FCS':'Frontiers of Computer Science'}
# Citations fetched by update_bibtex.py (published version first, then arXiv);
# papers without one fall back to an entry generated from the publication data.
bibtex_path=ROOT/'data/bibtex.json'
fetched_bibtex=json.loads(bibtex_path.read_text()) if bibtex_path.exists() else {}
def bibtex(p):
    if p['id'] in fetched_bibtex: return fetched_bibtex[p['id']]['bibtex']
    authors=[a.strip().rstrip('†*').strip() for a in p['authors'].split(',')]
    authors=['others' if a=='et al.' else a for a in authors if a]
    key=re.sub(r'[^a-z]','',authors[0].split()[-1].lower())+str(p['year'])+re.sub(r'[^a-z]','',p['title'].split()[0].lower())
    venue=p['venue'].split()[0]
    fields=[('title','{'+p['title']+'}'),('author',' and '.join(authors)),('year',str(p['year']))]
    if 'Workshop' in p['venue']: kind,extra='inproceedings',[('booktitle','Companion Proceedings of the ACM Web Conference')]
    elif venue in CONFERENCES: kind,extra='inproceedings',[('booktitle',CONFERENCES[venue])]
    elif venue in JOURNALS: kind,extra='article',[('journal',JOURNALS[venue])]
    else: kind,extra='misc',[('howpublished',venue if venue!='Preprint' else 'Preprint')]
    if p['link']: extra.append(('url',p['link']))
    body=',\n'.join(f'  {name}={{{value}}}' for name,value in fields+extra)
    return f'@{kind}{{{key},\n{body}\n}}'

rows=[]
last_year=None
for p in papers:
    if p['year']!=last_year:
        if last_year is not None: rows.append('</ul></div>')
        rows.append(f'<div class="publication-year" id="year-{p["year"]}"><h3 class="year-heading"><span>{p["year"]}</span></h3><ul class="publications-list">')
        last_year=p['year']
    title=esc(p['title'])
    title_url=p['link'] or p.get('website','')
    if title_url: title=f'<a href="{esc(title_url,quote=True)}">{title}</a>'
    badges=[]
    if 'CCF-A' in p['badge']: badges.append('<span class="badge ccf-a">CCF-A</span>')
    elif 'CCF-B' in p['badge']: badges.append('<span class="badge ccf-b">CCF-B</span>')
    if p['award']: badges.append(f'<span class="badge award">🏆 {esc(p["award"])}</span>')
    if 'Oral' in p['badge']: badges.append('<span class="badge oral">🌟 Oral</span>')
    if p.get('deployed'):
        badges.append('<span class="badge deployed" title="Deployed in a real-world industrial system"><span aria-hidden="true">🚀</span> Deployed</span>')
    resource_links=[]
    for resource in p.get('resources', []):
        label=esc(resource['label'])
        url=esc(resource['url'],quote=True)
        accessible_label=esc(f"{resource['label']}: {p['title']}",quote=True)
        if resource['label']=='Code' and resource['url'].startswith('https://github.com/'):
            resource_links.append(repo_button(resource['url'],f"Code: {p['title']}"))
        else:
            resource_links.append(f'<a class="paper-link" href="{url}" aria-label="{accessible_label}">[{label}]</a>')
    paper_link=f'<a class="action-chip" href="{esc(p["link"],quote=True)}" aria-label="Paper: {esc(p["title"],quote=True)}" title="Read paper">{icon("paper")}<span>Paper</span></a>' if p['link'] else ''
    venue_badge=f'<span class="badge venue">{esc(p["venue"])}</span>'
    if p.get('website'):
        venue_badge=f'<a class="badge venue" href="{esc(p["website"],quote=True)}" title="Workshop website">{esc(p["venue"])}</a>'
    year=p['year']
    bib_button=f'<button type="button" class="action-chip bibtex-button" data-bibtex="{esc(bibtex(p),quote=True)}" title="Copy BibTeX" hidden>{icon("quote")}<span>BibTeX</span></button>'
    flags=' '.join(f'data-{name}="true"' for name,on in [('selected',p.get('selected')),('deployed',p.get('deployed')),('award',p['award'])] if on)
    search_text=' '.join([p['title'],p.get('short',''),p['authors'].replace('†','').replace('*',''),p['venue'],p['badge'],p['award'],p.get('summary',''),'deployed industrial' if p.get('deployed') else ''])
    rows.append(f'''<li class="publication" id="{p['id']}" data-year="{year}" data-first="{str(p['first']).lower()}" {flags} data-search="{esc(search_text.lower(),quote=True)}">
      <h4>{title}</h4>
      <p class="authors">{author_html(p['authors'])}</p>
      <p class="paper-meta">{venue_badge}{''.join(badges)}{paper_link}{''.join(resource_links)}{bib_button}</p>
    </li>''')
rows.append('</ul></div>')

# Homepage cards: papers marked "selected" in the data, in their listed order.
# An optional "teaser" image path replaces the typographic cover.
selected_cards=[]
for p in sorted((p for p in papers if p.get('selected')),key=lambda p:p['selected']):
    url=esc(p['link'] or f"publications.html#{p['id']}",quote=True)
    cover=f'<img src="{esc(p["teaser"],quote=True)}" alt="" loading="lazy" decoding="async"><span class="cover-chip">{esc(p["short"])}</span>' if p.get('teaser') else f'<span class="cover-name">{esc(p["short"])}</span><span class="cover-venue">{esc(p["venue"])}</span>'
    # The typographic cover already names the venue.
    tags=[f'<span class="badge venue">{esc(p["venue"])}</span>'] if p.get('teaser') else []
    if p['award']: tags.append('<span class="badge award">🏆 Best Paper</span>')
    if 'Oral' in p['badge']: tags.append('<span class="badge oral">🌟 Oral</span>')
    if p.get('deployed'): tags.append('<span class="badge deployed"><span aria-hidden="true">🚀</span> Deployed</span>')
    role='First author' if p['authors'].split(',')[0].strip().rstrip('†*')=='Jiakai Tang' else 'Co-first author'
    code=next((r['url'] for r in p.get('resources',[]) if r['label']=='Code'),'')
    actions=(f'<a href="{esc(p["link"],quote=True)}">Paper</a>' if p['link'] else '')+(f'<a href="{esc(code,quote=True)}">Code</a>' if code else '')
    selected_cards.append(f'''<li class="paper-card">
        <a class="paper-cover {'paper-cover--figure' if p.get('teaser') else 'cover-'+str(p['selected'])}" href="{url}" tabindex="-1" aria-hidden="true">{cover}</a>
        <div class="paper-card-body">
          <p class="paper-tags">{''.join(tags)}</p>
          <h3><a href="{url}">{esc(p['title'])}</a></h3>
          <p class="paper-summary">{esc(p['summary'])}</p>
          <p class="paper-card-foot"><span>{role}</span><span class="paper-actions">{actions}</span></p>
        </div>
      </li>''')

patents=json.loads((ROOT/'data/patents.json').read_text())
patent_rows=[]
for patent in sorted(patents,key=lambda p:p['filing_date'],reverse=True):
    status_label='Granted · 已授权' if patent['status']=='granted' else 'Filed · 已申请'
    inventors=esc(patent['inventors']).replace('唐嘉凯','<strong>唐嘉凯</strong>')
    patent_rows.append(f'''<li class="patent">
      <h3 lang="zh-CN">{esc(patent['title'])}</h3>
      <p class="authors" lang="zh-CN">{inventors}</p>
      <p class="patent-applicant"><span>Applicant:</span> <span lang="zh-CN">{esc(patent['applicant'])}</span></p>
      <p class="paper-meta"><span class="badge patent-{patent['status']}">{status_label}</span><span class="patent-number">Application No. CN {esc(patent['application_number'])}</span><span class="patent-date">Filed {esc(patent['filing_date'].replace('-','.'))}</span></p>
    </li>''')

service_data=json.loads((ROOT/'data/service.json').read_text())
talk_rows=[]
for talk in sorted(service_data.get('invited_talks', []), key=lambda t:t['date'], reverse=True):
    talk_rows.append(f'''<li><time class="date" datetime="{esc(talk['date'],quote=True)}">{esc(talk['date'].replace('-','.'))}</time><div><div class="service-entry-heading"><h4>{esc(talk['title'])}</h4></div><p class="service-description">{esc(talk['host'])} · {esc(talk['location'])}</p><p class="service-description" lang="zh-CN">{esc(talk['title_zh'])}</p></div></li>''')
workshop_rows=[]
for workshop in sorted(service_data['workshops'],key=lambda w:w['year'],reverse=True):
    workshop_rows.append(f'''<li><span class="date">{workshop['year']}</span><div><div class="service-entry-heading"><h4><a href="{esc(workshop['url'],quote=True)}">{esc(workshop['name'])}</a></h4><span class="service-role service-role--organizer">{esc(workshop['role'])}</span></div><p class="service-description">{esc(workshop['title'])}</p></div></li>''')
volunteer_rows=[]
for event in sorted(service_data.get('volunteering', []), key=lambda e:e['year'], reverse=True):
    volunteer_rows.append(f'''<li><span class="date">{event['year']}</span><div class="service-entry-heading"><h4>{esc(event['conference'])}</h4><span class="service-role service-role--volunteer">{esc(event['role'])}</span></div></li>''')
software_rows=[]
for project in service_data['open_source']:
    role_style='lead' if project['role']=='Lead Developer' else 'contributor'
    software_rows.append(f'''<li><div class="software-heading"><h4><a href="{esc(project['url'],quote=True)}">{icon('github')}{esc(project['name'])}</a></h4><span class="service-role service-role--{role_style}">{esc(project['role'])}</span>{star_badge(project['url'], show_all=True)}</div><p class="service-description">{esc(project['description'])}</p></li>''')
review_rows=[]
for group in service_data['reviewing']:
    venues=''.join(f'<li>{esc(venue)}</li>' for venue in group['venues'])
    review_rows.append(f'''<div class="review-group"><div><h4>{esc(group['label'])}</h4><span class="review-role">{esc(group['role'])}</span></div><ul class="venue-list" aria-label="{esc(group['label'])}">{venues}</ul></div>''')

nav=[('index.html','Home'),('publications.html','Publications'),('patents.html','Patents'),('gallery.html','Gallery')]
navhtml=''.join(f'<a href="{k}">{v}</a>' for k,v in nav)
structured={"@context":"https://schema.org","@type":"Person","name":"Jiakai Tang","alternateName":"唐嘉凯","url":"https://tangjiakai.github.io/","image":"https://tangjiakai.github.io/assets/portrait.jpg","affiliation":{"@type":"CollegeOrUniversity","name":"Renmin University of China"},"sameAs":["https://github.com/TangJiakai","https://scholar.google.com/citations?user=7kB-4sEAAAAJ"],"knowsAbout":["Recommender Systems","Large Language Models","Personalized Agents"]}
structured['sameAs'].extend(['https://dblp.org/pid/294/2295.html','https://www.linkedin.com/in/%E5%98%89%E5%87%AF-%E5%94%90-744894299/'])
html=f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Jiakai Tang · 唐嘉凯</title>
  <meta name="description" content="Jiakai Tang is a Ph.D. student at Renmin University of China. Research on recommender systems, reasoning with large language models, and personalized agents.">
  <meta name="theme-color" content="#ffffff">
  <meta name="color-scheme" content="light">
  <script>
    // Light by default; apply a saved dark choice before the first paint.
    (() => {{
      let theme;
      try {{ theme = localStorage.getItem('theme'); }} catch {{}}
      document.documentElement.dataset.theme = theme === 'dark' ? 'dark' : 'light';
    }})();
  </script>
  <meta name="google-site-verification" content="IjU5DXIl_b3xuy8beeihjfm2RMkB2Yd6SPrrIbL4gnI">
  <link rel="canonical" href="https://tangjiakai.github.io/">
  <meta property="og:type" content="profile">
  <meta property="og:title" content="Jiakai Tang · 唐嘉凯">
  <meta property="og:description" content="Recommender systems, large language models, and personalized agents. Ph.D. student at Renmin University of China.">
  <meta property="og:url" content="https://tangjiakai.github.io/">
  <meta property="og:image" content="https://tangjiakai.github.io/assets/portrait.jpg">
  <link rel="icon" href="assets/favicon.svg?v={favicon_version}" type="image/svg+xml">
  <link rel="preload" href="assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="assets/style.css?v={style_version}">
  <script type="application/ld+json">{json.dumps(structured,ensure_ascii=False)}</script>
  <script src="assets/site.js?v={script_version}" defer></script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="masthead"><div class="nav-wrap">
  <a class="brand" href="index.html">Jiakai Tang</a>
  <nav aria-label="Main navigation"><div class="nav-sections">{navhtml}</div><a class="nav-cv" href="assets/Jiakai-Tang-CV.pdf" target="_blank" rel="noopener" title="View CV in a new tab">CV</a><button type="button" class="theme-toggle" aria-label="Switch to dark mode" title="Switch theme"><svg class="icon-moon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z"/></svg><svg class="icon-sun" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/></svg></button></nav>
</div></header>
<div class="page-layout">
  <aside class="profile" aria-label="Profile">
    <img class="portrait" src="assets/portrait.jpg" width="413" height="591" alt="Portrait of Jiakai Tang">
    <h1>Jiakai Tang <span lang="zh-CN">唐嘉凯</span></h1>
    <p class="affiliation">Ph.D. student at Gaoling School of Artificial Intelligence, Renmin University of China.</p>
    <p class="profile-interests">Recommender Systems,<br>Large Language Models,<br>and Personalized Agents.</p>
    <ul class="contact-links">
      <li><span class="contact-row">{icon('pin')}<span>Beijing, China</span></span></li>
      <li><a class="contact-row" href="mailto:tangjiakai5704@gmail.com">{icon('mail')}<span>Email</span></a></li>
      <li><a class="contact-row" href="https://github.com/TangJiakai">{icon('github')}<span>GitHub</span></a></li>
      <li><a class="contact-row" href="https://scholar.google.com/citations?user=7kB-4sEAAAAJ">{icon('scholar')}<span>Google Scholar</span></a></li>
      <li><a class="contact-row" href="https://dblp.org/pid/294/2295.html">{icon('dblp')}<span>DBLP</span></a></li>
      <li><a class="contact-row" href="https://www.linkedin.com/in/%E5%98%89%E5%87%AF-%E5%94%90-744894299/">{icon('linkedin')}<span>LinkedIn</span></a></li>
    </ul>
  </aside>
  <main id="main">
    <section id="about" aria-labelledby="about-title">
      <h2 id="about-title" class="sr-only">About Me</h2>
      <p>I am a Ph.D. student in the <a href="https://ai.ruc.edu.cn/">Gaoling School of Artificial Intelligence</a> at <a href="https://www.ruc.edu.cn/">Renmin University of China</a>, advised by <a href="https://ai.ruc.edu.cn/szdw/zrjs/cx/index.htm">Prof. Xu Chen</a>. I am a member of the <a href="https://ai-engine-lab.com/">AI-Engine Lab</a>. I joined the integrated master's–Ph.D. program in 2022 and expect to graduate in 2028. Previously, I received my bachelor's degree in Computer Science and Technology from Wuhan University of Technology in 2022.</p>
      <p>My research focuses on <strong>LLM-powered recommender systems and personalized agents</strong>. I study reasoning for recommendation, user intent understanding, and interactive agents with long-term memory. I am also interested in faithful user simulation and evaluation, connecting algorithmic advances with real-world applications.</p>
      <p>I have worked on industrial recommendation at Taobao through the RecGPT series (<a href="https://dl.acm.org/doi/10.1145/3846382" aria-label="RecGPT V1 paper">V1</a> · <a href="https://arxiv.org/abs/2512.14503" aria-label="RecGPT V2 technical report">V2</a> · <a href="https://arxiv.org/abs/2607.15591" aria-label="RecGPT V3 technical report">V3</a>), and on reasoning for industrial ranking through <a href="https://dl.acm.org/doi/10.1145/3770855.3818456">OnePiece</a>. My recent research interests include efficient long-sequence modeling for large language models, personalized memory, and personalized agents.</p>
      <div class="email-contacts" aria-label="Email addresses">
        <div class="email-contact-row"><span class="email-label">Long-term</span><div class="email-options"><a href="mailto:tangjiakai5704@gmail.com">tangjiakai5704@gmail.com</a><a href="mailto:1049765241@qq.com">1049765241@qq.com</a></div></div>
        <div class="email-contact-row"><span class="email-label">University</span><div><a href="mailto:tangjiakai5704@ruc.edu.cn">tangjiakai5704@ruc.edu.cn</a><span class="email-note">May be unavailable after graduation.</span></div></div>
      </div>
      <ul class="stat-strip" aria-label="Google Scholar metrics">
        <li><a href="{scholar['source_url']}"><strong>{scholar['citations']:,}</strong><span>Citations</span></a></li>
        <li><a href="{scholar['source_url']}"><strong>{scholar['h_index']}</strong><span>h-index</span></a></li>
      </ul>
      <p class="stat-note">{icon('scholar')}<span>Citation metrics from <a href="{scholar['source_url']}">Google Scholar</a>, updated {scholar_date}</span></p>
    </section>
    <section id="selected" aria-labelledby="selected-title">
      <h2 id="selected-title"><span aria-hidden="true">✨</span> Selected Publications</h2>
      <ul class="paper-cards">{''.join(selected_cards)}</ul>
      <p class="section-more"><a href="publications.html">All {len(papers)} publications →</a></p>
    </section>
    <section id="news" aria-labelledby="news-title">
      <h2 id="news-title"><span aria-hidden="true">🔥</span> News</h2>
      <ul class="news-list">
        <li><time datetime="2026-12">2026.12</time><span><span class="news-celebration" aria-hidden="true">🎉</span> <strong>RecGPT-V3</strong> received the <span class="award-text">🏆 SIGIR-AP GRIT Workshop Best Paper</span> award.</span></li>
        <li><time datetime="2026-12">2026.12</time><span><span class="news-celebration" aria-hidden="true">🎉</span> Received my fourth <strong>National Scholarship</strong>, following awards in 2019, 2020, and 2021.</span></li>
        <li><time datetime="2026-10">2026.10</time><span>Released <a href="https://arxiv.org/abs/2610.30932">UserArena</a> (<strong>co-first author</strong>; proposed the core idea and co-wrote the paper), a benchmark for interactive user simulation with long-horizon shopping agents.</span></li>
        <li><time datetime="2026-10">2026.10</time><span>Released <a href="https://arxiv.org/abs/2610.30128">LoopRec</a> (<strong>co-first author</strong>; proposed the core idea and co-wrote the paper), exploring item-level adaptive recursion for sequential recommendation.</span></li>
        <li><time datetime="2026-09">2026.09</time><span><span class="news-celebration" aria-hidden="true">🎉</span> <a href="https://ieeexplore.ieee.org/document/11523596/">ReaRec</a> (<strong>first author</strong>) was published in <strong>IEEE TKDE</strong>.</span></li>
        <li><time datetime="2026-08">2026.08</time><span>Released <a href="https://arxiv.org/abs/2608.20707">RecVerse</a> (<strong>first author</strong>), a GUI-grounded shopping simulation agent with hierarchical memory and trajectory-level reinforcement learning.</span></li>
        <li><time datetime="2026-08">2026.08</time><span><span class="news-celebration" aria-hidden="true">🎉</span> <a href="https://dl.acm.org/doi/10.1145/3770855.3818456">OnePiece</a> (<strong>co-first author</strong>) was published at <strong>KDD 2026</strong> with an <span class="oral-text">🌟 Oral presentation</span>.</span></li>
        <li><time datetime="2026-08">2026.08</time><span><span class="news-celebration" aria-hidden="true">🎉</span> <a href="https://dl.acm.org/doi/10.1145/3770855.3817619">RecBot</a> (<strong>first author</strong>) was published at <strong>KDD 2026</strong>.</span></li>
        <li><time datetime="2026-08">2026.08</time><span><span class="news-celebration" aria-hidden="true">🎉</span> <a href="https://dl.acm.org/doi/10.1145/3770855.3818457">OneRank</a> (<strong>first author</strong>) was published at <strong>KDD 2026</strong>.</span></li>
        <li><time datetime="2026-08">2026.08</time><span><span class="news-celebration" aria-hidden="true">🎉</span> <a href="https://dl.acm.org/doi/10.1145/3846382">RecGPT</a> (<strong>first author</strong>) was accepted by <strong>ACM TOIS</strong>.</span></li>
      </ul>
    </section>
    <section id="publications" aria-labelledby="publications-title">
      <h2 id="publications-title"><span aria-hidden="true">📝</span> Publications</h2>
      {''.join(rows)}
    </section>
    <section id="patents" aria-labelledby="patents-title">
      <h2 id="patents-title"><span aria-hidden="true">💡</span> Patents</h2>
      <ul class="patents-list">{''.join(patent_rows)}</ul>
    </section>
    <section id="honors" aria-labelledby="honors-title">
      <h2 id="honors-title"><span aria-hidden="true">🎖️</span> Honors and Awards</h2>
      {''.join(honor_groups)}
    </section>
    <section id="education" aria-labelledby="education-title">
      <h2 id="education-title"><span aria-hidden="true">📖</span> Education</h2>
      <ul class="dated-list education-list">
        <li><span class="date">2022.09–Present</span><div class="school"><span class="school-logo" aria-hidden="true"><img src="assets/logos/ruc.webp" alt="" width="56" height="56" loading="lazy" decoding="async"></span><h3>Renmin University of China</h3><p>Integrated Master's–Ph.D. Program in Artificial Intelligence<br>Gaoling School of Artificial Intelligence · Advisor: <a href="https://ai.ruc.edu.cn/szdw/zrjs/cx/index.htm" target="_blank" rel="noopener">Xu Chen</a><br><span class="muted">Expected graduation: 2028</span></p></div></li>
        <li><span class="date">2026.05–2026.11</span><div class="school school--next"><span class="school-logo school-logo--next" aria-hidden="true"><img src="assets/logos/next.png" alt="" width="100" height="56" loading="lazy" decoding="async"></span><h3>National University of Singapore</h3><p>Joint Ph.D. Training · School of Computing<br><a href="https://www.nextcenter.org/" target="_blank" rel="noopener">NExT++ Lab</a><br>Advisors: <a href="https://www.comp.nus.edu.sg/cs/people/ngsk/" target="_blank" rel="noopener">See-Kiong Ng</a> and <a href="https://zyang1580.github.io/" target="_blank" rel="noopener">Yang Zhang</a></p></div></li>
        <li><span class="date">2018.09–2022.06</span><div class="school"><span class="school-logo" aria-hidden="true"><img src="assets/logos/whut.png" alt="" width="56" height="56" loading="lazy" decoding="async"></span><h3>Wuhan University of Technology</h3><p>Bachelor's Degree in Computer Science and Technology<br><span class="muted">Ranked 1 / 257</span></p></div></li>
      </ul>
    </section>
    <section id="experience" aria-labelledby="experience-title">
      <h2 id="experience-title"><span aria-hidden="true">💻</span> Internships</h2>
      <ul class="dated-list experience-list">
        <li><span class="date">2025.04–Present</span><div class="employer"><span class="company-logo company-logo--taotian" aria-hidden="true"><img src="assets/logos/taotian.png" alt="" loading="lazy" decoding="async"></span><div><h3 class="employer-heading"><span>Alibaba · Taotian</span><span class="talent-badge" title="T-Star 人才实习"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8-6.2-3.2L5.8 21 7 14.2 2 9.3l6.9-1Z"/></svg><strong>T-Star</strong><span>Talent Intern</span></span></h3><p class="position">Recommendation Algorithm Intern</p></div></div></li>
        <li><span class="date">2024.11–2025.03</span><div class="employer"><span class="company-logo company-logo--wechat" aria-hidden="true"><img src="assets/logos/wechat.svg" alt="" loading="lazy" decoding="async"></span><div><h3>Tencent · WeChat</h3><p class="position">LLM Agent Algorithm Intern</p></div></div></li>
        <li><span class="date">2024.05–2024.11</span><div class="employer"><span class="company-logo company-logo--tongyi" aria-hidden="true"><img src="assets/logos/tongyi.svg" alt="" loading="lazy" decoding="async"></span><div><h3>Alibaba · Tongyi</h3><p class="position">LLM Agent Algorithm Intern</p></div></div></li>
        <li><span class="date">2023.10–2024.04</span><div class="employer"><span class="company-logo company-logo--kuaishou" aria-hidden="true"><img src="assets/logos/kuaishou.png" alt="" loading="lazy" decoding="async"></span><div><h3>Kuaishou</h3><p class="position">Recommendation Algorithm Intern</p></div></div></li>
        <li><span class="date">2023.02–2023.07</span><div class="employer"><span class="company-logo company-logo--noah" aria-hidden="true"><img src="assets/logos/noah.png" alt="" loading="lazy" decoding="async"></span><div><h3>Huawei · Noah's Ark Lab</h3><p class="position">Recommendation Algorithm Intern</p></div></div></li>
      </ul>
    </section>
    <section id="talks" aria-labelledby="talks-title">
      <h2 id="talks-title"><span aria-hidden="true">🎤</span> Invited Talks</h2>
      <ul class="dated-list workshop-list">{''.join(talk_rows)}</ul>
    </section>
    <section id="service" aria-labelledby="service-title">
      <h2 id="service-title"><span aria-hidden="true">📚</span> Academic Services</h2>
      <div class="service-group">
        <h3 class="service-group-title">Workshop Organization</h3>
        <ul class="dated-list workshop-list">{''.join(workshop_rows)}</ul>
      </div>
      <div class="service-group" id="conference-volunteering">
        <h3 class="service-group-title">Conference Volunteering</h3>
        <ul class="dated-list workshop-list">{''.join(volunteer_rows)}</ul>
      </div>
      <div class="service-group">
        <h3 class="service-group-title">Open-Source Software</h3>
        <ul class="software-list">{''.join(software_rows)}</ul>
      </div>
      <div class="service-group">
        <h3 class="service-group-title">Conference &amp; Journal Service</h3>
        {''.join(review_rows)}
      </div>
    </section>
    <footer><span>© 2026 Jiakai Tang · Last updated October 24, 2026</span><a href="#about">Back to top ↑</a></footer>
  </main>
</div>
</body>
</html>
'''
# Share the profile and page shell while keeping long collections off the homepage.
sections={match.group(1):match.group(0) for match in re.finditer(r'<section id="([^"]+)".*?</section>',html,re.S)}
news_items=re.findall(r'<li>.*?</li>',sections['news'],re.S)
# Keep this year's news and the previous year's final quarter expanded.
# In 2027, August and September 2026 move into Earlier news on the next build.
news_cutoff=f"{datetime.now(ZoneInfo('Asia/Singapore')).year-1}-10"
recent_news=[]
archived_news=[]
for item in news_items:
    month=re.search(r'datetime="(\d{4}-\d{2})"',item)
    (archived_news if month and month.group(1)<news_cutoff else recent_news).append(item)
sections['news']=re.sub(r'<ul class="news-list">.*?</ul>',
    '<ul class="news-list">'+''.join(recent_news)+'</ul>'+
    ('<details class="news-archive"><summary>Earlier news</summary><ul class="news-list">'+''.join(archived_news)+'</ul></details>' if archived_news else ''),
    sections['news'],flags=re.S)
home_sections=[('about','About Me'),('selected','Selected Papers'),('news','News'),('experience','Internships'),('education','Education'),('honors','Honors and Awards'),('talks','Invited Talks'),('service','Academic Services')]
home_nav='<nav class="section-nav floating-nav" aria-label="On this page">'+''.join(f'<a href="#{key}">{label}</a>' for key,label in home_sections)+'</nav>'
home_blocks=[]
for index,(key,label) in enumerate(home_sections):
    classes='home-section' + (' home-section--tinted' if index % 2 else '')
    home_blocks.append(sections[key].replace('<section ',f'<section class="{classes}" ',1))
home_body=home_nav+'\n'+'\n'.join(home_blocks)
publication_nav='<nav class="section-nav floating-nav year-nav" aria-label="Publication years"><span class="floating-nav-label">Year</span>'+''.join(f'<a href="#year-{year}">{year}</a>' for year in sorted({p['year'] for p in papers},reverse=True))+'</nav>'
# Full-text search index: abstracts (update_abstracts.py) plus hand-written English and
# Chinese topic keywords (data/search_keywords.json). site.js loads it on first use.
abstracts_path=ROOT/'data/abstracts.json'
keywords_path=ROOT/'data/search_keywords.json'
abstracts=json.loads(abstracts_path.read_text()) if abstracts_path.exists() else {}
search_keywords=json.loads(keywords_path.read_text()) if keywords_path.exists() else {}
search_index={p['id']:{'abstract':abstracts.get(p['id'],{}).get('abstract',''),'topics':' '.join(search_keywords.get(p['id'],[]))} for p in papers}
index_text=json.dumps(search_index,ensure_ascii=False,separators=(',',':'))
(ROOT/'assets/search-index.json').write_text(index_text)
index_version=sha256(index_text.encode()).hexdigest()[:12]
# Semantic search: the Worker URL (data/semantic.json) and bge-m3 paper vectors
# (update_embeddings.py). Without both, the page keeps keyword search only.
semantic_path=ROOT/'data/semantic.json'
embeddings_path=ROOT/'data/embeddings.json'
semantic_attrs=''
if semantic_path.exists() and embeddings_path.exists():
    # Passage vectors go in one int8 binary file; the manifest lists each passage's paper and text.
    embeddings=json.loads(embeddings_path.read_text())
    current={p['id'] for p in papers}
    passages=[passage for passage in embeddings['passages'] if passage['paper'] in current]
    vector_bytes=b''.join(base64.b64decode(passage['vector']) for passage in passages)
    manifest=json.dumps({'dims':embeddings['dims'],'passages':[[passage['paper'],passage['kind'],passage['text']] for passage in passages]},ensure_ascii=False,separators=(',',':'))
    (ROOT/'assets/semantic-vectors.bin').write_bytes(vector_bytes)
    (ROOT/'assets/semantic-passages.json').write_text(manifest)
    (ROOT/'assets/semantic-index.json').unlink(missing_ok=True)
    semantic_version=sha256(vector_bytes+manifest.encode()).hexdigest()[:12]
    endpoint=json.loads(semantic_path.read_text())['endpoint']
    semantic_attrs=f' data-semantic-endpoint="{esc(endpoint,quote=True)}" data-semantic-vectors="assets/semantic-vectors.bin?v={semantic_version}" data-semantic-passages="assets/semantic-passages.json?v={semantic_version}"'
# Search and filters need JavaScript, so the toolbar stays hidden until site.js reveals it.
publication_filters=[('all','All'),('selected','Selected'),('first','First author'),('deployed','Deployed'),('award','Awards')]
publication_tools=f'''<div class="pub-tools" data-index="assets/search-index.json?v={index_version}"{semantic_attrs} hidden>
  <label class="pub-search">{icon('search')}<span class="sr-only">Search publications</span><input type="search" placeholder="Search titles, abstracts, topics or co-authors (English or 中文)" autocomplete="off" spellcheck="false"><kbd>/</kbd></label>
  <div class="pub-filters" role="group" aria-label="Filter publications">{''.join(f'<button type="button" data-filter="{key}" aria-pressed="{str(key=="all").lower()}">{label}</button>' for key,label in publication_filters)}</div>
  <p class="pub-examples" hidden><span>Try searching by meaning:</span>{''.join(f'<button type="button">{esc(query)}</button>' for query in ['make recommendation cheaper','agents that imitate real shoppers','让推荐更省钱','let users tell the feed what they want'])}</p>
  <p class="pub-count" aria-live="polite"></p>
</div>'''

gallery_items=json.loads((ROOT/'data/gallery.json').read_text())
gallery_groups=[]
gallery_links=[]
album_labels={"CCF YOCSEF · Jinan":"YOCSEF", "KDD 2026 · Jeju Island":"KDD 2026", "KDD 2024 · Barcelona":"KDD 2024", "Singapore · NUS":"NUS", "Everyday Memories":"Everyday", "Jeju Island":"Jeju", "Pingtan · Fujian":"Pingtan", "Spain":"Spain"}
for category,label,description in [('academic','Academic Moments','Talks, conferences, and research gatherings.'),('life','Life','Moments beyond research.')]:
    albums={}
    for photo in (p for p in gallery_items if p['category']==category):
        albums.setdefault(photo.get('album',label),[]).append(photo)
    album_html=[]
    for album,items in albums.items():
        album_id="album-"+re.sub(r"[^a-z0-9]+","-",album.lower()).strip("-")
        gallery_links.append(f'<a href="#{album_id}">{esc(album_labels.get(album,album))}</a>')
        photos=[]
        for photo in items:
            src=esc(photo['src'],quote=True)
            caption=esc(photo.get('caption',''))
            alt=esc(photo['alt'],quote=True)
            thumbnail=esc(photo.get('thumbnail',photo['src']),quote=True)
            dimensions=f' width="{int(photo["width"])}" height="{int(photo["height"])}"' if photo.get('width') and photo.get('height') else ''
            photos.append(f'<figure class="gallery-photo"><a class="gallery-image" href="{src}" data-caption="{esc(photo.get("caption",""),quote=True)}" aria-label="View photo: {alt}"><img src="{thumbnail}" alt="{alt}"{dimensions} loading="lazy" decoding="async"><span class="photo-expand" aria-hidden="true">↗</span></a><figcaption>{caption}</figcaption></figure>')
        layout=' gallery-grid--single' if len(items)==1 else (' gallery-grid--pair' if len(items)==2 or len(items)==4 else '')
        album_html.append(f'<article class="gallery-album" id="{album_id}"><header class="album-heading"><h4>{esc(album)}</h4></header><div class="gallery-grid{layout}">'+''.join(photos)+'</div></article>')
    content=''.join(album_html) if album_html else '<p class="gallery-empty">Photos coming soon.</p>'
    gallery_groups.append(f'<section class="gallery-group" id="{category}"><h3>{label}</h3><p class="muted">{description}</p>{content}</section>')
gallery_body='<section id="gallery" aria-labelledby="gallery-title"><h2 id="gallery-title"><span aria-hidden="true">📷</span> Gallery</h2><p class="page-intro">A collection of academic and everyday moments.</p></section>'+'<nav class="section-nav floating-nav gallery-nav" aria-label="Photo albums">'+''.join(gallery_links)+'</nav>'+''.join(gallery_groups)
gallery_body+='''<dialog class="photo-viewer" aria-label="Photo viewer"><button type="button" class="photo-close" aria-label="Close photo">×</button><figure><img alt=""><figcaption></figcaption></figure></dialog>'''

pages={
    'index.html':('Home',home_body,'Jiakai Tang is a Ph.D. student at Renmin University of China. Research on recommender systems, reasoning with large language models, and personalized agents.'),
    'publications.html':('Publications',sections['publications'].replace('</h2>','</h2>'+publication_tools+publication_nav,1),'Publications by Jiakai Tang on recommender systems, large language models, and personalized agents.'),
    'patents.html':('Patents',sections['patents'],'Patents and industrial research contributions by Jiakai Tang.'),
    'gallery.html':('Gallery',gallery_body,'Academic and everyday moments from Jiakai Tang.'),
}
for filename,(label,body,description) in pages.items():
    url='https://tangjiakai.github.io/'+('' if filename=='index.html' else filename)
    title='Jiakai Tang · 唐嘉凯' if filename=='index.html' else f'{label} · Jiakai Tang'
    footer='<footer><span>© 2026 Jiakai Tang · Last updated October 24, 2026</span><a href="#main">Back to top ↑</a></footer>'
    page=re.sub(r'<main id="main">.*?</main>',lambda _: '<main id="main">'+body+footer+'</main>',html,flags=re.S)
    page=page.replace(f'<a href="{filename}">{label}</a>',f'<a href="{filename}" class="active" aria-current="page">{label}</a>')
    page=re.sub(r'<title>.*?</title>',f'<title>{title}</title>',page)
    for pattern,replacement in [
        (r'<link rel="canonical"[^>]+>',f'<link rel="canonical" href="{url}">'),
        (r'<meta property="og:url"[^>]+>',f'<meta property="og:url" content="{url}">'),
        (r'<meta property="og:title"[^>]+>',f'<meta property="og:title" content="{title}">'),
        (r'<meta name="description"[^>]+>',f'<meta name="description" content="{description}">'),
        (r'<meta property="og:description"[^>]+>',f'<meta property="og:description" content="{description}">'),
    ]:
        page=re.sub(pattern,lambda _,replacement=replacement:replacement,page)
    (ROOT/filename).write_text(page)
urls=''.join('<url><loc>https://tangjiakai.github.io/'+('' if filename=='index.html' else filename)+'</loc><lastmod>2026-10-24</lastmod></url>' for filename in pages)
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>\n')
print(f'Built {len(pages)} pages: {len(papers)} publications, {len(patents)} patents, {len(gallery_items)} photos.')
