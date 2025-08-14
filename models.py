from dataclasses import dataclass

@dataclass
class Job:
    id: int
    title: str
    company: str
    description: str

@dataclass
class Employee:
    id: int
    name: str
    skills: str
    experience: str
