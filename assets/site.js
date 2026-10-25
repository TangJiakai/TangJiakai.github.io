(() => {
  // Preserve links shared before publications and patents moved to their own pages.
  if (document.querySelector('#about') && ['#publications', '#patents'].includes(location.hash)) {
    location.replace(location.hash.slice(1) + '.html');
    return;
  }
  // Header theme switch: light by default, and the visitor's choice is remembered.
  const themeToggle = document.querySelector('.theme-toggle');
  const themeColor = document.querySelector('meta[name="theme-color"]');
  const setTheme = (theme, remember) => {
    document.documentElement.dataset.theme = theme;
    if (themeColor) themeColor.content = theme === 'dark' ? '#16191d' : '#ffffff';
    if (themeToggle) themeToggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    if (remember) { try { localStorage.setItem('theme', theme); } catch {} }
  };
  setTheme(document.documentElement.dataset.theme || 'light', false);
  if (themeToggle) themeToggle.addEventListener('click', () => setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark', true));
  const sectionNav = document.querySelector('.section-nav');
  const links = [...document.querySelectorAll('.section-nav a')];
  const targets = links.map(link => document.getElementById(link.hash.slice(1)));
  const floatingNav = document.querySelector('.floating-nav');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let offset = 90;
  let scheduled = false;
  const measureNavigation = () => {
    const headerHeight = document.querySelector('.masthead').getBoundingClientRect().height;
    document.documentElement.style.setProperty('--masthead-height', `${headerHeight}px`);
    offset = headerHeight + (floatingNav ? floatingNav.getBoundingClientRect().height + 30 : 30);
    document.documentElement.style.setProperty('--section-offset', `${offset}px`);
  };
  const updateNavigation = () => {
    scheduled = false;
    if (!links.length) return;
    let selected = 0;
    targets.forEach((target, index) => {
      if (target && !target.closest('details:not([open])') && target.getClientRects().length && target.getBoundingClientRect().top <= offset + (parseFloat(getComputedStyle(target).scrollMarginTop) || 0) + 3) selected = index;
    });
    if (window.scrollY > 0 && window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4) {
      targets.forEach((target, index) => { if (target && !target.closest('details:not([open])') && target.getClientRects().length) selected = index; });
    }
    links.forEach((link, index) => {
      const active = index === selected;
      const changed = active && !link.classList.contains('active');
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
      if (changed && floatingNav && sectionNav.scrollWidth > sectionNav.clientWidth) {
        const bounds = sectionNav.getBoundingClientRect();
        const item = link.getBoundingClientRect();
        if (item.left < bounds.left || item.right > bounds.right) {
          sectionNav.scrollTo({left: sectionNav.scrollLeft + item.left - bounds.left - (bounds.width - item.width) / 2, behavior: reducedMotion.matches ? 'instant' : 'smooth'});
        }
      }
    });
  };
  const scheduleUpdate = () => {
    if (!scheduled) { scheduled = true; requestAnimationFrame(updateNavigation); }
  };
  measureNavigation();
  updateNavigation();
  window.addEventListener('scroll', scheduleUpdate, {passive: true});
  window.addEventListener('resize', () => { measureNavigation(); scheduleUpdate(); });
  window.addEventListener('load', () => { measureNavigation(); scheduleUpdate(); });
  window.addEventListener('hashchange', scheduleUpdate);
  // Life stays folded until requested, including direct links to a life album.
  const openLifeAlbum = hash => {
    const target = document.getElementById(hash.slice(1));
    const disclosure = target && target.closest('.gallery-life');
    if (disclosure && !disclosure.open) {
      disclosure.open = true;
      requestAnimationFrame(() => requestAnimationFrame(() => {
        target.scrollIntoView({block:'start', behavior:'instant'});
        scheduleUpdate();
      }));
    }
  };
  document.querySelectorAll('.gallery-nav a').forEach(link => {
    link.addEventListener('click', event => {
      if (!event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey) openLifeAlbum(link.hash);
    });
  });
  window.addEventListener('hashchange', () => openLifeAlbum(location.hash));
  document.querySelectorAll('.gallery-life').forEach(details => details.addEventListener('toggle', scheduleUpdate));
  openLifeAlbum(location.hash);
  // Keep full photo proportions and pack unequal card heights into compact rows.
  // Without ResizeObserver, the regular responsive grid remains usable.
  if (typeof ResizeObserver === 'function') {
    document.querySelectorAll('.gallery-grid').forEach(grid => {
      const cards = [...grid.querySelectorAll('.gallery-photo')];
      const layout = () => {
        if (!grid.getClientRects().length) return;
        const gap = parseFloat(getComputedStyle(grid).getPropertyValue('--photo-gap')) || 0;
        const spans = cards.map(card => Math.ceil(card.getBoundingClientRect().height + gap));
        cards.forEach((card, index) => { card.style.gridRowEnd = `span ${spans[index]}`; });
      };
      grid.classList.add('gallery-grid--masonry');
      layout();
      const observer = new ResizeObserver(layout);
      cards.forEach(card => observer.observe(card));
    });
  }
  const viewer = document.querySelector('.photo-viewer');
  if (viewer && typeof viewer.showModal === 'function') {
    let trigger;
    document.querySelectorAll('.gallery-image').forEach(link => {
      link.addEventListener('click', event => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        trigger = link;
        viewer.querySelector('img').src = link.href;
        viewer.querySelector('img').alt = link.querySelector('img').alt;
        viewer.querySelector('figcaption').textContent = link.dataset.caption;
        viewer.showModal();
      });
    });
    viewer.querySelector('.photo-close').addEventListener('click', () => viewer.close());
    viewer.addEventListener('click', event => { if (event.target === viewer) viewer.close(); });
    viewer.addEventListener('close', () => { if (trigger) trigger.focus(); });
  }
  // Fade sections in once as they enter the viewport.
  if ('IntersectionObserver' in window && !reducedMotion.matches) {
    const revealer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('is-visible'); revealer.unobserve(entry.target); }
    }), {rootMargin: '0px 0px -8% 0px'});
    document.querySelectorAll('.home-section, .gallery-album').forEach(element => {
      element.classList.add('reveal');
      revealer.observe(element);
    });
  }
  // Copy a generated BibTeX entry for each publication.
  document.querySelectorAll('.bibtex-button').forEach(button => {
    if (!navigator.clipboard) return;
    button.hidden = false;
    const label = button.querySelector('span');
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(button.dataset.bibtex);
        button.classList.add('copied');
        label.textContent = 'Copied';
      } catch {
        label.textContent = 'Copy failed';
      }
      setTimeout(() => { button.classList.remove('copied'); label.textContent = 'BibTeX'; }, 1600);
    });
  });
  // Publication search over titles, authors, venues, abstracts and topic keywords
  // (English and Chinese). Results are ranked by relevance, with the matching
  // abstract sentence shown under each paper.
  const tools = document.querySelector('.pub-tools');
  if (tools) {
    const input = tools.querySelector('input');
    const buttons = [...tools.querySelectorAll('[data-filter]')];
    const count = tools.querySelector('.pub-count');
    const papers = [...document.querySelectorAll('.publication')];
    const years = [...document.querySelectorAll('.publication-year')];
    const titles = new Map(papers.map(paper => [paper, paper.querySelector('h4').innerHTML]));
    const homes = new Map(papers.map(paper => [paper, paper.parentElement]));
    const results = document.createElement('ol');
    results.className = 'publications-list search-results';
    results.hidden = true;
    years[0].before(results);
    const empty = document.createElement('p');
    empty.className = 'pub-empty';
    empty.hidden = true;
    empty.textContent = 'No publications match this search.';
    results.after(empty);
    const related = [
      ['llm', 'large language model', 'language model', 'gpt', '大模型', '大语言模型'],
      ['agent', 'agents', 'agentic', '智能体'],
      ['reasoning', 'reason', 'think', 'thinking', '推理'],
      ['ctr', 'click-through', '点击率'],
      ['ranking', 'rank', 'ranker', '排序'],
      ['sequential', 'sequence', 'seqrec', '序列'],
      ['simulation', 'simulator', 'simulate', '模拟', '仿真'],
      ['explainable', 'explanation', 'explanations', '可解释', '解释'],
      ['robust', 'robustness', 'adversarial', '鲁棒'],
      ['fair', 'fairness', 'bias', 'debias', '公平'],
      ['industrial', 'deployed', 'deployment', 'production', 'online', '工业', '落地', '部署'],
      ['rl', 'reinforcement learning', 'policy optimization', '强化学习'],
      ['conversational', 'multi-turn', 'interactive', 'dialogue', '对话', '交互'],
      ['memory', 'memories', '记忆'],
      ['efficient', 'efficiency', 'latency', 'compute', 'faster', 'speed', '效率', '高效', '加速'],
      ['cost', 'cheaper', 'cheap', 'saving', 'resource consumption', 'gpu', '成本', '省钱', '降本', '资源'],
      ['recommendation', 'recommender', 'recsys', '推荐'],
      ['survey', 'review', '综述'],
      ['benchmark', 'dataset', '基准', '数据集'],
    ];
    const isCJK = text => /[㐀-鿿]/.test(text);
    const expand = word => {
      const terms = new Set([word]);
      related.forEach(group => {
        if (group.some(term => term === word || (!isCJK(word) && word.length > 3 && term.startsWith(word)) || (isCJK(word) && term.includes(word)))) group.forEach(term => terms.add(term));
      });
      return [...terms];
    };
    const escapeRegExp = text => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    // Short Latin terms match whole words; longer ones also match word prefixes ("simulat" finds "simulation").
    const termSource = term => isCJK(term) ? escapeRegExp(term) : term.length <= 3 ? `\\b${escapeRegExp(term)}\\b` : `\\b${escapeRegExp(term)}`;
    const counter = term => new RegExp(termSource(term), 'gi');
    let index = new Map(papers.map(paper => [paper, {title: paper.querySelector('h4').textContent.toLowerCase(), meta: paper.dataset.search, abstract: '', topics: ''}]));
    let loaded = false;
    const loadIndex = async () => {
      if (loaded || !tools.dataset.index) return;
      loaded = true;
      try {
        const entries = await (await fetch(tools.dataset.index)).json();
        papers.forEach(paper => {
          const entry = entries[paper.id];
          if (entry) Object.assign(index.get(paper), {abstract: entry.abstract || '', abstractLower: (entry.abstract || '').toLowerCase(), topics: (entry.topics || '').toLowerCase()});
        });
        apply();
      } catch {
        loaded = false;
      }
    };
    // Semantic search: the Worker embeds the query with bge-m3, and papers are compared
    // with precomputed vectors. Keyword results show first; meaning-based ranking follows.
    const semanticEndpoint = tools.dataset.semanticEndpoint;
    const queryVectors = new Map();
    let paperVectors = null;
    let semanticTimer = 0;
    let semanticKey = '';
    let semanticFailed = false;
    let semanticMean = null;
    const normalize = vector => {
      let norm = 0;
      for (let position = 0; position < vector.length; position += 1) norm += vector[position] ** 2;
      norm = Math.sqrt(norm) || 1;
      for (let position = 0; position < vector.length; position += 1) vector[position] /= norm;
      return vector;
    };
    // Every paper is about recommendation, so all vectors share one strong direction.
    // Subtracting the corpus mean (from passages and queries alike) leaves what sets each passage apart.
    const center = vector => {
      const centered = new Float32Array(vector.length);
      for (let position = 0; position < vector.length; position += 1) centered[position] = vector[position] - semanticMean[position];
      return normalize(centered);
    };
    const loadVectors = async () => {
      if (paperVectors || !semanticEndpoint) return paperVectors;
      const [manifest, buffer] = await Promise.all([
        fetch(tools.dataset.semanticPassages).then(response => response.json()),
        fetch(tools.dataset.semanticVectors).then(response => response.arrayBuffer()),
      ]);
      const bytes = new Int8Array(buffer);
      const raw = manifest.passages.map((_, row) => normalize(Float32Array.from(bytes.subarray(row * manifest.dims, (row + 1) * manifest.dims))));
      semanticMean = new Float32Array(manifest.dims);
      raw.forEach(vector => vector.forEach((value, position) => { semanticMean[position] += value / raw.length; }));
      const byId = new Map(papers.map(paper => [paper.id, paper]));
      paperVectors = manifest.passages.map(([id, kind, text], row) => ({paper: byId.get(id), kind, text, vector: center(raw[row])})).filter(passage => passage.paper);
      return paperVectors;
    };
    const requestSemantic = query => {
      clearTimeout(semanticTimer);
      if (!semanticEndpoint || queryVectors.has(query) || query.length < 2) return;
      semanticTimer = setTimeout(async () => {
        try {
          const [response] = await Promise.all([
            fetch(semanticEndpoint, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({texts: [query]}), signal: AbortSignal.timeout(4000)}),
            loadVectors(),
          ]);
          if (!response.ok) throw new Error(`Worker returned ${response.status}`);
          const [vector] = (await response.json()).vectors;
          queryVectors.set(query, center(normalize(Float32Array.from(vector))));
          semanticFailed = false;
        } catch {
          // Without the Worker, search stays keyword-only.
          semanticFailed = true;
        }
        if (semanticKey === query) apply();
      }, 300);
    };
    // A paper's semantic score is its best passage (title, one abstract sentence, or topics).
    const similarities = query => {
      const vector = queryVectors.get(query);
      if (!vector || !paperVectors) return null;
      const result = new Map();
      paperVectors.forEach(passage => {
        let score = 0;
        for (let position = 0; position < vector.length; position += 1) score += vector[position] * passage.vector[position];
        // Short titles resemble any short query, so they count slightly less than abstract sentences.
        if (passage.kind === 'title') score *= 0.9;
        const best = result.get(passage.paper);
        if (!best || score > best.score) result.set(passage.paper, {score, passage});
      });
      return result;
    };
    const weights = {title: 4, topics: 3, meta: 2, abstractLower: 1};
    const fieldScore = (paper, terms) => {
      const fields = index.get(paper);
      let best = 0;
      terms.forEach(term => {
        const pattern = counter(term);
        Object.entries(weights).forEach(([field, weight]) => {
          const hits = (fields[field] || '').match(pattern);
          if (hits) best = Math.max(best, weight * (1 + Math.log(hits.length)) * (terms[0] === term ? 1 : 0.7));
        });
      });
      return best;
    };
    // IDF: a word found in most papers ("recommendation") counts little and does not
    // decide which papers cover the query; rare words carry the ranking.
    const groupStats = groups => groups.map(terms => {
      const found = papers.filter(paper => fieldScore(paper, terms) > 0).length;
      return {terms, idf: Math.log(1 + papers.length / Math.max(found, 1)) / Math.log(1 + papers.length), generic: found > papers.length / 2};
    });
    const score = (paper, stats) => {
      const allGeneric = stats.every(stat => stat.generic);
      let total = 0;
      let matched = 0;
      stats.forEach(({terms, idf, generic}) => {
        const best = fieldScore(paper, terms);
        if (best && (!generic || allGeneric)) matched += 1;
        total += best * idf;
      });
      return {total, matched};
    };
    const snippet = (paper, terms) => {
      const text = index.get(paper).abstract;
      if (!text) return '';
      // Split at sentence ends only, so decimals such as "55.8%" stay inside their sentence.
      const sentences = text.split(/(?<=[.!?])\s+(?=[A-Z(])/);
      let best = '';
      let bestHits = 0;
      sentences.forEach(sentence => {
        const hits = terms.filter(term => counter(term).test(sentence)).length;
        if (hits > bestHits) { best = sentence.trim(); bestHits = hits; }
      });
      return best;
    };
    const markText = (element, terms) => {
      if (!terms.length) return;
      const source = terms.map(termSource).join('|');
      const pattern = new RegExp(`(${source})`, 'gi');
      const tester = new RegExp(source, 'i');
      const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
      const nodes = [];
      while (walker.nextNode()) nodes.push(walker.currentNode);
      nodes.forEach(node => {
        if (!tester.test(node.data)) return;
        const fragment = document.createDocumentFragment();
        node.data.split(pattern).forEach((part, position) => {
          if (position % 2) { const mark = document.createElement('mark'); mark.textContent = part; fragment.append(mark); }
          else if (part) fragment.append(part);
        });
        node.replaceWith(fragment);
      });
    };
    const stopwords = new Set(['a', 'an', 'the', 'of', 'for', 'and', 'or', 'to', 'in', 'on', 'with', 'by', 'via', 'how', 'what', 'which', 'paper', 'papers', 'about', 'using', 'is', 'are', 'can', 'do', 'does', 'make', 'let', 'get', 'want', 'need', 'more', 'less', 'better', 'that', 'this', 'they', 'them', 'their', 'it', '的', '和', '论文', '关于', '让', '更', '怎么', '如何', '一个', '我', '想']);
    // Chinese has no spaces: pick out known words (topic keywords and related terms), longest first.
    const cjkWords = () => {
      const vocabulary = new Set(related.flat().filter(isCJK));
      index.forEach(fields => fields.topics.split(' ').filter(isCJK).forEach(word => vocabulary.add(word)));
      return [...vocabulary].sort((a, b) => b.length - a.length);
    };
    const segment = word => {
      if (!isCJK(word) || word.length <= 2) return [word];
      const found = [];
      let rest = word;
      cjkWords().forEach(term => { if (rest.includes(term)) { found.push(term); rest = rest.split(term).join(' '); } });
      return found.length ? found : [word];
    };
    let filter = 'all';
    const apply = () => {
      const words = input.value.toLowerCase().split(/[\s,，、]+/).flatMap(segment).filter(word => word && !stopwords.has(word));
      const groups = words.map(expand);
      const terms = groups.flat();
      const passesFilter = paper => filter === 'all' || paper.dataset[filter] === 'true';
      papers.forEach(paper => {
        paper.querySelector('h4').innerHTML = titles.get(paper);
        paper.querySelector('.search-snippet')?.remove();
      });
      let shown = 0;
      if (!words.length) {
        // Browse mode: papers return to their year lists, in their original order.
        papers.forEach(paper => {
          homes.get(paper).append(paper);
          paper.hidden = !passesFilter(paper);
          if (!paper.hidden) shown += 1;
        });
        years.forEach(year => {
          year.hidden = !year.querySelector('.publication:not([hidden])');
          const link = document.querySelector(`.year-nav a[href="#${year.id}"]`);
          if (link) link.hidden = year.hidden;
        });
        results.hidden = true;
      } else {
        // Search mode: one list ranked by relevance; papers matching every word come first.
        loadIndex();
        const stats = groupStats(groups);
        const ranked = papers.filter(passesFilter).map(paper => ({paper, ...score(paper, stats)})).filter(item => item.total > 0 && item.matched > 0);
        // Keep the papers that cover the most query words, then rank them by score.
        const coverage = Math.max(0, ...ranked.map(item => item.matched));
        let list = ranked.filter(item => item.matched === coverage).sort((a, b) => b.total - a.total);
        // The model sees the query plus English related terms of its specific words, which
        // helps short, vague queries ("cheaper" also brings "cost", "resource consumption").
        const expansion = stats.filter(stat => !stat.generic).flatMap(stat => stat.terms.slice(1)).filter(term => !isCJK(term));
        const query = [input.value.trim().toLowerCase(), ...new Set(expansion)].slice(0, 9).join(' ');
        semanticKey = query;
        requestSemantic(query);
        const meaning = similarities(query);
        if (meaning) {
          // Blend meaning (relative to the best and worst paper) and keyword score (relative to
          // the strongest keyword match) equally. Papers close in meaning join without shared
          // words: clear matches near the best one, or the closest few when no keyword matched.
          const scores = [...meaning.entries()].filter(([paper]) => passesFilter(paper));
          const best = Math.max(...scores.map(([, value]) => value.score));
          const worst = Math.min(...scores.map(([, value]) => value.score));
          const spread = best - worst || 1;
          const topKeyword = Math.max(0, ...list.map(item => item.total)) || 1;
          const keywordScores = new Map(list.map(item => [item.paper, item.total / topKeyword]));
          const floor = list.length ? 0.28 : -1;
          const related = scores.filter(([paper, value]) => !keywordScores.has(paper) && value.score >= best - (list.length ? 0.08 : 0.05) && value.score >= floor).sort((a, b) => b[1].score - a[1].score).slice(0, list.length ? 6 : 5);
          list = list.map(item => item.paper).concat(related.map(([paper]) => paper)).map(paper => ({
            paper,
            related: !keywordScores.has(paper),
            passage: meaning.get(paper)?.passage,
            close: (meaning.get(paper)?.score ?? -1) >= best - 0.1,
            blended: 0.5 * ((meaning.get(paper)?.score ?? worst) - worst) / spread + 0.5 * (keywordScores.get(paper) || 0),
          })).sort((a, b) => b.blended - a.blended);
        }
        papers.forEach(paper => { paper.hidden = true; });
        list.forEach(({paper}) => {
          paper.hidden = false;
          results.append(paper);
          const highlight = stats.some(stat => !stat.generic) ? stats.filter(stat => !stat.generic).flatMap(stat => stat.terms) : terms;
          markText(paper.querySelector('h4'), highlight);
          const item = list.find(entry => entry.paper === paper);
          // Prefer the sentence with the query words; otherwise the sentence that matched by meaning.
          // Prefer the abstract sentence closest in meaning when the paper is a strong semantic
          // match; otherwise the sentence with the query's specific (not generic) words.
          const specific = stats.filter(stat => !stat.generic).flatMap(stat => stat.terms);
          const byMeaning = item.passage?.kind === 'abstract' && item.close;
          const sentence = byMeaning ? item.passage.text : (specific.length ? snippet(paper, specific) : '') || (item.passage?.kind === 'abstract' ? item.passage.text : '') || snippet(paper, terms);
          paper.querySelector('.related-tag')?.remove();
          if (item.related) {
            const tag = document.createElement('span');
            tag.className = 'related-tag';
            tag.textContent = 'Related by meaning';
            paper.querySelector('h4').append(tag);
          }
          if (sentence) {
            const line = document.createElement('p');
            line.className = 'search-snippet';
            line.textContent = sentence;
            markText(line, highlight);
            if (byMeaning) {
              const label = document.createElement('span');
              label.className = 'snippet-label';
              label.textContent = 'Closest in meaning';
              line.prepend(label);
            }
            paper.querySelector('.authors').after(line);
          }
        });
        shown = list.length;
        years.forEach(year => { year.hidden = true; });
        document.querySelectorAll('.year-nav a').forEach(link => { link.hidden = true; });
        results.hidden = false;
      }
      empty.hidden = shown > 0;
      const semantic = words.length && similarities(semanticKey);
      const found = `${shown} ${shown === 1 ? 'result' : 'results'}`;
      const status = !semanticEndpoint ? `${found}, ranked by keyword relevance` : semantic ? `✨ ${found}, ranked by meaning and keywords` : semanticFailed ? `${found} by keywords (semantic search unavailable)` : `${found} by keywords, understanding your query…`;
      count.textContent = !words.length && shown === papers.length ? `${papers.length} publications` : words.length ? status : `Showing ${shown} of ${papers.length} publications`;
      count.classList.toggle('is-semantic', Boolean(semantic));
      document.querySelector('.year-nav')?.toggleAttribute('hidden', words.length > 0);
      scheduleUpdate();
    };
    buttons.forEach(button => button.addEventListener('click', () => {
      filter = button.dataset.filter;
      buttons.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
      apply();
    }));
    input.addEventListener('input', apply);
    input.addEventListener('focus', loadIndex, {once: true});
    const examples = tools.querySelector('.pub-examples');
    if (examples && semanticEndpoint) {
      examples.hidden = false;
      examples.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
        input.value = button.textContent;
        loadIndex();
        apply();
        input.focus();
      }));
    }
    document.addEventListener('keydown', event => {
      if (event.key === '/' && document.activeElement !== input && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) { event.preventDefault(); input.focus(); }
      if (event.key === 'Escape' && document.activeElement === input) { input.value = ''; apply(); }
    });
    const query = new URLSearchParams(location.search).get('q');
    if (query) { input.value = query; loadIndex(); }
    tools.hidden = false;
    measureNavigation();
    apply();
  }
})();
