import gradio as gr
import os
from typing import Dict, List, Optional
import json
from datetime import datetime

# Import custom modules
from modules.career_roadmap_engine import CareerRoadmapEngine
from modules.job_scraper import JobScraper
from modules.skills_matcher import SkillsMatcher
from modules.application_assistant import ApplicationAssistant
from modules.user_database import UserDatabase
from modules.config_manager import ConfigManager

# Import AI modules
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Initialize modules
config = ConfigManager()
career_engine = CareerRoadmapEngine()
job_scraper = JobScraper()
skills_matcher = SkillsMatcher()
app_assistant = ApplicationAssistant()
user_db = UserDatabase()

# Initialize AI model
os.environ["OPENAI_API_KEY"] = config.get('api_keys.openai', '')
llm = ChatOpenAI(model_name="gpt-4o")

# Session management
store = {}
current_user = {"id": None, "username": None}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# User Authentication Functions
def login_user(username: str, email: str):
    if not username or not email:
        return "Please provide both username and email", None
    
    user = user_db.get_user(username=username)
    if not user:
        # Create new user
        user_id = user_db.create_user(username, email)
        user = user_db.get_user(user_id=user_id)
    
    current_user["id"] = user["id"]
    current_user["username"] = user["username"]
    
    return f"Welcome, {username}!", user

def get_user_profile():
    if not current_user["id"]:
        return None
    return user_db.get_profile(current_user["id"])

# Career Roadmap Functions
def generate_career_roadmap(name: str, experience_years: int, current_role: str, 
                           target_role: str, skills: str, interests: str, timeline: str):
    if not all([name, current_role, target_role]):
        return "Please fill in all required fields", None, None
    
    # Parse skills
    skills_list = [s.strip() for s in skills.split(',') if s.strip()]
    
    # Create user profile
    user_profile = {
        'name': name,
        'experience_years': experience_years,
        'current_role': current_role,
        'target_role': target_role,
        'skills': skills_list,
        'interests': interests,
        'timeline': timeline
    }
    
    # Save to database if logged in
    if current_user["id"]:
        user_db.update_profile(current_user["id"], user_profile)
    
    # Generate roadmap
    roadmap = career_engine.generate_roadmap(user_profile)
    
    # Format roadmap for display
    roadmap_display = format_roadmap_display(roadmap)
    
    # Generate milestones chart
    milestones_chart = create_milestones_chart(roadmap['milestones'])
    
    # Get skill gap analysis
    gap_analysis = skills_matcher.analyze_skill_gaps(
        skills_list, 
        roadmap['gap_analysis']['required_skills']
    )
    
    return roadmap_display, milestones_chart, format_gap_analysis(gap_analysis)

def format_roadmap_display(roadmap: Dict) -> str:
    display = f"""
# Your Personalized Career Roadmap

## Current Position
- **Role:** {roadmap['current_position']['role']}
- **Level:** {roadmap['current_position']['level']}
- **Experience:** {roadmap['current_position']['experience']} years

## Target Position
- **Role:** {roadmap['target_position']['role']}
- **Level:** {roadmap['target_position']['level']}
- **Timeline:** {roadmap['target_position']['expected_timeline']}

## Learning Path
"""
    
    for phase in roadmap['learning_path']:
        display += f"\n### {phase['level']} ({phase['duration']})\n"
        display += f"**Expected Salary:** {phase['expected_salary']}\n\n"
        display += "**Skills to Learn:**\n"
        for skill in phase['skills_to_learn']:
            display += f"- {skill}\n"
        
        if phase['certifications']:
            display += "\n**Recommended Certifications:**\n"
            for cert in phase['certifications']:
                display += f"- {cert}\n"
        
        display += "\n**Projects to Complete:**\n"
        for project in phase['projects']:
            display += f"- {project}\n"
    
    return display

def create_milestones_chart(milestones: List[Dict]) -> str:
    chart = "## Career Milestones Timeline\n\n"
    for milestone in milestones:
        status = "✅" if milestone['completed'] else "⭕"
        chart += f"{status} **{milestone['description']}**\n"
        chart += f"   Target: {milestone['target_date']} | Level: {milestone['level']}\n\n"
    return chart

def format_gap_analysis(gap_analysis: Dict) -> str:
    display = f"""
## Skills Gap Analysis

**Current Coverage:** {gap_analysis['skill_coverage']}%

### Missing Skills (Priority Order)
"""
    
    for skill in gap_analysis['prioritized_skills'][:10]:
        display += f"- **{skill['skill']}** (Demand: {skill['demand']}, Difficulty: {skill['difficulty']})\n"
    
    display += "\n### Recommended Learning Plan\n"
    for item in gap_analysis['learning_plan'][:5]:
        display += f"\n**{item['order']}. {item['skill']}**\n"
        display += f"- Time: {item['time_estimate']}\n"
        display += f"- Project: {item['practice_project']}\n"
    
    display += f"\n**Estimated Total Time:** {gap_analysis['estimated_time']}"
    
    return display

# Job Search Functions
def search_and_match_jobs(job_title: str, location: str, skills: str, 
                         experience_level: str, min_salary: int, remote_only: bool):
    if not job_title:
        return "Please enter a job title", None
    
    # Parse skills
    skills_list = [s.strip() for s in skills.split(',') if s.strip()]
    
    # Search for jobs
    jobs = job_scraper.search_jobs(
        job_title=job_title,
        location=location,
        skills=skills_list,
        experience_level=experience_level,
        max_results=20
    )
    
    # Apply filters
    filters = {
        'min_salary': min_salary if min_salary > 0 else None,
        'remote_only': remote_only,
        'experience_level': experience_level if experience_level != "Any" else None
    }
    
    filtered_jobs = job_scraper.filter_jobs(jobs, filters)
    
    # Calculate match scores
    for job in filtered_jobs:
        match_result = skills_matcher.calculate_job_match_score(skills_list, job)
        job['match_score'] = match_result['score']
        job['match_category'] = match_result['category']
        job['match_details'] = match_result
    
    # Sort by match score
    filtered_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Format for display
    jobs_display = format_jobs_display(filtered_jobs)
    
    # Create match analysis
    match_analysis = create_match_analysis(filtered_jobs)
    
    return jobs_display, match_analysis

def format_jobs_display(jobs: List[Dict]) -> str:
    if not jobs:
        return "No jobs found matching your criteria."
    
    display = "# Job Matches\n\n"
    
    for job in jobs[:10]:
        match_emoji = get_match_emoji(job['match_category'])
        display += f"## {match_emoji} {job['title']} at {job['company']}\n"
        display += f"**Match Score:** {job['match_score']}% ({job['match_category']})\n"
        display += f"**Location:** {job['location']} {'🏠 Remote' if job.get('remote') else ''}\n"
        display += f"**Salary:** {job['salary_range']}\n"
        display += f"**Posted:** {job['posted_date']}\n"
        display += f"**Level:** {job['experience_level']}\n\n"
        display += f"**Description:** {job['description'][:200]}...\n\n"
        
        if job.get('match_details'):
            display += "**Why you match:**\n"
            for rec in job['match_details']['recommendations'][:2]:
                display += f"- {rec}\n"
        
        display += f"\n[Apply Now]({job['url']})\n"
        display += "\n---\n\n"
    
    return display

def get_match_emoji(category: str) -> str:
    emojis = {
        "Perfect Match": "🎯",
        "Strong Match": "💪",
        "Good Match": "👍",
        "Possible Match": "🤔",
        "Stretch Opportunity": "🚀"
    }
    return emojis.get(category, "📋")

def create_match_analysis(jobs: List[Dict]) -> str:
    if not jobs:
        return "No jobs to analyze."
    
    perfect = len([j for j in jobs if j.get('match_category') == "Perfect Match"])
    strong = len([j for j in jobs if j.get('match_category') == "Strong Match"])
    good = len([j for j in jobs if j.get('match_category') == "Good Match"])
    
    analysis = f"""
# Match Analysis

## Summary
- 🎯 Perfect Matches: {perfect}
- 💪 Strong Matches: {strong}
- 👍 Good Matches: {good}
- Total Opportunities: {len(jobs)}

## Top Skills in Demand
"""
    
    # Analyze common required skills
    all_skills = []
    for job in jobs:
        all_skills.extend(job.get('skills_required', []))
    
    from collections import Counter
    skill_counts = Counter(all_skills)
    
    for skill, count in skill_counts.most_common(5):
        analysis += f"- {skill}: {count} jobs\n"
    
    return analysis

# Application Assistant Functions
def analyze_resume_for_job(resume_text: str, job_description: str):
    if not resume_text or not job_description:
        return "Please provide both resume and job description"
    
    # Analyze job description
    job_analysis = app_assistant.analyze_job_description(job_description)
    
    # Optimize resume
    optimization = app_assistant.optimize_resume(resume_text, job_analysis)
    
    # Format results
    results = f"""
# Resume Optimization Report

## ATS Score: {optimization['ats_score']}%

## Key Suggestions
"""
    
    for suggestion in optimization['suggestions']:
        priority_emoji = "🔴" if suggestion['priority'] == 'high' else "🟡"
        results += f"\n{priority_emoji} **{suggestion['type'].replace('_', ' ').title()}**\n"
        results += f"   {suggestion['message']}\n"
    
    if optimization['missing_keywords']:
        results += "\n## Missing Keywords\n"
        for keyword in optimization['missing_keywords'][:10]:
            results += f"- {keyword}\n"
    
    results += "\n## Recommended Resume Sections\n"
    for section in optimization['recommended_sections']:
        results += f"- {section}\n"
    
    return results

def generate_cover_letter_for_job(name: str, current_position: str, 
                                 target_position: str, company: str,
                                 skills: str, achievement: str,
                                 template_type: str):
    if not all([name, target_position, company]):
        return "Please fill in required fields"
    
    skills_list = [s.strip() for s in skills.split(',') if s.strip()]
    
    user_info = {
        'name': name,
        'current_position': current_position,
        'skills': skills_list,
        'achievement': achievement,
        'experience_years': '3',  # Could be dynamic
        'field': current_position.split()[-1] if current_position else 'technology',
        'key_skill': skills_list[0] if skills_list else 'technical expertise'
    }
    
    job_info = {
        'position': target_position,
        'company': company,
        'company_reason': 'of your innovative approach and industry leadership',
        'company_value': 'innovation and team collaboration',
        'company_goal': 'driving technological advancement'
    }
    
    cover_letter = app_assistant.generate_cover_letter(user_info, job_info, template_type)
    
    return cover_letter

def get_interview_prep(job_title: str, job_description: str, experience_level: str):
    if not job_title:
        return "Please provide a job title"
    
    questions = app_assistant.generate_interview_questions(
        job_title, job_description, experience_level
    )
    
    prep_guide = "# Interview Preparation Guide\n\n"
    
    prep_guide += "## Behavioral Questions\n"
    for q in questions['behavioral'][:5]:
        prep_guide += f"- {q}\n"
    
    prep_guide += "\n## Technical Questions\n"
    for q in questions['technical'][:5]:
        prep_guide += f"- {q}\n"
    
    prep_guide += "\n## Situational Questions\n"
    for q in questions['situational'][:5]:
        prep_guide += f"- {q}\n"
    
    prep_guide += "\n## Questions to Ask the Interviewer\n"
    for q in questions['questions_to_ask'][:5]:
        prep_guide += f"- {q}\n"
    
    return prep_guide

# AI Chat Function (Enhanced)
def ai_career_chat(message: str, history):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert career advisor AI assistant. You help users with:
        - Career planning and roadmaps
        - Job search strategies
        - Resume and cover letter optimization
        - Interview preparation
        - Skill development recommendations
        - Industry insights and trends
        
        Be supportive, practical, and provide actionable advice.
        If asked about specific features, guide them to use the appropriate tabs in the application."""),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    conversation_chain = RunnableWithMessageHistory(chain, get_session_history)
    
    response = conversation_chain.invoke(
        {"input": message},
        config={"configurable": {"session_id": "main"}}
    )
    
    return response.content

# Gradio Interface
def create_interface():
    with gr.Blocks(title="AI Career Assistant", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🚀 AI Career Assistant
        ### Your Comprehensive Career Development Platform
        """)
        
        with gr.Tab("🎯 Career Roadmap"):
            with gr.Row():
                with gr.Column():
                    roadmap_name = gr.Textbox(label="Your Name")
                    roadmap_experience = gr.Slider(label="Years of Experience", minimum=0, maximum=30, value=2)
                    roadmap_current = gr.Textbox(label="Current Role")
                    roadmap_target = gr.Textbox(label="Target Role")
                    roadmap_skills = gr.Textbox(label="Current Skills (comma-separated)", 
                                               placeholder="Python, JavaScript, SQL, Machine Learning...")
                    roadmap_interests = gr.Textbox(label="Professional Interests")
                    roadmap_timeline = gr.Radio(label="Target Timeline", 
                                              choices=["6 months", "1 year", "2 years", "3-5 years"],
                                              value="2 years")
                    roadmap_btn = gr.Button("Generate Roadmap", variant="primary")
                
                with gr.Column():
                    roadmap_output = gr.Markdown(label="Your Career Roadmap")
                    milestones_output = gr.Markdown(label="Milestones")
                    gap_analysis_output = gr.Markdown(label="Skills Gap Analysis")
            
            roadmap_btn.click(
                generate_career_roadmap,
                inputs=[roadmap_name, roadmap_experience, roadmap_current, 
                       roadmap_target, roadmap_skills, roadmap_interests, roadmap_timeline],
                outputs=[roadmap_output, milestones_output, gap_analysis_output]
            )
        
        with gr.Tab("💼 Job Search"):
            with gr.Row():
                with gr.Column():
                    job_title = gr.Textbox(label="Job Title")
                    job_location = gr.Textbox(label="Location", value="Remote")
                    job_skills = gr.Textbox(label="Your Skills (comma-separated)")
                    job_experience = gr.Dropdown(label="Experience Level",
                                                choices=["Any", "Junior", "Mid-Level", "Senior", "Lead"],
                                                value="Any")
                    job_min_salary = gr.Slider(label="Minimum Salary ($K)", 
                                              minimum=0, maximum=300, value=0, step=10)
                    job_remote = gr.Checkbox(label="Remote Only", value=False)
                    search_btn = gr.Button("Search & Match Jobs", variant="primary")
                
                with gr.Column():
                    jobs_output = gr.Markdown(label="Matched Jobs")
                    match_analysis = gr.Markdown(label="Match Analysis")
            
            search_btn.click(
                search_and_match_jobs,
                inputs=[job_title, job_location, job_skills, 
                       job_experience, job_min_salary, job_remote],
                outputs=[jobs_output, match_analysis]
            )
        
        with gr.Tab("📝 Application Helper"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Resume Optimizer")
                    resume_text = gr.Textbox(label="Paste Your Resume", lines=10)
                    job_desc = gr.Textbox(label="Paste Job Description", lines=10)
                    optimize_btn = gr.Button("Optimize Resume", variant="primary")
                    optimization_output = gr.Markdown(label="Optimization Suggestions")
                    
                    optimize_btn.click(
                        analyze_resume_for_job,
                        inputs=[resume_text, job_desc],
                        outputs=optimization_output
                    )
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Cover Letter Generator")
                    cl_name = gr.Textbox(label="Your Name")
                    cl_current = gr.Textbox(label="Current Position")
                    cl_target = gr.Textbox(label="Target Position")
                    cl_company = gr.Textbox(label="Company Name")
                    cl_skills = gr.Textbox(label="Key Skills (comma-separated)")
                    cl_achievement = gr.Textbox(label="Key Achievement", lines=2)
                    cl_template = gr.Radio(label="Template Type", 
                                         choices=["standard", "career_change", "entry_level"],
                                         value="standard")
                    generate_cl_btn = gr.Button("Generate Cover Letter", variant="primary")
                    
                with gr.Column():
                    cover_letter_output = gr.Textbox(label="Generated Cover Letter", lines=20)
                    
                    generate_cl_btn.click(
                        generate_cover_letter_for_job,
                        inputs=[cl_name, cl_current, cl_target, cl_company, 
                               cl_skills, cl_achievement, cl_template],
                        outputs=cover_letter_output
                    )
        
        with gr.Tab("🎤 Interview Prep"):
            with gr.Row():
                with gr.Column():
                    interview_job = gr.Textbox(label="Job Title")
                    interview_desc = gr.Textbox(label="Job Description (optional)", lines=5)
                    interview_level = gr.Dropdown(label="Experience Level",
                                                 choices=["Junior", "Mid-Level", "Senior"],
                                                 value="Mid-Level")
                    prep_btn = gr.Button("Generate Interview Prep", variant="primary")
                
                with gr.Column():
                    interview_output = gr.Markdown(label="Interview Preparation Guide")
            
            prep_btn.click(
                get_interview_prep,
                inputs=[interview_job, interview_desc, interview_level],
                outputs=interview_output
            )
        
        with gr.Tab("💬 AI Career Advisor"):
            gr.Markdown("""
            ### Chat with your AI Career Advisor
            Ask questions about career planning, job search strategies, skill development, or any career-related topic.
            """)
            
            chatbot = gr.Chatbot(height=400)
            msg = gr.Textbox(label="Your Message", placeholder="Ask me anything about your career...")
            clear = gr.Button("Clear Chat")
            
            def respond(message, chat_history):
                bot_message = ai_career_chat(message, chat_history)
                chat_history.append((message, bot_message))
                return "", chat_history
            
            msg.submit(respond, [msg, chatbot], [msg, chatbot])
            clear.click(lambda: None, None, chatbot, queue=False)
        
        with gr.Tab("👤 Profile"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Login/Register")
                    profile_username = gr.Textbox(label="Username")
                    profile_email = gr.Textbox(label="Email")
                    login_btn = gr.Button("Login/Register", variant="primary")
                    login_status = gr.Textbox(label="Status", interactive=False)
                    
                    login_btn.click(
                        login_user,
                        inputs=[profile_username, profile_email],
                        outputs=[login_status]
                    )
                
                with gr.Column():
                    gr.Markdown("### Your Progress")
                    gr.Markdown("""
                    - Track your career journey
                    - View saved job applications
                    - Monitor skill development
                    - Review interview history
                    
                    *Login to access your personalized dashboard*
                    """)
    
    return app

# Main execution
if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=False, debug=True)