(() => {
  // Preserve links shared before publications and patents moved to their own pages.
  if (document.querySelector('#about') && ['#publications', '#patents'].includes(location.hash)) {
    location.replace(location.hash.slice(1) + '.html');
    return;
  }
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
})();
