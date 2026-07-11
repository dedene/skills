const q = __QUERY_JSON__;
const p = await openTab('https://www.tiktok.com/search?q=' + encodeURIComponent(q));
await p.waitForLoadState('load');
await new Promise(r => setTimeout(r, 8000));
const login = await p.evaluate(`(() => {
  return !!document.querySelector('#loginContainer, [data-e2e="login-modal"]') && !document.querySelector('[data-e2e="search_top-item"]');
})()`);
if (login) {
  console.log('<<<JSON_START>>>');
  console.log(JSON.stringify({ login_required: true, source: 'tiktok', items: [] }));
  console.log('<<<JSON_END>>>');
  await closeTab(p);
} else {
await p.waitForSelector('[data-e2e="search_top-item"]', { timeout: 20000 });
for (let i = 0; i < __SCROLLS__; i++) { await p.evaluate('window.scrollBy(0, 2500)'); await new Promise(r => setTimeout(r, 1800)); }
const payload = await p.evaluate(`(() => {
  const items = [];
  for (const card of document.querySelectorAll('[data-e2e="search_top-item"]')) {
    // walk up while the ancestor still wraps only THIS card
    let scope = card;
    let up = card.parentElement;
    while (up && up.querySelectorAll('[data-e2e="search_top-item"]').length === 1) { scope = up; up = up.parentElement; }
    const link = scope.querySelector('a[href*="/video/"]');
    const desc = scope.querySelector('[data-e2e="search-card-video-caption"]');
    const userLink = scope.querySelector('[data-e2e="search-card-user-link"]');
    const uid = scope.querySelector('[data-e2e="search-card-user-unique-id"]');
    const views = scope.querySelector('[data-e2e="video-views"]');
    items.push({
      url: link ? link.getAttribute('href') : null,
      caption: desc ? desc.innerText : null,
      author_href: userLink ? userLink.getAttribute('href') : null,
      author_handle: uid ? uid.innerText.trim() : null,
      views: views ? views.innerText.trim() : null,
      scope_text: (scope.innerText || '').slice(0, 320),
    });
  }
  return { query: ${JSON.stringify(__QUERY_JSON__)}, count: items.length, items };
})()`);
console.log('<<<JSON_START>>>');
console.log(JSON.stringify(payload));
console.log('<<<JSON_END>>>');
await closeTab(p);
}
