"""
Milestone Tracker

A comprehensive module for tracking career roadmap progress, milestone completion,
skill acquisition, and providing recommendations for next steps. Includes
visualization data for progress tracking dashboards.

Features:
- Milestone completion tracking with timestamps
- Skill acquisition progress monitoring
- Progress visualization data generation
- Intelligent next-step recommendations
- Performance analytics and insights
- Achievement badges and rewards system
- Progress sharing and export capabilities

Author: AI Career Assistant
Created: September 2025
"""

import json
import os
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta, date
import logging
import math
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MilestoneStatus(Enum):
    """Milestone completion status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class SkillLevel(Enum):
    """Skill proficiency levels"""
    NOVICE = "novice"          # 0-25%
    BEGINNER = "beginner"      # 25-50%
    INTERMEDIATE = "intermediate"  # 50-75%
    ADVANCED = "advanced"      # 75-90%
    EXPERT = "expert"          # 90-100%


class ProgressMetric(Enum):
    """Types of progress metrics"""
    COMPLETION_RATE = "completion_rate"
    TIME_TO_COMPLETION = "time_to_completion"
    SKILL_ACQUISITION = "skill_acquisition"
    CERTIFICATION_PROGRESS = "certification_progress"
    PROJECT_COMPLETION = "project_completion"
    CAREER_ADVANCEMENT = "career_advancement"


@dataclass
class MilestoneProgress:
    """Tracks progress of a single milestone"""
    milestone_id: str
    milestone_title: str
    status: MilestoneStatus
    progress_percentage: float  # 0.0 to 100.0
    start_date: Optional[str]
    target_date: str
    completion_date: Optional[str]
    estimated_hours: int
    hours_spent: int
    prerequisites_met: List[str]
    blockers: List[str]
    notes: List[str]
    attachments: List[str]  # File paths or URLs
    last_updated: str


@dataclass
class SkillProgress:
    """Tracks progress of skill development"""
    skill_name: str
    current_level: SkillLevel
    target_level: SkillLevel
    progress_percentage: float
    learning_resources: List[str]
    practice_hours: int
    assessments_completed: List[str]
    projects_applied: List[str]
    certifications_earned: List[str]
    last_assessment_date: Optional[str]
    next_milestone: Optional[str]
    improvement_rate: float  # Skills gained per month


@dataclass
class Achievement:
    """Represents an achievement or badge"""
    id: str
    title: str
    description: str
    badge_icon: str
    earned_date: str
    category: str  # "milestone", "skill", "project", "time", "streak"
    points: int
    rarity: str  # "common", "rare", "epic", "legendary"


@dataclass
class ProgressInsight:
    """Data-driven insight about progress"""
    insight_type: str
    title: str
    description: str
    recommendation: str
    urgency: str  # "low", "medium", "high", "critical"
    impact: str   # "low", "medium", "high"
    category: str
    data_points: List[Dict[str, any]]


@dataclass
class VisualizationData:
    """Data structure for progress visualizations"""
    chart_type: str  # "line", "bar", "pie", "radar", "timeline"
    title: str
    labels: List[str]
    datasets: List[Dict[str, any]]
    options: Dict[str, any]
    time_range: Optional[str]


@dataclass
class CareerProgressSnapshot:
    """Complete snapshot of career progress"""
    user_id: str
    roadmap_id: str
    career_field: str
    snapshot_date: str
    
    # Progress data
    milestones: List[MilestoneProgress]
    skills: List[SkillProgress]
    achievements: List[Achievement]
    
    # Analytics
    overall_progress: float  # 0.0 to 100.0
    weekly_progress: float
    monthly_progress: float
    streak_days: int
    
    # Insights and recommendations
    insights: List[ProgressInsight]
    next_actions: List[str]
    
    # Visualization data
    progress_charts: List[VisualizationData]
    
    # Metadata
    last_activity_date: str
    total_hours_invested: int


class MilestoneTracker:
    """Main class for tracking career roadmap progress"""
    
    def __init__(self, data_dir: str = None):
        """Initialize the milestone tracker"""
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'progress')
        
        self.data_dir = data_dir
        self.ensure_data_directory()
        
        # Progress storage
        self.user_progress = {}  # user_id -> CareerProgressSnapshot
        self.achievement_definitions = {}
        self.skill_assessments = {}
        
        # Load existing data
        self._load_progress_data()
        self._load_achievement_definitions()
    
    def ensure_data_directory(self) -> None:
        """Ensure progress data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'users'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'achievements'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'backups'), exist_ok=True)
    
    def _load_progress_data(self) -> None:
        """Load existing progress data"""
        try:
            users_dir = os.path.join(self.data_dir, 'users')
            if os.path.exists(users_dir):
                for filename in os.listdir(users_dir):
                    if filename.endswith('.json'):
                        user_id = filename.replace('.json', '')
                        file_path = os.path.join(users_dir, filename)
                        
                        with open(file_path, 'r') as f:
                            progress_data = json.load(f)
                            self.user_progress[user_id] = self._deserialize_progress(progress_data)
                
                logger.info(f"Loaded progress data for {len(self.user_progress)} users")
        
        except Exception as e:
            logger.error(f"Error loading progress data: {e}")
    
    def _load_achievement_definitions(self) -> None:
        """Load achievement definitions"""
        try:
            achievements_file = os.path.join(self.data_dir, 'achievements', 'definitions.json')
            if os.path.exists(achievements_file):
                with open(achievements_file, 'r') as f:
                    self.achievement_definitions = json.load(f)
            else:
                self._create_default_achievements()
        
        except Exception as e:
            logger.error(f"Error loading achievement definitions: {e}")
            self._create_default_achievements()
    
    def _create_default_achievements(self) -> None:
        """Create default achievement definitions"""
        self.achievement_definitions = {
            "first_milestone": {
                "title": "First Steps",
                "description": "Complete your first milestone",
                "category": "milestone",
                "points": 100,
                "rarity": "common"
            },
            "skill_master": {
                "title": "Skill Master",
                "description": "Reach advanced level in a skill",
                "category": "skill", 
                "points": 300,
                "rarity": "rare"
            },
            "week_streak": {
                "title": "Consistent Learner",
                "description": "Maintain 7-day learning streak",
                "category": "streak",
                "points": 200,
                "rarity": "common"
            },
            "project_pioneer": {
                "title": "Project Pioneer",
                "description": "Complete your first major project",
                "category": "project",
                "points": 250,
                "rarity": "common"
            }
        }
        
        # Save default achievements
        try:
            os.makedirs(os.path.join(self.data_dir, 'achievements'), exist_ok=True)
            with open(os.path.join(self.data_dir, 'achievements', 'definitions.json'), 'w') as f:
                json.dump(self.achievement_definitions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving default achievements: {e}")
    
    def start_tracking_roadmap(
        self, 
        user_id: str, 
        roadmap: any,  # CareerRoadmap object
        initial_skills: Dict[str, SkillLevel] = None
    ) -> bool:
        """Start tracking progress for a new roadmap"""
        try:
            initial_skills = initial_skills or {}
            
            # Initialize milestone progress
            milestones = []
            for milestone in roadmap.milestones:
                milestones.append(MilestoneProgress(
                    milestone_id=milestone.id,
                    milestone_title=milestone.title,
                    status=MilestoneStatus.NOT_STARTED,
                    progress_percentage=0.0,
                    start_date=None,
                    target_date=milestone.target_date,
                    completion_date=None,
                    estimated_hours=milestone.estimated_hours,
                    hours_spent=0,
                    prerequisites_met=[],
                    blockers=[],
                    notes=[],
                    attachments=[],
                    last_updated=datetime.now().isoformat()
                ))
            
            # Initialize skill progress
            skills = []
            all_skills = set()
            
            # Collect all skills from roadmap
            for year_skills in roadmap.skill_progression.values():
                all_skills.update(year_skills)
            
            for milestone in roadmap.milestones:
                all_skills.update(milestone.skills_gained)
            
            for skill in all_skills:
                current_level = initial_skills.get(skill, SkillLevel.NOVICE)
                skills.append(SkillProgress(
                    skill_name=skill,
                    current_level=current_level,
                    target_level=SkillLevel.ADVANCED,  # Default target
                    progress_percentage=self._skill_level_to_percentage(current_level),
                    learning_resources=[],
                    practice_hours=0,
                    assessments_completed=[],
                    projects_applied=[],
                    certifications_earned=[],
                    last_assessment_date=None,
                    next_milestone=None,
                    improvement_rate=0.0
                ))
            
            # Create initial progress snapshot
            snapshot = CareerProgressSnapshot(
                user_id=user_id,
                roadmap_id=getattr(roadmap, 'id', str(uuid.uuid4())),
                career_field=roadmap.career_field,
                snapshot_date=datetime.now().isoformat(),
                milestones=milestones,
                skills=skills,
                achievements=[],
                overall_progress=0.0,
                weekly_progress=0.0,
                monthly_progress=0.0,
                streak_days=0,
                insights=[],
                next_actions=self._generate_initial_next_actions(roadmap),
                progress_charts=[],
                last_activity_date=datetime.now().isoformat(),
                total_hours_invested=0
            )
            
            self.user_progress[user_id] = snapshot
            self._save_user_progress(user_id)
            
            logger.info(f"Started tracking roadmap for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting roadmap tracking: {e}")
            return False
    
    def update_milestone_progress(
        self, 
        user_id: str, 
        milestone_id: str,
        progress_percentage: float = None,
        status: MilestoneStatus = None,
        hours_spent: int = None,
        notes: str = None,
        attachments: List[str] = None
    ) -> bool:
        """Update progress on a specific milestone"""
        try:
            if user_id not in self.user_progress:
                logger.error(f"No progress data found for user {user_id}")
                return False
            
            snapshot = self.user_progress[user_id]
            milestone = None
            
            # Find the milestone
            for m in snapshot.milestones:
                if m.milestone_id == milestone_id:
                    milestone = m
                    break
            
            if not milestone:
                logger.error(f"Milestone {milestone_id} not found for user {user_id}")
                return False
            
            # Update milestone data
            if progress_percentage is not None:
                milestone.progress_percentage = max(0.0, min(100.0, progress_percentage))
                
                # Auto-update status based on progress
                if milestone.progress_percentage == 100.0:
                    milestone.status = MilestoneStatus.COMPLETED
                    milestone.completion_date = datetime.now().isoformat()
                elif milestone.progress_percentage > 0:
                    if milestone.status == MilestoneStatus.NOT_STARTED:
                        milestone.status = MilestoneStatus.IN_PROGRESS
                        milestone.start_date = datetime.now().isoformat()
            
            if status is not None:
                milestone.status = status
                if status == MilestoneStatus.COMPLETED and not milestone.completion_date:
                    milestone.completion_date = datetime.now().isoformat()
                    milestone.progress_percentage = 100.0
            
            if hours_spent is not None:
                milestone.hours_spent += hours_spent
                snapshot.total_hours_invested += hours_spent
            
            if notes:
                milestone.notes.append({
                    "date": datetime.now().isoformat(),
                    "note": notes
                })
            
            if attachments:
                milestone.attachments.extend(attachments)
            
            milestone.last_updated = datetime.now().isoformat()
            snapshot.last_activity_date = datetime.now().isoformat()
            
            # Update overall progress and check for achievements
            self._recalculate_overall_progress(user_id)
            self._check_achievements(user_id, milestone_id)
            self._update_insights(user_id)
            
            # Save changes
            self._save_user_progress(user_id)
            
            logger.info(f"Updated milestone {milestone_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating milestone progress: {e}")
            return False
    
    def update_skill_progress(
        self,
        user_id: str,
        skill_name: str,
        new_level: SkillLevel = None,
        practice_hours: int = None,
        assessment_completed: str = None,
        project_applied: str = None,
        certification_earned: str = None
    ) -> bool:
        """Update progress on skill development"""
        try:
            if user_id not in self.user_progress:
                logger.error(f"No progress data found for user {user_id}")
                return False
            
            snapshot = self.user_progress[user_id]
            skill = None
            
            # Find the skill
            for s in snapshot.skills:
                if s.skill_name == skill_name:
                    skill = s
                    break
            
            if not skill:
                # Create new skill entry
                skill = SkillProgress(
                    skill_name=skill_name,
                    current_level=SkillLevel.NOVICE,
                    target_level=SkillLevel.ADVANCED,
                    progress_percentage=0.0,
                    learning_resources=[],
                    practice_hours=0,
                    assessments_completed=[],
                    projects_applied=[],
                    certifications_earned=[],
                    last_assessment_date=None,
                    next_milestone=None,
                    improvement_rate=0.0
                )
                snapshot.skills.append(skill)
            
            # Update skill data
            if new_level is not None:
                old_level = skill.current_level
                skill.current_level = new_level
                skill.progress_percentage = self._skill_level_to_percentage(new_level)
                skill.last_assessment_date = datetime.now().isoformat()
                
                # Calculate improvement rate
                if old_level != new_level:
                    self._update_skill_improvement_rate(skill)
            
            if practice_hours is not None:
                skill.practice_hours += practice_hours
                snapshot.total_hours_invested += practice_hours
            
            if assessment_completed:
                skill.assessments_completed.append({
                    "assessment": assessment_completed,
                    "date": datetime.now().isoformat()
                })
            
            if project_applied:
                skill.projects_applied.append({
                    "project": project_applied,
                    "date": datetime.now().isoformat()
                })
            
            if certification_earned:
                skill.certifications_earned.append({
                    "certification": certification_earned,
                    "date": datetime.now().isoformat()
                })
            
            snapshot.last_activity_date = datetime.now().isoformat()
            
            # Check for achievements and update insights
            self._check_skill_achievements(user_id, skill_name, new_level)
            self._update_insights(user_id)
            
            # Save changes
            self._save_user_progress(user_id)
            
            logger.info(f"Updated skill {skill_name} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating skill progress: {e}")
            return False
    
    def get_progress_summary(self, user_id: str) -> Optional[Dict[str, any]]:
        """Get a comprehensive progress summary"""
        if user_id not in self.user_progress:
            return None
        
        snapshot = self.user_progress[user_id]
        
        # Calculate statistics
        total_milestones = len(snapshot.milestones)
        completed_milestones = len([m for m in snapshot.milestones if m.status == MilestoneStatus.COMPLETED])
        in_progress_milestones = len([m for m in snapshot.milestones if m.status == MilestoneStatus.IN_PROGRESS])
        overdue_milestones = len([m for m in snapshot.milestones if m.status == MilestoneStatus.OVERDUE])
        
        # Skill statistics
        total_skills = len(snapshot.skills)
        advanced_skills = len([s for s in snapshot.skills if s.current_level in [SkillLevel.ADVANCED, SkillLevel.EXPERT]])
        
        # Recent activity
        recent_activity = self._get_recent_activity(user_id, days=7)
        
        return {
            "user_id": user_id,
            "career_field": snapshot.career_field,
            "overall_progress": snapshot.overall_progress,
            "milestones": {
                "total": total_milestones,
                "completed": completed_milestones,
                "in_progress": in_progress_milestones,
                "overdue": overdue_milestones,
                "completion_rate": (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
            },
            "skills": {
                "total": total_skills,
                "advanced": advanced_skills,
                "proficiency_rate": (advanced_skills / total_skills * 100) if total_skills > 0 else 0
            },
            "achievements": {
                "total": len(snapshot.achievements),
                "points": sum(a.points for a in snapshot.achievements)
            },
            "time_investment": {
                "total_hours": snapshot.total_hours_invested,
                "streak_days": snapshot.streak_days
            },
            "recent_activity": recent_activity,
            "next_actions": snapshot.next_actions[:5],  # Top 5 recommendations
            "insights_count": len(snapshot.insights),
            "last_updated": snapshot.last_activity_date
        }
    
    def generate_progress_visualizations(self, user_id: str) -> List[VisualizationData]:
        """Generate visualization data for progress tracking"""
        if user_id not in self.user_progress:
            return []
        
        snapshot = self.user_progress[user_id]
        visualizations = []
        
        # 1. Overall Progress Chart
        milestones_by_status = {}
        for milestone in snapshot.milestones:
            status = milestone.status.value
            milestones_by_status[status] = milestones_by_status.get(status, 0) + 1
        
        visualizations.append(VisualizationData(
            chart_type="pie",
            title="Milestone Status Distribution",
            labels=list(milestones_by_status.keys()),
            datasets=[{
                "data": list(milestones_by_status.values()),
                "backgroundColor": ["#10B981", "#F59E0B", "#6B7280", "#EF4444"]
            }],
            options={"responsive": True},
            time_range=None
        ))
        
        # 2. Skills Progress Radar Chart
        skill_names = [s.skill_name for s in snapshot.skills[:8]]  # Top 8 skills
        skill_percentages = [s.progress_percentage for s in snapshot.skills[:8]]
        
        visualizations.append(VisualizationData(
            chart_type="radar",
            title="Skills Proficiency",
            labels=skill_names,
            datasets=[{
                "label": "Current Level",
                "data": skill_percentages,
                "borderColor": "#3B82F6",
                "backgroundColor": "rgba(59, 130, 246, 0.2)"
            }],
            options={
                "scales": {
                    "r": {"beginAtZero": True, "max": 100}
                }
            },
            time_range=None
        ))
        
        # 3. Progress Timeline
        timeline_data = self._generate_timeline_data(user_id)
        if timeline_data:
            visualizations.append(VisualizationData(
                chart_type="line",
                title="Progress Over Time",
                labels=timeline_data["dates"],
                datasets=[{
                    "label": "Overall Progress",
                    "data": timeline_data["progress"],
                    "borderColor": "#10B981",
                    "tension": 0.1
                }],
                options={"responsive": True},
                time_range="30_days"
            ))
        
        # 4. Hours Investment Chart
        hours_by_category = self._calculate_hours_by_category(user_id)
        visualizations.append(VisualizationData(
            chart_type="bar",
            title="Time Investment by Category",
            labels=list(hours_by_category.keys()),
            datasets=[{
                "label": "Hours",
                "data": list(hours_by_category.values()),
                "backgroundColor": "#8B5CF6"
            }],
            options={"responsive": True},
            time_range=None
        ))
        
        return visualizations
    
    def get_next_recommendations(self, user_id: str, limit: int = 10) -> List[str]:
        """Get intelligent recommendations for next actions"""
        if user_id not in self.user_progress:
            return []
        
        snapshot = self.user_progress[user_id]
        recommendations = []
        
        # High priority: Overdue milestones
        overdue_milestones = [m for m in snapshot.milestones if m.status == MilestoneStatus.OVERDUE]
        for milestone in overdue_milestones[:3]:
            recommendations.append(f"🚨 Complete overdue milestone: {milestone.milestone_title}")
        
        # Medium priority: In-progress milestones
        in_progress = [m for m in snapshot.milestones if m.status == MilestoneStatus.IN_PROGRESS]
        for milestone in in_progress[:2]:
            recommendations.append(f"⏳ Continue working on: {milestone.milestone_title}")
        
        # Skills that need attention
        stagnant_skills = [s for s in snapshot.skills if s.improvement_rate == 0.0 and s.practice_hours == 0]
        for skill in stagnant_skills[:2]:
            recommendations.append(f"📚 Start practicing: {skill.skill_name}")
        
        # Achievements close to completion
        potential_achievements = self._identify_potential_achievements(user_id)
        for achievement in potential_achievements[:2]:
            recommendations.append(f"🏆 Close to earning: {achievement}")
        
        # Next logical milestones
        next_milestones = [m for m in snapshot.milestones if m.status == MilestoneStatus.NOT_STARTED]
        next_milestones.sort(key=lambda x: x.target_date)
        for milestone in next_milestones[:2]:
            recommendations.append(f"🎯 Start next milestone: {milestone.milestone_title}")
        
        return recommendations[:limit]
    
    def export_progress_report(self, user_id: str, filepath: str, format: str = "json") -> bool:
        """Export comprehensive progress report"""
        try:
            if user_id not in self.user_progress:
                logger.error(f"No progress data found for user {user_id}")
                return False
            
            snapshot = self.user_progress[user_id]
            
            if format.lower() == "json":
                # Create comprehensive report
                report = {
                    "report_generated": datetime.now().isoformat(),
                    "user_progress": asdict(snapshot),
                    "summary": self.get_progress_summary(user_id),
                    "visualizations": [asdict(viz) for viz in self.generate_progress_visualizations(user_id)],
                    "recommendations": self.get_next_recommendations(user_id)
                }
                
                with open(filepath, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                
                logger.info(f"Progress report exported to {filepath}")
                return True
            
        except Exception as e:
            logger.error(f"Error exporting progress report: {e}")
            return False
    
    # Helper methods
    def _skill_level_to_percentage(self, level: SkillLevel) -> float:
        """Convert skill level to percentage"""
        level_map = {
            SkillLevel.NOVICE: 12.5,
            SkillLevel.BEGINNER: 37.5,
            SkillLevel.INTERMEDIATE: 62.5,
            SkillLevel.ADVANCED: 87.5,
            SkillLevel.EXPERT: 100.0
        }
        return level_map.get(level, 0.0)
    
    def _recalculate_overall_progress(self, user_id: str) -> None:
        """Recalculate overall progress percentage"""
        snapshot = self.user_progress[user_id]
        
        if not snapshot.milestones:
            snapshot.overall_progress = 0.0
            return
        
        total_progress = sum(m.progress_percentage for m in snapshot.milestones)
        snapshot.overall_progress = total_progress / len(snapshot.milestones)
    
    def _check_achievements(self, user_id: str, milestone_id: str) -> None:
        """Check and award achievements"""
        snapshot = self.user_progress[user_id]
        milestone = next((m for m in snapshot.milestones if m.milestone_id == milestone_id), None)
        
        if not milestone:
            return
        
        # Check for first milestone completion
        if milestone.status == MilestoneStatus.COMPLETED:
            completed_count = len([m for m in snapshot.milestones if m.status == MilestoneStatus.COMPLETED])
            
            if completed_count == 1:
                self._award_achievement(user_id, "first_milestone")
    
    def _check_skill_achievements(self, user_id: str, skill_name: str, new_level: SkillLevel) -> None:
        """Check for skill-related achievements"""
        if new_level == SkillLevel.ADVANCED:
            self._award_achievement(user_id, "skill_master")
    
    def _award_achievement(self, user_id: str, achievement_key: str) -> None:
        """Award an achievement to a user"""
        if achievement_key not in self.achievement_definitions:
            return
        
        snapshot = self.user_progress[user_id]
        
        # Check if already awarded
        if any(a.id == achievement_key for a in snapshot.achievements):
            return
        
        achievement_def = self.achievement_definitions[achievement_key]
        achievement = Achievement(
            id=achievement_key,
            title=achievement_def["title"],
            description=achievement_def["description"],
            badge_icon=f"badge_{achievement_key}",
            earned_date=datetime.now().isoformat(),
            category=achievement_def["category"],
            points=achievement_def["points"],
            rarity=achievement_def["rarity"]
        )
        
        snapshot.achievements.append(achievement)
        logger.info(f"Awarded achievement '{achievement.title}' to user {user_id}")
    
    def _update_insights(self, user_id: str) -> None:
        """Generate and update progress insights"""
        snapshot = self.user_progress[user_id]
        insights = []
        
        # Check for stagnation
        overdue_count = len([m for m in snapshot.milestones if m.status == MilestoneStatus.OVERDUE])
        if overdue_count > 0:
            insights.append(ProgressInsight(
                insight_type="warning",
                title="Overdue Milestones",
                description=f"You have {overdue_count} overdue milestone(s)",
                recommendation="Focus on completing overdue items to get back on track",
                urgency="high",
                impact="high",
                category="milestone",
                data_points=[{"overdue_count": overdue_count}]
            ))
        
        # Check for skill gaps
        novice_skills = [s for s in snapshot.skills if s.current_level == SkillLevel.NOVICE]
        if len(novice_skills) > 3:
            insights.append(ProgressInsight(
                insight_type="recommendation",
                title="Skill Development Opportunity",
                description=f"You have {len(novice_skills)} skills at novice level",
                recommendation="Consider focusing on 2-3 key skills for faster progress",
                urgency="medium",
                impact="medium",
                category="skill",
                data_points=[{"novice_skills": len(novice_skills)}]
            ))
        
        snapshot.insights = insights
    
    def _generate_initial_next_actions(self, roadmap: any) -> List[str]:
        """Generate initial next actions for a new roadmap"""
        actions = []
        
        # First milestone
        if roadmap.milestones:
            first_milestone = roadmap.milestones[0]
            actions.append(f"Start working on: {first_milestone.title}")
        
        # First skills to develop
        if roadmap.skill_progression.get('1'):
            first_skills = roadmap.skill_progression['1'][:2]
            for skill in first_skills:
                actions.append(f"Begin learning: {skill}")
        
        # First project
        if roadmap.projects:
            first_project = roadmap.projects[0]
            actions.append(f"Start project: {first_project.name}")
        
        return actions
    
    def _get_recent_activity(self, user_id: str, days: int = 7) -> List[Dict[str, any]]:
        """Get recent activity for a user"""
        # This would normally query activity logs
        # For now, return basic activity based on last updates
        snapshot = self.user_progress[user_id]
        
        recent_activity = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for milestone in snapshot.milestones:
            if milestone.last_updated:
                update_date = datetime.fromisoformat(milestone.last_updated.replace('Z', '+00:00'))
                if update_date >= cutoff_date:
                    recent_activity.append({
                        "type": "milestone_update",
                        "title": milestone.milestone_title,
                        "date": milestone.last_updated
                    })
        
        return sorted(recent_activity, key=lambda x: x["date"], reverse=True)[:10]
    
    def _generate_timeline_data(self, user_id: str) -> Optional[Dict[str, List]]:
        """Generate timeline data for progress visualization"""
        # This would normally query historical progress data
        # For demonstration, return sample data
        return {
            "dates": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "progress": [10, 25, 45, 60]
        }
    
    def _calculate_hours_by_category(self, user_id: str) -> Dict[str, int]:
        """Calculate hours spent by category"""
        snapshot = self.user_progress[user_id]
        hours_by_category = {}
        
        for milestone in snapshot.milestones:
            category = milestone.milestone_title.split(' ')[0]  # Simple categorization
            hours_by_category[category] = hours_by_category.get(category, 0) + milestone.hours_spent
        
        for skill in snapshot.skills:
            hours_by_category["Skills"] = hours_by_category.get("Skills", 0) + skill.practice_hours
        
        return hours_by_category
    
    def _identify_potential_achievements(self, user_id: str) -> List[str]:
        """Identify achievements the user is close to earning"""
        # This would analyze user progress against achievement criteria
        return ["Complete 5 milestones", "Maintain 30-day streak"]
    
    def _update_skill_improvement_rate(self, skill: SkillProgress) -> None:
        """Update skill improvement rate calculation"""
        # Simple calculation - would be more sophisticated in real implementation
        skill.improvement_rate = 1.0  # 1 level per month
    
    def _deserialize_progress(self, data: Dict) -> CareerProgressSnapshot:
        """Deserialize progress data from JSON"""
        # Convert data back to CareerProgressSnapshot object
        # This is simplified - full implementation would handle all nested objects
        return CareerProgressSnapshot(**data)
    
    def _save_user_progress(self, user_id: str) -> None:
        """Save user progress to file"""
        try:
            snapshot = self.user_progress[user_id]
            file_path = os.path.join(self.data_dir, 'users', f'{user_id}.json')
            
            with open(file_path, 'w') as f:
                json.dump(asdict(snapshot), f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Error saving progress for user {user_id}: {e}")


# Example usage
if __name__ == "__main__":
    tracker = MilestoneTracker()
    
    # Example: Update milestone progress
    success = tracker.update_milestone_progress(
        user_id="test_user",
        milestone_id="skill_1",
        progress_percentage=75.0,
        status=MilestoneStatus.IN_PROGRESS,
        hours_spent=10,
        notes="Making good progress on Python fundamentals"
    )
    
    if success:
        # Get progress summary
        summary = tracker.get_progress_summary("test_user")
        if summary:
            print(json.dumps(summary, indent=2))