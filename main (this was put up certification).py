import logging

from flask import Flask
from flask_ask import Ask, request, session, question, statement
from six.moves.urllib.request import urlopen

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

@ask.launch
def launch():
    speech_text = 'Welcome to the Alexa skill for Simmon\'s Hall.'
    return question(speech_text).reprompt(speech_text).simple_card('Laundry', speech_text)

# if a floor slot was inputed, it gives the appropriate response
# logic for if one floor or all floors should be read
@ask.intent('LaundryIntent')
def laundry(floor):
    if floor:
        floor_str = get_floor(floor)
        speech_text = craft_laundry(floor_str, floor)
    else:
        speech_text = craft_laundry("346", "3rd")
        speech_text += craft_laundry("529", "5th")
        speech_text += craft_laundry("676", "6th")
        speech_text += craft_laundry("765", "7th")
        speech_text += craft_laundry("845", "8th")
    return statement(speech_text).simple_card('Laundry', speech_text)

@ask.intent('WasherIntent')
def washers(floor):
    if floor:
        floor_str = get_floor(floor)
        speech_text = craft_washer(floor_str, floor)
        if speech_text == '':
            speech_text = "There are no washers availible on this floor."
    else:
        speech_text = craft_washer("346", "3rd")
        speech_text += craft_washer("529", "5th")
        speech_text += craft_washer("676", "6th")
        speech_text += craft_washer("765", "7th")
        speech_text += craft_washer("845", "8th")
    return statement(speech_text).simple_card('Washers', speech_text)

@ask.intent('DryerIntent')
def dryers(floor):
    if floor:
        floor_str = get_floor(floor)
        speech_text = craft_dryer(floor_str, floor)
        if speech_text == '':
            speech_text = "There are no dryers availible on this floor."
    else:
        speech_text = craft_dryer("346", "3rd")
        speech_text += craft_dryer("529", "5th")
        speech_text += craft_dryer("676", "6th")
        speech_text += craft_dryer("765", "7th")
        speech_text += craft_dryer("845", "8th")
    return statement(speech_text).simple_card('Dryers', speech_text)

# returns the floor as a room number: 3rd -> 346 or 5 -> 529
def get_floor(floor):
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

# crafts the laundry response for one floor
def craft_laundry(floor_str, floor):
    machines = get_machines(floor_str)
    washers = get_washers(machines[0])
    dryers = get_dryers(machines[1])
    floor_text = craft_floor(floor)
    laundry_text = floor_text + washers + " and " + dryers + " are availible. "
    return laundry_text

# crafts the washer response for one floor
def craft_washer(floor_str, floor):
    machines = get_machines(floor_str)
    washers = get_washers(machines[0])
    floor_text = craft_floor(floor)
    if machines[0] == "0":
        washer_text = ''
    elif machines[0] == "1":
        washer_text = floor_text + washers + " is availible. "
    else:
        washer_text = floor_text + washers + " are availible. "
    return washer_text

# crafts the dryer response for one floor
def craft_dryer(floor_str, floor):
    machines = get_machines(floor_str)
    dryers = get_dryers(machines[1])
    floor_text = craft_floor(floor)
    if machines[1] == "0":
        dryer_text = ''
    elif machines[1] == "1":
        dryer_text = floor_text + dryers + " is availible. "
    else:
        dryer_text = floor_text + dryers + " are availible. "
    return dryer_text
# returns an array containing the number of washer and dryers availible
def get_machines(floor_str):
    url = 'http://dormbase.mit.edu/demo/laundry/'
    text = urlopen(url).read()
    slice_start = 6 + text.index(floor_str)
    slice_end = slice_start + 9
    text = text[slice_start:slice_end];
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
