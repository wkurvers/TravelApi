from flask import jsonify
from database import Persister, Event
import datetime
from sqlalchemy.sql import func
import time, sys

persister = Persister()

def postEvent(form):
    print("post event", file=sys.stderr)
    event = Event(
        name = form.get('name'),
        category = form.get('category'),
        description = form.get('description'),
        location = form.get('location'),
        startDate = func.now(),
        endDate=func.now(),
        image=str(int(time.time()))
    )
    persister.persist_object(event)
    return "success"

