
const PLAYER_ID_KEY = "philoagents_player_id";

export function getPlayerId() {
    let id = localStorage.getItem(PLAYER_ID_KEY);

    if (!id) {
        id = crypto.randomUUID();
        localStorage.setItem(PLAYER_ID_KEY, id);
    }

    return id;
}

export function setPlayerId(id) {
    if (id) {
        localStorage.setItem(PLAYER_ID_KEY, id);
    }
}
