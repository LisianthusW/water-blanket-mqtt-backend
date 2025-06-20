#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报警配置文件
"""

ALARM_CONFIG = {
    # 报警开关
    'enable_connection_lost_alarm': False,     # 是否启用连接丢失报警
    'enable_device_alarm': True,               # 是否启用设备报警
    
    # 显示控制
    'console_output': False,                   # 是否在控制台显示报警
    'silent_mode': True,                       # 静默模式（只记录日志）
    
    # 报警级别过滤
    'min_alarm_level': 'MEDIUM',              # 最小报警级别 (LOW/MEDIUM/HIGH)
    
    # 报警冷却时间（秒）
    'connection_lost_cooldown': 300,          # 连接丢失报警冷却时间（5分钟）
    'device_alarm_cooldown': 60,              # 设备报警冷却时间（1分钟）
    
    # 设备过滤
    'ignored_devices': ['SB067'],             # 忽略报警的设备列表
}