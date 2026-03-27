/**
 * <qa-dashboard> Web Component
 * v0.1.0 — QA coverage dashboard renderer
 *
 * Reads qa_summary.json and renders:
 *   - Top-level stats (total tests, screenshots, coverage)
 *   - Per-group coverage table
 *   - "Needs attention" list (groups below 100% coverage)
 *
 * Usage:
 *   <qa-dashboard></qa-dashboard>
 */

class QaDashboard extends HTMLElement {
    connectedCallback() {
        this.innerHTML = '<p class="qa-loading">Loading dashboard…</p>';
        this._fetchAndRender();
    }

    async _fetchAndRender() {
        try {
            const resp = await fetch('/_data/qa_summary.json');
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const data = await resp.json();
            this.innerHTML = this._buildHTML(data);
        } catch (err) {
            this.innerHTML = `<p class="qa-error">Dashboard unavailable: ${this._esc(err.message)}</p>`;
        }
    }

    _buildHTML(data) {
        const groups = data.groups || [];
        const totalTests       = data.total_tests || 0;
        const totalScreenshots = data.total_screenshots || 0;
        const zeroEvidence     = data.zero_evidence || 0;
        const version          = data.version || '';
        const generatedAt      = data.generated_at || '';

        const withEvidence   = totalTests - zeroEvidence;
        const overallCovPct  = totalTests > 0 ? Math.round((withEvidence / totalTests) * 100) : 0;

        // Attention: groups below 100%
        const needsAttention = groups.filter(g => g.coverage_pct < 100);

        const statsHTML = `
            <div class="qa-stats">
                <div class="qa-stat-card">
                    <span class="number">${totalTests}</span>
                    <span class="label">Tests</span>
                </div>
                <div class="qa-stat-card">
                    <span class="number">${totalScreenshots}</span>
                    <span class="label">Screenshots</span>
                </div>
                <div class="qa-stat-card">
                    <span class="number">${overallCovPct}%</span>
                    <span class="label">With Evidence</span>
                </div>
                <div class="qa-stat-card">
                    <span class="number">${groups.length}</span>
                    <span class="label">Groups</span>
                </div>
            </div>`;

        const coverageBar = (pct) => {
            const cls = pct === 100 ? 'qa-bar--full' : pct >= 80 ? 'qa-bar--good' : pct >= 50 ? 'qa-bar--warn' : 'qa-bar--low';
            return `<div class="qa-bar ${cls}" style="width:${pct}%" title="${pct}%"></div>`;
        };

        const groupTableHTML = `
            <h2>Coverage by Group</h2>
            <table class="qa-coverage-table">
                <thead>
                    <tr><th>Group</th><th>Tests</th><th>With Evidence</th><th>Coverage</th></tr>
                </thead>
                <tbody>
                    ${groups.map(g => `<tr>
                        <td><a href="/pages/use-cases/${this._esc(g.id)}/">${this._esc(g.icon || '')} ${this._esc(g.name)}</a></td>
                        <td>${g.total}</td>
                        <td>${g.with_evidence}</td>
                        <td>
                            <div class="qa-bar-wrap" title="${g.coverage_pct}%">
                                ${coverageBar(g.coverage_pct)}
                            </div>
                            <span class="qa-bar-label">${g.coverage_pct}%</span>
                        </td>
                    </tr>`).join('')}
                </tbody>
            </table>`;

        const attentionHTML = needsAttention.length ? `
            <h2>Needs Attention</h2>
            <ul class="qa-attention-list">
                ${needsAttention.map(g => `<li>
                    <a href="/pages/use-cases/${this._esc(g.id)}/">${this._esc(g.icon || '')} ${this._esc(g.name)}</a>
                    — ${g.coverage_pct}% (${g.with_evidence}/${g.total} with screenshots)
                </li>`).join('')}
            </ul>` : `<p class="qa-all-good">All groups have screenshot evidence. ✓</p>`;

        const metaHTML = (version || generatedAt) ? `
            <p class="qa-provenance">
                ${version ? `<span>${this._esc(version)}</span>` : ''}
                ${generatedAt ? `<span>${this._esc(generatedAt.replace('T', ' ').replace('Z', ' UTC'))}</span>` : ''}
            </p>` : '';

        return `
            <section class="qa-dashboard">
                <h1>QA Coverage Dashboard</h1>
                ${metaHTML}
                ${statsHTML}
                ${groupTableHTML}
                ${attentionHTML}
            </section>`;
    }

    _esc(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
}

customElements.define('qa-dashboard', QaDashboard);
