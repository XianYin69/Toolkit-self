#!/bin/bash

# 提示用户输入备份文件的路径
echo "请输入要用于恢复的 .tar.gz 备份文件的完整路径："
read backup_file

# 检查文件是否存在
if [ ! -f "$backup_file" ]; then
  echo "错误：文件 '$backup_file' 不存在。请检查路径是否正确。"
  exit 1
fi

# 显示警告并请求确认
echo "警告：此操作将使用备份文件中的内容覆盖您现有的 /home 目录中的同名文件。"
echo "强烈建议您在继续之前备份当前数据。"
echo -n "您确定要继续恢复操作吗？ (y/n): "
read confirmation

# 检查用户的确认
if [[ "$confirmation" != "y" && "$confirmation" != "Y" ]]; then
  echo "操作已取消。"
  exit 0
fi

# 执行恢复操作
echo "正在从 '$backup_file' 恢复到 / ..."
# 使用 sudo 是因为需要权限解压到根目录 /
# -p 选项用于保留文件的原始权限
# -C / 指定解压的目标目录为根目录
sudo tar -xzpf "$backup_file" -C /

# 检查 tar 命令是否成功执行
if [ $? -eq 0 ]; then
  echo "恢复操作成功完成。"
else
  echo "恢复操作失败。请检查错误信息。"
  exit 1
fi

exit 0