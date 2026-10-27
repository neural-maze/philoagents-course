import { getPlayerId, setPlayerId } from '../playerId';
import { httpBaseUrl } from './apiBase';

const SESSION_KEY = 'philoagents_session';
// Renew a while before the deadline so a long play session never sends an expired token.
const RENEW_SKEW_SECONDS = 600;

let pending = null;

function cached() {
    try {
        return JSON.parse(localStorage.getItem(SESSION_KEY));
    } catch (error) {
        return null;
    }
}

async function mint() {
    const response = await fetch(`${httpBaseUrl()}/session`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({player_id: getPlayerId()})
    });

    if (!response.ok) {
        throw new Error(`无法开始会话：HTTP ${response.status}`);
    }

    const session = await response.json();
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    // The server owns the canonical id, so adopt whatever it hands back.
    setPlayerId(session.player_id);
    return session;
}

export async function getSession(force = false) {
    const current = cached();
    const now = Math.floor(Date.now() / 1000);

    if (!force && current && current.token && current.expires_at - now > RENEW_SKEW_SECONDS) {
        return current;
    }

    // Share one in-flight mint between the history reads that fire on the same scene.
    if (!pending) {
        pending = mint().finally(() => {
            pending = null;
        });
    }
    return pending;
}

export async function authHeaders() {
    const session = await getSession();
    return {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${session.token}`
    };
}

export async function authFrame() {
    const session = await getSession();
    // player_id is only read by a server running without SESSION_SECRET; an authenticated
    // one takes the identity from the token and ignores this claim.
    return JSON.stringify({auth: session.token, player_id: getPlayerId()});
}

export function forgetSession() {
    localStorage.removeItem(SESSION_KEY);
}
