import math
import datetime
import numpy as np
import matplotlib
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import pandas as pd
import logging


###################################################################################################
# ログ設定
###################################################################################################

logLevel = logging.DEBUG
ch = logging.StreamHandler()
ch.setLevel(logLevel)
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger = logging.getLogger(__name__)
logger.setLevel(logLevel)
logger.addHandler(ch)


###################################################################################################
# クラス定義
###################################################################################################

class NAOJ_JulianDay:
    """国立天文台のWebページで算出したユリウス日を返す。

    別途用意したプログラムで、国立天文台のWebページでユリウス日を算出してCSVファイルに保存しておく。
    """

    __FILE_PATH = 'D:/GitHub/misc/data/JulianDay_by_NAOJ_all.csv'
    

    def __init__(self):
        self.df = pd.read_csv(self.__FILE_PATH, index_col='年月日')
        logger.debug(self.df)
    

    def julianDay(self, y: int, m: int, d: int) -> float:
        """国立天文台のWebページで算出したユリウス日を返す。

        別途用意したプログラムで、国立天文台のWebページでユリウス日を算出してCSVファイルに保存しておく。
        引数で指定された年月日のユリウス日がすでに算出されてCSV内に保存されていれば、そのユリウス日を返し、
        CSV内にまだ保存されていなければ、Noneを返す。
        Args:
            y   (int)   :   年
            m   (int)   :   月
            d   (int)   :   日
        Returns:
            jd  (float) :   ユリウス日（ユリウス通日）。
                            ただしユリウス日を別途用意したプログラムで未算出の場合（所定のCSVファイル内に未保存の場合）にはNoneを返す。
        """
        key = '{:04}/{:02}/{:02}'.format(y, m, d)
        try:
            jd = self.df.at[key, 'ユリウス日']
            if type(jd) is np.float64:      # 該当するデータが1つの場合
                return jd
            elif type(jd) is np.ndarray:    # 該当するデータが複数の場合、1つ目のデータを返す
                return jd[0]
            else:
                raise ValueError('想定外の型: {}'.format(type(jd)))
        except KeyError:
            return None


###################################################################################################
# 関数定義（ユリウス日計算の各アルゴリズム）
###################################################################################################

def julianDay_wikipedia(y: int, m: int, d: int) -> float:
    """グレゴリオ暦からユリウス日を求める。

    References:
        wikipedia / ユリウス通日#Julian Day Number (JDN)
        https://ja.wikipedia.org/wiki/%E3%83%A6%E3%83%AA%E3%82%A6%E3%82%B9%E9%80%9A%E6%97%A5#Julian_Day_Number_(JDN)
            Note:
            1月と2月はそれぞれ前年（Yの値を-1する）の13月、14月として代入する（例: 2013年2月5日の場合、Y=2012, M=14, D=5）。
    Args:
        y   (int)   :   年
        m   (int)   :   月
        d   (int)   :   日
    Returns:
        JD  (float) :   ユリウス日（ユリウス通日）
    """
    if m in (1, 2):
        M = m + 12
        Y = y - 1
    else:
        M = m
        Y = y
    
    JD =  math.floor(365.25 * Y) + math.floor(Y / 400) - math.floor(Y / 100) \
        + math.floor(30.59 * (M - 2)) \
        + d + 1721088.5
    return JD


def julianDay_Fliegel(y: int, m: int, d: int) -> float:
    """グレゴリオ暦からユリウス日を求める。

    References:
        Fliegel, H. F. and Van Flandern, T. C., "A Machine Algorithm for Processing Calendar Dates," Communications of the ACM 11, p. 657, 1968.
        http://www.cs.otago.ac.nz/cosc345/resources/Fliegel.pdf

        COMPUTATION AND MEASUREMENT
        PROBLEM 11.
        https://er.jsc.nasa.gov/seh/math16.html
            Note:
            In FORTRAN integer arithmetic, multiplication and division are performed left to right in the order of occurrence, and the absolute value of each result is truncated to the next lower integer value after each operation, so that both 2/12 and -2/12 become 0.

        wikipedia / Julian day#Converting Gregorian calendar date to Julian Day Number
        https://en.wikipedia.org/wiki/Julian_day#Converting_Gregorian_calendar_date_to_Julian_Day_Number
            Note:
            The algorithm[61] is valid for all (possibly proleptic) Gregorian calendar dates after November 23, −4713. Divisions are integer divisions, fractional parts are ignored.
    Args:
        y   (int)   :   年
        m   (int)   :   月
        d   (int)   :   日
    Returns:
        JD  (float) :   ユリウス日（ユリウス通日）
    """
    JD = d - 32075 \
        + 1461 * (y + 4800 + (m - 14) // 12) // 4 \
        + 367 * (m - 2 - (m - 14) // 12 * 12) // 12 \
        - 3 * ((y + 4900 + (m - 14) // 12) // 100) // 4
    return JD


def julianDay_Hatcher(y: int, m: int, d: int) -> float:
    """グレゴリオ暦からユリウス日を求める。

    References:
        Hatcher, D. A., Simple formulae for Julian day numbers and calendar dates, Quarterly Journal of the Royal Astronomical Society, v. 25, p. 53-55, 1984
        http://adsabs.harvard.edu/full/1985QJRAS..26..151H
            Note:
            (x) INT is the integral part of x, and x is assumed to be positive; (x) MOD y is the positive remainder on divideing x by y.
    Args:
        y   (int)   :   年
        m   (int)   :   月
        d   (int)   :   日
    Returns:
        JD  (float) :   ユリウス日（ユリウス通日）
    """
    Y = y + 4716 - int(abs((14 - m) / 12))
    M = (m - 3) % 12
    D = d - 1
    JD =  int(abs(1461 * Y / 4)) + int(abs((153 * M + 2) / 5)) + D \
        - (1401 + int(abs(int(abs((Y + 184) / 100)) * 3 / 4)) - 38)
    return JD


def julianDay_Meeus(y: int, m: int, d: int) -> float:
    """グレゴリオ暦からユリウス日を求める。

    References:
        Meeus, J., Astronomical Algorithms, 1998
        http://www.agopax.it/Libri_astronomia/pdf/Astronomical%20Algorithms.pdf
            Note:
            INT(x) the greatest integer less than or equal to x.
            for instance, INT(-7.83) = -8
    Args:
        y   (int)   :   年
        m   (int)   :   月
        d   (int)   :   日
    Returns:
        JD  (float) :   ユリウス日（ユリウス通日）
    """
    A = math.floor(y / 100)
    B = 2 - A + math.floor(A / 4)
    JD =  math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + B - 1524.5
    return JD


def julianDay_Vallado(y: int, m: int, d: int) -> float:
    """グレゴリオ暦からユリウス日を求める。

    References:
        CelesTrak / Revisiting Spacetrack Report #3 - AIAA 2006-6753 - Source code (C++)
        http://www.celestrak.com/publications/AIAA/2006-6753/
        Vallado, David A., Paul Crawford, Richard Hujsak, and T.S. Kelso, "Revisiting Spacetrack Report #3," presented at the AIAA/AAS Astrodynamics Specialist Conference, Keystone, CO, 2006 August 21–24.
    Args:
        y   (int)   :   年
        m   (int)   :   月
        d   (int)   :   日
    Returns:
        JD  (float) :   ユリウス日（ユリウス通日）
    """
    JD =  367.0 * y - \
        math.floor((7 * (y + math.floor((m + 9) / 12.0))) * 0.25) + \
        math.floor(275 * m / 9.0) + d + 1721013.5
    return JD


def julianDay_Curtis2020(y: int, m: int, d: int) -> float:
    """グレゴリオ暦からユリウス日を求める。

    References:
        ScienceDirect / Julian Day Number
        https://www.sciencedirect.com/topics/engineering/julian-day-number
        Howard D. Curtis, in Orbital Mechanics for Engineering Students (Fourth Edition), 2020
            Note:
            INT(x) means retaining only the integer portion of x, without rounding (or, in other words, round toward zero). For example, INT(− 3.9) = −3 and INT(3.9) = 3.
    Args:
        y   (int)   :   年
        m   (int)   :   月
        d   (int)   :   日
    Returns:
        JD  (float) :   ユリウス日（ユリウス通日）
    """
    JD =  367 * y - int((7 * y + int((m + 9) / 12)) / 4) + int(275 * m / 9) + d + 1721013.5
    return JD


def julianDay_Curtis2014(y: int, m: int, d: int) -> float:
    """グレゴリオ暦からユリウス日を求める。

    References:
        ScienceDirect / Julian Day Number
        https://www.sciencedirect.com/topics/engineering/julian-day-number
        Howard D. Curtis, in Orbital Mechanics for Engineering Students (Third Edition), 2014
            Note:
            INT (x) means to retain only the integer portion of x, without rounding (or, in other words, round toward zero), that is, INT (−3.9) = −3 and INT (3.9) = 3
    Args:
        y   (int)   :   年
        m   (int)   :   月
        d   (int)   :   日
    Returns:
        JD  (float) :   ユリウス日（ユリウス通日）
    """
    JD =  367 * y - int(7 * (y + int((m + 9) / 12)) / 4) + int(275 * m / 9) + d + 1721013.5
    return JD


def julianDay_boost(y: int, m: int, d: int) -> float:
    """グレゴリオ暦からユリウス日を求める。

    References:
        boost/date_time/gregorian_calendar.ipp
        https://www.boost.org/doc/libs/1_72_0/boost/date_time/gregorian_calendar.ipp
    Args:
        y   (int)   :   年
        m   (int)   :   月
        d   (int)   :   日
    Returns:
        JD  (float) :   ユリウス日（ユリウス通日）
    """
    a = int((14 - m) / 12)
    Y = y + 4800 - a
    M = m + 12 * a - 3
    JD = int(d + ((153 * M + 2) / 5) + 365 * Y + (Y / 4) - (Y / 100) + (Y / 400) - 32045)
    return JD


def julianDay_php(y: int, m: int, d: int) -> float:
    """グレゴリオ暦からユリウス日を求める。

    References:
        php-src/ext/calendar/gregor.c
        https://github.com/php/php-src/blob/master/ext/calendar/gregor.c
    Args:
        y   (int)   :   年
        m   (int)   :   月
        d   (int)   :   日
    Returns:
        JD  (float) :   ユリウス日（ユリウス通日）
    """
    if y < 0:
        Y = y + 4801
    else:
        Y = y + 4800

    if m > 2:
        M = m - 3
    else:
        M = m + 9
        Y = Y - 1

    JD = int( \
        ((Y // 100) * 146097) // 4 \
        + ((Y % 100) * 1461) // 4 \
        + (M * 153 + 2) // 5 \
        + d \
        - 32045 \
        )
    return JD


def julianDay_pyorbital(y: int, m: int, d: int) -> float:
    """グレゴリオ暦からユリウス日を求める。

    References:
        pyorbital/pyorbital/astronomy.py
        https://github.com/pytroll/pyorbital/blob/master/pyorbital/astronomy.py
    Args:
        y   (int)   :   年
        m   (int)   :   月
        d   (int)   :   日
    Returns:
        JD  (float) :   ユリウス日（ユリウス通日）。                        
    """
    dt2np = np.datetime64('{:04}-{:02}-{:02}'.format(y, m, d))
    jdays2000 = (dt2np - np.datetime64('2000-01-01T12:00')) / np.timedelta64(1, 'D')
    JD =  jdays2000 + 2451545
    return JD


###################################################################################################
# 関数定義（main関数用）
###################################################################################################

def __toCSV(funcs: dict, yearRange: range, monthRange: range, dayRange: range, filepath: str):
    """グレゴリオ暦の各日時に対応するユリウス日をCSVに出力する。
    """
    with open(filepath, mode='w') as file:
        # 見出し行を出力
        file.write('Gregorian')
        for name in funcs.keys():
            file.write(',{}'.format(name))
        file.write(',{},{},{},{},{}'.format('minName', 'minJD', 'maxName', 'maxJD', 'max-min'))
        file.write('\n')

        # グレゴリオ暦の日時を進めながら、その時点その時点のユリウス日を出力していく
        for y in yearRange:
            for m in monthRange:
                for d in dayRange:
                    file.write('{:04}/{:02}/{:02}'.format(y, m, d)) # グレゴリオ暦
                    name_jd = {}    # 最小値・最大値特定用
                    for name, func in funcs.items():  # 各アルゴリズムによるユリウス日を出力
                        jd = func(y, m, d)
                        if jd is None:
                            jd = math.nan
                        file.write(',{}'.format(jd))
                        name_jd[name] = jd
                    # 最大のユリウス日・最小のユリウス日を算出したアルゴリズムを特定する
                    minName, minJD = min(name_jd.items(), key=lambda x: x[1])
                    maxName, maxJD = max(name_jd.items(), key=lambda x: x[1])
                    file.write(',{},{},{},{},{}'.format(minName, minJD, maxName, maxJD, maxJD - minJD))
                    file.write('\n')


def __configPlot1(df: pd.DataFrame, ax: matplotlib.axes.Axes):
    """グラフの描画設定を行う。
    """
    ax.get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    ax.get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    ax.ticklabel_format(style='plain', axis='both', useOffset=False, useMathText=False)
    ax.margins(x=0, y=0)
    ax.set_xticks(list(range(0, 80000 + 1, 2000)))
    ax.set_xticklabels([df.at[i, 'Gregorian'] for i in range(0, 80000 + 1, 2000)], rotation=30)


def __configPlot2(df: pd.DataFrame, ax: matplotlib.axes.Axes):
    """グラフの描画設定を行う。
    """
    ax.get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    ax.get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    ax.ticklabel_format(style='plain', axis='both', useOffset=False, useMathText=False)
    ax.margins(x=0, y=0)
    ax.set_xticks(list(df.index))
    ax.set_xticklabels(list(df['Gregorian']), rotation=30)
    

###################################################################################################
# main関数
###################################################################################################

def main():

    naoj = NAOJ_JulianDay()

    # 計算対象のアルゴリズム
    FUNCS = {
        'wikipedia':    julianDay_wikipedia,
        'Fliegel':      julianDay_Fliegel,
        'Hatcher':      julianDay_Hatcher,
        'Meeus':        julianDay_Meeus,
        'Vallado':      julianDay_Vallado,
        'Curtis2020':   julianDay_Curtis2020,
        'Curtis2014':   julianDay_Curtis2014,
        'boost':        julianDay_boost,
        'php':          julianDay_php,
        'pyorbital':    julianDay_pyorbital,
        'NAOJ':         naoj.julianDay
    }

    DIR = 'D:/GitHub/misc/data/'
    PREFIX = 'JulianDayCompare_'
    
    # -4713/01/01～2000/12/01（1ヶ月間隔（各月の1日））
    __toCSV(FUNCS, range(-4713, 2000 + 1), range(1, 12 + 1), range(1, 1 + 1), DIR + PREFIX + '-47130101_20001201.csv')
    # -4713/01/01～-4711/12/01（1ヶ月間隔（各月の1日））
    __toCSV(FUNCS, range(-4713, -4711 + 1), range(1, 12 + 1), range(1, 1 + 1), DIR + PREFIX + '-47130101_-47111201.csv')
    # -0001/01/01～0001/12/01（1ヶ月間隔（各月の1日））
    __toCSV(FUNCS, range(-1, 1 + 1), range(1, 12 + 1), range(1, 1 + 1), DIR + PREFIX + '-00010101_00011201.csv')
    # -0001/01/01～0001/12/01（1ヶ月間隔（各月の1日）、ただし0年を除く）
    __toCSV(FUNCS, list(range(-1, -1 + 1)) + list(range(1, 1 + 1)), range(1, 12 + 1), range(1, 1 + 1), DIR + PREFIX + '-00010101_00011201_exceptYear0.csv')
    # 1582/10/01～1582/10/31（1日間隔（各日の0時））
    # ユリウス暦1582/10/4（ユリウス暦最終日）とその翌日のグレゴリオ暦1582/10/15（グレゴリオ暦初日）の周辺
    __toCSV(FUNCS, range(1582, 1582 + 1), range(10, 10 + 1), range(1, 31 + 1), DIR + PREFIX + '15821001_15821031.csv')

    # CSVを読み込みグラフ化する

    nameBase = DIR + PREFIX + '-47130101_20001201'
    df = pd.read_csv(nameBase + '.csv')
    ax = df.loc[:, FUNCS.keys()].plot(title='-4713/01/01 ~ 2000/12/01', grid=True, figsize=(16, 9))
    __configPlot1(df, ax)
    plt.savefig(nameBase + '.png')

    ax = df.loc[:, ['max-min']].plot(title='-4713/01/01 ~ 2000/12/01  max-min', grid=True, figsize=(16, 9))
    __configPlot1(df, ax)
    plt.savefig(nameBase + '_max-min.png')

    nameBase = DIR + PREFIX + '-47130101_-47111201'
    df = pd.read_csv(nameBase + '.csv')
    ax = df.loc[:, FUNCS.keys()].plot(title='-4713/01/01 ~ -4711/12/01', grid=True, figsize=(16,9))
    __configPlot2(df, ax)
    plt.savefig(nameBase + '.png')

    nameBase = DIR + PREFIX + '-00010101_00011201'
    df = pd.read_csv(nameBase + '.csv')
    ax = df.loc[:, FUNCS.keys()].plot(title='-0001/01/01 ~ 0001/12/01', grid=True, figsize=(16,9))
    __configPlot2(df, ax)
    plt.savefig(nameBase + '.png')

    nameBase = DIR + PREFIX + '-00010101_00011201_exceptYear0'
    df = pd.read_csv(nameBase + '.csv')
    ax = df.loc[:, FUNCS.keys()].plot(title='-0001/01/01 ~ 0001/12/01  except year 0', grid=True, figsize=(16,9))
    __configPlot2(df, ax)
    plt.savefig(nameBase + '.png')

    nameBase = DIR + PREFIX + '15821001_15821031'
    df = pd.read_csv(nameBase + '.csv')
    ax = df.loc[:, FUNCS.keys()].plot(title='1582/10/01 ~ 1582/10/31', grid=True, figsize=(16,9))
    __configPlot2(df, ax)
    plt.savefig(nameBase + '.png')

    plt.show()



if __name__ == '__main__':
    main()