(() => {
  const controls = document.querySelector('.publication-controls');
  const papers = [...document.querySelectorAll('.publication')];
  const input = document.querySelector('#paper-search');
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const status = document.querySelector('#search-status');
  let filter = 'all';
  function update() {
    const query = input.value.trim().toLocaleLowerCase();
    let count = 0;
    papers.forEach(paper => {
      const matches = (filter === 'all' || paper.dataset.first === 'true') && paper.textContent.toLocaleLowerCase().includes(query);
      paper.hidden = !matches;
      count += Number(matches);
    });
    status.textContent = `${count} publications shown`;
    document.querySelector('#no-results').hidden = count > 0;
  }
  buttons.forEach(button => button.addEventListener('click', () => {
    filter = button.dataset.filter;
    buttons.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    update();
  }));
  input.addEventListener('input', update);
  controls.hidden = false;
  update();
  const links = [...document.querySelectorAll('nav a')];
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
})();
