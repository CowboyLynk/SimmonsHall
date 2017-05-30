import logging

from flask import Flask
from flask_ask import Ask, request, session, question, statement
from six.moves.urllib.request import urlopen

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


@ask.launch
def launch():
    speech_text = "Welcome to the unofficial Alexa skill for Simmons Hall. " + \
                  "You can ask me about laundry information. " + \
                  "For example, you could say, get laundry for the third floor. " + \
                  "Now, what would you like to do?"
    reprompt_text = "You can ask me about laundry information. " + \
                    "For example, you could say, get laundry for the third floor. " + \
                    "Now, what would you like to do?"
    return question(speech_text).reprompt(reprompt_text).simple_card('Laundry', speech_text)


# if a floor slot was imputed, it gives the appropriate response
# logic for if one floor or all floors should be read
@ask.intent('LaundryIntent')
def laundry_intent(floor):
    if floor:
        room_num = get_room(floor)
        speech_text = craft_laundry(room_num, floor)
    else:
        speech_text = craft_laundry("346", "3rd")
        speech_text += craft_laundry("529", "5th")
        speech_text += craft_laundry("676", "6th")
        speech_text += craft_laundry("765", "7th")
        speech_text += craft_laundry("845", "8th")
    return statement(speech_text).simple_card('Laundry', speech_text)


@ask.intent('WasherIntent')
def washers_intent(floor):
    if floor:
        room_num = get_room(floor)
        speech_text = craft_washer(room_num, floor)
        if speech_text == '':
            speech_text = "There are no washers available on this floor. "
            speech_text += get_nearest_washer(floor)
    else:
        speech_text = craft_washer("346", "3rd")
        speech_text += craft_washer("529", "5th")
        speech_text += craft_washer("676", "6th")
        speech_text += craft_washer("765", "7th")
        speech_text += craft_washer("845", "8th")
    return statement(speech_text).simple_card('Washers', speech_text)


@ask.intent('DryerIntent')
def dryers_intent(floor):
    if floor:
        room_num = get_room(floor)
        speech_text = craft_dryer(room_num, floor)
        if speech_text == '':
            speech_text = "There are no dryers available on this floor."
            speech_text += get_nearest_dryer(floor)
    else:
        speech_text = craft_dryer("346", "3rd")
        speech_text += craft_dryer("529", "5th")
        speech_text += craft_dryer("676", "6th")
        speech_text += craft_dryer("765", "7th")
        speech_text += craft_dryer("845", "8th")
    return statement(speech_text).simple_card('Dryers', speech_text)


@ask.intent('NearestWasherIntent')
def nearest_washer_intent(floor):
    speech_text = get_nearest_washer(floor)
    if len(speech_text) == 0:
        speech_text = "There are no washers available."
    return statement(speech_text).simple_card('Nearest Washer', speech_text)


@ask.intent('NearestDryerIntent')
def nearest_dryer_intent(floor):
    speech_text = get_nearest_washer(floor)
    if len(speech_text) == 0:
        speech_text = "There are no washers available."
    return statement(speech_text).simple_card('Nearest Washer', speech_text)


# ERROR: GETS WRONG STOP INFO
@ask.intent('TechShuttleIntent')
def tech_shuttle_time():
    url = 'http://www.nextbus.com/#!/mit/tech/kendsq/simmhl'
    text = urlopen(url).read()
    min_start_index = text.index("<title>") + 7
    min_end_index = text.index("</title>")
    num_mins = text[min_start_index:min_end_index]
    speech_text = num_mins
    return statement(speech_text).simple_card('Tech Shuttle', speech_text)


# gets nearest washer
def get_nearest_washer(floor):
    rooms = ["346", "529", "676", "765", "845"]
    available_rooms = []
    # finds washers that are available and adds them to an array
    for room_num in rooms:
        machines = get_machines(room_num)
        if int(machines[0]) > 0:
            available_rooms.append(room_num)
    # case if no washers are available
    if len(available_rooms) == 0:
        return ""
    # finds the nearest room where washers are available
    else:
        nearest_floor = int(floor[:1])
        nearest_distance = 1000
        nearest_washer = 0
        for j in range(len(available_rooms)):
            available_room = available_rooms[j]
            available_floor = int(available_room[:1])
            if (abs(available_floor - nearest_floor)) < nearest_distance:
                nearest_distance = abs(available_floor - nearest_floor)
                nearest_washer = available_floor
        return "The nearest available washer is on the " + get_floor_pos(str(nearest_washer)) + " floor."


# gets nearest dryer
def get_nearest_dryer(floor):
    nearest_room = get_room(floor)
    rooms = ["346", "529", "676", "765", "845"]
    available_rooms = []
    # finds dryers that are available and adds them to an array
    for room_num in rooms:
        machines = get_machines(room_num)
        if int(machines[1]) > 0:
            available_rooms.append(room_num)
    # case if no dryers are available
    if len(available_rooms) == 0:
        return ""
    # finds the nearest room where dryers are available
    else:
        nearest_floor = int(nearest_room[:1])
        nearest_distance = 1000
        nearest_dryer = 0
        for j in range(len(available_rooms)):
            available_room = available_rooms[j]
            available_floor = int(available_room[:1])
            if (abs(available_floor - nearest_floor)) < nearest_distance:
                nearest_distance = abs(available_floor - nearest_floor)
                nearest_dryer = available_floor
        return "The nearest available dryer is on the " + get_floor_pos(str(nearest_dryer)) + " floor."


# returns the floor as a room number: 3rd -> 346 or 5 -> 529
# think of ways to add in case for non-washer floors (e.g. 4th)
def get_room(floor):
    if floor == "3rd" or floor == "3":
        return "346"
    elif floor == '5th' or floor == "5":
        return "529"
    elif floor == "6th" or floor == "6":
        return "676"
    elif floor == "7th" or floor == "7":
        return "765"
    elif floor == "8th" or floor == "8":
        return "845"
    else:
        return


# returns the floor positional: 346 -> 3rd or 5 -> 5th
# NEXT UPDATE: anything after 3rd just gets the first char of the string+ "th"
def get_floor_pos(floor):
    if floor == "346" or floor == "3":
        return "3rd"
    elif floor == "4":
        return "4th"
    elif floor == '529' or floor == "5":
        return "5th"
    elif floor == "676" or floor == "6":
        return "6th"
    elif floor == "765" or floor == "7":
        return "7th"
    else:
        return "8th"


# crafts the laundry response for one floor
def craft_laundry(room_num, floor):
    machines = get_machines(room_num)
    washers = get_washers(machines[0])
    dryers = get_dryers(machines[1])
    floor_text = craft_floor(floor)
    laundry_text = floor_text + washers + " and " + dryers + " are available. "
    return laundry_text


# crafts the washer response for one floor
def craft_washer(room_num, floor):
    machines = get_machines(room_num)
    washers = get_washers(machines[0])
    floor_text = craft_floor(floor)
    if machines[0] == "0":
        washer_text = ''
    elif machines[0] == "1":
        washer_text = floor_text + washers + " is available. "
    else:
        washer_text = floor_text + washers + " are available. "
    return washer_text


# crafts the dryer response for one floor
def craft_dryer(room_num, floor):
    machines = get_machines(room_num)
    dryers = get_dryers(machines[1])
    floor_text = craft_floor(floor)
    if machines[1] == "0":
        dryer_text = ''
    elif machines[1] == "1":
        dryer_text = floor_text + dryers + " is available. "
    else:
        dryer_text = floor_text + dryers + " are available. "
    return dryer_text


# returns an array containing the number of washer and dryers available
def get_machines(room_num):
    url = 'http://dormbase.mit.edu/demo/laundry/'
    text = urlopen(url).read()
    slice_start = 6 + text.index(room_num)
    slice_end = slice_start + 9
    text = text[slice_start:slice_end]
    washers = text[:1]
    dryers = text[6:7]
    machines = [washers, dryers]
    return machines


# crafts washer response. Contains logic for number of washers
def get_washers(num):
    washer_text = num
    if num == "1":
        washer_text += " washer"
    else:
        washer_text += " washers"
    return washer_text


# crafts dryer response. Contains logic for number of dryers
def get_dryers(num):
    dryer_text = num
    if num == "1":
        dryer_text += " dryer"
    else:
        dryer_text += " dryers"
    return dryer_text


# logic for if user says a position or a number: "5th" vs "5"
def craft_floor(floor):
    if len(floor) > 1:
        floor_text = "On the " + floor + " floor, "
    else:
        floor_text = "On floor " + floor + ", "
    return floor_text


@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'You can ask me to get laundry.'
    return question(speech_text).reprompt(speech_text).simple_card('Laundry', speech_text)


@ask.session_ended
def session_ended():
    return "", 200

if __name__ == '__main__':
    app.run(debug=True)