#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理器
负责MySQL数据库的连接、数据存储和查询操作
"""

import pymysql
import logging
from datetime import datetime, timedelta
import json
from server_config import get_database_config

class MySQLDataManager:
    """MySQL数据库管理器"""
    
    def __init__(self):
        self.db_config = get_database_config()['mysql']
        self.connection = None
        self.setup_logging()
        self.connect_database()
        self.create_tables()
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def connect_database(self):
        """连接数据库"""
        try:
            self.connection = pymysql.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                charset='utf8mb4',
                autocommit=True
            )
            self.logger.info(f"✅ 数据库连接成功: {self.db_config['host']}:{self.db_config['port']}")
        except Exception as e:
            self.logger.error(f"❌ 数据库连接失败: {e}")
            raise
    
    def create_tables(self):
        """创建必要的数据表"""
        try:
            cursor = self.connection.cursor()
            
            # 创建设备数据表
            create_device_data_table = """
            CREATE TABLE IF NOT EXISTS device_data (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                device_id VARCHAR(50) NOT NULL,
                raw_value INT,
                rms_value DECIMAL(10,2),
                threshold_value DECIMAL(10,2),
                state TINYINT,
                movement_count INT,
                is_connected TINYINT DEFAULT 1,
                is_alarm TINYINT DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_device_id (device_id),
                INDEX idx_timestamp (timestamp),
                INDEX idx_device_timestamp (device_id, timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            
            # 创建报警记录表
            create_alarm_table = """
            CREATE TABLE IF NOT EXISTS alarm_records (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                device_id VARCHAR(50) NOT NULL,
                alarm_type VARCHAR(50) NOT NULL,
                alarm_level VARCHAR(20) NOT NULL,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved TINYINT DEFAULT 0,
                INDEX idx_device_id (device_id),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            
            cursor.execute(create_device_data_table)
            cursor.execute(create_alarm_table)
            cursor.close()
            
            self.logger.info("✅ 数据表创建/检查完成")
            
        except Exception as e:
            self.logger.error(f"❌ 创建数据表失败: {e}")
            raise
    
    def insert_device_data(self, device_id, data_dict):
        """插入设备数据"""
        try:
            cursor = self.connection.cursor()
            
            sql = """
            INSERT INTO device_data 
            (device_id, raw_value, rms_value, threshold_value, state, 
             movement_count, is_connected, is_alarm, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                device_id,
                data_dict.get('raw_value'),
                data_dict.get('rms_value'),
                data_dict.get('threshold_value'),
                data_dict.get('state'),
                data_dict.get('movement_count'),
                data_dict.get('is_connected', 1),
                data_dict.get('is_alarm', 0),
                data_dict.get('timestamp', datetime.now())
            )
            
            cursor.execute(sql, values)
            cursor.close()
            
            self.logger.debug(f"📊 设备数据已保存: {device_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 插入设备数据失败: {e}")
            return False
    
    def get_devices_list(self):
        """获取设备列表"""
        try:
            cursor = self.connection.cursor()
            
            sql = """
            SELECT device_id, 
                   COUNT(*) as total_records,
                   MAX(timestamp) as last_update,
                   AVG(CASE WHEN is_connected = 1 THEN 1 ELSE 0 END) * 100 as online_rate
            FROM device_data 
            GROUP BY device_id 
            ORDER BY last_update DESC
            """
            
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            
            devices = []
            for row in results:
                devices.append({
                    'device_id': row[0],
                    'total_records': row[1],
                    'last_update': row[2].isoformat() if row[2] else None,
                    'online_rate': round(row[3], 2) if row[3] else 0
                })
            
            return devices
            
        except Exception as e:
            self.logger.error(f"❌ 获取设备列表失败: {e}")
            return []
    
    def get_latest_data(self, device_id=None, limit=10):
        """获取最新数据"""
        try:
            cursor = self.connection.cursor()
            
            if device_id:
                sql = """
                SELECT * FROM device_data 
                WHERE device_id = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
                """
                cursor.execute(sql, (device_id, limit))
            else:
                sql = """
                SELECT * FROM device_data 
                ORDER BY timestamp DESC 
                LIMIT %s
                """
                cursor.execute(sql, (limit,))
            
            results = cursor.fetchall()
            cursor.close()
            
            data = []
            for row in results:
                data.append({
                    'id': row[0],
                    'device_id': row[1],
                    'raw_value': row[2],
                    'rms_value': float(row[3]) if row[3] else None,
                    'threshold_value': float(row[4]) if row[4] else None,
                    'state': row[5],
                    'movement_count': row[6],
                    'is_connected': row[7],
                    'is_alarm': row[8],
                    'timestamp': row[9].isoformat() if row[9] else None
                })
            
            return data
            
        except Exception as e:
            self.logger.error(f"❌ 获取最新数据失败: {e}")
            return []
    
    def get_paginated_data(self, page=1, per_page=20, device_id=None, start_time=None, end_time=None):
        """获取分页数据"""
        try:
            cursor = self.connection.cursor()
            
            # 构建查询条件
            conditions = []
            params = []
            
            if device_id:
                conditions.append("device_id = %s")
                params.append(device_id)
            
            if start_time:
                conditions.append("timestamp >= %s")
                params.append(start_time)
            
            if end_time:
                conditions.append("timestamp <= %s")
                params.append(end_time)
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            # 获取总数
            count_sql = f"SELECT COUNT(*) FROM device_data {where_clause}"
            cursor.execute(count_sql, params)
            total_count = cursor.fetchone()[0]
            
            # 获取分页数据
            offset = (page - 1) * per_page
            data_sql = f"""
            SELECT * FROM device_data {where_clause}
            ORDER BY timestamp DESC 
            LIMIT %s OFFSET %s
            """
            
            cursor.execute(data_sql, params + [per_page, offset])
            results = cursor.fetchall()
            cursor.close()
            
            data = []
            for row in results:
                data.append({
                    'id': row[0],
                    'device_id': row[1],
                    'raw_value': row[2],
                    'rms_value': float(row[3]) if row[3] else None,
                    'threshold_value': float(row[4]) if row[4] else None,
                    'state': row[5],
                    'movement_count': row[6],
                    'is_connected': row[7],
                    'is_alarm': row[8],
                    'timestamp': row[9].isoformat() if row[9] else None
                })
            
            # 计算分页信息
            total_pages = (total_count + per_page - 1) // per_page
            
            return {
                'data': data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ 获取分页数据失败: {e}")
            return {'data': [], 'pagination': {}}
    
    def get_statistics(self, device_id=None, hours=24):
        """获取统计数据"""
        try:
            cursor = self.connection.cursor()
            
            # 时间范围
            start_time = datetime.now() - timedelta(hours=hours)
            
            if device_id:
                sql = """
                SELECT 
                    COUNT(*) as total_records,
                    AVG(CASE WHEN is_connected = 1 THEN 1 ELSE 0 END) * 100 as online_rate,
                    SUM(CASE WHEN is_alarm = 1 THEN 1 ELSE 0 END) as alarm_count,
                    AVG(CASE WHEN state = 1 THEN 1 ELSE 0 END) * 100 as occupancy_rate,
                    AVG(movement_count) as avg_movement
                FROM device_data 
                WHERE device_id = %s AND timestamp >= %s
                """
                cursor.execute(sql, (device_id, start_time))
            else:
                sql = """
                SELECT 
                    COUNT(*) as total_records,
                    AVG(CASE WHEN is_connected = 1 THEN 1 ELSE 0 END) * 100 as online_rate,
                    SUM(CASE WHEN is_alarm = 1 THEN 1 ELSE 0 END) as alarm_count,
                    AVG(CASE WHEN state = 1 THEN 1 ELSE 0 END) * 100 as occupancy_rate,
                    AVG(movement_count) as avg_movement
                FROM device_data 
                WHERE timestamp >= %s
                """
                cursor.execute(sql, (start_time,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'total_records': result[0],
                    'online_rate': round(result[1], 2) if result[1] else 0,
                    'alarm_count': result[2],
                    'occupancy_rate': round(result[3], 2) if result[3] else 0,
                    'avg_movement': round(result[4], 2) if result[4] else 0,
                    'time_range_hours': hours
                }
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"❌ 获取统计数据失败: {e}")
            return {}
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.logger.info("🔌 数据库连接已关闭")

# 测试代码
if __name__ == "__main__":
    try:
        db_manager = MySQLDataManager()
        
        # 测试获取设备列表
        devices = db_manager.get_devices_list()
        print(f"📱 发现 {len(devices)} 个设备")
        
        for device in devices[:5]:  # 只显示前5个
            print(f"  - {device['device_id']}: {device['total_records']} 条记录")
        
        # 测试获取最新数据
        latest_data = db_manager.get_latest_data(limit=5)
        print(f"\n📊 最新 {len(latest_data)} 条数据:")
        
        for data in latest_data:
            print(f"  - {data['device_id']}: {data['timestamp']}")
        
        db_manager.close_connection()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")