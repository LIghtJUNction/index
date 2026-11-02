# LIghtJUNction · 项目索引

[浏览项目索引](https://lightjunction.github.io/index/) · [GitHub 主页](https://github.com/LIghtJUNction)

自动收录 LIghtJUNction 的公开 GitHub 仓库，支持按名称、描述和主题搜索，按语言筛选，以及按 Star、最近推送和名称排序。默认隐藏 Fork，可手动显示；归档项目保留并标注。

## 本地运行

需要 Python 3.10+；JavaScript 语法检查需要 Node.js。没有第三方运行依赖。

```sh
python scripts/update.py                 # 使用已提交的数据构建 dist/
python -m http.server 8000 --directory dist
```

打开 http://localhost:8000。刷新数据：

```sh
GH_TOKEN="$(gh auth token)" python scripts/update.py --refresh
```

Token 只用于 API 请求，不写入数据或网页；也可以不设置 Token，使用匿名 API 配额。只收录公开仓库。

## 自动检查、更新和发布

GitHub Actions 在推送和 PR 时运行单元测试、JavaScript 语法检查及构建。主分支通过检查后同步数据并发布 GitHub Pages；PR 不修改数据或部署。

每天 UTC 22:23（台北时间次日 06:23）自动同步，也可在 Actions 页面选择 **Run workflow**。GitHub 可能延迟定时任务，公开仓库长期没有活动时也可能暂停定时任务，可手动重新启用。数据变化才提交 `site/projects.json`。API 失败或返回空列表会中止，保留上次的数据与线上版本。

首次设置：仓库 Settings → Pages → Source 选择 **GitHub Actions**。默认 `GITHUB_TOKEN` 即可，无需另存个人 Token。机器人提交不会再次触发 push 工作流，因此同步与部署在同一次运行内完成。

## 验证与维护

```sh
python -m unittest discover -s tests -v
node --check site/app.js
python scripts/update.py
```

页面代码在 `site/`，同步和构建逻辑在 `scripts/update.py`，自动化配置在 `.github/workflows/index.yml`。修改页面后检查桌面和手机布局、搜索、筛选与空结果。贡献约定见 [AGENTS.md](AGENTS.md)。

API 与部署方式参考 [GitHub REST 文档](https://docs.github.com/en/rest/repos/repos) 和 [Pages 自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。
