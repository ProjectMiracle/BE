#!/usr/bin/python
# -*- encoding:utf-8 -*-

from pyltp import Segmentor, Postagger, NamedEntityRecognizer, Parser
import os
import logging
from api.Config import *


class SentenceDeepAnalysis(object):
    config = Config()
    logger = logging.getLogger('django.request')

    segmentor = config.getSegmentor()
    parser = config.getParser()
    postagger = config.getPostagger()
    recognizer = config.getNameRecognizer()
    chech_verbs = [u'查', u'查询', u'看', u'看看', u'多少', u'查查', u'问问', u'问', u'有', u'剩']
    negative_advs = [u'不', u'别', u'非', u'否', u'不该', u'勿']
    question_words = [u'为什么', u'怎么', u'怎么就', u'为何', u'如何']
    accn_words = [u'账户', u'卡', u'余额', u'银行卡', u'卡里', u'多少', u'存折']
    pls_words = [u'给', u'把']
    frwd_words = [u'转', u'转账', u'转钱', u'付', u'給', u'付给', u'打', u'转给', u'打给', u'花', u'收入', u'支付']
    exch_words = [u'交易记录', u'交易', u'记录', u'消费记录', u'消费', u'收入记录', u'收入', u'哪', u'钱']

    num_words = [u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'十一', u'十二']
    unit_words = [u'万', u'千', u'百', u'十']
    time_units = [u'年', u'月', u'天', u'日', u'次', u'笔']
    eng_time_units = ['y', 'm', 'd', 'd', 't', 't']
    time_pos_pat = [('nd', 'nt'), ('nt',), ('nd',), ('nt', 'nt')]
    nd_keywords = [u'前', u'上', u'最近', u'近']

    rela_vob = 'VOB'
    rela_iob = 'IOB'
    rela_sob = 'SOB'
    rela_pob = 'POB'

    rela_sbv = 'SBV'
    rela_att = 'ATT'
    chck_att_1 = [u'账户', u'卡里', u'银行卡', u'存折', u'卡', u'钱']
    chck_att_2 = [u'余额', u'多少', u'钱']

    def __init__(self, effSentence):
        self.sentence = effSentence
        self.username = ''

    def __concatSeq(self, seq):
        concated_seq = None
        if seq:
            if (len(seq) > 1):
                concated_seq = " ".join(seq)
            else:
                concated_seq = seq[0]
        return concated_seq

    def __ifSeqinSeq(self, seqstr1, seqstr2):
        matchpos = seqstr1.find(seqstr2)
        if matchpos >= 1:
            return matchpos - 1
        else:
            return "None"

    def __getSpeciPos(self, words, pos, po_char):
        speci_words = []
        index = 0
        for po in pos:
            if po == po_char:
                speci_words.append(words[index])
            index = index + 1
        return speci_words

    def __getTimeUnit(self, nt_word):
        index = 0
        for time_unit in self.time_units:
            if nt_word.find(time_unit) != -1:
                return self.eng_time_units[index]
            index = index + 1
        return "None"

    def __getTimeUnit2(self, nt_word):
        index = 0
        for time_unit in self.time_units:
            if nt_word.find(time_unit) != -1:
                return self.time_units[index]
            index = index + 1
        return "None"

    def __timeToList(self, nt_word):
        to_list = []
        word = nt_word
        time_unit = self.__getTimeUnit(word)
        time_unit2 = self.__getTimeUnit2(word)
        if time_unit != "None":
            to_list.insert(0, time_unit)
            word = word.replace(time_unit2, '')
            # print (word)
            num = self.__mapWordNum(word)
            to_list.insert(0, num)
            return to_list
        else:
            return None

    def __getQuaWords(self, words, pos):
        m_words = []
        if words and pos:
            index = 0
            for po in pos:
                if po == 'm':
                    m_words.append(words[index])
                index += 1
        return m_words

    def __getQuaUnits(self, words, pos):
        q_words = []
        if words and pos:
            index = 0
            for po in pos:
                if po == 'q':
                    q_words.append(words[index])
                index += 1
        return q_words

    # time_pos_pat = [('m', 'm', 'q', 'nt', 'nt'),('m', 'q', 'nt', 'nt'),('m', 'q', 'nt'),('nt', 'nt', 'nt'),('nt','nt'),('nd','nt'),('nt')]
    def __getTimeInfo(self, words, pos):
        nt_words = self.__getSpeciPos(words, pos, 'nt')
        nd_words = self.__getSpeciPos(words, pos, 'nd')

        if (len(nd_words) > 1 or len(nt_words) > 1):
            return ["None", "无法定位到您想要的时间点"]

        if (len(nd_words) == 1) and (nd_words[0] in self.nd_keywords):
            if len(nt_words) == 1:
                time_list = self.__timeToList(nt_words[0])
                return time_list
            else:
                return ["None", "无法定位到您想要的时间点"]

        if (len(nd_words) == 1 and len(nt_words) == 0 and nd_words[0] in self.nd_keywords) \
                or (len(nt_words) == 1 and len(nd_words) == 0 and nt_words[0] in self.nd_keywords):
            m_words = self.__getQuaWords(words, pos)
            q_words = self.__getQuaUnits(words, pos)
            self.logger.debug(pos)
            self.logger.debug(self.__concatSeq(q_words))
            if (len(m_words) == 1 and len(q_words) == 1):
                m_num = self.__mapWordNum(m_words[0])
                q_num = self.__getTimeUnit(q_words[0])
                return [m_num, q_num]

        return ["None", "无法定位到您想要的时间点"]

    def __getNameinSent(self, words, pos):
        names = self.recognizer.recognize(words, pos)
        pers_name = []
        index = 0
        for name in names:
            if name == 'S-Ni' or name == 'S-Nh':
                pers_name.append(words[index])
            index = index + 1
        index = 0
        if len(pers_name) == 0:
            for po in pos:
                if po == 'nh':
                    pers_name.append(words[index])
                index = index + 1
        return pers_name

    def __getVerbinSent(self, words, pos):
        index = 0
        verbs = []
        for po in pos:
            if po == 'v':
                verbs.append(words[index])
            index = index + 1
        return verbs

    def __getAdvinSent(self, words, pos):
        index = 0
        advs = []
        for po in pos:
            if po == 'd':
                advs.append(words[index])
            index = index + 1
        return advs

    def __getPlsinSent(self, words, pos):
        index = 0
        advs = []
        for po in pos:
            if po == 'p':
                advs.append(words[index])
            index = index + 1
        return advs

    def __getRawSentence(self, words):
        sentence = ''
        for word in words:
            sentence = sentence + str(word)
        return sentence

    def __getWordRelation(self, words, pos):
        arcs = self.parser.parse(words, pos)
        return arcs

    def __getAllRelation(self, arcs):
        all_relation = []
        if arcs:
            for arc in arcs:
                all_relation.append(arc.relation)
        return all_relation

    def __getRelationID(self, arcs, relation):
        relay_ids = []
        index = 0
        for arc in arcs:
            if arc.relation == relation:
                relay_ids.append(index)
            index = index + 1
        return relay_ids

    def __getRelationHead(self, words, arcs, relay_id):
        return words[arcs[relay_id].head - 1]

    def __getPostags(self, words):
        return self.postagger.postag(words)

    def __checkFrwdAmount(self, words, pos):
        frwd_amount = []
        m_word = ''
        index = 0
        for po in pos:
            if po == 'm':
                m_word = words[index]
                if m_word.find(u'元') or m_word.find(u'块'):
                    m_word = m_word.replace('元', '')
                    m_word = m_word.replace('块', '')
                    frwd_amount.append(m_word)
                else:
                    frwd_amount.append(m_word)
            index = index + 1
            # print (m_word)
        return frwd_amount

    def __mapWordNum(self, amount_word):
        index = 0;
        if (amount_word.isdigit()):
            return amount_word
        if (amount_word == u'两'):
            return 2
        if not (amount_word):
            return 1
        for num_word in self.num_words:
            if num_word == amount_word:
                return index
            index = index + 1
        return None

    def __mapUnitNum(self, word):
        if word == u'万':
            return 10000
        if word == u'千':
            return 1000
        if word == u'百':
            return 100
        if word == u'十':
            return 10
        if word == u'零':
            return 0

    def __convertToNumber(self, amount_word):
        if (amount_word.isdigit()):
            return amount_word
        word = amount_word[::-1]
        word = list(word)
        amount = 0;
        if word[0] in self.num_words:
            amount += self.__mapWordNum(word[0])
            word.pop(0)
        while (len(word)):
            unit_word = word[0]
            num_word = word[1]
            unit_amount = self.__mapUnitNum(unit_word)
            num_amount = self.__mapWordNum(num_word)
            total_amount = unit_amount * num_amount
            amount += total_amount
            if (unit_word == u'零'):
                word.pop(0)
            else:
                word.pop(0)
                word.pop(0)
        return total_amount

    def checkRemainAmount(self, sentences):
        self.logger.debug(sentences)
        for sentence in sentences:
            pos = self.__getPostags(sentence)
            person = self.__getNameinSent(sentence, pos)
            rawsentence = self.__getRawSentence(sentence)
            arcs = self.__getWordRelation(sentence, pos)
            arc_relations = self.__getAllRelation(arcs)

            if (len(person) > 1):
                return [99, "你不可能查两个人的余额"]
            if (len(person) != 0 and person[0] != self.username):
                return [99, "你不可能查别人的余额"]
            verbs = self.__getVerbinSent(sentence, pos)
            self.logger.debug(verbs)
            advs = self.__getAdvinSent(sentence, pos)
            # print (advs)
            if self.rela_vob in arc_relations and verbs:
                for verb in verbs:
                    if verb in self.chech_verbs:
                        vob_relation_id = self.__getRelationID(arcs, self.rela_vob)
                        for id in vob_relation_id:
                            vob_relation_head = self.__getRelationHead(sentence, arcs, id)
                            self.logger.debug(vob_relation_head)
                            for adv in advs:
                                adv_verb = str(adv) + str(verb)
                                adv_verb2 = str(verb) + str(adv)
                                if rawsentence.find(adv_verb) == -1 and rawsentence.find(adv_verb2) == -1:
                                    continue
                                else:
                                    if adv in self.negative_advs:
                                        return [99, "您不想查询余额"]
                                    else:
                                        continue
                            self.logger.debug("To here!")
                            if sentence[id] in self.accn_words and vob_relation_head == verb:
                                return [1]
                                # index += 1

            if self.rela_att in arc_relations:
                att_relation_id = self.__getRelationID(arcs, self.rela_att)
                for id in att_relation_id:
                    att_relation_head = self.__getRelationHead(sentence, arcs, id)
                    if (sentence[id] in self.chck_att_1 and att_relation_head in self.chck_att_2) or \
                            (sentence[id] in self.chck_att_2 and att_relation_head in self.chck_att_2):
                        return [1]

            if self.rela_sbv in arc_relations:
                sbv_relation_id = self.__getRelationID(arcs, self.rela_sbv)
                for id in sbv_relation_id:
                    sbv_relation_head = self.__getRelationHead(sentence, arcs, id)
                    if (sentence[id] in self.chck_att_1 and sbv_relation_head in self.chck_att_2) or \
                            (sentence[id] in self.chck_att_2 and sbv_relation_head in self.chck_att_2):
                        return [1]

        return [99, "您给的指令有误"]

    def forwardMoney(self, sentences):
        self.logger.debug(sentences)
        for sentence in sentences:
            pos = self.__getPostags(sentence)
            person = self.__getNameinSent(sentence, pos)
            rawsentence = self.__getRawSentence(sentence)
            arcs = self.__getWordRelation(sentence, pos)

        if len(person) == 0:
            return [99, "不知道您要转账给谁"]
        else:
            verbs = self.__getVerbinSent(sentence, pos)
            pls = self.__getPlsinSent(sentence, pos)
            advs = self.__getAdvinSent(sentence, pos)
            for pl in pls:
                verbs.insert(0, pl)
            self.logger.debug(verbs)
            for verb in verbs:
                if verb in self.frwd_words or verb == u'给':
                    self.logger.debug("verbs " + verb + " is in frwd_words")

                    # print (vob_relation_id)

                    # print (vob_relation_head)
                    for adv in advs:
                        adv_verb = str(adv) + str(verb)
                        adv_verb2 = str(verb) + str(adv)
                        if rawsentence.find(adv_verb) == -1 or rawsentence.find(adv_verb2) == -1:
                            continue
                        else:
                            if adv in self.negative_advs:
                                return [99, "您不转账"]
                            else:
                                continue

                    vob_relation_id = self.__getRelationID(arcs, self.rela_vob)
                    if vob_relation_id:
                        # print ("VOB on " + str(vob_relation_id))
                        # print ("OBJ is " + str(sentence[vob_relation_id[0]]))
                        for id in vob_relation_id:
                            vob_relation_head = self.__getRelationHead(sentence, arcs, id)
                            if (sentence[id].find(u'元') != -1 or sentence[id].find(u'块') != -1 or sentence[
                                id].isdigit()) and vob_relation_head == verb:
                                frwd_amount = self.__checkFrwdAmount(sentence, pos)
                                self.logger.debug(frwd_amount)
                                if len(frwd_amount) != 1:
                                    return [99, "缺失转账金额或没有转账金额"]
                                amount = self.__convertToNumber(frwd_amount[0])
                                return [3, person[0], amount]

            pob_relation_id = self.__getRelationID(arcs, self.rela_pob)
            if pob_relation_id:
                pob_relation_head = self.__getRelationHead(sentence, arcs, pob_relation_id[0])
                self.logger.debug("POB on " + str(pob_relation_id))
                self.logger.debug("OBJ is " + str(sentence[pob_relation_id[0]]))
                if (sentence[pob_relation_id[0]].find(u'元') != -1 or sentence[pob_relation_id[0]].find(u'块') != -1 or
                        sentence[pob_relation_id[0]].isdigit()) and pob_relation_head == pls[0]:
                    frwd_amount = self.__checkFrwdAmount(sentence, pos)
                    self.logger.debug(frwd_amount)
                    if len(frwd_amount) != 1:
                        return [99, "缺失转账金额或没有转账金额"]
                    amount = self.__convertToNumber(frwd_amount[0])
                    return [3, person[0], amount]
        return [99, "您给的指令有误"]

    def checkAccountExch(self, sentences):
        for sentence in sentences:
            pos = self.__getPostags(sentence)
            person = self.__getNameinSent(sentence, pos)
            rawsentence = self.__getRawSentence(sentence)
            arcs = self.__getWordRelation(sentence, pos)
            arc_relations = self.__getAllRelation(arcs)

            if (len(person) > 1):
                return [99, "你不可能查两个人的交易记录"]
            if (len(person) != 0 and person[0] != self.username):
                return [99, "你不可能查别人的交易记录"]
            verbs = self.__getVerbinSent(sentence, pos)
            advs = self.__getAdvinSent(sentence, pos)
            if self.rela_vob in arc_relations and verbs:
                for verb in verbs:
                    if verb in self.chech_verbs:
                        for adv in advs:
                            adv_verb = str(adv) + str(verb)
                            adv_verb2 = str(verb) + str(adv)
                            if rawsentence.find(adv_verb) == -1 and rawsentence.find(adv_verb2) == -1:
                                continue
                            else:
                                if adv in self.negative_advs:
                                    return [99, "您不想查询交易记录"]

                    vob_relation_id = self.__getRelationID(arcs, self.rela_vob)
                    for id in vob_relation_id:
                        vob_relation_head = self.__getRelationHead(sentence, arcs, id)
                        if vob_relation_id:
                            if sentence[id] in self.exch_words and vob_relation_head == verb:
                                for pat in self.time_pos_pat:
                                    seq_pat = self.__concatSeq(pat)
                                    # print (seq_pat)
                                    sentence_pat = self.__concatSeq(pos)
                                    # print (sentence_pat)
                                    if self.__ifSeqinSeq(sentence_pat, seq_pat) != "None":
                                        time_result = self.__getTimeInfo(sentence, pos)
                                        self.logger.debug(time_result)
                                        if time_result[0] == "None":
                                            return [99, time_result[1]]
                                        else:
                                            return [2, time_result[0], time_result[1]]
                    return [99, "指令不对，无法完成收入查询操作"]

        return [99, "指令不明确，无法完成收入查询操作"]
