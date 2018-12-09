from datetime import datetime
import time
import sys
from opencvWebcamToImage import video_to_frames
import os
import schedule
import requests

import iothub_client
from iothub_client import (IoTHubModuleClient, IoTHubClientError, IoTHubError,
                           IoTHubMessage, IoTHubMessageDispositionResult,
                           IoTHubTransportProvider)
# global counters
SEND_CALLBACKS = 0

# Define the JSON message to send to IoT Hub.
def set_msg_txt(predictions, sendTime):
    return {"table": "T10","predictions": predictions,"sendTime": sendTime}

def send_to_Hub_callback(strMessage):
    message = IoTHubMessage(bytearray(strMessage, 'utf8'))
    hubManager.send_event_to_output("output1", message, 0)

# Callback received when the message that we're forwarding is processed.
def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
SEND_CALLBACKS += 1

class HubManager(object):

    def __init__(
            self,
            messageTimeout,
            protocol,
            verbose):
        '''
        Communicate with the Edge Hub
        :param int messageTimeout: the maximum time in milliseconds until a message times out. The timeout period starts at IoTHubClient.send_event_async. By default, messages do not expire.
        :param IoTHubTransportProvider protocol: Choose HTTP, AMQP or MQTT as transport protocol.  Currently only MQTT is supported.
        :param bool verbose: set to true to get detailed logs on messages
        '''
        self.messageTimeout = messageTimeout
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)
        self.client.set_option("messageTimeout", self.messageTimeout)
        self.client.set_option("product_info","edge-camera-capture")
        if verbose:
            self.client.set_option("logtrace", 1) #enables MQTT logging

    def send_event_to_output(self, outputQueueName, event, send_context):
        self.client.send_event_async(outputQueueName, event, send_confirmation_callback, send_context)

def main_function(endpoint_url, input_loc, output_loc, hubManager):
    picture_location = video_to_frames(input_loc, output_loc)
    try:
        headers = {'Content-Type': 'application/octet-stream'}
        img = open(picture_location, 'rb')
        response = requests.post(headers = headers, url=endpoint_url, data = img)
        print(response.content)
        sendTime = (int)(time.mktime(datetime.utcnow().timetuple()))
        msg_txt_formatted = str(set_msg_txt(response.content, sendTime))
        message = IoTHubMessage(bytearray(msg_txt_formatted, 'utf8'))
        hubManager.send_event_to_output("output1", message, 0)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print ("Error " + str(e))
    os.system('rm ' + picture_location)
    print(picture_location)

if __name__ == '__main__':
    try:
        IMAGE_PROCESSING_ENDPOINT = os.getenv('IMAGE_PROCESSING_ENDPOINT', "")
        VIDEO_PATH = os.getenv('VIDEO_PATH', "")
        print ( "\nPython %s\n" % sys.version )
        user=os.popen('echo $(whoami)').read().replace('\n', '')
        input_loc = '/home/' + user + '/' + VIDEO_PATH
        output_loc = '/home/' + user + '/opencv-storage'
        hubManager = HubManager(10000, IoTHubTransportProvider.MQTT, False)
        schedule.every(2).seconds.do(main_function, endpoint_url=IMAGE_PROCESSING_ENDPOINT, \
            hubManager=hubManager, input_loc=input_loc, output_loc=output_loc)
        while True:
            schedule.run_pending()
            time.sleep(1)
    except ValueError as error:
        print ( "CameraCapture module stopped" )
        print ( error )
        sys.exit(1)           
    except KeyboardInterrupt:
        print ( "CameraCapture module stopped" )
