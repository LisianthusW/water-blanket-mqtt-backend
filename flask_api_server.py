#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
睡眠毯数据 Flask API 服务器
功能：提供RESTful API接口查询睡眠毯设备数据
作者：TaskManager Pro
版本：1.1 - 修复版
日期：2025-01-27
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime
import json
from database_manager import MySQLDataManager

class SleepBlanketAPI:
    """睡眠毯API服务器"""
    
    def __init__(self, host='0.0.0.0', port=5000):
        self.app = Flask(__name__)
        CORS(self.app)  # 启用跨域支持
        
        # 初始化数据库管理器
        self.data_manager = MySQLDataManager()
        
        # 配置
        self.host = host
        self.port = port
        
        # 设置日志
        self._setup_logging()
        
        # 设置路由
        self._setup_routes()
        
        # 启动信息
        self.start_time = datetime.now()
        
        # 添加系统统计
        self.api_stats = {
            'start_time': self.start_time,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0
        }
    
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('flask_api.log'),
                logging.StreamHandler()
            ]
        )
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/', methods=['GET'])
        def root():
            """根路径"""
            return jsonify({
                'service': '睡眠毯数据API服务',
                'version': '1.1',
                'status': 'running',
                'start_time': self.start_time.isoformat(),
                'endpoints': {
                    'health': '/api/health',
                    'stats': '/api/stats',
                    'devices': '/api/devices',
                    'latest_data': '/api/data/latest',
                    'history_data': '/api/data/history',
                    'realtime_data': '/api/data/realtime',
                    'statistics': '/api/statistics',
                    'alarms': '/api/alarms',
                    'status_summary': '/api/status/summary'
                }
            })
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """健康检查"""
            self.api_stats['total_requests'] += 1
            try:
                self.api_stats['successful_requests'] += 1
                return jsonify({
                    'status': 'ok',
                    'timestamp': datetime.now().isoformat(),
                    'service': 'Sleep Blanket Data API',
                    'uptime_seconds': int((datetime.now() - self.start_time).total_seconds())
                })
            except Exception as e:
                self.api_stats['failed_requests'] += 1
                raise
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_api_stats():
            """获取API统计信息"""
            self.api_stats['total_requests'] += 1
            try:
                uptime = datetime.now() - self.start_time
                stats = {
                    'api_uptime_seconds': int(uptime.total_seconds()),
                    'api_start_time': self.start_time.isoformat(),
                    'total_api_requests': self.api_stats['total_requests'],
                    'successful_requests': self.api_stats['successful_requests'],
                    'failed_requests': self.api_stats['failed_requests'],
                    'success_rate': (self.api_stats['successful_requests'] / max(self.api_stats['total_requests'], 1)) * 100
                }
                
                self.api_stats['successful_requests'] += 1
                return jsonify({
                    'status': 'success',
                    'data': stats
                })
            except Exception as e:
                self.api_stats['failed_requests'] += 1
                logging.error(f"获取API统计失败: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/devices', methods=['GET'])
        def get_devices():
            """获取设备列表"""
            self.api_stats['total_requests'] += 1
            try:
                devices = self.data_manager.get_devices_list()
                self.api_stats['successful_requests'] += 1
                return jsonify({
                    'status': 'success',
                    'data': devices,
                    'count': len(devices)
                })
            except Exception as e:
                self.api_stats['failed_requests'] += 1
                logging.error(f"获取设备列表失败: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/data/latest', methods=['GET'])
        def get_latest_data():
            """获取最新数据"""
            self.api_stats['total_requests'] += 1
            try:
                device_id = request.args.get('device_id')
                limit = int(request.args.get('limit', 10))
                
                if limit > 100:  # 限制最大查询数量
                    limit = 100
                
                data = self.data_manager.get_latest_data(device_id, limit)
                self.api_stats['successful_requests'] += 1
                return jsonify({
                    'status': 'success',
                    'data': data,
                    'count': len(data),
                    'device_id': device_id,
                    'limit': limit
                })
            except Exception as e:
                self.api_stats['failed_requests'] += 1
                logging.error(f"获取最新数据失败: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/data/history', methods=['GET'])
        def get_history_data():
            """获取历史数据（分页）"""
            self.api_stats['total_requests'] += 1
            try:
                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', 20))
                device_id = request.args.get('device_id')
                start_time = request.args.get('start_time')
                end_time = request.args.get('end_time')
                
                # 限制每页最大数量
                if per_page > 100:
                    per_page = 100
                
                result = self.data_manager.get_paginated_data(
                    page, per_page, device_id, start_time, end_time
                )
                
                self.api_stats['successful_requests'] += 1
                return jsonify({
                    'status': 'success',
                    'data': result['data'],
                    'pagination': result['pagination'],
                    'filters': {
                        'device_id': device_id,
                        'start_time': start_time,
                        'end_time': end_time
                    }
                })
            except Exception as e:
                self.api_stats['failed_requests'] += 1
                logging.error(f"获取历史数据失败: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        # 错误处理
        @self.app.errorhandler(404)
        def not_found(error):
            self.api_stats['failed_requests'] += 1
            return jsonify({
                'status': 'error',
                'message': 'API endpoint not found',
                'code': 404
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            self.api_stats['failed_requests'] += 1
            return jsonify({
                'status': 'error',
                'message': 'Internal server error',
                'code': 500
            }), 500
    
    def run(self, debug=False):
        """运行Flask服务器"""
        print("=" * 60)
        print("🌐 睡眠毯数据API服务器")
        print(f"📍 服务地址: http://{self.host}:{self.port}")
        print(f"📊 数据库: {self.data_manager.db_config['host']}:{self.data_manager.db_config['port']}")
        print("=" * 60)
        print("📖 API接口:")
        print(f"  GET  http://{self.host}:{self.port}/api/health            - 健康检查")
        print(f"  GET  http://{self.host}:{self.port}/api/stats             - API统计信息")
        print(f"  GET  http://{self.host}:{self.port}/api/devices           - 设备列表")
        print(f"  GET  http://{self.host}:{self.port}/api/data/latest       - 最新数据")
        print(f"  GET  http://{self.host}:{self.port}/api/data/history      - 历史数据")
        print("=" * 60)
        print("按 Ctrl+C 停止服务")
        print("=" * 60)
        
        try:
            self.app.run(host=self.host, port=self.port, debug=debug, threaded=True)
        except KeyboardInterrupt:
            print("\n\n🛑 服务已停止")
        except Exception as e:
            logging.error(f"服务器运行错误: {e}")

def check_and_install_dependencies():
    """检查并安装依赖"""
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'pymysql': 'pymysql'
    }
    
    import subprocess
    import sys
    
    for package_name, pip_name in required_packages.items():
        try:
            __import__(package_name)
            print(f"✅ {pip_name} 已安装")
        except ImportError:
            print(f"❌ {pip_name} 未安装，正在安装...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
                print(f"✅ {pip_name} 安装完成")
            except subprocess.CalledProcessError:
                print(f"❌ {pip_name} 安装失败")
                return False
    
    return True

def main():
    """主函数"""
    print("🌐 睡眠毯数据Flask API服务器")
    print("🔧 独立运行版本")
    print("=" * 40)
    
    # 检查依赖
    print("🔍 检查依赖...")
    if not check_and_install_dependencies():
        print("❌ 依赖安装失败，程序退出")
        return
    
    print("✅ 依赖检查完成")
    print("=" * 40)
    
    # 创建并运行API服务器
    try:
        api_server = SleepBlanketAPI(host='0.0.0.0', port=5000)
        api_server.run(debug=False)
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()