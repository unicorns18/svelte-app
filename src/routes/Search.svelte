<script>
	import { notify, searchData } from '../store.js';
	import { onMount } from 'svelte';
	let searchInput = '';
	/**
	 * @type {any[]}
	 */
	let searchResults = [];
	/**
	 * @type {any[]}
	 */
	let searchHistory = [];
	/**
	 * @type {any}
	 */
	let selectedResult = null;

	/**
	 * @param {{ preventDefault: () => void; } | undefined} [event]
	 */
	async function handleSearch(event) {
		if (event) event.preventDefault();
		console.log(searchInput);

		if (!searchInput.trim()) {
			console.log('Search term cannot be empty');
			return;
		}

		try {
			const response = await fetch('http://localhost:6942/search', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					search_term: searchInput
				})
			});

			if (!response.ok) {
				const data = await response.json();
				console.log('(handleSearch) error: ', data);
				notify('error', data.error);
				return;
			}

			const data = await response.json();
			notify('success', 'Search successful');
			console.log('(handleSearch) data: ', data);
			searchResults = data;
		} catch (error) {
			console.log('Error: ', error);
		}
	}

	/**
	 * @param {{ title: any; id: any; }} result
	 */
	async function selectResult(result) {
		try {
			const response = await fetch('http://127.0.0.1:69420/select', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					title: result.title, // Result's title
					id: result.id // Result's ID
				})
			});

			if (!response.ok) {
				const data = await response.json();
				console.log('(selectResult) error: ', data);
				notify('error', data.error);
				return;
			}

			const data = await response.json();
			notify('success', 'Result selected');
			console.log('(selectResult) data: ', data);
			selectedResult = { result: result, imdb_id: data.imdb_id };
		} catch (error) {
			console.log('Error: ', error);
		}
	}

	/**
	 * @param {any} imdb_id
	 */
	async function searchForTitle(imdb_id) {
		try {
			const response = await fetch('http://127.0.0.1:6942/search_for_title', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					imdb_id: imdb_id
				})
			});

			if (!response.ok) {
				const data = await response.json();
				console.log('(searchForTitle) error: ', data);
				notify('error', data.error);
				return;
			}

			const data = await response.json();
			notify('success', 'Search for title successful');
			console.log('Server response:', data);
			searchData.set(data);
			// navigate('/results');
		} catch (error) {
			console.log('Error: ', error);
		}
	}

	/**
	 * @param {string} search_term
	 */
	async function handleHistorySearch(search_term) {
		searchInput = search_term;
		await handleSearch();
	}

	async function fetchSearchHistory() {
		try {
			const response = await fetch('http://127.0.0.1:6942/retrieve_search_history');

			if (!response.ok) {
				const data = await response.json();
				console.log('(fetchSearchHistory) error: ', data);
				notify('error', data.error);
				return;
			}

			const data = await response.json();
			notify('success', 'Search history retrieved');
			console.log('(fetchSearchHistory) data:', data);
			searchHistory = data;
		} catch (error) {
			console.log('Error: ', error);
		}
	}

	onMount(() => {
		// fetchSearchHistory();
	});
</script>

<div class="container">
	<div id="searchHistoryContainer">
		<h2>Search history</h2>
		{#each searchHistory.filter((item, index) => searchHistory.findIndex((i) => i.search_term === item.search_term) === index) as item (item._id)}
			<div class="searchHistoryItem">
				<h4>{item.search_term}</h4>
				<button class="historyButton" on:click={() => handleHistorySearch(item.search_term)}
					>Search again</button
				>
			</div>
		{/each}
	</div>
	<div id="searchPanel">
		<form id="searchForm" on:submit|preventDefault={handleSearch}>
			<input type="text" id="searchBox" placeholder="Search..." bind:value={searchInput} />
			<button type="submit">Search</button>
		</form>
	</div>
	<div id="searchResultsPanel">
		<div id="searchResultsContainer">
			{#each searchResults as result (result.id)}
				<!-- assumes each result has an ID property -->
				<div
					class="result"
					on:click={() => selectResult(result)}
					on:keydown={(event) => event.key === 'Enter' && selectResult(result)}
				>
					<h2>{result.title}</h2>
					<p>{result.overview}</p>
					<p>Release date: {result.release_date}</p>
					{#if selectedResult && selectedResult.result.id == result.id}
						<img
							class="poster"
							src="https://image.tmdb.org/t/p/w500{result.poster_path}"
							alt="{result.title} poster"
						/>
						<button
							class="searchButton"
							on:click|stopPropagation={() => searchForTitle(selectedResult.imdb_id)}
							>Search for this title</button
						>
					{/if}
				</div>
			{/each}
		</div>
	</div>
</div>

<style>
	@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap');

	.container {
		display: flex;
		flex-direction: row;
		justify-content: flex-start;
		align-items: stretch;
		max-width: 600px;
		margin: 0 auto;
		padding: 20px;
		background-color: #1a1a1a;
		border-radius: 10px;
		box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.75);
		transform: translateY(50px);
	}

	#searchBox {
		flex-grow: 1;
		margin-right: 10px;
		border: none;
		background-color: #0a0a0a;
		color: #fff;
		border-radius: 5px;
		box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.75);
		outline: none;
		font-size: 1em;
		padding: 15px;
		transition: background-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
	}

	#searchBox::placeholder {
		color: #777;
	}

	#searchBox:focus {
		background-color: #0a0a0a;
		box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.75), 0px 0px 10px 0px #0a0a0a;
		outline: 2px solid #111;
	}

	button {
		padding: 10px 20px;
		border: none;
		background-color: #0a0a0a;
		color: #fff;
		border-radius: 5px;
		box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.75);
		cursor: pointer;
		transition: background-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
	}

	button:hover {
		background-color: #333333;
		transform: scale(1.1);
	}

	#searchResultsContainer {
		margin-top: 20px;
	}

	.result {
		background-color: #222;
		border-radius: 5px;
		padding: 10px;
		margin-bottom: 10px;
		cursor: pointer;
		transition: background-color 0.3s ease;
	}

	.result:hover {
		background-color: #333;
		transition: none;
	}

	.result:focus {
		outline: none;
		background-color: #333;
	}

	.result h2 {
		margin-top: 0;
		color: #fff;
		font-size: 1.2em;
		line-height: 1.5;
	}

	.result p {
		margin-bottom: 0;
		color: #aaa;
		line-height: 1.5;
	}

	.poster {
		width: 250px;
		height: auto;
	}

	/* Search history styling */
	#searchHistoryContainer {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
		flex: 0 0 200px;
		position: absolute;
		top: 0;
		left: 0;
		width: 200px;
		height: auto;
		padding: 20px;
		background-color: #1a1a1a;
		border-radius: 10px;
		box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.75);
		overflow-y: auto;
		transform: translate(-24vw, 0);
		transition: transform 0.3s ease;
	}

	#searchHistoryContainer::-webkit-scrollbar {
		display: none;
	}

	.searchHistoryItem {
		background-color: #222;
		border-radius: 5px;
		padding: 10px;
		margin-bottom: 10px;
		cursor: pointer;
		transition: background-color 0.3s ease;
	}

	.searchHistoryItem:hover {
		background-color: #333;
		transition: none;
	}

	.searchHistoryItem h4 {
		margin: 0;
		color: #fff;
	}

	.historyButton {
		margin-top: 10px;
		border: none;
		background-color: #0a0a0a;
		color: #fff;
		border-radius: 5px;
		box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.75);
		cursor: pointer;
		transition: background-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
	}

	@media (max-width: 600px) {
		.container {
			padding: 10px;
		}

		#searchForm {
			flex-direction: column;
		}

		#searchBox {
			margin-right: 0;
			margin-bottom: 10px;
		}
	}
</style>
