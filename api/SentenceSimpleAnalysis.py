#!/usr/bin/python
# -*- coding:utf-8 -*-

from snownlp import SnowNLP
from pyltp import Segmentor
from api.Config import *
from api.SentenceDeepAnalysis import *
import logging


class SentenceSimpleAnalysis(object):
    segmentor = Config().getSegmentor()
    logger = logging.getLogger('django.request')

    chckWords = [u'查', u'查询', u'看', u'看看', u'多少', u'查查', u'告诉', u'知道', u'问', u'问问']
    accnWords = [u'账户', u'账号', u'卡', u'余额', u'银行卡', u'存折']
    frwdWords = [u'转', u'转钱', u'付', u'给', u'付给', u'打', u'转账给', u'转给', u'打给']

    exchWords = [u'交易记录', u'交易', u'记录', u'消费记录', u'消费', u'收入记录', u'收入', \
                 u'转账记录', u'交易历史', u'交易历史记录', u'支出历史', \
                 u'支出历史记录', u'收入历史', u'收入历史记录', u'转账历史', u'转账历史记录', \
                 u'花哪里', u'花掉']

    chckCommon = []
    exchCommon = []

    chckfile = "/var/www/BE/api/checkcomm.txt"
    exchfile = "/var/www/BE/api/exchangecomm.txt"

    chckfd = open(chckfile, 'r')
    exchfd = open(exchfile, 'r')

    for line in chckfd:
        chckCommon.append(line)

    for line in exchfd:
        exchCommon.append(line)

    symbols = set([u'，', u'。', u'！', u'？'])
    virtualwords = [u'吧', u'啊', u'吗', u'儿', u'请', u'帮忙', u'帮', u'一下', u'想', u'想要', u'想让你', u'我的', u'我', u'个', u'去',
                    u'到', u'还', u'是', u'里面', u'里', u'都', u'了']
    chck_del_words = [u'是', u'钱']

    def __init__(self):
        self.chckSentences = []
        self.frwdSentences = []
        self.exchSentences = []

    def __delCheckWords(self, sentence):
        temp = sentence
        for del_word in self.chck_del_words:
            temp = temp.replace(del_word, '')
        return temp

    def delNonUsedWords(self, sentence):
        for symbol in self.symbols:
            sentence = sentence.replace(symbol, '')
        for virtualword in self.virtualwords:
            sentence = sentence.replace(virtualword, '')
        return sentence

    def commClass(self, sentence1):
        sentence = self.delNonUsedWords(sentence1)
        self.logger.debug(sentence)

        for line in self.chckCommon:
            line = line.replace('\n', '')
            if sentence == line:
                return [1]
        for line in self.exchCommon:
            line = line.replace('\n', '')
            linelist = line.split('\t')
            if linelist[0] == sentence:
                result = linelist[1].split('%')
                index = 0
                for res in result:
                    if res.isdigit():
                        result[index] = int(res)
                    index += 1
                return result

        return False

    def cutWords(self, sentence):
        # can be replaced by pyltp
        wordlist = self.segmentor.segment(sentence)
        result = list(wordlist)
        return result

    def cutSentence(self, text):
        result = SnowNLP(text)
        sentences = result.sentences
        return sentences

    def isChckWords(self, wordlist):
        chckCata = False
        for ll in self.chckWords:
            for ww in wordlist:
                if ww.find(ll) != -1:
                    chckCata = True
                    break

        accnCata = False
        for ll2 in self.accnWords:
            for ww2 in wordlist:
                if ww2.find(ll2) != -1:
                    accnCata = True
                    break

        if accnCata:
            return True

        if (chckCata & accnCata):
            return True

        return False

    def isFrwdWords(self, wordlist):
        for ll in self.frwdWords:
            for ww in wordlist:
                if ww.find(ll) != -1:
                    return True
        return False

    def isExchWords(self, wordlist):
        for ll in self.exchWords:
            for ww in wordlist:
                if ww.find(ll) != -1:
                    return True
        return False

    def getEffectSentence(self, sentences):
        for sentence in sentences:
            self.logger.debug(sentence)
            commands = self.delNonUsedWords(sentence)
            wordlist = self.cutWords(commands)
            if self.isExchWords(wordlist):
                self.exchSentences.append(wordlist)
            elif self.isChckWords(wordlist):
                tempstr = "".join(wordlist)
                tempstr = self.__delCheckWords(tempstr)
                wordlist = self.cutWords(tempstr)
                self.chckSentences.append(wordlist)
            elif self.isFrwdWords(wordlist):
                self.frwdSentences.append(wordlist)
            else:
                continue

    def processSentence(self, rawsentence):
        sentences = self.cutSentence(rawsentence)
        self.logger.debug("sentences is " + str(sentences))

        if (len(sentences) == 1):
            comm_result = self.commClass(sentences[0])
            if comm_result:
                return comm_result

        self.getEffectSentence(sentences)
        # print (effsentences)

        if (len(self.chckSentences) == 0 and len(self.frwdSentences) == 0 and len(self.exchSentences) == 0):
            return [0]
        else:
            self.logger.debug("Go to further process.")
            if len(self.chckSentences):
                sda = SentenceDeepAnalysis(self.chckSentences)
                self.logger.debug("Go to checkRemainAmount")
                result = sda.checkRemainAmount(self.chckSentences)
                self.chckSentences = []
                return result
            if len(self.frwdSentences):
                sda = SentenceDeepAnalysis(self.frwdSentences)
                self.logger.debug("Go to forwardMoney")
                result = sda.forwardMoney(self.frwdSentences)
                self.frwdSentences = []
                return result
            if len(self.exchSentences):
                sda = SentenceDeepAnalysis(self.exchSentences)
                self.logger.debug("Go to checkAccountExch")
                result = sda.checkAccountExch(self.exchSentences)
                self.exchSentences = []
                return result
            return [0]


if __name__ == '__main__':
    ssa = SentenceSimpleAnalysis()
    """
    print (ssa.processSentence(u"三国演义"))
    print (ssa.processSentence(u"武松打虎"))
    print (ssa.processSentence(u"我想转账"))
    print (ssa.processSentence(u"我想查前三个月的消费记录"))
    print (ssa.processSentence(u'转给陈文一千元'))
    print (ssa.processSentence(u"转陈文500元"))
    print (ssa.processSentence(u"给陈文转一千元"))
    print (ssa.processSentence(u"我想查余额"))
    print (ssa.processSentence(u"不查余额"))
    print (ssa.processSentence(u"查最近交易记录"))
    print (ssa.processSentence(u"查最近三次交易记录"))
    print (ssa.processSentence(u"请问我的账户余额是多少"))
    print (ssa.processSentence(u"请问我的账户里面总共有多少钱"))
    print (ssa.processSentence(u"我想查一下我的账户里还有多少钱"))
    print (ssa.processSentence(u"我想查一下我的卡里还有多少钱"))
    print (ssa.processSentence(u"我想查一下我的银行卡里还有多少钱"))
    print (ssa.processSentence(u"请问我的卡里的余额是多少"))
    print (ssa.processSentence(u"请问我的银行卡里的余额是多少"))
    print (ssa.processSentence(u"请问我的存折里还有多少钱"))
    
    
    print (ssa.processSentence(u"查询余额"))
    print (ssa.processSentence(u"查最近三笔转账记录"))
    
    
    print (ssa.processSentence(u"我想查一下我的账户最近5次的交易记录"))
    print (ssa.processSentence(u"我想查一下最近的转账记录"))
    print (ssa.processSentence(u"查最近三笔转账记录"))
    
    #print (ssa.processSentence(u"我想查最近三个月我的钱都花哪了"))
  
    
    print (ssa.processSentence(u"我想付100元给陈大文"))
    print (ssa.processSentence(u"我想给陈大文100元"))
    print (ssa.processSentence(u"我想把100元给陈大文"))
    print (ssa.processSentence(u"请帮忙支付100元给陈大文"))
    print (ssa.processSentence(u"请帮忙给陈大文100元"))
    print (ssa.processSentence(u"我想转100元给陈大文"))
    print (ssa.processSentence(u"我想把100元转账给陈大文"))
  
    print (ssa.processSentence(u"查询我最近三笔转账记录"))
    print (ssa.processSentence(u"请问我的账户余额是多少"))
    print (ssa.processSentence(u"转账给小明3000块"))
    print (ssa.processSentence(u"转账给小明三千块"))
    """
    """
    print (ssa.processSentence(u"我的账号有多少钱"))
    print (ssa.processSentence(u"我的账号还有多少钱"))
    print (ssa.processSentence(u"账号余额"))
    print (ssa.processSentence(u"我的账号还剩多少"))
    print (ssa.processSentence(u"我想查一下我的银行卡的最近5次的交易历史记录"))
    """
    """
    print (ssa.processSentence(u"转100元给小明"))
    print (ssa.processSentence(u"转小明100元"))
    print (ssa.processSentence(u"转账小明100元"))
    """
