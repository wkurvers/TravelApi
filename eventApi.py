from database import Persister, Event
from flask import jsonify
import os, time, json, sys
from decimal import Decimal
import checks

persister = Persister()

def postEvent(request):
    form = request.args

    location = form.get('location').strip()
    name = form.get('name').strip()
    description = form.get('description').strip()
    startDate = form.get('startDate')
    startTime = form.get('startTime')
    endDate = form.get('endDate')
    endTime = form.get('endTime')
    owner = form.get('owner')
    lng = form.get('lng')
    lat = form.get('lat')

    if checks.emptyCheck([location, name, description, startDate, startTime, endDate, endTime, owner, lng, lat]):
        return jsonify({
            "message": "Please, fill in all fields."
        }), 400, {'ContentType': 'application/json'}

    if checks.lengthSixtyFourCheck([name]):
        return jsonify({
            "message": "Please don't fill in more than 64 characters."
        }), 400, {'ContentType': 'application/json'}

    if checks.dateTimeCheck(startDate, startTime, endDate, endTime):
        return jsonify({
            "message": "A problem occurred with regards to the dates and times of this event.<br>"
                   "Rules:<br>"
                   "- Events that start later than 1 year from now are not allowed.<br>"
                   "- The event's start date/time can't be later than the end date/time.<br>"
                   "- You can't enter dates earlier than today.<br>"
                   "- An event's length can't be longer than a year."
        }), 400, {'ContentType': 'application/json'}

    if request.files.get('image', None):
        file = request.files.get('image', None)
        img = str(time.time()).replace(".", "")
        ext = file.filename.partition(".")[-1]
        if not checks.imgExtensionCheck(ext):
            return jsonify({
                "message": "Only .png, .jpg or .jpeg  images are valid!"
            }), 400, {'ContentType': 'application/json'}
        img = img + "." + ext
        file.save(os.path.join('images\events', img))
    else:
        img = None

    temp = location.split(', ')
    country = None
    city = None
    address = None
    if len(temp) > 0:
        country = temp.pop()
    if len(temp) > 0:
        city = temp.pop()
        if len(city.split(" ")) > 2:
            temp2 = city.split(" ")
            city = temp2.pop()
            address = ", " + " ".join(temp2)
    if len(temp) > 0:
        if address:
            address = ', '.join(temp) + address
        else:
            address = ', '.join(temp)

    event = Event(
        name=name,
        description=description,
        address=address,
        city=city,
        country=country,
        startDate=startDate,
        startTime=startTime,
        endDate=endDate,
        endTime=endTime,
        owner=owner,
        lng=lng,
        lat=lat,
        image=img
    )

    persister.persist_object(event)

    return jsonify({
        "message": "Event created! You can now view it in your profile."
    }), 200, {'ContentType': 'application/json'}


def updateEvent(request):
    return persister.updateEvent(request)


def deleteEvent(request, username):
    eventId = request.args.get('eventId', None)
    if eventId:
        return persister.deleteEvent(eventId, username)
    else:
        return jsonify({
            "message": "No event id."
        }), 400, {'ContentType': 'application/json'}


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
