<script>
	import { Router, Route } from 'svelte-routing';
	import Search from "./components/Search.svelte";
	import Results from './components/Results.svelte';
	export let name;
</script>

<Router>
	<Route path="/" component={Search} />
	<Route path="/results" component={Results} />
</Router>