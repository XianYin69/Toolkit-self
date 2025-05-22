#!/bin/bash

# 1. 识别包管理器
echo "正在识别系统包管理器..."
if command -v dnf &> /dev/null; then
    PACKAGE_MANAGER="dnf"
    echo "识别到包管理器: dnf"
elif command -v yum &> /dev/null; then
    PACKAGE_MANAGER="yum"
    echo "识别到包管理器: yum"
else
    echo "错误: 未识别到支持的包管理器 (dnf 或 yum)。"
    exit 1
fi

# 2. 安装LibreOffice中文语言包和帮助文档
PACKAGES=("libreoffice-langpack-zh-CN" "libreoffice-help-zh-CN")

for PACKAGE in "${PACKAGES[@]}"; do
    echo "正在安装 $PACKAGE..."
    sudo "$PACKAGE_MANAGER" install -y "$PACKAGE"
    
    # 3. 错误处理
    if [ $? -ne 0 ]; then
        echo "错误: 安装 $PACKAGE 失败。"
        exit 1
    fi
    echo "$PACKAGE 安装成功。"
done

echo "所有指定的LibreOffice中文语言包和帮助文档已成功安装。"