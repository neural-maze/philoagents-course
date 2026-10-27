// Both services used to resolve the API origin on their own; the session fetch needs the
// same answer, so the rules live here once.
export function httpBaseUrl() {
    if (window.PHILOAGENTS_API_URL) {
        return window.PHILOAGENTS_API_URL;
    }

    if (window.location.protocol === 'https:') {
        const currentHostname = window.location.hostname;
        return `https://${currentHostname.replace('8080', '8000')}`;
    }

    return 'http://localhost:8000';
}

export function wsBaseUrl() {
    if (window.PHILOAGENTS_WS_URL) {
        return window.PHILOAGENTS_WS_URL;
    }

    if (window.location.protocol === 'https:') {
        const currentHostname = window.location.hostname;
        return `wss://${currentHostname.replace('8080', '8000')}`;
    }

    return 'ws://localhost:8000';
}
