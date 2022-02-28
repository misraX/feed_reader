from feed_reader.celery import app


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')