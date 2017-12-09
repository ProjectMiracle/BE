#!/usr/bin/python
# -*- coding:utf-8 -*-

from snownlp import SnowNLP
from pyltp import Segmentor
from Config import *
from SentenceDeepAnalysis import *

class SimpSentClas (object):
  
  segmentor = Config().getSegmentor()

  chckWords = [u'查',u'查询',u'看',u'看看',u'多少']
  accnWords = [u'账户',u'卡',u'余额',u'银行卡',u'卡里']
  frwdWords = [u'转',u'转账',u'转钱',u'付',u'給'] 
  exchWords = [u'交易记录',u'交易']
  cnsmWords = [u'消费记录',u'消费',u'花哪里',u'花掉',u'花到哪里',u'花去哪里']
  incmWords = [u'收入记录',u'收入']

  chckCommon = []
  #frwdCommon = []
  #exchCommon = []
  #incmCommon = []
  #cnsmCommon = []

  chckfile = "/home/prin/checkcomm.txt"
  #frwdfile = "/home/prin/forwardcomm.txt"
  #exchfile = "/home/prin/exchangecomm.txt"
  #incmfile = "/home/prin/incomecomm.txt"
  #cnsmfile = "/home/prin/consumecomm.txt"

  chckfd = open (chckfile,'r')
  #frwdfd = open (frwdfile,'r')
  #exchfd = open (exchfile,'r')
  #incmfd = open (incmfile,'r')
  #cnsmfd = open (cnsmfile,'r')

  for line in chckfd:
    chckCommon.append(line)

  for line in frwdfd:
    frwdCommon.append(line)

  for line in exchfd:
    exchCommon.append(line)

  for line in incmfd:
    incmCommon.append(line)

  for line in cnsmfd:
    cnsmCommon.append(line)

  symbols = set([u'，', u'。', u'！', u'？'])
  virtualWords = set(u'吧', u'啊', u'吗', u'儿', u'请', u'帮', u'一下', u'想', u'想要', u'想让你', u'我', u'我的')

  chckopertype = 'check'
  frwdopertype = 'forward'
  exchopertype = 'exchangeRecord'
  incmopertype = 'incomeRecord'
  cnsmopertype = 'comsumeRecord'
	
  def __init__ (self):
    self.chckSentences = []
    self.frwdSentences = []
    self.incmSentences = []
    self.exchSentences = []
    self.cnsmSentences = []  


  def delNonUsedWords (self,sentence):
    for symbol in symbols:
      sentence.replace(symbol, '')
    for virtualword in virtualwords:
      sentence.replace(virtualword, '')
	return sentence 
	
  def commClass (self, sentence1):
    sentence = delNonUsedWords(sentence1)

    for line in chckCommon:
      line.replace('\n','')
      if sentence == line:
        return True
'''
    for line in frwdCommon:
      line.replace('\n','')
      if sentence == line:
        return frwdopertype

    for line in exchCommon:
      line.replace('\n','')
      if sentence == line:
        return exchopertype

    for line in incmCommon:
      line.replace('\n','')
      if sentence == line:
        return incmopertype

    for line in cnsmCommon:
      line.replace('\n','')
      if sentence == line:
        return cnsmopertype
'''
    return False


  def cutWords (self, sentence):
    #can be replaced by pyltp
    wordlist = jieba.cut(sentence, ALL_CUT=True)
    result = list(wordlist)
    return result


  def cutSentence (self, text):
    result = SnowNLP(sentence)
    sentences = result.sentences
    return sentences


  def isChckWords (self, wordlist):
    chckCata = False
    for ll in chckWords:
      for ww in wordlist:
        if ww.find(ll) != -1:
          chckCata = True 
          break
     
    accnCata = False
    for ll2 in accnWords:
      for ww2 in wordlist:
        if ww2.find(ll2) != -1:
          accnCata = True
          break
     
    if accnCata :
      return True
    else if chckCata :
      return True
    else :
      return False
 

  def isFrwdWords (self, wordlist):
    for ll in frwdWords:
      for ww in wordlist:
        if ww.find(ll) != -1:
          return True
    return False


  def isExchWords (self, wordlist):
  
    for ll in exchWords:
      for ww in wordlist:
        if ww.find(ll) != -1:
          return True
    return False
  

  def isCnsmWords (self, wordlist):
    for ll in cnsmWords:
      for ww in wordlist:
        if ww.find(ll) != -1:
          return True
    return False


  def isIncmWords (self, wordlist):
    for ll in incmWords:
      for ww in wordlist:
        if ww.find(ll) != -1:
          return True
    return False


  def getEffectSentence (self, sentences):
    for sentence in sentences:
	  commands = self.delNonUsedWords (sentence)
      wordlist = self.cutSentence(commands)
      if self.isChckWords(wordlist):
        chckSentences.append(wordlist)
      else if self.isFrwdWords(wordlist):
        frwdSentences.append(wordlist)
      else if self.isExchWords(wordlist);
        exchSentences.append(wordlist)
      else if self.isIncmWords(wordlist):
        incmSentences.append(wordlist)
      else if self.isCnsmWords(wordlist):
        cnsmSentences.append(wordlist)
      else:
        continue

  def processSentence (self, rawsentence):
    sentences = self.cutSentence(rawsentence)
	
	if (len(sentences) == 1):
	  if self.commClass(sentences[0]):
	    return [chckopertype]
		
	effsentences = self.getEffectSentence(sentences)
    if (len(chckSentences) == 0 and len(frwdSentences) ==0 and len(exchSentences) ==0 and len(cnsmSentences) ==0 and len(incmSentences) ==0):
      return ["None"]
    else-
      if len(chckSentences) :
        sda = SentenceDeepAnalysis (is_chck=True, effsentences)
		result = sda.checkAnalysis()
		return result
      if len(frwdSentences) :
        sda = SentenceDeepAnalysis (is_frwd=True, effsentences)
		result = sda.frwdAnalysis()
		return result
	  if len(exchSentences) :
        sda = SentenceDeepAnalysis (is_exch=True, effsentences)
		result = sda.checkAnalysis()
		return result
	  if len(cnsmSentence) :
	    sda = SentenceDeepAnalysis (is_exch=True, effsentences)
		result = sda.checkAnalysis()
		return result
	  if len(cnsmSentence) :
	    sda = SentenceDeepAnalysis (is_exch=True, effsentences)
		result = sda.checkAnalysis()
		return result
      return ["None"]
