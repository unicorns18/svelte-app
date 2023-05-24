import { writable } from 'svelte/store';

export const searchData = writable([]);
export const notifications = writable([]);

let notificationId = 0;

/**
 * @param {string} message
 * @param {string} type
 */
export function notify(message, type) {
	// @ts-ignore
	notifications.update((all) => {
		return [...all, { id: notificationId++, message, type }];
	});

	setTimeout(() => {
		notifications.update((all) => {
			// @ts-ignore
			return all.filter((n) => n.id !== notificationId - 1);
		});
	}, 5000);
}
