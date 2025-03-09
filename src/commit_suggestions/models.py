from pydantic import BaseModel
from typing import List


class AddedFiles(BaseModel):
    added_files: List[str]


class DeletedFiles(BaseModel):
    deleted_files: List[str]


class ModifiedCodeSnippet(BaseModel):
    """This represents a section of modified code in the codebase."""

    filename: str
    modified_code: str
    start_line: int
    end_line: int


class ModifiedCodeSnippets(BaseModel):
    modified_code_snippets: List[ModifiedCodeSnippet]


class Hunk(BaseModel):
    """This represents a parsed git hunk."""

    file_header: str
    index_line: str
    file_path_indicators: str
    hunk_header: str
    modified_code: str


class Hunks(BaseModel):
    hunks: List[Hunk]


class StageSuggestion(BaseModel):
    """This class represents the arguments in a `git add` command  used to stage content in a file."""

    filename: str
    start_line: int
    end_line: int


class CommitSuggestion(BaseModel):
    """Represents a commit suggestion"""

    message: str
    code_snippet_indices: List[int]


class CommitSuggestions(BaseModel):
    commit_suggestions: List[CommitSuggestion]
