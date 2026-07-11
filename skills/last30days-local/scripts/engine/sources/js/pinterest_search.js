const q = __QUERY_JSON__;
const p = await openTab('https://www.pinterest.com/search/pins/?q=' + encodeURIComponent(q));
await p.waitForLoadState('load');
await new Promise(r => setTimeout(r, 8000));
const login = await p.evaluate(`(() => {
  return !!document.querySelector('[data-test-id="login-button"], form[data-test-id="registerForm"]') && !document.querySelector('[data-test-id="pin"]');
})()`);
if (login) {
  console.log('<<<JSON_START>>>');
  console.log(JSON.stringify({ login_required: true, source: 'pinterest', items: [] }));
  console.log('<<<JSON_END>>>');
  await closeTab(p);
} else {
for (let i = 0; i < __SCROLLS__; i++) { await p.evaluate('window.scrollBy(0, 2500)'); await new Promise(r => setTimeout(r, 1800)); }
const payload = await p.evaluate(`(() => {
  const items = [];
  const seen = new Set();
  for (const a of document.querySelectorAll('a[href^="/pin/"]')) {
    const href = (a.getAttribute('href') || '').split('?')[0];
    if (!href || seen.has(href)) continue;
    seen.add(href);
    const card = a.closest('[data-test-id="pin"]') || a.closest('div[data-grid-item]') || a;
    const img = card.querySelector('img');
    items.push({
      href,
      alt: img ? (img.getAttribute('alt') || '').slice(0, 300) : null,
      card_text: (card.innerText || '').slice(0, 200),
    });
  }
  return { query: ${JSON.stringify(__QUERY_JSON__)}, count: items.length, items };
})()`);
console.log('<<<JSON_START>>>');
console.log(JSON.stringify(payload));
console.log('<<<JSON_END>>>');
await closeTab(p);
}
