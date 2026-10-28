(() => {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  const input = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  const status = document.getElementById('search-status');
  if (!input || !results || !status) return;

  let index = [];
  const params = new URLSearchParams(location.search);
  input.value = params.get('q') || '';
  fetch('/search-index.json')
    .then(response => {
      if (!response.ok) throw new Error('搜索索引加载失败');
      return response.json();
    })
    .then(data => { index = data; render(); })
    .catch(() => { status.textContent = '搜索暂时无法使用，请从归档浏览文章。'; });

  input.addEventListener('input', () => {
    const q = input.value.trim();
    const url = new URL(location.href);
    if (q) url.searchParams.set('q', q);
    else url.searchParams.delete('q');
    history.replaceState(null, '', url);
    render();
  });

  function render() {
    results.replaceChildren();
    const query = input.value.trim().toLocaleLowerCase();
    if (!query) { status.textContent = '输入关键词开始搜索'; return; }
    const terms = query.split(/\s+/).filter(Boolean);
    const scored = index.map(post => {
      const title = post.title.toLocaleLowerCase();
      const tags = post.tags.join(' ').toLocaleLowerCase();
      const summary = post.summary.toLocaleLowerCase();
      const body = post.plain.toLocaleLowerCase();
      const haystack = [title, tags, summary, body, post.category.toLocaleLowerCase()].join(' ');
      if (!terms.every(term => haystack.includes(term))) return null;
      const score = terms.reduce((value, term) => value + (title.includes(term) ? 8 : 0) + (tags.includes(term) ? 4 : 0) + (summary.includes(term) ? 2 : 0), 0);
      return { post, score };
    }).filter(Boolean).sort((a, b) => b.score - a.score || b.post.date.localeCompare(a.post.date));
    status.textContent = `找到 ${scored.length} 篇文章`;
    for (const { post } of scored.slice(0, 50)) {
      const link = document.createElement('a');
      link.className = 'search-result';
      link.href = post.url;
      const meta = document.createElement('small');
      meta.textContent = `${post.date} · ${post.category}`;
      const title = document.createElement('strong');
      title.textContent = post.title;
      const excerpt = document.createElement('p');
      const lower = post.plain.toLocaleLowerCase();
      const at = lower.indexOf(terms[0]);
      const start = Math.max(0, at - 45);
      excerpt.textContent = post.plain.slice(start, start + 135) + (post.plain.length > start + 135 ? '…' : '');
      link.append(meta, title, excerpt);
      results.append(link);
    }
  }
})();
