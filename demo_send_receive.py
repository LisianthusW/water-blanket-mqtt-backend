#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQTT数据发送和接收演示脚本
简单演示如何发送数据和查看接收到的数据
"""

import paho.mqtt.client as mqtt
import time
import random
import json
import threading
from datetime import datetime
from server_config import SERVER_IP

class MQTTDemo:
    """MQTT演示类"""
    
    def __init__(self):
        self.server_ip = SERVER_IP
        self.port = 1883
        self.received_messages = []
        self.is_running = False
        
    def create_receiver(self):
        """创建接收器客户端"""
        client = mqtt.Client("demo_receiver")
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("✅ 接收器连接成功")
                # 订阅所有睡眠毯相关主题
                client.subscribe("sleep_blanket/+/data")
                client.subscribe("device/sleep_blanket")
                print("📡 已订阅主题: sleep_blanket/+/data, device/sleep_blanket")
            else:
                print(f"❌ 接收器连接失败: {rc}")
        
        def on_message(client, userdata, msg):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            message = msg.payload.decode('utf-8')
            topic = msg.topic
            
            # 存储接收到的消息
            received_data = {
                'timestamp': timestamp,
                'topic': topic,
                'message': message
            }
            self.received_messages.append(received_data)
            
            # 实时显示接收到的数据
            print(f"\n📥 [{timestamp}] 收到数据:")
            print(f"   主题: {topic}")
            print(f"   内容: {message}")
            
            # 解析数据（如果是睡眠毯数据格式）
            if "RAW:" in message:
                self.parse_and_display_data(message)
        
        client.on_connect = on_connect
        client.on_message = on_message
        return client
    
    def create_sender(self):
        """创建发送器客户端"""
        client = mqtt.Client("demo_sender")
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("✅ 发送器连接成功")
            else:
                print(f"❌ 发送器连接失败: {rc}")
        
        def on_publish(client, userdata, mid):
            print(f"📤 消息发送成功 (ID: {mid})")
        
        client.on_connect = on_connect
        client.on_publish = on_publish
        return client
    
    def parse_and_display_data(self, data_string):
        """解析并美化显示数据"""
        try:
            # 简单解析数据
            parts = data_string.split(', ')
            parsed = {}
            
            for part in parts:
                if ':' in part:
                    key, value = part.split(':', 1)
                    parsed[key.strip()] = value.strip()
            
            # 美化显示
            print("   📊 解析结果:")
            if parsed.get('RAW') != 'N/A':
                print(f"      原始值: {parsed.get('RAW', 'N/A')}")
                print(f"      RMS值: {parsed.get('RMS', 'N/A')}")
                print(f"      阈值: {parsed.get('TH', 'N/A')}")
                print(f"      状态: {'有人' if parsed.get('STATE') == '1' else '无人' if parsed.get('STATE') == '0' else 'N/A'}")
                print(f"      体动次数: {parsed.get('MOVE', 'N/A')}")
            
            connection_status = "🟢 在线" if parsed.get('CONNECTED') == '1' else "🔴 离线"
            alarm_status = "🚨 报警" if parsed.get('ALARM') == '1' else "✅ 正常"
            print(f"      连接状态: {connection_status}")
            print(f"      报警状态: {alarm_status}")
            
        except Exception as e:
            print(f"   ⚠️  数据解析失败: {e}")
    
    def generate_sample_data(self):
        """生成示例数据"""
        # 模拟真实的睡眠毯数据
        raw_value = random.randint(2800, 3200)
        rms_value = raw_value * 0.6 + random.uniform(-50, 50)
        threshold_value = rms_value + random.uniform(100, 300)
        state = random.choice([0, 1])  # 0=无人，1=有人
        movement_count = random.randint(0, 20)
        is_connected = random.choice([0, 1])  # 90%概率在线
        is_alarm = random.choice([0, 0, 0, 0, 1])  # 20%概率报警
        
        if is_connected:
            data = f"RAW:{raw_value}, RMS:{rms_value:.2f}, TH:{threshold_value:.2f}, STATE:{state}, MOVE:{movement_count}, CONNECTED:1, ALARM:{is_alarm}"
        else:
            data = f"RAW:N/A, RMS:N/A, TH:N/A, STATE:N/A, MOVE:N/A, CONNECTED:0, ALARM:{is_alarm}"
        
        return data
    
    def start_demo(self):
        """启动演示"""
        print("🛏️  MQTT数据发送接收演示")
        print("=" * 60)
        print(f"🖥️  服务器: {self.server_ip}:{self.port}")
        print("=" * 60)
        
        try:
            # 创建接收器
            receiver = self.create_receiver()
            receiver.connect(self.server_ip, self.port, 60)
            receiver.loop_start()
            
            # 等待接收器连接
            time.sleep(2)
            
            # 创建发送器
            sender = self.create_sender()
            sender.connect(self.server_ip, self.port, 60)
            sender.loop_start()
            
            # 等待发送器连接
            time.sleep(2)
            
            self.is_running = True
            
            print("\n🚀 开始演示...")
            print("💡 提示: 按 Ctrl+C 停止演示")
            print("=" * 60)
            
            message_count = 0
            
            while self.is_running:
                message_count += 1
                
                # 生成示例数据
                data = self.generate_sample_data()
                topic = f"sleep_blanket/SB{message_count:03d}/data"
                
                # 发送数据
                print(f"\n📤 [{datetime.now().strftime('%H:%M:%S')}] 发送第 {message_count} 条数据:")
                print(f"   主题: {topic}")
                print(f"   数据: {data}")
                
                sender.publish(topic, data, qos=1)
                
                # 等待一段时间
                time.sleep(3)
                
                # 每5条消息显示一次统计
                if message_count % 5 == 0:
                    self.show_statistics()
            
        except KeyboardInterrupt:
            print("\n\n⏹️  演示被用户停止")
        except Exception as e:
            print(f"\n❌ 演示过程出错: {e}")
        finally:
            self.is_running = False
            try:
                receiver.loop_stop()
                receiver.disconnect()
                sender.loop_stop()
                sender.disconnect()
            except:
                pass
            
            print("\n📊 演示结束统计:")
            self.show_final_statistics()
    
    def show_statistics(self):
        """显示统计信息"""
        total_received = len(self.received_messages)
        print(f"\n📈 当前统计: 已接收 {total_received} 条消息")
    
    def show_final_statistics(self):
        """显示最终统计"""
        total_received = len(self.received_messages)
        print(f"   总接收消息数: {total_received}")
        
        if self.received_messages:
            print(f"   首条消息时间: {self.received_messages[0]['timestamp']}")
            print(f"   末条消息时间: {self.received_messages[-1]['timestamp']}")
            
            # 统计主题
            topics = {}
            for msg in self.received_messages:
                topic = msg['topic']
                topics[topic] = topics.get(topic, 0) + 1
            
            print(f"   主题统计:")
            for topic, count in topics.items():
                print(f"     {topic}: {count} 条")
        
        print(f"\n💾 接收到的数据已保存在内存中，共 {total_received} 条")
        print("👋 演示完成！")

def main():
    """主函数"""
    demo = MQTTDemo()
    
    print("🎯 选择演示模式:")
    print("1. 自动演示 (自动发送和接收数据)")
    print("2. 仅接收模式 (只接收数据，不发送)")
    
    try:
        choice = input("\n请选择 (1-2): ").strip()
        
        if choice == "1":
            demo.start_demo()
        elif choice == "2":
            print("🛏️  仅接收模式")
            print("=" * 40)
            print(f"🖥️  服务器: {demo.server_ip}:{demo.port}")
            print("💡 按 Ctrl+C 停止接收")
            print("=" * 40)
            
            receiver = demo.create_receiver()
            receiver.connect(demo.server_ip, demo.port, 60)
            receiver.loop_start()
            
            print("🔄 等待接收数据...")
            
            while True:
                time.sleep(1)
        else:
            print("❌ 无效选择")
    
    except KeyboardInterrupt:
        print("\n👋 程序已退出")

if __name__ == "__main__":
    main()