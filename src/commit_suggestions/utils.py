from commit_suggestions.models import (
    Hunk,
    Hunks,
    ModifiedCodeSnippets,
    ModifiedCodeSnippet,
)
from typing import List


def color_code(uncolored_code_txt: str) -> str:
    """Given a string of code, color added lines (+) green, removed lines (-) red, and unmodified lines white."""
    # Split the text into lines
    uncolored_code_lines = uncolored_code_txt.splitlines()

    colored_code_lines: List[str] = []
    for uncolored_code_line in uncolored_code_lines:
        if uncolored_code_line.startswith("+"):
            colored_code_line = "[green]" + uncolored_code_line + "[/]"
        elif uncolored_code_line.startswith("-"):
            colored_code_line = "[red]" + uncolored_code_line + "[/]"
        else:
            # Keep the text white
            colored_code_line = uncolored_code_line
        colored_code_lines.append(colored_code_line)

    return "\n".join(colored_code_lines)


def parse_git_diff_into_hunks(diff_txt: str) -> Hunks:
    """Create parsed hunks from git diff txt."""
    if not isinstance(diff_txt, str):
        raise TypeError("Argument must be a string")

    # Get rid of whitespace
    lines = diff_txt.splitlines()

    # Parse hunks from git diff text
    file_header: str = ""
    index_line: str = ""
    file_path_indicators: str = ""
    hunk_header: str = ""
    modified_code: str = ""
    line_index: int = 0
    hunks = Hunks(hunks=[])
    while line_index < len(lines):
        # Set the hunk meta data for the hunks we're looking at
        # NOTE: When we change this information, it means we're looking at hunks from a particular file
        if lines[line_index].startswith("diff --git"):
            file_header = lines[line_index]
            line_index += 1

            index_line = lines[line_index]
            line_index += 1

            file_path_indicators = "\n".join(lines[line_index : line_index + 2])
            line_index += 2

        # Set the hunk header information
        hunk_header = lines[line_index]
        line_index += 1

        # Parse modified code in the hunk
        modified_code_lines = []
        while (
            line_index < len(lines)
            and not lines[line_index].startswith("@@")
            and not lines[line_index].startswith("diff --git")
        ):
            modified_code_lines.append(lines[line_index])
            line_index += 1
        modified_code = "\n".join(modified_code_lines)

        # Add hunk to list of hunks
        hunks.hunks.append(
            Hunk(
                file_header=file_header,
                index_line=index_line,
                file_path_indicators=file_path_indicators,
                hunk_header=hunk_header,
                modified_code=modified_code,
            )
        )

    return hunks


def get_snippets_from_hunks(hunks: Hunks) -> ModifiedCodeSnippets:
    """Create Code Snippets from a git diff."""
    if not isinstance(hunks, Hunks):
        raise TypeError("Argument must be `Hunks`")

    # Create modified code snippets from hunks
    modified_code_snippets: ModifiedCodeSnippets = ModifiedCodeSnippets(
        modified_code_snippets=[]
    )
    for hunk in hunks.hunks:
        # Use the new filename as the filename in the code snippet
        filename = hunk.file_path_indicators.split("+++ b/", 1)[1].split(" ", 1)[0]

        # Use the index line to get the start and end lines of the code snippet
        start_line, index_line = (
            hunk.hunk_header.split("@@ ", 1)[1].split(" +", 1)[1].split(",", 1)
        )
        start_line = int(start_line)  # Cast string to integer
        end_line = int(index_line.split(" ", 1)[0]) + start_line

        # Get the modified code
        modified_code = hunk.modified_code

        modified_code_snippets.modified_code_snippets.append(
            ModifiedCodeSnippet(
                filename=filename,
                start_line=start_line,
                end_line=end_line,
                modified_code=modified_code,
            )
        )
    return modified_code_snippets
