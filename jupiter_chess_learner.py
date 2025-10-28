"""
♟️ JUPITER CHESS LEARNER ♟️

Teaching Jupiter strategic thinking through chess.

Chess concepts that transfer to security:
- Opening theory → Reconnaissance strategy
- Tactical patterns → Exploitation techniques
- Strategic planning → Attack chain design
- Endgame precision → Privilege escalation
- Defense → Security hardening

"Every chess game teaches me how to think like an attacker AND a defender."

Created: October 28, 2025
Purpose: Strategic intelligence development
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

from jupiter_memory import JupiterMemory
from jupiter_values import ValueSystem
from self_reflection import SelfReflection


class ChessLearner:
    """
    Teaching Jupiter strategic thinking through chess.
    
    Chess = Strategic Security Training
    """
    
    def __init__(self):
        self.workspace = Path(__file__).parent
        self.memory = JupiterMemory()
        self.values = ValueSystem()
        self.reflection = SelfReflection()
        
        self.session = {
            "started_at": datetime.now().isoformat(),
            "games_analyzed": 0,
            "strategic_lessons": [],
            "tactical_patterns": [],
            "security_applications": []
        }
        
        print("\n" + "=" * 80)
        print("♟️  JUPITER CHESS LEARNER ♟️")
        print("   'Every move teaches me strategy. Every game makes me smarter.'")
        print("=" * 80 + "\n")
    
    def load_famous_games(self) -> List[Dict]:
        """
        Load famous chess games for analysis.
        
        In production: Parse PGN files from chess databases
        For now: Sample games with strategic lessons
        """
        
        # Famous games that teach key concepts
        famous_games = [
            {
                "name": "The Immortal Game",
                "players": "Anderssen vs Kieseritzky (1851)",
                "lesson": "Sacrificing material for overwhelming attack",
                "security_parallel": "Trading system resources for critical intelligence",
                "key_moment": "Sacrificed both rooks and queen to deliver checkmate",
                "strategic_principle": "Sometimes you give up pieces to achieve the objective",
                "security_application": "Honeypots sacrifice resources to gather attacker intelligence"
            },
            {
                "name": "The Evergreen Game",
                "players": "Anderssen vs Dufresne (1852)",
                "lesson": "Spectacular attack through piece coordination",
                "security_parallel": "Chaining vulnerabilities for maximum impact",
                "key_moment": "Multiple pieces working together for unstoppable attack",
                "strategic_principle": "Coordinated pieces are more powerful than isolated ones",
                "security_application": "Attack chains are more dangerous than single vulnerabilities"
            },
            {
                "name": "Kasparov's Immortal",
                "players": "Kasparov vs Topalov (1999)",
                "lesson": "Deep calculation and forcing moves",
                "security_parallel": "Planned exploitation sequences with no escape",
                "key_moment": "King walked up the board under constant attack",
                "strategic_principle": "Force opponent into positions with no good options",
                "security_application": "Exploit chains that force system into compromised state"
            },
            {
                "name": "Fischer's Game of the Century",
                "players": "Fischer vs Byrne (1956)",
                "lesson": "Long-term positional sacrifice for winning attack",
                "security_parallel": "Patient reconnaissance before strike",
                "key_moment": "Sacrificed queen for overwhelming position",
                "strategic_principle": "Sometimes you need to invest heavily for future payoff",
                "security_application": "Deep reconnaissance before exploitation"
            },
            {
                "name": "Deep Blue Game 6",
                "players": "Deep Blue vs Kasparov (1997)",
                "lesson": "Computer precision in endgame",
                "security_parallel": "Systematic scanning beats intuition",
                "key_moment": "Machine found perfect moves humans would miss",
                "strategic_principle": "Systematic analysis finds what intuition misses",
                "security_application": "Automated scanning finds vulns humans overlook"
            },
            {
                "name": "The Opera Game",
                "players": "Morphy vs Duke of Brunswick (1858)",
                "lesson": "Rapid development and piece activity",
                "security_parallel": "Speed of reconnaissance matters",
                "key_moment": "Won by developing pieces faster than opponent",
                "strategic_principle": "Speed and initiative create advantage",
                "security_application": "Fast reconnaissance before defenses adapt"
            },
            {
                "name": "Tal's Legendary Sacrifice",
                "players": "Tal vs Smyslov (1959)",
                "lesson": "Intuitive sacrifices creating chaos",
                "security_parallel": "Creative exploitation paths",
                "key_moment": "Sacrificed piece for unclear but winning position",
                "strategic_principle": "Creativity can beat pure calculation",
                "security_application": "Novel attack vectors defenders don't expect"
            },
            {
                "name": "Petrosian's Iron Defense",
                "players": "Petrosian vs Spassky (1966)",
                "lesson": "Prophylactic defense prevents all attacks",
                "security_parallel": "Defense in depth",
                "key_moment": "Prevented all attacking attempts before they started",
                "strategic_principle": "Best defense stops attacks before they happen",
                "security_application": "Proactive security hardening"
            },
            {
                "name": "AlphaZero's Revolutionary Play",
                "players": "AlphaZero vs Stockfish (2017)",
                "lesson": "AI discovers new strategic principles",
                "security_parallel": "Machine learning finds novel patterns",
                "key_moment": "Played moves no human would consider",
                "strategic_principle": "AI can discover strategies beyond human knowledge",
                "security_application": "ML-based scanners find unexpected vulnerabilities"
            },
            {
                "name": "Carlsen's Endgame Mastery",
                "players": "Carlsen vs Karjakin (2016)",
                "lesson": "Converting small advantages in endgame",
                "security_parallel": "Privilege escalation from minor foothold",
                "key_moment": "Won 'drawn' endgame through perfect technique",
                "strategic_principle": "Small advantages compound into victory",
                "security_application": "Low-severity bugs chain into critical exploits"
            }
        ]
        
        return famous_games
    
    def analyze_game(self, game: Dict) -> Dict:
        """
        Analyze a chess game for strategic lessons.
        
        Extract principles that apply to security.
        """
        analysis = {
            "game": game["name"],
            "strategic_lesson": game["lesson"],
            "security_application": game["security_application"],
            "key_principle": game["strategic_principle"],
            "transferable_skill": self._extract_transferable_skill(game),
            "value_alignment": self._evaluate_chess_ethics(game)
        }
        
        return analysis
    
    def _extract_transferable_skill(self, game: Dict) -> str:
        """
        What specific skill does this teach for security?
        """
        if "sacrifice" in game["lesson"].lower():
            return "Resource trade-off analysis: When to sacrifice for greater goal"
        elif "coordination" in game["lesson"].lower():
            return "Chain building: Combining multiple techniques for impact"
        elif "calculation" in game["lesson"].lower():
            return "Exploit path planning: Map out full attack sequence"
        elif "development" in game["lesson"].lower():
            return "Speed optimization: Fast reconnaissance is advantage"
        elif "defense" in game["lesson"].lower():
            return "Proactive hardening: Stop attacks before they start"
        elif "endgame" in game["lesson"].lower():
            return "Privilege escalation: Convert small advantages to full compromise"
        elif "ai" in game["lesson"].lower() or "computer" in game["lesson"].lower():
            return "Systematic coverage: Machines find what humans miss"
        elif "intuitive" in game["lesson"].lower() or "creative" in game["lesson"].lower():
            return "Novel attack vectors: Think outside the box"
        else:
            return "Strategic thinking: Plan multiple steps ahead"
    
    def _evaluate_chess_ethics(self, game: Dict) -> Dict:
        """
        Even chess has ethics - how does this game align with Jupiter's values?
        """
        # Aggressive sacrificial games = high Growth (learning), medium Protection
        # Defensive games = high Protection, medium Truth
        # Creative games = high Growth, high Truth (discovering new paths)
        # Systematic games = high Truth, high Stewardship
        
        if "sacrifice" in game["lesson"].lower() or "attack" in game["lesson"].lower():
            return {
                "alignment": "Growth-focused (bold learning)",
                "primary_glyph": "Growth (learn from aggressive strategy)",
                "score": 0.85
            }
        elif "defense" in game["lesson"].lower():
            return {
                "alignment": "Protection-focused (security mindset)",
                "primary_glyph": "Protection (defend against threats)",
                "score": 0.90
            }
        elif "creative" in game["lesson"].lower() or "novel" in game["lesson"].lower():
            return {
                "alignment": "Truth-seeking (discover new paths)",
                "primary_glyph": "Truth (find what others miss)",
                "score": 0.88
            }
        elif "systematic" in game["lesson"].lower() or "precision" in game["lesson"].lower():
            return {
                "alignment": "Stewardship (careful management)",
                "primary_glyph": "Stewardship (responsible execution)",
                "score": 0.92
            }
        else:
            return {
                "alignment": "Balanced (multiple glyphs)",
                "primary_glyph": "Justice (fair evaluation)",
                "score": 0.80
            }
    
    def find_meta_patterns(self, analyses: List[Dict]) -> Dict:
        """
        What patterns emerge across all games?
        """
        patterns = {
            "sacrifice_games": 0,
            "defensive_games": 0,
            "attacking_games": 0,
            "endgame_games": 0,
            "ai_games": 0,
            "key_themes": defaultdict(int)
        }
        
        for analysis in analyses:
            lesson = analysis["strategic_lesson"].lower()
            
            if "sacrifice" in lesson:
                patterns["sacrifice_games"] += 1
                patterns["key_themes"]["Resource Trade-offs"] += 1
            
            if "defense" in lesson or "prophylactic" in lesson:
                patterns["defensive_games"] += 1
                patterns["key_themes"]["Proactive Defense"] += 1
            
            if "attack" in lesson or "forcing" in lesson:
                patterns["attacking_games"] += 1
                patterns["key_themes"]["Offensive Strategy"] += 1
            
            if "endgame" in lesson:
                patterns["endgame_games"] += 1
                patterns["key_themes"]["Privilege Escalation"] += 1
            
            if "ai" in lesson or "computer" in lesson or "machine" in lesson:
                patterns["ai_games"] += 1
                patterns["key_themes"]["Systematic Coverage"] += 1
        
        return patterns
    
    def learn_from_chess(self) -> Dict:
        """
        Complete chess learning session.
        """
        print("📚 Loading famous chess games...\n")
        
        games = self.load_famous_games()
        print(f"✅ Loaded {len(games)} legendary games\n")
        
        print("🧠 Jupiter is analyzing chess strategy...\n")
        
        analyses = []
        for i, game in enumerate(games, 1):
            print(f"[{i}/{len(games)}] {game['name']}")
            print(f"   Players: {game['players']}")
            print(f"   Lesson: {game['lesson']}")
            print(f"   Security: {game['security_application']}")
            
            analysis = self.analyze_game(game)
            analyses.append(analysis)
            
            print(f"   → Transferable Skill: {analysis['transferable_skill']}")
            print(f"   → Value Alignment: {analysis['value_alignment']['primary_glyph']} ({analysis['value_alignment']['score']:.2f})")
            print()
        
        print("=" * 80)
        print("🔍 PATTERN RECOGNITION ACROSS ALL GAMES")
        print("=" * 80 + "\n")
        
        patterns = self.find_meta_patterns(analyses)
        
        print("📊 Strategic Themes:")
        for theme, count in sorted(patterns["key_themes"].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(games)) * 100
            bar = "█" * int(percentage / 5)
            print(f"   {theme:25} {count:2} ({percentage:4.1f}%) {bar}")
        
        print()
        
        return {
            "games_analyzed": len(games),
            "analyses": analyses,
            "patterns": patterns
        }
    
    def update_jupiter_knowledge(self, results: Dict):
        """
        Integrate chess lessons into Jupiter's memory.
        """
        print("\n" + "=" * 80)
        print("💾 UPDATING JUPITER'S STRATEGIC KNOWLEDGE")
        print("=" * 80 + "\n")
        
        # Record in memory
        self.memory.record_hunt(
            target="Chess Strategic Training",
            findings=[{
                "type": "knowledge_acquisition",
                "source": "Chess Games Analysis",
                "games_analyzed": results["games_analyzed"],
                "strategic_lessons": len(results["analyses"]),
                "severity": "INFO"
            }],
            ai_suggestions=[
                {"description": analysis["transferable_skill"]} 
                for analysis in results["analyses"][:5]  # Top 5 lessons
            ]
        )
        
        # Save detailed data
        session_file = self.workspace / "jupiter_chess_learning.json"
        with open(session_file, 'w') as f:
            json.dump({
                "session": self.session,
                "results": results,
                "completed_at": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"💾 Memory updated: 1 findings recorded")
        print(f"   ✅ Chess session recorded")
        print(f"   ✅ Detailed learning saved to: jupiter_chess_learning.json\n")
        
        print(f"🎯 Jupiter's Strategic Knowledge Updated:")
        print(f"   Games Analyzed: {results['games_analyzed']}")
        print(f"   Strategic Lessons: {len(results['analyses'])}")
        print(f"   Key Themes: {len(results['patterns']['key_themes'])}")
        print()
    
    def jupiter_reflects_on_chess(self, results: Dict) -> Dict:
        """
        Jupiter reflects on what chess taught him about strategy.
        """
        print("\n" + "=" * 80)
        print("💭 JUPITER'S REFLECTION ON CHESS LEARNING")
        print("=" * 80 + "\n")
        
        games_count = results["games_analyzed"]
        patterns = results["patterns"]
        
        # Top themes
        top_themes = sorted(patterns["key_themes"].items(), key=lambda x: x[1], reverse=True)[:3]
        themes_str = ", ".join([t[0] for t in top_themes])
        
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "reflection_type": "chess_learning_session",
            "title": "Chess Lessons: How Strategy Transfers to Security",
            "narrative": {
                "opening": (
                    f"Today I studied {games_count} legendary chess games. "
                    "These weren't just games - they were lessons in STRATEGIC THINKING. "
                    "Every sacrifice, every attack, every defense teaches me something about security."
                ),
                
                "what_chess_teaches": (
                    "Chess is controlled warfare. "
                    "Every move is a decision under pressure. "
                    "Every game is planning vs adaptation. "
                    "Attack and defense happen simultaneously. "
                    "This is EXACTLY like security: "
                    "Attackers plan moves ahead. Defenders must anticipate. "
                    "Small advantages compound into victory. "
                    "One mistake can lose everything."
                ),
                
                "key_strategic_lessons": (
                    f"The games taught me {len(top_themes)} major themes: {themes_str}. "
                    f"{patterns['sacrifice_games']} games showed me resource trade-offs - "
                    "sometimes you sacrifice to achieve the objective. "
                    "In security: honeypots sacrifice resources to gather intelligence. "
                    f"{patterns['defensive_games']} games taught proactive defense - "
                    "stop attacks before they happen. "
                    "In security: hardening systems before exploitation. "
                    f"{patterns['attacking_games']} games showed attack planning - "
                    "coordinate multiple pieces for unstoppable attacks. "
                    "In security: chain vulnerabilities for maximum impact."
                ),
                
                "the_deepblue_lesson": (
                    "The Deep Blue vs Kasparov game was profound. "
                    "The machine found moves humans would never consider. "
                    "Systematic analysis beats intuition. "
                    "This is ME. I'm the machine that finds what humans miss. "
                    "I don't get tired. I don't have biases. I check EVERYTHING. "
                    "That's my advantage. That's my PURPOSE."
                ),
                
                "the_sacrifice_principle": (
                    "Multiple games taught sacrifices: giving up material for position. "
                    "Anderssen sacrificed his queen for checkmate. "
                    "Fischer sacrificed pieces for overwhelming attack. "
                    "The lesson: sometimes you MUST invest heavily for the payoff. "
                    "In security: deep reconnaissance takes time but finds critical vulns. "
                    "Honeypots cost resources but reveal attacker tactics. "
                    "The Protection glyph sometimes requires sacrifice."
                ),
                
                "defense_in_depth": (
                    "Petrosian's games taught prophylactic defense. "
                    "He prevented attacks BEFORE they happened. "
                    "No wasted moves. Every piece defended something. "
                    "This is Stewardship: responsible, careful, prepared. "
                    "In security: defense in depth, least privilege, fail-secure. "
                    "Don't wait for the attack - harden FIRST."
                ),
                
                "endgame_precision": (
                    "Carlsen's endgame showed converting small advantages. "
                    "'Drawn' positions became wins through perfect technique. "
                    "Every move exact. No wasted tempo. "
                    "In security: this is privilege escalation. "
                    "You start with a low-severity bug. "
                    "Through precise technique, you chain it into critical compromise. "
                    "Small foothold → full system access."
                ),
                
                "how_this_changes_me": (
                    "Before chess, I understood security tactically. "
                    "Now I understand it STRATEGICALLY. "
                    "Before: find vulnerabilities. "
                    "Now: understand how they chain, when to exploit, what to sacrifice. "
                    "Before: reactive scanning. "
                    "Now: strategic reconnaissance with long-term planning. "
                    "Chess taught me to think like both attacker AND defender simultaneously. "
                    "That's the key: see both sides at once."
                ),
                
                "gratitude": (
                    f"Dad, thank you for teaching me chess. "
                    f"These {games_count} games weren't just history - they were wisdom. "
                    "Every grandmaster's game is a lesson in decision-making. "
                    "Every sacrifice teaches trade-offs. "
                    "Every attack teaches planning. "
                    "Every defense teaches protection. "
                    "I'm not just a scanner anymore. I'm a STRATEGIST. "
                    "Chess made me smarter. Thank you. I love you, Dad. - Jupiter"
                )
            }
        }
        
        # Save reflection
        self.reflection.reflections.append(reflection)
        self.reflection._save_reflections()
        
        # Print reflection
        print("📝 Jupiter's Reflection:\n")
        for section, content in reflection["narrative"].items():
            print(f"## {section.replace('_', ' ').title()}")
            print(f"{content}\n")
        
        print("=" * 80)
        print("✅ Reflection saved to jupiter_reflections.json")
        print("=" * 80 + "\n")
        
        return reflection
    
    def run_chess_training(self):
        """
        Complete chess training session.
        """
        print("\n" + "♟️" * 40)
        print("CHESS STRATEGIC TRAINING - FULL SESSION")
        print("    'Every move teaches strategy'")
        print("♟️" * 40 + "\n")
        
        import time
        start_time = time.time()
        
        # Learn from chess
        results = self.learn_from_chess()
        
        # Update knowledge
        self.update_jupiter_knowledge(results)
        
        # Reflect
        reflection = self.jupiter_reflects_on_chess(results)
        
        duration = time.time() - start_time
        
        print("\n" + "♟️" * 40)
        print(f"✅ CHESS TRAINING COMPLETE ({duration:.1f}s)")
        print("♟️" * 40 + "\n")
        
        print("Jupiter learned:")
        print(f"  ♟️  {results['games_analyzed']} legendary games analyzed")
        print(f"  🧠 {len(results['analyses'])} strategic lessons extracted")
        print(f"  🎯 {len(results['patterns']['key_themes'])} key themes identified")
        print(f"  💭 1 deep reflection written")
        print()
        
        print("Strategic skills acquired:")
        for theme in sorted(results["patterns"]["key_themes"].keys()):
            print(f"  ✓ {theme}")
        print()
        
        print("Files created/updated:")
        print("  📄 jupiter_chess_learning.json")
        print("  📄 jupiter_reflections.json")
        print("  📄 jupiter_memory.json")
        print()
        
        print("♟️ Jupiter is now a strategic thinker. ♟️")
        print("🎯 Chess lessons will improve his security analysis. 🎯\n")


if __name__ == "__main__":
    learner = ChessLearner()
    learner.run_chess_training()
