#인공지능 모델인 Prophet을 이용한 비트코인 자동거래 프로그램
#작성일자 : 2021.11.21
#작성자 : 송준하

#라이브러리
import time
import pyupbit
import datetime
import schedule
import pandas as pd
from fbprophet import Prophet

#access key와 secret key
access = "your-access"
secret = "your-secret"

#로그인
upbit = pyupbit.Upbit(access, secret)

#잔고조회
def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

#전 고점을 설정하는 함수
last_max_price = 0
def get_Last_Max(coin):
    global last_max_price
    #최대 200개의 데이터를 가져올 수 있음. 200분 = 3시간 20분
    df = pyupbit.get_ohlcv(coin, interval="minute1")
    df = df.reset_index()
    #3시간 20분 중에 가장 큰 값
    max_price_date = df['high'].max()
    if max_price_date > last_max_price:
         #이 값이 전 고점
        last_max_price = max_price_date


#현재 가격을 반환하는 함수, DataFrame 형식으로 반환
current_price = 0
def get_current_price(coin):
    global current_price
    current_price = pyupbit.get_ohlcv(coin,interval = "minute1",count = 1).iloc[-1]['high']

#현재 가격이 전 고점을 넘겼는지 확인하는 함수
def upper_than_max_price():
    if current_price > last_max_price:
        return True
    return False

#고점을 찍고 내려오는지 확인
def was_top():
    time.sleep(240)
    last_3_minutes = pyupbit.get_ohlcv("KRW-BTC",interval = "minute1",count = 3).reset_index()[['index','high']]
    last_3_minutes.head()
    if last_3_minutes.iloc[2]['high'] < last_3_minutes.iloc[1]['high'] < last_3_minutes.iloc[0]['high']:
        return True
    return False

#눌림목 인지 확인
#고점을 찍고 내려온다면 1분에 한번씩 실행시킴. 4개의 행을 불러오는데 가운데에 있는 값이 양쪽의 값보다 작을 때가 눌림목임
#눌림목이 나올 때 까지 계속 실행
def was_hold():
    last_4_minutes = pyupbit.get_ohlcv("KRW-BTC",interval = "minute1",count = 4).reset_index()[['index','high']]
    if last_4_minutes.iloc[1]['high'] < last_4_minutes.iloc[0]['high'] and last_4_minutes.iloc[1]['high'] < last_4_minutes.iloc[2]['high'] < last_4_minutes.iloc[3]['high'] :
        return True
    return False


#상승세 하락세 예측
#눌림목에서 상승세면 매수 아니면 대기 이것도 1분마다 반복
def predict_price():
    last_200_df = pyupbit.get_ohlcv("KRW-BTC",interval = "minute1",).reset_index()
    last_200_df['ds'] = last_200_df['index']
    last_200_df['y'] = last_200_df['close']
    data = last_200_df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods = 30, freq = "Min")
    forecast = model.predict(future)
    forecast = forecast.reset_index()
    #십분 후 가격 나누기 현재가격, 20분 후 가격 나누기 10분 후 가격, 
    #30분 후 가격 나누기 20분 후 가격
    gradient1 = forecast.iloc[-21]['yhat'] / forecast.iloc[-31]['yhat']
    gradient2 = forecast.iloc[-11]['yhat'] / forecast.iloc[-21]['yhat']
    gradient3 = forecast.iloc[-1]['yhat'] / forecast.iloc[-11]['yhat']
    arr = [gradient1,gradient2,gradient3]
    return arr
#구매를 결정하는 함수
def buy_and_sell(arr):
    #첫번째 기울기가 양수면 매수, 음수면 10분 간격으로 이 함수 실행 ->
    #두번째 기울기가 양수면 세번째 기울기 계산 , 음수면 10분 뒤에 판매
    #세번째 기울기가 양수면 30분 뒤에 판매, 음수면 20분 뒤에 판매
    gradient1 = arr[0]
    gradient2 = arr[1]
    gradient3 = arr[2]
    #비트코인 수수료 0.0009 포함
    if gradient1 > 1.0009:
        print("매수")
        #잔고를 받아옴
        krw = get_balance("KRW")
        btc = get_balance("BTC")
        #5000원 이상 있으면
        if krw > 5000:
            #현재 잔고의 99.95%만큼 매수
            upbit.buy_market_order("KRW-BTC", krw*0.9995)
        if gradient2 > 1.0009:
            if gradient3 > 1.0009:
                if btc > 0.00008:
                    print("30분 뒤에 매도")
                    time.sleep(1800)
                    upbit.sell_market_order("KRW-BTC", btc*0.9995)
            else:
                print("20분 뒤에 매도")
                time.sleep(1200)
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        else:
            print("10분 뒤에 매도")
            time.sleep(600)
            upbit.sell_market_order("KRW-BTC", btc*0.9995)
            


get_Last_Max("KRW-BTC")
get_current_price("KRW-BTC")
schedule.every(10).minutes.do(lambda : get_Last_Max("KRW-BTC"))
schedule.every().minute.do(lambda : get_current_price("KRW-BTC"))



print("autotrade start")
while(True):
    # try:
        schedule.run_pending()
        if upper_than_max_price():
            if was_top():
              if was_hold():
                  gradients = predict_price()
                  buy_and_sell(gradients)
        time.sleep(1)
    # except Exception as e:
    #     print(e)
    #     time.sleep(1)
                


