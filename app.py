from flask import Flask, render_template, session, redirect, url_for
from models import Job, Employee

app = Flask(__name__)
app.secret_key = "dev"

jobs = [
    Job(1, "Backend Developer", "TechCorp", "Work on APIs and services."),
    Job(2, "Frontend Developer", "Webify", "Build engaging user interfaces."),
    Job(3, "Data Scientist", "DataMagic", "Analyze and model complex datasets."),
    Job(4, "DevOps Engineer", "CloudNine", "Manage infrastructure and deployments."),
    Job(5, "Product Manager", "InnoSoft", "Guide product vision and execution."),
]

employees = [
    Employee(1, "Alice", "Python, Flask", "3 years at StartUp"),
    Employee(2, "Bob", "JavaScript, React", "2 years freelancing"),
    Employee(3, "Carol", "Data analysis, SQL", "4 years at FinanceCo"),
    Employee(4, "Dave", "DevOps, Docker", "5 years at CloudCo"),
    Employee(5, "Eve", "Product strategy, Agile", "6 years at BigCorp"),
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/jobs")
def swipe_jobs():
    index = session.get("job_index", 0)
    if index >= len(jobs):
        return render_template("done.html", target="jobs")
    job = jobs[index]
    return render_template("job.html", job=job)

@app.route("/jobs/<action>", methods=["POST"])
def handle_job_action(action):
    index = session.get("job_index", 0)
    session["job_index"] = index + 1
    return redirect(url_for("swipe_jobs"))

@app.route("/candidates")
def swipe_candidates():
    index = session.get("candidate_index", 0)
    if index >= len(employees):
        return render_template("done.html", target="candidates")
    candidate = employees[index]
    return render_template("candidate.html", candidate=candidate)

@app.route("/candidates/<action>", methods=["POST"])
def handle_candidate_action(action):
    index = session.get("candidate_index", 0)
    session["candidate_index"] = index + 1
    return redirect(url_for("swipe_candidates"))

if __name__ == "__main__":
    app.run(debug=True)
