#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQTT数据接收器 - MySQL版本
接收MQTT数据并存储到MySQL数据库
"""

import paho.mqtt.client as mqtt
import json
import logging
import time
from datetime import datetime
import threading
import re
from database_manager import MySQLDataManager
from server_config import get_mqtt_config, get_full_config
from alarm_config import ALARM_CONFIG

class MQTTReceiver:
    """MQTT数据接收器"""
    
    def __init__(self):
        self.config = get_full_config()
        self.mqtt_config = self.config['mqtt']
        self.alarm_config = ALARM_CONFIG
        
        # 初始化数据库管理器
        self.db_manager = MySQLDataManager()
        
        # 统计信息
        self.stats = {
            'total_received': 0,
            'total_processed': 0,
            'total_errors': 0,
            'start_time': datetime.now(),
            'last_message_time': None
        }
        
        # 设置日志
        self.setup_logging()
        
        # 创建MQTT客户端
        self.client = mqtt.Client("sleep_blanket_receiver")
        self.setup_mqtt_client()
        
        # 运行状态
        self.is_running = False
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mqtt_mysql_receiver.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_mqtt_client(self):
        """设置MQTT客户端"""
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.logger.info("✅ MQTT连接成功")
                # 订阅所有配置的主题
                for topic in self.mqtt_config['topics']:
                    client.subscribe(topic, qos=self.mqtt_config.get('qos', 1))
                    self.logger.info(f"📡 已订阅主题: {topic}")
            else:
                self.logger.error(f"❌ MQTT连接失败: {rc}")
        
        def on_message(client, userdata, msg):
            self.handle_message(msg)
        
        def on_disconnect(client, userdata, rc):
            if rc != 0:
                self.logger.warning(f"⚠️ MQTT连接意外断开: {rc}")
            else:
                self.logger.info("🔌 MQTT连接已断开")
        
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_disconnect = on_disconnect
        
        # 设置认证信息（如果有）
        if self.mqtt_config.get('username') and self.mqtt_config.get('password'):
            self.client.username_pw_set(
                self.mqtt_config['username'], 
                self.mqtt_config['password']
            )
    
    def handle_message(self, msg):
        """处理接收到的消息"""
        try:
            self.stats['total_received'] += 1
            self.stats['last_message_time'] = datetime.now()
            
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            self.logger.debug(f"📥 收到消息: {topic} -> {payload}")
            
            # 解析设备ID
            device_id = self.extract_device_id(topic)
            if not device_id:
                self.logger.warning(f"⚠️ 无法从主题提取设备ID: {topic}")
                return
            
            # 解析数据
            data_dict = self.parse_data(payload)
            if not data_dict:
                self.logger.warning(f"⚠️ 数据解析失败: {payload}")
                return
            
            # 添加时间戳
            data_dict['timestamp'] = datetime.now()
            
            # 存储到数据库
            if self.db_manager.insert_device_data(device_id, data_dict):
                self.stats['total_processed'] += 1
                self.logger.debug(f"✅ 数据已存储: {device_id}")
            else:
                self.stats['total_errors'] += 1
                self.logger.error(f"❌ 数据存储失败: {device_id}")
            
            # 检查报警
            if data_dict.get('is_alarm') == 1:
                self.handle_alarm(device_id, data_dict)
            
        except Exception as e:
            self.stats['total_errors'] += 1
            self.logger.error(f"❌ 处理消息失败: {e}")
    
    def extract_device_id(self, topic):
        """从主题中提取设备ID"""
        # 匹配 sleep_blanket/{device_id}/data 格式
        match = re.search(r'sleep_blanket/([^/]+)/data', topic)
        if match:
            return match.group(1)
        
        # 匹配其他格式
        if 'device/sleep_blanket' in topic:
            return 'GENERAL_DEVICE'
        
        if 'sensors/sleep_monitor' in topic:
            return 'MONITOR_SENSOR'
        
        return None
    
    def parse_data(self, payload):
        """解析数据负载"""
        try:
            # 尝试解析JSON格式
            if payload.startswith('{'):
                return json.loads(payload)
            
            # 解析自定义格式: RAW:1024, RMS:23.45, TH:25.0, STATE:1, MOVE:15, CONNECTED:1, ALARM:0
            data_dict = {}
            parts = payload.split(', ')
            
            for part in parts:
                if ':' in part:
                    key, value = part.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    # 处理不同类型的值
                    if value == 'N/A':
                        data_dict[f'{key}_value' if key in ['raw', 'rms', 'th'] else key] = None
                    elif key == 'raw':
                        data_dict['raw_value'] = int(value) if value.isdigit() else None
                    elif key == 'rms':
                        data_dict['rms_value'] = float(value) if value.replace('.', '').isdigit() else None
                    elif key == 'th':
                        data_dict['threshold_value'] = float(value) if value.replace('.', '').isdigit() else None
                    elif key == 'state':
                        data_dict['state'] = int(value) if value.isdigit() else None
                    elif key == 'move':
                        data_dict['movement_count'] = int(value) if value.isdigit() else None
                    elif key == 'connected':
                        data_dict['is_connected'] = int(value) if value.isdigit() else 1
                    elif key == 'alarm':
                        data_dict['is_alarm'] = int(value) if value.isdigit() else 0
            
            return data_dict
            
        except Exception as e:
            self.logger.error(f"❌ 数据解析错误: {e}")
            return None
    
    def handle_alarm(self, device_id, data_dict):
        """处理报警"""
        if not self.alarm_config.get('enable_device_alarm', True):
            return
        
        # 检查设备是否在忽略列表中
        if device_id in self.alarm_config.get('ignored_devices', []):
            return
        
        alarm_message = f"设备 {device_id} 触发报警"
        
        if not self.alarm_config.get('silent_mode', True):
            print(f"🚨 {alarm_message}")
        
        self.logger.warning(f"🚨 {alarm_message}")
    
    def start(self):
        """启动接收器"""
        try:
            self.logger.info("🚀 启动MQTT接收器...")
            self.logger.info(f"📡 连接到: {self.mqtt_config['broker_host']}:{self.mqtt_config['broker_port']}")
            
            # 连接MQTT代理
            self.client.connect(
                self.mqtt_config['broker_host'],
                self.mqtt_config['broker_port'],
                self.mqtt_config.get('keepalive', 60)
            )
            
            self.is_running = True
            
            # 启动统计线程
            stats_thread = threading.Thread(target=self.stats_reporter, daemon=True)
            stats_thread.start()
            
            # 开始循环
            self.client.loop_forever()
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ 接收到停止信号")
            self.stop()
        except Exception as e:
            self.logger.error(f"❌ 启动失败: {e}")
            raise
    
    def stop(self):
        """停止接收器"""
        self.is_running = False
        self.client.disconnect()
        self.db_manager.close_connection()
        self.logger.info("🛑 MQTT接收器已停止")
    
    def stats_reporter(self):
        """统计报告线程"""
        while self.is_running:
            time.sleep(60)  # 每分钟报告一次
            
            uptime = datetime.now() - self.stats['start_time']
            uptime_str = str(uptime).split('.')[0]  # 去掉微秒
            
            self.logger.info(
                f"📊 统计: 运行时间={uptime_str}, "
                f"接收={self.stats['total_received']}, "
                f"处理={self.stats['total_processed']}, "
                f"错误={self.stats['total_errors']}"
            )

def main():
    """主函数"""
    print("🛏️ 睡眠毯MQTT数据接收器 (MySQL版本)")
    print("=" * 50)
    
    try:
        receiver = MQTTReceiver()
        receiver.start()
    except Exception as e:
        print(f"❌ 程序运行失败: {e}")
        logging.error(f"程序运行失败: {e}")

if __name__ == "__main__":
    main()