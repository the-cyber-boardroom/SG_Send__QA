/**
 * <qa-sidebar> Web Component
 * v0.1.0 — QA site navigation sidebar
 *
 * Fetches /_data/qa_sidebar.json and renders grouped navigation.
 * Highlights the current page based on window.location.pathname.
 * Groups are collapsible; composite use-cases get a ★ marker.
 *
 * Attributes:
 *   data-current  Override the active page path (optional — defaults to window.location.pathname)
 *
 * Usage:
 *   <qa-sidebar></qa-sidebar>
 *   <qa-sidebar data-current="/pages/use-cases/02-upload-share/combined_link/"></qa-sidebar>
 */

class QaSidebar extends HTMLElement {
    connectedCallback() {
        this._current = this.getAttribute('data-current') || window.location.pathname;
        this._renderLoading();
        this._fetchAndRender();
    }

    _renderLoading() {
        this.innerHTML = '<nav class="qa-nav"><p class="qa-nav-meta">Loading…</p></nav>';
    }

    async _fetchAndRender() {
        try {
            // Use absolute path — works regardless of page depth
            const resp = await fetch('/_data/qa_sidebar.json');
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const data = await resp.json();
            this.innerHTML = this._buildHTML(data);
            this._setupToggles();
        } catch (err) {
            this.innerHTML = `<nav class="qa-nav"><p class="qa-nav-meta" style="color:var(--color-error)">
                Sidebar unavailable: ${err.message}
            </p></nav>`;
        }
    }

    _isActive(href) {
        const cur = this._current;
        // Exact match or current path starts with the href
        return cur === href || cur.startsWith(href);
    }

    _buildHTML(data) {
        const staticLinks = [
            { label: 'Home',       href: '/pages/' },
            { label: 'Dashboard',  href: '/pages/dashboard/' },
            { label: 'Pipeline',   href: '/pages/pipeline/' },
            { label: 'Roadmap',    href: '/pages/roadmap/' },
            { label: 'Known Bugs', href: '/pages/known-bugs/' },
        ];

        const externalLinks = [
            { label: 'SG/Send App', href: 'https://send.sgraph.ai' },
            { label: 'GitHub Repo', href: 'https://github.com/the-cyber-boardroom/SG_Send__qa' },
        ];

        const staticHTML = staticLinks.map(l =>
            `<a class="qa-nav-link${this._isActive(l.href) ? ' is-active' : ''}" href="${l.href}">${this._esc(l.label)}</a>`
        ).join('\n');

        const groupsHTML = (data.groups || []).map(group => {
            const groupHref = `/pages/use-cases/${group.id}/`;
            const isGroupActive = (data.groups || []).some(() => false) ||
                (group.members || []).some(m => this._isActive(`/pages/use-cases/${group.id}/${m.id}/`));

            const membersHTML = (group.members || []).map(m => {
                const href = `/pages/use-cases/${group.id}/${m.id}/`;
                const active = this._isActive(href);
                return `<a class="qa-nav-item${active ? ' is-active' : ''}" href="${href}">${m.composite ? '<span class="qa-nav-star" title="Composite test">★</span> ' : ''}${this._esc(m.title)}</a>`;
            }).join('\n');

            return `<div class="qa-nav-group${isGroupActive ? ' is-open' : ''}">
                <button class="qa-nav-group-toggle" aria-expanded="${isGroupActive}" type="button">
                    <span class="qa-nav-group-label"><span class="qa-nav-icon">${group.icon}</span> ${this._esc(group.name)}</span>
                    <span class="qa-nav-chevron" aria-hidden="true">▶</span>
                </button>
                <div class="qa-nav-group-members">
                    ${membersHTML}
                </div>
            </div>`;
        }).join('\n');

        const externalHTML = externalLinks.map(l =>
            `<a class="qa-nav-link qa-nav-link--external" href="${this._esc(l.href)}" target="_blank" rel="noopener noreferrer">${this._esc(l.label)} ↗</a>`
        ).join('\n');

        return `<nav class="qa-nav" aria-label="QA site navigation">
            <div class="qa-nav-section">
                ${staticHTML}
            </div>
            <div class="qa-nav-section">
                <div class="qa-nav-section-header">Use Cases</div>
                ${groupsHTML}
            </div>
            <div class="qa-nav-section qa-nav-section--external">
                ${externalHTML}
            </div>
        </nav>`;
    }

    _setupToggles() {
        this.querySelectorAll('.qa-nav-group-toggle').forEach(btn => {
            btn.addEventListener('click', () => {
                const group = btn.closest('.qa-nav-group');
                const nowOpen = group.classList.toggle('is-open');
                btn.setAttribute('aria-expanded', String(nowOpen));
            });
        });
    }

    _esc(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
}

customElements.define('qa-sidebar', QaSidebar);
