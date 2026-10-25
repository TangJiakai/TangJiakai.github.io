// Embeds search text with bge-m3 on Cloudflare Workers AI for the homepage's semantic search.
// The site sends one query at a time; scripts/update_embeddings.py sends paper texts in batches.
const MODEL = '@cf/baai/bge-m3';
const MAX_TEXTS = 40;
const MAX_CHARS = 2400;
const ALLOWED_ORIGINS = ['https://tangjiakai.github.io', 'http://127.0.0.1:8790', 'http://localhost:8790'];

const corsHeaders = origin => ({
  'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0],
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Max-Age': '86400',
  Vary: 'Origin',
});

const reply = (body, status, origin) => new Response(JSON.stringify(body), {
  status,
  headers: {'Content-Type': 'application/json', ...corsHeaders(origin)},
});

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    if (request.method === 'OPTIONS') return new Response(null, {status: 204, headers: corsHeaders(origin)});
    if (request.method !== 'POST') return reply({error: 'Use POST with {"texts": [...]}'}, 405, origin);
    // Browsers always send Origin on cross-site POST; requests without one come from the batch script.
    if (origin && !ALLOWED_ORIGINS.includes(origin)) return reply({error: 'Origin not allowed'}, 403, origin);

    let texts;
    try {
      ({texts} = await request.json());
    } catch {
      return reply({error: 'Invalid JSON'}, 400, origin);
    }
    if (!Array.isArray(texts) || !texts.length || texts.length > MAX_TEXTS || texts.some(text => typeof text !== 'string' || !text.trim())) {
      return reply({error: `Send 1 to ${MAX_TEXTS} non-empty texts`}, 400, origin);
    }
    const result = await env.AI.run(MODEL, {text: texts.map(text => text.slice(0, MAX_CHARS))});
    return reply({model: MODEL, vectors: result.data}, 200, origin);
  },
};
