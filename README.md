# AI Career Assistant Platform

A comprehensive AI-powered career development platform that provides personalized career roadmaps, job matching, and application assistance.

## Features

### 🎯 Career Roadmap Generator
- Personalized career progression paths from current to target role
- Skill gap analysis with prioritized learning plans
- Milestone tracking with timeline estimates
- Salary progression insights
- Project recommendations for portfolio building

### 💼 Smart Job Matching
- Real-time job scraping from multiple sources
- AI-powered job matching with compatibility scores
- Advanced filtering (salary, location, remote, experience)
- Skill-based recommendations
- Match analysis and insights

### 📝 Application Assistant
- Resume optimization for ATS compatibility
- Job description keyword analysis
- Cover letter generation (multiple templates)
- Interview preparation guides
- Application tracking system

### 🤖 AI Career Advisor
- Interactive chat with GPT-4 powered advisor
- Personalized career guidance
- Industry insights and trends
- Skill development recommendations

### 👤 User Profiles
- Persistent user data storage
- Progress tracking
- Saved jobs and applications
- Career journey history

## Tech Stack

- **Frontend**: Gradio 4.0+
- **AI/ML**: OpenAI GPT-4, LangChain
- **Backend**: Python 3.9+
- **Database**: SQLite/PostgreSQL
- **Web Scraping**: BeautifulSoup4, Selenium
- **Data Processing**: Pandas, NumPy, Scikit-learn

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rahulmehta25/AI-assistant-CSharpCorner.git
cd AI-assistant-CSharpCorner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the application:
```bash
python main.py
```

## Project Structure

```
AI-assistant-CSharpCorner/
├── main.py                    # Main application with Gradio interface
├── modules/
│   ├── career_roadmap_engine.py  # Career path generation
│   ├── job_scraper.py            # Job data aggregation
│   ├── skills_matcher.py         # Skill matching algorithms
│   ├── application_assistant.py  # Resume/cover letter tools
│   ├── user_database.py         # User data management
│   └── config_manager.py        # Configuration handling
├── data/
│   ├── careers/              # Career path definitions
│   ├── skills_db.json       # Skills database
│   └── cache/               # Cached job data
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## Key Modules

### CareerRoadmapEngine
Generates personalized career progression paths with:
- Level-based progression (Junior → Senior → Expert)
- Skill requirements and gap analysis
- Learning resource recommendations
- Timeline and salary estimates

### JobScraper
Aggregates job postings with:
- Multi-source job scraping
- Intelligent caching system
- Advanced filtering capabilities
- Real-time data updates

### SkillsMatcher
Provides intelligent matching with:
- Skill similarity algorithms
- Job compatibility scoring
- Gap analysis and recommendations
- Learning path generation

### ApplicationAssistant
Helps with job applications through:
- ATS-optimized resume suggestions
- Keyword extraction and matching
- Cover letter templates
- Interview question preparation

## Usage

1. **Career Roadmap**: Enter your current role, target role, and skills to get a personalized career path
2. **Job Search**: Search for jobs with advanced filters and see compatibility scores
3. **Application Helper**: Optimize your resume and generate cover letters for specific jobs
4. **Interview Prep**: Get customized interview questions based on the job role
5. **AI Advisor**: Chat with the AI for personalized career advice

## Future Enhancements

- Integration with LinkedIn, Indeed, and Glassdoor APIs
- Real-time job alerts and notifications
- Video interview practice with AI feedback
- Networking recommendations
- Salary negotiation assistant
- Portfolio showcase integration
- Peer mentoring connections

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License.

## Author

Rahul Mehta - [GitHub](https://github.com/rahulmehta25)

## Acknowledgments

- Originally developed for C# Corner platform
- Powered by OpenAI GPT-4 and LangChain
- Built with Gradio for the user interface
