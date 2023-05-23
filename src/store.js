import { writable } from "svelte/store";

export const searchData = writable([]);
export const notifications = writable([]);

let notificationId = 0;

export function notify(message, type)
{
    notifications.update(all => {
        return [...all, { id: notificationId++, message, type }];
    });

    setTimeout(() => {
        notifications.update(all => {
            return all.filter(n => n.id !== notificationId-1);
        });
    }, 5000);
}
