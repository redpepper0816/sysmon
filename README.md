# SysMon - macOS 菜单栏系统监控工具

实时显示 CPU、内存、网络速度、GPU 利用率、温度等系统信息。

![SysMon](https://img.shields.io/badge/platform-macOS-blue) ![Python](https://img.shields.io/badge/python-3.9+-green)

## 功能

- 🖥 CPU 使用率
- 🧠 内存使用率
- 📤📥 上下行网速
- 🎮 GPU 利用率（支持 Apple Silicon / Intel）
- 🌡 CPU 温度（需安装 `osx-cpu-temp`）
- 📊 进程数 & 开机时长

## 安装

```bash
# 安装依赖
pip3 install "pyobjc-core<11" "pyobjc-framework-Cocoa<11" rumps psutil

# 可选：安装温度监控工具
brew install osx-cpu-temp
```

## 使用

### 方式一：直接运行

```bash
python3 sysmon.py
```

### 方式二：使用 App

双击 `SysMon.app` 或通过 Spotlight 搜索 "SysMon" 打开。

### 命令行控制

```bash
bash sysmon.sh start   # 启动
bash sysmon.sh stop    # 停止
bash sysmon.sh         # 切换
```

## 项目结构

```
sysmon/
├── sysmon.py          # 主程序
├── sysmon.sh          # 启动/停止脚本
├── requirements.txt   # Python 依赖
├── setup.sh           # 一键安装脚本
└── SysMon.app/        # macOS 应用包
```

## License

MIT
