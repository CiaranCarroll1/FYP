import time
from extract import extract
from celery import Celery

redis_url = "redis://h:pccc9ec6523412f670125b1cc08c3b03c064fd186b3f4bc0356e3beefcd31d101@ec2-52-50-246-38.eu-west-1.compute.amazonaws.com:21709"
celery_app = Celery('query', backend=redis_url, broker=redis_url)


# This is the function that will be run by Celery
# You need to change the function declaration to include all the
# arguments that the app will pass to the function:
@celery_app.task(bind=True)
def query(self, args):
    task_id = self.request.id
    # Don't touch this:
    self.update_state(state='PROGRESS')
    time.sleep(1.5)  # a short dwell is necessary for other async processes to catch-up

    results = extract(args)

    return results
