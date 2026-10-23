#!/usr/bin/env python3
"""Build a dependency-free academic homepage from public publication data."""
from pathlib import Path
from html import escape as esc
import json,re
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
papers=json.loads((ROOT/'data/publications.json').read_text())
def publication_priority(p):
    published=not any(tag in p['badge'] for tag in ('Preprint','Under review'))
    return (p['year'],bool(p['award']),p['first'],published)
papers.sort(key=publication_priority,reverse=True)
scholar=json.loads((ROOT/'data/scholar.json').read_text())
scholar_date=datetime.fromisoformat(scholar['updated_at']).astimezone(ZoneInfo('Asia/Singapore')).strftime('%b %d, %Y')
honors=json.loads((ROOT/'data/honors.json').read_text())
honor_rows=[]
for award in honors:
    title=esc(award['title'])
    if award['highlight']: title=f'<strong class="award-text">{title}</strong>'
    chinese=f'<span class="honor-cn" lang="zh-CN">{esc(award["chinese"])}</span>' if award['chinese'] else ''
    honor_rows.append(f'<li><span class="date">{esc(award["date"])}</span><div>{title}{chinese}<span class="honor-detail">{esc(award["detail"])}</span></div></li>')

def icon(name):
    paths={
        'pin':'<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5" fill="white"/>',
        'mail':'<path d="M2 5h20v14H2Z"/><path d="m3 6 9 7 9-7" fill="none" stroke="white" stroke-width="1.8"/>',
        'scholar':'<path d="m1 8 11-6 11 6-11 6Zm5 4 6 3 6-3v6c-4 3-8 3-12 0Zm15-1h2v8h-2Z"/>',
        'github':'<path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.69c-2.78.61-3.37-1.18-3.37-1.18-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.61.07-.61 1 .07 1.53 1.03 1.53 1.03.89 1.53 2.34 1.09 2.91.83.09-.65.35-1.09.64-1.34-2.22-.25-4.56-1.11-4.56-4.94 0-1.09.39-1.99 1.03-2.69-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.03A9.6 9.6 0 0 1 12 6.99c.85 0 1.71.11 2.51.34 1.91-1.3 2.75-1.03 2.75-1.03.55 1.38.2 2.4.1 2.65.64.7 1.03 1.6 1.03 2.69 0 3.84-2.34 4.69-4.57 4.94.36.31.68.92.68 1.85v2.58c0 .27.18.58.69.48A10 10 0 0 0 12 2Z"/>'
    }
    return f'<svg class="contact-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{paths[name]}</svg>'

def author_html(s):
    return esc(s).replace('Jiakai Tang','<strong>Jiakai Tang</strong>').replace('†','<sup>†</sup>').replace('*','<sup>*</sup>')

rows=[]
last_year=None
for p in papers:
    if p['year']!=last_year:
        if last_year is not None: rows.append('</ul></div>')
        rows.append(f'<div class="publication-year"><h3 class="year-heading"><span>{p["year"]}</span></h3><ul class="publications-list">')
        last_year=p['year']
    title=esc(p['title'])
    if p['link']: title=f'<a href="{esc(p["link"],quote=True)}">{title}</a>'
    badges=[]
    if 'CCF-A' in p['badge']: badges.append('<span class="badge ccf-a">CCF-A</span>')
    elif 'CCF-B' in p['badge']: badges.append('<span class="badge ccf-b">CCF-B</span>')
    if p['award']: badges.append(f'<span class="badge award">🏆 {esc(p["award"])}</span>')
    if 'Oral' in p['badge']: badges.append('<span class="badge oral">🌟 Oral</span>')
    if 'Under review' in p['badge']: badges.append('<span class="badge status">Under review</span>')
    elif 'Preprint' in p['badge']: badges.append('<span class="badge status">Preprint</span>')
    year=p['year']
    rows.append(f'''<li class="publication" data-year="{year}" data-first="{str(p['first']).lower()}">
      <h4>{title}</h4>
      <p class="authors">{author_html(p['authors'])}</p>
      <p class="paper-meta"><span class="badge venue">{esc(p['venue'])}</span>{''.join(badges)}{f'<a class="paper-link" href="{esc(p["link"],quote=True)}">[Paper]</a>' if p['link'] else ''}</p>
    </li>''')
rows.append('</ul></div>')

nav=[('about','About Me'),('news','News'),('publications','Publications'),('honors','Honors and Awards'),('education','Education'),('service','Academic Services'),('experience','Internships')]
navhtml=''.join(f'<a href="#{k}">{v}</a>' for k,v in nav)
structured={"@context":"https://schema.org","@type":"Person","name":"Jiakai Tang","alternateName":"唐嘉凯","url":"https://tangjiakai.github.io/","image":"https://tangjiakai.github.io/assets/portrait.jpg","affiliation":{"@type":"CollegeOrUniversity","name":"Renmin University of China"},"sameAs":["https://github.com/TangJiakai","https://scholar.google.com/citations?user=7kB-4sEAAAAJ"],"knowsAbout":["Recommender Systems","Large Language Models","Intelligent Agents"]}
html=f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Jiakai Tang · 唐嘉凯</title>
  <meta name="description" content="Jiakai Tang is a Ph.D. student at Renmin University of China. Research on recommender systems, reasoning with large language models, and intelligent agents.">
  <meta name="theme-color" content="#ffffff">
  <link rel="canonical" href="https://tangjiakai.github.io/">
  <meta property="og:type" content="profile">
  <meta property="og:title" content="Jiakai Tang · 唐嘉凯">
  <meta property="og:description" content="Recommender systems, large language models, and intelligent agents. Ph.D. student at Renmin University of China.">
  <meta property="og:url" content="https://tangjiakai.github.io/">
  <meta property="og:image" content="https://tangjiakai.github.io/assets/portrait.jpg">
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="assets/style.css">
  <script type="application/ld+json">{json.dumps(structured,ensure_ascii=False)}</script>
  <script src="assets/site.js" defer></script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="masthead"><div class="nav-wrap">
  <a class="brand" href="#about">Homepage</a>
  <nav aria-label="Main navigation">{navhtml}</nav>
</div></header>
<div class="page-layout">
  <aside class="profile" aria-label="Profile">
    <img class="portrait" src="assets/portrait.jpg" width="413" height="591" alt="Portrait of Jiakai Tang">
    <h1>Jiakai Tang <span lang="zh-CN">唐嘉凯</span></h1>
    <p class="affiliation">Ph.D. student at Gaoling School of Artificial Intelligence, Renmin University of China.</p>
    <p class="profile-interests">Recommender Systems,<br>Large Language Models,<br>and Intelligent Agents.</p>
    <ul class="contact-links">
      <li><span class="contact-row">{icon('pin')}<span>Beijing, China</span></span></li>
      <li><a class="contact-row" href="mailto:tangjiakai5704@ruc.edu.cn">{icon('mail')}<span>Email</span></a></li>
      <li><a class="contact-row" href="https://github.com/TangJiakai">{icon('github')}<span>GitHub</span></a></li>
      <li><a class="contact-row" href="https://scholar.google.com/citations?user=7kB-4sEAAAAJ">{icon('scholar')}<span>Google Scholar</span></a></li>
    </ul>
  </aside>
  <main id="main">
    <section id="about" aria-labelledby="about-title">
      <h2 id="about-title" class="sr-only">About Me</h2>
      <p>I am a Ph.D. student in the <a href="https://ai.ruc.edu.cn/">Gaoling School of Artificial Intelligence</a> at <a href="https://www.ruc.edu.cn/">Renmin University of China</a>, advised by <a href="https://ai.ruc.edu.cn/szdw/zrjs/cx/index.htm">Prof. Xu Chen</a>. I joined the integrated master's–Ph.D. program in 2022 and expect to graduate in 2028. Previously, I received my bachelor's degree in Computer Science and Technology from Wuhan University of Technology in 2022.</p>
      <p>My research focuses on <strong>LLM-powered recommender systems and intelligent agents</strong>. I study reasoning for recommendation, user intent understanding, and interactive agents with long-term memory. I am also interested in faithful user simulation and evaluation, connecting algorithmic advances with real-world applications.</p>
      <p>I have worked on industrial recommendation at Taobao through the <a href="https://dl.acm.org/doi/10.1145/3846382">RecGPT</a> series, and on reasoning for industrial ranking through <a href="https://dl.acm.org/doi/10.1145/3770855.3818456">OnePiece</a>. My recent interests include adaptive computation, recommendation scaling, and agents that learn from experience.</p>
      <p class="scholar-stats"><a href="{scholar['source_url']}">Google Scholar</a>: <strong>{scholar['citations']:,}</strong> citations · h-index <strong>{scholar['h_index']}</strong> · i10-index <strong>{scholar['i10_index']}</strong><span class="metrics-date">Updated {scholar_date}</span></p>
    </section>
    <section id="news" aria-labelledby="news-title">
      <h2 id="news-title"><span aria-hidden="true">🔥</span> News</h2>
      <ul class="news-list">
        <li><time datetime="2026-10">2026.10</time><span>Released <a href="https://arxiv.org/abs/2610.30932">UserArena</a> (<strong>co-first author</strong>), a benchmark for interactive user simulation with long-horizon shopping agents.</span></li>
        <li><time datetime="2026-10">2026.10</time><span>Released <a href="https://arxiv.org/abs/2610.30128">LoopRec</a> (<strong>co-first author</strong>), exploring item-level adaptive recursion for sequential recommendation.</span></li>
        <li><time datetime="2026-08">2026.08</time><span>Released <a href="https://arxiv.org/abs/2608.20707">RecVerse</a> (<strong>first author</strong>), a GUI-grounded shopping simulation agent with hierarchical memory and trajectory-level reinforcement learning.</span></li>
        <li><time datetime="2026-08">2026.08</time><span><a href="https://dl.acm.org/doi/10.1145/3770855.3818456">OnePiece</a> (<strong>co-first author</strong>) was published at <strong>KDD 2026</strong> with an <span class="oral-text">🌟 Oral presentation</span>. RecBot and OneRank were also published at KDD 2026.</span></li>
        <li><time>2026</time><span><strong>RecGPT-V3</strong> received the <span class="award-text">🏆 SIGIR-AP GRIT Workshop Best Paper</span> award.</span></li>
        <li><time>2026</time><span><strong>RecGPT</strong> and <strong>ReaRec</strong> were accepted by <strong>ACM TOIS</strong> and <strong>IEEE TKDE</strong>, respectively.</span></li>
        <li><time>2026</time><span>Received my fourth <strong>National Scholarship</strong>, following awards in 2019, 2020, and 2021.</span></li>
      </ul>
    </section>
    <section id="publications" aria-labelledby="publications-title">
      <h2 id="publications-title"><span aria-hidden="true">📝</span> Publications</h2>
      <p class="section-note">Journal and conference papers, preprints, and workshop contributions.<br><sup>†</sup> Equal contribution. <sup>*</sup> Corresponding author.</p>
      {''.join(rows)}
    </section>
    <section id="honors" aria-labelledby="honors-title">
      <h2 id="honors-title"><span aria-hidden="true">🎖️</span> Honors and Awards</h2>
      <ul class="dated-list honors-list">{''.join(honor_rows)}</ul>
    </section>
    <section id="education" aria-labelledby="education-title">
      <h2 id="education-title"><span aria-hidden="true">📖</span> Education</h2>
      <ul class="dated-list">
        <li><span class="date">2022–Present</span><div><h3>Renmin University of China</h3><p>Integrated Master's–Ph.D. Program in Artificial Intelligence<br>Gaoling School of Artificial Intelligence · Advisor: Xu Chen<br><span class="muted">Expected graduation: 2028</span></p></div></li>
        <li><span class="date">2018–2022</span><div><h3>Wuhan University of Technology</h3><p>Bachelor's Degree in Computer Science and Technology<br><span class="muted">Ranked 1 / 257</span></p></div></li>
      </ul>
    </section>
    <section id="experience" aria-labelledby="experience-title">
      <h2 id="experience-title"><span aria-hidden="true">💻</span> Internships</h2>
      <ul class="dated-list experience-list">
        <li><span class="date">2025.04–Present</span><div><h3>Alibaba · Taotian</h3><p class="position">Recommendation Algorithm Intern · Search &amp; Recommendation Intelligent Products</p><p>RecGPT: intent-centric industrial recommendation, with continued work on RecGPT-V2/V3. RecBot: interactive recommendation through natural-language user commands.</p></div></li>
        <li><span class="date">2024.11–2025.03</span><div><h3>Tencent · WeChat</h3><p class="position">LLM Agent Algorithm Intern</p><p>KAPA: deliberative multi-agent reasoning and a tree-structured knowledge base for multi-domain user intent understanding.</p></div></li>
        <li><span class="date">2024.05–2024.11</span><div><h3>Alibaba · Tongyi</h3><p class="position">LLM Agent Algorithm Intern · Intelligent Computing Lab</p><p>GenSim: a general social simulation platform with large language model agents, supporting large-scale simulation, intervention, and interviews.</p></div></li>
        <li><span class="date">2023.10–2024.04</span><div><h3>Kuaishou</h3><p class="position">Recommendation Research Intern · Community Science, Strategy &amp; Algorithms<br><span lang="zh-CN">社区科学线 · 策略算法部</span></p><p>RGCL: decision boundary-aware graph contrastive learning for robust recommendation. Published at KDD 2024.</p></div></li>
        <li><span class="date">2023.02–2023.07</span><div><h3>Huawei · Noah's Ark Lab</h3><p class="position">Recommendation Algorithm Intern</p><p>Multi-interest modeling for browser video retrieval.</p></div></li>
      </ul>
    </section>
    <section id="service" aria-labelledby="service-title">
      <h2 id="service-title"><span aria-hidden="true">📚</span> Academic Services</h2>
      <h3>Reviewing</h3><p><strong>Conferences:</strong> NeurIPS, ICLR, AAAI, IJCAI, KDD, SIGIR, WSDM, ACL, EMNLP, WWW.<br><strong>Journals:</strong> ACM TOIS, IEEE TKDE, ACM TORS.</p>
      <h3>Organization</h3><p>Core organizer of the Human-Centered Recommender Systems (HCRS) Workshop at WWW 2026 and 2027.</p>
      <h3>Open Source</h3><p>Contributor to the <strong>RecBole</strong> recommendation framework and lead developer of <strong>RecBole-FairRec</strong>. Contributed to core functionality and evaluation in <strong>RecAgent</strong>.</p>
    </section>
    <footer><span>© 2026 Jiakai Tang · Last updated October 23, 2026</span><a href="#about">Back to top ↑</a></footer>
  </main>
</div>
</body>
</html>
'''
# Keep the body order consistent with the reference-style navigation.
service=re.search(r'    <section id="service".*?</section>',html,re.S).group(0)
html=html.replace(service,'').replace('    <section id="experience"',service+'\n    <section id="experience"')
(ROOT/'index.html').write_text(html)
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://tangjiakai.github.io/</loc><lastmod>2026-10-23</lastmod></url></urlset>\n')
print(f'Built index.html: {len(papers)} publications, {sum(p["first"] for p in papers)} first/co-first-author papers.')
