#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
km_api_client.py

集成 WCH USB Composite KM 与 PS/2 模拟两大功能的上位机控制工具。

================ USB 模式 命令说明 =================
  rel               切换到 相对 (REL) 鼠标模式
  abs               切换到 绝对 (ABS) 鼠标模式
  key               切换到 键盘 (KEY) 模式
  idle              返回 默认 (IDLE) 模式
  local             启用 本地 (LOCAL) 控制
  remote            启用 远程 (REMOTE) 控制
  move dx dy [opts] REL 模式下：相对移动 dx,dy
                    可选参数：
                      --left   按下左键
                      --right  按下右键
                      --middle 按下中键
                      --wheel n 滚轮位移（IntelliMouse）
  abs-move x y [opts]
                    ABS 模式下：绝对定位 x,y
                      (--left/--right/--middle/--wheel 同上)
  res w h           设置屏幕分辨率 w×h（影响 ABS 模式映射）
  text CONTENT      KEY 模式下：发送字符串 CONTENT
  combo COMBO       KEY 模式下：发送组合键 COMBO（如 CTRL+ALT+DEL）
  fwinfo            查询固件版本信息
  status            查询当前模式与 LOCAL/REMOTE 状态
  debug-on          打开调试日志输出
  debug-off         关闭调试日志输出
  reboot            软件复位 MCU

================ PS/2 模拟 命令说明 ================
  sim-on            进入 PS/2 模拟（断开输入，MCU 侧接地输出）
  sim-off           退出 PS/2 模拟（恢复非干扰状态）
  mouse             切换到 PS/2 鼠标模式
  key               切换到 PS/2 键盘模式
  move dx dy [opts] PS/2 鼠标：dx,dy,left,right,middle[,wheel]
  type TEXT         PS/2 键盘：发送 TEXT 或 组合键
  exit              退出当前 PS/2 模式
  reboot            软件复位 MCU

依赖：pyserial

用法示例：
  # USB 自动匹配串口
  python km_api_client.py usb rel
  python km_api_client.py usb move 10 -5 --left --wheel 1
  python km_api_client.py usb res 1920 1080
  python km_api_client.py usb text "Hello World"
  python km_api_client.py usb status
  python km_api_client.py usb fwinfo

  # PS/2 自动匹配串口
  python km_api_client.py ps2 sim-on
  python km_api_client.py ps2 mouse
  python km_api_client.py ps2 move 5 5 --right
  python km_api_client.py ps2 type "CTRL+ALT+DEL"
  python km_api_client.py ps2 exit
"""

import serial
import serial.tools.list_ports
import time
import argparse


class CompositeKMController:
    """
    USB Composite KM 控制器封装。

    方法映射：
      set_mode_rel()       ->  #0xA1@USBcmd
      set_mode_abs()       ->  #0xA2@USBcmd
      set_mode_key()       ->  #0xB2@USBcmd
      return_idle()        ->  #0xZ26@CMD
      enable_local()       ->  #0xC3@USBcmd01
      enable_remote()      ->  #0xC3@USBcmd10
      set_resolution(w,h)  ->  #0xD5@USBcmd:<w>x<h>
      get_firmware_info()  ->  #0xW23@FH
      get_status()         ->  #0xX24@GET
      enable_debug()       ->  #0xY25@DEG1
      disable_debug()      ->  #0xY25@DEG0
      reboot()             ->  #0xZ26@RET

      move_rel(dx,dy,...)  -> REL 模式数据包
      move_abs(x,y,...)    -> ABS 模式数据包
      send_text(text)      -> KEY 模式发送文本
      send_combo(combo)    -> KEY 模式发送组合键
    """
    DEFAULT_BAUDRATE = 115200
    WAIT = 0.05

    CMD_REL_MODE   = "#0xA1@USBcmd"
    CMD_ABS_MODE   = "#0xA2@USBcmd"
    CMD_KEY_MODE   = "#0xB2@USBcmd"
    CMD_LOCAL_ON   = "#0xC3@USBcmd01"
    CMD_REMOTE_ON  = "#0xC3@USBcmd10"
    CMD_RESOLUTION = "#0xD5@USBcmd"
    CMD_FW_INFO    = "#0xW23@FH"
    CMD_GET_STATUS = "#0xX24@GET"
    CMD_DEBUG_OFF  = "#0xY25@DEG0"
    CMD_DEBUG_ON   = "#0xY25@DEG1"
    CMD_IDLE       = "#0xZ26@CMD"
    CMD_REBOOT     = "#0xZ26@RET"

    def __init__(self, port=None, baudrate=None, timeout=0.5):
        self.ser = serial.Serial(
            self._find_port(port),
            baudrate or self.DEFAULT_BAUDRATE,
            timeout=timeout
        )
        time.sleep(0.1)

    def _find_port(self, port):
        """自动匹配 CH340/WCH 串口，或使用手动指定端口。"""
        if port:
            return port
        for p in serial.tools.list_ports.comports():
            if "USB-SERIAL CH340" in p.description or "WCH" in p.description:
                return p.device
        raise RuntimeError("未找到 USB Composite KM 串口设备，请使用 --port 指定")

    def _send(self, cmd=None, param=None):
        """底层组合并发送 cmd:param、单独 cmd 或单独 param。"""
        if cmd and param:
            pkt = f"{cmd}:{param}\r\n"
        elif cmd:
            pkt = f"{cmd}\r\n"
        elif param:
            pkt = f"{param}\r\n"
        else:
            return
        self.ser.write(pkt.encode())
        time.sleep(self.WAIT)

    # —————— 模式与控制 ——————
    def set_mode_rel(self):      self._send(cmd=self.CMD_REL_MODE)
    def set_mode_abs(self):      self._send(cmd=self.CMD_ABS_MODE)
    def set_mode_key(self):      self._send(cmd=self.CMD_KEY_MODE)
    def return_idle(self):       self._send(cmd=self.CMD_IDLE)
    def enable_local(self):      self._send(cmd=self.CMD_LOCAL_ON)
    def enable_remote(self):     self._send(cmd=self.CMD_REMOTE_ON)
    def set_resolution(self, w, h): self._send(cmd=self.CMD_RESOLUTION, param=f"{w}x{h}")
    def get_firmware_info(self): self._send(cmd=self.CMD_FW_INFO)
    def get_status(self):        self._send(cmd=self.CMD_GET_STATUS)
    def enable_debug(self):      self._send(cmd=self.CMD_DEBUG_ON)
    def disable_debug(self):     self._send(cmd=self.CMD_DEBUG_OFF)
    def reboot(self):            self._send(cmd=self.CMD_REBOOT)

    # —————— 鼠标 & 键盘 ——————
    def move_rel(self, dx, dy,
                 left=False, right=False,
                 middle=False, wheel=0):
        flags = (1 if left else 0, 1 if right else 0, 1 if middle else 0)
        payload = f"{dx},{dy},{flags[0]},{flags[1]},{flags[2]},{wheel}"
        self._send(param=payload)

    def move_abs(self, x, y,
                 left=False, right=False,
                 middle=False, wheel=0):
        flags = (1 if left else 0, 1 if right else 0, 1 if middle else 0)
        payload = f"{x},{y},{flags[0]},{flags[1]},{flags[2]},{wheel}"
        self._send(param=payload)

    def send_text(self, text):   self._send(param=text)
    def send_combo(self, combo): self.send_text(combo)

    def close(self):
        if self.ser.is_open:
            self.ser.close()


class PS2Controller:
    """
    PS/2 模拟控制器封装，方法与底层命令对应：
      enter_sim_mode(), exit_sim_mode(),
      set_mode_mouse(), set_mode_keyboard(),
      send_mouse(), send_keys(), exit_mode(), reboot()
    """
    DEFAULT_BAUDRATE = 115200
    WAIT = 0.05

    CMD_SIM_ON     = "#0xC3@PS2cmd10"
    CMD_SIM_OFF    = "#0xC3@PS2cmd01"
    CMD_MOUSE_MODE = "#0xA1@PS2cmd"
    CMD_KEY_MODE   = "#0xB2@PS2cmd"
    CMD_EXIT       = "#0xZ26@CMD"
    CMD_REBOOT     = "#0xZ26@RET"

    def __init__(self, port=None, baudrate=None, timeout=0.5):
        self.ser = serial.Serial(
            self._find_port(port),
            baudrate or self.DEFAULT_BAUDRATE,
            timeout=timeout
        )
        time.sleep(0.1)

    def _find_port(self, port):
        if port:
            return port
        for p in serial.tools.list_ports.comports():
            if "USB-SERIAL CH340" in p.description or "WCH" in p.description:
                return p.device
        raise RuntimeError("未找到 PS/2 串口设备，请使用 --port 指定")

    def _send(self, cmd):
        self.ser.write((cmd + "\r\n").encode())
        #time.sleep(self.WAIT)
        #self.WAIT = 0.05  # Define a wait time in seconds

        #if self.ser.in_waiting:
            #resp = self.ser.readline().decode(errors="ignore").strip()
            #print("[MCU]", resp)

    def enter_sim_mode(self):    self._send(self.CMD_SIM_ON)
    def exit_sim_mode(self):     self._send(self.CMD_SIM_OFF)
    def set_mode_mouse(self):    self._send(self.CMD_MOUSE_MODE)
    def set_mode_keyboard(self): self._send(self.CMD_KEY_MODE)
    def exit_mode(self):         self._send(self.CMD_EXIT)
    def reboot(self):            self._send(self.CMD_REBOOT)

    def send_mouse(self, dx, dy,
                   left=False, right=False,
                   middle=False, wheel=None):
        flags = (1 if left else 0, 1 if right else 0, 1 if middle else 0)
        if wheel is None:
            payload = f"{dx},{dy},{flags[0]},{flags[1]},{flags[2]}"
        else:
            payload = f"{dx},{dy},{flags[0]},{flags[1]},{flags[2]},{wheel}"
        self._send(payload)

    def send_keys(self, data):   self._send(data)

    def close(self):
        if self.ser.is_open:
            self.ser.close()


def main():
    parser = argparse.ArgumentParser(
        description="KM 上位机控制工具 (USB & PS/2 模式)"
    )
    sub_if = parser.add_subparsers(
        dest="interface", required=True,
        help="选择要使用的接口类型：usb 或 ps2"
    )

    # USB 子命令
    usb = sub_if.add_parser("usb", help="USB Composite KM 操作")
    usb.add_argument(
        "-p", "--port",
        help="串口号 (如 COM3 或 /dev/ttyUSB0)，不指定时自动匹配 CH340/WCH"
    )
    usbc = usb.add_subparsers(dest="cmd", required=True, help="USB 功能")

    for name in ("rel", "abs", "key", "idle", "local", "remote",
                 "fwinfo", "status", "debug-on", "debug-off", "reboot"):
        usbc.add_parser(name, help=name)

    m1 = usbc.add_parser("move", help="REL 模式 下 相对 移动")
    m1.add_argument("dx", type=int, help="X 轴 相对 位移（正右，负左）")
    m1.add_argument("dy", type=int, help="Y 轴 相对 位移（正下，负上）")
    m1.add_argument("--left",   action="store_true", help="按下 左键")
    m1.add_argument("--right",  action="store_true", help="按下 右键")
    m1.add_argument("--middle", action="store_true", help="按下 中键")
    m1.add_argument("--wheel",  type=int, default=0, help="滚轮 位移")

    m2 = usbc.add_parser("abs-move", help="ABS 模式 下 绝对 定位")
    m2.add_argument("x", type=int, help="X 轴 绝对 坐标")
    m2.add_argument("y", type=int, help="Y 轴 绝对 坐标")
    m2.add_argument("--left",   action="store_true", help="按下 左键")
    m2.add_argument("--right",  action="store_true", help="按下 右键")
    m2.add_argument("--middle", action="store_true", help="按下 中键")
    m2.add_argument("--wheel",  type=int, default=0, help="滚轮 位移")

    r = usbc.add_parser("res", help="设置 屏幕 分辨率")
    r.add_argument("width", type=int, help="屏幕 宽度")
    r.add_argument("height", type=int, help="屏幕 高度")

    t1 = usbc.add_parser("text", help="KEY 模式 下 发送 文本")
    t1.add_argument("content", help="要 发送 的 文本")

    t2 = usbc.add_parser("combo", help="KEY 模式 下 发送 组合键")
    t2.add_argument("combo", help="例如 CTRL+ALT+DEL")

    # PS/2 子命令
    ps2 = sub_if.add_parser("ps2", help="PS/2 模拟 操作")
    ps2.add_argument(
        "-p", "--port", help="串口号，不指定时自动匹配 CH340/WCH"
    )
    ps2c = ps2.add_subparsers(dest="action", required=True, help="PS/2 功能")

    for name in ("sim-on", "sim-off", "mouse", "key", "exit", "reboot"):
        ps2c.add_parser(name, help=name)

    pm = ps2c.add_parser("move", help="PS/2 鼠标 模式 下 发送 移动")
    pm.add_argument("dx", type=int, help="X 轴 位移")
    pm.add_argument("dy", type=int, help="Y 轴 位移")
    pm.add_argument("--left",   action="store_true", help="按下 左键")
    pm.add_argument("--right",  action="store_true", help="按下 右键")
    pm.add_argument("--middle", action="store_true", help="按下 中键")
    pm.add_argument("--wheel",  type=int, default=None, help="滚轮 位移")

    pt = ps2c.add_parser("type", help="PS/2 键盘 模式 下 发送 文本/组合键")
    pt.add_argument("text", help="要 发送 的 文本 或 组合键")

    args = parser.parse_args()

    if args.interface == "usb":
        km = CompositeKMController(port=args.port)
        try:
            cmd = args.cmd
            if cmd == "rel":
                km.set_mode_rel()
            elif cmd == "abs":
                km.set_mode_abs()
            elif cmd == "key":
                km.set_mode_key()
            elif cmd == "idle":
                km.return_idle()
            elif cmd == "local":
                km.enable_local()
            elif cmd == "remote":
                km.enable_remote()
            elif cmd == "fwinfo":
                km.get_firmware_info()
            elif cmd == "status":
                km.get_status()
            elif cmd == "debug-on":
                km.enable_debug()
            elif cmd == "debug-off":
                km.disable_debug()
            elif cmd == "reboot":
                km.reboot()
            elif cmd == "move":
                km.move_rel(
                    args.dx, args.dy,
                    left=args.left,
                    right=args.right,
                    middle=args.middle,
                    wheel=args.wheel
                )
            elif cmd == "abs-move":
                km.move_abs(
                    args.x, args.y,
                    left=args.left,
                    right=args.right,
                    middle=args.middle,
                    wheel=args.wheel
                )
            elif cmd == "res":
                km.set_resolution(args.width, args.height)
            elif cmd == "text":
                km.set_mode_key()
                km.send_text(args.content)
            elif cmd == "combo":
                km.set_mode_key()
                km.send_combo(args.combo)
        finally:
            km.close()
    else:
        api = PS2Controller(port=args.port)
        try:
            act = args.action
            if act == "sim-on":
                api.enter_sim_mode()
            elif act == "sim-off":
                api.exit_sim_mode()
            elif act == "mouse":
                api.set_mode_mouse()
            elif act == "key":
                api.set_mode_keyboard()
            elif act == "exit":
                api.exit_mode()
            elif act == "reboot":
                api.reboot()
            elif act == "move":
                api.send_mouse(
                    args.dx, args.dy,
                    left=args.left,
                    right=args.right,
                    middle=args.middle,
                    wheel=args.wheel
                )
            elif act == "type":
                api.send_keys(args.text)
        finally:
            api.close()


if __name__ == "__main__":
    main()
