#!/usr/bin/env python3
"""Todo tracking CLI for .agents/todo/todo.sqlite"""

import argparse
import sqlite3
import sys
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo.sqlite")

SCHEMA = """
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'blocked', 'done', 'cancel')),
    priority TEXT NOT NULL DEFAULT 'medium' CHECK(priority IN ('critical', 'high', 'medium', 'low')),
    assignee TEXT DEFAULT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS todo_deps (
    todo_id INTEGER NOT NULL,
    depends_on INTEGER NOT NULL,
    PRIMARY KEY (todo_id, depends_on),
    FOREIGN KEY (todo_id) REFERENCES todos(id),
    FOREIGN KEY (depends_on) REFERENCES todos(id)
);

CREATE INDEX IF NOT EXISTS idx_todos_status ON todos(status);
CREATE INDEX IF NOT EXISTS idx_todos_priority ON todos(priority);
"""


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def cmd_init(args):
    conn = get_db()
    conn.executescript(SCHEMA)
    conn.close()
    print("Database initialized.")


def cmd_add(args):
    conn = get_db()
    now = datetime.now().isoformat()
    cur = conn.execute(
        "INSERT INTO todos (title, description, status, priority, assignee, created_at, updated_at) "
        "VALUES (?, ?, 'pending', ?, ?, ?, ?)",
        (args.title, args.description or "", args.priority or "medium", args.assignee, now, now),
    )
    conn.commit()
    todo_id = cur.lastrowid
    if args.depends_on:
        for dep_id in args.depends_on:
            conn.execute("INSERT OR IGNORE INTO todo_deps (todo_id, depends_on) VALUES (?, ?)", (todo_id, dep_id))
        conn.commit()
    conn.close()
    print(f"Todo #{todo_id} created: {args.title}")


def cmd_list(args):
    conn = get_db()
    filters = []
    params = []
    if args.status:
        filters.append("status = ?")
        params.append(args.status)
    if args.priority:
        filters.append("priority = ?")
        params.append(args.priority)
    if args.assignee:
        filters.append("assignee = ?")
        params.append(args.assignee)
    where = (" WHERE " + " AND ".join(filters)) if filters else ""
    order = "ORDER BY CASE priority WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END, created_at"
    rows = conn.execute(f"SELECT * FROM todos{where} {order}", params).fetchall()
    conn.close()
    if not rows:
        print("No todos found.")
        return
    for r in rows:
        deps = _get_deps(conn, r["id"])
        dep_str = f" depends_on: {deps}" if deps else ""
        marker = ">>>" if r["status"] == "in_progress" else "   "
        print(f"{marker} #{r['id']} [{r['status']}] [{r['priority']}] {r['title']}{dep_str}")
        if r["assignee"]:
            print(f"      assignee: {r['assignee']}")


def _get_deps(conn, todo_id):
    rows = conn.execute("SELECT depends_on FROM todo_deps WHERE todo_id = ?", (todo_id,)).fetchall()
    return [r[0] for r in rows]


def cmd_query(args):
    conn = get_db()
    filters = []
    params = []
    if args.status:
        filters.append("status = ?")
        params.append(args.status)
    if args.priority:
        filters.append("priority = ?")
        params.append(args.priority)
    if args.assignee:
        filters.append("assignee = ?")
        params.append(args.assignee)
    if args.search:
        filters.append("(title LIKE ? OR description LIKE ?)")
        params.extend([f"%{args.search}%", f"%{args.search}%"])
    where = (" WHERE " + " AND ".join(filters)) if filters else ""
    order = "ORDER BY CASE priority WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END, created_at"
    rows = conn.execute(f"SELECT * FROM todos{where} {order}", params).fetchall()
    if not rows:
        print("No matching todos.")
        conn.close()
        return
    for r in rows:
        deps = _get_deps(conn, r["id"])
        dep_str = f" depends_on: {deps}" if deps else ""
        print(f"#{r['id']} [{r['status']}] [{r['priority']}] {r['title']}{dep_str}")
        print(f"   {r['description'][:200]}")
        print(f"   assignee: {r['assignee'] or 'none'} | created: {r['created_at'][:10]}")
        print()
    conn.close()


def cmd_update(args):
    conn = get_db()
    now = datetime.now().isoformat()
    updates = ["updated_at = ?"]
    params = [now]
    if args.status:
        updates.append("status = ?")
        params.append(args.status)
    if args.priority:
        updates.append("priority = ?")
        params.append(args.priority)
    if args.assignee:
        updates.append("assignee = ?")
        params.append(args.assignee)
    params.append(args.todo_id)
    cursor = conn.execute(f"UPDATE todos SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    if affected == 0:
        print(f"Todo #{args.todo_id} not found.")
    else:
        print(f"Todo #{args.todo_id} updated.")


def cmd_show(args):
    conn = get_db()
    r = conn.execute("SELECT * FROM todos WHERE id = ?", (args.todo_id,)).fetchone()
    if not r:
        print(f"Todo #{args.todo_id} not found.")
        conn.close()
        return
    deps = _get_deps(conn, args.todo_id)
    blocked_by = _get_blocked_by(conn, args.todo_id)
    conn.close()
    print(f"Todo #{r['id']}: {r['title']}")
    print(f"  Status:    {r['status']}")
    print(f"  Priority:  {r['priority']}")
    print(f"  Assignee:  {r['assignee'] or 'none'}")
    print(f"  Created:   {r['created_at']}")
    print(f"  Updated:   {r['updated_at']}")
    if deps:
        print(f"  Depends on: {deps}")
    if blocked_by:
        print(f"  Blocking:  {blocked_by}")
    print(f"  Description:\n{r['description']}")


def _get_blocked_by(conn, todo_id):
    rows = conn.execute("SELECT todo_id FROM todo_deps WHERE depends_on = ?", (todo_id,)).fetchall()
    return [r[0] for r in rows]


def _would_create_cycle(conn, todo_id, depends_on):
    """Check if adding todo_id -> depends_on would create a cycle."""
    if todo_id == depends_on:
        return True
    visited = set()
    queue = [depends_on]
    while queue:
        current = queue.pop(0)
        if current == todo_id:
            return True
        if current in visited:
            continue
        visited.add(current)
        deps = conn.execute("SELECT depends_on FROM todo_deps WHERE todo_id = ?", (current,)).fetchall()
        for d in deps:
            queue.append(d[0])
    return False


def cmd_add_dep(args):
    conn = get_db()
    if args.todo_id == args.depends_on:
        conn.close()
        print(f"Error: Todo #{args.todo_id} cannot depend on itself.")
        return
    if _would_create_cycle(conn, args.todo_id, args.depends_on):
        conn.close()
        print(f"Error: Adding this dependency would create a cycle (Todo #{args.todo_id} -> #{args.depends_on}).")
        return
    conn.execute("INSERT OR IGNORE INTO todo_deps (todo_id, depends_on) VALUES (?, ?)", (args.todo_id, args.depends_on))
    conn.commit()
    conn.close()
    print(f"Todo #{args.todo_id} now depends on #{args.depends_on}.")


def cmd_rm_dep(args):
    conn = get_db()
    conn.execute("DELETE FROM todo_deps WHERE todo_id = ? AND depends_on = ?", (args.todo_id, args.depends_on))
    conn.commit()
    conn.close()
    print(f"Removed dependency: Todo #{args.todo_id} no longer depends on #{args.depends_on}.")


def cmd_export(args):
    conn = get_db()
    rows = conn.execute("SELECT * FROM todos ORDER BY CASE priority WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END").fetchall()
    conn.close()
    lines = ["# Todo List\n"]
    for r in rows:
        marker = "[x]" if r["status"] == "done" else "[ ]"
        lines.append(f"- {marker} #{r['id']} [{r['priority']}] {r['title']} ({r['status']})")
    output = "\n".join(lines)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Exported to {args.output}")
    else:
        print(output)


def main():
    parser = argparse.ArgumentParser(description="Todo tracking CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Initialize the database")

    p_add = sub.add_parser("add", help="Add a new todo")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--description", default="")
    p_add.add_argument("--priority", choices=["critical", "high", "medium", "low"], default="medium")
    p_add.add_argument("--assignee", default=None)
    p_add.add_argument("--depends-on", type=int, action="append")

    p_list = sub.add_parser("list", help="List todos")
    p_list.add_argument("--status", choices=["pending", "in_progress", "blocked", "done", "cancel"])
    p_list.add_argument("--priority", choices=["critical", "high", "medium", "low"])
    p_list.add_argument("--assignee")

    p_query = sub.add_parser("query", help="Query todos with filters")
    p_query.add_argument("--status", choices=["pending", "in_progress", "blocked", "done", "cancel"])
    p_query.add_argument("--priority", choices=["critical", "high", "medium", "low"])
    p_query.add_argument("--assignee")
    p_query.add_argument("--search")

    p_update = sub.add_parser("update", help="Update a todo")
    p_update.add_argument("todo_id", type=int)
    p_update.add_argument("--status", choices=["pending", "in_progress", "blocked", "done", "cancel"])
    p_update.add_argument("--priority", choices=["critical", "high", "medium", "low"])
    p_update.add_argument("--assignee")

    p_show = sub.add_parser("show", help="Show todo details")
    p_show.add_argument("todo_id", type=int)

    p_dep = sub.add_parser("add-dep", help="Add dependency")
    p_dep.add_argument("todo_id", type=int)
    p_dep.add_argument("depends_on", type=int)

    p_rmdep = sub.add_parser("rm-dep", help="Remove dependency")
    p_rmdep.add_argument("todo_id", type=int)
    p_rmdep.add_argument("depends_on", type=int)

    p_export = sub.add_parser("export", help="Export todos")
    p_export.add_argument("--output")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "init": cmd_init,
        "add": cmd_add,
        "list": cmd_list,
        "query": cmd_query,
        "update": cmd_update,
        "show": cmd_show,
        "add-dep": cmd_add_dep,
        "rm-dep": cmd_rm_dep,
        "export": cmd_export,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
