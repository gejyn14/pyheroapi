#!/usr/bin/env python3
"""
Test ka10171 using official Kiwoom WebSocket pattern
"""

import asyncio 
import websockets
import json
import os

# Socket configuration
SOCKET_URL = 'wss://api.kiwoom.com:10000/api/dostk/websocket'  # Production URL
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')  # Get from environment

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
        self.connected = False
        self.keep_running = True

    # Connect to WebSocket server
    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            print("서버와 연결을 시도 중입니다.")

            # Login packet
            param = {
                'trnm': 'LOGIN',
                'token': ACCESS_TOKEN
            }

            print('실시간 시세 서버로 로그인 패킷을 전송합니다.')
            # Send login info when WebSocket connects
            await self.send_message(message=param)

        except Exception as e:
            print(f'Connection error: {e}')
            self.connected = False

    # Send message to server. Auto-connect if no connection.
    async def send_message(self, message):
        if not self.connected:
            await self.connect()  # Reconnect if disconnected
        if self.connected:
            # Serialize to JSON if message is not string
            if not isinstance(message, str):
                message = json.dumps(message)

        await self.websocket.send(message)
        print(f'Message sent: {message}')

    # Receive and print messages from server
    async def receive_messages(self):
        while self.keep_running:
            try:
                # Parse received message from server as JSON
                response = json.loads(await self.websocket.recv())

                # Check login result if message type is LOGIN
                if response.get('trnm') == 'LOGIN':
                    if response.get('return_code') != 0:
                        print('로그인 실패하였습니다. : ', response.get('return_msg'))
                        await self.disconnect()
                    else:
                        print('로그인 성공하였습니다.')

                # Send back the same value if message type is PING
                elif response.get('trnm') == 'PING':
                    await self.send_message(response)

                if response.get('trnm') != 'PING':
                    print(f'실시간 시세 서버 응답 수신: {response}')

            except websockets.ConnectionClosed:
                print('Connection closed by the server')
                self.connected = False
                await self.websocket.close()

    # Run WebSocket
    async def run(self):
        await self.connect()
        await self.receive_messages()

    # Close WebSocket connection
    async def disconnect(self):
        self.keep_running = False
        if self.connected and self.websocket:
            await self.websocket.close()
            self.connected = False
            print('Disconnected from WebSocket server')

async def main():
    if not ACCESS_TOKEN:
        print("Error: ACCESS_TOKEN environment variable required")
        return

    # Declare WebSocketClient global variable
    websocket_client = WebSocketClient(SOCKET_URL)

    # Run WebSocket client in background
    receive_task = asyncio.create_task(websocket_client.run())

    # Wait for connection and login
    await asyncio.sleep(2)
    
    # Request conditional search list
    await websocket_client.send_message({ 
        'trnm': 'CNSRLST', # TR name
    })
    
    await asyncio.sleep(3)
    
    # Test ka10171 - conditional search with seq=1, search_type=0
    await websocket_client.send_message({
        "trnm": "CNSRREQ",
        "seq": "1",
        "search_type": "0",
        "stex_tp": "K",
        "cont_yn": "N",
        "next_key": ""
    })
    
    await asyncio.sleep(5)
    
    # Test ka10171 - conditional search with seq=1, search_type=1
    await websocket_client.send_message({
        "trnm": "CNSRREQ",
        "seq": "1",
        "search_type": "1",
        "stex_tp": "K"
    })

    # Wait for responses and then disconnect
    await asyncio.sleep(10)
    await websocket_client.disconnect()

# Run program with asyncio
if __name__ == '__main__':
    asyncio.run(main()) 