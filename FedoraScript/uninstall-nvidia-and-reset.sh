#!/bin/bash

# ==============================================================================
#                 NVIDIA 驱动终极卸载与重置脚本
# ==============================================================================
# 目标: 彻底清除所有NVIDIA专有驱动组件，并将系统恢复至使用
#       开源Nouveau驱动的稳定状态。
#
# 用法:
# 1. 保存为 'uninstall-nvidia-and-reset.sh'
# 2. chmod +x uninstall-nvidia-and-reset.sh
# 3. sudo bash uninstall-nvidia-and-reset.sh
# ==============================================================================

# 定义颜色常量
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BLUE='\033[0;34m'; NC='\033[0m'

# 确保以 root 权限运行
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}此脚本需要 root 权限。请使用 'sudo bash $0' 运行。${NC}"; exit 1
fi

echo -e "${BLUE}==============================================${NC}"
echo -e "${BLUE}     NVIDIA 驱动终极卸载与重置脚本         ${NC}"
echo -e "${BLUE}==============================================${NC}"
echo -e "${YELLOW}!!! 警告：此脚本将彻底清除您系统上所有NVIDIA专有驱动组件。!!!${NC}"
echo -e "${YELLOW}!!! 它将修复GRUB，重建RPM数据库，并恢复开源Nouveau驱动。   !!!${NC}"
echo -e "${YELLOW}!!! 在继续之前，请务必切换到 TTY (Ctrl+Alt+F2-F6)。   !!!${NC}"
read -p "如果您确认要卸载闭源驱动并重置，请按 Enter 键继续。按 Ctrl+C 取消。"

GRUB_DEFAULT_FILE="/etc/default/grub"
GRUB_OUTPUT_PATH="/boot/grub2/grub.cfg"

# --- 步骤 1: 修复 GRUB 配置文件 (如果损坏) ---
echo -e "\n${CYAN}--- 步骤 1: 检查并修复 GRUB 配置文件 ---${NC}"
if [ -f "$GRUB_DEFAULT_FILE" ] && grep -qE "(^sed,|^,)" "$GRUB_DEFAULT_FILE"; then
    echo -e "${RED}检测到 '/etc/default/grub' 文件已损坏，正在强制修复...${NC}"
    sudo cp "$GRUB_DEFAULT_FILE" "${GRUB_DEFAULT_FILE}.bak.$(date +%s)"
    sudo tee "$GRUB_DEFAULT_FILE" > /dev/null << EOF
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR="\$(sed 's, release .*\$,,g' /etc/system-release)"
GRUB_DEFAULT=saved
GRUB_DISABLE_SUBMENU=true
GRUB_TERMINAL_OUTPUT="console"
GRUB_CMDLINE_LINUX="rhgb quiet"
GRUB_DISABLE_RECOVERY="true"
GRUB_ENABLE_BLSCFG=true
EOF
    echo -e "${GREEN}GRUB 配置文件已强制重置为标准模板。${NC}"
fi

# --- 步骤 2: 修复 RPM 数据库 ---
echo -e "\n${CYAN}--- 步骤 2: 清理 DNF 缓存并重建 RPM 数据库 ---${NC}"
echo -e "${YELLOW}正在清理 DNF 缓存...${NC}"; sudo dnf clean all -y
echo -e "${YELLOW}正在重建 RPM 数据库... 这可能需要一些时间。${NC}"; sudo rpm --rebuilddb
echo -e "${GREEN}RPM 数据库重建完成。${NC}\n"

# --- 步骤 3: 强制卸载所有 NVIDIA 软件包 ---
echo -e "\n${CYAN}--- 步骤 3: 强制卸载所有 NVIDIA 软件包 ---${NC}"
echo -e "${YELLOW}正在使用 'dnf remove' 卸载所有匹配 '*nvidia*' 的软件包...${NC}"
sudo dnf remove -y "*nvidia*"
echo -e "${YELLOW}正在运行 'dnf autoremove' 清理残留依赖...${NC}"
sudo dnf autoremove -y
echo -e "${GREEN}NVIDIA 软件包卸载完成。${NC}\n"

# --- 步骤 4: 清理所有已知NVIDIA残留文件和目录 ---
echo -e "\n${CYAN}--- 步骤 4: 清理所有已知NVIDIA残留文件和目录 ---${NC}"
echo -e "${YELLOW}正在删除 MOK 密钥文件、Nouveau 黑名单、akmods缓存、Xorg配置...${NC}"
sudo rm -rf /etc/pki/akmods /etc/modprobe.d/blacklist-nouveau.conf /var/cache/akmods/* /usr/src/nvidia-* /etc/nvidia
sudo find /etc/X11/xorg.conf.d -name '*-nvidia.conf' -delete
echo -e "${GREEN}残留文件清理完成。${NC}\n"

# --- 步骤 5: 强制重置 GRUB 引导参数 (移除Nouveau黑名单) ---
echo -e "\n${CYAN}--- 步骤 5: 强制重置 GRUB 引导参数 ---${NC}"
echo -e "${YELLOW}正在从 GRUB_CMDLINE_LINUX 中彻底移除所有 Nouveau 黑名单参数...${NC}"
sudo sed -i -E 's/rd\.driver\.blacklist=[^[:space:]]*nouveau[^[:space:]]*//g' "$GRUB_DEFAULT_FILE"
sudo sed -i -E 's/modprobe\.blacklist=[^[:space:]]*nouveau[^[:space:]]*//g' "$GRUB_DEFAULT_FILE"
sudo sed -i -E 's/nouveau\.modeset=0//g' "$GRUB_DEFAULT_FILE"
sudo sed -i -E 's/\s+/ /g' "$GRUB_DEFAULT_FILE" # 清理多余空格
echo -e "${YELLOW}正在重新生成 GRUB 配置文件...${NC}"
sudo grub2-mkconfig -o "$GRUB_OUTPUT_PATH" || { echo -e "${RED}致命错误：重新生成 GRUB 配置失败！${NC}"; exit 1; }
echo -e "${GREEN}GRUB 配置已成功重置并生成。${NC}\n"

# --- 步骤 6: 更新 initramfs 以完全恢复 Nouveau ---
echo -e "\n${CYAN}--- 步骤 6: 更新 initramfs 以完全恢复 Nouveau ---${NC}"
echo -e "${YELLOW}正在重新生成 initramfs，确保 Nouveau 驱动被正确包含...${NC}"
sudo dracut --force --verbose || { echo -e "${RED}错误：重新生成 initramfs 失败。${NC}"; exit 1; }
echo -e "${GREEN}initramfs 更新完成。${NC}\n"

echo -e "${GREEN}==============================================${NC}"
echo -e "${GREEN}--- NVIDIA 驱动终极卸载与重置已完成。---${NC}"
echo -e "${GREEN}==============================================${NC}"
echo -e "${YELLOW}您的系统已被清理至最干净状态。开源 Nouveau 驱动将在下次启动时加载。${NC}"
echo -e "${RED}!!! 最终和最重要的步骤：务必立即重启系统。 !!!${NC}"
read -p "按 Enter 键立即重启。"
sudo systemctl reboot
