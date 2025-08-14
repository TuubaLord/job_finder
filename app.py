from flask import Flask, render_template, session, redirect, url_for, request
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


@app.route("/create_job", methods=["POST"])
def create_job():
    job_data = {
        "title": request.form.get("title"),
        "company": request.form.get("company"),
        "description": request.form.get("description"),
    }
    session["my_job"] = job_data
    session["candidate_index"] = 0
    return redirect(url_for("swipe_candidates"))


@app.route("/create_employee", methods=["POST"])
def create_employee():
    employee_data = {
        "name": request.form.get("name"),
        "skills": request.form.get("skills"),
        "experience": request.form.get("experience"),
    }
    session["my_employee"] = employee_data
    session["job_index"] = 0
    return redirect(url_for("swipe_jobs"))

@app.route("/jobs")
def swipe_jobs():
    if "my_employee" not in session:
        return redirect(url_for("index"))
    index = session.get("job_index", 0)
    if index >= len(jobs):
        return render_template("done.html", target="jobs")
    job = jobs[index]
    return render_template("job.html", job=job, employee=session.get("my_employee"))

@app.route("/jobs/<action>", methods=["POST"])
def handle_job_action(action):
    index = session.get("job_index", 0)
    session["job_index"] = index + 1
    return redirect(url_for("swipe_jobs"))

@app.route("/candidates")
def swipe_candidates():
    if "my_job" not in session:
        return redirect(url_for("index"))
    index = session.get("candidate_index", 0)
    if index >= len(employees):
        return render_template("done.html", target="candidates")
    candidate = employees[index]
    return render_template(
        "candidate.html", candidate=candidate, job=session.get("my_job")
    )

@app.route("/candidates/<action>", methods=["POST"])
def handle_candidate_action(action):
    index = session.get("candidate_index", 0)
    session["candidate_index"] = index + 1
    return redirect(url_for("swipe_candidates"))

if __name__ == "__main__":
    app.run(debug=True, port=8000)
