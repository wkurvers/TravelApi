from database import Persister, Event
from flask import jsonify
import os, time, json, sys
from decimal import Decimal

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

    location = form.get('location')
    print(location, file=sys.stderr)
    temp = location.split(', ')
    print(temp, file=sys.stderr)

    country = None
    city = None
    address = None
    if len(temp) > 0:
        country = temp.pop()
    if len(temp) > 0:
        city = temp.pop()
    if len(temp) > 0:
        address = temp.pop()

    event = Event(
        name=form.get('name'),
        category=form.get('category'),
        description=form.get('description'),
        address=address,
        city=city,
        country=country,
        startDate=form.get('start_date'),
        startTime=form.get('start_time'),
        endDate=form.get('end_date'),
        endTime=form.get('end_time'),
        owner=form.get('owner'),
        lng=form.get('lng'),
        lat=form.get('lat'),
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

    location = ""
    if event.address:
        if event.city:
            location += event.address + ", "
        else:
            location += event.address
    if event.city:
        if event.country:
            location += event.city + ", "
        else:
            location += event.city
    if event.country:
        location += event.country

    result = {
        'name': event.name,
        'category': event.category,
        'description': event.description,
        'address': event.address,
        'city': event.city,
        'location': location,
        'country': event.country,
        'startDate': event.startDate,
        'startTime': event.startTime,
        'endDate': event.endDate,
        'endTime': event.endTime,
        'lat': event.lat,
        'lng': event.lng
    }

    return json.dumps(result, indent=4, default=str)


def getEvents(city, country):
    events = persister.getCityEvents(city, country)
    result = []

    if events:
        result.append(events[0])
        for event in events[1]:

            location = ""
            if event.address:
                if event.city:
                    location += event.address + ", "
                else:
                    location += event.address
            if event.city:
                if event.country:
                    location += event.city + ", "
                else:
                    location += event.city
            if event.country:
                location += event.country

            result.append({
                "name": event.name,
                "address": event.address,
                "city": event.city,
                "country": event.country,
                "startDate": event.startDate,
                "location": location,
                "description": event.description,
                "id": event.id,
                "startTime": event.startTime,
                "endDate": event.endDate,
                "endTime": event.endTime,
                "image": event.image,
                "lat": event.lat,
                "lng": event.lng,
            })
    return json.dumps(result, indent=4, default=str)
