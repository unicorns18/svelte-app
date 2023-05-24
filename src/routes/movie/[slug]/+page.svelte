<script>
	/** @type {import('./$types').PageData} */
	export let data;

	console.log(data);
</script>

<h1>{data.slug}</h1>
<span>{JSON.stringify(data.json, null, 4)}</span>
