import json

from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential

from agent.graph.state import ReviewCommentDict

def parse_llm_response(content: str) -> List[ReviewCommentDict]:
  try:
    data = json.loads(content)
    if isinstance(data, list):
      return data
    return []
  except Exception:
    return []
  
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
async def call_llm(chain, payload):
  return await chain.ainvoke(payload)

def sanitize_comments(comments):
  valid = []
  for c in comments:
    if "file" in c and "line" in c:
      valid.append(c)
  return valid