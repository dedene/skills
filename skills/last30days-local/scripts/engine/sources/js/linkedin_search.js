const q = __QUERY_JSON__;
const LIMIT = __LIMIT__;
const url = 'https://www.linkedin.com/search/results/content/?keywords=' + encodeURIComponent(q) + '&sortBy=%22date_posted%22';
const p = await openTab(url);
await p.waitForLoadState('load');
await new Promise(r => setTimeout(r, 6000));
const login = await p.evaluate(`(() => {
  return /\\/(login|authwall|checkpoint)/.test(location.pathname) || !!document.querySelector('.sign-in-form, form.login__form, a[data-tracking-control-name*="sign-in"]');
})()`);
if (login) {
  console.log('<<<JSON_START>>>');
  console.log(JSON.stringify({ login_required: true, source: 'linkedin', items: [] }));
  console.log('<<<JSON_END>>>');
  await closeTab(p);
} else {
await p.waitForSelector('[data-testid="expandable-text-box"]', { timeout: 25000 });
for (let i = 0; i < __SCROLLS__; i++) {
  await p.evaluate('window.scrollBy(0, 2500)');
  await new Promise(r => setTimeout(r, 1800));
}
const payload = await p.evaluate(`(async () => {
  const seen = new Set();
  const containers = [];
  for (const box of document.querySelectorAll('[data-testid="expandable-text-box"]')) {
    let c = box;
    for (let i = 0; i < 14 && c; i++) {
      if ((c.innerText || '').startsWith('Feed post')) break;
      c = c.parentElement;
    }
    if (!c || seen.has(c)) continue;
    seen.add(c);
    containers.push(c);
  }
  window.__copied = null;
  navigator.clipboard.writeText = async (t) => { window.__copied = t; };
  const items = [];
  for (const c of containers.slice(0, ${LIMIT})) {
    const box = c.querySelector('[data-testid="expandable-text-box"]');
    const authorLink = c.querySelector('a[href*="/in/"], a[href*="/company/"]');
    const it = {
      text: box ? box.innerText : null,
      author_name: authorLink ? (authorLink.innerText || '').split('\\n')[0].trim() : null,
      author_href: authorLink ? authorLink.getAttribute('href') : null,
      container_head: (c.innerText || '').slice(0, 260),
      container_tail: (c.innerText || '').slice(-220),
      aria_social: Array.from(c.querySelectorAll('[aria-label]'))
        .map(e => e.getAttribute('aria-label'))
        .filter(a => /reaction|comment|repost|impression/i.test(a || ''))
        .slice(0, 8),
      url: null,
    };
    const menuBtn = c.querySelector('button[aria-label^="Open control menu"]');
    if (menuBtn) {
      window.__copied = null;
      menuBtn.click();
      await new Promise(r => setTimeout(r, 800));
      const copy = Array.from(document.querySelectorAll('[role="menu"] [role="menuitem"], [role="menu"] button, [role="dialog"] button'))
        .find(b => /copy link/i.test(b.innerText || ''));
      if (copy) { copy.click(); await new Promise(r => setTimeout(r, 600)); }
      it.url = window.__copied;
      document.body.click();
      await new Promise(r => setTimeout(r, 300));
    }
    items.push(it);
  }
  return { query: ${JSON.stringify(q)}, count: items.length, items };
})()`);
console.log('<<<JSON_START>>>');
console.log(JSON.stringify(payload));
console.log('<<<JSON_END>>>');
await closeTab(p);
}
