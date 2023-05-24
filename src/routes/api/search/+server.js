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

async function getMovieInfo(choice) {
	const [tmdbRes, mdbRes] = await Promise.all([
		getTMDBData({
			type: 'MOVIE',
			id: choice.id
		}),
		getMDBData({
			tm: choice.id
		})
	]);

	console.log(mdbRes, tmdbRes);

	const imdbRating = mdbRes.ratings.find((rating) => rating.source === 'imdb');
	const metacriticRating = mdbRes.ratings.find((rating) => rating.source === 'metacritic');
	const traktRating = mdbRes.ratings.find((rating) => rating.source === 'trakt');
	const tomatoesRating = mdbRes.ratings.find((rating) => rating.source === 'tomatoes');
	const tmdbRating = mdbRes.ratings.find((rating) => rating.source === 'tmdb');
	const letterboxdRating = mdbRes.ratings.find((rating) => rating.source === 'letterboxd');

	const directorCredits = tmdbRes.credits.crew.filter((credit) => credit.job === 'Director');

	const getDirectors = () => {
		const directors = new Set();
		directorCredits.forEach((credit) => {
			directors.add(credit.name);
		});
		return [...directors];
	};

	const writerCredits = tmdbRes.credits.crew.filter(
		(credit) => credit.job === 'Screenplay' || credit.job === 'Story'
	);

	const getWriters = () => {
		const writers = new Set();
		writerCredits.forEach((credit) => {
			writers.add(credit.name);
		});
		return [...writers];
	};

	const editorCredits = tmdbRes.credits.crew.filter((credit) => credit.job === 'Editor');

	const getEditors = () => {
		const editors = new Set();
		editorCredits.forEach((credit) => {
			editors.add(credit.name);
		});
		return [...editors];
	};

	const directorPhotography = tmdbRes.credits.crew.find(
		(credit) => credit.job === 'Director of Photography'
	)
		? tmdbRes.credits.crew.find((credit) => credit.job === 'Director of Photography').name
		: 'n/A';

	const topCastCredits =
		tmdbRes.credits.cast.length > 6 ? tmdbRes.credits.cast.slice(0, 6) : tmdbRes.credits.cast;

	const getTopCast = () => {
		const topCast = new Set();
		topCastCredits.forEach((credit) => {
			topCast.add(credit.name);
		});
		return [...topCast];
	};

	const getProductionCompanies = () => {
		const companies = new Set();
		tmdbRes.production_companies.forEach((company) => {
			companies.add(company.name);
		});
		return [...companies];
	};

	const getGenres = () => {
		const genres = new Set();
		tmdbRes.genres.forEach((genre) => {
			genres.add(genre.name);
		});
		return [...genres];
	};

	return {
		title: mdbRes.title ? mdbRes.title : 'n/A',
		year: mdbRes.year ? mdbRes.year : 'n/A',
		description: mdbRes.description ? mdbRes.description : 'n/A',
		runtime: mdbRes.runtime ? mdbRes.runtime : 'n/A',

		filename: replaceIllegalFileNameCharactersInString(`${mdbRes.title} (${mdbRes.year})`),

		poster: mdbRes.poster ? mdbRes.poster : 'n/A',
		backdrop: mdbRes.backdrop ? mdbRes.backdrop : 'n/A',

		language: mdbRes.language ? mdbRes.language.toUpperCase() : 'n/A',
		country: mdbRes.country ? mdbRes.country.toUpperCase() : 'n/A',

		imdbid: mdbRes.imdbid ? mdbRes.imdbid : 'n/A',
		tmdbid: mdbRes.tmdbid ? mdbRes.tmdbid : 'n/A',
		traktid: mdbRes.traktid ? mdbRes.traktid : 'n/A',

		imdbRating: imdbRating.score ? imdbRating.score : 'n/A',
		metacriticRating: metacriticRating.score ? metacriticRating.score : 'n/A',
		metacriticSlug: metacriticRating.url ? metacriticRating.url : 'n/A',
		tmdbRating: tmdbRating.score ? tmdbRating.score : 'n/A',
		traktRating: traktRating.score ? traktRating.score : 'n/A',
		tmdbRating: traktRating.score ? traktRating.score : 'n/A',
		tomatoesRating: tomatoesRating.score ? tomatoesRating.score : 'n/A',
		tomatoesSlug: tomatoesRating.url ? tomatoesRating.url : 'n/A',
		letterboxdRating: letterboxdRating.score ? letterboxdRating.score : 'n/A',
		letterboxdSlug: letterboxdRating.url ? letterboxdRating.url : 'n/A',
		mdbScore: mdbRes.score ? mdbRes.score : 'n/A',

		budget: tmdbRes.budget ? tmdbRes.budget : 'n/A',
		revenue: tmdbRes.revenue ? tmdbRes.revenue : 'n/A',

		genres: linkifyList(getGenres()),
		productionCompanies: linkifyList(getProductionCompanies()),

		directors: linkifyList(getDirectors()),
		writers: linkifyList(getWriters()),
		editors: linkifyList(getEditors()),
		directorPhotography: linkifyList([directorPhotography]),
		topCast: linkifyList(getTopCast())
	};
}

function minTwoDigits(n) {
	return (n < 10 ? '0' : '') + n;
}

async function getMDBData(data) {
	const API_URL = new URL(`https://mdblist.com/api/`);

	API_URL.searchParams.append('apikey', MDB_API_KEY);

	for (const [key, value] of Object.entries(data)) {
		API_URL.searchParams.append(key, value);
	}

	const apiRes = await request({
		url: API_URL.href,
		method: 'GET',
		cache: 'no-cache',
		headers: {
			'Content-Type': 'application/json'
		}
	});
	console.log('URL: ', API_URL);
	return JSON.parse(apiRes);
}

function linkifyList(list, type) {
	if (list.length === 0) return '';

	if (type === 'genres') {
		if (list.length === 1) return `[[${list[0]} (Genre)]]`;
		return list.map((item) => `[[${item.trim()} (Genre)]]`).join(', ');
	}

	if (list.length === 1) return `[[${list[0]}]]`;

	return list.map((item) => `[[${item.trim()}]]`).join(', ');
}
function replaceIllegalFileNameCharactersInString(string) {
	return string.replace(/[\\,#%&\{\}\/*<>?$\'\":@]*/g, '');
}
