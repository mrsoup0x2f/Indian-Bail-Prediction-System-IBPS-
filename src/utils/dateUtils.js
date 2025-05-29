// src/utils/dateUtils.js - Utility functions for date formatting
export function formatTimestamp(date) {
    if (!date) return '';

    // Format: "Today, 2:30 PM" or "May 15, 2:30 PM"
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();

    const timeOptions = { hour: 'numeric', minute: 'numeric' };
    const formattedTime = date.toLocaleTimeString(undefined, timeOptions);

    if (isToday) {
        return `Today, ${formattedTime}`;
    } else {
        const dateOptions = { month: 'short', day: 'numeric' };
        const formattedDate = date.toLocaleDateString(undefined, dateOptions);
        return `${formattedDate}, ${formattedTime}`;
    }
}
