import { error, json } from '@sveltejs/kit';

/** @type {import('./$types').RequestHandler} */
export async function GET({ url }) {
	const imdbID = url.searchParams.get('id');
	console.log(url);

	if (!imdbID) {
		throw error(400, 'No ID Provided');
	}

	const API_URL = new URL(`http://206.81.16.199:1337/search_id`);

	API_URL.searchParams.append('imdb_id', imdbID);

	const apiRes = await fetch(API_URL.href, {
		method: 'post',
		headers: {
			apikey: `${process.env.API_KEY}`
		}
	});

	const res = await apiRes.json();

	console.log(API_URL.href);
	console.log(res);

	return json(res);
}
