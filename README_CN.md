# AGENTS Work Protocol

> 一个让所有 AI Agent 工具说同一种语言的开放协议。

## 为什么需要这个协议

我是一个程序员。日常开发中，我同时使用多个 AI Agent 工具——Claude Code、OpenAI Codex、OpenClaw、Hermes……它们各有擅长的场景，我在不同阶段切换不同的工具来完成工作。

但我很快发现了一个问题：**这些工具之间是信息孤岛。**

Claude Code 在这个项目里积累了架构记忆和设计决策，换成 Codex 进来，它什么都不知道。上一个 agent 提交的 bug 还没处理完，下一个 agent 又重复踩了同样的坑。我不得不一遍又一遍地用自然语言向不同的工具解释同一个项目的上下文、规范、进度和决策。

这不对。

一个项目的知识——架构、决策、进度、bug、计划——不应该绑定在某个 agent 工具的私有存储里。它应该属于项目本身。

**所以我设计了 AGENTS Work Protocol。**

## 它是什么

AGENTS Work Protocol 是一个开放的项目级工作规范。它的核心思想是：

**在每个项目根目录下建立一个 `.agents/` 目录，作为所有 Agent 工具共享的上下文操作系统。**

无论你用哪个 Agent 工具打开这个项目，只要它遵循这个协议，就能：

- 读取同一份项目记忆
- 使用同一套 Skills
- 查询同一个 Bug 数据库和 Todo 数据库
- 了解同一个路线图和计划
- 遵循同一套工作规范

Agent 工具可以不同，但项目知识只有一个来源。

## 核心设计理念

### 路标，不是内容

这个协议最重要的设计决策是**三级上下文披露**：

| 层级 | 内容 | 何时加载 |
|------|------|----------|
| Tier 0 | 启动钩子 (`AGENTS.md`) | Agent 自动加载 |
| Tier 1 | 角色定义 + 路由表 (`SOUL.md`, `ROUTER.md`, `MANIFEST.yaml`) | 启动后立即 |
| Tier 2 | 实际内容 (prompt, skill, memory, plan, bug...) | 任务命中时按需 |

这是一个类 RAG 的检索思路：先给 agent 看路标（"这里有什么，在哪里"），等它确认需要什么之后，再加载具体内容。而不是一上来就把所有东西塞进上下文窗口。

上下文窗口是稀缺资源。加载太多会污染注意力，加载太少会让 agent 迷路。路标和内容之间的平衡，是这个协议要解决的核心矛盾。

### 文件负责可读，数据库负责状态

- **计划 (plans)**、**记忆 (memories)**、**路线图 (roadmaps)** 用文件存储——人可以读，git 可以追踪，agent 可以按需加载
- **Bug**、**Todo**、**对话记录 (chats)** 用 SQLite 存储——支持结构化查询、并发写入、状态流转

两种存储方式各司其职，不互相替代。

### 工具无关

这个协议不绑定任何特定的 Agent 工具。它只是一套目录结构、文件格式约定、和工作流程规范。任何 Agent 工具只要能读文件、能执行 Python 脚本，就能接入。

Claude Code 可以用它。Codex 可以用它。未来的新工具也可以用它。

## 目录结构

```
.agents/
├── AGENTS.md              # 自动加载钩子（Tier 0）
├── SOUL.md                # 主控 Agent 角色 + 工作循环
├── ROUTER.md              # 任务路由表（人类可读）
├── MANIFEST.yaml          # 资源索引（机器可读）
├── AGENTS_SPEC.md         # 完整规范文档
├── VERSION                # 规范版本号
│
├── prompts/               # 子 Agent 角色定义
│   ├── INDEX.md           #   路标（先读这个）
│   ├── product-designer.md
│   ├── backend-engineer.md
│   ├── test-engineer.md
│   ├── devops-engineer.md
│   └── reviewer.md
│
├── skills/                # 可复用技能
│   ├── INDEX.md
│   ├── code-review/
│   ├── bug-triage/
│   └── plan-management/
│
├── memories/              # 项目记忆
│   ├── MEMORY.md          #   主入口（≤1KB，只放索引）
│   ├── architecture.md
│   ├── decisions.md
│   ├── project.md
│   └── user-preferences.md
│
├── plans/                 # 任务计划
│   ├── INDEX.md
│   └── archive/{done,cancel}/
│
├── bugs/                  # Bug 追踪系统
│   ├── bugs.sqlite + bugs_cli.py
│
├── todo/                  # Todo 追踪系统
│   ├── todo.sqlite + todo_cli.py
│
├── chats/                 # 对话记录
│   ├── chats.sqlite + chats_cli.py
│
└── roadmaps/              # 项目路线图
    └── ROADMAP.md
```

## 工作循环

Agent 进入项目后，遵循 OODRA 循环：

```
Observe  → 读取用户输入
Orient   → 识别意图
Route    → 通过 ROUTER.md 匹配资源
Retrieve → 按需加载内容
Decide   → 自己执行或委派子 Agent
Act      → 执行工作
Verify   → 验证结果
Write    → 写回状态（plans/todo/bugs/memory）
Report   → 向用户汇报
```

## 快速开始

1. 把 `.agents/` 目录复制到你的项目根目录
2. 编辑 `memories/MEMORY.md`，填入你的项目信息
3. 编辑 `roadmaps/ROADMAP.md`，写入你的路线图
4. 用 `python .agents/bugs/bugs_cli.py init` 初始化数据库（如已存在可跳过）
5. 让你的 Agent 工具读取 `.agents/AGENTS.md` 作为入口

## 规范版本

当前版本：**v0.1.0**

版本号遵循语义化版本（SemVer）：
- **主版本号**变更：不兼容的结构性改动
- **次版本号**变更：向后兼容的功能新增
- **修订号**变更：向后兼容的问题修复

版本信息在以下位置保持同步：
- `.agents/VERSION`
- `.agents/SOUL.md`
- `.agents/ROUTER.md`
- `.agents/AGENTS_SPEC.md`
- `.agents/MANIFEST.yaml`

## License

MIT
