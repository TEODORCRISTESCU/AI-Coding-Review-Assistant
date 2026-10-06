import re


_HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def diff_parser(diff: str) -> dict[str, set[int]]:
    added_lines: dict[str, set[int]] = {}
    file_path: str | None = None
    new_line_number: int | None = None

    for line in diff.splitlines():

        if line.startswith("diff --git "):
            file_path = None
            continue

        if new_line_number is None and line.startswith("+++ "):
            path = line[4:]
            if path == "/dev/null":
                file_path = None
            else:
                file_path = path[2:] if path.startswith("b/") else path
                added_lines.setdefault(file_path, set())
            new_line_number = None
            continue

        hunk_match = _HUNK_HEADER.match(line)
        if hunk_match:
            new_line_number = int(hunk_match.group(1))
            continue

        if file_path is None or new_line_number is None or not line:
            continue

        prefix = line[0]
        if prefix == "+":
            added_lines[file_path].add(new_line_number)
            new_line_number += 1
        elif prefix == " ":
            new_line_number += 1

    return added_lines
