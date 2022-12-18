"""API code to summarize schema and connect to websocket"""

import os
import json
import logging
from pprint import pformat
import websocket

from .code_analyzer import SearchableAST
from .utils import create_hash, download_app

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)

class SpacesAPI:
    """HuggingSpace API class to connect interfaces"""
    hf_remote_url = "https://huggingface.co/spaces/"
    ws_remote_url = 'wss://{}-{}.hf.space/queue/join'

    def __init__(self, username, space_name, app_path="app.py", check_before_send=True):
        self.username = username
        self.space_name = space_name
        self.app_path = app_path
        self.precheck = check_before_send # to be implemented
        self.remote_point, self.demo_params = self.create_template()

    def create_template(self):
        """Download the code and analyze for the clicks

        Returns:
            remote_wss (string): the endpoint to connect
            demo_params (dict):  schema of the parameters
        """        
        remote_app_url = os.path.join(self.hf_remote_url, self.username, self.space_name)
        self.app_text = download_app(remote_app_url, app_path=self.app_path)

        sast = SearchableAST(self.app_text)
        demo_objs = sast.find_all_by_attribute_name('Interface')
        if len(demo_objs) == 0:
            demo_objs = sast.find_all_by_attribute_name('(click|submit)')

        demo_params = []
        for idx, demos in enumerate(demo_objs):
            params = sast.get_schema(demos)
            log_string = f"""Function {idx}:\n summary:\n {pformat(params)}"""
            logging.info(log_string)
            demo_params.append(params)

        ws_username = self.username.replace('_', '-')
        ws_spacename = self.space_name.replace('_', '-')
        remote_wss = self.ws_remote_url.format(ws_username, ws_spacename)
        return remote_wss, demo_params

    def interact(self, data: dict, fn_index=0):
        """Interaction function with the endpoint

        Args:
            data (dict): _description_
            fn_index (int, optional): The function number to run. The index depends on the click/submit order. Defaults to 0.

        Returns:
            _type_: _description_
        """        

        websock = websocket.create_connection(self.remote_point)
        response = websock.recv()
        first_msg = json.loads(response)

        if first_msg['msg'] != 'send_hash':
            logging.error('Error at first message: %s' % first_msg['msg'])
            return

        session_hash = create_hash()
        send_msg = {"session_hash": session_hash, "fn_index": fn_index}
        websock.send(json.dumps(send_msg))

        while True:
            response = websock.recv()
            response = json.loads(response)
            if response['msg'] == 'send_data':
                break
            if response['msg'] == 'estimation':
                print(f'\r{response["rank"]}', end='')

        send_msg = {"fn_index": fn_index,
                    "data": data, "session_hash": session_hash}
        websock.send(json.dumps(send_msg))

        while True:
            response = websock.recv()
            response = json.loads(response)
            if response['msg'] == "process_completed":
                break

        return response["output"]
