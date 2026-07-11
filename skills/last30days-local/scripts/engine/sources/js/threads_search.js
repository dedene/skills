const q = __QUERY_JSON__;
const p = await openTab('https://www.threads.com/search?q=' + encodeURIComponent(q) + '&filter=recent');
await p.waitForLoadState('load');
await new Promise(r => setTimeout(r, 7000));
const login = await p.evaluate(`(() => {
  return /\\/login/.test(location.pathname) || !!document.querySelector('a[href*="/login"] , div[role="button"][tabindex="0"] a[href="/login/"]');
})()`);
if (login) {
  console.log('<<<JSON_START>>>');
  console.log(JSON.stringify({ login_required: true, source: 'threads', items: [] }));
  console.log('<<<JSON_END>>>');
  await closeTab(p);
} else {
await p.waitForSelector('div[data-pressable-container] a[href*="/post/"]', { timeout: 20000 });
for (let i = 0; i < __SCROLLS__; i++) { await p.evaluate('window.scrollBy(0, 2200)'); await new Promise(r => setTimeout(r, 1600)); }
const payload = await p.evaluate(`(() => {
  const seen = new Set();
  const items = [];
  for (const a of document.querySelectorAll('div[data-pressable-container] a[href*="/post/"]')) {
    let c = a.closest('div[data-pressable-container]');
    if (!c || seen.has(c)) continue;
    seen.add(c);
    const timeEl = c.querySelector('time');
    const userA = c.querySelector('a[href^="/@"]');
    // action bar: buttons whose svg has an aria-label; capture order + trailing count text
    const actions = [];
    for (const svg of c.querySelectorAll('svg[aria-label]')) {
      const btn = svg.closest('div[role="button"], button');
      if (!btn) continue;
      const count = (btn.innerText || '').replace(/[^0-9.,KkMm]/g, '');
      actions.push({ label: svg.getAttribute('aria-label'), count });
    }
    items.push({
      post_href: a.getAttribute('href'),
      datetime: timeEl ? timeEl.getAttribute('datetime') : null,
      author_href: userA ? userA.getAttribute('href') : null,
      text: (c.innerText || ''),
      actions: actions.slice(0, 8),
    });
  }
  return { query: ${JSON.stringify(__QUERY_JSON__)}, count: items.length, items };
})()`);
console.log('<<<JSON_START>>>');
console.log(JSON.stringify(payload));
console.log('<<<JSON_END>>>');
await closeTab(p);
}
