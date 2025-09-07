"""
Career Assistant - Integrated Main Application

This is the main application file that provides a comprehensive Gradio interface
integrating all Career Assistant components:
- Career exploration and recommendations
- Student pathways and education planning  
- Career roadmaps and milestone tracking
- Job search and recommendations
- Skills assessment and gap analysis
- Progress tracking dashboard

Author: Career Assistant AI System
Version: 2.0.0
"""

import os
import sys
import json
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Import the integrated core system
from modules.career_assistant_core import CareerAssistantCore, UserProfile, CareerRecommendation

# Global variables
core_system = None
current_user_id = "demo_user"
session_state = {}


def initialize_system():
    """Initialize the Career Assistant Core system"""
    global core_system
    try:
        core_system = CareerAssistantCore()
        
        # Create a demo user if doesn't exist
        if not core_system.get_user_profile(current_user_id):
            core_system.create_user_profile(
                user_id=current_user_id,
                name="Demo User",
                education_level="Bachelor's Degree",
                current_skills=["Python", "Data Analysis", "Communication"],
                interests=["Technology", "Problem Solving", "Innovation"],
                career_goals=["Software Developer", "Data Scientist"],
                preferred_locations=["Remote", "San Francisco", "New York"]
            )
        
        return "✅ System initialized successfully!"
    except Exception as e:
        return f"❌ Error initializing system: {str(e)}"


def get_user_profile_info():
    """Get current user profile information"""
    global core_system, current_user_id
    
    try:
        if not core_system:
            return "System not initialized. Please initialize first."
        
        profile = core_system.get_user_profile(current_user_id)
        if not profile:
            return "No user profile found."
        
        info = f"""
**User Profile: {profile.name}**

📚 **Education Level:** {profile.education_level}
🎯 **Current Skills:** {', '.join(profile.current_skills)}
💡 **Interests:** {', '.join(profile.interests)}
🎯 **Career Goals:** {', '.join(profile.career_goals)}
📍 **Preferred Locations:** {', '.join(profile.preferred_locations)}

*Profile created: {profile.created_at.strftime('%Y-%m-%d %H:%M')}*
*Last updated: {profile.updated_at.strftime('%Y-%m-%d %H:%M')}*
        """
        
        return info
        
    except Exception as e:
        return f"Error loading profile: {str(e)}"


def update_user_profile(name: str, education: str, skills: str, interests: str, goals: str, locations: str):
    """Update user profile with new information"""
    global core_system, current_user_id
    
    try:
        if not core_system:
            return "System not initialized. Please initialize first."
        
        profile = core_system.get_user_profile(current_user_id)
        if not profile:
            return "No user profile found."
        
        # Update profile fields
        profile.name = name if name else profile.name
        profile.education_level = education if education else profile.education_level
        profile.current_skills = [s.strip() for s in skills.split(',')] if skills else profile.current_skills
        profile.interests = [i.strip() for i in interests.split(',')] if interests else profile.interests
        profile.career_goals = [g.strip() for g in goals.split(',')] if goals else profile.career_goals
        profile.preferred_locations = [l.strip() for l in locations.split(',')] if locations else profile.preferred_locations
        
        # Save updated profile
        success = core_system.save_user_profile(profile)
        
        if success:
            return "✅ Profile updated successfully!"
        else:
            return "❌ Error updating profile."
            
    except Exception as e:
        return f"Error updating profile: {str(e)}"


def get_career_recommendations(limit: int = 10):
    """Get personalized career recommendations"""
    global core_system, current_user_id
    
    try:
        if not core_system:
            return "System not initialized.", None
        
        recommendations = core_system.get_career_recommendations(current_user_id, limit=limit)
        
        if not recommendations:
            return "No recommendations found. Please check your profile.", None
        
        # Format recommendations for display
        rec_text = "## 🎯 Personalized Career Recommendations\\n\\n"
        rec_data = []
        
        for i, rec in enumerate(recommendations, 1):
            rec_text += f"""
**{i}. {rec.title}**
- **Match Score:** {rec.match_score:.1%}
- **Career Code:** {rec.career_code}
- **Salary Range:** ${rec.salary_range.get('min', 'N/A')} - ${rec.salary_range.get('max', 'N/A')}
- **Growth Outlook:** {rec.growth_outlook}
- **Key Skills:** {', '.join(rec.key_skills[:5])}
- **Reasoning:** {rec.reasoning}

---
            """
            
            rec_data.append({
                'Rank': i,
                'Title': rec.title,
                'Match Score': f"{rec.match_score:.1%}",
                'Growth Outlook': rec.growth_outlook,
                'Min Salary': rec.salary_range.get('min', 'N/A'),
                'Max Salary': rec.salary_range.get('max', 'N/A')
            })
        
        # Create DataFrame for table display
        df = pd.DataFrame(rec_data)
        
        return rec_text, df
        
    except Exception as e:
        return f"Error getting recommendations: {str(e)}", None


def search_careers(query: str):
    """Search for careers by keyword"""
    global core_system
    
    try:
        if not core_system:
            return "System not initialized.", None
        
        if not query:
            return "Please enter a search query.", None
        
        results = core_system.search_careers(query)
        
        if not results:
            return f"No careers found matching '{query}'.", None
        
        search_text = f"## 🔍 Search Results for '{query}'\\n\\n"
        search_data = []
        
        for result in results[:10]:  # Limit to 10 results
            search_text += f"""
**{result.get('title', 'Unknown Title')}**
- **Code:** {result.get('soc_code', 'N/A')}
- **Description:** {result.get('description', 'No description available')[:200]}...
- **Median Salary:** ${result.get('median_salary', 'N/A')}
- **Growth Rate:** {result.get('growth_rate', 'N/A')}

---
            """
            
            search_data.append({
                'Title': result.get('title', 'Unknown'),
                'Code': result.get('soc_code', 'N/A'),
                'Median Salary': result.get('median_salary', 'N/A'),
                'Growth Rate': result.get('growth_rate', 'N/A')
            })
        
        df = pd.DataFrame(search_data)
        return search_text, df
        
    except Exception as e:
        return f"Error searching careers: {str(e)}", None


def generate_student_pathway(target_career: str):
    """Generate education pathway for target career"""
    global core_system, current_user_id
    
    try:
        if not core_system:
            return "System not initialized."
        
        if not target_career:
            return "Please enter a target career."
        
        pathway = core_system.generate_student_pathway(current_user_id, target_career)
        
        if not pathway:
            return "Could not generate pathway. Please check the career name."
        
        pathway_text = f"## 🎓 Education Pathway: {target_career}\\n\\n"
        
        if 'pathway_steps' in pathway:
            pathway_text += "### Recommended Steps:\\n"
            for i, step in enumerate(pathway['pathway_steps'], 1):
                pathway_text += f"{i}. **{step.get('title', 'Unknown Step')}**\\n"
                pathway_text += f"   - Duration: {step.get('duration', 'N/A')}\\n"
                pathway_text += f"   - Description: {step.get('description', 'No description')}\\n\\n"
        
        if 'estimated_timeline' in pathway:
            pathway_text += f"**Total Estimated Time:** {pathway['estimated_timeline']}\\n\\n"
        
        if 'prerequisites' in pathway:
            pathway_text += "### Prerequisites:\\n"
            for prereq in pathway['prerequisites']:
                pathway_text += f"- {prereq}\\n"
        
        return pathway_text
        
    except Exception as e:
        return f"Error generating pathway: {str(e)}"


def generate_career_roadmap(target_career: str, timeline_months: int = 24):
    """Generate detailed career roadmap"""
    global core_system, current_user_id
    
    try:
        if not core_system:
            return "System not initialized."
        
        if not target_career:
            return "Please enter a target career."
        
        roadmap = core_system.generate_career_roadmap(current_user_id, target_career, timeline_months)
        
        if not roadmap:
            return "Could not generate roadmap. Please check the career name."
        
        roadmap_text = f"## 🗺️ Career Roadmap: {target_career}\\n\\n"
        roadmap_text += f"**Timeline:** {timeline_months} months\\n\\n"
        
        if 'phases' in roadmap:
            for phase in roadmap['phases']:
                roadmap_text += f"### {phase.get('title', 'Phase')} ({phase.get('duration', 'N/A')})\\n"
                roadmap_text += f"{phase.get('description', 'No description')}\\n\\n"
                
                if 'milestones' in phase:
                    roadmap_text += "**Milestones:**\\n"
                    for milestone in phase['milestones']:
                        roadmap_text += f"- {milestone.get('title', 'Unknown milestone')}\\n"
                
                roadmap_text += "\\n---\\n\\n"
        
        return roadmap_text
        
    except Exception as e:
        return f"Error generating roadmap: {str(e)}"


def search_jobs(query: str, location: str = "", job_type: str = ""):
    """Search for jobs"""
    global core_system
    
    try:
        if not core_system:
            return "System not initialized.", None
        
        if not query:
            return "Please enter a job search query.", None
        
        jobs = core_system.search_jobs(query, location, job_type, limit=20)
        
        if not jobs:
            return f"No jobs found for '{query}'.", None
        
        jobs_text = f"## 💼 Job Search Results: '{query}'\\n\\n"
        if location:
            jobs_text += f"**Location:** {location}\\n"
        if job_type:
            jobs_text += f"**Job Type:** {job_type}\\n\\n"
        
        jobs_data = []
        
        for job in jobs[:10]:  # Limit display to 10 jobs
            jobs_text += f"""
**{job.get('title', 'Unknown Title')}**
- **Company:** {job.get('company', 'Unknown Company')}
- **Location:** {job.get('location', 'Unknown Location')}
- **Salary:** {job.get('salary', 'Not specified')}
- **Type:** {job.get('job_type', 'Not specified')}
- **Posted:** {job.get('posted_date', 'Unknown')}

{job.get('description', 'No description available')[:200]}...

---
            """
            
            jobs_data.append({
                'Title': job.get('title', 'Unknown'),
                'Company': job.get('company', 'Unknown'),
                'Location': job.get('location', 'Unknown'),
                'Salary': job.get('salary', 'Not specified'),
                'Type': job.get('job_type', 'Not specified')
            })
        
        df = pd.DataFrame(jobs_data)
        return jobs_text, df
        
    except Exception as e:
        return f"Error searching jobs: {str(e)}", None


def get_job_recommendations():
    """Get job recommendations based on user profile"""
    global core_system, current_user_id
    
    try:
        if not core_system:
            return "System not initialized.", None
        
        jobs = core_system.get_job_recommendations(current_user_id, limit=15)
        
        if not jobs:
            return "No job recommendations available. Please update your profile.", None
        
        rec_text = "## 🎯 Personalized Job Recommendations\\n\\n"
        jobs_data = []
        
        for job in jobs:
            rec_text += f"""
**{job.get('title', 'Unknown Title')}**
- **Company:** {job.get('company', 'Unknown Company')}
- **Location:** {job.get('location', 'Unknown Location')}
- **Salary:** {job.get('salary', 'Not specified')}
- **Match Reason:** Based on your interests in {', '.join(job.get('match_reasons', ['your profile']))}

---
            """
            
            jobs_data.append({
                'Title': job.get('title', 'Unknown'),
                'Company': job.get('company', 'Unknown'),
                'Location': job.get('location', 'Unknown'),
                'Salary': job.get('salary', 'Not specified')
            })
        
        df = pd.DataFrame(jobs_data)
        return rec_text, df
        
    except Exception as e:
        return f"Error getting job recommendations: {str(e)}", None


def analyze_skill_gaps(target_career: str):
    """Analyze skill gaps for target career"""
    global core_system, current_user_id
    
    try:
        if not core_system:
            return "System not initialized.", None
        
        if not target_career:
            return "Please enter a target career.", None
        
        gaps = core_system.get_skill_gaps(current_user_id, target_career)
        
        if not gaps:
            return "Could not analyze skill gaps for this career.", None
        
        gap_text = f"## 📊 Skill Gap Analysis: {target_career}\\n\\n"
        gap_text += f"**Match Percentage:** {gaps.get('match_percentage', 0):.1f}%\\n\\n"
        
        if gaps.get('matching_skills'):
            gap_text += f"### ✅ Skills You Have ({len(gaps['matching_skills'])})\\n"
            for skill in gaps['matching_skills'][:10]:
                gap_text += f"- {skill}\\n"
            gap_text += "\\n"
        
        if gaps.get('missing_skills'):
            gap_text += f"### ❌ Skills to Develop ({len(gaps['missing_skills'])})\\n"
            for skill in gaps['missing_skills'][:10]:
                gap_text += f"- {skill}\\n"
            gap_text += "\\n"
        
        # Create visualization data
        viz_data = {
            'Skills You Have': len(gaps.get('matching_skills', [])),
            'Skills to Develop': len(gaps.get('missing_skills', []))
        }
        
        # Create pie chart
        fig = px.pie(
            values=list(viz_data.values()),
            names=list(viz_data.keys()),
            title=f"Skill Gap Analysis - {target_career}",
            color_discrete_sequence=['#2ecc71', '#e74c3c']
        )
        
        return gap_text, fig
        
    except Exception as e:
        return f"Error analyzing skill gaps: {str(e)}", None


def get_progress_dashboard():
    """Generate user progress dashboard"""
    global core_system, current_user_id
    
    try:
        if not core_system:
            return "System not initialized.", None, None
        
        analytics = core_system.generate_user_analytics(current_user_id)
        progress = core_system.get_user_progress(current_user_id)
        
        if not analytics:
            return "No analytics data available.", None, None
        
        # Progress summary text
        summary = f"""
## 📈 Progress Dashboard

### Profile Completeness
**{analytics.get('profile_completeness', 0):.1f}%** complete

### Activity Summary
- **Career Exploration Score:** {analytics.get('career_exploration_score', 0):.1f}/100
- **Recommendations Taken:** {analytics.get('recommendations_taken', 0)}
- **Active Roadmaps:** {analytics.get('active_roadmaps', 0)}
- **Skills Added:** {analytics.get('skill_development_progress', {}).get('skills_added', 0)}
- **Assessments Taken:** {analytics.get('skill_development_progress', {}).get('assessments_taken', 0)}

### Recent Activity
- Profile last updated: Recently
- Last career search: Today
- Last job search: Today
        """
        
        # Create progress chart
        progress_data = {
            'Metric': ['Profile Completeness', 'Career Exploration', 'Recommendations', 'Active Roadmaps'],
            'Value': [
                analytics.get('profile_completeness', 0),
                analytics.get('career_exploration_score', 0),
                analytics.get('recommendations_taken', 0) * 10,  # Scale for visualization
                analytics.get('active_roadmaps', 0) * 20  # Scale for visualization
            ]
        }
        
        progress_fig = px.bar(
            x=progress_data['Metric'],
            y=progress_data['Value'],
            title="Progress Overview",
            labels={'x': 'Metrics', 'y': 'Score/Count'},
            color=progress_data['Value'],
            color_continuous_scale='viridis'
        )
        
        # Create skills development chart
        skill_data = analytics.get('skill_development_progress', {})
        skills_fig = px.pie(
            values=[
                skill_data.get('skills_added', 0),
                skill_data.get('assessments_taken', 0) * 2,
                len(skill_data.get('improvement_areas', [])) * 3
            ],
            names=['Skills Added', 'Assessments', 'Improvement Areas'],
            title="Skill Development Breakdown"
        )
        
        return summary, progress_fig, skills_fig
        
    except Exception as e:
        return f"Error generating dashboard: {str(e)}", None, None


def export_user_data():
    """Export user data"""
    global core_system, current_user_id
    
    try:
        if not core_system:
            return "System not initialized."
        
        filepath = core_system.export_user_data(current_user_id, format="json")
        
        if filepath:
            return f"✅ Data exported successfully to: {filepath}"
        else:
            return "❌ Error exporting data."
            
    except Exception as e:
        return f"Error exporting data: {str(e)}"


def system_health_check():
    """Check system health"""
    global core_system
    
    try:
        if not core_system:
            return "System not initialized."
        
        health = core_system.health_check()
        
        health_text = f"""
## 🏥 System Health Check

**Status:** {health.get('status', 'Unknown').upper()}
**Timestamp:** {health.get('timestamp', 'N/A')}

### Module Status
"""
        
        modules = health.get('modules', {})
        for module, status in modules.items():
            status_icon = "✅" if status else "❌"
            health_text += f"- **{module}:** {status_icon}\\n"
        
        health_text += "\\n### Data Integrity\\n"
        data_integrity = health.get('data_integrity', {})
        for check, status in data_integrity.items():
            status_icon = "✅" if status else "❌"
            health_text += f"- **{check}:** {status_icon}\\n"
        
        health_text += "\\n### Performance\\n"
        performance = health.get('performance', {})
        health_text += f"- **Active Sessions:** {performance.get('active_sessions', 0)}\\n"
        health_text += f"- **System Uptime:** {performance.get('system_uptime', 'N/A')}\\n"
        
        return health_text
        
    except Exception as e:
        return f"Error checking system health: {str(e)}"


def create_gradio_interface():
    """Create the main Gradio interface"""
    
    with gr.Blocks(
        theme=gr.themes.Soft(),
        title="Career Assistant AI - Integrated Platform",
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .tab-nav {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        """
    ) as app:
        
        gr.Markdown("""
        # 🚀 Career Assistant AI - Integrated Platform
        
        **Your comprehensive career guidance system powered by AI**
        
        Explore careers, plan your education, build roadmaps, search jobs, and track your progress - all in one place!
        """)
        
        # System Status
        with gr.Row():
            with gr.Column():
                init_btn = gr.Button("🔄 Initialize System", variant="primary")
                init_output = gr.Textbox(label="System Status", lines=2)
                init_btn.click(initialize_system, outputs=init_output)
        
        # Main application tabs
        with gr.Tabs():
            
            # Tab 1: Profile & Dashboard
            with gr.Tab("👤 Profile & Dashboard") as profile_tab:
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📝 User Profile")
                        profile_info = gr.Textbox(
                            label="Current Profile", 
                            lines=15, 
                            interactive=False
                        )
                        profile_btn = gr.Button("🔄 Refresh Profile")
                        profile_btn.click(get_user_profile_info, outputs=profile_info)
                        
                        # Profile update form
                        with gr.Accordion("Edit Profile", open=False):
                            name_input = gr.Textbox(label="Name", placeholder="Enter your name")
                            education_input = gr.Dropdown(
                                label="Education Level",
                                choices=["High School", "Associate's Degree", "Bachelor's Degree", "Master's Degree", "Doctoral Degree", "Professional Certificate"]
                            )
                            skills_input = gr.Textbox(label="Skills (comma-separated)", placeholder="Python, Communication, Problem Solving")
                            interests_input = gr.Textbox(label="Interests (comma-separated)", placeholder="Technology, Innovation, Healthcare")
                            goals_input = gr.Textbox(label="Career Goals (comma-separated)", placeholder="Software Developer, Data Scientist")
                            locations_input = gr.Textbox(label="Preferred Locations (comma-separated)", placeholder="Remote, San Francisco, New York")
                            
                            update_btn = gr.Button("💾 Update Profile", variant="primary")
                            update_output = gr.Textbox(label="Update Status")
                            
                            update_btn.click(
                                update_user_profile,
                                inputs=[name_input, education_input, skills_input, interests_input, goals_input, locations_input],
                                outputs=update_output
                            )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 📊 Progress Dashboard")
                        dashboard_btn = gr.Button("📈 Generate Dashboard")
                        dashboard_output = gr.Textbox(label="Progress Summary", lines=15)
                        progress_chart = gr.Plot(label="Progress Overview")
                        skills_chart = gr.Plot(label="Skills Development")
                        
                        dashboard_btn.click(
                            get_progress_dashboard,
                            outputs=[dashboard_output, progress_chart, skills_chart]
                        )
            
            # Tab 2: Career Explorer
            with gr.Tab("🎯 Career Explorer") as career_tab:
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 🎯 Personalized Career Recommendations")
                        rec_limit = gr.Slider(minimum=5, maximum=20, value=10, label="Number of Recommendations")
                        get_rec_btn = gr.Button("🎯 Get Recommendations", variant="primary")
                        career_rec_output = gr.Textbox(label="Career Recommendations", lines=20)
                        career_rec_table = gr.DataFrame(label="Recommendations Table")
                        
                        get_rec_btn.click(
                            get_career_recommendations,
                            inputs=rec_limit,
                            outputs=[career_rec_output, career_rec_table]
                        )
                    
                    with gr.Column():
                        gr.Markdown("### 🔍 Career Search")
                        search_query = gr.Textbox(label="Search Careers", placeholder="e.g., software developer, nurse, teacher")
                        search_btn = gr.Button("🔍 Search Careers")
                        career_search_output = gr.Textbox(label="Search Results", lines=20)
                        career_search_table = gr.DataFrame(label="Search Results Table")
                        
                        search_btn.click(
                            search_careers,
                            inputs=search_query,
                            outputs=[career_search_output, career_search_table]
                        )
            
            # Tab 3: Student Pathways
            with gr.Tab("🎓 Student Pathways") as pathway_tab:
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 🎓 Education Pathway Generator")
                        pathway_career = gr.Textbox(
                            label="Target Career",
                            placeholder="e.g., Software Developer, Data Scientist, Nurse"
                        )
                        pathway_btn = gr.Button("🎓 Generate Pathway", variant="primary")
                        pathway_output = gr.Textbox(label="Education Pathway", lines=25)
                        
                        pathway_btn.click(
                            generate_student_pathway,
                            inputs=pathway_career,
                            outputs=pathway_output
                        )
                    
                    with gr.Column():
                        gr.Markdown("### 🗺️ Career Roadmap")
                        roadmap_career = gr.Textbox(
                            label="Target Career",
                            placeholder="e.g., Software Developer, Data Scientist"
                        )
                        roadmap_timeline = gr.Slider(
                            minimum=6, maximum=60, value=24,
                            label="Timeline (months)"
                        )
                        roadmap_btn = gr.Button("🗺️ Generate Roadmap", variant="primary")
                        roadmap_output = gr.Textbox(label="Career Roadmap", lines=25)
                        
                        roadmap_btn.click(
                            generate_career_roadmap,
                            inputs=[roadmap_career, roadmap_timeline],
                            outputs=roadmap_output
                        )
            
            # Tab 4: Job Search
            with gr.Tab("💼 Job Search") as job_tab:
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 💼 Job Search")
                        job_query = gr.Textbox(label="Job Title/Keywords", placeholder="e.g., Python Developer, Data Analyst")
                        job_location = gr.Textbox(label="Location (optional)", placeholder="e.g., San Francisco, Remote")
                        job_type = gr.Dropdown(
                            label="Job Type (optional)",
                            choices=["", "Full-time", "Part-time", "Contract", "Internship", "Remote"],
                            value=""
                        )
                        search_jobs_btn = gr.Button("🔍 Search Jobs", variant="primary")
                        job_search_output = gr.Textbox(label="Job Search Results", lines=20)
                        job_search_table = gr.DataFrame(label="Jobs Table")
                        
                        search_jobs_btn.click(
                            search_jobs,
                            inputs=[job_query, job_location, job_type],
                            outputs=[job_search_output, job_search_table]
                        )
                    
                    with gr.Column():
                        gr.Markdown("### 🎯 Personalized Job Recommendations")
                        job_rec_btn = gr.Button("🎯 Get Job Recommendations", variant="primary")
                        job_rec_output = gr.Textbox(label="Job Recommendations", lines=20)
                        job_rec_table = gr.DataFrame(label="Recommended Jobs Table")
                        
                        job_rec_btn.click(
                            get_job_recommendations,
                            outputs=[job_rec_output, job_rec_table]
                        )
            
            # Tab 5: Skills Analysis
            with gr.Tab("📊 Skills Analysis") as skills_tab:
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 📊 Skill Gap Analysis")
                        gap_career = gr.Textbox(
                            label="Target Career",
                            placeholder="e.g., Data Scientist, Web Developer"
                        )
                        gap_btn = gr.Button("📊 Analyze Skill Gaps", variant="primary")
                        gap_output = gr.Textbox(label="Skill Gap Analysis", lines=20)
                        gap_chart = gr.Plot(label="Skills Breakdown")
                        
                        gap_btn.click(
                            analyze_skill_gaps,
                            inputs=gap_career,
                            outputs=[gap_output, gap_chart]
                        )
                    
                    with gr.Column():
                        gr.Markdown("### 💾 Data Management")
                        
                        with gr.Group():
                            export_btn = gr.Button("📤 Export My Data", variant="secondary")
                            export_output = gr.Textbox(label="Export Status", lines=3)
                            export_btn.click(export_user_data, outputs=export_output)
                        
                        with gr.Group():
                            health_btn = gr.Button("🏥 System Health Check", variant="secondary")
                            health_output = gr.Textbox(label="System Health", lines=15)
                            health_btn.click(system_health_check, outputs=health_output)
        
        # Footer
        gr.Markdown("""
        ---
        
        ### 📚 How to Use This System:
        
        1. **Initialize** the system first using the button at the top
        2. **Update your profile** with your skills, interests, and goals
        3. **Explore careers** using recommendations or search
        4. **Plan your education** with pathway and roadmap generators
        5. **Search for jobs** or get personalized recommendations
        6. **Analyze skill gaps** to identify areas for improvement
        7. **Track your progress** using the dashboard
        
        **Note:** This is a comprehensive demo system. In production, user data would be securely stored and managed.
        
        *Career Assistant AI v2.0 - Integrated Platform*
        """)
    
    return app


if __name__ == "__main__":
    # Initialize and launch the application
    print("🚀 Starting Career Assistant AI - Integrated Platform...")
    print("🔧 Creating Gradio interface...")
    
    app = create_gradio_interface()
    
    print("✅ Interface created successfully!")
    print("🌐 Launching application...")
    
    # Launch with custom settings
    app.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,       # Default port
        share=False,            # Set to True to create public link
        debug=True,             # Enable debug mode
        show_error=True,        # Show detailed errors
        quiet=False,            # Show startup logs
        inbrowser=True          # Open browser automatically
    )