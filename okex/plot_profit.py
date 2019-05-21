#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append('..')
import codecs
import time
from base.entity import Coin
from base.utils import timestamp2string


if __name__ == '__main__':
    if len(sys.argv) > 2:
        coin_name = sys.argv[1]
        coin = Coin(coin_name, "usdt")
        instrument_id = coin.get_instrument_id()
        future_instrument_id = coin.get_future_instrument_id()
        file_transaction, file_deal = coin.gen_file_name()
        config_file = sys.argv[2]
        plot_file_name = coin.gen_plot_filename(config_file)
        if config_file == 'config_mother':
            from okex.config_mother import spotAPI
        else:
            print('输入config_file有误，请输入config_mother or config_son1 or config_son3')
            sys.exit()

        while True:
            try:
                ticker = spotAPI.get_specific_ticker(instrument_id)
                cur_price = float(ticker['last'])
                coin_account = spotAPI.get_coin_account_info(coin.name)
                coin_balance = float(coin_account['balance'])
                usdt_account = spotAPI.get_coin_account_info("usdt")
                usdt_balance = float(usdt_account['balance'])
                okdk_account = spotAPI.get_coin_account_info("okdk")
                okdk_balance = float(okdk_account['balance'])

                total_balance = coin_balance * cur_price + usdt_balance + okdk_balance * 0.17

                with codecs.open(plot_file_name, 'a+', 'UTF-8') as f:
                    cur_time_str = timestamp2string(int(time.time()))
                    profit_info = '%s cur_price: %.3f, total_account: %.3f, coin: %.3f, usdt: %.3f, okdk: %.2f' \
                                  % (cur_time_str, cur_price, total_balance, coin_balance, usdt_balance, okdk_balance)
                    print(profit_info)
                    f.writelines(profit_info + '\r\n')
                time.sleep(10)
            except Exception as e:
                print(repr(e))
    else:
        print('缺少参数 coin_name, config_file')
        print('for example: python monitor_spot etc config_mother')