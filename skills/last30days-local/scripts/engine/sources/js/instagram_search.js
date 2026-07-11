const q = __QUERY_JSON__;
const ENRICH = __ENRICH__;
const searchUrl = 'https://www.instagram.com/explore/search/keyword/?q=' + encodeURIComponent(q);
const p = await openTab(searchUrl);
await p.waitForLoadState('load');
await new Promise(r => setTimeout(r, 9000));
const state = await p.evaluate(`(() => {
  if (document.querySelector('input[name="username"]')) return 'login';
  const links = document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]').length;
  if (links > 0) return 'results';
  return 'empty';
})()`);
if (state === 'login') {
  console.log('<<<JSON_START>>>');
  console.log(JSON.stringify({ login_required: true, source: 'instagram', items: [] }));
  console.log('<<<JSON_END>>>');
  await closeTab(p);
} else {
if (state === 'empty') {
  const tagQ = '#' + q.replace(/[^a-z0-9]+/gi, '').toLowerCase();
  await p.goto('https://www.instagram.com/explore/search/keyword/?q=' + encodeURIComponent(tagQ));
  await new Promise(r => setTimeout(r, 9000));
}
for (let i = 0; i < __SCROLLS__; i++) { await p.evaluate('window.scrollBy(0, 2200)'); await new Promise(r => setTimeout(r, 1800)); }
const grid = await p.evaluate(`(() => {
  const items = [];
  const seen = new Set();
  for (const a of document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]')) {
    const href = (a.getAttribute('href') || '').split('?')[0];
    if (!href || seen.has(href)) continue;
    seen.add(href);
    const img = a.querySelector('img');
    items.push({ href, alt: img ? (img.getAttribute('alt') || '') : null });
  }
  return items;
})()`);
const enriched = [];
for (const it of grid.slice(0, ENRICH)) {
  try {
    await p.goto('https://www.instagram.com' + it.href);
    await new Promise(r => setTimeout(r, 5000));
    const detail = await p.evaluate(`(() => {
      const timeEl = document.querySelector('time[datetime]');
      const authorA = document.querySelector('header a[href^="/"], section a[href^="/"]');
      const likeText = Array.from(document.querySelectorAll('section span'))
        .map(s => (s.innerText || '').trim())
        .find(t => /^\\d[\\d.,]*\\s/.test(t) && t.length < 60) || null;
      return {
        datetime: timeEl ? timeEl.getAttribute('datetime') : null,
        author_href: authorA ? authorA.getAttribute('href') : null,
        like_text: likeText,
      };
    })()`);
    enriched.push({ ...it, ...detail });
  } catch (e) {
    enriched.push({ ...it, error: String(e).slice(0, 100) });
  }
}
const rest = grid.slice(ENRICH).map(it => ({ ...it }));
console.log('<<<JSON_START>>>');
console.log(JSON.stringify({ query: q, count: grid.length, items: enriched.concat(rest) }));
console.log('<<<JSON_END>>>');
await closeTab(p);
}
