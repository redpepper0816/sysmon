#!/bin/bash
# SysMon 安装脚本
set -e

echo "╔══════════════════════════════════════╗"
echo "║   SysMon - macOS 系统监控工具安装    ║"
echo "╚══════════════════════════════════════╝"
echo ""

# 检查 Python 3
if ! command -v python3 &>/dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3"
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

# 安装 pip 依赖
echo ""
echo "📦 安装 Python 依赖..."
pip3 install -r requirements.txt
echo "✅ rumps + psutil 已安装"

# 尝试安装温度工具
echo ""
if command -v brew &>/dev/null; then
    echo "🌡  安装温度监控工具 (osx-cpu-temp)..."
    if brew install osx-cpu-temp 2>/dev/null; then
        echo "✅ osx-cpu-temp 已安装（支持温度显示）"
    else
        echo "⚠️  osx-cpu-temp 安装失败，温度将显示 N/A"
        echo "   可手动安装: brew install osx-cpu-temp"
    fi
else
    echo "⚠️  未检测到 Homebrew"
    echo "   安装 Homebrew 后可启用温度监控:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "   brew install osx-cpu-temp"
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   ✅ 安装完成！                      ║"
echo "╠══════════════════════════════════════╣"
echo "║   启动命令:                          ║"
echo "║   python3 sysmon.py                  ║"
echo "╚══════════════════════════════════════╝"
