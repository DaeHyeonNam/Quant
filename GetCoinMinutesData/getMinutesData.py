import requests as r
import json
import time
import datetime
import os
from fake_useragent import UserAgent

#--- wireless module only works in linux ---#
linux = False

if linux:
    from wireless import Wireless

    wire = Wireless()

    #--- wifi setting ---# 
    # By using various wifi, we can use various IP! 
    wifi = [ "iptime","Redmi"]
    pw = ["00000000","12345678"]
    wifiNum=len(wifi)


#--- running setting ---#
ticker = "krw-btc"
# be careful with the form!
from_ = "2013-04-10 00:00:00"
to_ = "2019-07-28 00:00:00"


dataSaveFolder = "./minutesData"
dataSaveFile = "./minutesData/"+ticker+".csv"

if not os.path.isdir(dataSaveFolder):
    os.mkdir(dataSaveFolder)
    
#--- wifi initializing ---#
if linux:
    wire.connect(ssid=wifi[1], password= pw[1])
    time.sleep(3)

#--- session initializing ---#
session = r.Session()

ua = UserAgent()
http_header = {
    #by using ua.random, we can get random user agent. it prevents IP blocking
    'user-agent': str(ua.random),
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
}
    
session.headers.update(http_header)


def COOKIE_UPDATE():
    '''
    COOKIE UPDATE TO PREVENT EXPIRING
    '''

    global session
    global http_header

    session = r.Session()

    ua = UserAgent()
    http_header = {
        'user-agent': str(ua.random),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    session.headers.update(http_header)
        
    url = "https://api.upbit.com/v1/candles/minutes/1?market=krw-btc&to=2017-11-11T00:00:00Z&count=200"
    res = session.get(url)
    print(res)


#--- time out decorator ---#
# it also only works for linux
if linux:
    from functools import wraps
    import errno
    import os
    import signal

    class TimeoutError(Exception):
        pass

    def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
        def decorator(func):
            def _handle_timeout(signum, frame):
                raise TimeoutError(error_message)

            def wrapper(*args, **kwargs):
                signal.signal(signal.SIGALRM, _handle_timeout)
                signal.alarm(seconds)
                try:
                    result = func(*args, **kwargs)
                finally:
                    signal.alarm(0)
                return result

            return wraps(func)(wrapper)

        return decorator



#--- Data Crawling ---#

searchBaseUrl = "https://api.upbit.com/v1/candles/minutes/1?market="+ticker+"&to={Y}-{M}-{D}T{h}:{m}:{s}Z&count=200"


# @timeout(10) if you use linux, use it.
def GET_200_MINS_DATA(Y_, M_, D_, h_, m_, s_):
    '''
    Y_:year(str)
    M_:month(str)
    D_:day(str)
    h_:hour(str)
    m_:minute(str)
    s_:second(str)
    '''
    res = session.get(searchBaseUrl.format(Y=Y_, M=M_, D=D_, h= h_, m=m_, s=s_)).text
    resDict = json.loads(res)

    minData = []
    for dict_ in resDict:
        elem = [dict_["candle_date_time_kst"], dict_["opening_price"], dict_["trade_price"], dict_["high_price"], dict_["low_price"], dict_["candle_acc_trade_volume"]]
        minData.append(elem)

    return minData


def CSV_APPEND(data):
    '''
    data: [-1 * 6] (date_time_time_kst,open, close, high, low, volume)
    '''
    with open(dataSaveFile, mode= 'a', encoding= "UTF-8") as f:
        for i in range(0, len(data)):
            for j in range(0, len(data[i])):
                f.write(str(data[i][j]))
                if j == len(data[i]) -1:
                    f.write("\n")
                else:
                    f.write(",")


if __name__ == "__main__":
    print("start")
    startDate = datetime.datetime.strptime(to_, "%Y-%m-%d %H:%M:%S")
    endDate = datetime.datetime.strptime(from_, "%Y-%m-%d %H:%M:%S")

    processDate = startDate
    count=0
    if linux:
        wifiCount=0
    while(processDate > endDate):
        print("{}days data are saved".format((count*200)/(24*60)))
        while True: # If Get method returns Error, it updates cookie and try again until it success 
            try:
                data = GET_200_MINS_DATA(processDate.strftime('%Y'), processDate.strftime('%m'),   processDate.strftime('%d'), processDate.strftime('%H'), processDate.strftime('%M'), processDate.strftime('%S'))
            except Exception as ex:
                print(ex)
                COOKIE_UPDATE()
                time.sleep(1)
                pass
            else:
                break

        CSV_APPEND(data)
        processDate = processDate - datetime.timedelta(minutes = 200)
        time.sleep(0.2)
        count+=1

        if count % 150 == 0: # every 150 times, take a rest for not being blocked.
            while True:
                try:
                    if linux: # if linux, change wifi which means changing IP to not be blocked.
                        wire.connect(ssid=wifi[wifiCount%wifiNum], password= pw[wifiCount%wifiNum])
                        wifiCount+=1
                    time.sleep(3)
                    COOKIE_UPDATE()
                    time.sleep(3)
                except:
                    time.sleep(1)
                    pass
                else:
                    break
