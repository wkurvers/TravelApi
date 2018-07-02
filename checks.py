from datetime import datetime, timedelta

def checkSpecialChars(items):
    for item in items:
        if set('[~!#$%^&*()_+{}":;\']+$').intersection(item):
            return True
    return False


def checkSpecialCharsEmail(email):
    return set('[~!#$%^&*()_+{}":;\']+$').intersection(email)


def passwordLengthCheck(password):
    check1 = len(password) < 5
    check2 = len(password) > 64
    if check1:
        return [False, "short"]
    if check2:
        return [False, "long"]
    else:
        return [True, ""]

# Returns True if one of the items is empty
def emptyCheck(items):
    count = 0
    for item in items:
        if not item:
            print(count)
            return True
        count += 1
    return False


# Returns True if end date and time are earlier than start date and time
def dateTimeCheck(startDate, startTime, endDate, endTime):
    if not startDate == endDate or startDate < endDate:
        print("1")
        return True

    if startDate == endDate:
        if endTime < startTime:
            print("2")
            return True
        if endTime == startTime:
            print("3")
            return True

    start = datetime.strptime(startDate, "%Y-%m-%d")
    end = datetime.strptime(endDate, "%Y-%m-%d")
    currentTime = datetime.now() - timedelta(days=1)

    if start < currentTime:
        print("4")
        return True

    if start.year > (currentTime.year+1):
        print("5")
        return True

    if (end-start).days > 365:
        print("6")
        return True

    return False

def lengthSixtyFourCheck(items):
    for item in items:
        if len(item) > 64:
            return True
    return False


# Returns False if ext is not a valid extension
def imgExtensionCheck(ext):
    if ext == "jpg" or "jpeg" or "png":
        return True
    return False
