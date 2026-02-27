# movie-agent

movie-agent 是一个可定时运行的每日电影推荐 Agent：它会抓取 TMDB Trending 榜单，识别新进榜/飙升电影，调用火山引擎 Ark（豆包）生成结构化推荐理由，再通过 Gmail SMTP 发送简洁可读的推荐邮件。

## 架构
- `src/collector_tmdb.py`: 拉取 TMDB Trending 电影榜单。
- `src/store_sqlite.py`: 持久化每日榜单与已发送记录（SQLite 单文件 `data/app.db`）。
- `src/detector.py`: 根据“新进榜 + 名次飙升”筛选候选。
- `src/analyzer_ark.py`: 调用火山引擎 Ark（豆包）+ web_search 生成结构化推荐卡片。
- `src/email_template.py`: 渲染移动端可读 HTML 邮件。
- `src/report_excel.py`: 生成电影数据 Excel（`daily_snapshot` 与 `sent_log`）供邮件附件与审计。
- `src/emailer_smtp.py`: 使用 Gmail SMTP 发送邮件（附带 Excel 数据附件）。
- `main.py`: 端到端流程编排，支持 `--limit` 与 `--dry-run`。
- `.github/workflows/daily.yml`: GitHub Actions 定时 + 手动触发。

## Quickstart
1. 配置环境变量
   ```bash
   cp .env.example .env
   # 编辑 .env 填入真实值
   ```
2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
3. 运行主流程
   ```bash
   python main.py --limit 1
   ```

## SMTP 测试命令
```bash
python -m src.email_test
# 仅预览 HTML：
python -m src.email_test --preview
```

## GitHub Actions Secrets 清单
- `TMDB_API_KEY`
- `ARK_API_KEY`
- `TO_EMAIL`
- `FROM_EMAIL`（可选）
- `SMTP_USER`
- `SMTP_APP_PASSWORD`
- （已内置）时区 `Asia/Singapore`
- （已内置）SMTP 主机 `smtp.gmail.com`，端口 `465`
- （已内置）Ark Base URL `https://ark.cn-beijing.volces.com/api/v3`
- （已内置）Ark Model `doubao-seed-1-6-250615`（默认开启 web_search）

## 常见错误
- **TMDB key 无效**：检查 `TMDB_API_KEY` 是否正确、是否有 API 访问权限。
- **SMTP app password 失败**：Gmail 必须使用 App Password，普通密码无法 SMTP 登录。
- **Ark 返回非 JSON**：模型偶发输出非严格 JSON，程序会自动重试一次；仍失败则退出并报错，不发送空邮件。


## 数据保留与 Artifact
- 主流程每次启动会先清理超过 365 天的 `daily_snapshot` 与 `sent_log` 数据。
- GitHub Actions 会在运行前尝试下载上一次 `movie-agent-db` artifact 中的 `data/app.db`，运行完成后再覆盖上传，形成按天滚动更新的数据库。
- artifact 保留期设置为 365 天。
