#!/usr/bin/env python3

"""
Python CLI utility to manage:
- Bash aliases in ~/.bashrc
- Environment exports in ~/.bashrc
- Safe sudoers updates using visudo

Usage examples:
  tool.py alias add ll "ls -l"
  tool.py alias remove ll
  tool.py export add JAVA_HOME "/usr/lib/jvm/java-21"
  tool.py sudoers add "marcelo ALL=(ALL) NOPASSWD: /usr/bin/systemctl"
"""

import argparse
import os
import subprocess
from pathlib import Path

BASHRC = Path.home() / ".bashrc"
SUDOERS_TMP = "/tmp/sudoers_edit"


def ensure_bashrc():
    if not BASHRC.exists():
        BASHRC.touch()


def add_alias(name, command):
    ensure_bashrc()
    line = f"alias {name}='{command}'\n"
    with open(BASHRC, "a") as f:
        f.write(line)
    print(f"Alias added: {line.strip()}")


def remove_alias(name):
    ensure_bashrc()
    lines = []
    with open(BASHRC) as f:
        lines = f.readlines()
    with open(BASHRC, "w") as f:
        for line in lines:
            if not line.strip().startswith(f"alias {name}="):
                f.write(line)
    print(f"Alias removed: {name}")


def add_export(var, value):
    ensure_bashrc()
    line = f"export {var}={value}\n"
    with open(BASHRC, "a") as f:
        f.write(line)
    print(f"Export added: {line.strip()}")


def remove_export(var):
    ensure_bashrc()
    lines = []
    with open(BASHRC) as f:
        lines = f.readlines()
    with open(BASHRC, "w") as f:
        for line in lines:
            if not line.strip().startswith(f"export {var}="):
                f.write(line)
    print(f"Export removed: {var}")


def sudoers_add(entry):
    # Write current sudoers to temp
    subprocess.run(["sudo", "cp", "/etc/sudoers", SUDOERS_TMP], check=True)

    # Append entry
    with open(SUDOERS_TMP, "a") as f:
        f.write(f"\n{entry}\n")

    # Validate with visudo
    result = subprocess.run(["sudo", "visudo", "-c", "-f", SUDOERS_TMP])
    if result.returncode == 0:
        subprocess.run(["sudo", "cp", SUDOERS_TMP, "/etc/sudoers"], check=True)
        print("Sudoers updated successfully.")
    else:
        print("Error: sudoers entry invalid. No changes were made.")


def main():
    parser = argparse.ArgumentParser(description="Manage bash aliases, exports, and sudoers safely.")
    sub = parser.add_subparsers(dest="cmd")

    # Alias
    alias = sub.add_parser("alias")
    alias_sub = alias.add_subparsers(dest="action")

    alias_add = alias_sub.add_parser("add")
    alias_add.add_argument("name")
    alias_add.add_argument("command")

    alias_rm = alias_sub.add_parser("remove")
    alias_rm.add_argument("name")

    # Export
    export = sub.add_parser("export")
    exp_sub = export.add_subparsers(dest="action")

    exp_add = exp_sub.add_parser("add")
    exp_add.add_argument("var")
    exp_add.add_argument("value")

    exp_rm = exp_sub.add_parser("remove")
    exp_rm.add_argument("var")

    # Sudoers
    sudo = sub.add_parser("sudoers")
    sudo_add = sudo.add_subparsers(dest="action").add_parser("add")
    sudo_add.add_argument("entry")

    args = parser.parse_args()

    if args.cmd == "alias":
        if args.action == "add":
            add_alias(args.name, args.command)
        elif args.action == "remove":
            remove_alias(args.name)

    elif args.cmd == "export":
        if args.action == "add":
            add_export(args.var, args.value)
        elif args.action == "remove":
            remove_export(args.var)

    elif args.cmd == "sudoers":
        if args.action == "add":
            sudoers_add(args.entry)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
