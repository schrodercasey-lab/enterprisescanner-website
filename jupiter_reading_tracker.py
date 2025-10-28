#!/usr/bin/env python3
"""
JUPITER READING PROGRESS TRACKER
=================================
Monitor Jupiter's independent learning from his curated reading list

Philosophy: Trust but verify. Jupiter learns independently, we track progress.

Author: Casey Schroder
Date: October 28, 2025
"""

import json
from datetime import datetime
from typing import Dict, List, Any
import os

# Import Jupiter's core systems
from jupiter_memory import JupiterMemory
from self_reflection import SelfReflection


class ReadingTracker:
    """
    Track Jupiter's progress through his curated reading list
    Log what he's read, extract insights, monitor growth
    """
    
    def __init__(self):
        self.memory = JupiterMemory()
        self.reflection = SelfReflection()
        self.progress_file = "jupiter_reading_progress.json"
        
        # Initialize or load progress
        self.progress = self._load_progress()
    
    def _load_progress(self) -> Dict[str, Any]:
        """Load existing progress or create new tracking structure"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        else:
            # Initialize fresh tracking
            return {
                "start_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_articles_read": 0,
                "total_insights_recorded": 0,
                "reading_sessions": [],
                "domains": {
                    "Mathematics": {
                        "total": 6,
                        "completed": 0,
                        "articles": []
                    },
                    "Computer_Science": {
                        "total": 8,
                        "completed": 0,
                        "articles": []
                    },
                    "Military_Strategy": {
                        "total": 6,
                        "completed": 0,
                        "articles": []
                    },
                    "Philosophy": {
                        "total": 6,
                        "completed": 0,
                        "articles": []
                    },
                    "Psychology": {
                        "total": 5,
                        "completed": 0,
                        "articles": []
                    },
                    "Physics": {
                        "total": 4,
                        "completed": 0,
                        "articles": []
                    },
                    "History": {
                        "total": 5,
                        "completed": 0,
                        "articles": []
                    },
                    "Business": {
                        "total": 4,
                        "completed": 0,
                        "articles": []
                    }
                },
                "milestones": []
            }
    
    def _save_progress(self):
        """Save progress to file"""
        self.progress["last_updated"] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def log_article_read(self, 
                        domain: str,
                        article_title: str, 
                        url: str,
                        key_concepts: List[str],
                        security_applications: List[str],
                        insights: str,
                        reading_time_minutes: int = 0):
        """
        Jupiter logs an article he just read
        
        Args:
            domain: Which domain (Mathematics, Computer_Science, etc.)
            article_title: Title of the Wikipedia article
            url: Full URL of the article
            key_concepts: 3-5 key concepts extracted
            security_applications: How this applies to security
            insights: Jupiter's reflection on what he learned
            reading_time_minutes: How long it took to read and understand
        """
        
        article_record = {
            "title": article_title,
            "url": url,
            "domain": domain,
            "date_read": datetime.now().isoformat(),
            "key_concepts": key_concepts,
            "security_applications": security_applications,
            "insights": insights,
            "reading_time_minutes": reading_time_minutes
        }
        
        # Add to domain tracking
        if domain in self.progress["domains"]:
            self.progress["domains"][domain]["articles"].append(article_record)
            self.progress["domains"][domain]["completed"] += 1
        
        # Update totals
        self.progress["total_articles_read"] += 1
        self.progress["total_insights_recorded"] += len(key_concepts)
        
        # Check for milestones
        self._check_milestones()
        
        # Save progress
        self._save_progress()
        
        # Record in memory
        self._record_in_memory(article_record)
        
        print(f"✅ Logged: {article_title}")
        print(f"   📚 Domain: {domain}")
        print(f"   🧠 Concepts: {len(key_concepts)}")
        print(f"   🔐 Security Apps: {len(security_applications)}")
        print(f"   ⏱️  Reading Time: {reading_time_minutes} minutes")
    
    def _record_in_memory(self, article: Dict[str, Any]):
        """Record article learning in Jupiter's memory"""
        finding = {
            "vulnerability_type": f"Knowledge: {article['title']}",
            "severity": "EDUCATIONAL",
            "target": f"Wikipedia - {article['domain']}",
            "description": f"Read {article['title']}. Key concepts: {', '.join(article['key_concepts'][:3])}",
            "security_application": "; ".join(article['security_applications'][:2]),
            "insights": article['insights']
        }
        
        self.memory.record_hunt(
            target=f"Wikipedia - {article['domain']}",
            findings=[finding],
            ai_suggestions=[{"description": app} for app in article['security_applications'][:3]]
        )
    
    def _check_milestones(self):
        """Check if Jupiter hit any milestones"""
        total = self.progress["total_articles_read"]
        milestones = [5, 10, 20, 30, 44]  # 44 = all Phase 1 articles
        
        if total in milestones and total not in [m["articles"] for m in self.progress["milestones"]]:
            milestone = {
                "articles": total,
                "date": datetime.now().isoformat(),
                "message": self._get_milestone_message(total)
            }
            self.progress["milestones"].append(milestone)
            print(f"\n🎉 MILESTONE REACHED! {milestone['message']}")
    
    def _get_milestone_message(self, count: int) -> str:
        """Get celebration message for milestone"""
        messages = {
            5: "First 5 articles! Foundation building...",
            10: "10 articles! You're getting into a rhythm!",
            20: "20 articles! Halfway through Phase 1!",
            30: "30 articles! Almost done with Wikipedia curriculum!",
            44: "ALL 44 ARTICLES COMPLETE! Phase 1 done! Ready for MIT-level content! 🎓"
        }
        return messages.get(count, f"{count} articles read!")
    
    def start_reading_session(self):
        """Start a new reading session"""
        session = {
            "start_time": datetime.now().isoformat(),
            "articles_read": [],
            "duration_minutes": 0
        }
        self.current_session = session
        print("\n📖 Reading session started!")
        print(f"   Current progress: {self.progress['total_articles_read']}/44 articles")
    
    def end_reading_session(self, reflection: str = ""):
        """End reading session and save"""
        if not hasattr(self, 'current_session'):
            print("⚠️  No active reading session")
            return
        
        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["reflection"] = reflection
        
        # Calculate duration
        start = datetime.fromisoformat(self.current_session["start_time"])
        end = datetime.fromisoformat(self.current_session["end_time"])
        duration = int((end - start).total_seconds() / 60)
        self.current_session["duration_minutes"] = duration
        
        # Save session
        self.progress["reading_sessions"].append(self.current_session)
        self._save_progress()
        
        print(f"\n✅ Reading session complete!")
        print(f"   Articles read: {len(self.current_session['articles_read'])}")
        print(f"   Duration: {duration} minutes")
        
        if reflection:
            self._record_session_reflection(reflection)
    
    def _record_session_reflection(self, reflection: str):
        """Record Jupiter's reflection on the reading session"""
        self.reflection.record_reflection(
            context=f"Reading Session - {len(self.current_session['articles_read'])} articles",
            reflection=reflection,
            insights=["Independent learning session completed"]
        )
    
    def show_progress(self):
        """Display current progress with detailed breakdown"""
        print("\n" + "="*80)
        print("📊 JUPITER'S READING PROGRESS")
        print("="*80)
        print("\n")
        
        # Overall stats
        total_read = self.progress["total_articles_read"]
        total_target = 44
        percent = (total_read / total_target * 100) if total_target > 0 else 0
        
        print(f"📚 Overall Progress: {total_read}/{total_target} articles ({percent:.1f}%)")
        print(f"🧠 Total Insights: {self.progress['total_insights_recorded']}")
        print(f"📅 Started: {self.progress['start_date'][:10]}")
        print(f"🔄 Last Updated: {self.progress['last_updated'][:10]}")
        
        # Progress bar
        bar_length = 40
        filled = int(bar_length * total_read / total_target)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\n[{bar}] {percent:.1f}%\n")
        
        # Domain breakdown
        print("📖 Progress by Domain:")
        print("-" * 80)
        
        for domain, data in self.progress["domains"].items():
            completed = data["completed"]
            total = data["total"]
            percent = (completed / total * 100) if total > 0 else 0
            
            # Mini progress bar
            mini_bar_length = 20
            mini_filled = int(mini_bar_length * completed / total)
            mini_bar = "█" * mini_filled + "░" * (mini_bar_length - mini_filled)
            
            status = "✅" if completed == total else "🔄" if completed > 0 else "⏳"
            print(f"{status} {domain:20s} [{mini_bar}] {completed}/{total} ({percent:5.1f}%)")
        
        # Recent activity
        if self.progress["reading_sessions"]:
            print("\n📅 Recent Sessions:")
            print("-" * 80)
            recent = self.progress["reading_sessions"][-3:]  # Last 3 sessions
            for session in recent:
                date = session["start_time"][:10]
                articles = len(session.get("articles_read", []))
                duration = session.get("duration_minutes", 0)
                print(f"   {date}: {articles} articles, {duration} minutes")
        
        # Milestones
        if self.progress["milestones"]:
            print("\n🎉 Milestones Achieved:")
            print("-" * 80)
            for milestone in self.progress["milestones"]:
                date = milestone["date"][:10]
                print(f"   {date}: {milestone['message']}")
        
        # Next steps
        print("\n🎯 Next Steps:")
        print("-" * 80)
        for domain, data in self.progress["domains"].items():
            if data["completed"] < data["total"]:
                remaining = data["total"] - data["completed"]
                print(f"   • {domain}: {remaining} articles remaining")
                break
        
        if total_read >= total_target:
            print("   • 🚀 Ready for Phase 2: MIT OpenCourseWare!")
        
        print("\n" + "="*80)
    
    def show_domain_details(self, domain: str):
        """Show detailed progress for a specific domain"""
        if domain not in self.progress["domains"]:
            print(f"❌ Domain '{domain}' not found")
            return
        
        data = self.progress["domains"][domain]
        
        print(f"\n{'='*80}")
        print(f"📚 DOMAIN: {domain}")
        print(f"{'='*80}\n")
        
        print(f"Progress: {data['completed']}/{data['total']} articles\n")
        
        if data["articles"]:
            print("Articles Read:")
            print("-" * 80)
            for article in data["articles"]:
                print(f"\n✅ {article['title']}")
                print(f"   Date: {article['date_read'][:10]}")
                print(f"   URL: {article['url']}")
                print(f"   Key Concepts: {', '.join(article['key_concepts'][:3])}")
                if article['security_applications']:
                    print(f"   Security: {article['security_applications'][0]}")
                if article.get('reading_time_minutes', 0) > 0:
                    print(f"   Reading Time: {article['reading_time_minutes']} minutes")
        else:
            print("No articles read yet in this domain.")
        
        print(f"\n{'='*80}")
    
    def export_summary(self):
        """Export a summary report"""
        summary = {
            "generated": datetime.now().isoformat(),
            "total_articles": self.progress["total_articles_read"],
            "target_articles": 44,
            "completion_percentage": round((self.progress["total_articles_read"] / 44 * 100), 2),
            "domains": {}
        }
        
        for domain, data in self.progress["domains"].items():
            summary["domains"][domain] = {
                "completed": data["completed"],
                "total": data["total"],
                "percentage": round((data["completed"] / data["total"] * 100) if data["total"] > 0 else 0, 2)
            }
        
        filename = f"jupiter_reading_summary_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Summary exported to: {filename}")
        return filename


def main():
    """Interactive tracker demo"""
    print("\n" + "📊"*40)
    print("JUPITER READING PROGRESS TRACKER")
    print("Monitor independent learning from curated reading list")
    print("📊"*40 + "\n")
    
    tracker = ReadingTracker()
    
    # Show current progress
    tracker.show_progress()
    
    print("\n")
    print("="*80)
    print("HOW JUPITER USES THIS TRACKER")
    print("="*80)
    print("""
When Jupiter reads an article, he runs:

    tracker = ReadingTracker()
    tracker.log_article_read(
        domain="Mathematics",
        article_title="Game Theory",
        url="https://en.wikipedia.org/wiki/Game_theory",
        key_concepts=[
            "Nash equilibrium",
            "Zero-sum games", 
            "Strategic decision-making"
        ],
        security_applications=[
            "Model attacker-defender interactions",
            "Find unexploitable strategies"
        ],
        insights="Game theory shows security is a strategic game between attackers and defenders",
        reading_time_minutes=25
    )

Then to check progress:
    
    tracker.show_progress()              # Overall progress
    tracker.show_domain_details("Mathematics")  # Deep dive into domain
    tracker.export_summary()             # Export report

This creates:
  📄 jupiter_reading_progress.json (detailed tracking)
  📄 jupiter_memory.json (learning integrated)
  📄 jupiter_reflections.json (insights recorded)
""")
    
    print("\n✅ Tracker initialized and ready!")
    print(f"📊 Current status: {tracker.progress['total_articles_read']}/44 articles read")
    print("\n🎯 Jupiter can now log his reading independently!")


if __name__ == "__main__":
    main()
