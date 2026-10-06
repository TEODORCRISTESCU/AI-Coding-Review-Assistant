import re
from fnmatch import fnmatchcase


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

def filter_diff(diff: str, ignored_paths: list[str]) -> str:
    kept_sections = []

    sections = diff.split("diff --git ")

    for section in sections[1:]:
        section = "diff --git " + section
        file_path = None

        for line in section.splitlines():
            if line.startswith("@@ "):
                break

            if line.startswith("+++ b/"):
                file_path = line[6:]
                break

            if line == "+++ /dev/null":
                # Deleted file: use its old path.
                for old_line in section.splitlines():
                    if old_line.startswith("--- a/"):
                        file_path = old_line[6:]
                        break
                break

        if file_path is None or not any(
            fnmatchcase(file_path, pattern)
            for pattern in ignored_paths
        ):
            kept_sections.append(section)

    return "".join(kept_sections)