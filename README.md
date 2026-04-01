# nanoCC

**Claude Code in 500 lines of Python.**

[English](#english) | [中文](#中文)

```bash
pip install nanocc && nanocc
```

> Inspired by Claude Code's architecture. For educational purposes only.
> One install. One command. Your own coding agent.

---

<a id="english"></a>

## English

### Why nanoCC?

The TypeScript source of Claude Code was extracted from the npm package `@anthropic-ai/claude-code` (v2.1.88) — **500K lines, 48+ tools, and a sophisticated agent harness**. We studied its architecture and distilled the essence into **~400 lines of Python** that actually runs.

- **From the source** — architecture and patterns derived from studying Claude Code's published npm package, not guesswork
- **One line to install** — `pip install nanocc && nanocc`, that's it, you have a working coding agent
- **30 minutes to master** — read 3 files and you understand how every coding agent (Claude Code, Cursor, Codex CLI) works under the hood
- **Any LLM** — not locked to Claude. Use GPT, Gemini, local models, anything [LiteLLM](https://github.com/BerriAI/litellm) supports

Like [minGPT](https://github.com/karpathy/minGPT) is to GPT, **nanoCC** is to Claude Code.

### What it does

nanoCC is a fully functional coding agent that can:

- Read, write, and edit files
- Execute shell commands
- Search codebases with glob and grep
- Stream responses in real-time
- Work with **any LLM** (Claude, GPT, Gemini, local models) via [LiteLLM](https://github.com/BerriAI/litellm)

### Architecture (3 files, that's it)

```
nanocc/
├── agent.py    (144 lines)  # The agent loop — the heart of it all
├── tools.py    (191 lines)  # 6 tools: Read, Write, Edit, Bash, Glob, Grep
└── cli.py      ( 68 lines)  # Interactive terminal REPL
```

### The Agent Loop

Every coding agent — Claude Code, Codex CLI, Cursor, Cline — runs the same loop:

```
┌─────────────────────────────────────────┐
│                                         │
│   User message                          │
│       │                                 │
│       ▼                                 │
│   ┌─────────┐                           │
│   │   LLM   │ ◄── system prompt         │
│   │         │ ◄── tools schema          │
│   │         │ ◄── conversation history   │
│   └────┬────┘                           │
│        │                                │
│        ▼                                │
│   ┌──────────┐    Yes    ┌───────────┐  │
│   │ tool_use?│──────────►│ execute() │  │
│   └────┬─────┘           └─────┬─────┘  │
│        │ No                    │         │
│        ▼                       │         │
│   Print response         Append result  │
│                                │         │
│                     ┌──────────┘         │
│                     ▼                    │
│              Loop back to LLM            │
│                                         │
└─────────────────────────────────────────┘
```

That's it. The entire `run_agent_loop()` function is ~80 lines. Read it — there's no magic.

### The Tool System

Tools are plain Python functions with a JSON Schema description:

```python
@_register("Read", "Read a file and return its contents.", { ... })
def read_file(file_path: str, offset: int = 0, limit: int = 2000) -> str:
    with open(file_path, "r") as f:
        lines = f.readlines()
    return "".join(f"{i+1}\t{line}" for i, line in enumerate(lines[offset:offset+limit]))
```

6 tools is enough to be genuinely useful:

| Tool | What it does |
|------|-------------|
| `Read` | Read file contents with line numbers |
| `Write` | Create or overwrite files |
| `Edit` | Find-and-replace in files |
| `Bash` | Execute shell commands |
| `Glob` | Find files by pattern |
| `Grep` | Search file contents with regex |

### Quick Start

```bash
# One line install + run
pip install nanocc && nanocc

# Or install from source
git clone https://github.com/o-pencil-agent/nanoCC.git && cd nanoCC && pip install -e .

# Set your API key (pick one)
export ANTHROPIC_API_KEY=sk-ant-...
# or: export OPENAI_API_KEY=sk-...
# or: export GEMINI_API_KEY=...

# Run
nanocc

# Or with a different model
nanocc -m gpt-4o
nanocc -m gemini/gemini-2.5-pro

# Or with an inline prompt
nanocc "find all TODO comments in this project"
```

### Claude Code vs nanoCC — What we kept, what we cut

We studied Claude Code's 500K-line codebase and extracted the **20% that does 80% of the work**:

| Claude Code (500K lines) | nanoCC (400 lines) | Status |
|---|---|---|
| Agent Loop (`QueryEngine.ts`) | `agent.py` | **Kept** — the core |
| Tool System (`Tool.ts`, 48 tools) | `tools.py` (6 tools) | **Simplified** — 6 is enough |
| Streaming Response | `agent.py` | **Kept** — real-time output |
| CLI Interface (`main.tsx`) | `cli.py` | **Kept** — interactive REPL |
| Memory System (MEMORY.md) | - | Cut |
| Sub-agents (Agent tool) | - | Cut |
| Permission System | - | Cut |
| MCP Protocol | - | Cut |
| Telemetry / Feature Flags | - | Cut |
| KAIROS Autonomous Mode | - | Cut |

The result: **everything you need, nothing you don't**.

### How it compares

| | Claude Code | claw-code | **nanoCC** |
|---|---|---|---|
| Goal | Production tool | Faithful port | **Learn + Use** |
| Language | TypeScript | Python + Rust | **Python** |
| Lines of code | ~500K | Growing | **~400** |
| Tools | 48+ | Mirroring | **6** |
| Models | Claude only | Claude focus | **Any (LiteLLM)** |
| Install | `npm` + subscription | Build from source | **`pip install nanocc`** |
| Time to understand | Weeks | Days | **30 minutes** |

### Exercises

1. **Add a new tool** — e.g., `WebFetch`. Follow the `@_register` pattern in `tools.py`.
2. **Add conversation memory** — save/load messages to JSON between sessions.
3. **Add a permission system** — confirm before Write/Edit/Bash.
4. **Add context compression** — summarize old messages when the conversation gets long.
5. **Add sub-agents** — spawn a new `run_agent_loop()` for isolated tasks.

---

<a id="中文"></a>

## 中文

### 为什么做 nanoCC？

Claude Code 的 TypeScript 源码从 npm 包 `@anthropic-ai/claude-code`（v2.1.88）中提取 —— **50 万行代码、48+ 工具、完整的 agent 调度系统**。我们研究了它的架构，将精华浓缩为**约 400 行 Python**，而且真的能跑。

- **源于源码** —— 架构与设计模式来自对 Claude Code 已发布 npm 包的研究，不是猜测
- **一行安装** —— `pip install nanocc && nanocc`，你就拥有了一个可用的编程智能体
- **30 分钟掌握** —— 读完 3 个文件，你就理解了所有 coding agent（Claude Code、Cursor、Codex CLI）的底层原理
- **不绑定模型** —— 不锁定 Claude，支持 GPT、Gemini、本地模型，[LiteLLM](https://github.com/BerriAI/litellm) 支持的都能用

正如 [minGPT](https://github.com/karpathy/minGPT) 之于 GPT，**nanoCC** 之于 Claude Code。

### 功能

nanoCC 是一个完整可用的编程智能体：

- 读取、写入、编辑文件
- 执行 Shell 命令
- 通过 glob 和 grep 搜索代码库
- 流式实时输出
- 通过 [LiteLLM](https://github.com/BerriAI/litellm) 支持**任意大模型**（Claude / GPT / Gemini / 本地模型）

### 架构（3 个文件，没了）

```
nanocc/
├── agent.py    (144 行)  # Agent 循环 —— 整个项目的核心
├── tools.py    (191 行)  # 6 个工具：Read, Write, Edit, Bash, Glob, Grep
└── cli.py      ( 68 行)  # 交互式终端 REPL
```

### Agent 循环

所有 coding agent —— Claude Code、Codex CLI、Cursor、Cline —— 都在跑同一个循环：

```
┌──────────────────────────────────────┐
│                                      │
│   用户消息                            │
│       │                              │
│       ▼                              │
│   ┌─────────┐                        │
│   │  大模型  │ ◄── system prompt      │
│   │         │ ◄── 工具定义            │
│   │         │ ◄── 对话历史            │
│   └────┬────┘                        │
│        │                             │
│        ▼                             │
│   ┌──────────┐   是   ┌──────────┐   │
│   │ 调用工具？│───────►│ 执行工具  │   │
│   └────┬─────┘        └────┬─────┘   │
│        │ 否                │         │
│        ▼                   │         │
│   输出回复           追加工具结果      │
│                            │         │
│                  ┌─────────┘         │
│                  ▼                   │
│            回到大模型继续              │
│                                      │
└──────────────────────────────────────┘
```

就这些。整个 `run_agent_loop()` 函数只有约 80 行。去读它 —— 没有任何黑魔法。

### 快速开始

```bash
# 一行安装 + 运行
pip install nanocc && nanocc

# 或从源码安装
git clone https://github.com/o-pencil-agent/nanoCC.git && cd nanoCC && pip install -e .

# 设置 API Key（选一个）
export ANTHROPIC_API_KEY=sk-ant-...
# 或：export OPENAI_API_KEY=sk-...
# 或：export GEMINI_API_KEY=...

# 运行
nanocc

# 使用其他模型
nanocc -m gpt-4o
nanocc -m gemini/gemini-2.5-pro

# 带提示词直接运行
nanocc "找出这个项目里所有的 TODO 注释"
```

### Claude Code vs nanoCC —— 保留了什么，砍掉了什么

我们研究了 Claude Code 50 万行代码库，提取了**做到 80% 效果的那 20% 核心**：

| Claude Code（50万行） | nanoCC（400行） | 状态 |
|---|---|---|
| Agent 循环（`QueryEngine.ts`） | `agent.py` | **保留** —— 核心中的核心 |
| 工具系统（`Tool.ts`，48 个工具） | `tools.py`（6 个工具） | **精简** —— 6 个就够了 |
| 流式响应 | `agent.py` | **保留** —— 实时输出 |
| CLI 界面（`main.tsx`） | `cli.py` | **保留** —— 交互式 REPL |
| 记忆系统（MEMORY.md） | - | 砍掉 |
| 子 Agent（Agent tool） | - | 砍掉 |
| 权限系统 | - | 砍掉 |
| MCP 协议 | - | 砍掉 |
| 遥测 / Feature Flags | - | 砍掉 |
| KAIROS 自主模式 | - | 砍掉 |

结果：**该有的都有，多余的全没有**。

### 对比

| | Claude Code | claw-code | **nanoCC** |
|---|---|---|---|
| 目标 | 生产工具 | 忠实移植 | **学习 + 使用** |
| 语言 | TypeScript | Python + Rust | **Python** |
| 代码量 | ~500K 行 | 持续增长 | **~400 行** |
| 工具数 | 48+ | 镜像 | **6 个** |
| 模型 | 仅 Claude | Claude 为主 | **任意（LiteLLM）** |
| 安装 | `npm` + 订阅 | 从源码构建 | **`pip install nanocc`** |
| 读懂耗时 | 数周 | 数天 | **30 分钟** |

### 进阶练习

1. **添加新工具** —— 比如 `WebFetch`，参考 `tools.py` 中的 `@_register` 模式
2. **添加对话记忆** —— 在会话间保存/加载消息到 JSON 文件
3. **添加权限系统** —— 在执行 Write/Edit/Bash 前请求确认
4. **添加上下文压缩** —— 对话过长时自动摘要历史消息
5. **添加子 Agent** —— 为隔离任务启动新的 `run_agent_loop()`

---

## Disclaimer / 免责声明

**English:**

All original Claude Code source code is the intellectual property of **Anthropic** and **Claude**. The architecture studied in this project was extracted from the publicly available npm package `@anthropic-ai/claude-code` (v2.1.88).

This repository is intended **solely for technical research, educational purposes, and communication among research enthusiasts**. It is strictly prohibited for any individual, organization, or entity to use the contents of this repository for commercial purposes, profit-driven activities, illegal activities, or any other unauthorized scenarios.

If any content in this repository infringes upon your legitimate rights, intellectual property, or raises other concerns, please contact us promptly and we will verify and remove the relevant content immediately.

**中文：**

本仓库中涉及的所有 Claude Code 原始源码版权归 **Anthropic** 和 **Claude** 所有。本项目研究的架构来源于公开发布的 npm 包 `@anthropic-ai/claude-code`（v2.1.88）。

本仓库**仅用于技术研究和科研爱好者交流学习参考**，严禁任何个人、机构及组织将其用于商业用途、盈利性活动、非法用途及其他未经授权的场景。

若内容涉及侵犯您的合法权益、知识产权或存在其他侵权问题，请及时联系我们，我们将第一时间核实并予以删除处理。

---

## License / 许可证

MIT
