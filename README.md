# Awesome Browser

双源精选资源浏览器 —— 842 个精选资源，37 个分类，MCP 服务器可接入任何 AI 工具。

## 数据源

| 数据源 | 分类 | 条目 | 来源 |
|---|---|---|---|
| 😎 Awesome 精选 | 27 | 605 | [sindresorhus/awesome](https://github.com/sindresorhus/awesome) |
| 🪽 Hermes 生态 | 10 | 237 | [0xNyk/awesome-hermes-agent](https://github.com/0xNyk/awesome-hermes-agent) |

## 使用方式

### 1. 浏览器直接打开
双击 `index.html` 或访问 GitHub Pages。

### 2. 安装为全局 MCP 服务（推荐）

```bash
pip install -e .
```

安装后 `awesome-browser` 命令在所有项目中可用。

### 3. 接入 AI 工具

安装后，在对应工具的 MCP 配置中添加：

#### Hermes Agent

```yaml
# ~/.hermes/config.yaml
mcp_servers:
  awesome-lists:
    command: awesome-browser
    enabled: true
```

或使用 CLI：
```bash
hermes mcp add awesome-lists --command awesome-browser
```

#### Claude Code

```json
// .claude/mcp.json
{
  "mcpServers": {
    "awesome-lists": {
      "command": "awesome-browser"
    }
  }
}
```

#### Cursor / Windsurf

```json
// .cursor/mcp.json 或 .windsurf/mcp.json
{
  "mcpServers": {
    "awesome-lists": {
      "command": "awesome-browser"
    }
  }
}
```

#### Codex (OpenAI)

```json
// ~/.codex/mcp.json
{
  "mcpServers": {
    "awesome-lists": {
      "command": "awesome-browser"
    }
  }
}
```

#### VS Code / Copilot

```json
// .vscode/mcp.json
{
  "servers": {
    "awesome-lists": {
      "command": "awesome-browser"
    }
  }
}
```

### 4. MCP 工具列表

| 工具 | 功能 |
|---|---|
| `search` | 关键词搜索（支持 all/awesome/hermes 源过滤） |
| `list_categories` | 列出所有分类及条目数 |
| `get_category` | 获取指定分类的所有条目 |
| `get_stats` | 获取数据统计 |

## 项目结构

```
awesome-browser/
├── awesome_browser/        # Python 包（MCP 服务）
│   ├── __init__.py
│   ├── server.py           # MCP 服务主程序
│   ├── data.json           # Awesome 数据
│   └── hermes_data.json    # Hermes 数据
├── index.html              # 自包含浏览站点（离线可用）
├── pyproject.toml          # pip 安装配置
└── .github/workflows/      # 自动部署到 GitHub Pages
```
