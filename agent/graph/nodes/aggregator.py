from typing import List, Dict, Tuple

from agent.graph.state import ReviewCommentDict, ReviewState

async def aggregator(state: ReviewState) -> Dict[str, List[ReviewCommentDict]]:
  all_comments: List[ReviewCommentDict] = []

  for key in ["security_comments", "performance_comments", "style_comments"]:
    all_comments.extend(state.get(key, []))

    seen: set[Tuple[str, int, str, str]] = set()
    deduped: List[ReviewCommentDict] = []
    for c in all_comments:
      dedup_key = (c["file"], c["line"], c["category"], c["message"])
      if dedup_key not in seen:
        seen.add(dedup_key)
        deduped.append(c)
  
  return {
    "final_comments": deduped
  }