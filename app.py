from flask import Flask, render_template, session, redirect, url_for, request
from models import Job, Employee
from dataclasses import asdict
import json
import os

app = Flask(__name__)
app.secret_key = "dev"

DATA_FILE = "data.json"


def load_data():
    """Load persisted jobs, employees and swipe data."""
    global jobs, employees, job_likes, job_dislikes, employee_likes, employee_dislikes, matches
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            data = json.load(f)
        jobs = [Job(**j) for j in data.get("jobs", [])]
        employees = [Employee(**e) for e in data.get("employees", [])]
        likes = data.get("likes", {})
        job_likes = {int(k): set(v) for k, v in likes.get("job_likes", {}).items()}
        job_dislikes = {int(k): set(v) for k, v in likes.get("job_dislikes", {}).items()}
        employee_likes = {int(k): set(v) for k, v in likes.get("employee_likes", {}).items()}
        employee_dislikes = {int(k): set(v) for k, v in likes.get("employee_dislikes", {}).items()}
        matches = set(tuple(m) for m in data.get("matches", []))
    else:
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

        job_likes = {}
        job_dislikes = {}
        employee_likes = {}
        employee_dislikes = {}
        matches = set()
        save_data()


def save_data():
    data = {
        "jobs": [asdict(j) for j in jobs],
        "employees": [asdict(e) for e in employees],
        "likes": {
            "job_likes": {k: list(v) for k, v in job_likes.items()},
            "job_dislikes": {k: list(v) for k, v in job_dislikes.items()},
            "employee_likes": {k: list(v) for k, v in employee_likes.items()},
            "employee_dislikes": {k: list(v) for k, v in employee_dislikes.items()},
        },
        "matches": [list(m) for m in matches],
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


# initialise data
load_data()

@app.route("/")
def index():
    return render_template("index.html", jobs=jobs, employees=employees)


@app.route("/create_job", methods=["POST"])
def create_job():
    next_id = max([j.id for j in jobs], default=0) + 1
    job = Job(
        next_id,
        request.form.get("title"),
        request.form.get("company"),
        request.form.get("description"),
    )
    jobs.append(job)
    session["my_job_id"] = job.id
    session["candidate_index"] = 0
    session.pop("my_employee_id", None)
    save_data()
    return redirect(url_for("swipe_candidates"))


@app.route("/create_employee", methods=["POST"])
def create_employee():
    next_id = max([e.id for e in employees], default=0) + 1
    employee = Employee(
        next_id,
        request.form.get("name"),
        request.form.get("skills"),
        request.form.get("experience"),
    )
    employees.append(employee)
    session["my_employee_id"] = employee.id
    session["job_index"] = 0
    session.pop("my_job_id", None)
    save_data()
    return redirect(url_for("swipe_jobs"))


@app.route("/login_job/<int:job_id>")
def login_job(job_id):
    session["my_job_id"] = job_id
    session["candidate_index"] = 0
    session.pop("my_employee_id", None)
    return redirect(url_for("swipe_candidates"))


@app.route("/login_employee/<int:employee_id>")
def login_employee(employee_id):
    session["my_employee_id"] = employee_id
    session["job_index"] = 0
    session.pop("my_job_id", None)
    return redirect(url_for("swipe_jobs"))

@app.route("/jobs")
def swipe_jobs():
    if "my_employee_id" not in session:
        return redirect(url_for("index"))
    emp_id = session["my_employee_id"]
    liked = employee_likes.get(emp_id, set())
    disliked = employee_dislikes.get(emp_id, set())
    available_jobs = [j for j in jobs if j.id not in liked and j.id not in disliked]
    index = session.get("job_index", 0)
    if index >= len(available_jobs):
        return render_template("done.html", target="jobs", employee=_get_employee(emp_id))
    job = available_jobs[index]
    return render_template("job.html", job=job, employee=_get_employee(emp_id))

@app.route("/jobs/<action>", methods=["POST"])
def handle_job_action(action):
    if "my_employee_id" not in session:
        return redirect(url_for("index"))
    emp_id = session["my_employee_id"]
    liked = employee_likes.get(emp_id, set())
    disliked = employee_dislikes.get(emp_id, set())
    available_jobs = [j for j in jobs if j.id not in liked and j.id not in disliked]
    index = session.get("job_index", 0)
    if index >= len(available_jobs):
        return redirect(url_for("swipe_jobs"))
    job = available_jobs[index]
    job_id = job.id
    if action == "like":
        employee_likes.setdefault(emp_id, set()).add(job_id)
        if emp_id in job_likes.get(job_id, set()):
            matches.add((job_id, emp_id))
    else:
        employee_dislikes.setdefault(emp_id, set()).add(job_id)
    # Reset the job index.  The available_jobs list is rebuilt on each
    # request with already liked/disliked jobs filtered out, so simply
    # keeping the index the same (effectively zero) ensures we don't skip
    # the next unseen job.
    session["job_index"] = 0
    save_data()
    return redirect(url_for("swipe_jobs"))

@app.route("/candidates")
def swipe_candidates():
    if "my_job_id" not in session:
        return redirect(url_for("index"))
    job_id = session["my_job_id"]
    liked = job_likes.get(job_id, set())
    disliked = job_dislikes.get(job_id, set())
    available_candidates = [e for e in employees if e.id not in liked and e.id not in disliked]
    index = session.get("candidate_index", 0)
    if index >= len(available_candidates):
        return render_template("done.html", target="candidates", job=_get_job(job_id))
    candidate = available_candidates[index]
    return render_template("candidate.html", candidate=candidate, job=_get_job(job_id))

@app.route("/candidates/<action>", methods=["POST"])
def handle_candidate_action(action):
    if "my_job_id" not in session:
        return redirect(url_for("index"))
    job_id = session["my_job_id"]
    liked = job_likes.get(job_id, set())
    disliked = job_dislikes.get(job_id, set())
    available_candidates = [e for e in employees if e.id not in liked and e.id not in disliked]
    index = session.get("candidate_index", 0)
    if index >= len(available_candidates):
        return redirect(url_for("swipe_candidates"))
    candidate = available_candidates[index]
    emp_id = candidate.id
    if action == "like":
        job_likes.setdefault(job_id, set()).add(emp_id)
        if job_id in employee_likes.get(emp_id, set()):
            matches.add((job_id, emp_id))
    else:
        job_dislikes.setdefault(job_id, set()).add(emp_id)
    # Similar to job swiping above, reset the candidate index so that after
    # removing the current candidate from the available list we present the
    # next unseen candidate instead of skipping ahead.
    session["candidate_index"] = 0
    save_data()
    return redirect(url_for("swipe_candidates"))


# Provide a consistent endpoint name so url_for('matches') works
# even though there's a global 'matches' set in this module.
@app.route("/matches", endpoint="matches")
def matches_view():
    if "my_job_id" in session:
        job_id = session["my_job_id"]
        matched_emp_ids = [e for j, e in matches if j == job_id]
        matched_emps = [e for e in employees if e.id in matched_emp_ids]
        return render_template("matches.html", my_job=_get_job(job_id), matches=matched_emps)
    if "my_employee_id" in session:
        emp_id = session["my_employee_id"]
        matched_job_ids = [j for j, e in matches if e == emp_id]
        matched_jobs = [j for j in jobs if j.id in matched_job_ids]
        return render_template("matches.html", my_employee=_get_employee(emp_id), matches=matched_jobs)
    return redirect(url_for("index"))


def _get_job(job_id):
    return next((j for j in jobs if j.id == job_id), None)


def _get_employee(emp_id):
    return next((e for e in employees if e.id == emp_id), None)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
