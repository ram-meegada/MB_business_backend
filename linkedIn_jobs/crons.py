from django_cron import CronJobBase, Schedule
from linkedIn_jobs.jobs_manager import JobsManager
from linkedIn_jobs.models import Job


class SaveLinkedInJobsCron(CronJobBase):
    """
        Cron to create orders for morning and evening
    """
    RUN_AT_TIMES = []
    RETRY_AFTER_FAILURE_MINS = 1
    MIN_NUM_FAILURES = 1

    schedule = Schedule(run_at_times=RUN_AT_TIMES, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = "SaveLinkedInJobsCron"

    def do(self):
        jobs_manager = JobsManager(source=Job.LINKEDIN)
        jobs_manager.start()
