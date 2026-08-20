#!/usr/bin/env python3
"""
SysMon - macOS 菜单栏系统监控工具
实时监控 CPU / 内存 / 网络 / 温度 / GPU
"""

import rumps
import psutil
import subprocess
import time
import re


class SysMonApp(rumps.App):
    """macOS 菜单栏系统监控应用"""

    def __init__(self):
        super().__init__(name="SysMon", title="⏳", quit_button=None)

        # 网络速度计算
        self._last_net = psutil.net_io_counters()
        self._last_time = time.time()

        # 缓存
        self._cpu = 0.0
        self._mem = 0.0
        self._up = 0.0
        self._down = 0.0
        self._temp = "N/A"
        self._gpu = "N/A"

        # 检测温度工具
        self._temp_tool = self._detect_temp_tool()

        # ── 创建菜单项（只创建一次，后续只更新文字） ──
        self._item_cpu = rumps.MenuItem("🖥  CPU       --")
        self._item_mem = rumps.MenuItem("🧠 内存       --")
        self._item_up = rumps.MenuItem("📤 上传速度    --")
        self._item_dn = rumps.MenuItem("📥 下载速度    --")
        self._item_temp = rumps.MenuItem("🌡  CPU 温度   --")
        self._item_gpu = rumps.MenuItem("🎮 GPU        --")
        self._item_proc = rumps.MenuItem("📊 进程数      --")
        self._item_uptime = rumps.MenuItem("⏱  开机时长   --")
        self._item_refresh = rumps.MenuItem("🔄 立即刷新", callback=lambda _: self._update(None))
        self._item_quit = rumps.MenuItem("❌ 退出", callback=lambda _: rumps.quit_application())

        self.menu = [
            self._item_cpu,
            self._item_mem,
            self._item_up,
            self._item_dn,
            None,
            self._item_temp,
            self._item_gpu,
            None,
            self._item_proc,
            self._item_uptime,
            None,
            self._item_refresh,
            self._item_quit,
        ]

        # 首次更新
        self._update(None)

        # 每 2 秒刷新
        self._timer = rumps.Timer(self._update, 2)
        self._timer.start()

    # ── 格式化工具 ────────────────────────────────────────────

    @staticmethod
    def _fmt_speed(bps):
        """将 bytes/s 转为可读字符串"""
        if bps < 1024:
            return f"{bps:.0f}B"
        elif bps < 1024 ** 2:
            return f"{bps / 1024:.1f}K"
        elif bps < 1024 ** 3:
            return f"{bps / 1024 ** 2:.1f}M"
        return f"{bps / 1024 ** 3:.2f}G"

    @staticmethod
    def _fmt_uptime():
        """格式化系统开机时长"""
        secs = int(time.time() - psutil.boot_time())
        days, secs = divmod(secs, 86400)
        hours, secs = divmod(secs, 3600)
        mins, _ = divmod(secs, 60)
        if days > 0:
            return f"{days}天{hours}时{mins}分"
        elif hours > 0:
            return f"{hours}时{mins}分"
        return f"{mins}分钟"

    # ── 数据采集 ──────────────────────────────────────────────

    def _calc_net_speed(self):
        now = time.time()
        cur = psutil.net_io_counters()
        dt = now - self._last_time
        if dt > 0:
            self._up = (cur.bytes_sent - self._last_net.bytes_sent) / dt
            self._down = (cur.bytes_recv - self._last_net.bytes_recv) / dt
        self._last_net = cur
        self._last_time = now

    def _get_temp(self):
        """读取 CPU 温度"""
        if self._temp_tool == "osx-cpu-temp":
            try:
                out = subprocess.check_output(
                    ["osx-cpu-temp"], text=True, timeout=3
                ).strip()
                m = re.search(r"([\d.]+)", out)
                if m:
                    return f"{m.group(1)}°C"
            except Exception:
                pass
        elif self._temp_tool == "powermetrics":
            try:
                out = subprocess.check_output(
                    ["sudo", "-n", "powermetrics",
                     "--samplers", "smc", "-i", "500", "-n", "1"],
                    text=True, timeout=5, stderr=subprocess.DEVNULL,
                )
                m = re.search(r"CPU die.*?([\d.]+)\s*C", out)
                if m:
                    return f"{m.group(1)}°C"
            except Exception:
                pass
        # Apple Silicon 备用方案：电池温度
        if self._temp_tool is None:
            try:
                out = subprocess.check_output(
                    ["ioreg", "-r", "-c", "AppleSmartBattery"],
                    text=True, timeout=3, stderr=subprocess.DEVNULL,
                )
                m = re.search(r'"Temperature"\s*=\s*(\d+)', out)
                if m:
                    return f"{int(m.group(1)) / 100:.0f}°C(电池)"
            except Exception:
                pass
        return "N/A"

    def _get_gpu(self):
        """通过 ioreg 读取 GPU 负载百分比（兼容 Intel / Apple Silicon）"""
        try:
            out = subprocess.check_output(
                ["ioreg", "-l", "-w0"],
                text=True, timeout=5, stderr=subprocess.DEVNULL,
            )
            for line in out.splitlines():
                if "PerformanceStatistics" not in line:
                    continue
                # Apple Silicon: "Device Utilization %"=13
                m = re.search(r'"Device Utilization %"\s*=\s*(\d+)', line)
                if m:
                    return f"{m.group(1)}%"
                # Intel Mac: "CoreLoad" = 42
                m = re.search(r'"CoreLoad"\s*=\s*(\d+)', line)
                if m:
                    return f"{m.group(1)}%"
        except Exception:
            pass
        return "N/A"

    # ── 温度工具检测 ──────────────────────────────────────────

    def _detect_temp_tool(self):
        try:
            r = subprocess.run(["which", "osx-cpu-temp"], capture_output=True)
            if r.returncode == 0:
                return "osx-cpu-temp"
        except Exception:
            pass
        try:
            r = subprocess.run(["which", "powermetrics"], capture_output=True)
            if r.returncode == 0:
                return "powermetrics"
        except Exception:
            pass
        return None

    # ── 定时回调（只更新文字，不重建菜单） ────────────────────

    def _update(self, _):
        # 采集数据
        self._cpu = psutil.cpu_percent(interval=0)
        self._mem = psutil.virtual_memory().percent
        self._calc_net_speed()
        self._temp = self._get_temp()
        self._gpu = self._get_gpu()

        up_s = self._fmt_speed(self._up)
        dn_s = self._fmt_speed(self._down)

        # 更新菜单栏标题
        self.title = f"⚡{self._cpu:.0f}%  {self._mem:.0f}%  ↑{up_s} ↓{dn_s}"

        # 更新下拉菜单文字（原地更新，不创建新菜单项）
        self._item_cpu.title = f"🖥  CPU       {self._cpu:.1f}%"
        self._item_mem.title = f"🧠 内存       {self._mem:.1f}%"
        self._item_up.title = f"📤 上传速度    {up_s}B/s"
        self._item_dn.title = f"📥 下载速度    {dn_s}B/s"
        self._item_temp.title = f"🌡  CPU 温度   {self._temp}"
        self._item_gpu.title = f"🎮 GPU        {self._gpu}"
        self._item_proc.title = f"📊 进程数      {len(psutil.pids())}"
        self._item_uptime.title = f"⏱  开机时长   {self._fmt_uptime()}"


if __name__ == "__main__":
    SysMonApp().run()
