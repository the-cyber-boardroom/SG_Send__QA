/**
 * <qa-test-page> Web Component
 * v0.1.0 — Full use-case documentation page renderer
 *
 * Reads metadata from <script type="application/json" id="qa-metadata"> embedded
 * in the page at generation time (no extra HTTP request). Falls back to fetching
 * screenshots/_metadata.json if the inline block is absent.
 *
 * Attributes:
 *   data-use-case      Use case id, e.g. "combined_link"
 *   data-group         Group id, e.g. "02-upload-share"
 *   data-commit        Git commit SHA (for provenance line)
 *   data-version       Site version, e.g. "v0.2.38"
 *   data-github-url    Full GitHub URL to the test file
 *   data-live-site-url Base URL for screenshots, e.g. "https://qa.send.sgraph.ai"
 *
 * Sections rendered (in order):
 *   1. Title
 *   2. Provenance line (version, commit, timestamp)
 *   3. User story (from module_doc)
 *   4. Test methods table
 *   5. Screenshot gallery (using <qa-screenshot-step>)
 *   6. Test source code (collapsible, from <script type="text/qa-source">)
 *   7. GitHub link
 */

class QaTestPage extends HTMLElement {
    connectedCallback() {
        this._useCase    = this.getAttribute('data-use-case') || '';
        this._group      = this.getAttribute('data-group') || '';
        this._commit     = this.getAttribute('data-commit') || '';
        this._version    = this.getAttribute('data-version') || '';
        this._githubUrl  = this.getAttribute('data-github-url') || '';
        this._liveSiteUrl = this.getAttribute('data-live-site-url') || 'https://qa.send.sgraph.ai';

        this._loadAndRender();
    }

    async _loadAndRender() {
        const metadata = await this._loadMetadata();
        if (!metadata) {
            this.innerHTML = `<p class="qa-error">Could not load metadata for <code>${this._esc(this._useCase)}</code>.</p>`;
            return;
        }
        this.innerHTML = this._buildHTML(metadata);
    }

    async _loadMetadata() {
        // 1. Try inline embedded JSON
        const inlineEl = document.getElementById('qa-metadata');
        if (inlineEl) {
            try { return JSON.parse(inlineEl.textContent); } catch (e) { /* fall through */ }
        }
        // 2. Fall back to fetching _metadata.json relative to the page
        try {
            const resp = await fetch('screenshots/_metadata.json');
            if (resp.ok) return await resp.json();
        } catch (e) { /* fall through */ }
        return null;
    }

    _deduplicateTests(tests) {
        // Strip __NN__ prefix to find duplicates:
        //   test__01__foo_bar  →  test_foo_bar (normalised)
        //   test_foo_bar       →  test_foo_bar (normalised, same)
        // When both exist, keep the __NN__ prefixed (newer) version.
        const byNorm = new Map();
        for (const t of tests) {
            const norm = t.method.replace(/__\d+__/, '_');
            if (!byNorm.has(norm)) byNorm.set(norm, []);
            byNorm.get(norm).push(t);
        }
        const result = [];
        for (const group of byNorm.values()) {
            if (group.length === 1) {
                result.push(group[0]);
            } else {
                // Prefer the one with __NN__ in its name
                const prefixed = group.find(t => /__\d+__/.test(t.method));
                result.push(prefixed || group[0]);
            }
        }
        return result;
    }

    _screenshotUrl(name) {
        // During migration: full URL to live site
        // After cutover (Session 5): relative path
        return `${this._liveSiteUrl}/pages/use-cases/${this._group}/${this._useCase}/screenshots/${name}.png`;
    }

    _deterministicUrl(name) {
        return `${this._liveSiteUrl}/pages/use-cases/${this._group}/${this._useCase}/screenshots/${name}__deterministic.png`;
    }

    _buildHTML(meta) {
        const title = (this._useCase || meta.use_case || '')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, c => c.toUpperCase());

        const tests = this._deduplicateTests(meta.tests || []);
        const screenshots = meta.screenshots || [];

        // --- Provenance ---
        const version = this._version || meta.version || '';
        const commit  = this._commit  ? this._commit.slice(0, 8) : '';
        const genAt   = meta.generated_at || '';
        const provenanceParts = [];
        if (version)  provenanceParts.push(`<span>${this._esc(version)}</span>`);
        if (commit)   provenanceParts.push(`<a class="qa-commit" href="${this._esc(this._githubUrl)}" target="_blank" rel="noopener">${this._esc(commit)}</a>`);
        if (genAt)    provenanceParts.push(`<span>${this._esc(genAt.replace('T', ' ').replace('Z', ' UTC'))}</span>`);
        const provenanceHTML = provenanceParts.length
            ? `<p class="qa-provenance">${provenanceParts.join(' · ')}</p>`
            : '';

        // --- User story ---
        const moduleDoc = (meta.module_doc || '').trim();
        const userStoryHTML = moduleDoc
            ? `<blockquote class="qa-user-story"><pre class="qa-user-story__text">${this._esc(moduleDoc)}</pre></blockquote>`
            : '';

        // --- Test methods table ---
        const methodsHTML = tests.length ? `
            <h2>Test Methods</h2>
            <table class="qa-methods-table">
                <thead><tr><th>Method</th><th>Description</th><th>Screenshots</th></tr></thead>
                <tbody>
                    ${tests.map(t => `<tr>
                        <td><code>${this._esc(t.method)}</code></td>
                        <td>${this._esc(t.doc || '')}</td>
                        <td>${(t.screenshots || []).length}</td>
                    </tr>`).join('')}
                </tbody>
            </table>` : '';

        // --- Screenshot gallery ---
        const galleryHTML = screenshots.length ? `
            <h2>Screenshots</h2>
            <div class="qa-gallery">
                ${screenshots.map(s => {
                    const hasdet = s.has_masks;
                    return `<qa-screenshot-step
                        name="${this._esc(s.name)}"
                        description="${this._esc(s.description || '')}"
                        screenshot-url="${this._esc(this._screenshotUrl(s.name))}"
                        ${hasdet ? `deterministic-url="${this._esc(this._deterministicUrl(s.name))}"` : ''}
                    ></qa-screenshot-step>`;
                }).join('\n')}
            </div>` : '';

        // --- Test source ---
        const sourceEl = document.querySelector('script[type="text/qa-source"]');
        const sourceHTML = sourceEl && sourceEl.textContent.trim() ? `
            <details class="qa-source-block">
                <summary>Test source code</summary>
                <div class="highlight"><pre>${sourceEl.textContent.trim()}</pre></div>
            </details>` : '';

        // --- GitHub link ---
        const githubHTML = this._githubUrl ? `
            <p class="qa-github-link">
                <a href="${this._esc(this._githubUrl)}" target="_blank" rel="noopener">
                    View test source on GitHub ↗
                </a>
            </p>` : '';

        return `
            <article class="qa-test-page">
                <h1 class="qa-test-page__title">${this._esc(title)}</h1>
                ${provenanceHTML}
                ${userStoryHTML}
                ${methodsHTML}
                ${galleryHTML}
                ${sourceHTML}
                ${githubHTML}
            </article>`;
    }

    _esc(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
}

customElements.define('qa-test-page', QaTestPage);
