# Local Intelligence Hub - Operation Runbook

## 项目定位

Local Intelligence Hub 是一个本地情报聚合工具，用于收集和分析来自多个公共数据源的世界事件、科技、财经、科学和加密货币市场数据。

**重要声明**：
- 本工具仅供信息聚合用途
- **不是**金融或投资建议
- 所有信息应在使用前进行验证
- 用户对基于本工具数据的决策承担全部责任

## 一次性运行

初始化数据库、获取数据、生成报告：

```bash
bash intelligence_hub/scripts/run_once.sh
```

这将按顺序执行：
1. `python3 intelligence_hub/src/main.py init-db` - 初始化数据库
2. `python3 intelligence_hub/src/main.py fetch-once` - 从所有启用的数据源获取数据
3. `python3 intelligence_hub/src/main.py digest` - 生成每日摘要
4. `python3 intelligence_hub/src/main.py status` - 显示当前状态

## Dashboard 启动

启动 Web Dashboard（默认端口 8765）：

```bash
bash intelligence_hub/scripts/serve.sh
```

然后在浏览器中打开：http://127.0.0.1:8765

Dashboard 功能：
- 查看所有聚合的新闻/数据项
- 按分类和来源过滤
- 按重要性分数排序
- 导出 JSON 格式数据

## Watch 模式

持续轮询数据源，每 5 分钟更新一次：

```bash
bash intelligence_hub/scripts/watch.sh
```

或指定间隔（秒）：

```bash
bash intelligence_hub/scripts/watch.sh 600
```

Watch 模式特点：
- 周期性执行 fetch-once 和 digest
- 每次生成新的摘要报告
- 安全的 Ctrl+C 退出处理

## tmux 使用建议

为了在后台持续运行 Dashboard 或 Watch 模式，建议使用 tmux：

```bash
# 创建新会话
tmux new -s intelligence

# 在会话中启动 Dashboard
bash intelligence_hub/scripts/serve.sh

# 分离会话（保留在后台）
# 按 Ctrl+B，然后按 D

# 恢复会话
tmux attach -t intelligence

# 查看所有会话
tmux ls

# 关闭会话
tmux kill-session -t intelligence
```

## 常见问题

### 如何确认没有提交运行生成物？

检查 `.gitignore` 文件确认以下规则存在：

```gitignore
intelligence_hub/data/*.db
intelligence_hub/logs/*.log
intelligence_hub/reports/latest_digest.md
__pycache__/
*.pyc
```

运行以下命令确认没有生成物在暂存区：

```bash
git status --short | grep -E "intelligence_hub/(data|logs|reports)"
```

### 如何清理本地数据库和日志？

```bash
# 删除数据库
rm -f intelligence_hub/data/intelligence.db

# 删除日志
rm -f intelligence_hub/logs/fetch.log

# 删除生成的摘要
rm -f intelligence_hub/reports/latest_digest.md

# 删除所有 Python 缓存
find intelligence_hub -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find intelligence_hub -name "*.pyc" -delete
```

## 数据源失败处理

### GDELT 返回 0 条数据

**原因**：
- API 临时不可用
- 网络连接问题
- API 返回空结果

**处理方法**：
1. 检查日志：`cat intelligence_hub/logs/fetch.log`
2. 稍后重试：`python3 intelligence_hub/src/main.py fetch-once`
3. 调整关键词或 timespan 参数

### CoinGecko 速率限制

**原因**：
- 免费 API 有请求限制
- 短时间内请求过多

**处理方法**：
1. 等待 1-2 分钟
2. 减少轮询频率
3. 只保留必要的币种配置

### RSS 源失败

**原因**：
- 目标服务器不可用
- 网络问题
- 格式解析错误

**处理方法**：
1. 检查单个 RSS 源是否可用
2. 移除不可用的源或更换 URL
3. RSS 源失败不会影响其他数据源

### SEC EDGAR 访问被拒绝

**原因**：
- 缺少有效的 User-Agent
- 请求过于频繁

**处理方法**：
1. 编辑 `config/sources.json`
2. 更新 `sec_edgar.user_agent` 为真实的联系信息
3. 例如：`"user_agent": "Your Name your@email.com"`

## 如何添加自定义 RSS

编辑 `intelligence_hub/config/sources.json`：

```json
{
  "sources": {
    "rss": {
      "enabled": true,
      "feeds": [
        {
          "name": "Your Feed Name",
          "category": "tech",
          "url": "https://example.com/feed.xml"
        }
      ]
    }
  }
}
```

支持的分类：
- `world` - 国际新闻
- `tech` - 科技
- `science` - 科学
- `finance` - 财经
- `crypto` - 加密货币

## 如何调整 Watchlist

Watchlist 允许你配置自定义关键词，被匹配的项目会获得额外加分并在摘要中优先显示。

编辑 `intelligence_hub/config/sources.json`：

```json
{
  "watchlist": {
    "enabled": true,
    "keywords": [
      "OpenAI",
      "Anthropic",
      "Nvidia",
      "semiconductor",
      "AI",
      "central bank",
      "inflation",
      "recession",
      "war",
      "sanctions",
      "Bitcoin",
      "Ethereum"
    ]
  }
}
```

关键词匹配规则：
- 不区分大小写
- 匹配标题或摘要中的关键词
- 匹配项获得 +15 到 +23 加分

## 配置说明

### 主要配置项

| 配置 | 说明 | 默认值 |
|------|------|--------|
| `dashboard_host` | Dashboard 监听地址 | 127.0.0.1 |
| `dashboard_port` | Dashboard 端口 | 8765 |
| `fetch.default_limit` | 默认获取数量 | 20 |
| `fetch.min_watch_interval_seconds` | 最小轮询间隔 | 60 秒 |

### 数据源配置

每个数据源可单独启用/禁用：

```json
{
  "sources": {
    "gdelt": {
      "enabled": true,
      "limit": 20,
      "timespan": "1d"
    },
    "coingecko": {
      "enabled": true,
      "coins": ["bitcoin", "ethereum", "solana"]
    }
  }
}
```

## 安全注意事项

1. **不要**提交 API 密钥或敏感信息到版本控制
2. **不要**在公共网络访问 Dashboard（默认绑定 127.0.0.1）
3. **始终**验证来自外部源的信息
4. **不要**将本工具用于自动交易或投资决策

## 获取帮助

```bash
# 查看所有可用命令
python3 intelligence_hub/src/main.py

# 运行测试
python3 intelligence_hub/tests/test_basic.py

# 查看当前状态
python3 intelligence_hub/src/main.py status
```

## 免责声明

本工具聚合的新闻和信息来自公共来源，**仅供信息目的**。

- **不是**金融或投资建议
- **不负责**基于本数据的决策
- 所有信息应在使用前进行验证
- API 可用性取决于第三方服务
