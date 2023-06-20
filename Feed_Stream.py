#!/usr/bin/python3

import socket, sys, threading
import os, requests, json, time

bearer_token = os.environ.get('BEARER_TOKEN')# this is my bearer token
print("My Bearer Token Is Not None:{}".format(bearer_token!=None))

def create_url():
    return "https://api.twitter.com/2/tweets/sample/stream"


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2SampledStreamPython"
    return r


if len(sys.argv) != 3:
    print("Usage: netcat.py HOSTNAME PORT", file=sys.stderr)
    sys.exit(-1)

HOST = sys.argv[1]
PORT = int(sys.argv[2])
#request the stream
response = requests.request("GET", create_url(), auth=bearer_oauth, stream=True)
print("Response Status Is:{}".format(response.status_code))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    clients = []
    def accept():
        client, address = s.accept()
        print(f'New client @ {address}')
        clients.append(client)
        threading.Thread(target=accept).start()
    threading.Thread(target=accept).start()

    while True:
        if len(clients) > 0:
            for response_line in response.iter_lines():
                if response_line:
                    data = json.loads(response_line)['data']['text']
                    for client in clients:
                        try:
                            print(f'Sending {data.rstrip()} to {client.getpeername()}')
                            client.sendall(data.encode())
                            #sleep for 0.5 second to slow down the stream
                            time.sleep(0.5)
                        except:
                            clients.remove(client)

                if response.status_code != 200:
                    raise Exception(
                        "Request returned an error: {} {}".format(
                            response.status_code, response.text
                        )
                    )
