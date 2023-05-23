<script>
	import { Router, Route } from 'svelte-routing';
	// TODO: move notifications into store.js
	import { notifications, notify } from './store.js';
	import Search from "./components/Search.svelte";
	import Results from './components/Results.svelte';
	export let name;
</script>

<Router>
	<Route path="/" component={Search} />
	<Route path="/results" component={Results} />
</Router>

<div id="notifications">
	{#each $notifications as notification (notification.id)}
		<div class="notification {notification.type}">
			<p>{notification.message}</p>
		</div>
	{/each}
</div>

<style>
	#notifications {
		position: fixed;
		top: 10px;
		right: 10px;
		z-index: 100;
	}

	.notification {
		margin-bottom: 10px;
		padding: 10px;
		border-radius: 5px;
		color: white;
	}

	.notification.error {
		background-color: #f44336;
	}

	.notification.success {
		background-color: #4caf50;
	}

	.notification.info {
		background-color: #2196f3;
	}
</style>