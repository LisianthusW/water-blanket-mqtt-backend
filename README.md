# 水暖毯MQTT后端系统

一个基于Python的睡眠毯MQTT数据接收、处理和API服务后端系统，支持实时数据监控、历史数据查询和报警功能。

## 项目概述

本项目是一个完整的IoT数据处理后端系统，专门为睡眠毯设备设计，通过MQTT协议接收设备数据，存储到MySQL数据库，并提供RESTful API接口供前端应用调用。

## 主要功能

- 🔄 **MQTT数据接收**: 实时接收睡眠毯设备通过MQTT协议发送的数据
- 💾 **数据存储**: 将接收到的数据存储到MySQL数据库中
- 🚨 **智能报警**: 支持多级别报警系统，可配置报警阈值和通知方式
- 🌐 **RESTful API**: 提供完整的API接口，支持数据查询、设备管理等功能
- 📊 **实时监控**: 支持实时数据推送和状态监控
- 📈 **数据统计**: 提供数据统计和分析功能
- 🔧 **配置管理**: 灵活的配置文件支持，易于部署和维护

## 技术栈

- **Python 3.8+**: 主要开发语言
- **Flask**: Web框架，提供API服务
- **paho-mqtt**: MQTT客户端库
- **MySQL**: 主数据库
- **Redis**: 缓存和会话存储
- **Flask-CORS**: 跨域支持

## 项目结构

```
mtqq/
├── flask_api_server.py      # Flask API服务器主文件
├── mqtt_receiver_mysql.py   # MQTT数据接收器
├── database_manager.py      # 数据库管理器
├── server_config.py         # 服务器配置
├── alarm_config.py          # 报警配置
├── demo_send_receive.py     # 演示和测试脚本
├── config.json              # 主配置文件
├── env_example.txt          # 环境变量示例
├── vue_receive/             # 前端Vue.js应用
├── data/                    # 数据文件目录
└── __pycache__/            # Python缓存文件
```

## 快速开始

### 环境要求

- Python 3.8 或更高版本
- MySQL 5.7 或更高版本
- Redis (可选，用于缓存)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/LisianthusW/water-blanket-mqtt-backend.git
   cd water-blanket-mqtt-backend
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp env_example.txt .env
   # 编辑.env文件，配置数据库连接等信息
   ```

4. **配置数据库**
   - 创建MySQL数据库
   - 运行数据库初始化脚本

5. **启动服务**
   ```bash
   # 启动MQTT接收器
   python mqtt_receiver_mysql.py
   
   # 启动API服务器
   python flask_api_server.py
   ```

## API文档

### 基础信息
- **基础URL**: `http://localhost:5000`
- **认证方式**: 暂无（开发阶段）

### 主要端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/devices` | GET | 获取设备列表 |
| `/api/data/latest` | GET | 获取最新数据 |
| `/api/data/history` | GET | 获取历史数据 |
| `/api/statistics` | GET | 获取统计信息 |
| `/api/alarms` | GET | 获取报警信息 |

### 示例请求

```bash
# 获取设备列表
curl http://localhost:5000/api/devices

# 获取最新数据
curl http://localhost:5000/api/data/latest?device_id=device001&limit=10

# 获取历史数据
curl http://localhost:5000/api/data/history?page=1&per_page=20
```

## 配置说明

### config.json 配置文件

```json
{
  "broker_host": "your-mqtt-broker-host",
  "broker_port": 1883,
  "topics": [
    "sleep_blanket/+/data",
    "sleep_blanket/+/status"
  ],
  "alarm_settings": {
    "cooldown_seconds": 60,
    "enable_email_alerts": false
  }
}
```

### 环境变量配置

参考 `env_example.txt` 文件配置以下环境变量：

- `MYSQL_HOST`: MySQL服务器地址
- `MYSQL_USER`: 数据库用户名
- `MYSQL_PASSWORD`: 数据库密码
- `MYSQL_DATABASE`: 数据库名称
- `MQTT_BROKER_HOST`: MQTT代理服务器地址

## 开发说明

### 代码结构

- `flask_api_server.py`: Flask API服务器，提供RESTful接口
- `mqtt_receiver_mysql.py`: MQTT数据接收器，负责接收和处理设备数据
- `database_manager.py`: 数据库操作封装，提供数据CRUD操作
- `server_config.py`: 服务器配置管理
- `alarm_config.py`: 报警系统配置

### 数据流程

1. 设备通过MQTT协议发送数据到MQTT代理
2. MQTT接收器订阅相关主题，接收数据
3. 接收到的数据经过处理后存储到MySQL数据库
4. Flask API服务器提供接口供前端查询数据
5. 报警系统监控数据异常并发送通知

## 部署指南

### Docker 部署（推荐）

```bash
# 构建镜像
docker build -t water-blanket-backend .

# 运行容器
docker run -d -p 5000:5000 --name water-blanket-backend water-blanket-backend
```

### 传统部署

1. 配置Python虚拟环境
2. 安装依赖包
3. 配置数据库连接
4. 启动服务进程
5. 配置反向代理（Nginx）

## 监控和日志

- API访问日志: `flask_api.log`
- MQTT接收日志: `mqtt_mysql_receiver.log`
- 系统运行状态可通过 `/api/health` 端点查询

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目地址: [https://github.com/LisianthusW/water-blanket-mqtt-backend](https://github.com/LisianthusW/water-blanket-mqtt-backend)
- 问题反馈: [Issues](https://github.com/LisianthusW/water-blanket-mqtt-backend/issues)

## 更新日志

### v1.1.0 (2025-01-27)
- 修复Flask API服务器的稳定性问题
- 增加API统计功能
- 优化数据库连接管理
- 改进错误处理机制

### v1.0.0 (2025-01-20)
- 初始版本发布
- 基础MQTT数据接收功能
- Flask API服务器
- 数据库存储和查询
- 基础报警系统

## 任务进度

- [ ] 项目初始化和环境配置 - 2025-06-20
- [ ] 创建GitHub仓库 - 2025-06-20
- [ ] 上传项目文件到GitHub - 2025-06-20
- [ ] 编写项目文档 - 2025-06-20
- [ ] 配置CI/CD流水线 - 待定
- [ ] 添加单元测试 - 待定
- [ ] 性能优化 - 待定