# -*- encoding: utf-8 -*-

import sys
sys.path.append('..')
import websocket
import codecs
from base.entity import Coin, Indicator, DealEntity
import traceback
from okex.utils import inflate, timestamp2string
import json
import time
from collections import deque
import threading
try:
    import thread
except ImportError:
    import _thread as thread

spot_queue_1s = deque()
future_queue_1s = deque()
spot_ind_1s = Indicator(1)
future_ind_1s = Indicator(1)
last_write_time = ''


def handle_deque(deq, entity, ts, ind):
    while len(deq) > 1:
        left = deq.popleft()
        if float(left.time + ind.interval) > float(ts):
            deq.appendleft(left)
            break
        ind.minus_vol(left)
        ind.minus_price(left)
    deq.append(entity)
    ind.add_price(entity)
    ind.add_vol(entity)


def on_message(ws, message):
    global last_write_time
    message = bytes.decode(inflate(message), 'utf-8')  # data decompress
    json_message = json.loads(message)
    table = json_message['table']
    if table == 'spot/trade':
        for json_data in json_message['data']:
            time_stamp_s = time.time()
            spot_price = float(json_data['price'])
            deal_entity = DealEntity(json_data['trade_id'],
                                     spot_price,
                                     round(float(json_data['size']), 3),
                                     time_stamp_s,
                                     json_data['side'])

            handle_deque(spot_queue_1s, deal_entity, time_stamp_s, spot_ind_1s)
            # if last_write_time != int(time_stamp_s):
            #     last_write_time = int(time_stamp_s)
            #     future_avg_price = future_ind_1s.cal_avg_price()
            #     spot_avg_price = spot_ind_1s.cal_avg_price()
            #     diff = (future_avg_price - spot_avg_price) / spot_avg_price * 100
            #     info = 'time: %s, spot_price: %.3f, future_price: %.3f, diff: %.3f%%' \
            #            % (timestamp2string(time_stamp_s), spot_avg_price, future_avg_price, diff)
            #     print(info)
            #     with codecs.open(coin_name + "_spot_future_diff.txt", 'a+', 'utf-8') as f:
            #         f.writelines(info + '\r\n')

    elif table == 'futures/trade':
        for json_data in json_message['data']:
            time_stamp_s = time.time()
            future_price = float(json_data['price'])
            deal_entity = DealEntity(json_data['trade_id'],
                                     future_price,
                                     int(json_data['qty']),
                                     time_stamp_s,
                                     json_data['side'])

            handle_deque(future_queue_1s, deal_entity, time_stamp_s, future_ind_1s)
            # if last_write_time != int(time_stamp_s):
            #     last_write_time = int(time_stamp_s)
            #     future_avg_price = future_ind_1s.cal_avg_price()
            #     spot_avg_price = spot_ind_1s.cal_avg_price()
            #     diff = (future_avg_price - spot_avg_price) / spot_avg_price * 100
            #     info = 'time: %s, spot_price: %.3f, future_price: %.3f, diff: %.3f%%' \
            #            % (timestamp2string(time_stamp_s), spot_avg_price, future_avg_price, diff)
            #     print(info)
            #     with codecs.open(coin_name + "_spot_future_diff.txt", 'a+', 'utf-8') as f:
            #         f.writelines(info + '\r\n')


def on_error(ws, error):
    traceback.print_exc()
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    print("websocket connected...")
    ws.send("{\"op\": \"subscribe\", \"args\": [\"spot/trade:%s-USDT\", \"futures/trade:%s\"]}"
            % (coin.name.upper(), coin.get_future_instrument_id().upper()))


def write_price_info():
    print(time.strftime('%Y-%m-%d %X', time.localtime()))
    future_avg_price = future_ind_1s.cal_avg_price()
    spot_avg_price = spot_ind_1s.cal_avg_price()
    if spot_avg_price != 0 and future_avg_price != 0:
        diff = (future_avg_price - spot_avg_price) / spot_avg_price * 100
        info = 'time: %s, spot_price: %.3f, future_price: %.3f, diff: %.3f%%' \
               % (timestamp2string(time.time()), spot_avg_price, future_avg_price, diff)
        print(info)
        with codecs.open(coin_name + "_spot_future_diff.txt", 'a+', 'utf-8') as f:
            f.writelines(info + '\r\n')
    timer = threading.Timer(1, write_price_info)
    timer.start()


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
        thread.start_new_thread(write_price_info, ())
        while True:
            ws.run_forever(ping_interval=20, ping_timeout=10)
            print("write left lines into file...")
            with codecs.open(file_depth, 'a+', 'UTF-8') as f:
                f.flush()
                f.close()
    else:
        print('miss param...')
