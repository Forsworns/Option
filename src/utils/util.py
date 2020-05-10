import pandas as pd

def amount_filter(x):
    if 'M' in x:
        x = float(x[:-1])*1 # 000000
    elif 'B' in x:
        x = float(x[:-1])*100 # 000000
    else:
        x = float(x)
    return x

def rate_filter(x):
    return float(x.strip('%'))/100

def load_data(cfg):
    df = pd.read_csv(cfg.data_file)
    df['Date'].replace('年', '/', regex=True, inplace=True)
    df['Date'].replace('月', '/', regex=True, inplace=True)
    df['Date'].replace('日', '', regex=True, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date'] = df['Date'].dt.date
    df['amount'] = df['amount'].map(amount_filter)
    df['rate'] = df['rate'].map(rate_filter)
    df = df.sort_values('Date')
    df = df.reset_index(drop=True)
    df_train = df.iloc[:-cfg.test_size]
    df_test = df.iloc[-cfg.test_size:]
    df_test = df_test.reset_index(drop=True)

    df_rate = pd.DataFrame()
    for shibor in cfg.SHIBOR:
        df = pd.read_excel(shibor)
        df['Date'] = df['Date'].dt.date
        df = df[['Date','3M']]
        df_rate = pd.concat([df_rate, df])
    df_rate = df_rate.reset_index(drop=True)
    df_rate['3M'] = df_rate['3M'].map(lambda x:x/100)
    return df_train, df_test, df_rate