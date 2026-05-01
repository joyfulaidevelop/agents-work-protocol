#!/usr/bin/env python3
"""Chat history CLI for .agents/chats/chats.sqlite"""

import argparse
import sqlite3
import sys
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chats.sqlite")

SCHEMA = """
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary TEXT NOT NULL,
    participants TEXT DEFAULT '',
    tags TEXT DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'agent', 'system')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chats_tags ON chats(tags);
CREATE INDEX IF NOT EXISTS idx_chat_messages_chat ON chat_messages(chat_id);
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
        "INSERT INTO chats (summary, participants, tags, created_at) VALUES (?, ?, ?, ?)",
        (args.summary, args.participants or "", args.tags or "", now),
    )
    conn.commit()
    chat_id = cur.lastrowid
    conn.close()
    print(f"Chat #{chat_id} saved: {args.summary[:80]}")


def cmd_add_msg(args):
    conn = get_db()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO chat_messages (chat_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (args.chat_id, args.role, args.content, now),
    )
    conn.commit()
    conn.close()
    print(f"Message added to chat #{args.chat_id}.")


def cmd_list(args):
    conn = get_db()
    rows = conn.execute("SELECT * FROM chats ORDER BY created_at DESC LIMIT ?", (args.limit or 20,)).fetchall()
    conn.close()
    if not rows:
        print("No chats found.")
        return
    for r in rows:
        print(f"#{r['id']} [{r['created_at'][:10]}] {r['summary'][:80]}")
        if r["tags"]:
            print(f"   tags: {r['tags']}")
        if r["participants"]:
            print(f"   participants: {r['participants']}")


def cmd_search(args):
    conn = get_db()
    query_str = f"%{args.query}%"
    rows = conn.execute(
        "SELECT * FROM chats WHERE summary LIKE ? OR tags LIKE ? ORDER BY created_at DESC LIMIT ?",
        (query_str, query_str, args.limit or 10),
    ).fetchall()
    if not rows:
        print("No matching chats.")
        conn.close()
        return
    for r in rows:
        print(f"#{r['id']} [{r['created_at'][:10]}] {r['summary'][:100]}")
        if r["tags"]:
            print(f"   tags: {r['tags']}")
        print()
    conn.close()


def cmd_get(args):
    conn = get_db()
    chat = conn.execute("SELECT * FROM chats WHERE id = ?", (args.chat_id,)).fetchone()
    if not chat:
        print(f"Chat #{args.chat_id} not found.")
        conn.close()
        return
    print(f"Chat #{chat['id']}: {chat['summary']}")
    print(f"  Participants: {chat['participants']}")
    print(f"  Tags: {chat['tags']}")
    print(f"  Created: {chat['created_at']}")

    if args.messages:
        msgs = conn.execute(
            "SELECT * FROM chat_messages WHERE chat_id = ? ORDER BY created_at",
            (args.chat_id,),
        ).fetchall()
        if msgs:
            print(f"\n  Messages ({len(msgs)}):")
            for m in msgs:
                print(f"    [{m['role']}] {m['content'][:200]}")
    conn.close()


def cmd_export(args):
    conn = get_db()
    rows = conn.execute("SELECT * FROM chats ORDER BY created_at DESC").fetchall()
    lines = ["# Chat History\n"]
    for r in rows:
        lines.append(f"## #{r['id']}: {r['summary']}\n")
        lines.append(f"- Participants: {r['participants']}")
        lines.append(f"- Tags: {r['tags']}")
        lines.append(f"- Created: {r['created_at'][:10]}\n")
        if args.with_messages:
            msgs = conn.execute(
                "SELECT * FROM chat_messages WHERE chat_id = ? ORDER BY created_at",
                (r["id"],),
            ).fetchall()
            for m in msgs:
                lines.append(f"  **{m['role']}**: {m['content'][:500]}\n")
    conn.close()
    output = "\n".join(lines)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Exported to {args.output}")
    else:
        print(output)


def main():
    parser = argparse.ArgumentParser(description="Chat history CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Initialize the database")

    p_add = sub.add_parser("add", help="Save a chat summary")
    p_add.add_argument("--summary", required=True)
    p_add.add_argument("--participants", default="")
    p_add.add_argument("--tags", default="")

    p_msg = sub.add_parser("add-msg", help="Add a message to a chat")
    p_msg.add_argument("chat_id", type=int)
    p_msg.add_argument("--role", required=True, choices=["user", "agent", "system"])
    p_msg.add_argument("--content", required=True)

    p_list = sub.add_parser("list", help="List recent chats")
    p_list.add_argument("--limit", type=int, default=20)

    p_search = sub.add_parser("search", help="Search chats")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--limit", type=int, default=10)

    p_get = sub.add_parser("get", help="Get chat details")
    p_get.add_argument("chat_id", type=int)
    p_get.add_argument("--messages", action="store_true", help="Include messages")

    p_export = sub.add_parser("export", help="Export chat history")
    p_export.add_argument("--output")
    p_export.add_argument("--with-messages", action="store_true")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "init": cmd_init,
        "add": cmd_add,
        "add-msg": cmd_add_msg,
        "list": cmd_list,
        "search": cmd_search,
        "get": cmd_get,
        "export": cmd_export,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
