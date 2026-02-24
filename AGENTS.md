# movie-agent 协作说明

## 项目目标
构建一个可在本地和 GitHub Actions 定时运行的电影推荐 Agent：拉取 TMDB Trending，识别飙升/新进榜电影，调用 DeepSeek 生成结构化建议，再通过 Gmail SMTP 发送邮件。

## 约束
- 严禁提交任何密钥、账号密码、`.env` 文件。
- 只能通过环境变量读取配置。
- 默认存储使用 `data/app.db`（SQLite 单文件）。
- 抓取/分析失败时不要发送空邮件，必须清晰日志并退出非 0。

## 本地运行
1. 复制环境变量模板：`cp .env.example .env`
2. 安装依赖：`pip install -r requirements.txt`
3. 运行主流程：`python main.py --limit 1`

## 测试命令
- SMTP 测试：`python -m src.email_test`
- 抓取测试：`python -m src.collector_test`
- 分析测试：`python -m src.analyzer_test`

## 环境变量清单
- TMDB_API_KEY
- DEEPSEEK_API_KEY
- TO_EMAIL
- FROM_EMAIL (可选，默认 SMTP_USER)
- SMTP_USER
- SMTP_APP_PASSWORD
- 内置时区：`Asia/Singapore`
- 内置 SMTP：`smtp.gmail.com:465`
- 内置 DeepSeek Base URL：`https://api.deepseek.com`
- 内置 DeepSeek Model：`deepseek-reasoner`

## 工作流建议
- 可小步提交，但需保证每次提交可运行。
- 合并前至少跑一次 `python main.py --dry-run`。
