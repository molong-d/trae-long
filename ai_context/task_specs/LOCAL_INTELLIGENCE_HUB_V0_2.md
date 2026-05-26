# Local Intelligence Hub v0.2 任务规格

## 0. 任务定位

你现在是本地代码执行器 TRAE，不是最终决策者。

本任务是在已有 intelligence_hub/ MVP 基础上进行 v0.2 增量增强。

目标不是重构系统，也不是做复杂商业平台，而是提升当前本地情报聚合中心的：

1. 数据源有效性；
2. Dashboard 可用性；
3. API 查询能力；
4. watchlist 关键词能力；
5. digest 可读性；
6. 本地运行便利性；
7. 测试和验证完整性。

本任务必须遵守 Harness 工程原则：

- 安全；
- 最小变更；
- 可验证；
- 可回滚；
- 分阶段推进；
- 不自动 commit；
- 不自动 merge；
- 所有命令、判断、验证、失败都记录到 ai_context/。

---

## 1. 项目信息

项目路径：

    /home/long/project/trae_project1

远程仓库：

    git@github.com:molong-d/trae-long.git

当前已有功能目录：

    intelligence_hub/
    ├── README.md
    ├── config/sources.json
    ├── src/main.py
    ├── src/db.py
    ├── src/scoring.py
    ├── src/digest.py
    ├── src/dashboard.py
    ├── src/fetchers/
    │   ├── gdelt.py
    │   ├── hackernews.py
    │   ├── arxiv_api.py
    │   ├── sec_edgar.py
    │   ├── coingecko.py
    │   └── rss.py
    └── tests/test_basic.py

已有命令：

    python3 intelligence_hub/src/main.py init-db
    python3 intelligence_hub/src/main.py fetch-once
    python3 intelligence_hub/src/main.py digest
    python3 intelligence_hub/src/main.py status
    python3 intelligence_hub/src/main.py serve
    python3 intelligence_hub/src/main.py watch --interval 300

---

## 2. 风险等级

本任务风险等级：L2-L3。

原因：

- 会修改已有 intelligence_hub/ 代码；
- 但只允许做独立工具的增量增强；
- 不允许修改其他业务代码；
- 不允许系统级操作；
- 不允许引入复杂依赖；
- 不允许自动 commit / merge。

---

## 3. 权限边界

### 3.1 允许修改

只允许修改：

    intelligence_hub/
    ai_context/
    .gitignore

允许新增：

    intelligence_hub/scripts/
    intelligence_hub/docs/
    intelligence_hub/tests/
    ai_context/patches/
    ai_context/logs/
    ai_context/validation/

允许做：

1. 修复已有 fetcher 的明显问题；
2. 增强 Dashboard 过滤；
3. 增强 /api/items 和 /api/status；
4. 增加 watchlist 配置；
5. 增强 digest 输出；
6. 增加本地运行脚本；
7. 增加运行文档；
8. 增加 unittest；
9. 更新 README；
10. 更新 ai_context/ 日志。

### 3.2 禁止事项

禁止：

1. 不允许重新 git init；
2. 不允许修改 git remote；
3. 不允许修改 main 历史；
4. 不允许直接在 main 分支修改；
5. 不允许修改机器人、业务代码或无关文件；
6. 不允许 sudo；
7. 不允许全局安装依赖；
8. 不允许硬编码 API key；
9. 不允许新增付费 API 强依赖；
10. 不允许自动交易；
11. 不允许输出投资建议；
12. 不允许大规模爬虫；
13. 不允许绕过网站反爬；
14. 不允许自动 commit；
15. 不允许自动 merge；
16. 不允许做大规模重构；
17. 不允许引入数据库服务、前端框架或后端框架；
18. 不允许把运行生成物提交进 git。

---

## 4. 阶段 0：Git 预检查

执行：

    pwd
    git rev-parse --show-toplevel
    git status
    git branch
    git remote -v
    git log --oneline -5

通过标准：

1. Git 根目录必须是 /home/long/project/trae_project1；
2. remote 必须是 git@github.com:molong-d/trae-long.git；
3. 当前分支必须是 main；
4. 工作区必须 clean；
5. main 必须与 origin/main 一致，或者明确说明是否领先/落后。

不满足条件，立即停止，不允许继续。

---

## 5. 阶段 1：创建任务分支

通过阶段 0 后，创建独立分支：

    git checkout -b trae/local-intelligence-hub-v0.2

所有修改必须在该分支完成。

---

## 6. 阶段 2：现状复检

先只读检查当前 MVP：

    find intelligence_hub -maxdepth 4 -type f | sort
    python3 intelligence_hub/tests/test_basic.py
    python3 intelligence_hub/src/main.py status

记录到：

    ai_context/COMMAND_LOG.md
    ai_context/VALIDATION_LOG.md

重点确认：

1. 当前测试是否通过；
2. 当前数据库是否存在；
3. 当前 status 是否能运行；
4. 当前 .gitignore 是否排除了 db/log/digest 生成物；
5. 当前 Dashboard 是否已有 HTML escaping；
6. 当前 fetcher 哪些返回 0 item。

---

## 7. v0.2 功能目标

本阶段只做以下功能，不做额外扩展。

---

## 7.1 数据源有效性增强

### 7.1.1 GDELT fetcher 修复

目标：让 GDELT 更稳定返回 world 类情报。

要求：

1. 检查当前 gdelt.py 查询 URL 是否正确；
2. 增加查询参数可配置；
3. 支持从 sources.json 读取 keywords、limit、timespan；
4. 默认 timespan 为 1d；
5. 默认 limit 不超过 20；
6. 如果 GDELT 返回 0 item，需要在日志里明确记录请求 URL、返回状态、是否为空结果；
7. 失败不能导致整个 fetch-once 崩溃。

禁止：

1. 不允许抓网页；
2. 不允许绕过 API；
3. 不允许高频请求。

### 7.1.2 CoinGecko fetcher 修复

目标：让 CoinGecko 返回 BTC/ETH/SOL 等基础价格情报。

要求：

1. 检查当前 coingecko.py 是否正确解析响应；
2. 使用公开 simple price endpoint；
3. 从 sources.json 读取 coins 和 vs_currency；
4. 默认 coins 为 bitcoin、ethereum、solana；
5. 默认 vs_currency 为 usd；
6. 每个币种生成一个 item；
7. item 的 category 必须是 crypto；
8. summary 至少包含当前价格和 24h 变化；
9. 如果 API 返回 0 item 或格式变化，写入 fetch_runs 和日志。

### 7.1.3 RSS 配置增强

目标：增加更多稳定 RSS 源，覆盖 world / finance / tech / science。

要求在 sources.json 中增加若干 RSS feed。

建议包括：

    BBC World
    NASA Breaking News
    MIT Technology Review
    NPR World
    Yahoo Finance Latest News
    Federal Reserve Press Releases

注意：

1. 只使用公开 RSS；
2. RSS 失效不能导致程序崩溃；
3. 每个 feed 独立失败记录；
4. 不允许引入需要 API key 的新闻源。

---

## 7.2 Watchlist 关键词能力

### 7.2.1 配置要求

在 sources.json 增加 watchlist 配置，语义如下：

    watchlist.enabled = true
    watchlist.keywords = OpenAI, Anthropic, Nvidia, semiconductor, AI, central bank, inflation, recession, war, sanctions, Bitcoin, Ethereum

### 7.2.2 功能要求

1. scoring 能读取 watchlist；
2. 标题命中 watchlist 关键词时加分；
3. summary 命中 watchlist 关键词时加分；
4. digest 中标记 watchlist 命中的 item；
5. Dashboard 中显示 watchlist 命中标记；
6. 不要让 watchlist 分数无限叠加，importance_score 仍保持 0-100。

---

## 7.3 Dashboard 增强

当前 Dashboard 只展示列表。v0.2 需要增强过滤和 API 查询。

### 7.3.1 页面过滤

Dashboard 支持 URL 参数：

    /?category=tech
    /?source=hackernews
    /?min_score=30
    /?category=world&min_score=50

要求：

1. category 过滤生效；
2. source 过滤生效；
3. min_score 过滤生效；
4. 页面上显示当前过滤条件；
5. 提供清除过滤链接；
6. 保留 HTML escaping；
7. 不引入前端框架。

### 7.3.2 API 查询

/api/items 支持 query 参数：

    /api/items?category=tech
    /api/items?source=rss
    /api/items?min_score=30
    /api/items?limit=50

要求：

1. 支持 category；
2. 支持 source；
3. 支持 min_score；
4. 支持 limit；
5. limit 最大不超过 200；
6. 返回 JSON；
7. 错误参数要安全处理，不导致服务崩溃。

/api/status 保持可用，并增加：

1. total_items；
2. categories；
3. sources；
4. recent_runs；
5. last_fetch_time。

---

## 7.4 Digest 增强

目标：让 latest_digest.md 更适合人工/GPT 阅读。

要求：

1. 按 category 分组；
2. 每个 category 显示 item 数量；
3. 增加 high priority section；
4. 增加 watchlist matched section；
5. 每条 item 显示 title、source、category、score、published_at、url、summary；
6. 增加生成时间；
7. 增加免责声明；
8. 不提交生成出的 latest_digest.md。

---

## 7.5 运行脚本

新增目录：

    intelligence_hub/scripts/

新增脚本：

    intelligence_hub/scripts/run_once.sh
    intelligence_hub/scripts/watch.sh
    intelligence_hub/scripts/serve.sh

要求：

1. 脚本使用 bash；
2. 脚本从仓库根目录运行；
3. 脚本内部切换到正确路径；
4. 不使用 sudo；
5. 不安装依赖；
6. 每个脚本要有简单说明和错误退出；
7. 给脚本添加可执行权限。

脚本功能：

run_once.sh 执行：

    python3 intelligence_hub/src/main.py init-db
    python3 intelligence_hub/src/main.py fetch-once
    python3 intelligence_hub/src/main.py digest
    python3 intelligence_hub/src/main.py status

watch.sh 执行：

    python3 intelligence_hub/src/main.py watch --interval 300

serve.sh 执行：

    python3 intelligence_hub/src/main.py serve

---

## 7.6 运行文档

新增：

    intelligence_hub/docs/OPERATION_RUNBOOK.md

内容至少包括：

1. 项目定位；
2. 一次性运行；
3. Dashboard 启动；
4. watch 模式；
5. tmux 使用建议；
6. 常见问题；
7. 数据源失败如何处理；
8. 如何添加 RSS；
9. 如何调整 watchlist；
10. 如何清理本地数据库和日志；
11. 如何确认没有提交运行生成物；
12. 金融/情报免责声明。

---

## 7.7 测试增强

更新或新增 unittest。

测试至少覆盖：

1. Dashboard query 参数解析；
2. Database 按 category 过滤；
3. Database 按 source 过滤；
4. Database 按 min_score 过滤；
5. API limit 最大值逻辑；
6. scoring watchlist 加分；
7. digest 生成不提交运行产物；
8. sources.json watchlist 可加载；
9. CoinGecko 响应解析函数；
10. GDELT 空结果处理。

要求：

1. 测试不依赖真实网络；
2. 网络响应解析要用 mock/sample data；
3. 使用 Python 标准库 unittest；
4. 不引入 pytest 依赖。

---

## 8. ai_context 记录要求

必须更新：

    ai_context/COMMAND_LOG.md
    ai_context/DECISION_LOG.md
    ai_context/VALIDATION_LOG.md
    ai_context/KNOWN_FAILURES.md
    ai_context/RISK_REGISTER.md
    ai_context/HANDOFF_PROMPT.md
    ai_context/task_state.json

### 8.1 COMMAND_LOG.md

记录：

1. Git 预检查命令；
2. 分支创建；
3. 当前 MVP 复检命令；
4. 修改摘要；
5. 验证命令；
6. patch 生成命令。

### 8.2 DECISION_LOG.md

记录：

1. 为什么 v0.2 不做重构；
2. 为什么优先数据源有效性；
3. 为什么增强 Dashboard 过滤；
4. 为什么新增 watchlist；
5. 为什么仍然不用第三方框架；
6. 为什么不提交运行生成物。

### 8.3 VALIDATION_LOG.md

记录实际结果，不允许保留 PENDING。

至少包括：

1. JSON 校验结果；
2. unittest 结果；
3. status 结果摘要；
4. digest 结果摘要；
5. run_once.sh 验证；
6. serve.sh 启动方式；
7. watch.sh 未长期运行但命令可用说明；
8. git diff 结果；
9. 生成物排除检查。

### 8.4 KNOWN_FAILURES.md

更新：

1. GDELT 可能 0 item；
2. CoinGecko 可能限流；
3. RSS 可能失效；
4. SEC EDGAR 默认禁用；
5. Dashboard 只适合本地访问；
6. watch 模式不是毫秒级实时。

### 8.5 task_state.json

保持合法 JSON。

至少包含：

    task_name: local-intelligence-hub-v0.2-operational-hardening
    risk_level: L2-L3
    current_phase: v0.2_operational_hardening
    git_branch: trae/local-intelligence-hub-v0.2
    validation_status: not_run
    human_confirmation_required: true

---

## 9. 验证要求

必须执行：

    python3 -m json.tool intelligence_hub/config/sources.json > /tmp/intelligence_sources_v02_check.json
    python3 -m json.tool ai_context/task_state.json > /tmp/intelligence_task_state_v02_check.json
    python3 intelligence_hub/tests/test_basic.py
    python3 intelligence_hub/src/main.py status
    python3 intelligence_hub/src/main.py digest
    python3 intelligence_hub/src/main.py status
    bash intelligence_hub/scripts/run_once.sh
    timeout 5 bash intelligence_hub/scripts/serve.sh
    timeout 10 bash intelligence_hub/scripts/watch.sh

注意：

1. serve.sh 会启动本地服务，验证时用 timeout，避免阻塞；
2. watch.sh 不要长期运行；
3. 如果外部网络导致 fetch 失败，必须记录，但不一定视为阻塞失败。

---

## 10. 生成物排除检查

必须确认以下文件没有进入 staged：

    intelligence_hub/data/intelligence.db
    intelligence_hub/logs/fetch.log
    intelligence_hub/reports/latest_digest.md
    __pycache__/
    *.pyc

执行：

    git status --short
    git diff --cached --name-only
    git check-ignore -v intelligence_hub/data/intelligence.db intelligence_hub/logs/fetch.log intelligence_hub/reports/latest_digest.md || true

---

## 11. Patch 要求

生成 patch 供 GPT 审查，但不要把 patch 文件 commit。

执行：

    mkdir -p ai_context/patches
    git diff --cached > ai_context/patches/local_intelligence_hub_v0_2.patch

要求：

1. patch 文件保留在本地；
2. 不加入 staged；
3. 不提交 patch 文件；
4. 最终报告给出 patch 路径和大小。

---

## 12. 最终报告格式

最终输出：

1. 当前分支；
2. 是否从 clean main 创建分支；
3. 修改摘要；
4. 新增/修改文件列表；
5. 数据源增强说明；
6. Dashboard 增强说明；
7. API 增强说明；
8. watchlist 增强说明；
9. digest 增强说明；
10. scripts 增强说明；
11. docs 增强说明；
12. unittest 结果；
13. JSON 校验结果；
14. 运行脚本验证结果；
15. git diff --cached --stat；
16. git diff --cached --name-only；
17. 运行生成物是否已排除；
18. patch 路径和大小；
19. 是否修改 git remote；
20. 是否自动 commit；
21. 是否自动 merge；
22. 已知失败或限制；
23. 下一步建议；
24. 需要我拿回给 GPT 审查的材料。

---

## 13. 停止条件

遇到以下情况必须停止：

1. Git 根目录不正确；
2. remote 不正确；
3. 当前分支不是 main；
4. 工作区不 clean；
5. 需要 sudo；
6. 需要安装全局依赖；
7. 需要 API key；
8. 需要修改业务代码；
9. 需要大规模重构；
10. 测试持续失败且无法小范围修复；
11. 外部 API 长时间不可用；
12. 出现不确定是否越权的修改。

停止后必须写入：

    ai_context/KNOWN_FAILURES.md
    ai_context/VALIDATION_LOG.md
    ai_context/task_state.json

---

## 14. 任务完成后禁止事项

任务完成后：

1. 不允许自动 commit；
2. 不允许自动 merge；
3. 不允许自动 push；
4. 不允许继续扩展 v0.3 功能；
5. 不允许新增未要求的数据源；
6. 不允许修改本任务规格文件。

等待人工/GPT 审查。
