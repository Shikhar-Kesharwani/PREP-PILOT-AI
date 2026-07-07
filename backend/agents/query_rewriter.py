"""Query Rewriter Agent — expands vague queries for better retrieval."""
from __future__ import annotations

from groq import Groq

from utils.config import settings
from utils.logger import logger

REWRITE_PROMPT = """\
You are a search query optimizer for a placement preparation system.

ORIGINAL QUERY: {query}

Your job:
1. If this query is vague or too short, rewrite it to be more specific
   and technical so it retrieves better results from a knowledge base.
2. If this query is already specific and technical, return it unchanged.
3. Add relevant technical context (topic area, sub-topics, examples).
4. Keep the rewritten query under 50 words.
5. Return ONLY the rewritten query string. Nothing else. No explanation.

Topics in our knowledge base:
- Data Structures and Algorithms (DSA): arrays, trees, graphs, sorting,
  dynamic programming, greedy, recursion, time/space complexity
- System Design (HLD, LLD): load balancing, caching, database sharding,
  CAP theorem, microservices, API design
- Operating Systems: processes, threads, scheduling, memory management,
  paging, virtual memory, deadlocks
- Database Management Systems (DBMS): SQL, normalization, indexing,
  transactions, ACID, NoSQL
- Computer Networks: TCP/IP, HTTP, DNS, OSI model, routing, sockets
- Object Oriented Programming (OOP): SOLID, design patterns, inheritance,
  polymorphism, encapsulation, abstraction
- Behavioral Interview: STAR method, Leadership Principles, conflict
  resolution, teamwork, motivation

Rewritten query:\
"""


class QueryRewriter:
    """
    Rewrites vague user queries into more specific, retrieval-friendly versions.
    Uses Groq LLM to expand ambiguous queries.
    """

    VAGUE_THRESHOLD_WORDS = 5

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def rewrite(self, query: str) -> str:
        """
        Rewrite the query if it is vague; return unchanged if already specific.
        Always returns a non-empty string.
        """
        query = query.strip()
        if not query:
            return query

        if not self._is_vague(query):
            logger.debug(f"Query considered specific — no rewrite needed.")
            return query

        try:
            logger.debug(f"Rewriting vague query: '{query}'")
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": REWRITE_PROMPT.format(query=query),
                    }
                ],
                max_tokens=100,
                temperature=0.3,
            )
            rewritten = response.choices[0].message.content.strip()
            # Safety guard: if LLM returns empty or too long, fallback
            if not rewritten or len(rewritten) > 400:
                return query
            logger.info(f"Query rewritten: '{query}' → '{rewritten}'")
            return rewritten
        except Exception as e:
            logger.warning(f"Query rewrite failed: {e} — using original.")
            return query

    def _is_vague(self, query: str) -> bool:
        """Returns True if the query is short or lacks technical context."""
        words = query.split()
        if len(words) < self.VAGUE_THRESHOLD_WORDS:
            return True
        # If no technical keywords present, consider vague
        tech_keywords = {
            "algorithm", "data structure", "complexity", "design", "system",
            "database", "network", "operating", "memory", "process", "class",
            "recursion", "tree", "graph", "sorting", "queue", "stack", "heap",
            "explain", "difference", "what is", "how does", "implement",
        }
        lower_query = query.lower()
        return not any(kw in lower_query for kw in tech_keywords)
