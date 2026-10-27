
const messages = {
  zh: {
    play: "开始游戏",
    "philosopher.socrates": "苏格拉底",
    "philosopher.plato": "柏拉图",
    "philosopher.aristotle": "亚里士多德",
    "philosopher.descartes": "笛卡尔",
    "philosopher.leibniz": "莱布尼茨",
    "philosopher.ada_lovelace": "阿达·洛夫莱斯",
    "philosopher.turing": "图灵",
    "philosopher.chomsky": "乔姆斯基",
    "philosopher.searle": "塞尔",
    "philosopher.dennett": "丹尼特",
    instructions: "操作说明",
    support: "支持原项目",
    language: "语言：中文（点击切换）",
    move: "方向键：移动人物",
    talk: "空格键：与哲学家交谈",
    closeDialogue: "ESC：关闭对话",
    close: "关闭",
    input: "输入中文或英文，回车发送",
    paused: "游戏已暂停",
    resume: "继续游戏",
    mainMenu: "返回主菜单",
    reset: "重新开始",
    resetFailed: "重置游戏失败，请重试",
  },
  en: {
    play: "Let's Play!",
    instructions: "Instructions",
    support: "Support PhiloAgents",
    language: "Language: English (Switch)",
    move: "Arrow keys: Move",
    talk: "SPACE: Talk to philosophers",
    closeDialogue: "ESC: Close dialogue",
    close: "Close",
    input: "Type your message and press Enter",
    paused: "GAME PAUSED",
    resume: "Resume Game",
    mainMenu: "Main Menu",
    reset: "Reset Game",
    resetFailed: "Failed to reset game. Try again.",
  }
};

export function getLanguage() {
  return localStorage.getItem("game_language") || "zh";
}

export function t(key) {
  return messages[getLanguage()]?.[key] || key;
}

// 哲学家在本语言下的显示名；没有配置时（如英文）沿用传入的默认名
export function philosopherName(id, defaultName) {
  return messages[getLanguage()]?.[`philosopher.${id}`] || defaultName;
}

export function toggleLanguage() {
  localStorage.setItem(
    "game_language",
    getLanguage() === "zh" ? "en" : "zh"
  );
}
