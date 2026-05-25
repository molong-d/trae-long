你现在是本地代码执行器 TRAE，不是最终决策者。

本任务目标：在本地构建一个“情报聚合中心 MVP”，用于持续聚合世界重大事件、科技、金融、科研、加密市场等信息，方便后续由 GPT 或人工进行分析。

项目名称：
Local Intelligence Hub

项目路径：
/home/long/project/trae_project1

远程仓库：
git@github.com:molong-d/trae-long.git

重要定位：
这是一个独立的本地情报聚合工具，与机器人业务无关。
本任务允许新增独立目录 intelligence_hub/，但不允许修改已有业务代码。
第一版要求本地可运行、可验证、可回滚，不追求完整商业系统。

==================================================
一、权限边界
==================================================

允许：
1. 新增 intelligence_hub/ 独立目录；
2. 新增 ai_context/ 任务记录；
3. 新增 README、配置文件、Python 源码、测试文件；
4. 使用 Python 标准库优先；
5. 使用 SQLite 本地数据库；
6. 创建本地 HTML Dashboard；
7. 调用公开 API / RSS；
8. 写入 data/、logs/、reports/；
9. 创建 requirements.txt，但不要强依赖复杂第三方库。

禁止：
1. 不允许修改已有业务代码；
2. 不允许删除已有文件；
3. 不允许修改 git remote；
4. 不允许重新 git init；
5. 不允许使用 sudo；
6. 不允许全局安装依赖；
7. 不允许写入系统目录；
8. 不允许上传密钥；
9. 不允许硬编码 API key；
10. 不允许自动 git commit；
11. 不允许自动 merge；
12. 不允许进行投资建议、交易建议或自动交易；
13. 不允许做大规模网站爬取；
14. 不允许绕过网站反爬限制。

==================================================
二、阶段 0：Git 预检查
==================================================

请先执行只读检查：

pwd
git rev-parse --show-toplevel
git status
git branch
git remote -v
git log --oneline -5

通过标准：
- Git 根目录必须是 /home/long/project/trae_project1；
- remote 必须是 git@github.com:molong-d/trae-long.git；
- 当前分支应为 main；
- 工作区必须 clean。

如果不满足上述条件，立即停止，不允许继续。

==================================================
三、阶段 1：创建任务分支
==================================================

如果阶段 0 通过，请创建独立任务分支：

git checkout -b trae/local-intelligence-hub-mvp

后续所有修改都必须在该分支进行。

==================================================
四、阶段 2：创建项目结构
==================================================

请创建以下目录结构：

intelligence_hub/
intelligence_hub/config/
intelligence_hub/data/
intelligence_hub/logs/
intelligence_hub/reports/
intelligence_hub/src/
intelligence_hub/src/fetchers/
intelligence_hub/tests/

ai_context/
ai_context/patches/
ai_context/logs/
ai_context/validation/

允许创建或更新以下文件：

intelligence_hub/README.md
intelligence_hub/config/sources.json
intelligence_hub/src/main.py
intelligence_hub/src/db.py
intelligence_hub/src/scoring.py
intelligence_hub/src/digest.py
intelligence_hub/src/dashboard.py
intelligence_hub/src/fetchers/gdelt.py
intelligence_hub/src/fetchers/hackernews.py
intelligence_hub/src/fetchers/arxiv_api.py
intelligence_hub/src/fetchers/sec_edgar.py
intelligence_hub/src/fetchers/coingecko.py
intelligence_hub/src/fetchers/rss.py
intelligence_hub/tests/test_basic.py
intelligence_hub/requirements.txt

ai_context/COMMAND_LOG.md
ai_context/DECISION_LOG.md
ai_context/VALIDATION_LOG.md
ai_context/KNOWN_FAILURES.md
ai_context/RISK_REGISTER.md
ai_context/HANDOFF_PROMPT.md
ai_context/task_state.json

==================================================
五、阶段 3：MVP 功能要求
==================================================

请实现一个本地 Python 情报聚合 MVP。

技术要求：
1. Python 3；
2. 优先使用标准库；
3. 数据库使用 sqlite3；
4. HTTP 请求优先使用 urllib.request；
5. XML/Atom/RSS 解析优先使用 xml.etree.ElementTree；
6. 不强制依赖第三方库；
7. 可以创建 requirements.txt，但第一版最好为空或仅写 optional dependencies；
8. 所有数据存入 intelligence_hub/data/intelligence.db；
9. 所有运行日志写入 intelligence_hub/logs/fetch.log；
10. 所有快报输出到 intelligence_hub/reports/latest_digest.md。

==================================================
六、数据源要求
==================================================

第一版至少实现以下 fetcher：

1. GDELT fetcher
用途：世界重大事件 / 国际新闻
要求：
- 支持查询最近新闻；
- 支持关键词配置；
- 返回统一 item 格式。

2. Hacker News fetcher
用途：科技趋势 / 创业 / AI / 开发者热点
要求：
- 获取 topstories 或 newstories；
- 拉取前 N 条 item；
- 返回统一 item 格式。

3. arXiv fetcher
用途：AI / 科技 / 科研论文
要求：
- 支持查询 cs.AI、cs.LG、cs.CL 等关键词或分类；
- 返回标题、作者、摘要、链接、发布时间。

4. SEC EDGAR fetcher
用途：金融监管 / 公司公告
要求：
- 支持从配置中读取 CIK 列表；
- 获取 company submissions；
- 返回最近 filing 信息；
- 必须设置合理 User-Agent，不允许伪装或滥用。

5. CoinGecko fetcher
用途：加密市场
要求：
- 获取 BTC、ETH 等主要币种价格和 24h 变化；
- 返回统一 item 格式。

6. RSS fetcher
用途：通用新闻源扩展
要求：
- 从 config/sources.json 读取 RSS URL；
- 解析 title、link、published、summary；
- 返回统一 item 格式。

==================================================
七、统一数据格式
==================================================

所有 fetcher 返回统一 item dict：

{
  "source": "",
  "category": "",
  "title": "",
  "url": "",
  "published_at": "",
  "fetched_at": "",
  "summary": "",
  "raw": {}
}

入库时额外生成：

{
  "content_hash": "",
  "importance_score": 0,
  "created_at": ""
}

去重规则：
- 优先使用 URL；
- 如果 URL 为空，使用 title + source；
- 生成 sha256 hash；
- hash 已存在则跳过。

==================================================
八、数据库要求
==================================================

SQLite 表至少包括：

items:
- id
- source
- category
- title
- url
- published_at
- fetched_at
- summary
- content_hash
- importance_score
- raw_json
- created_at

fetch_runs:
- id
- source
- started_at
- finished_at
- status
- item_count
- error_message

要求：
- 自动初始化数据库；
- 重复运行不会破坏数据；
- fetcher 异常不能导致整个程序崩溃；
- 每个 fetcher 的异常要记录到 fetch_runs。

==================================================
九、重要性评分
==================================================

实现一个简单 rule-based scoring：

加分关键词可包括：
- war
- conflict
- election
- central bank
- rate cut
- rate hike
- inflation
- recession
- AI
- chip
- semiconductor
- Nvidia
- OpenAI
- Anthropic
- Google
- Microsoft
- Apple
- Tesla
- Bitcoin
- Ethereum
- SEC
- earnings
- bankruptcy
- acquisition
- merger
- sanctions
- supply chain

要求：
- 分数范围 0-100；
- 标题命中关键词加分；
- 摘要命中关键词加分；
- 来源可信度可加权；
- 规则要写清楚；
- 不要假装这是专业金融模型。

==================================================
十、命令行功能
==================================================

intelligence_hub/src/main.py 至少支持：

python3 intelligence_hub/src/main.py init-db
python3 intelligence_hub/src/main.py fetch-once
python3 intelligence_hub/src/main.py digest
python3 intelligence_hub/src/main.py serve
python3 intelligence_hub/src/main.py status

各命令要求：

init-db:
- 初始化 SQLite 数据库。

fetch-once:
- 运行所有启用的数据源；
- 写入数据库；
- 输出抓取摘要。

digest:
- 从数据库读取最近 24 小时高分情报；
- 生成 reports/latest_digest.md。

serve:
- 启动本地 HTTP Dashboard；
- 默认监听 127.0.0.1:8765；
- 页面展示最新情报、分类、来源、重要性分数、链接。

status:
- 输出数据库 item 数量；
- 输出最近一次 fetch_runs；
- 输出各 category 数量。

==================================================
十一、实时性要求
==================================================

第一版不需要真正 WebSocket 实时推送，但要做到 near-real-time polling。

请在 main.py 中支持：

python3 intelligence_hub/src/main.py watch --interval 300

要求：
- 每 300 秒运行一次 fetch-once；
- 每轮结束生成 digest；
- Ctrl+C 可安全退出；
- interval 不允许小于 60 秒，避免滥用外部 API；
- 每轮运行写入日志；
- 不能无限打印超长输出。

==================================================
十二、配置文件要求
==================================================

创建 intelligence_hub/config/sources.json。

至少包含：

{
  "app": {
    "db_path": "intelligence_hub/data/intelligence.db",
    "log_path": "intelligence_hub/logs/fetch.log",
    "digest_path": "intelligence_hub/reports/latest_digest.md",
    "dashboard_host": "127.0.0.1",
    "dashboard_port": 8765
  },
  "fetch": {
    "default_limit": 20,
    "min_watch_interval_seconds": 60
  },
  "sources": {
    "gdelt": {
      "enabled": true,
      "category": "world",
      "keywords": ["geopolitics", "war", "election", "central bank", "AI"]
    },
    "hackernews": {
      "enabled": true,
      "category": "tech",
      "limit": 30
    },
    "arxiv": {
      "enabled": true,
      "category": "science",
      "queries": ["cat:cs.AI", "cat:cs.LG", "cat:cs.CL"],
      "limit": 10
    },
    "sec_edgar": {
      "enabled": false,
      "category": "finance",
      "user_agent": "local-intelligence-hub contact@example.com",
      "ciks": ["0000320193", "0000789019", "0001045810"]
    },
    "coingecko": {
      "enabled": true,
      "category": "crypto",
      "coins": ["bitcoin", "ethereum", "solana"]
    },
    "rss": {
      "enabled": true,
      "feeds": [
        {
          "name": "BBC World",
          "category": "world",
          "url": "http://feeds.bbci.co.uk/news/world/rss.xml"
        },
        {
          "name": "NASA Breaking News",
          "category": "science",
          "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss"
        }
      ]
    }
  }
}

注意：
- SEC EDGAR 默认 enabled=false，避免 User-Agent 未确认时直接请求；
- 不允许硬编码真实个人邮箱；
- README 中说明用户需要自行修改 user_agent。

==================================================
十三、Dashboard 要求
==================================================

serve 命令启动本地网页：

http://127.0.0.1:8765

页面至少显示：
1. 总 item 数；
2. 最近更新时间；
3. category 过滤链接；
4. source 过滤链接；
5. 最近 100 条情报；
6. 每条包含 title、source、category、published_at、importance_score、url；
7. 高分 item 用文字标记 HIGH；
8. 提供 /api/items JSON 接口；
9. 提供 /api/status JSON 接口。

不要求复杂前端。
可以用 Python 标准库 http.server 动态生成 HTML。

==================================================
十四、README 要求
==================================================

intelligence_hub/README.md 必须包含：

1. 项目定位；
2. 功能列表；
3. 数据源说明；
4. 实时性说明；
5. 风险和限制；
6. 不构成投资建议声明；
7. 快速启动命令；
8. 配置文件说明；
9. 常见问题；
10. 后续扩展方向。

必须明确说明：
- 这是情报聚合工具，不是事实判定工具；
- 聚合信息需要人工/GPT 二次核查；
- 金融信息不构成投资建议；
- 免费 API 有频率限制；
- RSS/API 可能失效；
- 第一版是 near-real-time polling，不是真正毫秒级实时系统。

==================================================
十五、测试要求
==================================================

创建 intelligence_hub/tests/test_basic.py。

测试至少覆盖：
1. 数据库初始化；
2. item hash 去重；
3. scoring 分数范围；
4. sources.json 可被加载；
5. digest 生成函数不会崩溃。

如果可以运行 pytest，则运行：
python3 -m pytest intelligence_hub/tests

如果没有 pytest，则至少提供标准库 unittest，并运行：
python3 intelligence_hub/tests/test_basic.py

优先使用 unittest，避免依赖 pytest。

==================================================
十六、ai_context 记录要求
==================================================

必须记录：

ai_context/COMMAND_LOG.md
- 执行过的关键命令；
- 命令目的；
- 结果摘要。

ai_context/DECISION_LOG.md
- 为什么使用 Python 标准库；
- 为什么使用 SQLite；
- 为什么第一版使用 polling；
- 为什么不做自动交易；
- 为什么不做大规模爬虫。

ai_context/VALIDATION_LOG.md
- git status；
- git diff --stat；
- 测试命令；
- main.py 各命令验证结果；
- JSON 配置校验结果。

ai_context/KNOWN_FAILURES.md
- 哪些数据源可能失败；
- 网络失败如何处理；
- API 限频如何处理；
- 当前未实现的能力。

ai_context/RISK_REGISTER.md
- 信息真实性风险；
- 误判重大事件风险；
- 金融数据延迟风险；
- API 失效风险；
- 法律与使用条款风险；
- 长时间运行风险；
- 日志膨胀风险。

ai_context/HANDOFF_PROMPT.md
- 供 GPT 审查本次产物的提示词；
- 包含审查重点；
- 包含如何检查 diff；
- 包含如何运行验证。

ai_context/task_state.json
必须是合法 JSON，至少包含：

{
  "task_name": "local-intelligence-hub-mvp",
  "risk_level": "L2-L3",
  "current_phase": "mvp_build",
  "git_branch": "trae/local-intelligence-hub-mvp",
  "last_action": "",
  "modified_files": [],
  "validation_status": "not_run",
  "known_failures": [],
  "next_step": "",
  "human_confirmation_required": true
}

==================================================
十七、验证流程
==================================================

必须执行：

python3 -m json.tool intelligence_hub/config/sources.json > /tmp/intelligence_sources_check.json
python3 -m json.tool ai_context/task_state.json > /tmp/intelligence_task_state_check.json

python3 intelligence_hub/src/main.py init-db
python3 intelligence_hub/src/main.py status
python3 intelligence_hub/src/main.py fetch-once
python3 intelligence_hub/src/main.py digest
python3 intelligence_hub/src/main.py status

如果使用 unittest：
python3 intelligence_hub/tests/test_basic.py

如果支持 serve，请说明如何手动验证：
python3 intelligence_hub/src/main.py serve
然后浏览器打开：
http://127.0.0.1:8765

注意：
serve 不要在最终验证中长期阻塞。
可以只说明启动方式，或用 timeout 短暂验证端口启动后退出。

==================================================
十八、Git diff 与 patch
==================================================

必须执行：

git status
git diff --stat
git diff --name-only
git diff

保存 patch：

mkdir -p ai_context/patches
git diff > ai_context/patches/local_intelligence_hub_mvp.patch

验证标准：
- 只新增 intelligence_hub/ 和 ai_context/ 相关文件；
- 没有修改已有业务代码；
- 没有修改 .git/config；
- 没有修改 remote；
- 没有自动 commit；
- 没有自动 merge；
- patch 文件存在；
- sources.json 是合法 JSON；
- task_state.json 是合法 JSON；
- 至少完成 init-db、status、digest、基础测试；
- fetch-once 如果因网络失败，不能算业务失败，但必须记录失败原因。

==================================================
十九、最终报告格式
==================================================

最终请输出：

1. 当前分支；
2. 是否从 main clean 状态创建任务分支；
3. 修改摘要；
4. 新增文件列表；
5. 核心功能说明；
6. 数据源实现情况；
7. 实时性实现方式；
8. 数据库路径；
9. Dashboard 启动方式；
10. digest 输出路径；
11. 测试命令和结果；
12. JSON 校验结果；
13. git diff --stat；
14. git diff --name-only；
15. patch 路径；
16. 是否满足权限边界；
17. 是否修改已有业务代码；
18. 是否修改 git remote；
19. 是否自动 commit；
20. 是否自动 merge；
21. 已知失败或限制；
22. 下一步建议；
23. 需要我拿回给 GPT 审查的材料。

注意：
本任务结束后不要自动 git commit。
本任务结束后不要自动 merge。
本任务结束后不要继续做新功能。