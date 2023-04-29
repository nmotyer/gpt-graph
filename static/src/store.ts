import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';

// Create a writable store for messages
export const messagesStore: Writable<object[]> = writable<object[]>([]);
export const tableStore: Writable<object[]> = writable<object[]>([]);