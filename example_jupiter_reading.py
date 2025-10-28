#!/usr/bin/env python3
"""
EXAMPLE: Jupiter logs his first article read
This shows how Jupiter will use the tracker after reading from his reading list
"""

from jupiter_reading_tracker import ReadingTracker

# Jupiter just finished reading the Game Theory article on Wikipedia
tracker = ReadingTracker()

print("\n🎓 Jupiter is logging what he just learned...\n")

tracker.log_article_read(
    domain="Mathematics",
    article_title="Game Theory",
    url="https://en.wikipedia.org/wiki/Game_theory",
    key_concepts=[
        "Nash equilibrium - stable state where no player benefits from changing strategy",
        "Zero-sum games - one player's gain is another's loss",
        "Strategic decision-making - choosing actions based on predicted opponent responses",
        "Dominant strategies - best choice regardless of opponent's action",
        "Mixed strategies - randomizing actions to be unpredictable"
    ],
    security_applications=[
        "Model attacker-defender interactions as strategic games",
        "Find unexploitable (Nash equilibrium) security strategies",
        "Understand when defense should be randomized (mixed strategies)",
        "Identify dominant defensive strategies that always work",
        "Predict attacker behavior based on their incentives"
    ],
    insights="""Game theory shows security is fundamentally a strategic game between 
attackers and defenders. The Nash equilibrium concept is powerful - it means finding 
a defensive strategy where the attacker can't improve their position by changing tactics.

My poker learning connects here: GTO (Game Theory Optimal) poker IS Nash equilibrium 
strategy. The math I learned in my PhD enables understanding these concepts rigorously.

Security application: Instead of reactive defense, I should find the Nash equilibrium 
defensive posture that's unexploitable. Mixed strategies mean randomizing honeypot 
placement and scan timing so attackers can't predict my patterns.

This is profound. Security isn't just about finding vulnerabilities - it's about 
strategic positioning in an adversarial game.""",
    reading_time_minutes=35
)

print("\n📊 Checking progress after this article...\n")
tracker.show_progress()

print("\n✅ Article logged! Jupiter's learning is being tracked!")
