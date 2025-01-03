def format_diff(diff_lines):
    formatted_diff = []
    for line in diff_lines:
        if line.startswith('--- ') or line.startswith('+++ '):
            # File names, keep them as-is (mark as "same")
            formatted_diff.append(("same", line))
        elif line.startswith('@@'):
            # Section header, keep it as-is (mark as "same")
            formatted_diff.append(("same", line + "\n"))
        elif line.startswith('+'):
            # Added lines
            if "ntp clock-period" in line:
                continue  # Skip this line
            formatted_diff.append(("add", line[1:]))
        elif line.startswith('-'):
            # Removed lines
            if "ntp clock-period" in line:
                continue  # Skip this line
            formatted_diff.append(("del", line[1:]))
        else:
            # Unchanged lines
            formatted_diff.append(("same", line))
    return formatted_diff

def check_changes(formatted_diff):
    sections = [[]]  # Initialize sections with an empty list
    i = 0
    for status, content in formatted_diff:
        if status == "same" and content.startswith('@@'):
            i += 1
            sections.append([])  # Append a new empty list for the next section
        sections[i].append((status, content))

    # Remove sections that don't contain 'del' or 'add'
    sections_to_remove = []
    for idx, section in enumerate(sections):
        contains_del_add = any(status in ["del", "add"] for status, _ in section)
        if not contains_del_add:
            sections_to_remove.append(idx)

    for idx in reversed(sections_to_remove):
        del sections[idx]

    return sections
