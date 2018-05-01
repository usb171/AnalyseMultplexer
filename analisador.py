#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
from threading import Thread


 #              1   2   3   4   5   6   7   8
 # Signal     | s | s | s | s | s | s | s | s |
 # Syne       | s | s | s | s | s | s | s | s |
 # Overflow   | s | s | s | s | s | s | s | s |
 # Rate(Mbps) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

class AnalyseMultplexer():

    dict_status = {
        'signal': None,
        'syne': None,
        'overflow': None,
        'rate': None,
    }

    dict_numero_linhas = {
        'signal': [64, 66, 68, 70, 72, 74, 76, 78],
        'syne': [85, 87, 89, 91, 93, 95, 97, 99],
        'overflow': [106, 108, 110, 112, 114, 116, 118, 120],
        'rate': [124, 125, 126, 127, 128, 129, 130, 131],
    }

    cores = ['gree', 'orange', 'silver']


    link = None
    path = None

    def __init__(self, link, path):
        self.link = link
        self.path = path


    def analyser(self):
        os.system('cd ' + str(self.path) + '; sudo wget ' + self.link) # Baixa uma nova página

        try:
            file = open(str(self.path) + "alarms.cgi", 'r')
            lines = file.readlines()

            for chave in self.dict_status.keys()[:3]:
                self.dict_status[chave] = map(lambda numero_linha: str(map(lambda cor: lines[numero_linha].find(cor), self.cores).index(21)), self.dict_numero_linhas[chave])

            self.dict_status['rate'] = map(lambda linha: float(''.join((ch if ch in '0123456789.-e' else ' ') for ch in lines[linha])), self.dict_numero_linhas['rate'])

            file.close()
            os.system('sudo rm ' + str(self.path) + 'alarms.*') # Limpa o arquivo baixado anteriormente


        except IOError:
            print "Erro ao abrir o arquivo ", str(self.path) + "alarms.*"
            return False

    def create_log(self):
        file_out = open(str(self.path) + "fileOut.txt", 'w')
        out = ""
        out += "Signal: " + reduce(lambda x, y: x + " " + y, self.dict_status['signal']) + str('\n')
        out += "Sync: " + reduce(lambda x, y: x + " " + y, self.dict_status['syne']) + str('\n')
        out += "Overflow: " + reduce(lambda x, y: x + " " + y, self.dict_status['overflow']) + str('\n')
        out += "Rate: " + reduce(lambda x, y: str(x) + " " + str(y), self.dict_status['rate']) + str('\n\n')
        file_out.write(out)
        file_out.close()

    def status(self):
        pass


class Th(Thread):
    def __init__ (self, tempo):
        Thread.__init__(self)
        self.tempo = tempo
    def run(self):
        while True:
            mux1 = AnalyseMultplexer(link="http://192.168.20.25/alarms.cgi", path="/etc/zabbix/AnalyseMultplexer/MUX_PAGE_1/")
            mux1.analyser()
            mux1.create_log()

            mux2 = AnalyseMultplexer(link="http://192.168.20.26/alarms.cgi", path="/etc/zabbix/AnalyseMultplexer/MUX_PAGE_2/")
            mux2.analyser()
            mux2.create_log()

            time.sleep(self.tempo)

t = Th(5)
t.start()
