<script>
	// import Header from './Header.svelte';

	import Sidebar from '../components/Sidebar.svelte';

	import './styles.css';
	import { notifications, notify } from '../store.js';
</script>

<div class="app">
	<!-- <Header /> -->
	<Sidebar />
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
		min-height: 100vh;
		width: 100%;
	}

	main {
		flex-grow: 1;
		padding: 16px;
		display: flex;
		flex-direction: column;
		padding: 1rem;
		width: 80%;
		margin: 0 auto;
		box-sizing: border-box;
		height: 400vh;
		margin-left: 16%;
		background-color: orange;
		overflow: none;
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
