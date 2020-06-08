import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import time
import os

###################################################################################################
# 関数定義（main関数用）
###################################################################################################

def __requestAndCSV(url: str, param: dict, filepath: str) -> None:
    """Webサイトへリクエストを送信して、結果をCSVファイルに出力する。
    """
    # Webサイトへリクエストを送信
    r = requests.post(url, data=param)
    if r.status_code != 200:
        print('エラー: {}'.format(r))
        exit()

    # Webサイトでの計算結果を抽出
    bsObj = BeautifulSoup(r.text, 'html.parser')
    table = bsObj.findAll('table', {'class': 'result'})[0]
    tr = table.findAll('tr')
    rows = []
    for row in tr:
        cols = []
        for cell in row.findAll(['td', 'th']):
            cols.append(cell.get_text())
        rows.append(cols)

    # CSVファイルに出力
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df = df.set_index('年月日')
    df.to_csv(filepath, mode='a', header=(not os.path.exists(filepath)))


def __plot(df: pd.DataFrame, title: str):
    """グラフの描画を行う。
    """
    plt.figure()
    ax = df['ユリウス日'].plot(title=title, grid=True, figsize=(16, 9))
    ax.get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    ax.get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    ax.ticklabel_format(style='plain', axis='both', useOffset=False, useMathText=False)
    ax.margins(x=0, y=0)
    ax.set_xticks(df.index)
    ax.set_xticklabels([df.loc[i, '年月日'] for i in df.index], rotation=30)


###################################################################################################
# main関数
###################################################################################################

def main():
    
    URL = 'http://eco.mtk.nao.ac.jp/cgi-bin/koyomi/cande/date2jd.cgi'   # 国立天文台 > 暦計算室 > 暦象年表 > ユリウス日
    # このWebサイトでは -4712/01/01 12:00 が最小値（ユリウス日＝0.0日）

    COMMON_PARAM = {
        'hour': 12, 'min': 0, 'sec': 0,  # 時刻
        'tsys': 1,              # 時刻系「世界時」
        'div': 1, 'divu': 3,    # 間隔「1」「日」
        'len': 1, 'lenu': 3,  # 期間「1」「日」
        '表示': '表示'
        }
    
    DIR = 'D:/GitHub/misc/data/'
    PREFIX = 'JulianDay_by_NAOJ_'
    
    # Webサイトへ渡すパラメータを用意
    params = []
    # -4712/01～-4711/12
    for y in range(-4712, -4711 + 1):
        for m in range(1, 12 + 1):
            param = {'year': y, 'month': m, 'day': 1}
            param.update(COMMON_PARAM)
            params.append(param)
    # -0001/01～0001/12
    for y in range(-1, 1 + 1):
        for m in range(1, 12 + 1):
            param = {'year': y, 'month': m, 'day': 1}
            param.update(COMMON_PARAM)
            params.append(param)
    # 1582/10/01～1582/10/31
    for d in range(1, 31 + 1):
        param = {'year': 1582, 'month': 10, 'day': d}
        param.update(COMMON_PARAM)
        params.append(param)

    # Webサイトにリクエストし、結果をCSVへ出力
    for param in params:
        print('request: {}'.format(param))
        __requestAndCSV(URL, param, DIR + PREFIX + 'all.csv')
        time.sleep(1)  # Webサイトへの負荷防止
    
    # CSVを読み込む
    df = pd.read_csv(DIR + PREFIX + 'all.csv')
    for i in range(0, len(df)): # データを絞り込みやすいように年月日の列を設ける
        ymd = df.at[i, '年月日'].split('/')
        df.at[i, 'year'] = int(ymd[0])
        df.at[i, 'month'] = int(ymd[1])
        df.at[i, 'day'] = int(ymd[2])
    print(df)
    print(df.dtypes)

    # グラフを作成する
    plotDf = df[(-4712 <= df.year) & (df.year <= -4711) & (1 <= df.month) & (df.month <= 12)]
    __plot(plotDf, '-4712/01 ~ -4711/12')
    plt.savefig(DIR + PREFIX + '-47120101_-47111201.png')
    
    plotDf = df[(-1 <= df.year) & (df.year <= 1) & (1 <= df.month) & (df.month <= 12)]
    __plot(plotDf, '-0001/01 ~ 0001/12')
    plt.savefig(DIR + PREFIX + '-00010101_00011201.png')
    
    plotDf = df[(df.year == 1582) & (df.month == 10) & (1 <= df.day) & (df.day <= 31)]
    __plot(plotDf, '1582/10/01 ~ 1582/10/31')
    plt.savefig(DIR + PREFIX + '15821001_15821031.png')
    
    plt.show()


if __name__ == '__main__':
    main()
