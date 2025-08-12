#!/bin/bash

# 定义颜色代码
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 提示用户输入文件路径
echo -e "${YELLOW}请输入压缩文件的路径（支持 .tar.gz 或 .tar.xz）：${NC}"
read -e SOURCE_ARCHIVE

# 如果用户输入为空，退出脚本
if [ -z "$SOURCE_ARCHIVE" ]; then
    echo -e "${RED}错误:${NC} 未输入文件路径"
    exit 1
fi

# 展开波浪号（如果存在）
SOURCE_ARCHIVE="${SOURCE_ARCHIVE/#\~/$HOME}"

# 检查文件是否存在
if [ ! -f "$SOURCE_ARCHIVE" ]; then
    echo -e "${RED}错误:${NC} 文件 '${YELLOW}$SOURCE_ARCHIVE${NC}' 不存在"
    exit 1
fi

# 检测Linux发行版
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo -e "${RED}错误:${NC} 无法检测Linux发行版"
    exit 1
fi

# 安装编译必需的包
install_build_essentials() {
    case $DISTRO in
        "ubuntu"|"debian")
            sudo apt-get update
            sudo apt-get install -y build-essential automake autoconf libtool pkg-config
            ;;
        "fedora")
            sudo dnf groupinstall -y "Development Tools"
            sudo dnf install -y automake autoconf libtool pkg-config
            ;;
        "centos"|"rhel")
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y automake autoconf libtool pkg-config
            ;;
        "opensuse"|"suse")
            sudo zypper install -y -t pattern devel_basis
            sudo zypper install -y automake autoconf libtool pkg-config
            ;;
        "arch")
            sudo pacman -Sy --noconfirm base-devel
            ;;
        *)
            echo "不支持的发行版: $DISTRO"
            exit 1
            ;;
    esac
}

# 创建临时目录
TEMP_DIR=$(mktemp -d)
echo -e "${GREEN}[✓]${NC} 创建临时目录: ${BLUE}$TEMP_DIR${NC}"

# 解压源代码
echo -e "${YELLOW}[*]${NC} 解压源代码..."
tar -xf "$SOURCE_ARCHIVE" -C "$TEMP_DIR"

# 切换到临时目录
cd "$TEMP_DIR" || exit 1

# 递归搜索所有可执行文件
echo -e "${YELLOW}[*]${NC} 搜索可执行文件..."
EXECUTABLE_FILES=()
while IFS= read -r -d '' file; do
    if [ -x "$file" ] && [ -f "$file" ] && ! [[ "$file" =~ \.(sh|py|pl|rb)$ ]]; then
        file_type=$(file -b "$file")
        if [[ $file_type == *"ELF"* ]]; then
            EXECUTABLE_FILES+=("$file")
        fi
    fi
done < <(find . -type f -print0)

# 检查是否找到可执行文件
if [ ${#EXECUTABLE_FILES[@]} -gt 0 ]; then
    echo -e "${GREEN}[✓]${NC} 找到 ${#EXECUTABLE_FILES[@]} 个可执行文件"
    
    # 如果找到多个可执行文件，让用户选择
    if [ ${#EXECUTABLE_FILES[@]} -gt 1 ]; then
        echo -e "${YELLOW}找到多个可执行文件，请选择要安装的文件：${NC}"
        for i in "${!EXECUTABLE_FILES[@]}"; do
            echo -e "$((i+1)). ${BLUE}${EXECUTABLE_FILES[$i]}${NC}"
        done
        
        read -p "请输入数字选择(1-${#EXECUTABLE_FILES[@]}): " choice
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#EXECUTABLE_FILES[@]}" ]; then
            SELECTED_FILE="${EXECUTABLE_FILES[$((choice-1))]}"
        else
            echo -e "${RED}错误:${NC} 无效的选择"
            cd
            rm -rf "$TEMP_DIR"
            exit 1
        fi
    else
        SELECTED_FILE="${EXECUTABLE_FILES[0]}"
    fi

    # 获取文件名（不包含路径）
    FILENAME=$(basename "$SELECTED_FILE")
    
    # 提示用户确认安装位置
    echo -e "${YELLOW}将安装 ${BLUE}$FILENAME${NC} 到系统。请选择安装位置：${NC}"
    echo -e "1. /usr/local/bin/ (推荐，所有用户可用)"
    echo -e "2. ~/bin/ (仅当前用户可用)"
    read -p "请选择安装位置 [1-2]: " location_choice
    
    case $location_choice in
        1)
            INSTALL_PATH="/usr/local/bin/$FILENAME"
            echo -e "${YELLOW}[*]${NC} 安装到 ${BLUE}$INSTALL_PATH${NC}..."
            sudo install -m 755 "$SELECTED_FILE" "$INSTALL_PATH"
            ;;
        2)
            mkdir -p ~/bin
            INSTALL_PATH="$HOME/bin/$FILENAME"
            echo -e "${YELLOW}[*]${NC} 安装到 ${BLUE}$INSTALL_PATH${NC}..."
            install -m 755 "$SELECTED_FILE" "$INSTALL_PATH"
            ;;
        *)
            echo -e "${RED}错误:${NC} 无效的选择"
            cd
            rm -rf "$TEMP_DIR"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}[✓]${NC} 安装完成！"
    echo -e "\n您可以通过以下命令运行程序："
    echo -e "${BLUE}$FILENAME${NC}"
    
else
    # 如果没有找到可执行文件，检查是否是源代码
    if [ -f "./configure" ] || [ -f "./autogen.sh" ] || [ -f "./CMakeLists.txt" ]; then
        echo -e "${YELLOW}[*]${NC} 检测到源代码，开始编译安装流程..."
        
        # 安装编译工具
        echo -e "${YELLOW}[*]${NC} 安装编译工具..."
        install_build_essentials

        # 配置、编译和安装
        echo -e "${YELLOW}[*]${NC} 配置源代码..."
        if [ -f "./configure" ]; then
            ./configure
        elif [ -f "./autogen.sh" ]; then
            ./autogen.sh
        elif [ -f "./CMakeLists.txt" ]; then
            mkdir build
            cd build
            cmake ..
        fi

        echo -e "${YELLOW}[*]${NC} 编译源代码..."
        make -j$(nproc)

        echo -e "${YELLOW}[*]${NC} 安装软件..."
        sudo make install
    else
        echo -e "${RED}错误:${NC} 未找到可执行文件或源代码"
        cd
        rm -rf "$TEMP_DIR"
        exit 1
    fi
fi

# 清理临时文件
echo -e "${YELLOW}[*]${NC} 清理临时文件..."
cd
rm -rf "$TEMP_DIR"

echo -e "${GREEN}[✓]${NC} 安装完成！"
