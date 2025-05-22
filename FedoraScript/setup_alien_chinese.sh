#!/bin/bash

# ==============================================================================
# 脚本名称: setup_alien_chinese.sh
# 功能描述: 本脚本用于安装 'alien' 软件包转换工具，并配置必要的中文环境，
#           以确保在处理包含中文字符的软件包时能够正常工作。
# 作者:     Kilo Code
# 创建日期: $(date +%Y-%m-%d)
# ==============================================================================

# --- 通用函数 ---

# 打印带有高亮标题的消息
print_message() {
    echo
    echo "================================================="
    echo " $1"
    echo "================================================="
    echo
}

# --- 脚本主体 ---

# 步骤 1: 安装 alien
print_message "步骤 1: 正在检查并安装 alien..."

# 检测包管理器
if command -v dnf &> /dev/null; then
    PACKAGE_MANAGER="dnf"
elif command -v apt-get &> /dev/null; then
    PACKAGE_MANAGER="apt"
elif command -v pacman &> /dev/null; then
    PACKAGE_MANAGER="pacman"
else
    echo "错误：未检测到支持的包管理器 (dnf, apt, pacman)。"
    echo "请手动安装 'alien' 后再重新运行此脚本。"
    exit 1
fi

echo "检测到包管理器: $PACKAGE_MANAGER。即将使用 sudo 执行安装命令。"

# 根据检测到的包管理器执行安装
case $PACKAGE_MANAGER in
    "dnf")
        sudo dnf install -y alien
        ;;
    "apt")
        sudo apt-get update && sudo apt-get install -y alien
        ;;
    "pacman")
        # Arch Linux 的 alien 在 AUR 中，通常需要使用 yay 或 paru 等辅助工具
        echo "警告：在 Arch Linux 上, 'alien' 通常位于 AUR (Arch User Repository)。"
        echo "请使用您的 AUR 助手 (例如 yay, paru) 手动安装 'alien' 或 'alien_package_converter'。"
        ;;
esac

# 检查 alien 是否安装成功
if ! command -v alien &> /dev/null; then
    echo
    echo "错误：'alien' 安装失败或未找到该命令。"
    echo "请检查上方的输出信息，解决问题后重试。"
    exit 1
else
    echo
    echo "'alien' 已成功安装。"
fi

# 步骤 2: 配置中文环境
print_message "步骤 2: 正在配置中文环境..."

# ------------------------------------------------------------------------------
# **为什么需要配置这些环境变量？**
#
# 'alien' 以及许多其他的 Linux 命令行工具在处理包含非 ASCII 字符（例如中文）
# 的文件名、路径或软件包元数据时，如果系统区域设置（locale）不正确，就可能
# 发生乱码或执行错误。
#
# **export LANG=zh_CN.UTF-8**:
#   - 此命令设置首选语言为简体中文，并指定使用通用的 UTF-8 字符编码。
#
# **export LC_ALL=zh_CN.UTF-8**:
#   - 此命令强制所有本地化相关的设置（如时间、货币格式等）统一为中文 UTF-8 环境，
#     以确保程序行为的一致性。
#
# 通过导出这两个变量，我们为当前的 Shell 会话以及由它启动的所有子进程
# (包括 'alien') 创建了一个明确的、能够正确显示和处理中文的运行环境。
# ------------------------------------------------------------------------------

echo "为了让 alien 正确处理中文字符，将导出以下环境变量："
echo "  - export LANG=zh_CN.UTF-8"
echo "  - export LC_ALL=zh_CN.UTF-8"
echo
echo "这些设置仅对当前终端会话有效。若需永久生效，您可以将这两行"
echo "命令添加到您的 Shell 配置文件中（例如 ~/.bashrc 或 ~/.zshrc）。"

# 在当前会话中导出变量以立即生效
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 步骤 3: 完成
print_message "步骤 3: 配置完成"
echo "Alien 安装及中文环境配置已顺利完成。"
echo "您现在可以直接在此终端窗口中使用 'alien' 来转换软件包了。"
echo "例如: alien -d your_package.rpm"