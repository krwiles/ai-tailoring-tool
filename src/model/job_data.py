from dataclasses import dataclass


@dataclass
class JobData:
    job_title: str
    company: str
    location: str
    job_description: str

