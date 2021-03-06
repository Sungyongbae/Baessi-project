
import time
import pyupbit
import datetime
import requests

access = "access"
secret = "secret"

myToken = "xoxb-2005118006242-2011295416340-DCkEspSYeXjBn2ZO2ruQyZuX"
#기윤
#myToken = "xoxb-2405325150050-2411528692612-sCB8LjUrQdrRRB7ArfzHXxlr"


def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minutes240", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minutes240", count=1)
    start_time = df.index[0]
    return start_time

def get_ma10(ticker):
    """10개봉 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute240", count=10)
    ma10 = df['close'].rolling(10).mean().iloc[-1]
    return ma10

def get_balance(coin):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == coin:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
#post_message(myToken,"#development", "autotrade start")
post_message(myToken, "#development", "autotrade start")

check_buy_ETH = False
check_buy_XRP = False

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETH")
        end_time = start_time + datetime.timedelta(hours=4)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price_ETH = get_target_price("KRW-ETH", 0.1)
            target_price_XRP = get_target_price("KRW-XRP", 0.4)
            ma10_ETH = get_ma10("KRW-ETH")
            ma10_XRP = get_ma10("KRW-XRP")
            current_price_ETH = get_current_price("KRW-ETH")
            current_price_XRP = get_current_price("KRW-XRP")
            if check_buy_ETH == False and target_price_ETH < current_price_ETH and ma10 < current_price_ETH:
                krw = get_balance("KRW")
                real_target_ETH = round(target_price_ETH,-3)

                if check_buy_XRP == True and krw > 5000:
                    total_ETH = (krw * 0.9995) / real_target_ETH
                    buy_result_ETH = upbit.buy_limit_order("KRW-ETH", real_target_ETH, total_ETH)
                    post_message(myToken,"#development", "ETH buy : " +str(buy_result_ETH))
                    check_buy_ETH = True
                elif check_buy_XRP == False and krw > 5000:
                    total_ETH = (krw * 0.5 * 0.9995) / real_target_ETH
                    buy_result_ETH = upbit.buy_limit_order("KRW-ETH", real_target_ETH, total_ETH)
                    post_message(myToken, "#development", "ETH buy : " + str(buy_result_ETH))
                    check_buy_ETH = True

            if check_buy_XRP == False and target_price_XRP < current_price_XRP and ma10 < current_price_XRP:
                krw = get_balance("KRW")
                real_target_XRP = round(target_price_XRP,-1)

                if check_buy_ETH == True and krw > 5000:
                    total_XRP = (krw * 0.9995) / real_target_XRP
                    buy_result_XRP = upbit.buy_limit_order("KRW-XRP", real_target_XRP, total_XRP)
                    post_message(myToken,"#development", "XRP buy : " +str(buy_result_XRP))
                    check_buy_XRP = True
                elif check_buy_ETH == False and krw > 5000:
                    total_XRP = (krw * 0.5 * 0.9995) / real_target_XRP
                    buy_result_XRP = upbit.buy_limit_order("KRW-XRP", real_target_XRP, total_XRP)
                    post_message(myToken, "#development", "XRP buy : " + str(buy_result_XRP))
                    check_buy_XRP = True
        else:
            btc_ETH = get_balance("ETH")
            btc_XRP = get_balance("XRP")
            if btc_ETH > 0.0016 or btc_XRP>3.0:
                if check_buy_ETH == True:
                    sell_result_ETH = upbit.sell_market_order("KRW-ETH", btc_ETH*0.9995)
                    post_message(myToken,"#development", "ETH sell : " +str(sell_result_ETH))
                    check_buy_ETH = False
                if check_buy_XRP == True:
                    sell_result_XRP = upbit.sell_market_order("KRW-XRP", btc_XRP * 0.9995)
                    post_message(myToken, "#development", "XRP sell : " + str(sell_result_XRP))
                    check_buy_XRP = False
            else:
                uuid_ETH = buy_result_ETH['uuid']
                cancel_result_ETH = upbit.cancel_order(uuid_ETH)
                post_message(myToken,"#development", "ETH cancel : " +str(cancel_result_ETH))
                uuid_XRP = buy_result_XRP['uuid']
                cancel_result_XRP = upbit.cancel_order(uuid_XRP)
                post_message(myToken, "#development", "XRP cancel : " + str(cancel_result_XRP))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#development", e)
        time.sleep(1)
