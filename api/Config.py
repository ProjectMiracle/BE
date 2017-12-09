#!/usr/bin/python
# -*- coding:utf-8 -*-

from pyltp import Segmentor, Postagger, NamedEntityRecognizer, Parser
import os

class Config(object):
  ltp_data_dir = "/home/prin/pyltp"
  seg_model = "cws.model"
  par_model = "parser.model"
  pos_model = "pos.model"
  ner_model = "ner.model"
  
  c_segmentor = None
  c_parser = None
  c_postagger = None
  c_namerecognizer = None
  
  @classmethod
  def getSegmentor(self) :
    if Config.c_segmentor != None:
      return Config.c_segmentor
    else :
      seg_model_path = os.path.join(Config.ltp_data_dir , Config.seg_model)
      Config.c_segmentor = Segmentor()
      Config.c_segmentor.load(seg_model_path)
      return Config.c_segmentor

  @classmethod
  def getParser(self) :
    if Config.c_parser != None :
      return Config.c_parser
    else :
      par_model_path = os.path.join(Config.ltp_data_dir , Config.par_model)
      Config.c_parser = Parser()
      Config.c_parser.load(par_model_path)
      return Config.c_parser
	  
  @classmethod
  def getPostagger(self) :
    if Config.c_postagger :
      return Config.c_postagger
    else :
      pos_model_path = os.path.join(Config.ltp_data_dir , Config.pos_model)
      Config.c_postagger = Postagger()
      Config.c_postagger.load(pos_model_path)
      return Config.c_postagger

  @classmethod
  def getNameRecognizer (self) :
    if Config.c_namerecognizer :
      return Config.c_namerecognizer
    else :
      ner_model_path = os.path.join(Config.ltp_data_dir , Config.ner_model)
      Config.c_namerecognizer = NamedEntityRecognizer()
      Config.c_namerecognizer.load(ner_model_path)
      return Config.c_namerecognizer
  
if __name__ == '__main__' :
  config = Config()
  config.getSegmentor()
  config.getPostagger()
  config.getNameRecognizer()
  config.getParser()
