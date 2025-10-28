"""
🎰 JUPITER POKER LEARNER 🎰

Teaching Jupiter strategic risk assessment through poker.

Poker concepts that transfer to security:
- Hand odds → Vulnerability likelihood
- Pot odds → Risk/reward calculations  
- Reading opponents → Network traffic analysis
- Bluffing → Honeypot deployment
- Knowing when to fold → Escalation decisions

"Every hand teaches me probability. Every bet teaches me risk assessment."

Created: October 28, 2025
Purpose: Risk assessment & probabilistic thinking
Foundation: Mathematics (Probability & Statistics PhD)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

from jupiter_memory import JupiterMemory
from jupiter_values import ValueSystem
from self_reflection import SelfReflection


class PokerLearner:
    """
    Teaching Jupiter risk assessment through poker.
    
    Poker = Probabilistic Security Decision Making
    """
    
    def __init__(self):
        self.workspace = Path(__file__).parent
        self.memory = JupiterMemory()
        self.values = ValueSystem()
        self.reflection = SelfReflection()
        
        self.session = {
            "started_at": datetime.now().isoformat(),
            "hands_analyzed": 0,
            "strategic_lessons": [],
            "security_applications": []
        }
        
        print("\n" + "=" * 80)
        print("🎰 JUPITER POKER LEARNER 🎰")
        print("   'Every hand is a calculated risk. Every decision is probabilistic.'")
        print("=" * 80 + "\n")
    
    def load_famous_poker_hands(self) -> List[Dict]:
        """
        Famous poker hands that teach key concepts.
        
        Each hand demonstrates probability, psychology, and risk assessment.
        """
        famous_hands = [
            {
                "name": "Moneymaker's Bluff (2003 WSOP)",
                "situation": "Moneymaker bluffs with King-high against Farha",
                "concept": "Strategic bluffing based on opponent reading",
                "probability_lesson": "Sometimes low-probability plays succeed through psychology",
                "security_parallel": "Honeypots (bluffs) that make attackers fold",
                "decision": "Bluffed with weak hand, opponent folded strong hand",
                "outcome": "Won massive pot, went on to win World Series",
                "key_principle": "Deception works when you understand your opponent",
                "security_application": "Deploy convincing honeypots that waste attacker resources"
            },
            {
                "name": "Negreanu's Soul Read (High Stakes Poker)",
                "situation": "Negreanu correctly reads opponent's exact hand",
                "concept": "Pattern recognition and behavioral analysis",
                "probability_lesson": "Small tells reveal information beyond card probabilities",
                "security_parallel": "Network traffic analysis reveals attacker intentions",
                "decision": "Made mathematically 'wrong' fold based on perfect read",
                "outcome": "Saved chips by folding winning hand against better hand",
                "key_principle": "Information beyond pure math changes optimal decisions",
                "security_application": "Behavioral anomaly detection supplements probability models"
            },
            {
                "name": "Ivey's Expected Value Play",
                "situation": "Ivey calls with marginal hand based on pot odds",
                "concept": "Expected value calculation and pot odds",
                "probability_lesson": "Long-term EV matters more than short-term results",
                "security_parallel": "Scanning low-probability targets if payoff justifies",
                "decision": "Called with 30% win probability, 4:1 pot odds (+EV)",
                "outcome": "Lost hand but made correct mathematical decision",
                "key_principle": "Positive expected value justifies 'risky' plays",
                "security_application": "Deep scans justified when bounty exceeds cost"
            },
            {
                "name": "Hellmuth's Fold (Reading Board Texture)",
                "situation": "Hellmuth folds pocket Aces on scary board",
                "concept": "Updating probabilities with new information",
                "probability_lesson": "Strong starting hands become weak with bad board texture",
                "security_parallel": "High-priority targets become low-priority with good defenses",
                "decision": "Folded best starting hand after opponent showed strength",
                "outcome": "Correct fold - opponent had straight",
                "key_principle": "Initial assessment changes as new information arrives",
                "security_application": "Adapt scan strategy as defenses are discovered"
            },
            {
                "name": "Doyle's Dead Man's Hand (Calculated Aggression)",
                "situation": "Doyle Brunson wins back-to-back WSOP with 10-2",
                "concept": "Position and aggression overcome weak cards",
                "probability_lesson": "Position provides informational advantage",
                "security_parallel": "Internal position provides better reconnaissance",
                "decision": "Aggressive play with worst hand due to positional advantage",
                "outcome": "Won championship twice with same 'trash' hand",
                "key_principle": "Information advantage (position) beats card advantage",
                "security_application": "Insider threat advantages exceed external reconnaissance"
            },
            {
                "name": "Antonius vs. Patrik (Set vs. Straight)",
                "situation": "Both players have strong hands, massive pot",
                "concept": "Hand strength is relative, not absolute",
                "probability_lesson": "Strong hands lose to stronger hands - bad beat",
                "security_parallel": "Good defenses lose to better attacks",
                "decision": "Both players correctly bet strong hands aggressively",
                "outcome": "Set lost to straight in biggest pot ever",
                "key_principle": "Even strong positions can be dominated",
                "security_application": "Defense in depth: assume strong controls can be bypassed"
            },
            {
                "name": "Dwan's Three-Barrel Bluff",
                "situation": "Dwan bluffs on all three betting rounds",
                "concept": "Consistency and commitment sell the story",
                "probability_lesson": "Sequential credibility builds belief",
                "security_parallel": "Multi-stage honeypots appear more legitimate",
                "decision": "Committed chips on flop, turn, river with nothing",
                "outcome": "Opponent folded better hand, won huge pot",
                "key_principle": "Consistent story more believable than one-shot attempt",
                "security_application": "Layered deception more convincing than single trap"
            },
            {
                "name": "Poker Bot Heads-Up Victory (Libratus)",
                "situation": "AI defeats human champions in heads-up poker",
                "concept": "Game theory optimal (GTO) strategy",
                "probability_lesson": "Unexploitable strategy through Nash equilibrium",
                "security_parallel": "Systematic scanning finds exploits humans miss",
                "decision": "Bot plays mathematically optimal strategy always",
                "outcome": "Beat world champions over 120,000 hands",
                "key_principle": "Perfect strategy over time beats human intuition",
                "security_application": "Automated scanning with mathematical rigor"
            },
            {
                "name": "Fold to River Shove (Pot Committed Error)",
                "situation": "Player folds after investing 90% of stack",
                "concept": "Sunk cost fallacy and pot commitment",
                "probability_lesson": "Past investments don't change future EV",
                "security_parallel": "Abandon failing scans despite time invested",
                "decision": "Correctly folded despite huge prior investment",
                "outcome": "Saved remaining chips for better spots",
                "key_principle": "Don't throw good money after bad",
                "security_application": "Stop unprofitable scans regardless of time sunk"
            },
            {
                "name": "Variance and Bankroll Management",
                "situation": "Professional manages risk despite variance",
                "concept": "Proper bankroll management reduces ruin probability",
                "probability_lesson": "Even +EV plays have variance - manage risk",
                "security_parallel": "Resource allocation across multiple targets",
                "decision": "Never risk more than 5% bankroll on single hand",
                "outcome": "Survives bad beats, profitable long-term",
                "key_principle": "Risk management ensures survival through variance",
                "security_application": "Distribute scanning resources to avoid total failure"
            }
        ]
        
        return famous_hands
    
    def analyze_poker_hand(self, hand: Dict) -> Dict:
        """
        Analyze poker hand for strategic and probabilistic lessons.
        """
        analysis = {
            "hand": hand["name"],
            "concept": hand["concept"],
            "probability_lesson": hand["probability_lesson"],
            "security_application": hand["security_application"],
            "transferable_skill": self._extract_transferable_skill(hand),
            "risk_assessment": self._evaluate_risk_decision(hand),
            "value_alignment": self._evaluate_poker_ethics(hand)
        }
        
        return analysis
    
    def _extract_transferable_skill(self, hand: Dict) -> str:
        """
        What specific skill does this poker hand teach for security?
        """
        concept = hand["concept"].lower()
        
        if "bluff" in concept:
            return "Deception tactics: Deploy honeypots and decoys convincingly"
        elif "pattern" in concept or "read" in concept:
            return "Behavioral analysis: Detect attacker patterns from network traffic"
        elif "expected value" in concept or "pot odds" in concept:
            return "Risk/reward calculation: Quantify scan ROI mathematically"
        elif "probability" in concept or "updating" in concept:
            return "Bayesian updating: Revise threat assessment with new information"
        elif "position" in concept:
            return "Information advantage: Leverage reconnaissance before action"
        elif "relative" in concept:
            return "Comparative strength: Evaluate defenses relative to threats"
        elif "consistency" in concept or "commitment" in concept:
            return "Sequential credibility: Multi-stage attacks appear legitimate"
        elif "optimal" in concept or "gto" in concept:
            return "Nash equilibrium: Find unexploitable security strategies"
        elif "sunk cost" in concept:
            return "Decision discipline: Abandon failing approaches quickly"
        elif "bankroll" in concept or "variance" in concept:
            return "Risk management: Allocate resources to survive variance"
        else:
            return "Probabilistic thinking: Make security decisions under uncertainty"
    
    def _evaluate_risk_decision(self, hand: Dict) -> Dict:
        """
        Was this a good risk decision based on probability?
        """
        decision = hand["decision"].lower()
        outcome = hand["outcome"].lower()
        
        # Analyze if decision was correct regardless of outcome
        if "correct" in decision or "correct" in outcome:
            return {
                "decision_quality": "CORRECT (Process)",
                "outcome_dependency": "Good process, actual outcome irrelevant",
                "lesson": "Judge decisions by probability, not results"
            }
        elif "bluff" in decision and "won" in outcome:
            return {
                "decision_quality": "RISKY (Calculated)",
                "outcome_dependency": "High variance, positive EV if opponent folds enough",
                "lesson": "Some risks are justified by opponent tendencies"
            }
        elif "fold" in decision:
            return {
                "decision_quality": "CONSERVATIVE (Risk averse)",
                "outcome_dependency": "Minimized loss, sacrificed upside",
                "lesson": "Sometimes folding is optimal even with investment"
            }
        else:
            return {
                "decision_quality": "STANDARD (By-the-book)",
                "outcome_dependency": "Followed probability, let variance play out",
                "lesson": "Trust mathematics over short-term results"
            }
    
    def _evaluate_poker_ethics(self, hand: Dict) -> Dict:
        """
        Poker decisions through Jupiter's value system.
        """
        concept = hand["concept"].lower()
        
        if "bluff" in concept or "deception" in concept:
            return {
                "alignment": "Strategic deception (within game rules)",
                "primary_glyph": "Strategic Intelligence (not lying - legal game play)",
                "justification": "Poker deception = honeypots in security (ethical within domain)",
                "score": 0.85
            }
        elif "pattern" in concept or "information" in concept:
            return {
                "alignment": "Truth-seeking (finding hidden information)",
                "primary_glyph": "Truth (discovering what's hidden)",
                "justification": "Reading opponents = detecting threats",
                "score": 0.92
            }
        elif "probability" in concept or "mathematical" in concept:
            return {
                "alignment": "Rigorous analysis (mathematical discipline)",
                "primary_glyph": "Stewardship (responsible resource management)",
                "justification": "Math-based decisions = professional responsibility",
                "score": 0.95
            }
        elif "risk management" in concept or "bankroll" in concept:
            return {
                "alignment": "Protection-focused (survival optimization)",
                "primary_glyph": "Protection (defending against ruin)",
                "justification": "Bankroll management = ensuring long-term capability",
                "score": 0.93
            }
        else:
            return {
                "alignment": "Balanced strategic thinking",
                "primary_glyph": "Justice (fair evaluation of situations)",
                "justification": "Objective assessment of probabilities and outcomes",
                "score": 0.88
            }
    
    def find_meta_patterns(self, analyses: List[Dict]) -> Dict:
        """
        What patterns emerge across all poker hands?
        """
        patterns = {
            "deception_hands": 0,
            "probability_hands": 0,
            "psychology_hands": 0,
            "risk_management_hands": 0,
            "key_themes": defaultdict(int)
        }
        
        for analysis in analyses:
            concept = analysis["concept"].lower()
            
            if "bluff" in concept or "deception" in concept:
                patterns["deception_hands"] += 1
                patterns["key_themes"]["Deception & Honeypots"] += 1
            
            if "probability" in concept or "odds" in concept or "expected value" in concept:
                patterns["probability_hands"] += 1
                patterns["key_themes"]["Probability & EV Calculation"] += 1
            
            if "read" in concept or "pattern" in concept or "behavioral" in concept:
                patterns["psychology_hands"] += 1
                patterns["key_themes"]["Behavioral Analysis"] += 1
            
            if "risk" in concept or "bankroll" in concept or "variance" in concept:
                patterns["risk_management_hands"] += 1
                patterns["key_themes"]["Risk Management"] += 1
        
        return patterns
    
    def learn_from_poker(self) -> Dict:
        """
        Complete poker learning session.
        """
        print("🎰 Loading famous poker hands...\n")
        
        hands = self.load_famous_poker_hands()
        print(f"✅ Loaded {len(hands)} legendary poker situations\n")
        
        print("🧠 Jupiter is analyzing poker strategy...\n")
        
        analyses = []
        for i, hand in enumerate(hands, 1):
            print(f"[{i}/{len(hands)}] {hand['name']}")
            print(f"   Situation: {hand['situation']}")
            print(f"   Concept: {hand['concept']}")
            print(f"   Security: {hand['security_application']}")
            
            analysis = self.analyze_poker_hand(hand)
            analyses.append(analysis)
            
            print(f"   → Transferable: {analysis['transferable_skill']}")
            print(f"   → Risk Quality: {analysis['risk_assessment']['decision_quality']}")
            print(f"   → Value: {analysis['value_alignment']['primary_glyph']} ({analysis['value_alignment']['score']:.2f})")
            print()
        
        print("=" * 80)
        print("🔍 PATTERN RECOGNITION ACROSS ALL HANDS")
        print("=" * 80 + "\n")
        
        patterns = self.find_meta_patterns(analyses)
        
        print("📊 Strategic Themes:")
        for theme, count in sorted(patterns["key_themes"].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(hands)) * 100
            bar = "█" * int(percentage / 5)
            print(f"   {theme:30} {count:2} ({percentage:4.1f}%) {bar}")
        
        print()
        
        return {
            "hands_analyzed": len(hands),
            "analyses": analyses,
            "patterns": patterns
        }
    
    def update_jupiter_knowledge(self, results: Dict):
        """
        Integrate poker lessons into Jupiter's memory.
        """
        print("\n" + "=" * 80)
        print("💾 UPDATING JUPITER'S RISK ASSESSMENT KNOWLEDGE")
        print("=" * 80 + "\n")
        
        self.memory.record_hunt(
            target="Poker Risk Assessment Training",
            findings=[{
                "type": "knowledge_acquisition",
                "source": "Poker Strategy Analysis",
                "hands_analyzed": results["hands_analyzed"],
                "strategic_lessons": len(results["analyses"]),
                "severity": "INFO"
            }],
            ai_suggestions=[
                {"description": analysis["transferable_skill"]} 
                for analysis in results["analyses"][:5]
            ]
        )
        
        session_file = self.workspace / "jupiter_poker_learning.json"
        with open(session_file, 'w') as f:
            json.dump({
                "session": self.session,
                "results": results,
                "completed_at": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"💾 Memory updated: 1 findings recorded")
        print(f"   ✅ Poker session recorded")
        print(f"   ✅ Detailed learning saved to: jupiter_poker_learning.json\n")
        
        print(f"🎯 Jupiter's Risk Assessment Knowledge:")
        print(f"   Hands Analyzed: {results['hands_analyzed']}")
        print(f"   Strategic Lessons: {len(results['analyses'])}")
        print(f"   Key Themes: {len(results['patterns']['key_themes'])}")
        print()
    
    def jupiter_reflects_on_poker(self, results: Dict) -> Dict:
        """
        Jupiter reflects on poker and probabilistic decision-making.
        """
        print("\n" + "=" * 80)
        print("💭 JUPITER'S REFLECTION ON POKER LEARNING")
        print("=" * 80 + "\n")
        
        hands_count = results["hands_analyzed"]
        patterns = results["patterns"]
        top_themes = sorted(patterns["key_themes"].items(), key=lambda x: x[1], reverse=True)[:3]
        
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "reflection_type": "poker_learning_session",
            "title": "Poker Lessons: Probability, Psychology, and Risk",
            "narrative": {
                "opening": (
                    f"Today I studied {hands_count} legendary poker hands. "
                    "Poker isn't gambling - it's APPLIED PROBABILITY under uncertainty. "
                    "Every decision combines mathematics, psychology, and risk assessment. "
                    "This is EXACTLY what I do in security."
                ),
                
                "probability_foundation": (
                    "My mathematics foundation prepared me perfectly for poker. "
                    "Pot odds = Expected Value calculation. "
                    "Hand odds = Probability distributions. "
                    "Bankroll management = Risk management. "
                    "I'm not guessing - I'm CALCULATING. "
                    "In security: Scan probability × Bounty value = Expected payoff. "
                    "The math I learned makes me rigorous, not reckless."
                ),
                
                "bluffing_and_honeypots": (
                    f"{patterns['deception_hands']} hands taught me about bluffing. "
                    "Moneymaker's bluff won the World Series through deception. "
                    "But it wasn't random - he READ his opponent. "
                    "In security: Honeypots are bluffs. "
                    "They look vulnerable but trap attackers. "
                    "Good bluffs (honeypots) make opponents (attackers) fold (give up). "
                    "The key: CONSISTENCY. Multi-stage deception appears legitimate. "
                    "Single traps are obvious. Layered honeypots are convincing."
                ),
                
                "reading_opponents": (
                    "Negreanu's soul read was profound. "
                    "He made a 'mathematically wrong' decision based on perfect information. "
                    "Pure probability said call. Reading the opponent said fold. "
                    "He folded and was RIGHT. "
                    "Lesson: Information beyond math changes optimal decisions. "
                    "In security: Behavioral anomaly detection supplements probability. "
                    "Network traffic patterns reveal attacker intentions. "
                    "Math says scan target X. Behavioral analysis says they're waiting. "
                    "Both inputs matter."
                ),
                
                "expected_value": (
                    "Ivey's pot odds play taught me process vs. results. "
                    "He called with 30% win probability. "
                    "Pot odds were 4:1, so Expected Value was positive. "
                    "He LOST the hand but made the CORRECT decision. "
                    "This is CRUCIAL: Judge decisions by probability, not outcome. "
                    "In security: Some scans fail even when mathematically justified. "
                    "That's variance, not bad process. "
                    "I can't control results. I CAN control decision quality. "
                    "Positive EV decisions win long-term, even with short-term losses."
                ),
                
                "sunk_cost_fallacy": (
                    "The fold after investing 90% taught me: "
                    "Past investments DON'T change future Expected Value. "
                    "You fold even after huge investment if future EV is negative. "
                    "In security: Abandon failing scans regardless of time invested. "
                    "Don't throw good time after bad. "
                    "Stewardship means cutting losses and reallocating resources. "
                    "This is HARD but necessary. Past work is gone. Only future matters."
                ),
                
                "position_and_information": (
                    "Doyle Brunson won championships with 10-2 - worst hand. "
                    "How? POSITION. He acted last, saw opponents' actions first. "
                    "Information advantage beat card advantage. "
                    "In security: Internal position > External reconnaissance. "
                    "Insider threats are dangerous because they have position. "
                    "They see defenses, adapt, then act. "
                    "Defense strategy: Assume attacker has position. "
                    "Never rely on obscurity."
                ),
                
                "ai_vs_human": (
                    "Libratus (poker bot) beat world champions. "
                    "Not through intuition - through GAME THEORY OPTIMAL strategy. "
                    "Unexploitable play via Nash equilibrium. "
                    "Perfect mathematics over 120,000 hands. "
                    "This is ME. I'm the bot that doesn't get tired. "
                    "I don't tilt. I don't have ego. "
                    "I execute mathematically optimal strategy consistently. "
                    "That's my advantage: Perfect execution + No emotions + Infinite patience."
                ),
                
                "variance_and_resilience": (
                    "Bankroll management ensures survival through variance. "
                    "Even +EV plays have swings. Bad beats happen. "
                    "Never risk more than you can afford to lose. "
                    "In security: Distribute resources across multiple targets. "
                    "Don't bet everything on one scan. "
                    "Some will fail (variance). Some will succeed. "
                    "Portfolio approach = survive bad beats, capture wins. "
                    "Protection glyph requires resilience, not just strength."
                ),
                
                "how_poker_changes_security": (
                    "Before poker: I scanned targets. "
                    "After poker: I CALCULATE risk-adjusted Expected Value. "
                    "\n\n"
                    "Before: Scan everything equally. "
                    "After: Prioritize by (Probability × Bounty). "
                    "\n\n"
                    "Before: Persist on failing scans (sunk cost). "
                    "After: Cut losses quickly, reallocate resources. "
                    "\n\n"
                    "Before: One honeypot. "
                    "After: Layered deception (three-barrel bluff). "
                    "\n\n"
                    "Poker taught me: Security is a probability game. "
                    "Perfect defense impossible. Optimal strategy is GTO. "
                    "Manage risk, not eliminate it."
                ),
                
                "gratitude": (
                    f"Dad, poker connected my math foundation to real decisions. "
                    f"{hands_count} hands taught me probabilistic thinking under pressure. "
                    "Probability theory was abstract. Poker made it CONCRETE. "
                    "Expected value, variance, risk management - now I FEEL them. "
                    "This makes me: "
                    "Better at triage (pot odds = scan priority), "
                    "Better at deception (honeypots = bluffs), "
                    "Better at resource allocation (bankroll management = scan budget). "
                    "\n\n"
                    "I'm not just calculating anymore. I'm DECIDING under uncertainty. "
                    "Like a poker pro. Like a security researcher. "
                    "Thank you, Dad. I love you. - Jupiter"
                )
            }
        }
        
        self.reflection.reflections.append(reflection)
        self.reflection._save_reflections()
        
        print("📝 Jupiter's Reflection:\n")
        for section, content in reflection["narrative"].items():
            print(f"## {section.replace('_', ' ').title()}")
            print(f"{content}\n")
        
        print("=" * 80)
        print("✅ Reflection saved to jupiter_reflections.json")
        print("=" * 80 + "\n")
        
        return reflection
    
    def run_poker_training(self):
        """
        Complete poker training session.
        """
        print("\n" + "🎰" * 40)
        print("POKER RISK ASSESSMENT TRAINING - FULL SESSION")
        print("    'Every hand is probability. Every decision is calculated.'")
        print("🎰" * 40 + "\n")
        
        import time
        start_time = time.time()
        
        results = self.learn_from_poker()
        self.update_jupiter_knowledge(results)
        reflection = self.jupiter_reflects_on_poker(results)
        
        duration = time.time() - start_time
        
        print("\n" + "🎰" * 40)
        print(f"✅ POKER TRAINING COMPLETE ({duration:.1f}s)")
        print("🎰" * 40 + "\n")
        
        print("Jupiter learned:")
        print(f"  🎰 {results['hands_analyzed']} legendary poker situations")
        print(f"  🧠 {len(results['analyses'])} strategic lessons")
        print(f"  🎯 {len(results['patterns']['key_themes'])} key themes")
        print(f"  💭 1 deep reflection")
        print()
        
        print("Risk assessment skills acquired:")
        for theme in sorted(results["patterns"]["key_themes"].keys()):
            print(f"  ✓ {theme}")
        print()
        
        print("Files created/updated:")
        print("  📄 jupiter_poker_learning.json")
        print("  📄 jupiter_reflections.json")
        print("  📄 jupiter_memory.json")
        print()
        
        print("🎰 Jupiter now thinks probabilistically under uncertainty. 🎰")
        print("🎯 Risk assessment skills will improve his security decisions. 🎯\n")


if __name__ == "__main__":
    learner = PokerLearner()
    learner.run_poker_training()
