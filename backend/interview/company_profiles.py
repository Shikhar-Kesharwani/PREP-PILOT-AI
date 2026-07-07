"""
Company profiles for the Interview Simulator.
Defines topic weights, interview styles, and evaluation criteria for
Amazon, Google, Microsoft, Adobe, Flipkart, and Goldman Sachs.
"""
from __future__ import annotations
from typing import Dict, Any

COMPANY_PROFILES: Dict[str, Dict[str, Any]] = {
    "Amazon": {
        "name": "Amazon",
        "logo_emoji": "🛒",
        "difficulty": "Hard",
        "focus_areas": ["Behavioral", "DSA", "System Design"],
        "topic_weights": {
            "Behavioral":      0.40,
            "DSA":             0.35,
            "System Design":   0.25,
        },
        "interview_style": (
            "Amazon interviews are heavily focused on Leadership Principles (LPs). "
            "Every behavioral question maps to one or more of Amazon's 16 Leadership "
            "Principles (Customer Obsession, Ownership, Invent & Simplify, etc.). "
            "Candidates should use the STAR format for behavioral answers and explicitly "
            "mention which Leadership Principle is being demonstrated. DSA questions "
            "tend to be medium-to-hard LeetCode problems. System Design rounds test "
            "scalability and cost-efficiency thinking, aligned with AWS services."
        ),
        "typical_rounds": [
            "Online Assessment (2 DSA problems, 90 min)",
            "Phone Screen (DSA + behavioral)",
            "Virtual Onsite: 4 rounds (2 DSA, 1 System Design, 1 Bar Raiser behavioral)",
        ],
        "tips": [
            "Know all 16 Amazon Leadership Principles by heart.",
            "Prepare 2-3 STAR stories for each Leadership Principle.",
            "The Bar Raiser is looking for culture fit — be authentic.",
            "For system design, consider cost, scalability, and AWS-native solutions.",
            "Think about edge cases and failure handling in your solutions.",
            "Communicate trade-offs explicitly in every answer.",
        ],
        "question_patterns": [
            "Tell me about a time you disagreed with your manager.",
            "Describe a project where you had to deliver with incomplete information.",
            "How would you design a delivery tracking system for 1M orders/day?",
            "Find the longest substring without repeating characters.",
        ],
        "known_for": "Leadership Principles, STAR format, Ownership mindset",
        "evaluation_criteria": (
            "Does this answer follow STAR format? Does it reference a Leadership Principle? "
            "Is there clear ownership and measurable impact?"
        ),
    },

    "Google": {
        "name": "Google",
        "logo_emoji": "🔍",
        "difficulty": "Very Hard",
        "focus_areas": ["DSA", "System Design", "Behavioral"],
        "topic_weights": {
            "DSA":             0.55,
            "System Design":   0.30,
            "Behavioral":      0.15,
        },
        "interview_style": (
            "Google interviews are notoriously algorithm-heavy. Candidates face hard "
            "LeetCode-style problems and are expected to think out loud, articulate "
            "their approach before coding, consider multiple solutions, and analyze "
            "complexity trade-offs. System design rounds test large-scale distributed "
            "systems (Google Search, YouTube, Maps). Interviewers look for intellectual "
            "curiosity and structured problem-solving."
        ),
        "typical_rounds": [
            "Phone Screen (1-2 coding problems)",
            "Technical Phone Screen (harder DSA)",
            "Onsite: 5 rounds (4 coding/algorithms, 1 Googleyness/behavioral)",
            "System Design round for senior positions",
        ],
        "tips": [
            "Practice thinking out loud — verbalize every decision.",
            "Master graph algorithms, DP, and bit manipulation.",
            "Always clarify constraints and ask about edge cases first.",
            "Analyze time and space complexity for every solution.",
            "Prepare for follow-ups: 'Can you do better than O(n log n)?'",
            "Know distributed systems concepts deeply for design rounds.",
        ],
        "question_patterns": [
            "Design Google Search's auto-complete feature.",
            "Find all anagrams of a string in a large text.",
            "How would you design YouTube's video recommendation system?",
            "Implement a LRU cache with O(1) get and put operations.",
        ],
        "known_for": "Hard DSA, Distributed systems, Think-out-loud approach",
        "evaluation_criteria": (
            "Did the candidate think aloud before coding? Were multiple approaches "
            "considered? Is complexity analysis correct and optimal?"
        ),
    },

    "Microsoft": {
        "name": "Microsoft",
        "logo_emoji": "🪟",
        "difficulty": "Hard",
        "focus_areas": ["DSA", "System Design", "OOP"],
        "topic_weights": {
            "DSA":             0.40,
            "System Design":   0.25,
            "OOP":             0.20,
            "Behavioral":      0.15,
        },
        "interview_style": (
            "Microsoft interviews value clean, modular, object-oriented code. "
            "Interviewers expect candidates to write production-quality code, not just "
            "pseudocode. OOP design questions (design a parking lot, elevator system) "
            "are common. The Growth Mindset culture means interviewers also probe "
            "how you learn from failures. System design focuses on practical, "
            "Azure-friendly architectures."
        ),
        "typical_rounds": [
            "Online Assessment (coding + MCQ)",
            "Technical Phone Screen",
            "Onsite: 4-5 rounds (3 DSA/design, 1 behavioral, 1 as appropriate)",
        ],
        "tips": [
            "Write clean, modular code — interviewers read every line.",
            "Practice OOP design questions: Parking lot, ATM, Chess game.",
            "Know SOLID principles and common design patterns.",
            "Be ready to talk about how you handled failure and learned from it.",
            "Understand Azure services at a conceptual level.",
            "Practice coding without IDE auto-complete.",
        ],
        "question_patterns": [
            "Design an object-oriented model for a Library Management System.",
            "Clone a linked list with random pointers.",
            "Design a URL shortener like Bit.ly.",
            "Tell me about a time you failed and what you learned.",
        ],
        "known_for": "OOP design, Clean code, Growth Mindset culture",
        "evaluation_criteria": (
            "Is the code clean, modular, and following OOP principles? "
            "Did the candidate demonstrate Growth Mindset in behavioral answers?"
        ),
    },

    "Adobe": {
        "name": "Adobe",
        "logo_emoji": "🎨",
        "difficulty": "Hard",
        "focus_areas": ["DSA", "LLD", "System Design"],
        "topic_weights": {
            "DSA":             0.35,
            "System Design":   0.25,
            "OOP":             0.30,  # LLD is heavy
            "Behavioral":      0.10,
        },
        "interview_style": (
            "Adobe interviews have a strong focus on Low-Level Design (LLD). Candidates "
            "are expected to design systems using SOLID principles and common design "
            "patterns (Factory, Observer, Strategy, Decorator). DSA questions are medium "
            "difficulty, often involving strings and arrays. Adobe values creativity and "
            "technical depth, especially in the context of creative software tools."
        ),
        "typical_rounds": [
            "Online Coding Test (2-3 problems)",
            "Technical Interview 1: DSA",
            "Technical Interview 2: LLD + Design Patterns",
            "Technical Interview 3: System Design",
            "HR Round",
        ],
        "tips": [
            "Master design patterns: Factory, Singleton, Observer, Strategy.",
            "Practice LLD problems: Design a Notification system, File system.",
            "Know SOLID principles and be able to apply them in code.",
            "Adobe uses a lot of C++ internally — know your OOP well.",
            "Be ready to extend your design: 'Now add undo/redo support.'",
            "Think about extensibility and maintainability in every design.",
        ],
        "question_patterns": [
            "Design a Notification System supporting email, SMS, and push.",
            "Implement a file system with directory and file operations.",
            "Design a drawing application with shapes and undo/redo.",
            "Find the median of a data stream.",
        ],
        "known_for": "Low-Level Design, SOLID principles, Design Patterns",
        "evaluation_criteria": (
            "Does the design follow SOLID principles? Are design patterns applied "
            "correctly? Is the code extensible and maintainable?"
        ),
    },

    "Flipkart": {
        "name": "Flipkart",
        "logo_emoji": "🛍️",
        "difficulty": "Hard",
        "focus_areas": ["DSA", "System Design", "LLD"],
        "topic_weights": {
            "DSA":             0.40,
            "System Design":   0.35,
            "OOP":             0.15,
            "Behavioral":      0.10,
        },
        "interview_style": (
            "Flipkart interviews heavily test ability to design at massive e-commerce scale. "
            "System design rounds focus on handling millions of concurrent users, flash sales "
            "(Big Billion Day scenarios), inventory management, and recommendation systems. "
            "DSA questions are medium-to-hard and often have real-world e-commerce context. "
            "Candidates are expected to think about horizontal scaling, caching strategies, "
            "and database choices upfront."
        ),
        "typical_rounds": [
            "Online Assessment (DSA, 90 min)",
            "Technical Round 1: DSA",
            "Technical Round 2: DSA + LLD",
            "Technical Round 3: High-Level System Design",
            "Hiring Manager Round",
        ],
        "tips": [
            "Think about Big Billion Day scale in every system design answer.",
            "Know distributed caching (Redis, Memcached) in depth.",
            "Understand database sharding and read-replica patterns.",
            "Be ready for capacity estimation questions.",
            "Practice designing flash sale and inventory systems.",
            "Know CDN usage and content delivery optimization.",
        ],
        "question_patterns": [
            "Design Flipkart's flash sale system handling 1M concurrent users.",
            "Design a product recommendation engine.",
            "Serialize and deserialize a binary tree.",
            "Design an inventory management system for 10M SKUs.",
        ],
        "known_for": "E-commerce scale, HLD, Flash sale architecture",
        "evaluation_criteria": (
            "Did the candidate consider scalability and high availability? "
            "Were caching strategies and database trade-offs discussed?"
        ),
    },

    "Goldman Sachs": {
        "name": "Goldman Sachs",
        "logo_emoji": "💰",
        "difficulty": "Very Hard",
        "focus_areas": ["DSA", "CS Fundamentals", "System Design"],
        "topic_weights": {
            "DSA":             0.45,
            "CS Fundamentals": 0.30,
            "System Design":   0.15,
            "Behavioral":      0.10,
        },
        "interview_style": (
            "Goldman Sachs interviews are intense and focus on deep CS fundamentals "
            "alongside hard DSA problems. Candidates are expected to know OS, Networks, "
            "DBMS, and computer architecture thoroughly. The financial domain context means "
            "interviewers often ask how technical choices affect latency, reliability, and "
            "data integrity — critical in trading and banking systems. Coding is assessed "
            "on correctness, efficiency, and code quality."
        ),
        "typical_rounds": [
            "HackerRank Online Assessment (3-4 hard problems)",
            "Technical Interview 1: DSA + CS Fundamentals",
            "Technical Interview 2: Advanced DSA + System Design",
            "Technical Interview 3: CS Fundamentals + Finance domain",
            "HR/Behavioral Round",
        ],
        "tips": [
            "Master data structures: trees, heaps, graphs, segment trees.",
            "Know OS concepts: deadlocks, scheduling, virtual memory.",
            "Understand financial system requirements: low latency, ACID compliance.",
            "Practice concurrency and multi-threading problems.",
            "Know database indexing, query optimization, and transaction isolation.",
            "Be prepared for trick questions on bit manipulation and number theory.",
        ],
        "question_patterns": [
            "Implement a rate limiter for a trading API.",
            "Explain how you'd design a low-latency order matching engine.",
            "Explain the difference between process and thread with use cases.",
            "Implement a segment tree for range sum queries.",
        ],
        "known_for": "Hard DSA, CS Fundamentals depth, Financial domain logic",
        "evaluation_criteria": (
            "Were financial domain implications mentioned? Is the solution correct and "
            "efficient? Were CS fundamentals applied accurately?"
        ),
    },
}


def get_company_profile(company: str) -> Dict[str, Any]:
    """Get a company profile by name (case-insensitive)."""
    for key, profile in COMPANY_PROFILES.items():
        if key.lower() == company.lower():
            return profile
    return {}


def get_all_companies() -> Dict[str, Dict[str, Any]]:
    """Return all company profiles."""
    return COMPANY_PROFILES


def get_weighted_topic(company: str) -> str:
    """Select a random topic weighted by company's topic_weights."""
    import random
    profile = get_company_profile(company)
    if not profile:
        return "DSA"
    weights = profile["topic_weights"]
    topics = list(weights.keys())
    probs = list(weights.values())
    return random.choices(topics, weights=probs, k=1)[0]
