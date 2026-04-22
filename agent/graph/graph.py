from typing import NotRequired, TypedDict, List

class FileDiff(TypedDict):
  file_path: str;
  added_lines: List[str];
  removed_lines: List[str];
  context: List[str];

class ReviewCommentDict(TypedDict):
  file: str;
  line: int;
  severity: str;
  category: str;
  message: str;
  suggestion: str;

class ReviewState(TypedDict):
  #input
  diff_files: List[FileDiff];

  #nodes output
  security_comments: NotRequired[List[ReviewCommentDict]];
  performance_comments: NotRequired[List[ReviewCommentDict]];
  style_comments: NotRequired[List[ReviewCommentDict]];

  #final output
  final_comments: NotRequired[List[ReviewCommentDict]];