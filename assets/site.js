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
      if (target && target.getBoundingClientRect().top <= offset + (parseFloat(getComputedStyle(target).scrollMarginTop) || 0) + 3) selected = index;
    });
    if (window.scrollY > 0 && window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4) selected = links.length - 1;
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
  // Keep full photo proportions and pack unequal card heights into compact rows.
  // Without ResizeObserver, the regular responsive grid remains usable.
  if (typeof ResizeObserver === 'function') {
    document.querySelectorAll('.gallery-grid').forEach(grid => {
      const cards = [...grid.querySelectorAll('.gallery-photo')];
      const layout = () => {
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
  // Publication search: every query word must match, directly or through a related term.
  const tools = document.querySelector('.pub-tools');
  if (tools) {
    const input = tools.querySelector('input');
    const buttons = [...tools.querySelectorAll('[data-filter]')];
    const count = tools.querySelector('.pub-count');
    const papers = [...document.querySelectorAll('.publication')];
    const years = [...document.querySelectorAll('.publication-year')];
    const titles = new Map(papers.map(paper => [paper, paper.querySelector('h4').innerHTML]));
    const empty = document.createElement('p');
    empty.className = 'pub-empty';
    empty.hidden = true;
    empty.textContent = 'No publications match this search.';
    years[years.length - 1].after(empty);
    const related = [
      ['llm', 'large language model', 'language model', 'gpt'],
      ['agent', 'agents', 'agentic', 'simulation', 'simulator'],
      ['reasoning', 'reason', 'think', 'latent', 'deliberative'],
      ['ctr', 'click-through', 'ranking', 'rank'],
      ['sequential', 'sequence', 'seq'],
      ['user simulation', 'simulation', 'simulate', 'behavior'],
      ['explainable', 'explanation', 'explanations'],
      ['robust', 'robustness', 'adversarial', 'noise'],
      ['fair', 'fairness', 'bias', 'debiased'],
      ['industrial', 'deployed', 'taobao', 'production'],
      ['rl', 'reinforcement learning', 'policy', 'preference optimization'],
      ['conversational', 'multi-turn', 'interactive', 'dialogue'],
      ['benchmark', 'library', 'toolkit', 'recbole'],
      ['recsys', 'recommendation', 'recommender'],
    ];
    const expand = word => {
      const terms = new Set([word]);
      related.forEach(group => { if (group.some(term => term === word || (word.length > 2 && term.startsWith(word)))) group.forEach(term => terms.add(term)); });
      return [...terms];
    };
    let filter = 'all';
    const escapeRegExp = text => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    // Short terms such as "rl" or "llm" only match whole words.
    const termSource = term => term.length <= 3 ? `\\b${escapeRegExp(term)}\\b` : escapeRegExp(term);
    const matches = (text, term) => term.length <= 3 ? new RegExp(termSource(term)).test(text) : text.includes(term);
    const highlight = (paper, words) => {
      const heading = paper.querySelector('h4');
      heading.innerHTML = titles.get(paper);
      if (!words.length) return;
      const source = words.map(termSource).join('|');
      const pattern = new RegExp(`(${source})`, 'gi');
      const tester = new RegExp(source, 'i');
      const walker = document.createTreeWalker(heading, NodeFilter.SHOW_TEXT);
      const nodes = [];
      while (walker.nextNode()) nodes.push(walker.currentNode);
      nodes.forEach(node => {
        if (!tester.test(node.data)) return;
        const fragment = document.createDocumentFragment();
        node.data.split(pattern).forEach((part, index) => {
          if (index % 2) { const mark = document.createElement('mark'); mark.textContent = part; fragment.append(mark); }
          else if (part) fragment.append(part);
        });
        node.replaceWith(fragment);
      });
    };
    const apply = () => {
      const words = input.value.toLowerCase().split(/\s+/).filter(Boolean);
      const groups = words.map(expand);
      let shown = 0;
      papers.forEach(paper => {
        const text = paper.dataset.search;
        const passes = (filter === 'all' || paper.dataset[filter] === 'true') && groups.every(terms => terms.some(term => matches(text, term)));
        paper.hidden = !passes;
        if (passes) shown += 1;
        highlight(paper, passes ? groups.flat() : []);
      });
      years.forEach(year => {
        year.hidden = !year.querySelector('.publication:not([hidden])');
        const link = document.querySelector(`.year-nav a[href="#${year.id}"]`);
        if (link) link.hidden = year.hidden;
      });
      empty.hidden = shown > 0;
      count.textContent = shown === papers.length ? `${papers.length} publications` : `Showing ${shown} of ${papers.length} publications`;
      scheduleUpdate();
    };
    buttons.forEach(button => button.addEventListener('click', () => {
      filter = button.dataset.filter;
      buttons.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
      apply();
    }));
    input.addEventListener('input', apply);
    document.addEventListener('keydown', event => {
      if (event.key === '/' && document.activeElement !== input && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) { event.preventDefault(); input.focus(); }
      if (event.key === 'Escape' && document.activeElement === input) { input.value = ''; apply(); }
    });
    const query = new URLSearchParams(location.search).get('q');
    if (query) input.value = query;
    tools.hidden = false;
    measureNavigation();
    apply();
  }
})();
