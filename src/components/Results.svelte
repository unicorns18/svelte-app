<script>
    import { searchData } from "../store.js";

    let data;
    const unsubscribe = searchData.subscribe(value => {
        data = value;
        console.log("data: ", data);
    });

    unsubscribe();
</script>

{#if data}
    {#each data as item (item.title)}
        <div>
            <h2>{item.title}</h2>
            <p>Quality: {item.quality}</p>
            <p>Score: {item.score}</p>
            <p>Size: {item.size}</p>
            <p>Source: {item.source}</p>
        </div>
    {/each}
{:else}
    <p>No data available.</p>
{/if}