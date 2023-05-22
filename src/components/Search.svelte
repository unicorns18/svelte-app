<script>
	import { navigate } from 'svelte-routing';
    import { searchData } from '../store.js';
    import { onMount } from "svelte";
    let searchInput = '';
    let searchResults = [];
    let selectedResult = null;
    
    async function handleSearch(event)
    {
        event.preventDefault();
        console.log(searchInput);

        try 
        {
            const response = await fetch('http://127.0.0.1:5000/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    search_term: searchInput
                }),
            });

            if (!response.ok)
            {
                throw new Error("Network response was not ok, error code: " + response.status);
            }

            const data = await response.json();
            console.log("(handleSearch) data: ", data);
            searchResults = data;
        }  catch (error)
        {
            console.log("Error: ", error);
        }
    }

    async function selectResult(result)
    {
        try
        {
            const response = await fetch('http://127.0.0.1:5000/select', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: result.title, // Result's title
                    id: result.id // Result's ID
                }),
            });

            if (!response.ok)
            {
                throw new Error("Network response was not ok, error code: " + response.status);
            }

            const data = await response.json();
            console.log("(selectResult) data: ", data);
            selectedResult = { result: result, imdb_id: data.imdb_id };
        } catch (error)
        {
            console.log("Error: ", error);
        }
    }

    async function searchForTitle(imdb_id)
    {
        try
        {
            const response = await fetch('http://127.0.0.1:5000/search_for_title', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    imdb_id: imdb_id
                }),
            });

            if (!response.ok)
            {
                throw new Error("Network response was not ok, error code: " + response.status);
            }

            const data = await response.json();
            console.log("Server response:", data);
            searchData.set(data);
            navigate('/results');
        } catch (error)
        {
            console.log("Error: ", error);
        }
    }
</script>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap');

    .container {
        display: flex;
        flex-direction: column;
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
        background-color: #1a1a1a;
        border-radius: 10px;
        box-shadow: 0px 0px 10px 0px rgba(0,0,0,0.75);
        transform: translateY(50px);
    }

    #searchBox {
        flex-grow: 1;
        margin-right: 10px;
        padding: 10px;
        border: none;
        background-color: #0a0a0a;
        color: #fff;
        border-radius: 5px;
        box-shadow: 0px 0px 10px 0px rgba(0,0,0,0.75);
    }

    button {
        padding: 10px 20px;
        border: none;
        background-color: #0a0a0a;
        color: #fff;
        border-radius: 5px;
        box-shadow: 0px 0px 10px 0px rgba(0,0,0,0.75);
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.3s ease;
    }

    button:hover {
        background-color: #222222;
        transform: scale(1.1);
    }

    #searchResultsContainer {
        margin-top: 20px;
    }

    #searchResults {
        list-style-type: none;
        padding: 20px;
        max-width: 600px;
        margin: 0 auto;
        margin-top: 50px;
        background-color: #1a1a1a;
        border-radius: 10px;
        box-shadow: 0px 0px 10px 0px rgba(0,0,0,0.75);
        transform: translateY(50px);
    }

    #searchResults li {
        display: flex;
        position: relative;
        align-items: center;
        gap: 10px;
        padding: 10px;
        background-color: #121212;
        margin-bottom: 10px;
        cursor: pointer;
        border-radius: 5px;
        transition: background-color 0.3s ease;
    }

    #searchResults li:hover {
        background-color: #222222;
        transition: none;
    }

    #searchResults img {
        width: 50px;
        height: 75px;
        object-fit: cover;
        border-radius: 5px;
    }

    #searchResults .details {
        flex-grow: 1;
    }

    .titleElement {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        width: 80%;
    }

    .typeElement {
        position: absolute;
        top: 16px;
        left: 7px;
        font-size: 0.8em;
        color: #555;
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
    }

    .result p {
        margin-bottom: 0;
        color: #aaa;
    }

    .poster {
        width: 250px;
        height: auto;
    }

    @media (max-width: 600px) {
        .container {
            padding: 10px;
        }

        #searchForm {
            flex-direction: column;
        }

        #searchResults {
            max-width: 100%;
        }

        #searchBox {
            margin-right: 0;
            margin-bottom: 10px;
        }
    }
</style>

<div class="container">
    <div id="searchPanel">
        <form id="searchForm" on:submit|preventDefault={handleSearch}>
            <input type="text" id="searchBox" placeholder="Search..." bind:value={searchInput}>
            <button type="submit">Search</button>
        </form>
    </div>
    <div id="searchResultsContainer">
        {#each searchResults as result (result.id)} <!-- assumes each result has an ID property -->
            <div class="result" on:click={() => selectResult(result)} on:keydown={(event) => event.key === 'Enter' && selectResult(result)}>
                <h2>{result.title}</h2>
                <p>{result.overview}</p>
                <p>Release date: {result.release_date}</p>
                {#if selectedResult && selectedResult.result.id == result.id}
                    <img class="poster" src=https://image.tmdb.org/t/p/w500{result.poster_path} alt="{result.title} poster">
                    <button class="searchButton" on:click|stopPropagation={() => searchForTitle(selectedResult.imdb_id)}>Search for this title</button>
                {/if}
            </div>
        {/each}
    </div>
</div>