import requests

from datetime import datetime

def read_api_key(fname='api-key.txt'):
    import json
    api_key = None
    with open(fname) as f:
        ipdb.set_trace()
        api_key = json.loads(f.read())['ifttt'].strip()

    return api_key


def send_event(event, api_key=None, value1=None, value2=None, value3=None):
    """Send an event to the IFTTT maker channel
    Parameters:
    -----------
    api_key : string
        Your IFTTT API key
    event : string
        The name of the IFTTT event to trigger
    value1 :
        Optional: Extra data sent with the event (default: None)
    value2 :
        Optional: Extra data sent with the event (default: None)
    value3 :
        Optional: Extra data sent with the event (default: None)
    """

    url = 'https://maker.ifttt.com/trigger/{e}/with/key/{k}/'.format(e=event,
                                                                     k=api_key)
    payload = {'value1': value1, 'value2': value2, 'value3': value3}
    print('making request with event %s and payload\n\t%s' % (event, payload))
    return requests.post(url, data=payload)



if __name__ == '__main__':
    key = read_api_key()
    eventOn = 'alarm_alert_start'
    eventOff = 'alarm_alert_dismiss'
    date =  datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    dataOn = {'ccurredAt': date,'EventName':eventOn}
    dataOff = {'ccurredAt': date,'EventName':eventOff}

    test = {'value1':1231, 'value2':2222, 'value3':3333}
    send_event(eventOff,api_key=key, **test)