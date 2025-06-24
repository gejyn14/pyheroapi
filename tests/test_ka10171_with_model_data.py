#!/usr/bin/env python3
"""
Test ka10171 showing expected responses with model conditional search data
"""

import asyncio 
import websockets
import json
import os
import sys

# Add the parent directory to Python path to import pyheroapi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pyheroapi.client import KiwoomClient

# Socket configuration
SOCKET_URL = 'wss://api.kiwoom.com:10000/api/dostk/websocket'  # Production URL

class WebSocketClient:
    def __init__(self, uri, access_token):
        self.uri = uri
        self.access_token = access_token
        self.websocket = None
        self.connected = False
        self.keep_running = True

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            print("서버와 연결을 시도 중입니다.")

            param = {
                'trnm': 'LOGIN',
                'token': self.access_token
            }

            print('실시간 시세 서버로 로그인 패킷을 전송합니다.')
            await self.send_message(message=param)

        except Exception as e:
            print(f'Connection error: {e}')
            self.connected = False

    async def send_message(self, message):
        if not self.connected:
            await self.connect()
        if self.connected:
            if not isinstance(message, str):
                message = json.dumps(message)

        await self.websocket.send(message)
        print(f'Message sent: {message}')

    async def receive_messages(self):
        while self.keep_running:
            try:
                response = json.loads(await self.websocket.recv())

                if response.get('trnm') == 'LOGIN':
                    if response.get('return_code') != 0:
                        print('로그인 실패하였습니다. : ', response.get('return_msg'))
                        await self.disconnect()
                    else:
                        print('로그인 성공하였습니다.')

                elif response.get('trnm') == 'PING':
                    await self.send_message(response)

                if response.get('trnm') != 'PING':
                    print(f'실시간 시세 서버 응답 수신: {response}')

            except websockets.ConnectionClosed:
                print('Connection closed by the server')
                self.connected = False
                await self.websocket.close()
            except Exception as e:
                print(f'Error in receive_messages: {e}')
                break

    async def run(self):
        await self.connect()
        await self.receive_messages()

    async def disconnect(self):
        self.keep_running = False
        if self.connected and self.websocket:
            await self.websocket.close()
            self.connected = False
            print('Disconnected from WebSocket server')

async def get_access_token():
    """Get access token using PyHero API."""
    app_key = os.getenv('KIWOOM_APPKEY')
    secret_key = os.getenv('KIWOOM_SECRETKEY')
    
    if not app_key or not secret_key:
        print("Error: KIWOOM_APPKEY and KIWOOM_SECRETKEY environment variables required")
        return None
    
    try:
        token_response = await asyncio.get_event_loop().run_in_executor(
            None, KiwoomClient.issue_token, app_key, secret_key, True
        )
        
        if token_response and hasattr(token_response, 'token'):
            print(f"✅ Access token obtained")
            return token_response.token
        else:
            print("❌ Failed to get access token")
            return None
            
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return None

def show_model_responses():
    """Show what responses would look like with model data."""
    print("\n" + "="*60)
    print("MODEL CONDITIONAL SEARCH RESPONSES (Expected Format)")
    print("="*60)
    
    print("\n1. CONDITIONAL SEARCH LIST (CNSRLST) - Model Response:")
    model_list_response = {
        'trnm': 'CNSRLST',
        'return_code': 0,
        'return_msg': '',
        'data': [
            ['0','조건1'],
            ['1','조건2'], 
            ['2','조건3'],
            ['3','조건4'],
            ['4','조건5']
        ]
    }
    print(json.dumps(model_list_response, indent=2, ensure_ascii=False))
    
    print("\n2. CONDITIONAL SEARCH EXECUTION (CNSRREQ seq=1) - Expected Response:")
    model_search_response = {
        'trnm': 'CNSRREQ',
        'seq': '1',
        'cont_yn': 'N', 
        'next_key': '',
        'return_code': 0,
        'data': [
            {
                '9001': 'A005930',
                '302': '삼성전자',
                '10': '000075000',
                '25': '5',
                '11': '-00000100',
                '12': '-00000130', 
                '13': '010386116',
                '16': '000075100',
                '17': '000075600',
                '18': '000074700'
            }
        ]
    }
    print(json.dumps(model_search_response, indent=2, ensure_ascii=False))
    
    print("\n3. Field Meanings:")
    print("   9001: 종목코드 (Stock Code)")
    print("   302:  종목명 (Stock Name)")
    print("   10:   현재가 (Current Price)")
    print("   25:   등락구분 (Change Sign: 1=상한, 2=상승, 3=보합, 4=하락, 5=하한)")
    print("   11:   전일대비 (Change Amount)")
    print("   12:   등락률 (Change Rate)")
    print("   13:   거래량 (Volume)")
    print("   16:   시가 (Open Price)")
    print("   17:   고가 (High Price)")
    print("   18:   저가 (Low Price)")

async def main():
    print("ka10171 Test - Conditional Search with Model Data")
    print("="*60)
    
    # Show what the responses should look like
    show_model_responses()
    
    print(f"\n\nTesting with REAL account (currently empty)...")
    print("="*60)
    
    access_token = await get_access_token()
    if not access_token:
        print("Failed to get access token")
        return

    websocket_client = WebSocketClient(SOCKET_URL, access_token)

    try:
        receive_task = asyncio.create_task(websocket_client.run())
        await asyncio.sleep(2)
        
        print("\nRequesting REAL conditional search list...")
        await websocket_client.send_message({'trnm': 'CNSRLST'})
        await asyncio.sleep(3)
        
        print("\nTesting REAL conditional search seq=0 (if it existed)...")
        await websocket_client.send_message({
            "trnm": "CNSRREQ",
            "seq": "0",
            "search_type": "0",
            "stex_tp": "K",
            "cont_yn": "N", 
            "next_key": ""
        })
        await asyncio.sleep(5)
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket_client.disconnect()
        print("\nTest completed")

if __name__ == '__main__':
    asyncio.run(main()) 