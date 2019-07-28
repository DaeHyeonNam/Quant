#!/usr/bin/env python
# coding: utf-8


import math
from matplotlib import pyplot as plt

def SIMULATION(baseData,buyFilter, sellFilter, buyFunc, sellFunc, commission= True, funds = 1000000, tradeWithClosePrice=True):
    '''
    baseData: "pandas dataFrame" [-1 * 5] open, close, high, low, volume (data order should be old to new)
    buyFilter: parameter- baseData, return- filtered data
    sellFilter: parameter- baseData, return- filtered data
    buyFunc: returns integer between 0 and 100. Zero means buy nothing and hundred means buy all.
    sellFunc: returns integer between 0 and 100. Zero means sell nothing and hundred means sell all.
    commission: apply commission or not
    funds: money to start
    tradeWithClosePrice: trade with open price if it is false
    
    return: interest rate
    '''
    #--- setting env ---#
    
    coinNum = 0.0
    moneyLeft = funds
    
    if tradeWithClosePrice:
        key='close'
    else:
        key='open'
    if commission:
        commissionRate = 0.9985
    else:
        commissionRate = 1

        
    #--- buy and sell function ---#
        
    def buy(rate, price, coinNum, moneyLeft):
        moneyToBuy = (rate/100)*(price*coinNum + moneyLeft)
        if moneyLeft > moneyToBuy:
            coinNum += (moneyToBuy/price)*commissionRate
            moneyLeft -= moneyToBuy
        else:
            coinNum += (moneyLeft/price)*commissionRate
            moneyLeft = 0
        
        return (coinNum, moneyLeft)
    
    
    def sell(rate, price, coinNum, moneyLeft):
        
        moneyToSell = (rate/100)*(price*coinNum + moneyLeft)
        if (coinNum*price) > moneyToSell:
            moneyLeft += moneyToSell*commissionRate
            coinNum -= (moneyToSell/price)
        else:
            moneyLeft += (coinNum*price)*commissionRate
            coinNum = 0
            
        return (coinNum, moneyLeft)


    #--- make indicators ---#

    buyIndicator= buyFilter(baseData)
    sellIndicator= sellFilter(baseData)
    assert(len(buyIndicator)==len(sellIndicator)==len(baseData))


    #--- back testing ---#
    
    buyXPoint= []
    buyYPoint= []
    sellXPoint= []
    sellYPoint= []
    print("Back-Testing Start")
    for i in range(0,len(baseData)-3):
        if not (math.isnan(buyIndicator[i]) or math.isnan(sellIndicator[i])) :
            try:
                buyRate = buyFunc(buyIndicator, i)
                sellRate = sellFunc(sellIndicator, i)
                if math.isnan(buyRate) or math.isnan(sellRate):
                    continue
            except:
                continue

            if buyRate == 0 and sellRate == 0:
                continue
            elif buyRate >= sellRate:
                print("Buy {} rate:{}".format(i, buyRate))
                buyXPoint.append(i+1)
                buyYPoint.append(int(baseData[i+1:i+2][key]))
                coinNum, moneyLeft = buy(buyRate, int(baseData[i+1:i+2][key]), coinNum, moneyLeft)
            else:
                sellXPoint.append(i+1)
                sellYPoint.append(int(baseData[i+1:i+2][key]))
                print("Sell {} rate:{}".format(i, sellRate))
                coinNum, moneyLeft =sell(sellRate, int(baseData[i+1:i+2][key]), coinNum, moneyLeft)

    # money left at the last and calculate interest rate
    moneyLeft += coinNum * int(baseData[-2:-1][key])
    interestRate = ((moneyLeft-funds)/funds)*100

    print("\n수익률: {}\n".format(interestRate))


    #--- trading result in plot ---#
    
    Xdata = [i for i in range(0, len(baseData))]
    Ydata = [int(baseData['close'][i]) for i in range(0,len(baseData))]
    
    plt.figure(figsize = (15,10))
    plt.plot(Xdata,Ydata)
    plt.scatter(buyXPoint,buyYPoint, color='r')
    plt.scatter(sellXPoint,sellYPoint, color='b')
    plt.show()
    
    
    return interestRate



