import sys
sys.path.append('..')
import websocket
import codecs
from base.entity import Coin
import traceback
from okex.utils import inflate
import json


def on_message(ws, message):
    message = bytes.decode(inflate(message), 'utf-8')  # data decompress
    json_message = json.loads(message)
    for each_data in json_message['data']:
        print(each_data['price'])
    # with codecs.open(file_depth, 'a+', 'utf-8') as f:
    #     f.writelines(str(json_message[0]) + '\r\n')


def on_error(ws, error):
    traceback.print_exc()
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    print("websocket connected...")
    ws.send("{\"op\": \"subscribe\", \"args\": [\"spot/trade:%s-USDT\", \"\"]}"
            % (coin.name.upper()))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        coin_name = sys.argv[1]
        # 默认币种handle_deque
        coin = Coin(coin_name, "usdt")
        instrument_id = coin.get_instrument_id()
        future_instrument_id = coin.get_future_instrument_id()
        file_depth = coin.gen_depth_filename()

        ws = websocket.WebSocketApp("wss://real.okex.com:10442/ws/v3?compress=true",
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.on_open = on_open
        while True:
            ws.run_forever(ping_interval=20, ping_timeout=10)
            print("write left lines into file...")
            with codecs.open(file_depth, 'a+', 'UTF-8') as f:
                f.flush()
                f.close()
    else:
        print('miss param...')
