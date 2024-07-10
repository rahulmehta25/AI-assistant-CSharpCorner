import gradio as gr
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import os

os.environ["OPENAI_API_KEY"] = ""
llm = ChatOpenAI(model_name="gpt-4o")

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def recommend_career(name, experience, skills, interests):
    if name and experience and skills and interests:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", f"""
                Tell the user their best career path given the following options. Give the output in one paragraph comprised of 5-10 sentences using plain text only.
                Provide the link as a hyperlink.
                If the user's information does not directly align with one of the options, let the user know there is no direct fit.
                ***options***
                    
                Career: "Machine Learning Engineer",
                Reason: With your background in Machine Learning with Python, you have the necessary skills to excel in this field. Machine learning engineers are in high demand, and this career offers numerous opportunities for growth and innovation.,
                Link: "[Machine Learning with Python](https://students.c-sharpcorner.com/home/course/chatgpt-masterclass/24)"
            
            
                Career: "AI Developer",
                Reason: Generative AI and Google Gemini Masterclass have provided you with a strong foundation in AI development. This role allows you to work on cutting-edge technologies and create intelligent systems.,
                Link: "[Generative AI: Getting Started](https://students.c-sharpcorner.com/home/course/generative-ai-getting-started/23)"
            
            
                Career: "Python Developer",
                Reason: Completing The Complete Python Course, Python Pandas, and Python NumPy for Data Science gives you a comprehensive understanding of Python, making you well-suited for a career as a Python Developer.,
                Link: "[The Complete Python Course](https://students.c-sharpcorner.com/home/course/the-complete-python-course/21)"
            
            
                Career": "Full Stack Web3 Developer",
                Reason": With your knowledge of Full Stack Web3 development and Getting Ready with REST APIs, you are equipped to build decentralized applications and contribute to the evolving Web3 landscape.,
                Link": "[Full Stack Web3 Developer](https://students.c-sharpcorner.com/home/course/full-stack-web3-developer/6)"
            
            
                Career: "Data Scientist",
                Reason: Courses like Machine Learning with Python and Python Pandas have provided you with essential data manipulation and analysis skills, which are crucial for a career in data science.,
                Link: "[Python Pandas](https://students.c-sharpcorner.com/home/course/python-pandas/19)"
            
            
                Career: "React Developer",
                Reason: React.js For Beginners and Angular 8 in 10 Days have equipped you with the skills to build dynamic and responsive web applications, making you a strong candidate for a React Developer role.,
                Link: "[React Developer](https://students.c-sharpcorner.com/home/course/react-developer/4)"
            
            
                Career: "Backend Developer",
                Reason: Your experience with Django in 20 Days and Mastering SQL makes you well-prepared for a backend developer role, where you can design and maintain server-side applications.,
                Link: "[Beginning with SQL Server](https://students.c-sharpcorner.com/home/course/beginning-with-sql-server/16)"
            
            
                Career: "Game Developer",
                Reason: Build a Unity Game in 1 Hr has provided you with the basics of game development, and with further practice, you can pursue a career in creating engaging and interactive games.,
                Link: "[Build a Unity Game in 1 Hr](https://students.c-sharpcorner.com/home/course/chatgpt-masterclass/24)"
            
            
                Career: "Cloud Engineer",
                Reason: Unveiling Cloud Basics has given you an introduction to cloud technologies, making you a good fit for roles that involve managing and deploying cloud-based solutions.,
                Link: "[Unveiling Cloud Basics](https://students.c-sharpcorner.com/home/course/unveiling-cloud-basics/10)"
            
            
                Career": "Database Administrator",
                Reason: The Ultimate MySQL Bootcamp and Beginning with SQL Server have equipped you with the knowledge to manage and maintain databases effectively, which is essential for a Database Administrator.,
                Link: "[The Ultimate MySQL Bootcamp](https://students.c-sharpcorner.com/home/course/the-ultimate-mysql-bootcamp/20)"
            
            
                Career: "Frontend Developer",
                Reason: With courses like React.js For Beginners and Angular 8 in 10 Days, you have the skills to build and maintain the front end of websites and applications.,
                Link: "[React Developer](https://students.c-sharpcorner.com/home/course/react-developer/4)"
            
            
                Career: "IoT Developer",
                Reason: Internet of Things in 21 Days has introduced you to the world of IoT, positioning you to work on innovative projects that connect devices and systems.,
                Link: "[Internet of Things in 21 Days](https://students.c-sharpcorner.com/home/course/unveiling-cloud-basics/10)"
            
            
                Career: "Software Engineer",
                Reason: Your comprehensive knowledge from courses like C# 7.0, C# 8.0, and ASP.NET MVC 5.0 prepares you for a broad range of software development projects.,
                Link: "[C# 7.0](https://students.c-sharpcorner.com/home/course/c-sharp-asynchronous-programming/3)"
            
            
                Career: "Technical Writer",
                Reason: With a broad understanding of multiple programming languages and tools from courses like Visual Studio Code and Introduction to MongoDB, you can excel in creating clear and concise technical documentation.,
                Link: "[Visual Studio Code](https://students.c-sharpcorner.com/home/course/chatgpt-masterclass/24)"
            
            
                Career: "Business Intelligence Developer",
                Reason: Crystal Reports Tutorials and SSRS in 1 Day have equipped you with the skills to develop and manage BI solutions, which are critical for data-driven decision making in businesses.,
                Link: "[Crystal Reports Tutorials](https://students.c-sharpcorner.com/home/course/chatgpt-masterclass/24)"
            
            
                Career: "Mobile App Developer",
                Reason: Flutter and Build Progressive Web Apps have provided you with the skills to create cross-platform mobile applications, making you a strong candidate for a Mobile App Developer role.,
                Link: "[Flutter](https://students.c-sharpcorner.com/home/course/flutter/24)"
                """) ,
                ("human", "{input}")
            ]
        )
        chain = prompt | llm
        conversation_chain = RunnableWithMessageHistory(chain, get_session_history)
        response = conversation_chain.invoke(
            {"input": f"My name is {name}. I have experience in {experience}, skills in {skills}, interests in {interests}"}, 
            config={"configurable": {"session_id": "1"}}
        )
        return response.content
    else:
        return "Please fill out all the fields."

iface = gr.Interface(
    fn=recommend_career,
    inputs=[
        gr.Textbox(label="What is your name"),
        gr.Textbox(label="What is your experience"),
        gr.Textbox(label="What are your skills"),
        gr.Textbox(label="What are your professional interests"),
    ],
    outputs=gr.Markdown(),
    title="Career Recommendation System",
    description="Provide your name, experience, skills, and interests to receive a career recommendation.",
    allow_flagging=False
)

iface.launch()
