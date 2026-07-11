const q = __QUERY_JSON__; // JSON string literal injected by Python via json.dumps
const p = await openTab('https://x.com/search?q=' + encodeURIComponent(q) + '&f=live');
let hasTweets = true;
try {
  await p.waitForSelector('article[data-testid="tweet"]', { timeout: 20000 });
} catch (e) {
  hasTweets = false;
}
if (!hasTweets) {
  const login = await p.evaluate(`(() => {
    return !!document.querySelector('a[href="/login"], a[data-testid="login"]');
  })()`);
  if (login) {
    console.log('<<<JSON_START>>>');
    console.log(JSON.stringify({ login_required: true, source: 'x', items: [] }));
    console.log('<<<JSON_END>>>');
    await closeTab(p);
  } else {
    console.log('<<<JSON_START>>>');
    console.log(JSON.stringify({ query: q, count: 0, items: [], note: 'no results or unrecognized page' }));
    console.log('<<<JSON_END>>>');
    await closeTab(p);
  }
} else {
for (let i = 0; i < __SCROLLS__; i++) {
  await p.evaluate('window.scrollBy(0, 2000)');
  await new Promise(r => setTimeout(r, 1500));
}
const rows = await p.evaluate(`(() => {
  const out = [];
  for (const art of document.querySelectorAll('article[data-testid="tweet"]')) {
    const textEl = art.querySelector('div[data-testid="tweetText"]');
    const timeEl = art.querySelector('time');
    const statusLink = timeEl ? timeEl.closest('a') : null;
    const userLink = art.querySelector('div[data-testid="User-Name"] a');
    const metrics = {};
    for (const btn of art.querySelectorAll('button[data-testid]')) {
      const t = btn.getAttribute('data-testid');
      if (['reply','retweet','like'].includes(t)) {
        metrics[t] = (btn.getAttribute('aria-label') || '');
      }
    }
    const analytics = art.querySelector('a[href$="/analytics"]');
    if (analytics) metrics.views = analytics.getAttribute('aria-label') || '';
    out.push({
      url: statusLink ? statusLink.href : null,
      datetime: timeEl ? timeEl.getAttribute('datetime') : null,
      author_href: userLink ? userLink.getAttribute('href') : null,
      author_name: userLink ? userLink.textContent : null,
      text: textEl ? textEl.innerText : null,
      metrics,
    });
  }
  return out;
})()`);
console.log('<<<JSON_START>>>');
console.log(JSON.stringify({ query: q, count: rows.length, items: rows }));
console.log('<<<JSON_END>>>');
await closeTab(p);
}
