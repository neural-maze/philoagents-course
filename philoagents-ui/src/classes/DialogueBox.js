
class DialogueBox {
    constructor(scene, config = {}) {
        this.scene = scene;
        this.awaitingInput = false;

        const {
            x = 100,
            y = 500,
            width = 824,
            height = 200,
            depth = 30
        } = config;

        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;

        // 每页最多显示 5 行
        this.maxLines = 5;
        this.firstLine = 0;
        this.followLatest = true;
        this.fullMessage = "";
        this.allLines = [];

        // 对话框背景
        const background = scene.add.graphics();

        background.fillStyle(0x000000, 0.85);
        background.fillRect(x, y, width, height);

        background.lineStyle(2, 0xffffff);
        background.strokeRect(x, y, width, height);

        // 对话文字
        this.text = scene.add.text(
            x + 20,
            y + 16,
            "",
            {
                fontFamily: "Microsoft YaHei, Arial, sans-serif",
                fontSize: "22px",
                color: "#ffffff",
                lineSpacing: 6
            }
        );

        // 滚动提示
        this.scrollHint = scene.add.text(
            x + width - 20,
            y + height - 17,
            "鼠标滚轮查看前后内容",
            {
                fontFamily: "Microsoft YaHei, Arial, sans-serif",
                fontSize: "14px",
                color: "#aaccff"
            }
        ).setOrigin(1, 0.5);

        this.container = scene.add.container(
            0, 0,
            [background, this.text, this.scrollHint]
        );

        this.container.setDepth(depth);
        this.container.setScrollFactor(0);

        // 鼠标滚轮翻阅长对话
        this.onWheel = (pointer, objects, dx, dy) => {
            if (!this.isVisible()) return;

            // 只有鼠标在对话框区域时才滚动
            if (
                pointer.x < this.x ||
                pointer.x > this.x + this.width ||
                pointer.y < this.y ||
                pointer.y > this.y + this.height
            ) {
                return;
            }

            const maxFirst = Math.max(
                0,
                this.allLines.length - this.maxLines
            );

            if (maxFirst === 0) return;

            // 每次滚动两行
            const direction = Math.sign(dy);

            this.firstLine = Phaser.Math.Clamp(
                this.firstLine + direction * 2,
                0,
                maxFirst
            );

            // 滚动到最底部后继续跟随 AI 输出
            this.followLatest = this.firstLine === maxFirst;

            this.renderText();
        };

        scene.input.on("wheel", this.onWheel);

        // 避免切换场景时残留事件
        scene.events.once("shutdown", () => {
            scene.input.off("wheel", this.onWheel);
        });

        this.hide();
    }

    // 中文、英文均按实际字符宽度换行
    wrapMessage(message) {
        const context = this.text.context;

        context.font =
            '22px "Microsoft YaHei", Arial, sans-serif';

        const maxWidth = this.width - 40;
        const result = [];

        // 保留 AI 返回的自然换行
        const paragraphs = String(message).split(/\r?\n/);

        for (const paragraph of paragraphs) {
            let line = "";
            let lineWidth = 0;

            for (const char of paragraph) {
                const charWidth = context.measureText(char).width;

                if (
                    line.length > 0 &&
                    lineWidth + charWidth > maxWidth
                ) {
                    result.push(line);
                    line = char;
                    lineWidth = charWidth;
                } else {
                    line += char;
                    lineWidth += charWidth;
                }
            }

            result.push(line);
        }

        return result;
    }

    // 只渲染当前显示的几行
    renderText() {
        const maxFirst = Math.max(
            0,
            this.allLines.length - this.maxLines
        );

        if (this.followLatest) {
            this.firstLine = maxFirst;
        } else {
            this.firstLine = Math.min(this.firstLine, maxFirst);
        }

        const visibleLines = this.allLines.slice(
            this.firstLine,
            this.firstLine + this.maxLines
        );

        this.text.setText(visibleLines.join("\n"));

        this.scrollHint.setVisible(
            this.allLines.length > this.maxLines
        );
    }

    show(message, awaitInput = false) {
        const newMessage = String(message ?? "");

        // 开始新对话时重置滚动位置
        if (
            !this.container.visible ||
            !newMessage.startsWith(this.fullMessage)
        ) {
            this.firstLine = 0;
            this.followLatest = true;
        }

        this.fullMessage = newMessage;
        this.allLines = this.wrapMessage(newMessage);

        this.renderText();

        this.container.setVisible(true);
        this.awaitingInput = awaitInput;
    }

    hide() {
        this.container.setVisible(false);
        this.awaitingInput = false;
        this.firstLine = 0;
        this.followLatest = true;
    }

    isVisible() {
        return this.container.visible;
    }

    isAwaitingInput() {
        return this.awaitingInput;
    }
}

export default DialogueBox;
