<script>
	// @ts-nocheck

	import { searchData } from '../../store.js';

	/**
	 * @type {never[]}
	 */
	let data;
	const unsubscribe = searchData.subscribe((value) => {
		data = value;
		console.log('data: ', data);
	});

	unsubscribe();
</script>

{#if data}
	{#each data as item (item.title)}
		<div class="data-container">
			<div>
				<h2>{item.title}</h2>
			</div>
			<div>
				<p>Quality: {item.quality}</p>
			</div>
			<div>
				<p>Score: {item.score}</p>
			</div>
			<div>
				<p>Size: {item.size}</p>
			</div>
			<div>
				<p>Source: {item.source}</p>
			</div>
		</div>
	{/each}
{:else}
	<p>No data available.</p>
{/if}

<style>
	.data-container {
		display: grid;
		grid-template-columns: repeat(5, 1fr);
		gap: 10px;
		align-items: center;
		border-bottom: 1px solid #333;
		padding: 10px;
		background-color: #1a1a1a;
		border-radius: 10px;
		box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.75);
		margin-bottom: 10px;
	}

	.data-container > div {
		display: flex;
		flex-direction: column;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.data-container > div > h2 {
		margin: 0;
		font-size: 1em;
		color: #fff;
	}

	.data-container > div > p {
		margin: 0;
		font-size: 0.8em;
		color: #aaa;
	}

	.data-container:nth-child(even) {
		background-color: #222;
	}
</style>
