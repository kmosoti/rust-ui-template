"""Summarize a GitHub Actions jobs API JSON response; no network credentials needed.

Example: gh api repos/OWNER/REPO/actions/runs/RUN/jobs | python3 scripts/ci_timings.py
"""
from datetime import datetime
import json
import sys


def seconds(start, end):
    if not start or not end:
        return None
    return int((datetime.fromisoformat(end.replace('Z', '+00:00')) - datetime.fromisoformat(start.replace('Z', '+00:00'))).total_seconds())


def main():
    data = json.load(sys.stdin)
    jobs = data.get('jobs', [data])
    print('| Job / step | Seconds | Result |\n| --- | ---: | --- |')
    for job in jobs:
        print(f'| {job.get("name", "job")} total | {seconds(job.get("started_at"), job.get("completed_at"))} | {job.get("conclusion")} |')
        for step in job.get('steps', []):
            print(f'| {step["name"]} | {seconds(step.get("started_at"), step.get("completed_at"))} | {step.get("conclusion")} |')


if __name__ == '__main__':
    main()
