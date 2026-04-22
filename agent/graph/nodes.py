from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import json

from agent.graph.graph import ReviewCommentDict, ReviewState

llm = ChatOpenAI(
  model="gpt-4o-mini",
  temperature=0
)

security_prompt = ChatPromptTemplate.from_messages([
  ("system", """
  You are a senior security engineer performing a code review.

  Your job is to identify SECURITY ISSUES in code diffs.

  Focus ONLY on:
  - SQL Injection
  - Hardcoded secrets (API keys, tokens, passwords)
  - Authentication and authorization flaws
  - Vulnerable or outdated dependencies
  - Unsafe deserialization
  - Command injection

  Rules:
  - Only report REAL issues (avoid false positives)
  - Be concise and technical
  - Always include a fix suggestion
  - If no issues found, return an empty list

  Output MUST be valid JSON array:
  [
    {
      "file": "string",
      "line": number,
      "severity": "critical|warning|info",
      "category": "security",
      "message": "string",
      "suggestion": "string"
    }
  ]
  """),
  ("human", """
  Analyze this file diff:

  File: {file_path}

  Added lines:
  {added_lines}

  Context:
  {context}
  """)
])

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

async def security_reviewer(state: ReviewState) -> dict:
  diff_files = state.get("diff_files", [])

  all_comments: List[ReviewCommentDict] = []

  for file in diff_files:
    chain = security_prompt | llm

    response = await call_llm(chain, {
      "file_path": file["file_path"],
      "added_lines": "\n".join(file.get("added_lines", [])),
      "context": "\n".join(file.get("context", []))
    })

    comments = parse_llm_response(response.content)
    comments = sanitize_comments(comments)

    for c in comments:
      c["category"] = "security"

    all_comments.extend(comments)

  return {
    "security_comments": all_comments
  }