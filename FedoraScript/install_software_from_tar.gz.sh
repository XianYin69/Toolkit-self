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

# 进入源代码目录
cd "$TEMP_DIR"/*/ || exit 1

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
else
    echo -e "${RED}错误:${NC} 未找到配置文件 (${YELLOW}configure${NC}, ${YELLOW}autogen.sh${NC}, 或 ${YELLOW}CMakeLists.txt${NC})"
    exit 1
fi

echo -e "${YELLOW}[*]${NC} 编译源代码..."
make -j$(nproc)

echo -e "${YELLOW}[*]${NC} 安装软件..."
sudo make install

# 清理临时文件
echo -e "${YELLOW}[*]${NC} 清理临时文件..."
cd
rm -rf "$TEMP_DIR"

echo -e "${GREEN}[✓]${NC} 安装完成！"
