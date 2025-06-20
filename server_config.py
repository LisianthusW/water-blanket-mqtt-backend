#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器配置文件
集中管理所有服务器地址和连接配置
"""

# 服务器基本信息
SERVER_IP = "154.219.127.234"
SERVER_NAME = "CentOS 7 Production Server"

# MQTT服务器配置
MQTT_CONFIG = {
    "broker_host": SERVER_IP,
    "broker_port": 1883,
    "websocket_port": 9001,
    "username": None,  # 如需认证请设置
    "password": None,  # 如需认证请设置
    "keepalive": 60,
    "qos": 1,
    "topics": [
        "sleep_blanket/+/data",
        "sleep_blanket/+/status", 
        "sleep_blanket/+/alarm",
        "device/sleep_blanket",
        "sensors/sleep_monitor"
    ]
}

# 数据库配置
DATABASE_CONFIG = {
    "mysql": {
        "host": SERVER_IP,
        "port": 3306,
        "database": "sleep_blanket_db",
        "user": "sleep_blanket_db",
        "password": "eWMS3aA58GnJiDyy"  # 请设置实际密码
    },
    "redis": {
        "host": SERVER_IP,
        "port": 6379,
        "db": 0,
        "password": None  # 如需认证请设置
    }
}

# 文件存储配置
STORAGE_CONFIG = {
    "data_directory": "./data/",
    "backup_directory": "./backup/",
    "log_directory": "./logs/",
    "csv_file": "device_data.csv",
    "json_file": "latest_data.json",
    "stats_file": "statistics.json",
    "alarm_log": "alarm_log.txt"
}

# 网络配置
NETWORK_CONFIG = {
    "connection_timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 5,
    "heartbeat_interval": 30
}

# 报警配置
ALARM_CONFIG = {
    "cooldown_seconds": 60,
    "enable_email_alerts": False,
    "email_recipients": [],
    "enable_log_file": True,
    "enable_console_output": True,
    "alarm_levels": {
        "low": {"threshold": 1, "color": "yellow"},
        "medium": {"threshold": 3, "color": "orange"}, 
        "high": {"threshold": 5, "color": "red"},
        "critical": {"threshold": 10, "color": "purple"}
    }
}

def get_mqtt_config():
    """获取MQTT配置"""
    return MQTT_CONFIG.copy()

def get_database_config():
    """获取数据库配置"""
    return DATABASE_CONFIG.copy()

def get_storage_config():
    """获取存储配置"""
    return STORAGE_CONFIG.copy()

def get_full_config():
    """获取完整配置"""
    return {
        "server": {
            "ip": SERVER_IP,
            "name": SERVER_NAME
        },
        "mqtt": MQTT_CONFIG,
        "database": DATABASE_CONFIG,
        "storage": STORAGE_CONFIG,
        "network": NETWORK_CONFIG,
        "alarm": ALARM_CONFIG
    }

def print_server_info():
    """打印服务器信息"""
    print("=" * 60)
    print(f"🖥️  服务器信息")
    print(f"📍 IP地址: {SERVER_IP}")
    print(f"🏷️  名称: {SERVER_NAME}")
    print(f"📡 MQTT端口: {MQTT_CONFIG['broker_port']}")
    print(f"🌐 WebSocket端口: {MQTT_CONFIG['websocket_port']}")
    print(f"🗄️  MySQL端口: {DATABASE_CONFIG['mysql']['port']}")
    print(f"🔄 Redis端口: {DATABASE_CONFIG['redis']['port']}")
    print("=" * 60)

if __name__ == "__main__":
    print_server_info()
    
    # 测试配置
    import json
    config = get_full_config()
    print("\n📋 完整配置:")
    print(json.dumps(config, indent=2, ensure_ascii=False))