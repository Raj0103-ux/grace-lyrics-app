/**
 * GGGM CLOUDFLARE MASTER WORKER (V2 - CORS UNLOCKED)
 * -----------------------------------------------
 */

const ADMIN_PASSWORD = "admin";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*", // Allows access from any domain (including your GitHub link)
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS, DELETE",
  "Access-Control-Allow-Headers": "Content-Type",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Handle Pre-flight (CORS) - This stops the "Uploading..." hang
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS_HEADERS });
    }

    // 1. API - Get Songs
    if (url.pathname === "/songs" && request.method === "GET") {
      const { results } = await env.DB.prepare("SELECT * FROM songs ORDER BY title ASC").all();
      return new Response(JSON.stringify(results), {
        headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
      });
    }

    // 2. API - Upload Songs (Single or Bulk)
    if (url.pathname === "/upload" && request.method === "POST") {
      const data = await request.json();
      const { title, language, lyrics, number } = data;
      const id = Date.now().toString() + Math.random().toString(36).substr(2, 5);
      
      await env.DB.prepare(
        "INSERT INTO songs (id, title, language, lyrics, number) VALUES (?, ?, ?, ?, ?)"
      ).bind(id, title, language, lyrics, number).run();

      return new Response(JSON.stringify({ success: true, id }), {
        headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
      });
    }

    // 3. API - Delete Songs
    if (url.pathname === "/delete" && request.method === "POST") {
      const { id } = await request.json();
      await env.DB.prepare("DELETE FROM songs WHERE id = ?").bind(id).run();
      return new Response(JSON.stringify({ success: true }), {
        headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
      });
    }

    return new Response("GGGM API GATEWAY V2", { status: 200, headers: CORS_HEADERS });
  },
};
