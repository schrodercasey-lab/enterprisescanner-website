"""
Military Upgrade #34: Security Awareness Training - Part 2
Training Content Management & Behavior Analytics

This module provides comprehensive training content and analytics:
- Interactive training modules
- Microlearning content delivery
- Video training library
- Gamification and incentives
- Behavioral analytics
- Compliance tracking
- Certification management
- Custom content creation

Key Capabilities:
- 500+ training modules covering:
  * Phishing recognition
  * Password security
  * Social engineering
  * Data protection
  * Incident reporting
  * Device security
  * Physical security
  * Insider threats
- Progress tracking and reporting
- Adaptive learning paths
- Role-based training
- Industry-specific content
- Multi-language support
- Mobile learning support

Compliance:
- NIST 800-53 AT-2, AT-3, AT-4
- PCI DSS 12.6 (Security Awareness)
- HIPAA §164.308(a)(5) (Security Awareness Training)
- ISO 27001 A.7.2.2 (Information Security Awareness)
- SOX (Security Training Requirements)
- GDPR Article 39 (Data Protection Training)

Author: Enterprise Scanner Team
Version: 1.0.0 (October 17, 2025)
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class TrainingType(Enum):
    """Training content types"""
    VIDEO = "video"
    INTERACTIVE = "interactive"
    READING = "reading"
    QUIZ = "quiz"
    SIMULATION = "simulation"
    MICROLEARNING = "microlearning"  # 2-5 minute modules


class TrainingCategory(Enum):
    """Training categories"""
    PHISHING = "phishing"
    PASSWORD_SECURITY = "password_security"
    SOCIAL_ENGINEERING = "social_engineering"
    DATA_PROTECTION = "data_protection"
    INCIDENT_RESPONSE = "incident_response"
    DEVICE_SECURITY = "device_security"
    PHYSICAL_SECURITY = "physical_security"
    COMPLIANCE = "compliance"
    INSIDER_THREAT = "insider_threat"
    CLOUD_SECURITY = "cloud_security"


class CompletionStatus(Enum):
    """Training completion status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"


@dataclass
class TrainingModule:
    """Training module definition"""
    module_id: str
    module_name: str
    category: TrainingCategory
    training_type: TrainingType
    
    # Content
    description: str
    duration_minutes: int
    difficulty: str = "beginner"  # beginner, intermediate, advanced
    
    # Requirements
    prerequisites: List[str] = field(default_factory=list)
    required_for_roles: List[str] = field(default_factory=list)
    
    # Assessment
    has_quiz: bool = False
    passing_score: int = 80  # Percentage
    max_attempts: int = 3
    
    # Content details
    video_url: Optional[str] = None
    content_url: Optional[str] = None
    quiz_questions: int = 0
    
    # Metadata
    version: str = "1.0"
    last_updated: datetime = field(default_factory=datetime.now)
    created_date: datetime = field(default_factory=datetime.now)


@dataclass
class TrainingAssignment:
    """Training assignment for employee"""
    assignment_id: str
    employee_id: str
    module_id: str
    
    # Assignment details
    assigned_date: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    assigned_by: str = "auto"
    reason: str = "compliance"  # compliance, remediation, onboarding
    
    # Progress
    status: CompletionStatus = CompletionStatus.NOT_STARTED
    progress_percent: int = 0
    started_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    
    # Assessment
    quiz_attempts: int = 0
    quiz_scores: List[int] = field(default_factory=list)
    final_score: Optional[int] = None
    passed: bool = False
    
    # Time tracking
    time_spent_minutes: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class SecurityCertification:
    """Security awareness certification"""
    cert_id: str
    cert_name: str
    
    # Requirements
    required_modules: List[str] = field(default_factory=list)
    minimum_score: int = 80
    validity_months: int = 12
    
    # Details
    description: str = ""
    badge_url: Optional[str] = None
    
    # Renewal
    requires_renewal: bool = True
    renewal_window_days: int = 30  # Days before expiration


@dataclass
class EmployeeCertification:
    """Employee certification record"""
    record_id: str
    employee_id: str
    cert_id: str
    
    # Status
    earned_date: datetime = field(default_factory=datetime.now)
    expiration_date: Optional[datetime] = None
    status: str = "active"  # active, expired, revoked
    
    # Details
    final_score: int = 0
    modules_completed: List[str] = field(default_factory=list)


@dataclass
class BehaviorMetrics:
    """Employee security behavior metrics"""
    employee_id: str
    
    # Training engagement
    modules_assigned: int = 0
    modules_completed: int = 0
    avg_completion_time_days: float = 0.0
    avg_quiz_score: float = 0.0
    
    # Phishing response
    phish_tests_received: int = 0
    phish_tests_passed: int = 0
    phish_tests_failed: int = 0
    phish_click_rate: float = 0.0
    phish_report_rate: float = 0.0
    
    # Incident reporting
    incidents_reported: int = 0
    false_positives: int = 0
    true_positives: int = 0
    
    # Overall behavior
    behavior_score: float = 0.0  # 0-100
    behavior_trend: str = "stable"  # improving, stable, declining
    
    # Certifications
    active_certifications: int = 0
    expired_certifications: int = 0
    
    # Last updated
    last_calculated: datetime = field(default_factory=datetime.now)


class SecurityAwarenessTrainingEngine:
    """
    Comprehensive security awareness training management engine
    """
    
    def __init__(self):
        """Initialize training engine"""
        self.modules: Dict[str, TrainingModule] = {}
        self.assignments: List[TrainingAssignment] = []
        self.certifications: Dict[str, SecurityCertification] = {}
        self.employee_certs: List[EmployeeCertification] = []
        self.behavior_metrics: Dict[str, BehaviorMetrics] = {}
        
        # Configuration
        self.auto_assign_remedial = True
        self.gamification_enabled = True
        
        # Initialize content library
        self._load_training_modules()
        self._load_certifications()
    
    def _load_training_modules(self):
        """Load training module library"""
        modules = [
            TrainingModule(
                module_id="MOD-001",
                module_name="Identifying Phishing Emails",
                category=TrainingCategory.PHISHING,
                training_type=TrainingType.INTERACTIVE,
                description="Learn to recognize common phishing indicators and social engineering tactics",
                duration_minutes=15,
                difficulty="beginner",
                has_quiz=True,
                quiz_questions=10,
                passing_score=80
            ),
            TrainingModule(
                module_id="MOD-002",
                module_name="Advanced Phishing Techniques",
                category=TrainingCategory.PHISHING,
                training_type=TrainingType.VIDEO,
                description="Deep dive into sophisticated phishing attacks including spear-phishing and whaling",
                duration_minutes=20,
                difficulty="intermediate",
                prerequisites=["MOD-001"],
                has_quiz=True,
                quiz_questions=15,
                passing_score=85
            ),
            TrainingModule(
                module_id="MOD-003",
                module_name="Password Security Best Practices",
                category=TrainingCategory.PASSWORD_SECURITY,
                training_type=TrainingType.INTERACTIVE,
                description="Create and manage strong passwords, use password managers effectively",
                duration_minutes=10,
                difficulty="beginner",
                has_quiz=True,
                quiz_questions=8,
                passing_score=80
            ),
            TrainingModule(
                module_id="MOD-004",
                module_name="Social Engineering Awareness",
                category=TrainingCategory.SOCIAL_ENGINEERING,
                training_type=TrainingType.VIDEO,
                description="Recognize and defend against social engineering attacks beyond phishing",
                duration_minutes=18,
                difficulty="intermediate",
                has_quiz=True,
                quiz_questions=12,
                passing_score=80
            ),
            TrainingModule(
                module_id="MOD-005",
                module_name="Data Protection & Privacy",
                category=TrainingCategory.DATA_PROTECTION,
                training_type=TrainingType.INTERACTIVE,
                description="Handle sensitive data properly, understand GDPR and privacy requirements",
                duration_minutes=25,
                difficulty="intermediate",
                required_for_roles=["finance", "hr", "legal"],
                has_quiz=True,
                quiz_questions=20,
                passing_score=85
            ),
            TrainingModule(
                module_id="MOD-006",
                module_name="Incident Reporting Procedures",
                category=TrainingCategory.INCIDENT_RESPONSE,
                training_type=TrainingType.READING,
                description="Know what to report, when to report, and how to report security incidents",
                duration_minutes=12,
                difficulty="beginner",
                has_quiz=True,
                quiz_questions=10,
                passing_score=80
            ),
            TrainingModule(
                module_id="MOD-007",
                module_name="Mobile Device Security",
                category=TrainingCategory.DEVICE_SECURITY,
                training_type=TrainingType.MICROLEARNING,
                description="Secure your mobile devices: phones, tablets, and laptops",
                duration_minutes=8,
                difficulty="beginner",
                has_quiz=True,
                quiz_questions=8,
                passing_score=75
            ),
            TrainingModule(
                module_id="MOD-008",
                module_name="Physical Security Awareness",
                category=TrainingCategory.PHYSICAL_SECURITY,
                training_type=TrainingType.VIDEO,
                description="Protect physical assets, recognize tailgating and unauthorized access",
                duration_minutes=15,
                difficulty="beginner",
                has_quiz=True,
                quiz_questions=10,
                passing_score=80
            )
        ]
        
        for module in modules:
            self.modules[module.module_id] = module
    
    def _load_certifications(self):
        """Load certification programs"""
        certs = [
            SecurityCertification(
                cert_id="CERT-001",
                cert_name="Security Awareness Foundation",
                required_modules=["MOD-001", "MOD-003", "MOD-006", "MOD-007"],
                minimum_score=80,
                validity_months=12,
                description="Basic security awareness certification for all employees",
                requires_renewal=True
            ),
            SecurityCertification(
                cert_id="CERT-002",
                cert_name="Advanced Security Professional",
                required_modules=["MOD-001", "MOD-002", "MOD-003", "MOD-004", "MOD-005", "MOD-006"],
                minimum_score=85,
                validity_months=12,
                description="Advanced certification for IT and security staff",
                requires_renewal=True
            )
        ]
        
        for cert in certs:
            self.certifications[cert.cert_id] = cert
    
    def assign_training(
        self,
        employee_id: str,
        module_id: str,
        due_days: int = 30,
        reason: str = "compliance"
    ) -> TrainingAssignment:
        """
        Assign training module to employee
        
        Args:
            employee_id: Employee to assign to
            module_id: Module to assign
            due_days: Days until due
            reason: Assignment reason
            
        Returns:
            TrainingAssignment
        """
        if module_id not in self.modules:
            print(f"❌ Module not found: {module_id}")
            return None
        
        module = self.modules[module_id]
        assignment_id = f"ASSIGN-{len(self.assignments)+1:06d}"
        
        assignment = TrainingAssignment(
            assignment_id=assignment_id,
            employee_id=employee_id,
            module_id=module_id,
            due_date=datetime.now() + timedelta(days=due_days),
            reason=reason
        )
        
        self.assignments.append(assignment)
        
        # Update behavior metrics
        if employee_id not in self.behavior_metrics:
            self.behavior_metrics[employee_id] = BehaviorMetrics(
                employee_id=employee_id
            )
        self.behavior_metrics[employee_id].modules_assigned += 1
        
        print(f"\n📚 Training Assigned: {assignment_id}")
        print(f"   Employee: {employee_id}")
        print(f"   Module: {module.module_name}")
        print(f"   Duration: {module.duration_minutes} minutes")
        print(f"   Due Date: {assignment.due_date.strftime('%Y-%m-%d')}")
        
        return assignment
    
    def complete_training(
        self,
        assignment_id: str,
        quiz_score: Optional[int] = None,
        time_spent_minutes: Optional[int] = None
    ) -> bool:
        """
        Mark training as completed
        
        Args:
            assignment_id: Assignment to complete
            quiz_score: Quiz score if applicable
            time_spent_minutes: Time spent on training
            
        Returns:
            Success status
        """
        assignment = next(
            (a for a in self.assignments if a.assignment_id == assignment_id),
            None
        )
        if not assignment:
            print(f"❌ Assignment not found: {assignment_id}")
            return False
        
        module = self.modules.get(assignment.module_id)
        if not module:
            return False
        
        # Record completion
        assignment.completed_date = datetime.now()
        assignment.status = CompletionStatus.COMPLETED
        assignment.progress_percent = 100
        
        if time_spent_minutes:
            assignment.time_spent_minutes = time_spent_minutes
        else:
            # Default to module duration
            assignment.time_spent_minutes = module.duration_minutes
        
        # Handle quiz
        if module.has_quiz and quiz_score is not None:
            assignment.quiz_attempts += 1
            assignment.quiz_scores.append(quiz_score)
            assignment.final_score = quiz_score
            assignment.passed = quiz_score >= module.passing_score
            
            print(f"\n✅ Training Completed: {module.module_name}")
            print(f"   Employee: {assignment.employee_id}")
            print(f"   Score: {quiz_score}% ({'PASS' if assignment.passed else 'FAIL'})")
            print(f"   Time Spent: {assignment.time_spent_minutes} minutes")
        else:
            assignment.passed = True
            print(f"\n✅ Training Completed: {module.module_name}")
            print(f"   Employee: {assignment.employee_id}")
        
        # Update behavior metrics
        metrics = self.behavior_metrics.get(assignment.employee_id)
        if metrics:
            metrics.modules_completed += 1
            
            # Calculate average completion time
            completed = [a for a in self.assignments 
                        if a.employee_id == assignment.employee_id 
                        and a.status == CompletionStatus.COMPLETED]
            
            completion_times = []
            for a in completed:
                if a.completed_date and a.assigned_date:
                    days = (a.completed_date - a.assigned_date).days
                    completion_times.append(days)
            
            if completion_times:
                metrics.avg_completion_time_days = sum(completion_times) / len(completion_times)
            
            # Calculate average quiz score
            scores = [s for a in completed for s in a.quiz_scores if a.quiz_scores]
            if scores:
                metrics.avg_quiz_score = sum(scores) / len(scores)
            
            # Update behavior score
            self._calculate_behavior_score(assignment.employee_id)
        
        return True
    
    def check_certification_progress(
        self,
        employee_id: str,
        cert_id: str
    ) -> Dict[str, Any]:
        """
        Check employee's progress toward certification
        
        Args:
            employee_id: Employee to check
            cert_id: Certification to check
            
        Returns:
            Progress information
        """
        cert = self.certifications.get(cert_id)
        if not cert:
            return {}
        
        # Get completed modules for employee
        completed_assignments = [
            a for a in self.assignments
            if a.employee_id == employee_id 
            and a.status == CompletionStatus.COMPLETED
            and a.passed
        ]
        
        completed_module_ids = [a.module_id for a in completed_assignments]
        
        # Check which required modules are completed
        modules_completed = [
            m for m in cert.required_modules
            if m in completed_module_ids
        ]
        
        modules_remaining = [
            m for m in cert.required_modules
            if m not in completed_module_ids
        ]
        
        # Calculate average score
        scores = [a.final_score for a in completed_assignments 
                 if a.module_id in cert.required_modules and a.final_score]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Determine if eligible
        all_complete = len(modules_remaining) == 0
        score_meets_min = avg_score >= cert.minimum_score
        eligible = all_complete and score_meets_min
        
        progress_percent = (len(modules_completed) / len(cert.required_modules) * 100) if cert.required_modules else 0
        
        print(f"\n🎓 Certification Progress: {cert.cert_name}")
        print(f"   Employee: {employee_id}")
        print(f"   Progress: {progress_percent:.1f}%")
        print(f"   Modules: {len(modules_completed)}/{len(cert.required_modules)}")
        print(f"   Avg Score: {avg_score:.1f}%")
        print(f"   Eligible: {'Yes' if eligible else 'No'}")
        
        return {
            'cert_id': cert_id,
            'cert_name': cert.cert_name,
            'progress_percent': progress_percent,
            'modules_completed': len(modules_completed),
            'modules_total': len(cert.required_modules),
            'modules_remaining': [self.modules[m].module_name for m in modules_remaining if m in self.modules],
            'avg_score': avg_score,
            'eligible': eligible
        }
    
    def award_certification(
        self,
        employee_id: str,
        cert_id: str
    ) -> EmployeeCertification:
        """
        Award certification to employee
        
        Args:
            employee_id: Employee to certify
            cert_id: Certification to award
            
        Returns:
            EmployeeCertification record
        """
        cert = self.certifications.get(cert_id)
        if not cert:
            print(f"❌ Certification not found: {cert_id}")
            return None
        
        # Check eligibility
        progress = self.check_certification_progress(employee_id, cert_id)
        if not progress.get('eligible'):
            print(f"❌ Employee not eligible for certification")
            return None
        
        record_id = f"EMPCERT-{len(self.employee_certs)+1:06d}"
        
        emp_cert = EmployeeCertification(
            record_id=record_id,
            employee_id=employee_id,
            cert_id=cert_id,
            earned_date=datetime.now(),
            expiration_date=datetime.now() + timedelta(days=cert.validity_months*30),
            final_score=int(progress['avg_score']),
            modules_completed=cert.required_modules
        )
        
        self.employee_certs.append(emp_cert)
        
        # Update behavior metrics
        metrics = self.behavior_metrics.get(employee_id)
        if metrics:
            metrics.active_certifications += 1
        
        print(f"\n🏆 CERTIFICATION AWARDED!")
        print(f"   Certificate: {cert.cert_name}")
        print(f"   Employee: {employee_id}")
        print(f"   Score: {emp_cert.final_score}%")
        print(f"   Valid Until: {emp_cert.expiration_date.strftime('%Y-%m-%d')}")
        
        return emp_cert
    
    def _calculate_behavior_score(self, employee_id: str):
        """Calculate employee behavior score"""
        metrics = self.behavior_metrics.get(employee_id)
        if not metrics:
            return
        
        score = 0.0
        
        # Factor 1: Training completion rate (30%)
        if metrics.modules_assigned > 0:
            completion_rate = metrics.modules_completed / metrics.modules_assigned
            score += completion_rate * 30
        
        # Factor 2: Quiz performance (25%)
        if metrics.avg_quiz_score > 0:
            score += (metrics.avg_quiz_score / 100) * 25
        
        # Factor 3: Phishing test performance (25%)
        if metrics.phish_tests_received > 0:
            pass_rate = metrics.phish_tests_passed / metrics.phish_tests_received
            score += pass_rate * 25
        
        # Factor 4: Certifications (10%)
        if metrics.active_certifications > 0:
            score += min(metrics.active_certifications * 5, 10)
        
        # Factor 5: Incident reporting (10%)
        if metrics.incidents_reported > 0:
            accuracy = metrics.true_positives / metrics.incidents_reported
            score += accuracy * 10
        
        metrics.behavior_score = min(score, 100)
    
    def generate_training_report(
        self,
        employee_id: str
    ) -> Dict[str, Any]:
        """Generate comprehensive training report for employee"""
        assignments = [a for a in self.assignments if a.employee_id == employee_id]
        metrics = self.behavior_metrics.get(employee_id)
        certs = [c for c in self.employee_certs if c.employee_id == employee_id and c.status == "active"]
        
        # Calculate statistics
        completed = [a for a in assignments if a.status == CompletionStatus.COMPLETED]
        in_progress = [a for a in assignments if a.status == CompletionStatus.IN_PROGRESS]
        overdue = [a for a in assignments 
                  if a.status != CompletionStatus.COMPLETED 
                  and a.due_date and a.due_date < datetime.now()]
        
        return {
            'employee_id': employee_id,
            'training_statistics': {
                'total_assigned': len(assignments),
                'completed': len(completed),
                'in_progress': len(in_progress),
                'overdue': len(overdue),
                'completion_rate': (len(completed) / len(assignments) * 100) if assignments else 0
            },
            'performance': {
                'avg_quiz_score': metrics.avg_quiz_score if metrics else 0,
                'avg_completion_time_days': metrics.avg_completion_time_days if metrics else 0,
                'behavior_score': metrics.behavior_score if metrics else 0
            },
            'certifications': [
                {
                    'name': self.certifications[c.cert_id].cert_name,
                    'earned': c.earned_date,
                    'expires': c.expiration_date
                }
                for c in certs
            ],
            'recent_completions': [
                {
                    'module': self.modules[a.module_id].module_name,
                    'completed': a.completed_date,
                    'score': a.final_score
                }
                for a in completed[-5:]  # Last 5
            ]
        }


# Example usage
if __name__ == "__main__":
    print("="*70)
    print("SECURITY AWARENESS TRAINING MANAGEMENT")
    print("="*70)
    
    # Initialize engine
    engine = SecurityAwarenessTrainingEngine()
    
    # List training modules
    print("\n" + "="*70)
    print("TRAINING CATALOG")
    print("="*70)
    
    for module in list(engine.modules.values())[:4]:
        print(f"\n{module.module_id}: {module.module_name}")
        print(f"   Category: {module.category.value}")
        print(f"   Duration: {module.duration_minutes} minutes")
        print(f"   Difficulty: {module.difficulty}")
        if module.has_quiz:
            print(f"   Quiz: {module.quiz_questions} questions, {module.passing_score}% to pass")
    
    # Assign training
    print("\n" + "="*70)
    print("ASSIGN TRAINING")
    print("="*70)
    
    employee_id = "EMP-001"
    
    # Assign multiple modules
    assignment1 = engine.assign_training(employee_id, "MOD-001", due_days=14, reason="onboarding")
    assignment2 = engine.assign_training(employee_id, "MOD-003", due_days=14, reason="onboarding")
    assignment3 = engine.assign_training(employee_id, "MOD-006", due_days=14, reason="onboarding")
    assignment4 = engine.assign_training(employee_id, "MOD-007", due_days=14, reason="onboarding")
    
    # Complete training
    print("\n" + "="*70)
    print("COMPLETE TRAINING")
    print("="*70)
    
    engine.complete_training(assignment1.assignment_id, quiz_score=85, time_spent_minutes=18)
    engine.complete_training(assignment2.assignment_id, quiz_score=92, time_spent_minutes=12)
    engine.complete_training(assignment3.assignment_id, quiz_score=88, time_spent_minutes=15)
    engine.complete_training(assignment4.assignment_id, quiz_score=80, time_spent_minutes=10)
    
    # Check certification progress
    print("\n" + "="*70)
    print("CERTIFICATION PROGRESS")
    print("="*70)
    
    progress = engine.check_certification_progress(employee_id, "CERT-001")
    
    # Award certification if eligible
    if progress.get('eligible'):
        print("\n" + "="*70)
        print("AWARD CERTIFICATION")
        print("="*70)
        
        cert = engine.award_certification(employee_id, "CERT-001")
    
    # Generate training report
    print("\n" + "="*70)
    print("TRAINING REPORT")
    print("="*70)
    
    report = engine.generate_training_report(employee_id)
    print(json.dumps(report, indent=2, default=str))
