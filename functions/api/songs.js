export async function onRequestGet(context) {
    const { results } = await context.env.DB.prepare("SELECT * FROM songs ORDER BY title ASC").all();
    return new Response(JSON.stringify(results), {
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
}
