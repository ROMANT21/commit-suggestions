from commit_suggestions.utils import parse_git_diff_into_hunks
from commit_suggestions.models import Hunk, Hunks
from textwrap import dedent
import pytest


@pytest.mark.parametrize("a", [(None), (1), (2.4), (True)])
def test_parse_git_diff_wrong_input(a):
    """Test the parse git diff function when the input is not a string"""
    with pytest.raises(TypeError):
        parse_git_diff_into_hunks(a)


def test_parse_git_diff_no_files_no_changes():
    """Test the parse git diff function when there is no diffs."""
    actual_hunks = parse_git_diff_into_hunks("")
    assert len(actual_hunks.hunks) == 0


def test_parse_git_diff_one_line_change():
    """Test the parse git diff function when there is only one line changed in a file."""
    diff_txt = dedent("""\
        diff --git a/README.md b/README.md
        index e69de29..b6c2d0e 100644
        --- a/README.md
        +++ b/README.md
        @@ -0,0 +1 @@
        +# Commit Suggestions""")

    expected_hunks = Hunks(
        hunks=[
            Hunk(
                file_header="diff --git a/README.md b/README.md",
                index_line="index e69de29..b6c2d0e 100644",
                file_path_indicators="--- a/README.md\n+++ b/README.md",
                hunk_header="@@ -0,0 +1 @@",
                modified_code=dedent("""\
                    +# Commit Suggestions"""),
            )
        ]
    )

    actual_hunks = parse_git_diff_into_hunks(diff_txt)
    assert expected_hunks == actual_hunks


def test_parse_git_diff_one_file_one_change():
    """Test the parse git diff function when one file had one change."""
    diff_txt = dedent("""\
        diff --git a/utils.py b/utils.py
        index 3a5b3c2..7d9f6e1 100644
        --- a/utils.py
        +++ b/utils.py
        @@ -5,2 +5,2 @@ def say_hello(name):
        -    return f"Hello, {name}"
        +    return f"Hello, {name}!\"""")

    expected_hunks = Hunks(
        hunks=[
            Hunk(
                file_header="diff --git a/utils.py b/utils.py",
                index_line="index 3a5b3c2..7d9f6e1 100644",
                file_path_indicators="--- a/utils.py\n+++ b/utils.py",
                hunk_header="@@ -5,2 +5,2 @@ def say_hello(name):",
                modified_code=dedent("""\
                    -    return f"Hello, {name}"
                    +    return f"Hello, {name}!\""""),
            )
        ]
    )

    actual_hunks = parse_git_diff_into_hunks(diff_txt)
    assert expected_hunks == actual_hunks


def test_parse_git_diff_one_file_multiple_changes():
    """Test parsing a git diff message when one file had multiple changes"""
    diff_txt = dedent("""\
        diff --git a/utils.py b/utils.py
        index 3a5b3c2..7d9f6e1 100644
        --- a/utils.py
        +++ b/utils.py
        @@ -5,2 +5,2 @@ def say_hello(name):
        -    return f"Hello, {name}"
        +    return f"Hello, {name}!\"
        @@ -10,7 +10,7 @@ def check_number(n):
        def check_number(n):
        -    if n > 0:
        +    if n >= 0:
            return "Positive"
        return "Negative\"""")

    expected_hunks = Hunks(
        hunks=[
            Hunk(
                file_header="diff --git a/utils.py b/utils.py",
                index_line="index 3a5b3c2..7d9f6e1 100644",
                file_path_indicators="--- a/utils.py\n+++ b/utils.py",
                hunk_header="@@ -5,2 +5,2 @@ def say_hello(name):",
                modified_code=dedent("""\
                    -    return f"Hello, {name}"
                    +    return f"Hello, {name}!\""""),
            ),
            Hunk(
                file_header="diff --git a/utils.py b/utils.py",
                index_line="index 3a5b3c2..7d9f6e1 100644",
                file_path_indicators="--- a/utils.py\n+++ b/utils.py",
                hunk_header="@@ -10,7 +10,7 @@ def check_number(n):",
                modified_code=dedent("""\
                    def check_number(n):
                    -    if n > 0:
                    +    if n >= 0:
                        return "Positive"
                    return "Negative\""""),
            ),
        ]
    )

    actual_hunks = parse_git_diff_into_hunks(diff_txt)
    assert expected_hunks == actual_hunks


def test_parse_git_diff_multiple_file_one_change_each():
    """Test parsing a git diff message when multiple files have one change."""
    diff_txt = dedent("""\
        diff --git a/utils.py b/utils.py
        index 3a5b3c2..7d9f6e1 100644
        --- a/utils.py
        +++ b/utils.py
        @@ -5,2 +5,2 @@ def say_hello(name):
        -    return f"Hello, {name}"
        +    return f"Hello, {name}!\"
        diff --git a/main.py b/main.py
        index 3a5b3c2..7d9f6e1 100644
        --- a/main.py
        +++ b/main.py
        @@ -10,7 +10,7 @@ def check_number(n):
        def check_number(n):
        -    if n > 0:
        +    if n >= 0:
            return "Positive"
        return "Negative\"""")

    expected_hunks = Hunks(
        hunks=[
            Hunk(
                file_header="diff --git a/utils.py b/utils.py",
                index_line="index 3a5b3c2..7d9f6e1 100644",
                file_path_indicators="--- a/utils.py\n+++ b/utils.py",
                hunk_header="@@ -5,2 +5,2 @@ def say_hello(name):",
                modified_code=dedent("""\
                    -    return f"Hello, {name}"
                    +    return f"Hello, {name}!\""""),
            ),
            Hunk(
                file_header="diff --git a/main.py b/main.py",
                index_line="index 3a5b3c2..7d9f6e1 100644",
                file_path_indicators="--- a/main.py\n+++ b/main.py",
                hunk_header="@@ -10,7 +10,7 @@ def check_number(n):",
                modified_code=dedent("""\
                    def check_number(n):
                    -    if n > 0:
                    +    if n >= 0:
                        return "Positive"
                    return "Negative\""""),
            ),
        ]
    )

    actual_hunks = parse_git_diff_into_hunks(diff_txt)
    assert expected_hunks == actual_hunks


def test_parse_git_diff_multiple_file_multiple_changes():
    """Test parsing a git diff message when multiple files have one change."""
    diff_txt = dedent("""\
        diff --git a/utils.py b/utils.py
        index 3a5b3c2..7d9f6e1 100644
        --- a/utils.py
        +++ b/utils.py
        @@ -1,5 +1,6 @@
         from openai import OpenAI
        -from commit_suggestions.models import CommitSuggestions
        +from models import CommitSuggestions
        +from git import Repo
        @@ -10,2 +10,2 @@ def say_hello(name):
        -    return f"Hello, {name}"
        +    return f"Hello, {name}!\"
        diff --git a/main.py b/main.py
        index 3a5b3c2..7d9f6e1 100644
        --- a/main.py
        +++ b/main.py
        @@ -10,7 +10,7 @@ def check_number(n):
        def check_number(n):
        -    if n > 0:
        +    if n >= 0:
            return "Positive"
        return "Negative\"""")

    expected_hunks = Hunks(
        hunks=[
            Hunk(
                file_header="diff --git a/utils.py b/utils.py",
                index_line="index 3a5b3c2..7d9f6e1 100644",
                file_path_indicators="--- a/utils.py\n+++ b/utils.py",
                hunk_header="@@ -1,5 +1,6 @@",
                modified_code=dedent("""\
                    from openai import OpenAI
                   -from commit_suggestions.models import CommitSuggestions
                   +from models import CommitSuggestions
                   +from git import Repo"""),
            ),
            Hunk(
                file_header="diff --git a/utils.py b/utils.py",
                index_line="index 3a5b3c2..7d9f6e1 100644",
                file_path_indicators="--- a/utils.py\n+++ b/utils.py",
                hunk_header="@@ -10,2 +10,2 @@ def say_hello(name):",
                modified_code=dedent("""\
                    -    return f"Hello, {name}"
                    +    return f"Hello, {name}!\""""),
            ),
            Hunk(
                file_header="diff --git a/main.py b/main.py",
                index_line="index 3a5b3c2..7d9f6e1 100644",
                file_path_indicators="--- a/main.py\n+++ b/main.py",
                hunk_header="@@ -10,7 +10,7 @@ def check_number(n):",
                modified_code=dedent("""\
                    def check_number(n):
                    -    if n > 0:
                    +    if n >= 0:
                        return "Positive"
                    return "Negative\""""),
            ),
        ]
    )

    actual_hunks = parse_git_diff_into_hunks(diff_txt)
    assert expected_hunks.hunks[2] == actual_hunks.hunks[2]


"""
Other test cases for future:
    RENAME TEST CASE
    diff --git a/old_name.py b/new_name.py
    similarity index 100%
    rename from old_name.py
    rename to new_name.py

    MODIFYING AN IF CONDITION CASE
    diff --git a/main.py b/main.py
    index 8c7b3d2..5e6a1f4 100644
    --- a/main.py
    +++ b/main.py
    @@ -10,7 +10,7 @@ def check_number(n):

     def check_number(n):
    -    if n > 0:
    +    if n >= 0:
             return "Positive"
         return "Negative"

    CHANGING A FUNCTION SIGNATURE CASE
    diff --git a/database.py b/database.py
    index 3b2a1c4..8f7e9d1 100644
    --- a/database.py
    +++ b/database.py
    @@ -3,7 +3,7 @@ import sqlite3

     def connect_db():
    -    return sqlite3.connect("database.db")
    +    return sqlite3.connect("database.sqlite3")

    UPDATING A LIST OR DICTIONARY CASE
    diff --git a/config.py b/config.py
    index 1a2b3c4..5d6e7f8 100644
    --- a/config.py
    +++ b/config.py
    @@ -2,5 +2,5 @@ settings = {
    -    "debug": True,
    +    "debug": False,
         "max_connections": 10,
    -    "timeout": 30
    +    "timeout": 60
     }


    COMMENT CHANGE
    diff --git a/api.py b/api.py
    index a1b2c3d..f4e5d6a 100644
    --- a/api.py
    +++ b/api.py
    @@ -1,5 +1,5 @@
    -def fetch_data():
    -    \"""Fetches data from the server\"""
    +def fetch_data():
    +    \"""Fetches data from the server (updated docstring)\"""
         pass

    MULTIPLE FILE CHANGES
"""
