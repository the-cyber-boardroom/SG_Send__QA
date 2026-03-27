/**
 * <qa-screenshot-step> Web Component
 * v0.1.0 — Single screenshot card with deterministic toggle
 *
 * Renders a screenshot with its step number, title, description,
 * and an optional "deterministic view" toggle.
 *
 * Attributes:
 *   name              Screenshot name, e.g. "01_file_selected"
 *   description       Human-readable description
 *   screenshot-url    URL to the main PNG
 *   deterministic-url URL to the deterministic PNG (optional)
 *   step-index        Override display number (optional — derived from name if absent)
 *
 * Usage:
 *   <qa-screenshot-step
 *       name="01_file_selected"
 *       description="File selected — delivery step active"
 *       screenshot-url="https://qa.send.sgraph.ai/.../01_file_selected.png"
 *       deterministic-url="https://qa.send.sgraph.ai/.../01_file_selected__deterministic.png">
 *   </qa-screenshot-step>
 */

class QaScreenshotStep extends HTMLElement {
    connectedCallback() {
        this._render();
    }

    static get observedAttributes() {
        return ['name', 'description', 'screenshot-url', 'deterministic-url'];
    }

    attributeChangedCallback() {
        if (this.isConnected) this._render();
    }

    _render() {
        const name        = this.getAttribute('name') || '';
        const description = this.getAttribute('description') || '';
        const screenshotUrl   = this.getAttribute('screenshot-url') || '';
        const deterministicUrl = this.getAttribute('deterministic-url') || '';

        // Derive step number and title from name: "01_file_selected" → "01", "File Selected"
        const match = name.match(/^(\d+)_(.+)$/);
        const stepNum = match ? match[1] : '—';
        const stepTitle = match
            ? match[2].replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
            : name.replace(/_/g, ' ');

        const hasDet = deterministicUrl && deterministicUrl !== screenshotUrl;
        const toggleId = `det-toggle-${name}-${Math.random().toString(36).slice(2, 7)}`;

        this.className = 'qa-screenshot-card';
        this.innerHTML = `
            <div class="qa-screenshot-card__header">
                <span class="qa-screenshot-card__step">${this._esc(stepNum)}</span>
                <h3 class="qa-screenshot-card__title">${this._esc(stepTitle)}</h3>
            </div>
            ${description ? `<p class="qa-screenshot-card__desc">${this._esc(description)}</p>` : ''}
            <div class="qa-screenshot-card__image-wrap">
                <img class="qa-screenshot-card__img"
                     src="${this._esc(screenshotUrl)}"
                     alt="${this._esc(stepTitle)}"
                     loading="lazy"
                     onerror="this.style.opacity='0.3';this.alt='Screenshot not available'">
            </div>
            ${hasDet ? `
            <div class="qa-screenshot-card__det-toggle">
                <label class="qa-toggle" for="${toggleId}">
                    <input class="qa-toggle__input" type="checkbox" id="${toggleId}" aria-label="Show deterministic view">
                    <span class="qa-toggle__label">Deterministic view</span>
                </label>
            </div>` : ''}
        `;

        if (hasDet) {
            const cb = this.querySelector(`#${toggleId}`);
            const img = this.querySelector('.qa-screenshot-card__img');
            cb.addEventListener('change', () => {
                img.src = cb.checked ? deterministicUrl : screenshotUrl;
            });
        }
    }

    _esc(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
}

customElements.define('qa-screenshot-step', QaScreenshotStep);
