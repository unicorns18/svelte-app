// @ts-nocheck
import { error, json } from '@sveltejs/kit';
import * as dotenv from 'dotenv';
dotenv.config();

const TMDB_API_URL = 'https://www.omdbapi.com/';
const OMDB_API_URL = 'https://www.omdbapi.com/';
const TMDB_API_KEY = process.env.TMDB_API_KEY;
const MDB_API_KEY = '';

/** @type {import('./$types').RequestHandler} */
export async function GET({ url }) {
	const query = url.searchParams.get('query');
	// console.log(url);

	if (!query) {
		throw error(400, 'Invalid Query');
	}

	const { results } = await getTMDBData({
		type: 'SEARCH_MOVIE',
		query: query
	});

	return json(results);
}

async function getTMDBData({ type, id, season, ep, ...data }) {
	console.log(type, id, season, ep);
	const API_URL = new URL(`https://api.themoviedb.org/3/${getURLByType(type, id, season, ep)}`);

	API_URL.searchParams.append('api_key', TMDB_API_KEY);

	for (const [key, value] of Object.entries(data)) {
		API_URL.searchParams.append(key, value);
	}

	if (type != 'SEARCH') {
		API_URL.searchParams.append('append_to_response', 'credits');
	}
	console.log('URL: ', API_URL);
	const apiRes = await fetch(API_URL.href);

	return apiRes.json();
}

/**
 * @param {any} type
 * @param {any} id
 * @param {any} season
 * @param {any} ep
 */
function getURLByType(type, id, season, ep) {
	switch (type) {
		case 'SEARCH':
			return 'search/multi';
		case 'SEARCH_MOVIE':
			return 'search/movie';
		case 'SEARCH_TV':
			return 'search/tv';
		case 'MOVIE':
			return `movie/${id}`;
		case 'TV':
			return `tv/${id}`;
		case 'SEASON':
			return `tv/${id}/season/${season}`;
		case 'EPISODE':
			return `tv/${id}/season/${season}/episode/${ep}`;
	}
}
