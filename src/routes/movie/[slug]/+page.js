export async function load({ fetch, params }) {
	let data = await fetch(`/api/movie?query=${params.slug}`);
	data = await data.json();
	return {
		slug: params.slug,
		json: data
	};
}
