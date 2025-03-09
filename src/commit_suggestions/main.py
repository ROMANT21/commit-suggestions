from openai import OpenAI
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from commit_suggestions.models import CommitSuggestions, Hunks, ModifiedCodeSnippets
from commit_suggestions.utils import (
    parse_git_diff_into_hunks,
    get_snippets_from_hunks,
    color_code,
)
import subprocess
from git import Repo

console = Console()


def prompt_user(
    commit_suggestions: CommitSuggestions,
    modified_code_snippets: ModifiedCodeSnippets,
    hunks: Hunks,
    repo: Repo,
):
    """Given a set of commit suggestions, show them to the user. Let them edit, reject, or execute them."""
    # Show the user each commit suggestion
    for commit_suggestion in commit_suggestions.commit_suggestions:
        # Show all the code changes associated with the suggested commit
        for code_snippet_index in commit_suggestion.code_snippet_indices:
            modified_code = modified_code_snippets.modified_code_snippets[
                code_snippet_index
            ]

            table = Table()
            table.add_column(modified_code.filename)
            table.add_row(color_code(modified_code.modified_code))
            console.print(table)

        # Show the suggested commit message
        console.print(f"[bold blue]Suggested Message:[/] {commit_suggestion.message}")

        # Ask the user if they accept the suggested commit message
        accepted_suggested_commit = Confirm.ask(
            "Would you like to accept the suggested commit?"
        )

        # Execute git commands depending on response
        console.print("[blue]Staging code snippets...[/]")
        if accepted_suggested_commit:
            for index in commit_suggestion.code_snippet_indices:
                hunk = hunks.hunks[index]
                # I'll have to work with this:  git diff | git apply --cached
                git_diff_bytes = "".join(
                    [
                        hunk.file_header,
                        "\n",
                        hunk.index_line,
                        "\n",
                        hunk.file_path_indicators,
                        "\n",
                        hunk.hunk_header,
                        "\n",
                        hunk.modified_code,
                        "\n",
                    ]
                )
                subprocess.run(
                    ["git", "apply", "--cached", "-"],
                    input=git_diff_bytes,
                    text=True,
                    cwd=repo.working_dir,
                )
            console.print("[blue]Executing git commit...[/]")
            subprocess.run(["git", "commit", "-m", f"{commit_suggestion.message}"])


def main():
    # Get differences between working directory and git HEAD
    console.rule("[bold blue]GATHERING CHANGES TO CODEBASE[/]")
    console.print("[yellow]Parsing `git diff` into code snippets...[/]")
    current_repo = Repo()
    diff_txt = current_repo.git.diff()
    hunks = parse_git_diff_into_hunks(diff_txt)
    if len(hunks.hunks) == 0:
        console.print("There are no changes! Exiting Program!")
        return
    modified_code_snippets = get_snippets_from_hunks(hunks)
    console.print("[green]Done parsing `git diff`![/]")

    # Create a openai client
    client = OpenAI()

    commit_message_generator_prompt = f"""
    You are a commit message generator. You will be given a series of code changes (parsed from the `git diff` command), and you are expected
    to return suggested git commits.

    Input Details:
    * The code changes are called modified code snippets.
    * A modified code snippet contains:
        * `filename` (The filepath to the modified code)
        * `start_line` and `end_line` (line numbers of changes in `filename`)
        * `modified_code` (the actual code change)
    * The order that the code changes are given does not matter, so do not assume that the changes are in sequential order.

    Output Details:
    * Each commit suggestion should include:
        * A commit message (following Conventional Commits Format)
        * The modified code snippet indices from the input associated with the commit.
            * Possible indices are in the range 0-{len(modified_code_snippets.modified_code_snippets) - 1}
            * Don't be afraid to group hunks that you think are related!
    * The commits should be ordered logically, grouping related changes together (e.g., refactoring before feature additions).
    * The git commit suggestion is made up of a suggested message and modified code snippets to stage.
        * The generated message should use conventional commit standards. The `start_line` should be the line number the code snippet starts on and the `end_line` should be the end line of the code snippet.
    * Commit messages should be concise and clear (limit the subject line to 72 characters).
    """

    # Ask chat gpt for commit suggestions
    console.rule("[bold blue]SUGGESTING COMMITS[/]")
    console.print("[yellow]Creating commit suggestions...[/]")
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        store=True,
        messages=[
            {
                "role": "system",
                "content": commit_message_generator_prompt,
            },
            {
                "role": "user",
                "content": modified_code_snippets.model_dump_json(indent=2),
            },
        ],
        response_format=CommitSuggestions,
    )

    commit_suggestions = completion.choices[0].message.parsed
    if commit_suggestions is None:
        console.print("There was an error generating prompts! Exiting Program!")
        return
    console.print("Done generating Prompts!")

    prompt_user(commit_suggestions, modified_code_snippets, hunks, current_repo)
    console.print("Exiting Program! You're so good at commits ;)")


if __name__ == "__main__":
    print("Hello")
    main()
