
import ApiService from './services/ApiService';

export function createHistoryPanel(scene) {
    // 聊天记录按钮
    const button = document.createElement('button');
    button.textContent = '📜 聊天记录';

    Object.assign(button.style, {
        position: 'fixed',
        right: '20px',
        top: '20px',
        zIndex: '9998',
        padding: '10px 16px',
        background: '#254b73',
        color: 'white',
        border: 'none',
        borderRadius: '8px',
        cursor: 'pointer'
    });

    // 历史记录窗口
    const panel = document.createElement('div');

    Object.assign(panel.style, {
        position: 'fixed',
        right: '20px',
        top: '70px',
        width: 'min(440px, 90vw)',
        height: 'min(550px, 70vh)',
        zIndex: '9999',
        display: 'none',
        flexDirection: 'column',
        gap: '10px',
        padding: '16px',
        boxSizing: 'border-box',
        background: '#192536',
        color: 'white',
        borderRadius: '12px',
        fontFamily: 'Microsoft YaHei, Arial, sans-serif'
    });

    const title = document.createElement('h3');
    title.textContent = '聊天历史记录';
    title.style.margin = '0';

    const close = document.createElement('button');
    close.textContent = '关闭';

    const picker = document.createElement('select');
    picker.style.padding = '10px';

    // 从当前游戏中的 NPC 列表创建选项（带 defaultMessage 的 NPC 不能聊天，后端也不认识它们）
    for (const npc of scene.philosophers) {
        if (npc.defaultMessage) {
            continue;
        }

        const option = document.createElement('option');
        option.value = npc.id;
        option.textContent = npc.displayName;
        picker.appendChild(option);
    }

    const messages = document.createElement('div');

    Object.assign(messages.style, {
        flex: '1',
        minHeight: '0',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px'
    });

    panel.append(title, close, picker, messages);
    document.body.append(button, panel);

    function addBubble(speaker, text, isPlayer) {
        const bubble = document.createElement('div');

        bubble.textContent = `${speaker}\n${text}`;

        Object.assign(bubble.style, {
            padding: '12px',
            borderRadius: '10px',
            background: isPlayer ? '#315c86' : '#344154',
            whiteSpace: 'pre-wrap',
            overflowWrap: 'anywhere',
            lineHeight: '1.6'
        });

        messages.appendChild(bubble);
    }

    // 从 MongoDB 读取，而不是 localStorage
    async function loadHistory() {
        messages.textContent = '正在读取聊天记录...';

        try {
            const turns = await ApiService.getChatHistory(
                picker.value
            );

            messages.replaceChildren();

            if (turns.length === 0) {
                messages.textContent = '暂无聊天记录';
                return;
            }

            const npcName =
                picker.options[picker.selectedIndex]?.textContent
                || picker.value;

            for (const turn of turns) {
                addBubble('我', turn.user_message, true);
                addBubble(npcName, turn.assistant_message, false);
            }

            messages.scrollTop = messages.scrollHeight;

        } catch (error) {
            console.error(error);
            messages.textContent =
                '读取失败，请检查 MongoDB 后端是否正常运行';
        }
    }

    button.addEventListener('click', () => {
        const opening = panel.style.display === 'none';
        panel.style.display = opening ? 'flex' : 'none';

        if (opening) loadHistory();
    });

    picker.addEventListener('change', loadHistory);

    close.addEventListener('click', () => {
        panel.style.display = 'none';
    });

    // 防止 HTML 面板中的按键影响人物移动
    panel.addEventListener('keydown', event => {
        event.stopPropagation();
    });

    // 离开游戏场景时清理 HTML 元素
    scene.events.once('shutdown', () => {
        button.remove();
        panel.remove();
    });
}
