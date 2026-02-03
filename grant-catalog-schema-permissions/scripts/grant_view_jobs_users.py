from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

w = WorkspaceClient()

all_jobs = [job.job_id for job in w.jobs.list()]

group = "users"
permission = "CAN_VIEW"


def grants_job(job_id, group="users", permission="CAN_VIEW"):
    print(job_id, group)
    try:
      permission_level = jobs.JobPermissionLevel(permission)
      job_acl = jobs.JobAccessControlRequest(
          group_name=group,
          permission_level=permission_level
      )
      w.jobs.update_permissions(
          job_id=str(job_id),
          access_control_list=[job_acl]
      )
    except Exception as e:
      print(f"Exception occurred while updating {job_id} TO {group}: {e}")
      pass
  
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(grants_job,all_jobs)