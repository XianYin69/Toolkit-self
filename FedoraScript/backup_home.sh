#!/bin/bash

# 设置语言为C,确保日期格式一致
export LC_TIME=C

# 提示用户输入备份目标路径
read -p "请输入备份目标路径: " backup_dest

# 检查是否提供了目标路径
if [ -z "$backup_dest" ]; then
    echo "错误：备份目标路径不能为空。"
    exit 1
fi

# 检查目标目录是否存在且为有效目录
if [ ! -d "$backup_dest" ]; then
    echo "错误：目标路径 '$backup_dest' 不是一个有效的目录。"
    exit 1
fi

# 定义带有时间戳 (YYYY-MM-DD_HH-MM-SS) 的备份文件名
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
backup_filename="home_backup_${timestamp}.tar.gz"
full_backup_path="${backup_dest}/${backup_filename}"

# --- 构建排除列表 ---
# 查找 /home 下的所有用户目录,并为常见的缓存/临时文件夹构建排除选项。
# 这比静态列表更健壮。
exclude_opts=()
for user_home in /home/*; do
    # 在继续之前检查它是否是一个目录
    if [ -d "${user_home}" ]; then
        # 排除 .cache 目录
        if [ -d "${user_home}/.cache" ]; then
            exclude_opts+=(--exclude="${user_home}/.cache")
        fi
        # 排除回收站目录
        if [ -d "${user_home}/.local/share/Trash" ]; then
            exclude_opts+=(--exclude="${user_home}/.local/share/Trash")
        fi
    fi
done

echo ""
echo "正在开始备份 /home 目录..."
echo "目标路径: ${full_backup_path}"
echo "根据目录大小,这可能需要一些时间。"
echo ""

# 创建 tar.gz 归档文件并显示进度 (v 标志)
# 该命令将列出添加到归档中的每个文件。
tar -czvf "${full_backup_path}" "${exclude_opts[@]}" /home

# 检查 tar 命令的退出代码以确认成功
if [ $? -eq 0 ]; then
    echo ""
    echo "----------------------------------------"
    echo "备份成功！"
    echo "备份文件位于: ${full_backup_path}"
    echo "----------------------------------------"
else
    echo ""
    echo "----------------------------------------"
    echo "错误：备份失败。"
    echo "----------------------------------------"
    # 如果存在,则清理部分备份文件
    rm -f "${full_backup_path}"
    exit 1
fi

exit 0