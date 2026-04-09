export async function onRequestPost(context) {
    const { id } = await context.request.json();
    await context.env.DB.prepare("DELETE FROM songs WHERE id = ?").bind(id).run();
    return new Response(JSON.stringify({ success: true }), {
        headers: { "Content-Type": "application/json" },
    });
}
