/**
 * GGGM CLOUDFLARE MASTER WORKER
 * ----------------------------
 * This worker hosts your Admin Dashbord and the API for the mobile app.
 */

const ADMIN_PASSWORD = "admin"; // <--- CHANGE THIS TO YOUR SECURE PASSWORD

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 1. API - Get Songs for Mobile App
    if (url.pathname === "/songs" && request.method === "GET") {
      const { results } = await env.DB.prepare("SELECT * FROM songs").all();
      return new Response(JSON.stringify(results), {
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      });
    }

    // 2. ADMIN DASHBOARD - HTML UI
    if (url.pathname === "/admin") {
      return new Response(adminHtml(), {
        headers: { "Content-Type": "text/html" },
      });
    }

    // 3. API - Upload Songs
    if (url.pathname === "/upload" && request.method === "POST") {
      const data = await request.json();
      const { title, language, lyrics, number } = data;
      const id = Date.now().toString();
      
      await env.DB.prepare(
        "INSERT INTO songs (id, title, language, lyrics, number) VALUES (?, ?, ?, ?, ?)"
      ).bind(id, title, language, lyrics, number).run();

      return new Response(JSON.stringify({ success: true, id }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    // 4. API - Delete Songs
    if (url.pathname === "/delete" && request.method === "POST") {
      const { id } = await request.json();
      await env.DB.prepare("DELETE FROM songs WHERE id = ?").bind(id).run();
      return new Response(JSON.stringify({ success: true }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    return new Response("GGGM API GATEWAY", { status: 200 });
  },
};

function adminHtml() {
  return `
  <!DOCTYPE html>
  <html>
  <head>
    <title>GGGM Admin Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body { background: #F4F6F9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
      .navbar { background: #3F51B5; color: white; margin-bottom: 30px; }
      .card { border-radius: 15px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
      .btn-primary { background: #3F51B5; border: none; }
    </style>
  </head>
  <body>
    <nav class="navbar"><div class="container"><strong>GGGM Master Cloud Panel</strong></div></nav>
    <div class="container">
      <div id="login-sec">
        <div class="card p-4 mx-auto" style="max-width: 400px;">
          <h3>Admin Login</h3>
          <input type="password" id="pass" class="form-control mb-3" placeholder="Enter Password">
          <button class="btn btn-primary w-100" onclick="checkLogin()">Login</button>
        </div>
      </div>

      <div id="dash-sec" style="display:none;">
        <div class="row">
          <div class="col-md-5">
            <div class="card p-4 mb-4">
              <h4>Add New Song</h4>
              <input type="text" id="title" class="form-control mb-2" placeholder="Song Title">
              <select id="lang" class="form-select mb-2">
                <option value="tamil">Tamil</option>
                <option value="telugu">Telugu</option>
              </select>
              <textarea id="lyrics" class="form-control mb-2" rows="10" placeholder="Paste Lyrics Here..."></textarea>
              <button class="btn btn-primary w-100" onclick="upload()">UPLOAD TO CLOUD</button>
              <div id="status" class="mt-2 text-center"></div>
            </div>
          </div>
          <div class="col-md-7">
             <div class="card p-4">
               <h4>Manage Cloud Songs</h4>
               <div id="song-list">Loading...</div>
             </div>
          </div>
        </div>
      </div>
    </div>

    <script>
      let pass = "";
      function checkLogin() {
        const p = document.getElementById('pass').value;
        if (p === "admin") { // Replace with actual logic if needed
          document.getElementById('login-sec').style.display = 'none';
          document.getElementById('dash-sec').style.display = 'block';
          loadSongs();
        } else { alert("Wrong password!"); }
      }

      async function upload() {
        const data = {
          title: document.getElementById('title').value,
          language: document.getElementById('lang').value,
          lyrics: document.getElementById('lyrics').value,
          number: ""
        };
        const res = await fetch('/upload', { method: 'POST', body: JSON.stringify(data) });
        if (res.ok) { 
           alert("Success!"); 
           document.getElementById('title').value = "";
           document.getElementById('lyrics').value = "";
           loadSongs();
        }
      }

      async function loadSongs() {
        const res = await fetch('/songs');
        const songs = await res.json();
        const list = document.getElementById('song-list');
        list.innerHTML = songs.map(s => \`
          <div class="d-flex justify-content-between border-bottom py-2">
            <div><strong>\${s.title}</strong><br><small class="text-muted">\${s.language}</small></div>
            <button class="btn btn-sm btn-outline-danger" onclick="delSong('\${s.id}')">Delete</button>
          </div>
        \`).join('');
      }

      async function delSong(id) {
        if(!confirm("Delete forever?")) return;
        await fetch('/delete', { method: 'POST', body: JSON.stringify({id}) });
        loadSongs();
      }
    </script>
  </body>
  </html>
  `;
}
