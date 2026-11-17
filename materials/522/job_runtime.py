"""Small existing subprocess ETL runner, with cancellation cleanup to extend."""
import subprocess
import sys
from pathlib import Path

class JobRuntime:
    def __init__(self, locks):
        self.locks=locks
        self.jobs={}
    def submit(self, job_id, resource, control_dir, result_db):
        session='job:'+job_id
        grant=self.locks.acquire(session,resource)
        if grant['status']!='granted':
            return {'status':'deferred'}
        process=subprocess.Popen([sys.executable,str(Path(__file__).with_name('worker.py')),
                                  str(control_dir),str(result_db),job_id])
        self.jobs[job_id]={'process':process,'token':grant['token'],'session':session,'status':'running'}
        return {'status':'running'}
    def cancel(self,job_id):
        item=self.jobs[job_id]
        item['process'].terminate()
        self.locks.release(item['session'],item['token'])
        item['status']='cancelled'
    def reap(self,job_id):
        item=self.jobs[job_id]
        code=item['process'].poll()
        if code is None:return {'status':item['status'],'worker_alive':True}
        self.locks.release(item['session'],item['token'])
        if item['status']!='cancelled':item['status']='succeeded' if code==0 else 'failed'
        return {'status':item['status'],'worker_alive':False,'exit_code':code}
