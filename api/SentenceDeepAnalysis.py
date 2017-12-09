#!/usr/bin/python
#-*- coding:utf-8 -*-

from pyltp import Segmentor, Postagger, NamedEntityRecognizer, Parser
import os

class SentenceDeepAnalysis (object):
   
  ltp_data_dir = '/home/prin/pyltp'
  ltp_seg_model = 'cws.model'
  ltp_pos_model = 'pos.model'
  ltp_ent_model = 'ner.model'
  ltp_par_model = 'parser.model'

  seg_model_path = os.path.join(ltp_data_dir, ltp_seg_model)
  pos_model_path = os.path.join(ltp_data_dir, ltp_pos_model)
  ent_model_path = os.path.join(ltp_data_dir, ltp_ent_model)
  par_model_path = os.path.join(ltp_data_dir, ltp_par_model)

  segmentor = Segmentor()
  segmentor.load(seg_model_path)
  postagger = Postagger()
  postagger.load(pos_model_path)
  entityrecognizer = NamedEntityRecognizer()
  entityrecognizer.load(ent_model_path)
  parser = Parser()
  parser.load(par_model_path)

  def __init__ (self):
    pass

  
