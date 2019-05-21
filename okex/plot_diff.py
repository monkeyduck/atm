#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append('..')
import matplotlib.pyplot as plt
import codecs

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        lines = []
        with codecs.open(file_name, 'r', 'utf-8') as f:
            lines = f.readlines()
        ts_list = list(map(lambda l: l.split(",")[0].split(":", 1)[1], lines))
        spot_price_list = list(map(lambda l: float(l.split(",")[1].split(":", 1)[1]), lines))
        future_price_list = list(map(lambda l: float(l.split(",")[2].split(":", 1)[1]), lines))
        diff = list(map(lambda l: float(l.split(",")[3].split(":", 1)[1].strip().split('%')[0]), lines))
        fig = plt.figure(figsize=(10, 6))

        ax1 = fig.add_subplot(2, 1, 1)
        ax1.plot(spot_price_list, 'red')
        ax1.plot(future_price_list, 'blue')
        ax2 = fig.add_subplot(2, 1, 2)
        ax2.plot(diff, 'black')
        plt.show()

    # if len(sys.argv) > 1:
    #     file_name = sys.argv[1]
    # with codecs.open(file_name, 'r', 'utf-8') as f:
    #     lines = f.readlines()
    #     for line in lines:
