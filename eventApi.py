from database import Persister, Event
from flask import jsonify
import os, time, json

persister = Persister()

def postEvent(request):
    form = request.form

    if request.files.get('image', None):
        file = request.files.get('image', None)
        name = str(time.time()).replace(".", "")
        name = name + "." + file.filename.partition(".")[-1]
        file.save(os.path.join('images\events', name))
    else:
        name = None


    event = Event(
        name=form.get('name'),
        category=form.get('category'),
        description=form.get('description'),
        location=form.get('location'),
        startDate=form.get('start_date'),
        startTime=form.get('start_time'),
        endDate=form.get('end_date'),
        endTime=form.get('end_time'),
        owner=form.get('owner'),
        image=name
    )

    persister.persist_object(event)

    return "success"


def updateEvent(request):
    form = request

    persister.updateEvent(request)

    return "success"


def getEvent(id):
    event = persister.getEvent(id)

    result = {
        'name': event.name,
        'category': event.category,
        'description': event.description,
        'location': event.location,
        'startDate': event.startDate,
        'startTime': event.startTime,
        'endDate': event.endDate,
        'endTime': event.endTime
    }

    return json.dumps(result, indent=4, default=str)

