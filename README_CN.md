# AGENTS Work Protocol

> 一个让所有 AI Agent 工具说同一种语言的开放协议。

## 为什么需要这个协议

同一个软件项目里经常会使用多个 AI Agent 工具。不同工具各有优势，
但它们很容易变成信息孤岛：一个 agent 了解了架构，另一个 agent 记录了 bug，
第三个 agent 写了计划，下一轮工作却无法可靠继承这些项目状态。

项目知识和项目进度应该属于项目本身，而不是绑定在某个 agent 工具的私有存储里。

**AGENTS Work Protocol** 定义了一个共享的 `.agents/` 目录，让所有 agent 工具都能一致地读取和更新项目状态。

## 它是什么

AGENTS Work Protocol 是一个开放的项目级工作规范。核心思想是：

**在项目根目录建立 `.agents/` 目录，把它作为所有 Agent 工具共享的上下文操作系统。**

无论使用哪个 Agent 工具，只要遵循这个协议，就能：

- 读取同一份项目记忆
- 使用同一套可复用 skills
- 查询同一个 bug、chat、plan、todo 状态
- 理解同一份路线图和工作规范
- 接续其他 agent 已经开始的工作

Agent 工具可以不同，但项目知识只有一个来源。

## 核心设计理念

### 路标，不是内容

协议采用**三级上下文披露**：

| 层级 | 内容 | 何时加载 |
|------|------|----------|
| Tier 0 | 启动钩子 (`AGENTS.md`) | Agent 自动加载 |
| Tier 1 | 角色定义 + 路由表 (`SOUL.md`, `ROUTER.md`, `MANIFEST.yaml`) | 启动后立即 |
| Tier 2 | 实际内容（prompts、skills、memories、workflow、bugs 等） | 任务命中时按需加载 |

Agent 应先读路标，再按需加载具体内容。不要在启动时把整个 `.agents/` 目录塞进上下文窗口。

### 文件负责知识，SQLite 负责状态

- **文件**保存人类可读的知识：角色定义、路由、可复用 skills、项目记忆、路线图。
- **SQLite**保存可变状态：workflow 的 plans/todos、bugs、chat logs。

Plan 和 todo 不是两个割裂系统。Plan 是大的项目阶段或目标，todo 是这个 plan 里的可执行步骤。它们统一保存在 workflow 数据库里，避免 markdown 计划和另一个 todo 数据库之间出现状态割裂。

### Workflow 是项目工作队列

项目工作流状态的唯一权威位置是：

```text
.agents/workflow/workflow.sqlite
```

它包含：

- `plans`：大的工作阶段、里程碑或目标
- `todos`：每个 plan 里的最多 2 级步骤
- `workflow_events`：plan/todo 状态变化的追加日志
- `workflow_meta`：协议版本和迁移元数据

默认只展示未完成记录。已完成和已取消记录仍保存在数据库中，只有显式请求时才展示。

### 工具无关

这个协议不绑定任何特定 Agent 工具。它只是一套目录结构、存储约定和工作流规范。任何能读文件、能使用 SQLite 的 Agent 工具都可以接入。

Claude Code 可以用。Codex 可以用。Hermes 可以用。未来的新工具也可以用。

## 目录结构

```text
.agents/
├── AGENTS.md              # 自动加载钩子（Tier 0）
├── SOUL.md                # 主 Agent 角色 + 工作循环
├── ROUTER.md              # 任务路由表（人类可读）
├── MANIFEST.yaml          # 资源索引（机器可读）
├── AGENTS_SPEC.md         # 完整规范文档
├── VERSION                # 协议版本号
│
├── prompts/               # 子 Agent 角色定义
│   ├── INDEX.md           #   路标：先读这个
│   └── *.md
│
├── skills/                # 可复用技能和操作流程
│   ├── INDEX.md
│   └── <skill>/SKILL.md
│
├── memories/              # 项目记忆
│   ├── MEMORY.md          #   根索引，只放指针
│   └── *.md
│
├── workflow/              # 统一的 plan + todo 工作流状态
│   ├── WORKFLOW.md        #   人类可读的工作流说明
│   ├── workflow.sqlite    #   权威 workflow 数据库
│   ├── workflow_cli.py    #   标准 CLI
│   └── archive/           #   旧数据导入或导出快照
│
├── bugs/                  # Bug 追踪系统
│   ├── BUGS.md
│   ├── bugs.sqlite
│   └── bugs_cli.py
│
├── chats/                 # 对话记录
│   ├── CHATS.md
│   ├── chats.sqlite
│   └── chats_cli.py
│
└── roadmaps/              # 项目路线图
    └── ROADMAP.md
```

v0.1.x 的 `plans/` 和 `todo/` 目录只是 legacy 导入来源。迁移后，agent 不应继续把它们当成活跃状态的权威来源。

## Workflow 模型

### Plans

Plan 是大的阶段、里程碑或长期目标。一个项目可以有多个 plan，但一个 agent 工作流通常只激活一个 plan。

Plan 状态值：

- `new`
- `working`
- `blocked`
- `review`
- `done`
- `cancel`

### Todos

Todo 是 plan 内部的可执行步骤。最多支持两级：

```text
Plan
├── Todo
│   └── Child todo
└── Todo
```

第三级嵌套无效。如果只是顺序约束，应使用 dependency，而不是继续嵌套。

Todo 状态值：

- `pending`
- `in_progress`
- `blocked`
- `done`
- `cancel`

## 标准 Workflow CLI

实现应提供：

```bash
python .agents/workflow/workflow_cli.py init
python .agents/workflow/workflow_cli.py plan add --title "Database design"
python .agents/workflow/workflow_cli.py plan list
python .agents/workflow/workflow_cli.py plan show <plan_id>
python .agents/workflow/workflow_cli.py plan activate <plan_id>
python .agents/workflow/workflow_cli.py plan update <plan_id> --status done

python .agents/workflow/workflow_cli.py todo add --plan <plan_id> --title "Create schema"
python .agents/workflow/workflow_cli.py todo add --parent <todo_id> --title "Add indexes"
python .agents/workflow/workflow_cli.py todo list --plan <plan_id>
python .agents/workflow/workflow_cli.py todo update <todo_id> --status in_progress
python .agents/workflow/workflow_cli.py todo done <todo_id>
```

CLI 应直接查询 SQLite，不应要求 agent 把整张表 dump 到上下文里。

## 从 v0.1.x 迁移

旧项目可能包含：

```text
.agents/plans/*.md
.agents/plans/_active.md
.agents/todo/todo.sqlite
.agents/todo/todo_cli.py
```

迁移规则：

1. 把 markdown plans 导入 `workflow.sqlite:plans`。
2. 尽量用 `_active.md` 标记匹配的导入 plan 为 active。
3. 把旧 todo rows 导入 `workflow.sqlite:todos`。
4. 保留旧 todo 依赖关系。
5. 把已导入的旧文件移动到 `.agents/workflow/archive/imported-<timestamp>/`。
6. 不再向 legacy 位置写入活跃状态。

## 工作循环

Agent 进入项目后，遵循 OODRA 循环：

```text
Observe  -> 读取用户输入
Orient   -> 识别意图
Route    -> 通过 ROUTER.md 匹配资源
Retrieve -> 按需加载内容
Decide   -> 自己执行或委派子 Agent
Act      -> 执行工作
Verify   -> 验证结果
Write    -> 按需写回 workflow/bugs/memory
Report   -> 向用户汇报
```

对于多步骤工作，agent 应创建或更新 workflow plan 和 todo 列表。完成的工作应标记为 `done`，不要删除。

## 快速开始

1. 把 `.agents/` 目录复制到项目根目录。
2. 编辑 `memories/MEMORY.md`，写入项目信息。
3. 编辑 `roadmaps/ROADMAP.md`，写入路线图。
4. 运行 `python .agents/workflow/workflow_cli.py init`。
5. 如需 bug 追踪，运行 `python .agents/bugs/bugs_cli.py init`。
6. 让 Agent 工具读取 `.agents/AGENTS.md` 作为入口。

## 规范版本

当前版本：**v0.2.0**

版本号遵循语义化版本：

- **主版本号**：协议达到 1.0 后的不兼容结构变化
- **次版本号**：0.x 阶段的协议结构变化或功能新增
- **修订号**：兼容性说明和 bug 修复

版本信息在以下位置保持同步：

- `.agents/VERSION`
- `.agents/SOUL.md`
- `.agents/ROUTER.md`
- `.agents/AGENTS_SPEC.md`
- `.agents/MANIFEST.yaml`

## License

MIT
