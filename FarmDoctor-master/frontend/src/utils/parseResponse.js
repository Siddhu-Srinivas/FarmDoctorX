/**
 * parseResponse — splits the AI's raw text on emoji section markers
 * and assigns each chunk to the correct field.
 *
 * The AI backend generates sections in this order:
 *   🔎 Problem
 *   🌿 Natural Solution (Organic)
 *   💊 Strong Medicine (Inorganic)
 *   💡 Success Tip
 *   🌾 Additional Tips
 */
export default function parseResponse(response) {
  const text = response.raw_answer || response.answer || JSON.stringify(response);
  const language = response.language || 'English';

  // ── 1. Define every section marker the AI might use ──────────────────────
  const SECTION_MARKERS = [
    { key: 'problem',        emojis: ['🔎', '📘'] },
    { key: 'organic',        emojis: ['🌿'] },
    { key: 'inorganic',      emojis: ['💊', '⚙️'] },
    { key: 'successTip',     emojis: ['💡', '🏆', '📌'] },
    { key: 'additionalTips', emojis: ['🌾', '✅', '📍', '🌱'] },
  ];

  // ── 2. Find every marker position in the text ─────────────────────────────
  // We scan the text for each emoji and record where it occurs and which key it maps to.
  const hits = [];                // { index, key }

  for (const { key, emojis } of SECTION_MARKERS) {
    for (const emoji of emojis) {
      let pos = 0;
      while (true) {
        const idx = text.indexOf(emoji, pos);
        if (idx === -1) break;
        hits.push({ index: idx, key, emoji });
        pos = idx + emoji.length;
      }
    }
  }

  if (hits.length === 0) {
    // No markers found — return raw text only
    return { problem: '', organic: '', inorganic: '', successTip: '', additionalTips: '', raw: text };
  }

  // Sort hits by position ascending
  hits.sort((a, b) => a.index - b.index);

  // ── 3. De-duplicate: keep only the FIRST hit for each key ─────────────────
  const seen  = new Set();
  const unique = [];
  for (const hit of hits) {
    if (!seen.has(hit.key)) {
      seen.add(hit.key);
      unique.push(hit);
    }
  }

  // ── 4. Slice the text between consecutive marker positions ────────────────
  const sections = { problem: '', organic: '', inorganic: '', successTip: '', additionalTips: '', raw: text };

  for (let i = 0; i < unique.length; i++) {
    const start = unique[i].index;
    const end   = unique[i + 1] ? unique[i + 1].index : text.length;
    const key   = unique[i].key;

    // Raw chunk for this section (including its own header line)
    const chunk = text.slice(start, end);

    // Strip the header line itself (the first line that contains the emoji + label)
    const lines      = chunk.split('\n');
    const bodyLines  = lines.slice(1);           // everything after the header line

    sections[key] = bodyLines.join('\n').trim();
  }

  sections.language = language;
  return sections;
}
