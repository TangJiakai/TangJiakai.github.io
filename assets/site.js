(() => {
  // Preserve links shared before publications and patents moved to their own pages.
  if (document.querySelector('#about') && ['#publications', '#patents'].includes(location.hash)) {
    location.replace(location.hash.slice(1) + '.html');
    return;
  }
  const links = [...document.querySelectorAll('.section-nav a')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) links.forEach(link => {
          const active = link.hash === '#' + entry.target.id;
          link.classList.toggle('active', active);
          if (active) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      });
    }, {rootMargin: '-15% 0px -65% 0px'});
    document.querySelectorAll('main section').forEach(section => observer.observe(section));
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
