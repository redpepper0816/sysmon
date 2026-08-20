#!/bin/bash
# SysMon 启动/关闭脚本
APP="$HOME/Applications/SysMon.app"

case "${1:-toggle}" in
    start)
        if pgrep -f "SysMon.app.*sysmon.py" > /dev/null; then
            echo "⚡ SysMon 已在运行"
        else
            open "$APP" 2>/dev/null || "$APP/Contents/MacOS/sysmon" &
            echo "✅ SysMon 已启动"
        fi
        ;;
    stop)
        pkill -f "SysMon.app.*sysmon.py" 2>/dev/null
        echo "🛑 SysMon 已停止"
        ;;
    toggle|*)
        if pgrep -f "SysMon.app.*sysmon.py" > /dev/null; then
            pkill -f "SysMon.app.*sysmon.py" 2>/dev/null
            echo "🛑 SysMon 已停止"
        else
            open "$APP" 2>/dev/null || "$APP/Contents/MacOS/sysmon" &
            echo "✅ SysMon 已启动"
        fi
        ;;
esac
