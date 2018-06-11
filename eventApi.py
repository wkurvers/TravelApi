from database import Persister, Event
import os
import time

persister = Persister()

def postEvent(request):
    form = request.form

    if request.files['image']:
        file = request.files['image']
        name = str(time.time()).replace(".", "")
        name = name + "." + file.filename.partition(".")[-1]
        file.save(os.path.join('images\events', name))


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

