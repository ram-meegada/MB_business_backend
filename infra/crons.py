from django_cron import Schedule, CronJobBase
import subprocess
from decouple import config
from django.utils import timezone
import os
from utils.s3Boto import save_file_to_s3


class SaveBackUpOfProdDbCron(CronJobBase):
    """
        Cron to get the backup of prod db
    """
    RUN_AT_TIMES = ['02:00', '18:00']
    RETRY_AFTER_FAILURE_MINS = 1
    MIN_NUM_FAILURES = 1

    schedule = Schedule(run_at_times=RUN_AT_TIMES, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = "SaveBackUpOfProdDbCron"

    def do(self):
        # shell_command = "pg_dump -h localhost -U your_pg_user -F c -f /tmp/backup.sql your_database_name"

        timestamp = timezone.localtime(timezone.now()).strftime('%Y-%d-%B-%H-%M')
        filename = f"prod_backup_{timestamp}.sql"
        local_path = f"/tmp/{filename}"
        S3_BACKUPS_LOCATION = f'prod-backups/{filename}'

        PG_HOST = config('DB_HOST')
        PG_USER = config('DB_USER')
        DB_NAME = config('DB_NAME')

        os.environ["PGPASSWORD"] = config('DB_PASSWORD')

        dump_cmd = ["pg_dump", "-h", PG_HOST, "-U", PG_USER, "-F", "c", "-f", local_path, DB_NAME]
        subprocess.run(dump_cmd, check=True)

        if os.path.exists(local_path):
            save_file_to_s3(local_path, S3_BACKUPS_LOCATION)
            os.remove(local_path)
        else:
            raise Exception('Local path not found')
