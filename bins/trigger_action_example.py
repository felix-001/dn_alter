import sys
import os

# add library to python path , don't forget it
lib_name = 'libs'
sys.path.insert(0, os.path.sep.join([os.path.dirname(os.path.abspath(__file__)), lib_name]))

import logging
import requests, json

from pdr_python_sdk.trigger_action.on_demand_trigger_action import OnDemandTriggerAction
from pdr_python_sdk.on_demand_action import run
from urllib import parse
import time


wx_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=92f4334a-906a-4394-b975-d9bba071f19d"

class TriggerActionExample(OnDemandTriggerAction):

    def do_handle_init(self, packet):
        if packet.body().contains_metadata():
            metadata = packet.body().metadata()
            logging.info("metadata = %s", metadata)

    def send_msg(self, content):
        """发送指定信息到微信机器人"""
        data = json.dumps({"msgtype": "text", "text": {"content": content, "mentioned_list":["@all"]}})
        r = requests.post(wx_url, data, auth=('Content-Type', 'application/json'))

    def do_handle_events(self, events):
        length = len(events)
        event_name = ""
        evt_id = ""
        evt_time = ""
        alertDescription = ""
        logging.info("event length = {0}".format(length))

        if length > 0:
            event_name = events[0].eventName
            evt_id = events[0].eventId
            evt_time = events[0].eventTime
            alertDescription = events[0].alertDescription

        content = "告警: " + event_name + "\n"
        content += "事件描述: " + alertDescription + "\n"
        content += "触发时间: " + evt_time + "\n"
        content += "事件链接: " + "http://qvs-pdr.qnlinking.com/alert/events/" + evt_id + "\n"
        if len(events[0].additionContents) > 0:
            additions = events[0].additionContents
            query = parse.urlencode({'queryString' : additions[0].spl})
            url = "http://qvs-pdr.qnlinking.com/logdb/search/log?dataLimit=-1&mode=smart&preview=true"
            url += "&" + query
            timeArray = time.strptime(evt_time, "%Y-%m-%d %H:%M:%S")
            start = str(int(time.mktime(timeArray))*1000)
            url += "&start=" + start
            end_ms = int(round(time.time() * 1000))
            url += "&end=" + str(end_ms)
            content += "事件日志链接: " + url + "\n"
        # do send events to other platform
        self.send_msg(content)
        return content

if __name__ == '__main__':
    run(TriggerActionExample, sys.argv, sys.stdin.buffer, sys.stdout.buffer)
