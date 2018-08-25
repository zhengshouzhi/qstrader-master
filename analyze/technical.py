# -*- coding: utf-8 -*-
from numpy import std
from pandas import Series,DataFrame
import numpy as np
from scipy.stats import spearmanr


def smaspearmanr(closes,smaperiods):
    if(len(closes)<max(smaperiods)):
        return None
    smavaluelist = []
    smaorder = []
    for period in smaperiods:
        smavalue = np.average(closes[-period:])
        smavaluelist.append(smavalue)
    sortedsma = sorted(smavaluelist,reverse=True)

    for smavalue in sortedsma:
        ind = smavaluelist.index(smavalue)
        smaorder.append(smaperiods[ind])
    print(smaorder)
    spear = spearmanr(smaperiods,smaorder)
    return spear[0]





def cal_rsi(dates, closes, period=6):
    rsi_list = []
    rsi_str = 'rsi' + str(period)
    index = 0
    for date, close in zip(dates, closes):
        index += 1
        if index > period:
            p_sum, n_sum = 0, 0
            for i in range(index - period, index):
                if closes[i] - closes[i - 1] > 0:
                    p_sum += closes[i] - closes[i - 1]
                if closes[i] - closes[i - 1] < 0:
                    n_sum += closes[i] - closes[i - 1]
            rsi = p_sum / (p_sum + abs(n_sum)) * 100
            rsi_dic = {}
            rsi_dic['date'] = date
            rsi_dic[rsi_str] = rsi

            rsi_list.append(rsi_dic)

    return rsi_list

def get_cur_rsi(dates,closes,period=6):
    rsi_str = 'rsi' + str(period)
    rsi_list = cal_rsi(dates,closes,period)
    cur_rsi = rsi_list[-1][rsi_str]
    return cur_rsi

def cal_ema(dates, closes,  period=20):
    ema_list = []
    ema_str = 'ema' + str(period)
    index = 0
    for date,  close in zip(dates, closes):

        if index == 0:  # period:
            ema = close  # sum(closes[index - period: index]) / period
            ema_dic = {}
            ema_dic['date'] = date
            ema_dic[ema_str] = ema
            ema_list.append(ema_dic)
        else:  # if index > period:
            ema = (2 * close + (period - 1) * ema_list[-1][ema_str]) / (period + 1)
            ema_dic = {}
            ema_dic['date'] = date
            ema_dic[ema_str] = ema
            ema_list.append(ema_dic)

        index += 1
    return ema_list


def cal_macd(dates,closes, s_period=12, l_period=26, m_period=9):
    macd_list = []
    macd_str = 'macd'
    s_emas = cal_ema(dates,closes,s_period)
    l_emas = cal_ema(dates, closes, l_period)

    dif_list = []
    for s_ema, l_ema in zip(s_emas, l_emas):  # [l_period - s_period:]
        dif = s_ema['ema' + str(s_period)] - l_ema['ema' + str(l_period)]
        dif_dic = {}
        dif_dic['date'] = l_ema['date']
        dif_dic['dif'] = round(dif,3)
        dif_list.append(dif_dic)

    if len(dif_list) >= m_period:
        dif_value_list = [x['dif'] for x in dif_list]
        dea_list = cal_ema(dates, dif_value_list, m_period)

        dea_value_list = [x['ema' + str(m_period)] for x in dea_list]
        for date, dif, dea in zip(dates, dif_value_list, dea_value_list):
            macd = 2 * (dif - dea)
            macd_dic = {}
            macd_dic['date'] = date
            macd_dic['diff'] = round(dif,3)

            macd_dic['dea'] = round(dea,3)
            macd_dic[macd_str] = round(macd,3)

            macd_list.append(macd_dic)

    return macd_list

def cal_sma(dates, closes, period=20):
    ma_list = []
    ma_str = 'sma' + str(period)
    index = 0
    for date, close in zip(dates,closes):
        index += 1

        if index >= period:
            ma = sum(closes[index - period: index]) / period
            ma_dic = {}
            ma_dic['date'] = date
            ma_dic[ma_str] = ma

            ma_list.append(ma_dic)

    return ma_list

def cal_atr(dates, closes, highs,lows,period=13):
    i = 1
    TRlist = []
    while i < len(closes):
        curhigh = highs[i]
        curlow = lows[i]
        preClose = closes[i-1]
        curTR = max((curhigh-curlow),abs(curhigh-preClose),abs(curlow-preClose))
        TRlist.append(curTR)
        i += 1
    dates = dates[1:]

    atr_dic_list = cal_ema(dates,TRlist,period=period)

    return atr_dic_list

def last_atr(dates, closes, highs,lows,period=13):
    atr_dic_list = cal_atr(dates, closes, highs,lows,period=period)
    curatr = atr_dic_list[-1]['ema13']
    return curatr


def curdistosma(closes,smaperiod):
    if(len(closes)< smaperiod):
        return None
    maprice = sum(closes[-smaperiod:])/smaperiod
    absdis = closes[-1] - maprice
    perdis = (closes[-1] - maprice)*100/maprice

    return absdis, perdis,maprice

def SMA_Direction(dates,closes,smaperiod = 20,timespan = 1):
    '''
    :param dates: 日期
    :param closes: 收盘价
    :param SMAperiod: SMA周期
    :param timespan: 在SMA向前多少天计算方向，默认为1
    :return: 'up'向上，'down' 向下。
    '''
    sma_list = cal_sma(dates,closes,smaperiod)
    sma_str = 'sma' + str(smaperiod)
    if(len(sma_list)<smaperiod):
        return None
    cur_sma_dict = sma_list[len(sma_list)-1]

    cur_sma = cur_sma_dict[sma_str]
    pre_sma_dict = sma_list[len(sma_list)-timespan-1]
    pre_sma = pre_sma_dict[sma_str]

    if(cur_sma > pre_sma):
        return 'up'
    else:
        return 'down'


def EMA_Direction(dates,closes,emaperiod = 20,timespan = 1):
    '''
    :param dates: 日期
    :param closes: 收盘价
    :param emaperiod: ema周期
    :param timespan: 在ema向前多少天计算方向，默认为1
    :return: 'up'向上，'down' 向下。
    '''
    ema_list = cal_ema(dates,closes,emaperiod)
    ema_str = 'ema' + str(emaperiod)
    if (len(ema_list) < emaperiod):
        return None
    cur_ema_dict = ema_list[len(ema_list)-1]
    cur_ema = cur_ema_dict[ema_str]
    pre_ema_dict = ema_list[len(ema_list)-timespan-1]
    pre_ema = pre_ema_dict[ema_str]

    if(cur_ema > pre_ema):
        return 'up'
    else:
        return 'down'


def MACD_Direction(dates,closes,timespan = 1):
    '''
        :param dates: 日期
        :param closes: 收盘价
        :param macdperiod: macd周期
        :param timespan: 在macd向前多少天计算方向，默认为1
        :return: 'up'向上，'down' 向下。
        '''
    macd_list = cal_macd(dates, closes)
    macd_str = 'macd'

    cur_macd_dict = macd_list[len(macd_list)-1]
    cur_macd = cur_macd_dict[macd_str]
    pre_macd_dict = macd_list[len(macd_list)-timespan-1]
    pre_macd = pre_macd_dict[macd_str]

    if(cur_macd > 0 and pre_macd > 0) :
        if (cur_macd > pre_macd):
            return 'aboveup'
        else:
            return 'abovedown'
    elif (cur_macd < 0 and pre_macd < 0):
        if (abs(cur_macd) > abs(pre_macd)):
            return 'belowdown'
        else:
            return 'belowup'
    elif(cur_macd > 0 and pre_macd < 0):
        return 'upcross'
    else:
        return 'downcross'


def envelop_ratio( dates,highs, lows, closes,period=100,lowthresh = 0.9,highthresh = 0.95,smaperiod=20):
    sma_list = cal_sma(dates,closes,smaperiod)
    sma_str = 'sma' + str(smaperiod)

    sma_list = sma_list[-period:]

    dates = dates[-period:]
    highs = highs[-period:]
    lows = lows[-period:]


    bandratio = 0.03
    step = 0.002

    maxpenetration = int(period * (1-lowthresh))
    minpenetration = int(period*(1-highthresh))

    while(True):
        uppenetrationCounter = 0
        downpenetrationCounter = 0
        preCounter = None

        for date, sma_dic, high, low in zip(dates,sma_list,highs,lows):

            sma = sma_dic[sma_str]
            upband = sma * (1+bandratio)
            lowband = sma * (1-bandratio)

            
            if(high > upband):
                #print(date,sma,bandratio,high,low,upband,lowband)
                uppenetrationCounter += 1
            if(low < lowband):
                #print(date,sma,bandratio,high,low,upband,lowband)
                downpenetrationCounter += 1


            curCounter = uppenetrationCounter + downpenetrationCounter
            if(curCounter > maxpenetration):
                break


        if (preCounter is None):
            pass
        elif (preCounter < minpenetration and curCounter > maxpenetration)\
                    or(preCounter > maxpenetration and curCounter < minpenetration):
                return (uppenetrationCounter,downpenetrationCounter,None,upband,lowband)

        if(curCounter <= maxpenetration and curCounter >= minpenetration):
            return (uppenetrationCounter, downpenetrationCounter, bandratio, upband, lowband)

        elif(curCounter > maxpenetration):
            bandratio += step
            preCounter = curCounter
        elif(curCounter < minpenetration ):
            bandratio -= step
            preCounter = curCounter


def Average_Penetration(closes,period=100,smaperiod = 20):
    pass

def SMAValueZone_GX(dates,closes,shortSMA = 10,longSMA = 20):
    '''
    :param dates：日期时间序列
    :param closes: 收盘价时间序列
    :param shortSMA: 短周期均线
    :param longSMA: 长周期均线
    :return: in 在价值区内；above：价值区上；below:价值区下
    '''
    short_sma_list = cal_sma(dates,closes,shortSMA)
    long_sma_list = cal_sma(dates,closes,longSMA)
    short_ma_str = 'sma' + str(shortSMA)
    long_ma_str = 'sma' + str(longSMA)

    curClose = closes[-1]
    shortsma = short_sma_list[-1][short_ma_str]
    longsma = long_sma_list[-1][long_ma_str]

    if(shortsma >= longsma):
        if(curClose <= shortsma and curClose >= longsma ):
            rel = 'in'
        elif(curClose > shortsma):
            rel = 'above'
        elif(curClose < longsma):
            rel = 'below'
    else:
        if (curClose >= shortsma and curClose <= longsma):
            rel = 'in'
        elif (curClose > longsma):
            rel = 'above'
        elif (curClose < shortsma):
            rel = 'below'

    return rel

def ATRCounter(sATR):
    atrcountdic = {}
    atrcountdic['abovethree'] = sum(sATR>3)
    atrcountdic['twotothree'] = sum(sATR>2) - sum(sATR>3)
    atrcountdic['onetotwo'] = sum(sATR > 1) - sum(sATR > 2)
    atrcountdic['zerotoone'] = sum(sATR > 0) - sum(sATR > 1)
    atrcountdic['mabovethree'] = sum(sATR <-3)
    atrcountdic['mtwotothree'] = sum(sATR <-2) - sum(sATR <-3)
    atrcountdic['monetotwo'] = sum(sATR <-1) - sum(sATR <-2)
    atrcountdic['mzerotoone'] = sum(sATR < 0) - sum(sATR < -1)
    return atrcountdic


def get_macdpeaktrough(dates,macd,totalNum = 5):
    colNames = ['date','type','startindex','endindex','valueindex','value']
    dfpeaktrough = DataFrame([],columns=colNames)
    i = len(macd)-1
    peaktroughcounter = 0

    while(i >= 0 and peaktroughcounter < totalNum):

        curmacd = macd[i]
        endindex = i

        if(curmacd ==0):
            i -= 1
            continue
        if(curmacd < 0):
            while(curmacd <= 0 and i>=0):
                i -= 1
                curmacd = macd[i]
            startindex = i + 1

            value = min(macd[startindex:endindex+1])
            type = 'trough'
            valueindex = macd[startindex:endindex+1].index(value) + startindex
            date = dates[valueindex]

        elif(curmacd > 0):
            while (curmacd >= 0):
                i -= 1
                curmacd = macd[i]

            startindex = i + 1
            if(len(macd[startindex:endindex+1]) == 0):
                return None
            value = max(macd[startindex:endindex+1])
            type = 'peak'
            valueindex = macd[startindex:endindex+1].index(value)+startindex
            date = dates[valueindex]
        if(valueindex == len(macd)-1):
            continue
        s = Series([date,type,startindex,endindex,valueindex,value],index = colNames)
        dfpeaktrough = dfpeaktrough.append(s,ignore_index=True)
        peaktroughcounter += 1

    return dfpeaktrough

def macd_in_bulldivergence_signal(dates,macdlist):
    '''
    :param macdlist: macd值列表
    :return: 在macd的周期内，是否macd变负，回拉上穿零轴，且再变负，且右边的值比左右在（绿柱子缩短）
            是返回True，否返回False,2018-6-10加了没有右肩，即最近底的macd为正
    '''
    divstatus = {}
    divstatus['div'] = 0
    divstatus['macd'] = 0
    divstatus['period'] = 0

    if(macdlist[-1]>0 and macdlist[-1]>macdlist[-2] and macdlist[-3]>=macdlist[-2]):#没有右肩创新低的位置macd >0

        macdpeaktrough = get_macdpeaktrough(dates, macdlist)
        if (macdpeaktrough is None or len(macdpeaktrough) < 3):#or len(macdpeaktrough) < 2
            return divstatus
        if(macdpeaktrough.loc[1,'type'] =='trough'):
            divstatus['div'] = 5
            divstatus['macd'] = 5
            valueindex = int(macdpeaktrough.loc[1, 'valueindex']) #此处应该是2，但不知道为啥是2的时候，出不来结果，要改！
            divstatus['period'] = len(macdlist) - valueindex + 1

            return divstatus

    if (not(macdlist[-2]<0 and macdlist[-2]<macdlist[-1] and macdlist[-2]<=macdlist[-3])):
        return divstatus
    divstatus = macd_in_bulldivergence(dates,macdlist)
    return divstatus



def macd_in_bulldivergence(dates,macdlist):
    '''
    :param macdlist: macd值列表
    :return: 在macd的周期内，是否macd变负，回拉上穿零轴，且再变负，且右边的值比左右在（绿柱子缩短）
            是返回True，否返回False
    '''
    divstatus = {}
    divstatus['div'] = 0
    divstatus['macd'] = 0
    divstatus['period'] = 0

    macdpeaktrough = get_macdpeaktrough(dates,macdlist,totalNum=5)

    if(macdpeaktrough is None or len(macdpeaktrough) < 5 or macdpeaktrough.loc[0,'type'] =='peak'):
        return divstatus
    #各谷的深度,这里的谷是倒数
    firsttrough = abs(macdpeaktrough.loc[0,'value'])
    secondtrough = abs(macdpeaktrough.loc[2,'value'])
    thirdtrough = abs(macdpeaktrough.loc[4,'value'])
    #fourthtrough = abs(macdpeaktrough.loc[6,'value'])

    thresh = 1
    totalperiod = len(macdlist)
    if(firsttrough < secondtrough*thresh and secondtrough< thirdtrough):#'背了又背'
        divstatus['div'] = 3
        valueindex = int(macdpeaktrough.loc[4,'valueindex'])
        divstatus['period'] = totalperiod - valueindex + 1
        if(valueindex > 100 and -thirdtrough <= min(macdlist[valueindex-100:valueindex])):
            divstatus['macd'] = 2
        elif(valueindex > 50 and -thirdtrough <= min(macdlist[valueindex-50:valueindex])):
            divstatus['macd'] = 1
        return divstatus
    elif (firsttrough > secondtrough and firsttrough < thirdtrough*thresh):#与第一谷相背
        divstatus['div'] = 2
        valueindex = int(macdpeaktrough.loc[4, 'valueindex'])
        divstatus['period'] = totalperiod - valueindex + 1
        if (valueindex > 100 and -thirdtrough <= min(macdlist[valueindex - 100:valueindex])):
            divstatus['macd'] = 2
        elif (valueindex > 50 and -thirdtrough <= min(macdlist[valueindex - 50:valueindex])):
            divstatus['macd'] = 1
        return divstatus
    elif(firsttrough < secondtrough * thresh): #仅二三谷相背
        divstatus['div'] = 1
        valueindex = int(macdpeaktrough.loc[2, 'valueindex'])
        divstatus['period'] = totalperiod - valueindex + 1

        if (valueindex > 100 and -secondtrough <= min(macdlist[valueindex - 100:valueindex])):
            divstatus['macd'] = 2
        elif (valueindex > 50 and -secondtrough <= min(macdlist[valueindex - 50:valueindex])):
            divstatus['macd'] = 1
        return divstatus
    else:
        return divstatus
    '''
    elif(firsttrough < fourthtrough * thresh):#一四谷相背，奔缠论一买去，也可能是一五谷
        divstatus['div'] = 3
        valueindex = int(macdpeaktrough.loc[3, 'valueindex'])
        divstatus['period'] = totalperiod - valueindex + 1
        if (valueindex > 100 and -secondtrough <= min(macdlist[valueindex - 100:valueindex])):
            divstatus['macd'] = 2
        elif (valueindex > 50 and -secondtrough <= min(macdlist[valueindex - 50:valueindex])):
            divstatus['macd'] = 1
    '''



def in_loose_bulldivergence(indicatorvalues,period = 20):
    '''
    用于描述DIF、DEA是否在右侧未创新低
    :param indicatorvalues:
    :param period:
    :return:
    '''
    indicatorvalues = indicatorvalues[-period:]
    maxvalue = max(indicatorvalues)
    maxindex = indicatorvalues.index(maxvalue)
    if(maxindex == 0 or maxindex == len(indicatorvalues)-1):
        return False
    leftlist = indicatorvalues[0:maxindex]
    rightlist = indicatorvalues[maxindex:len(indicatorvalues)]

    leftmin = min(leftlist)
    rightmin = min(rightlist)

    if (leftmin < 0 and rightmin < 0 and rightmin > leftmin):
        return True
    else:
        return False

def smaupcrosssignal(closes,smaperiod):
    if(len(closes)< smaperiod):
        return False
    cursma = np.average(closes[-smaperiod:])
    presma = np.average(closes[-smaperiod-1:-1])
    if(closes[-1]>cursma and closes[-2]<presma):
        return True
    else:
        return False

def invaluezone(closes,shortmaper,longsmaper):
    if (len(closes) < longsmaper):
        return False
    longsma = np.average(closes[-longsmaper:])
    shortsma = np.average(closes[-shortmaper:])
    if (closes[-1] > longsma and closes[-1] < shortsma):
        return True
    else:
        return False

def get_pre_difenxing(dates,lows,totalnum=5):
    difenxinglist=[]

    icounter = 0
    i = len(lows)-2

    while i>=1:

        if(icounter>=totalnum):
            break
        if(lows[i]<lows[i+1] and lows[i]<lows[i-1]):
            fenxingdic = {}
            fenxingdic['date'] = dates[i]
            fenxingdic['low'] = lows[i]

            difenxinglist.append(fenxingdic)

            icounter += 1

        i -= 1

    return difenxinglist




