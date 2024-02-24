import json
from SmartApi import SmartConnect
import requests
import pandas as pd
import datetime
import http.client

import pyotp
token= ""


def angelbrok_login():
    try:
        global feedToken, client_code, obj, password, bToken
        password = ""
        client_code = ""
        obj = SmartConnect(api_key="")

        data = obj.generateSession(
            client_code, password, pyotp.TOTP(token).now())
        # print(data)
        # refreshToken = data['data']['refreshToken']
        # userProfile= obj.getProfile(refreshToken)
        # print (dict(userProfile))
        print("\nSession Started!")

        print("Client code is :", data['data']['clientcode'],
              "\nUser name is :", data['data']['name'])
        feedToken = obj.getfeedToken()
        bToken = data['data']['jwtToken']

        print("\nLogin succesfull!")
    except Exception as e:
        print("Error in login", e)


angelbrok_login()


def get_capital():
    try:

        conn = http.client.HTTPSConnection(
            "apiconnect.angelbroking.com"
        )
        payload = ''
        headers = {
            'Authorization': bToken,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': 'CLIENT_LOCAL_IP',
            'X-ClientPublicIP': 'CLIENT_PUBLIC_IP',
            'X-MACAddress': 'MAC_ADDRESS',
            'X-PrivateKey': 'OzdlFS1e'
        }
        conn.request("GET",
                     "/rest/secure/angelbroking/user/v1/getRMS",
                     payload,
                     headers)

        res = conn.getresponse()
        data = res.read()
        # print(type(data.decode("utf-8")))
        res = json.loads(data.decode("utf-8"))
        capital = int(float(res['data']['availablecash']))
        print(capital)
        return capital

    except Exception as e:
        print("Error in getting capital", e)


get_capital()


def get_instruments():
    global instrument_df
    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    request = requests.get(url=url, verify=False)
    data = request.json()
    instrument_df = pd.DataFrame(data)
    instrument_df.to_csv("instruments.csv")
    instrument_df.set_index("symbol", inplace=True)
    return instrument_df


instrument_df = get_instruments()
# print(instrument_df)


def get_token_and_exchange(name):
    symboltoken = instrument_df.loc[name]['token']
    exchange = instrument_df.loc[name]['exch_seg']
    return symboltoken, exchange


def get_ohlc(name, exchange):
    symboltoken = instrument_df.loc[name]['token']
    ohlc_data = obj.ltpData(exchange, name, symboltoken)
    ohlc_data = ohlc_data['data']
    return ohlc_data


def get_ltp(name, exchange):
    symboltoken = instrument_df.loc[name]['token']
    ltp_data = obj.ltpData(exchange, name, symboltoken)
    ltp = ltp_data['data']['ltp']
    return ltp


def get_historical_data(name, interval, timeperiod):

    token, exchange = get_token_and_exchange(name)

    try:
        intervals_dict = {'1min': 'ONE_MINUTE', '3min': 'THREE_MINUTE', '5min': 'FIVE_MINUTE', '10min': 'TEN_MINUTE',
                          '15min': 'FIFTEEN_MINUTE', '30min': 'THIRTY_MINUTE', 'hour': 'ONE_HOUR', 'day': 'ONE_DAY'}
        todate = str(datetime.datetime.now())[:16]
        from_date = str(datetime.datetime.now().date() -
                        datetime.timedelta(days=timeperiod))+" "+"09:15"
        symboltoken = instrument_df.loc[name]['token']
        historicParam = {"exchange": exchange, "symboltoken": symboltoken,
                         "interval": intervals_dict[interval], "fromdate": from_date,  "todate": todate}
        response = obj.getCandleData(historicParam)
        dict1 = {}
        historic_df = pd.DataFrame()
        for data in response['data']:
            dict1['date'] = data[0]
            dict1['open'] = data[1]
            dict1['high'] = data[2]
            dict1['low'] = data[3]
            dict1['close'] = data[4]
            dict1['volume'] = data[5]
            # historic_df = historic_df.append(dict1, ignore_index=True)
            historic_df = pd.concat(
                [historic_df, pd.DataFrame([dict1])], ignore_index=True)

        return historic_df
    except Exception as e:
        print(e)


def place_order(token, symbol, qty, buy_sell, ordertype, price, variety='NORMAL', exch_seg='NSE', triggerprice=0):
    try:
        orderparams = {
            "variety": variety,
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": buy_sell,
            "exchange": exch_seg,
            "ordertype": ordertype,
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": price,
            "squareoff": "0",
            "stoploss": "0",
            "quantity": qty,
            "triggerprice": triggerprice
        }
        orderId = obj.placeOrder(orderparams)
        print("The order id is: {}".format(orderId))
        return orderId
    except Exception as e:
        print("Order placement failed:")


print("ready")


watchlist = ['ADANIPORTS-EQ', 'APOLLOTYRE-EQ', 'ASHOKLEY-EQ', 'AXISBANK-EQ', 'BAJFINANCE-EQ', 'BAJAJFINSV-EQ', 'BANDHANBNK-EQ', 'BANKBARODA-EQ', 'BHEL-EQ', 'BPCL-EQ', 'CANFINHOME-EQ', 'CANBK-EQ', 'CHOLAFIN-EQ', 'COFORGE-EQ', 'DLF-EQ', 'ESCORTS-EQ', 'FEDERALBNK-EQ', 'GODREJPROP-EQ', 'GRASIM-EQ', 'HINDALCO-EQ', 'ICICIBANK-EQ', 'ICICIPRULI-EQ', 'IDFCFIRSTB-EQ', 'IBULHSGFIN-EQ', 'INDUSINDBK-EQ', 'JSWSTEEL-EQ', 'JINDALSTEL-EQ', 'L&TFH-EQ', 'LICHSGFIN-EQ', 'M&MFIN-EQ', 'MANAPPURAM-EQ', 'MARUTI-EQ', 'MFSL-EQ', 'MUTHOOTFIN-EQ', 'NMDC-EQ',
             'PEL-EQ', 'PFC-EQ', 'RBLBANK-EQ', 'RADICO-EQ', 'SBIN-EQ', 'SAIL-EQ', 'TATAMOTORS-EQ', 'TATASTEEL-EQ', 'UJJIVAN-EQ', 'VEDL-EQ', 'ACC-EQ', 'ASIANPAINT-EQ', 'BAJAJ-AUTO-EQ', 'BOSCHLTD-EQ', 'BRITANNIA-EQ', 'CIPLA-EQ', 'COALINDIA-EQ', 'COLPAL-EQ', 'DABUR-EQ', 'DRREDDY-EQ', 'HCLTECH-EQ', 'HDFCBANK-EQ', 'HEROMOTOCO-EQ', 'HINDUNILVR-EQ', 'ITC-EQ', 'IOC-EQ', 'INFY-EQ', 'KOTAKBANK-EQ', 'LT-EQ', 'MARICO-EQ', 'NTPC-EQ', 'NESTLEIND-EQ', 'PIDILITIND-EQ', 'POWERGRID-EQ', 'RELIANCE-EQ', 'TCS-EQ', 'TECHM-EQ', 'ULTRACEMCO-EQ', 'WIPRO-EQ']

name = 'RBLBANK-EQ'
exchange = "NSE"

token, exchange = get_token_and_exchange(name)

# no of shares to purchase
qty = 3
res1 = place_order(
    token, name, qty, 'SELL', 'MARKET', 0)  # sell order

# for buy order
# res1 = ab.place_order(
#     token, name, qty, 'BUY', 'MARKET', 0)  # sell order
print(res1)
