(() => {
  const DATA = window.PORTFOLIO_DATA || window.PORTFOLIO_DATA_FALLBACK;
  const view = document.getElementById('route-view');
  const navLinks = [...document.querySelectorAll('[data-route]')];
  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();

  const FILTERS = ['ALL', ...(DATA?.categories || [])];
  const PAGE_URLS = {
    home: 'index.html',
    about: 'about.html',
    writeups: 'writeups.html',
    resources: 'resources.html',
    skills: 'resources.html',
    contact: 'contact.html'
  };
  const PAGE_TITLES = {
    home: 'Home', about: 'About', writeups: 'Notes & Learning',
    resources: 'Resources', contact: 'Contact', writeup: 'Write-up'
  };
  let activeFilter = 'ALL';

  const escapeHtml = (value = '') => String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  const tags = (items = []) => items.map(item => `<span>${escapeHtml(item)}</span>`).join('');

  function imageData(page) {
    return DATA.sectionImages?.[page] || {};
  }

  function decorativeImage(page, className, decorative = true) {
    const image = imageData(page);
    if (!image.src) return '';
    const accessibility = decorative
      ? 'alt="" aria-hidden="true"'
      : `alt="${escapeHtml(image.alt || '')}"`;
    return `<img class="${escapeHtml(className)}" src="${escapeHtml(image.src)}" ${accessibility} decoding="async">`;
  }

  function sectionVisual(page, index) {
    const image = imageData(page);
    if (!image.src) return '';
    return `
      <figure class="section-visual ${escapeHtml(page)}-visual">
        <img src="${escapeHtml(image.src)}" alt="${escapeHtml(image.alt || '')}" loading="eager" decoding="async">
        <div class="section-visual-grid" aria-hidden="true"></div>
        <figcaption><span>VISUAL / ${escapeHtml(index)}</span><strong>${escapeHtml(image.caption || '')}</strong></figcaption>
      </figure>`;
  }

  function redirectLegacyRoute() {
    // Keep old bookmarks working without treating anchors such as #main as routes.
    if (!location.hash.startsWith('#/')) {
      if (!location.pathname.endsWith('/skills.html')) return false;
      const target = new URL('resources.html', location.href);
      target.search = location.search;
      target.hash = location.hash;
      location.replace(target.href);
      return true;
    }
    const [page = 'home', encodedSlug] = location.hash.slice(2).split('/').filter(Boolean);
    let href = Object.hasOwn(PAGE_URLS, page) ? PAGE_URLS[page] : PAGE_URLS.home;
    if (page === 'writeups' && encodedSlug) {
      let slug = encodedSlug;
      try { slug = decodeURIComponent(encodedSlug); } catch { /* Preserve malformed IDs for the not-found page. */ }
      href = `writeup.html?id=${encodeURIComponent(slug)}`;
    }
    location.replace(new URL(href, location.href).href);
    return true;
  }

  function setPageTitle(title) {
    document.title = `${title} | ${DATA.profile.handle}`;
  }

  function setActiveNav(page) {
    navLinks.forEach(link => {
      const active = link.dataset.route === page;
      link.classList.toggle('active', active);
      active ? link.setAttribute('aria-current', 'page') : link.removeAttribute('aria-current');
    });
  }

  function externalButton(label, url, variant = '') {
    return `<a class="button ${variant}" href="${escapeHtml(url)}" target="_blank" rel="noreferrer">${escapeHtml(label)} <span>↗</span></a>`;
  }

  function repoCard(repo) {
    return `
      <a class="repo-card" href="${escapeHtml(repo.url)}" target="_blank" rel="noreferrer">
        <div class="repo-topline"><span class="repo-icon">&gt;_</span><span class="public-pill">PUBLIC</span></div>
        <h3>${escapeHtml(repo.name)}</h3>
        <p>${escapeHtml(repo.summary)}</p>
        <div class="tag-row">${tags(repo.tags)}</div>
        <div class="repo-foot"><span>github.com/dungthtd9126</span><strong>VIEW ↗</strong></div>
      </a>`;
  }

  function homePage() {
    const github = DATA.links.find(x => x.label === 'GitHub')?.url || '#';
    const pwnable = DATA.links.find(x => x.label === 'pwnable.tw')?.url || '#';
    const hackmd = DATA.links.find(x => x.label === 'HackMD')?.url || '#';
    return `
      <section class="hero-page section-shell">
        ${decorativeImage('home', 'hero-background-image')}
        <div class="hero-copy">
          <div class="eyebrow"><span></span>${escapeHtml(DATA.profile.eyebrow || 'PWN / CTF / LOW LEVEL')}</div>
          <h1><span class="name-glow">${escapeHtml(DATA.profile.handle).toUpperCase()}</span><small>${escapeHtml(DATA.profile.headline)}</small></h1>
          <p>${escapeHtml(DATA.profile.intro)}</p>
          <div class="button-row">
            ${externalButton('GitHub', github)}
            ${externalButton('pwnable.tw', pwnable)}
            ${externalButton('HackMD', hackmd, 'violet')}
          </div>
          <div class="hero-status"><span class="pulse"></span><code>learning → breaking → documenting</code></div>
        </div>
        <div class="hero-art" aria-hidden="true">
          <div class="galaxy-disc"></div><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="planet"></div>
        </div>
      </section>

      <section class="home-projects section-shell">
        <div class="section-heading compact">
          <div><span class="index">/ 01</span><p class="kicker">SELECTED REPOSITORIES</p></div>
          <a href="writeups.html">Explore notes & learning →</a>
        </div>
        <div class="repo-grid">${DATA.repositories.map(repoCard).join('')}</div>
      </section>

      <section class="home-links section-shell">
        <a href="about.html"><span>01</span><strong>About</strong><em>Who I am and what I focus on.</em><b>→</b></a>
        <a href="writeups.html"><span>02</span><strong>Notes & Learning</strong><em>CTF notes and exploitation research.</em><b>→</b></a>
        <a href="resources.html"><span>03</span><strong>Resources</strong><em>Practice platforms, notes, and references.</em><b>→</b></a>
      </section>`;
  }

  function aboutPage() {
    return `
      <section class="subpage section-shell about-page">
        <header class="about-hero">
          <div class="about-intro">
            <div class="about-eyebrow"><span class="page-index">/ 01</span><p class="kicker">ABOUT ME</p></div>
            <h1>Beyond<br><span>the binary.</span></h1>
            <p class="about-lead">${escapeHtml(DATA.profile.aboutLead || DATA.profile.intro)}</p>
            <div class="about-actions">
              <a class="button" href="writeups.html">Read my write-ups <span aria-hidden="true">&#8594;</span></a>
              <a class="about-text-link" href="contact.html">Find me online <span aria-hidden="true">&#8599;</span></a>
            </div>
          </div>
          <figure class="about-visual">
            <div class="about-visual-frame">
              ${decorativeImage('about', 'about-visual-image', false)}
              <div class="scanline" aria-hidden="true"></div>
            </div>
            <figcaption class="about-identity">
              <div class="about-identity-meta">
                <span class="about-location">BASED IN VIETNAM</span>
                <span class="about-status"><i class="pulse" aria-hidden="true"></i>ALWAYS LEARNING</span>
              </div>
              <strong>${escapeHtml(DATA.profile.handle)}</strong>
              <div class="about-identity-footer">
                <span class="about-role">${escapeHtml(DATA.profile.role)}</span>
                <span class="about-index">VN / 01</span>
              </div>
            </figcaption>
          </figure>
        </header>

        <div class="about-details">
          <section class="about-story" aria-labelledby="about-story-title">
            <p class="kicker">THE APPROACH</p>
            <h2 id="about-story-title">Beyond the final script.</h2>
            ${(DATA.profile.about || []).map(p => `<p>${escapeHtml(p)}</p>`).join('')}
            <blockquote class="about-motto">${escapeHtml(DATA.profile.motto || '')}</blockquote>
            <blockquote class="about-quote">${escapeHtml(DATA.profile.aboutQuote || '')}</blockquote>
          </section>
          <aside class="about-focus" aria-labelledby="about-focus-title">
            <p class="kicker">ON MY RADAR</p>
            <h2 id="about-focus-title">Currently exploring</h2>
            <ol>
              ${(DATA.currentFocus || []).map((focus, i) => `<li><span aria-hidden="true">${String(i + 1).padStart(2, '0')}</span>${escapeHtml(focus)}</li>`).join('')}
            </ol>
            <a class="about-text-link" href="resources.html">Explore my resources <span aria-hidden="true">&#8594;</span></a>
          </aside>
        </div>

        ${(DATA.workflow || []).length ? `
          <section class="about-workflow" aria-labelledby="about-workflow-title">
            <div class="about-workflow-heading"><p class="kicker">HOW I LEARN</p><h2 id="about-workflow-title">One question at a time.</h2></div>
            <ol>
              ${DATA.workflow.map((step, i) => `<li><span class="workflow-number" aria-hidden="true">${String(i + 1).padStart(2, '0')}</span><h3>${escapeHtml(step.title)}</h3><p>${escapeHtml(step.summary)}</p></li>`).join('')}
            </ol>
          </section>` : ''}
      </section>`;
  }

  function allEntries() {
    return [...(DATA.writeups || []), ...(DATA.notes || [])];
  }

  function terminalCharacters(output) {
    const characters = Array.from(String(output));
    const characterCount = characters.length;
    const step = Math.max(55, 1000 / Math.max(characterCount, 1));
    return characters.map((character, index) => {
      const visibleCharacter = character === ' ' ? '&nbsp;' : escapeHtml(character);
      return `<span class="terminal-character" style="--character-index:${index};--terminal-step:${step}ms">${visibleCharacter}</span>`;
    }).join('');
  }

  function entryHref(item) {
    if (item.file) return `writeup.html?id=${encodeURIComponent(item.id)}`;
    return item.url || 'writeups.html';
  }

  function writeupCard(item, collection = 'writeups') {
    const internal = Boolean(item.file);
    const href = entryHref(item);
    const target = internal || !item.url ? '' : ' target="_blank" rel="noreferrer"';
    const action = internal ? 'OPEN NOTE' : collection === 'notes' ? 'READ NOTE' : 'READ WRITE-UP';
    return `
      <a class="writeup-card" href="${escapeHtml(href)}"${target}>
        <div class="writeup-meta"><span>${escapeHtml(item.category)}</span><span>${escapeHtml(item.source || (internal ? 'Portfolio' : 'External'))}</span></div>
        <h2>${escapeHtml(item.title)}</h2>
        <p>${escapeHtml(item.summary)}</p>
        <div class="tag-row">${tags(item.tags)}</div>
        <div class="writeup-link">${action} <span>${internal ? '→' : '↗'}</span></div>
      </a>`;
  }

  function writeupCards(collection = 'writeups') {
    const items = DATA[collection] || [];
    const filtered = activeFilter === 'ALL' ? items : items.filter(item => item.category === activeFilter);
    const noun = collection === 'notes' ? 'notes' : 'write-ups';
    return filtered.length ? filtered.map(item => writeupCard(item, collection)).join('') : `
      <div class="empty-state"><span>&gt;_</span><h2>No ${escapeHtml(activeFilter)} ${noun} yet.</h2><p>More notes are on the way. Explore another category in the meantime.</p></div>`;
  }

  function writeupsPage() {
    return `
      <section class="subpage section-shell">
        <div class="page-hero writeups-hero">
          <span class="page-index">/ 02</span>
          <div>
            <p class="kicker">NOTES & LEARNING</p>
            <h1>Break it.<br><span>Explain it.</span></h1>
            <p class="page-lead">Challenge write-ups, low-level research, and practical notes from the things I build, break, and learn.</p>
          </div>
          ${sectionVisual('writeups', '02')}
        </div>
        <div class="filter-bar" role="group" aria-label="Notes and learning categories">
          ${FILTERS.map(category => `<button type="button" data-filter="${category}" aria-pressed="${category === activeFilter}" class="${category === activeFilter ? 'active' : ''}">${category}</button>`).join('')}
        </div>
        <section class="entry-collection" aria-labelledby="writeups-collection-title">
          <div class="entry-collection-heading"><div><p class="kicker">WRITE-UPS</p><h2 id="writeups-collection-title">Challenge breakdowns.</h2></div><span>EXPLOIT / ANALYZE / DOCUMENT</span></div>
          <div class="writeup-grid" data-entry-collection="writeups" aria-live="polite">${writeupCards('writeups')}</div>
        </section>
        <section class="entry-collection notes-collection" aria-labelledby="notes-collection-title">
          <div class="entry-collection-heading"><div><p class="kicker">NOTES</p><h2 id="notes-collection-title">Ideas worth keeping.</h2></div><span>LEARN / APPLY / REPEAT</span></div>
          <div class="writeup-grid" data-entry-collection="notes" aria-live="polite">${writeupCards('notes')}</div>
        </section>
      </section>`;
  }

  function resourcesPage() {
    return `
      <section class="subpage section-shell">
        <div class="page-hero resources-hero">
          <span class="page-index">/ 03</span>
          <div class="resources-hero-copy">
            <div>
              <p class="kicker">RESOURCES & REFERENCES</p>
              <h1>Useful links.<br><span>Deeper reading.</span></h1>
              <p class="page-lead">Practice platforms, study notes, and documentation for exploring low-level systems.</p>
            </div>
            <aside class="resources-hero-note" aria-label="Resource philosophy">
              <span class="resources-note-label">FIELD NOTE / 03</span>
              <blockquote>${escapeHtml(DATA.profile.resourcesQuote || 'Read widely. Build deliberately. Break things until they make sense.')}</blockquote>
              <div class="resources-note-footer"><span></span><small>LEARN / APPLY / REPEAT</small></div>
            </aside>
          </div>
          ${sectionVisual('resources', '03')}
        </div>
        <div class="resource-grid">
          ${(DATA.resourceGroups || []).map((group, i) => `
            <article class="resource-card">
              <span class="resource-number">${String(i + 1).padStart(2, '0')}</span>
              <h2>${escapeHtml(group.title)}</h2>
              <ul class="resource-list">
                ${(group.items || []).map(item => `<li><a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer"><span><strong>${escapeHtml(item.label)}</strong><small>${escapeHtml(item.summary || '')}</small></span><b aria-hidden="true">&#8599;</b></a></li>`).join('')}
              </ul>
            </article>`).join('')}
        </div>
      </section>`;
  }

  function contactPage() {
    const terminalLines = [
      ['whoami', 'saitomu'],
      ['focus', 'pwn / low-level security / CTF'],
      ['status', 'always learning_']
    ];
    return `
      <section class="subpage section-shell contact-page">
        <div class="page-hero contact-hero">
          <span class="page-index">/ 04</span>
          <div><p class="kicker">CONTACT</p><h1>Find me<br><span>where I publish.</span></h1><p class="page-lead contact-lead">${escapeHtml(DATA.profile.contactLead || "Have a project in mind or a suggestion to share? I'd love to hear from you.")}</p></div>
          ${sectionVisual('contact', '04')}
        </div>
        <div class="contact-grid">
          ${(DATA.links || []).map(link => `<a href="${escapeHtml(link.url)}" target="_blank" rel="noreferrer"><span>${escapeHtml(link.label).toUpperCase()}</span><strong>${escapeHtml(link.value)}</strong><b>↗</b></a>`).join('')}
        </div>
        <div class="contact-terminal">
          <div class="terminal-top"><span></span><span></span><span></span><small>interactive shell / hover a command</small></div>
          <div class="terminal-body" aria-label="Interactive terminal">
            ${terminalLines.map(([command, output], index) => `
              <div class="terminal-entry">
                <button class="terminal-command" type="button" aria-expanded="false" aria-controls="terminal-output-${index}">$ ${escapeHtml(command)}</button>
                <code class="terminal-output" id="terminal-output-${index}">${terminalCharacters(output)}</code>
              </div>`).join('')}
          </div>
        </div>
      </section>`;
  }

  function inlineMarkdown(text) {
    return escapeHtml(text)
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1 ↗</a>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\*([^*]+)\*/g, '<em>$1</em>');
  }

  function markdownToHtml(markdown) {
    const lines = markdown.replace(/\r/g, '').split('\n');
    let html = '';
    let inCode = false;
    let codeLang = '';
    let code = [];
    let inList = false;

    const closeList = () => { if (inList) { html += '</ul>'; inList = false; } };

    for (const line of lines) {
      const fence = line.match(/^```\s*([^\s]*)/);
      if (fence) {
        closeList();
        if (!inCode) { inCode = true; codeLang = fence[1] || ''; code = []; }
        else {
          html += `<pre class="md-code"><div>${escapeHtml(codeLang || 'text')}</div><code>${escapeHtml(code.join('\n'))}</code></pre>`;
          inCode = false; codeLang = ''; code = [];
        }
        continue;
      }
      if (inCode) { code.push(line); continue; }
      if (!line.trim()) { closeList(); continue; }
      const h = line.match(/^(#{1,4})\s+(.+)$/);
      if (h) { closeList(); const level = h[1].length + 1; html += `<h${level}>${inlineMarkdown(h[2])}</h${level}>`; continue; }
      const quote = line.match(/^>\s?(.*)$/);
      if (quote) { closeList(); html += `<blockquote>${inlineMarkdown(quote[1])}</blockquote>`; continue; }
      const bullet = line.match(/^[-*]\s+(.+)$/);
      if (bullet) { if (!inList) { html += '<ul>'; inList = true; } html += `<li>${inlineMarkdown(bullet[1])}</li>`; continue; }
      closeList(); html += `<p>${inlineMarkdown(line)}</p>`;
    }
    closeList();
    if (inCode) html += `<pre class="md-code"><div>${escapeHtml(codeLang || 'text')}</div><code>${escapeHtml(code.join('\n'))}</code></pre>`;
    return html;
  }

  async function writeupDetailPage(slug) {
    const item = allEntries().find(entry => entry.id === slug && entry.file);
    if (!item) return notFoundPage();
    setPageTitle(item.title);
    view.innerHTML = `
      <section class="subpage section-shell"><div class="loading-note" role="status"><span class="pulse"></span><code>Loading note...</code></div></section>`;
    try {
      const response = await fetch(item.file, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const markdown = await response.text();
      return `
        <article class="subpage section-shell note-page">
          <a class="back-link" href="writeups.html">← Back to notes & learning</a>
          <header class="note-header"><p class="kicker">${escapeHtml(item.category)} / ${escapeHtml(item.source || 'Portfolio')}</p><h1>${escapeHtml(item.title)}</h1><p>${escapeHtml(item.summary || '')}</p><div class="tag-row">${tags(item.tags)}</div></header>
          <div class="markdown-body">${markdownToHtml(markdown)}</div>
        </article>`;
    } catch {
      return `
        <section class="subpage section-shell"><a class="back-link" href="writeups.html">← Back to notes & learning</a><div class="empty-state"><span>!</span><h1>Could not load this note.</h1><p>This note is unavailable right now. Please try again later.</p></div></section>`;
    }
  }

  function notFoundPage() {
    setPageTitle('Page not found');
    return `<section class="subpage section-shell"><div class="empty-state"><span>404</span><h1>Page not found.</h1><p><a href="index.html">Return home →</a></p></div></section>`;
  }

  async function render() {
    const page = document.body.dataset.page || 'home';
    setActiveNav(page === 'writeup' ? 'writeups' : page);
    setPageTitle(PAGE_TITLES[page] || 'Page not found');

    let html;
    if (page === 'writeup') html = await writeupDetailPage(new URLSearchParams(location.search).get('id'));
    else {
      const pages = { home: homePage, about: aboutPage, writeups: writeupsPage, resources: resourcesPage, contact: contactPage };
      html = pages[page] ? pages[page]() : notFoundPage();
    }

    view.innerHTML = html;
    view.classList.add('route-enter');

    if (page === 'writeups') {
      view.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', () => {
        activeFilter = button.dataset.filter;
        view.querySelectorAll('[data-filter]').forEach(filter => {
          const active = filter.dataset.filter === activeFilter;
          filter.classList.toggle('active', active);
          filter.setAttribute('aria-pressed', String(active));
        });
        view.querySelectorAll('[data-entry-collection]').forEach(grid => {
          grid.innerHTML = writeupCards(grid.dataset.entryCollection);
        });
      }));
    }
    if (page === 'contact') {
      view.querySelectorAll('.terminal-entry').forEach(entry => {
        const command = entry.querySelector('.terminal-command');
        const setOpen = open => {
          entry.classList.toggle('is-open', open);
          command.setAttribute('aria-expanded', String(open));
        };
        entry.addEventListener('mouseenter', () => setOpen(true));
        entry.addEventListener('mouseleave', () => {
          if (!command.matches(':focus')) setOpen(false);
        });
        command.addEventListener('focus', () => setOpen(true));
        command.addEventListener('blur', () => {
          if (!entry.matches(':hover')) setOpen(false);
        });
      });
    }
  }

  window.addEventListener('hashchange', redirectLegacyRoute);
  if (redirectLegacyRoute()) return;
  if (!DATA) {
    view.innerHTML = '<section class="subpage section-shell"><div class="empty-state"><span>!</span><h1>Portfolio content is unavailable.</h1><p>Please try again later.</p></div></section>';
    return;
  }
  render();
})();
