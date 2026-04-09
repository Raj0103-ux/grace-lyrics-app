export async function onRequestPost(context) {
    const data = await context.request.json();
    const { title, language, lyrics, number } = data;
    const id = Date.now().toString();
    
    await context.env.DB.prepare(
        "INSERT INTO songs (id, title, language, lyrics, number) VALUES (?, ?, ?, ?, ?)"
    ).bind(id, title, language, lyrics, number).run();

    return new Response(JSON.stringify({ success: true, id }), {
        headers: { "Content-Type": "application/json" },
    });
}
