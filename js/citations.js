// Citation formatting shared by index.html (Recent Publications) and publications.html.
// Citations are plain CV text ("Authors. Title. Journal. Year..."); these helpers find the
// author list and the journal so the pages can shorten long author lists, render the CV's
// author markers (* equal contribution, $ co-corresponding) as superscripts, and set journal
// names in bold italic. Every helper returns the text unchanged when it cannot read it with confidence.

const NAME = /^(?:(?:de|van|von|der|den|la|da|di|du|le|dos)\s+)*\p{Lu}[\p{L}'’\-]*(?:[ \-]\p{Lu}[\p{L}'’\-]*)*\s+\p{Lu}(?:[.\-]?\p{Lu}){0,3}[*$†]*/u;
// Read author names from the start of a citation. Returns { authors, end } where end is the
// index just past the author list, or end = -1 when the list could not be read with confidence.
function parseAuthors(text) {
    const authors = [];
    let pos = 0;
    while (pos < text.length) {
        const rest = text.slice(pos).replace(/^and\s+/, '');
        const m = rest.match(NAME);
        if (!m) break;
        const sep = rest.slice(m[0].length).match(/^(?:\s*\.?\s*,\s*(?:and\s+)?|\s+and\s+|\s*\.\s+)/);
        if (!sep) break;
        authors.push(m[0].trim());
        pos += (text.length - pos - rest.length) + m[0].length + sep[0].length;
        if (!sep[0].includes(',') && sep[0].includes('.')) {
            // A period ends the list, unless another name follows (CV typo such as "Eid SA. Hinder LM,")
            const peek = text.slice(pos), pm = peek.match(NAME);
            if (!(pm && /^\s*(?:,|\s+and\s)/.test(peek.slice(pm[0].length)))) return { authors, end: pos };
        }
    }
    return { authors, end: -1 };
}
// End of the author list when parseAuthors could not read every name (CV entries with
// full given names, "et al.", etc.): the first "initials. " or "et al. " not followed by "Name,".
function authorsEndLoose(text) {
    const re = /(?:\b\p{Lu}[\p{L}'’\-]*\s+(?:\p{Lu}(?:[.\-]?\p{Lu}){0,3}|\p{Lu}\p{Ll}+)|\bet al)[*$†]*\.\s+/gu;
    let m;
    while ((m = re.exec(text))) {
        const after = text.slice(m.index + m[0].length);
        if (!/^\p{Lu}[\p{L}'’\-]*\s+\p{Lu}{1,4}[*$†]*,/u.test(after)) return m.index + m[0].length;
    }
    return -1;
}
// End of the title sentence starting at `from`, skipping abbreviation periods ("E. coli", "U.S.", "vs.").
function titleEnd(text, from) {
    const re = /[.?!](?=\s+\S|\p{Lu})/gu;
    re.lastIndex = from;
    let m;
    while ((m = re.exec(text))) {
        const before = text.slice(Math.max(from, m.index - 6), m.index);
        if (m[0] === '.' && (/(^|[\s.(])\p{Lu}$/u.test(before) || /\b(?:vs|e\.g|i\.e|al|et|No|Fig|Dr|St)$/.test(before))) continue;
        const ws = text.slice(m.index + 1).match(/^\s*/)[0].length;
        return m.index + 1 + ws;
    }
    return -1;
}
// Locate the journal (or venue) right after the title: [start, end) or null when unsure.
function findJournal(text) {
    let { end } = parseAuthors(text);
    if (end < 0) end = authorsEndLoose(text);
    if (end < 0) return null;
    const start = titleEnd(text, end);
    if (start < 0) return null;
    const m = text.slice(start).match(/^(.+?)(?=\s*\.(?:\s|$|\p{Lu})|\s*,\s|\s+\(|\s+(?:19|20)\d{2}\b|\s*;)/u);
    if (!m) return null;
    const j = m[1].trim();
    if (j.length < 2 || j.length > 90 || /\d{4}|doi|http/i.test(j)) return null;
    return [start, start + m[1].length];
}

// Shorten long author lists to "first 3, …, Hur J, …, last". Returns the text unchanged when unsure.
function shortenAuthors(text, threshold) {
    const { authors, end } = parseAuthors(text);
    if (end < 0 || authors.length < threshold) return text;
    const pi = authors.findIndex(a => /^Hur\s+JU?[*$†]*$/.test(a));
    if (pi < 0) return text;                                  // never hide the PI
    const keep = [...new Set([0, 1, 2, pi, authors.length - 1])].sort((a, b) => a - b);
    const out = [];
    keep.forEach((k, i) => { if (i > 0 && k - keep[i - 1] > 1) out.push('…'); out.push(authors[k]); });
    return out.join(', ') + '. ' + text.slice(end);
}

function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Citation text -> safe HTML. opts.journal: bold-italic the journal; opts.shortenThreshold: shorten authors.
function formatCitation(text, opts = {}) {
    if (!text) return '';
    const t = opts.shortenThreshold ? shortenAuthors(text, opts.shortenThreshold) : text;
    const r = opts.journal ? findJournal(t) : null;
    const html = r
        ? escapeHtml(t.slice(0, r[0])) + '<strong><em>' + escapeHtml(t.slice(r[0], r[1])) + '</em></strong>' + escapeHtml(t.slice(r[1]))
        : escapeHtml(t);
    // Author markers sit right after initials ("Hur J$", "Huang F*"); "HLA-B*57" style text is left alone
    return html.replace(/(\b\p{Lu}(?:[.\-]?\p{Lu}){0,3})([*$†]+)(?=[\s,.;)]|$)/gu, '$1<sup>$2</sup>');
}

if (typeof module !== 'undefined') module.exports = { parseAuthors, authorsEndLoose, titleEnd, findJournal, shortenAuthors, formatCitation };
