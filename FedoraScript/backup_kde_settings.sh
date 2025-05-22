#!/bin/bash

# 设置备份目录名称，包含当前日期
BACKUP_DIR="kde_settings_backup_$(date +%Y-%m-%d)"
TARBALL_NAME="${BACKUP_DIR}.tar.gz"

# 定义需要备份的配置文件和目录列表
# 使用数组以正确处理可能包含空格的路径
declare -a CONFIG_FILES=(
    "plasma-org.kde.plasma.desktop-appletsrc"
    "kwinrc"
    "kdeglobals"
    "konsolerc"
    "kglobalshortcutsrc"
    "dolphinrc"
    "gtk-3.0/settings.ini"
    "gtk-4.0/settings.ini"
    "Kvantum"
    "kstyles"
)

declare -a LOCAL_SHARE_DIRS=(
    "color-schemes"
    "plasma"
    "konsole"
    "icons"
    "aurorae"
    "sddm"
    "themes"
    "fonts"
)

# --- 备份流程开始 ---

echo "正在开始备份KDE Plasma设置..."
echo "以下项目将被备份："

# 显示 ~/.config 中的文件
for item in "${CONFIG_FILES[@]}"; do
    echo "  - ~/.config/${item}"
done

# 显示 ~/.local/share 中的目录
for item in "${LOCAL_SHARE_DIRS[@]}"; do
    echo "  - ~/.local/share/${item}"
done
echo "  - 当前壁纸"
echo ""

# 创建主备份目录
echo "正在创建备份目录: ${BACKUP_DIR}"
mkdir -p "$BACKUP_DIR"

# 备份 ~/.config 中的文件
echo "正在备份配置文件..."
for item in "${CONFIG_FILES[@]}"; do
    if [ -e "$HOME/.config/${item}" ]; then
        # 确保目标目录存在，以维持原始结构
        mkdir -p "$BACKUP_DIR/config/$(dirname "${item}")"
        cp -r "$HOME/.config/${item}" "$BACKUP_DIR/config/${item}"
    else
        echo "警告: 未找到 ~/.config/${item}。正在跳过。"
    fi
done

# 备份 ~/.local/share 中的目录
echo "正在备份 local share 目录..."
for item in "${LOCAL_SHARE_DIRS[@]}"; do
    if [ -d "$HOME/.local/share/${item}" ]; then
        # 确保目标目录存在
        mkdir -p "$BACKUP_DIR/local/share/$(dirname "${item}")"
        cp -r "$HOME/.local/share/${item}" "$BACKUP_DIR/local/share/${item}"
    else
        echo "警告: 未找到 ~/.local/share/${item}。正在跳过。"
    fi
done

# 查找并备份当前壁纸
echo "正在备份当前壁纸..."
# 从 appletsrc 文件中提取壁纸路径
WALLPAPER_PATH=$(grep -oP 'Image=file://\K.*' "$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc" | head -n 1)

if [ -n "$WALLPAPER_PATH" ] && [ -f "$WALLPAPER_PATH" ]; then
    mkdir -p "$BACKUP_DIR/wallpapers"
    cp "$WALLPAPER_PATH" "$BACKUP_DIR/wallpapers/"
    echo "壁纸已备份: $(basename "$WALLPAPER_PATH")"
else
    echo "警告: 无法找到或访问当前壁纸。正在跳过。"
fi

# 创建压缩归档文件
echo "正在创建压缩包: ${TARBALL_NAME}"
tar -czf "${TARBALL_NAME}" "${BACKUP_DIR}"

# 清理临时目录
rm -rf "${BACKUP_DIR}"

echo ""
echo "----------------------------------------"
echo "备份完成！"
echo "您的KDE设置已保存在: $(pwd)/${TARBALL_NAME}"
echo "----------------------------------------"