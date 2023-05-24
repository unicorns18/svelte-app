<script>
	import Header from './Header.svelte';
	import './styles.css';
	import { notifications, notify } from '../store.js';
</script>

<div class="app">
	<Header />

	<main>
		<slot />
	</main>

	<div id="notifications">
		{#each $notifications as notification (notification.id)}
			<div class="notification {notification.type}">
				<p>{notification.message}</p>
			</div>
		{/each}
	</div>
</div>

<style>
	@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css');

	.app {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	main {
		flex: 1;
		display: flex;
		flex-direction: column;
		padding: 1rem;
		width: 100%;
		max-width: 64rem;
		margin: 0 auto;
		box-sizing: border-box;
	}

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
