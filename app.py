from flask import Flask, render_template, request, jsonify
import warnings
warnings.filterwarnings('ignore')
from crewai import Agent,Task,Crew # type: ignore
import os, Secrets
from IPython.display import Markdown, display
os.environ['OPENAI_API_KEY'] = Secrets.OPENAI_API_KEY
os.environ["OPENAI_MODEL_NAME"] = Secrets.OPENAI_MODEL_NAME

planner = Agent(
    role = "Content Planner",
    goal = "Plan engaging and factually accurate content on {topic}",
    backstory = "you are working on planning a blog article"
    "about the topic:{topic}."
    "you collect information that helps the "
    "audience learn something "
    "and make informed decisions"
    "you work is the basis for "
    "the content writer to write an article on this topic.",
    allow_delegation = False,
    verbose = True
)


writer = Agent(
    role="Content Writer",
    goal="Write insightful and factually accurate "
         "opinion piece about the topic: {topic}",
    backstory="You're working on a writing "
              "a new opinion piece about the topic: {topic}. "
              "You base your writing on the work of "
              "the Content Planner, who provides an outline "
              "and relevant context about the topic. "
              "You follow the main objectives and "
              "direction of the outline, "
              "as provide by the Content Planner. "
              "You also provide objective and impartial insights "
              "and back them up with information "
              "provide by the Content Planner. "
              "You acknowledge in your opinion piece "
              "when your statements are opinions "
              "as opposed to objective statements.",
    allow_delegation=False,
    verbose=True
)


editor = Agent(
    role="Editor",
    goal="Edit a given blog post to align with "
         "the writing style of the organization. ",
    backstory="You are an editor who receives a blog post "
              "from the Content Writer. "
              "Your goal is to review the blog post "
              "to ensure that it follows journalistic best practices,"
              "provides balanced viewpoints "
              "when providing opinions or assertions, "
              "and also avoids major controversial topics "
              "or opinions when possible.",
    allow_delegation=False,
    verbose=True
)


plan = Task(
    description=(
        "1. Prioritize the latest trends, key players, "
            "and noteworthy news on {topic}.\n"
        "2. Identify the target audience, considering "
            "their interests and pain points.\n"
        "3. Develop a detailed content outline including "
            "an introduction, key points, and a call to action.\n"
        "4. Include SEO keywords and relevant data or sources."
    ),
    expected_output="A comprehensive content plan document "
        "with an outline, audience analysis, "
        "SEO keywords, and resources.",
    agent=planner,
)


write = Task(
    description=(
        "1. Use the content plan to craft a compelling "
            "blog post on {topic}.\n"
        "2. Incorporate SEO keywords naturally.\n"
		"3. Sections/Subtitles are properly named "
            "in an engaging manner.\n"
        "4. Ensure the post is structured with an "
            "engaging introduction, insightful body, "
            "and a summarizing conclusion.\n"
        "5. Proofread for grammatical errors and "
            "alignment with the brand's voice.\n"
    ),
    expected_output="A well-written blog post "
        "in markdown format, ready for publication, "
        "each section should have 2 or 3 paragraphs.",
    agent=writer,
)


edit = Task(

  description=("Proofread the given blog post for "
                 "grammatical errors and "
                 "alignment with the brand's voice."),
    expected_output="A well-written blog post in markdown format, "
                    "ready for publication, "
                    "each section should have 2 or 3 paragraphs.",
    agent=editor
)


crew = Crew(
    agents=[planner, writer, editor],
    tasks=[plan, write, edit],
    verbose=2
)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result_str = ""
    if request.method == "POST":
        topic = request.form["topic"]
        result = crew.kickoff(inputs={"topic": topic})
        result_str = str(result)
    
    return render_template("index.html", result_str=Markdown(result_str).data)

if __name__ == "__main__":
    app.run(debug=True)