#!/usr/bin/env python3
"""Bug tracking CLI for .agents/bugs/bugs.sqlite"""

import argparse
import sqlite3
import sys
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bugs.sqlite")

SCHEMA = """
CREATE TABLE IF NOT EXISTS bugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    category TEXT NOT NULL CHECK(category IN ('code', 'design', 'performance', 'security', 'compatibility')),
    severity TEXT NOT NULL CHECK(severity IN ('critical', 'high', 'medium', 'low')),
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'confirmed', 'assigned', 'fixing', 'review', 'closed', 'wontfix')),
    assigned_to TEXT DEFAULT NULL,
    resolution TEXT DEFAULT NULL,
    reporter TEXT DEFAULT 'unknown',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bugs_status ON bugs(status);
CREATE INDEX IF NOT EXISTS idx_bugs_category ON bugs(category);
CREATE INDEX IF NOT EXISTS idx_bugs_severity ON bugs(severity);
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
        "INSERT INTO bugs (title, description, category, severity, status, reporter, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, 'open', ?, ?, ?)",
        (args.title, args.description or "", args.category, args.severity, args.reporter or "unknown", now, now),
    )
    conn.commit()
    bug_id = cur.lastrowid
    conn.close()
    print(f"Bug #{bug_id} created: {args.title}")


def cmd_list(args):
    conn = get_db()
    filters = []
    params = []
    if args.status:
        filters.append("status = ?")
        params.append(args.status)
    if args.category:
        filters.append("category = ?")
        params.append(args.category)
    where = (" WHERE " + " AND ".join(filters)) if filters else ""
    rows = conn.execute(f"SELECT * FROM bugs{where} ORDER BY created_at DESC", params).fetchall()
    conn.close()
    if not rows:
        print("No bugs found.")
        return
    for r in rows:
        print(f"#{r['id']} [{r['status']}] [{r['severity']}] [{r['category']}] {r['title']}")
        if args.verbose and r["description"]:
            print(f"   {r['description'][:120]}")
        print(f"   assigned: {r['assigned_to'] or 'none'} | created: {r['created_at'][:10]}")


def cmd_query(args):
    conn = get_db()
    filters = []
    params = []
    if args.status:
        filters.append("status = ?")
        params.append(args.status)
    if args.category:
        filters.append("category = ?")
        params.append(args.category)
    if args.severity:
        filters.append("severity = ?")
        params.append(args.severity)
    if args.assigned_to:
        filters.append("assigned_to = ?")
        params.append(args.assigned_to)
    if args.search:
        filters.append("(title LIKE ? OR description LIKE ?)")
        params.extend([f"%{args.search}%", f"%{args.search}%"])
    where = (" WHERE " + " AND ".join(filters)) if filters else ""
    rows = conn.execute(f"SELECT * FROM bugs{where} ORDER BY created_at DESC", params).fetchall()
    conn.close()
    if not rows:
        print("No matching bugs.")
        return
    for r in rows:
        print(f"#{r['id']} [{r['status']}] [{r['severity']}] [{r['category']}] {r['title']}")
        print(f"   {r['description'][:200]}")
        print(f"   assigned: {r['assigned_to'] or 'none'} | resolution: {r['resolution'] or 'none'}")
        print(f"   created: {r['created_at'][:10]} | updated: {r['updated_at'][:10]}")
        print()


def cmd_update(args):
    conn = get_db()
    now = datetime.now().isoformat()
    updates = ["updated_at = ?"]
    params = [now]
    if args.status:
        updates.append("status = ?")
        params.append(args.status)
    if args.assigned_to:
        updates.append("assigned_to = ?")
        params.append(args.assigned_to)
    if args.severity:
        updates.append("severity = ?")
        params.append(args.severity)
    if args.category:
        updates.append("category = ?")
        params.append(args.category)
    if args.resolution:
        updates.append("resolution = ?")
        params.append(args.resolution)
    params.append(args.bug_id)
    cursor = conn.execute(f"UPDATE bugs SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    if affected == 0:
        print(f"Bug #{args.bug_id} not found.")
    else:
        print(f"Bug #{args.bug_id} updated.")


def cmd_show(args):
    conn = get_db()
    r = conn.execute("SELECT * FROM bugs WHERE id = ?", (args.bug_id,)).fetchone()
    conn.close()
    if not r:
        print(f"Bug #{args.bug_id} not found.")
        return
    print(f"Bug #{r['id']}: {r['title']}")
    print(f"  Status:     {r['status']}")
    print(f"  Category:   {r['category']}")
    print(f"  Severity:   {r['severity']}")
    print(f"  Assigned:   {r['assigned_to'] or 'none'}")
    print(f"  Reporter:   {r['reporter']}")
    print(f"  Resolution: {r['resolution'] or 'none'}")
    print(f"  Created:    {r['created_at']}")
    print(f"  Updated:    {r['updated_at']}")
    print(f"  Description:\n{r['description']}")


def cmd_export(args):
    conn = get_db()
    rows = conn.execute("SELECT * FROM bugs ORDER BY created_at DESC").fetchall()
    conn.close()
    lines = ["# Bug Report\n"]
    for r in rows:
        lines.append(f"## #{r['id']}: {r['title']}\n")
        lines.append(f"- Status: {r['status']}")
        lines.append(f"- Category: {r['category']}")
        lines.append(f"- Severity: {r['severity']}")
        lines.append(f"- Assigned: {r['assigned_to'] or 'none'}")
        lines.append(f"- Resolution: {r['resolution'] or 'none'}")
        lines.append(f"- Created: {r['created_at'][:10]}")
        lines.append(f"\n{r['description']}\n")
    output = "\n".join(lines)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Exported to {args.output}")
    else:
        print(output)


def main():
    parser = argparse.ArgumentParser(description="Bug tracking CLI")
    sub = parser.add_subparsers(dest="command")

    # init
    sub.add_parser("init", help="Initialize the database")

    # add
    p_add = sub.add_parser("add", help="Add a new bug")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--description", default="")
    p_add.add_argument("--category", required=True, choices=["code", "design", "performance", "security", "compatibility"])
    p_add.add_argument("--severity", required=True, choices=["critical", "high", "medium", "low"])
    p_add.add_argument("--reporter", default="unknown")

    # list
    p_list = sub.add_parser("list", help="List bugs")
    p_list.add_argument("--status", choices=["open", "confirmed", "assigned", "fixing", "review", "closed", "wontfix"])
    p_list.add_argument("--category", choices=["code", "design", "performance", "security", "compatibility"])
    p_list.add_argument("--verbose", "-v", action="store_true")

    # query
    p_query = sub.add_parser("query", help="Query bugs with filters")
    p_query.add_argument("--status", choices=["open", "confirmed", "assigned", "fixing", "review", "closed", "wontfix"])
    p_query.add_argument("--category", choices=["code", "design", "performance", "security", "compatibility"])
    p_query.add_argument("--severity", choices=["critical", "high", "medium", "low"])
    p_query.add_argument("--assigned-to")
    p_query.add_argument("--search")

    # update
    p_update = sub.add_parser("update", help="Update a bug")
    p_update.add_argument("bug_id", type=int)
    p_update.add_argument("--status", choices=["open", "confirmed", "assigned", "fixing", "review", "closed", "wontfix"])
    p_update.add_argument("--assigned-to")
    p_update.add_argument("--severity", choices=["critical", "high", "medium", "low"])
    p_update.add_argument("--category", choices=["code", "design", "performance", "security", "compatibility"])
    p_update.add_argument("--resolution")

    # show
    p_show = sub.add_parser("show", help="Show bug details")
    p_show.add_argument("bug_id", type=int)

    # export
    p_export = sub.add_parser("export", help="Export bugs report")
    p_export.add_argument("--format", choices=["markdown"], default="markdown")
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
        "export": cmd_export,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
