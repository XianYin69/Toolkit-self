#!/bin/bash

# 函数：打印错误信息并退出
error_exit() {
    echo "错误: $1" >&2
    exit 1
}

# 检查alien工具是否安装，如果未安装则尝试安装
check_and_install_alien() {
    echo "正在检查 'alien' 工具..."
    if ! command -v alien &> /dev/null; then
        echo "'alien' 未安装。尝试安装..."
        if command -v dnf &> /dev/null; then
            sudo dnf install alien -y || error_exit "安装 'alien' 失败 (dnf)."
        elif command -v yum &> /dev/null; then
            sudo yum install alien -y || error_exit "安装 'alien' 失败 (yum)."
        else
            error_exit "未找到 dnf 或 yum 包管理器，无法自动安装 'alien'。请手动安装 'alien'。"
        fi
        echo "'alien' 已成功安装。"
    else
        echo "'alien' 已安装。"
    fi
}

# 检查输入参数
if [ "$#" -eq 0 ]; then
    echo "用法: $0 <deb文件1> [deb文件2...]"
    echo "示例: $0 myapp.deb"
    exit 1
fi

# 检查并安装alien
check_and_install_alien

# 遍历所有.deb文件进行转换和安装
for deb_file in "$@"; do
    if [ ! -f "$deb_file" ]; then
        echo "警告: 文件 '$deb_file' 不存在，跳过。"
        continue
    fi

    echo "正在处理文件: $deb_file"

    # 转换.deb到.rpm
    echo "正在将 '$deb_file' 转换为 RPM 包..."
    # 使用basename获取文件名（不带路径），然后替换.deb为.rpm来预测rpm文件名
    base_name=$(basename "$deb_file" .deb)
    rpm_file="${base_name}.rpm"
    # alien 会在当前目录生成rpm文件，所以不用担心路径问题
    sudo alien --to-rpm "$deb_file" || error_exit "将 '$deb_file' 转换为 RPM 失败。"
    echo "RPM 包 '$rpm_file' 已生成。"

    # 检查生成的rpm文件是否存在
    if [ ! -f "$rpm_file" ]; then
        error_exit "RPM 转换失败，未找到生成的 '$rpm_file' 文件。"
    fi

    # 安装.rpm包
    echo "正在安装 RPM 包 '$rpm_file'..."
    sudo rpm -ivh "$rpm_file" || error_exit "安装 RPM 包 '$rpm_file' 失败。"
    echo "RPM 包 '$rpm_file' 已成功安装。"

    # 清理：删除生成的.rpm文件
    echo "正在删除生成的 RPM 包 '$rpm_file'..."
    rm -f "$rpm_file"
    if [ $? -ne 0 ]; then
        echo "警告: 删除 RPM 包 '$rpm_file' 失败，请手动删除。"
    else
        echo "RPM 包 '$rpm_file' 已删除。"
    fi
    echo "" # 空行分隔不同文件的处理
done

echo "所有指定的 .deb 文件处理完成。"