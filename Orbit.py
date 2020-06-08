import logging
import math
import datetime
import re
import numpy

###################################################################################################
# ログ設定
###################################################################################################

logLevel = logging.INFO
ch = logging.StreamHandler()
ch.setLevel(logLevel)
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger = logging.getLogger(__name__)
logger.setLevel(logLevel)
logger.addHandler(ch)


###################################################################################################
# クラス定義
###################################################################################################

class TwoLineElements:
    """TLE (Two-line Elements) を扱うクラス。
    """
    
    def __init__(self, tleString: str = None):
        """TLEの文字列から軌道要素を抽出して本クラスに格納する。

        Args:
            tleString   (str)   :   TLEの文字列全部
        """

        ###########################################################################################
        # 変数宣言
        self.__tleString = tleString  # TLE全体
        
        ###########################################################################################
        # 変数宣言
        # TLEの各要素の文字列

        # 0行目
        self.__name = None
        # 1行目
        self.__lineNumber1 = '1'
        self.__satelliteNumber1 = None
        self.__classification = None
        self.__launchYear = None
        self.__launchNumber = None
        self.__launchPiece = None
        self.__epochYear = None
        self.__epochDay = None
        self.__firstDerivativeMeanMotion = None
        self.__secondDerivativeMeanMotion = None
        self.__bstar = None
        self.__ephemerisType = None
        self.__elementNumber = None
        self.__checksum1 = None
        # 2行目
        self.__lineNumber2 = '2'
        self.__satelliteNumber2 = None
        self.__inclination = None
        self.__raan = None
        self.__eccentricity = None
        self.__argumentOfPerigee = None
        self.__meanAnomaly = None
        self.__meanMotion = None
        self.__revolutionAtEpoch = None
        self.__checksum2 = None

        ###########################################################################################
        # 変数宣言
        # 要素に適した型で値を保持する変数

        # 1行目
        self.__satelliteNumber_int = None
        self.__launchYear_int = None
        self.__launchNumber_int = None
        self.__epochYear_int = None
        self.__epochDay_float = None
        self.__firstDerivativeMeanMotion_float = None
        self.__secondDerivativeMeanMotion_float = None
        self.__bstar_float = None
        self.__elementNumber_int = None
        # 2行目
        self.__inclination_float = None
        self.__raan_float = None
        self.__eccentricity_float = None
        self.__argumentOfPerigee_float = None
        self.__meanAnomaly_float = None
        self.__meanMotion_float = None
        self.__revolutionAtEpoch_int = None

        ###########################################################################################
        # TLEから各要素を文字列として抽出する。

        # TLEが引数に与えられずにコンストラクタが呼ばれた場合には、値がセットされていない状態のインスタンスになる。
        if tleString is None or type(tleString) is not str:
            return

        lines = tleString.rstrip().splitlines()
        if (len(lines) != 3 or len(lines[0]) > 24 or len(lines[1]) != 69 or len(lines[2]) != 69):
            raise ValueError('TLE is invalid')
        
        # 0行目
        self.__name = lines[0]

        # 1行目
        self.__lineNumber1 = lines[1][0]
        self.__satelliteNumber1 = lines[1][2:7]
        self.__classification = lines[1][7]
        self.__launchYear = lines[1][9:11]
        self.__launchNumber = lines[1][11:14]
        self.__launchPiece = lines[1][14:17]
        self.__epochYear = lines[1][18:20]
        self.__epochDay = lines[1][20:32]
        self.__firstDerivativeMeanMotion = lines[1][33:43]
        self.__secondDerivativeMeanMotion = lines[1][44:52]
        self.__bstar = lines[1][53:61]
        self.__ephemerisType = lines[1][62:63]
        self.__elementNumber = lines[1][64:68]
        self.__checksum1 = lines[1][68]

        # 2行目
        self.__lineNumber2 = lines[2][0]
        self.__satelliteNumber2 = lines[2][2:7]
        self.__inclination = lines[2][8:16]
        self.__raan = lines[2][17:25]
        self.__eccentricity = lines[2][26:33]
        self.__argumentOfPerigee = lines[2][34:42]
        self.__meanAnomaly = lines[2][43:51]
        self.__meanMotion = lines[2][52:63]
        self.__revolutionAtEpoch = lines[2][63:68]
        self.__checksum2 = lines[2][68]
        
        ###########################################################################################
        # 要素に適した型で値を保持する変数に、値をセットする。
        # 値のチェックも行う。
        # プロパティへ値をセットする形でsetterを呼べば、値のセットと共にチェックもsetterの中で行われる。

        # 0行目
        self.name = self.__name

        # 1行目
        if self.__lineNumber1 != '1':
            raise ValueError('Line1 LineNumber is invalid')
        self.satelliteNumber = self.__satelliteNumber1
        self.classification = self.__classification
        self.launchYear = self.__launchYear
        self.launchNumber = self.__launchNumber
        self.launchPiece = self.__launchPiece
        self.epochYear = self.__epochYear
        self.epochDay = self.__epochDay
        self.firstDerivativeMeanMotion = self.__firstDerivativeMeanMotion
        self.secondDerivativeMeanMotion = self.__secondDerivativeMeanMotion
        self.bstar = self.__bstar
        self.ephemerisType = self.__ephemerisType
        self.elementNumber = self.__elementNumber
        if re.fullmatch(r'[0-9]', self.__checksum1) is None:
            raise ValueError('Line1 CheckSum is invalid')

        # 2行目
        if self.__lineNumber2 != '2':
            raise ValueError('Line2 LineNumber is invalid')
        self.satelliteNumber = self.__satelliteNumber2
        self.inclination = self.__inclination
        self.raan = self.__raan
        self.eccentricity = self.__eccentricity
        self.argumentOfPerigee = self.__argumentOfPerigee
        self.meanAnomaly = self.__meanAnomaly
        self.meanMotion = self.__meanMotion
        self.revolutionAtEpoch = self.__revolutionAtEpoch
        if re.fullmatch(r'[0-9]', self.__checksum2) is None:
            raise ValueError('Line2 CheckSum is invalid')

        # その他のチェック
        if (self.__satelliteNumber1 != self.__satelliteNumber2):
            raise ValueError('Line1 Line2 SatelliteNumber is invalid')


    ###############################################################################################
    # プロパティ
    ###############################################################################################
    
    @property
    def name(self) -> str:
        return self.__name
    @name.setter
    def name(self, val):
        if type(val) is str and len(val) <= 24:
            self.__name = str(val) + ' ' * (24 - len(val))
        else:
            raise ValueError('Name is invalid')

    @property
    def satelliteNumber(self) -> str:
        return self.__satelliteNumber1
    @property
    def satelliteNumber_int(self) -> int:
        return self.__satelliteNumber_int
    @satelliteNumber.setter
    def satelliteNumber(self, val):
        if type(val) is str and re.fullmatch(r'[0-9]{1,5}', val.strip()):
            self.__satelliteNumber1 = self.__satelliteNumber2 = '0' * (5 - len(val.strip())) + str(val.strip())
            self.__satelliteNumber_int = int(val)
        elif type(val) is int and val >= 1 and val <= 99999:
            self.__satelliteNumber1 = self.__satelliteNumber2 = '{:05}'.format(val)
            self.__satelliteNumber_int = val
        else:
            raise ValueError('SatelliteNumber is invalid')

    @property
    def classification(self) -> str:
        return self.__classification
    @classification.setter
    def classification(self, val):
        if (type(val) is str and len(val) == 1):
            self.__classification = val
        else:
            raise ValueError('Classification is invalid')

    @property
    def launchYear(self) -> str:
        return self.__launchYear
    @property
    def launchYear_int(self) -> int:
        return self.__launchYear_int
    @launchYear.setter
    def launchYear(self, val):
        if type(val) is str and re.fullmatch(r'[0-9]{1,2}', val.strip()):
            self.__launchYear =  '0' * (2 - len(val.strip())) + str(val.strip())
            self.__launchYear_int = int(val)
        elif type(val) is int and val >= 0 and val <= 99:
            self.__launchYear =  '{:02}'.format(val)
            self.__launchYear_int = val
        else:
            raise ValueError('LaunchYear is invalid')

    @property
    def launchNumber(self) -> str:
        return self.__launchNumber
    @property
    def launchNumber_int(self) -> int:
        return self.__launchNumber_int
    @launchNumber.setter
    def launchNumber(self, val):
        if type(val) is str and re.fullmatch(r'[0-9]{1,3}', val.strip()):
            self.__launchNumber = '0' * (3 - len(val.strip())) + str(val.strip())
            self.__launchNumber_int = int(val)
        elif type(val) is int and val >= 0 and val <= 999:
            self.__launchNumber =  '{:03}'.format(val)
            self.__launchNumber_int = val
        else:
            raise ValueError('LaunchNumber is invalid')

    @property
    def launchPiece(self) -> str:
        return self.__launchPiece
    @launchPiece.setter
    def launchPiece(self, val):
        if (type(val) is str and len(val) == 3):
            self.__launchPiece = val
        else:
            raise ValueError('LaunchPiece is invalid')

    @property
    def epochYear(self) -> str:
        return self.__epochYear
    @property
    def epochYear_int(self) -> int:
        return self.__epochYear_int
    @epochYear.setter
    def epochYear(self, val):
        if type(val) is str and re.fullmatch(r'[0-9]{1,2}', val.strip()):
            self.__epochYear = '0' * (2 - len(val.strip())) + str(val.strip())
            self.__epochYear_int = int(val)
        elif type(val) is int and val >= 0 and val <= 99:
            self.__epochYear =  '{:02}'.format(val)
            self.__epochYear_int = val
        else:
            raise ValueError('EpochYear is invalid')

    @property
    def epochDay(self) -> str:
        return self.__epochDay
    @property
    def epochDay_float(self) -> float:
        return self.__epochDay_float
    @epochDay.setter
    def epochDay(self, val):
        if type(val) is str and re.fullmatch(r'[0-9]{1,3}\.[0-9]{1,8}', val.strip()):
            self.__epochDay = val
            self.__epochDay_float = float(val)
        elif type(val) is float and val >= 0:
            self.__epochDay =  '{:02.8}'.format(val)
            self.__epochDay_float = val
        else:
            raise ValueError('EpochDay is invalid')

    @property
    def firstDerivativeMeanMotion(self) -> str:
        return self.__firstDerivativeMeanMotion
    @property
    def firstDerivativeMeanMotion_float(self) -> float:
        return self.__firstDerivativeMeanMotion_float
    @firstDerivativeMeanMotion.setter
    def firstDerivativeMeanMotion(self, val):
        if type(val) is str and re.fullmatch(r'[\+|\-| ]\.[0-9]{1,8}', val):
            self.__firstDerivativeMeanMotion = val
            self.__firstDerivativeMeanMotion_float = float(val)
        elif type(val) is float:
            self.__firstDerivativeMeanMotion =  '{:00.8}'.format(val)
            self.__firstDerivativeMeanMotion_float = val
        else:
            raise ValueError('1stDerivativeMeanMotion is invalid')

    @property
    def secondDerivativeMeanMotion(self) -> str:
        return self.__secondDerivativeMeanMotion
    @property
    def secondDerivativeMeanMotion_float(self) -> float:
        return self.__secondDerivativeMeanMotion_float
    @secondDerivativeMeanMotion.setter
    def secondDerivativeMeanMotion(self, val):
        if type(val) is str:
            m = re.fullmatch(r'([\+|\-| ][0-9]{1,5})([\+|\-| ][0-9])', val)
            if m:
                self.__secondDerivativeMeanMotion = val
                self.__secondDerivativeMeanMotion_float = float(m.group(1) + 'e' + m.group(2))
        elif type(val) is float:
            self.__secondDerivativeMeanMotion =  '{:e}'.format(val)
            self.__secondDerivativeMeanMotion_float = val
        else:
            raise ValueError('2ndDerivativeMeanMotion is invalid')

    @property
    def bstar(self) -> str:
        return self.__bstar
    @property
    def bstar_float(self) -> float:
        return self.__bstar_float
    @bstar.setter
    def bstar(self, val):
        if type(val) is str:
            m = re.fullmatch(r'([\+|\-| ][0-9]{1,5})([\+|\-| ][0-9])', val)
            if m:
                self.__bstar = val
                self.__bstar_float = float(m.group(1) + 'e' + m.group(2))
        elif type(val) is float:
            self.__bstar =  '{:e}'.format(val)
            self.__bstar_float = val
        else:
            raise ValueError('BSTAR is invalid')

    @property
    def ephemerisType(self) -> str:
        return self.__ephemerisType
    @ephemerisType.setter
    def ephemerisType(self, val):
        if type(val) is str and re.fullmatch(r'[0-9]', val.strip()):
            self.__ephemerisType = val
        else:
            raise ValueError('EphemerisType is invalid')

    @property
    def elementNumber(self) -> str:
        return self.__elementNumber
    @property
    def elementNumber_int(self) -> int:
        return self.__elementNumber_int
    @elementNumber.setter
    def elementNumber(self, val):
        if type(val) is str and re.fullmatch(r'[0-9]{1,4}', val.strip()):
            self.__elementNumber = '0' * (4 - len(val.strip())) + str(val.strip())
            self.__elementNumber_int = int(val)
        elif type(val) is int and val >= 0 and val <= 9999:
            self.__elementNumber =  '{:04}'.format(val)
            self.__elementNumber_int = val
        else:
            raise ValueError('ElementNumber is invalid')
    
    @property
    def inclination(self) -> str:
        return self.__inclination
    @property
    def inclination_float(self) -> float:
        return self.__inclination_float
    @inclination.setter
    def inclination(self, val):
        if type(val) is str and re.fullmatch(r'[0-9]{1,3}\.[0-9]{1,4}', val.strip()):
            self.__inclination = val
            self.__inclination_float = float(val)
        elif type(val) is float and val >= 0:
            self.__inclination =  '{:03.4}'.format(val)
            self.__inclination_float = val
        else:
            raise ValueError('Inclination is invalid')

    @property
    def raan(self) -> str:
        return self.__raan
    @property
    def raan_float(self) -> float:
        return self.__raan_float
    @raan.setter
    def raan(self, val):
        if type(val) is str and re.fullmatch(r'[0-9]{1,3}\.[0-9]{1,4}', val.strip()):
            self.__raan = val
            self.__raan_float = float(val)
        elif type(val) is float and val >= 0:
            self.__raan =  '{:03.4}'.format(val)
            self.__raan_float = val
        else:
            raise ValueError('RAAN is invalid')

    @property
    def eccentricity(self) -> str:
        return self.__eccentricity
    @property
    def eccentricity_float(self) -> float:
        return self.__eccentricity_float
    @eccentricity.setter
    def eccentricity(self, val):
        if type(val) is str and re.fullmatch(r'[0-9]{1,7}', val.strip()):
            self.__eccentricity = val
            self.__eccentricity_float = float(val) / 10000000
        elif type(val) is float and val >= 0:
            self.__eccentricity =  '{:00.7}'.format(val)
            self.__eccentricity_float = val
        else:
            raise ValueError('Eccentricity is invalid')

    @property
    def argumentOfPerigee(self) -> str:
        return self.__argumentOfPerigee
    @property
    def argumentOfPerigee_float(self) -> float:
        return self.__argumentOfPerigee_float
    @argumentOfPerigee.setter
    def argumentOfPerigee(self, val):
        if type(val) is str and re.fullmatch(r'[0-9]{1,3}\.[0-9]{1,4}', val.strip()):
            self.__argumentOfPerigee = val
            self.__argumentOfPerigee_float = float(val)
        elif type(val) is float and val >= 0:
            self.__argumentOfPerigee =  '{:03.4}'.format(val)
            self.__argumentOfPerigee_float = val
        else:
            raise ValueError('ArgumentOfPerigee is invalid')

    @property
    def meanAnomaly(self) -> str:
        return self.__meanAnomaly
    @property
    def meanAnomaly_float(self) -> float:
        return self.__meanAnomaly_float
    @meanAnomaly.setter
    def meanAnomaly(self, val):
        if type(val) is str and re.fullmatch(r'[0-9]{1,3}\.[0-9]{1,4}', val.strip()):
            self.__meanAnomaly = val
            self.__meanAnomaly_float = float(val)
        elif type(val) is float and val >= 0:
            self.__meanAnomaly =  '{:03.4}'.format(val)
            self.__meanAnomaly_float = val
        else:
            raise ValueError('MeanAnomaly is invalid')

    @property
    def meanMotion(self) -> str:
        return self.__meanMotion
    @property
    def meanMotion_float(self) -> float:
        return self.__meanMotion_float
    @meanMotion.setter
    def meanMotion(self, val: float):
        if type(val) is str and re.fullmatch(r'[0-9]{1,2}\.[0-9]{1,8}', val.strip()):
            self.__meanMotion = val
            self.__meanMotion_float = float(val)
        elif type(val) is float and val >= 0:
            self.__meanMotion =  '{:02.8}'.format(val)
            self.__meanMotion_float = val
        else:
            raise ValueError('MeanMotion is invalid')

    @property
    def revolutionAtEpoch(self) -> str:
        return self.__revolutionAtEpoch
    @property
    def revolutionAtEpoch_int(self) -> int:
        return self.__revolutionAtEpoch_int
    @revolutionAtEpoch.setter
    def revolutionAtEpoch(self, val: int):
        if type(val) is str and re.fullmatch(r'[0-9]{1,5}', val.strip()):
            self.__revolutionAtEpoch = '0' * (5 - len(val.strip())) + str(val.strip())
            self.__revolutionAtEpoch_int = int(val)
        elif type(val) is int and val >= 0 and val <= 99999:
            self.__revolutionAtEpoch =  '{:05}'.format(val)
            self.__revolutionAtEpoch_int = val
        else:
            raise ValueError('RevolutionAtEpoch is invalid')
    
    @property
    def epoch_datetime(self) -> datetime.datetime:
        return datetime.datetime(2000 + self.__epochYear_int, 1, 1, 0, 0, 0, 0, datetime.timezone.utc) \
            + datetime.timedelta(days=self.__epochDay_float - 1)
    
    @property
    def elements(self) -> dict:
        return {
            # 0行目
            '0_Name'                :   self.__name,
            # 1行目
            '1_LineNumber'          :   self.__lineNumber1,
            '1_SatelliteNumber'     :   self.__satelliteNumber1,
            '1_Classification'      :   self.__classification,
            '1_LaunchYear'          :   self.__launchYear,
            '1_LaunchNumber  '      :   self.__launchNumber,
            '1_LaunchPiece'         :   self.__launchPiece,
            '1_EpochYear'           :   self.__epochYear,
            '1_EpochDay'            :   self.__epochDay,
            '1_1stDerivativeMeanMotion'   :   self.__firstDerivativeMeanMotion,
            '1_2ndDerivativeMeanMotion'   :   self.__secondDerivativeMeanMotion,
            '1_BSTAR'               :   self.__bstar,
            '1_EphemerisType'       :   self.__ephemerisType,
            '1_ElementNumber '      :   self.__elementNumber,
            '1_CheckSum'            :   self.__checksum1,
            # 2行目
            '2_LineNumber'          :   self.__lineNumber2,
            '2_SatelliteNumber'     :   self.__satelliteNumber2,
            '2_Inclination'         :   self.__inclination,
            '2_RAAN'                :   self.__raan,
            '2_Eccentricity'        :   self.__eccentricity,
            '2_ArgumentOfPerigee'   :   self.__argumentOfPerigee,
            '2_MeanAnomaly'         :   self.__meanAnomaly,
            '2_MeanMotion'          :   self.__meanMotion,
            '2_RevolutionAtEpoch'   :   self.__revolutionAtEpoch,
            '2_CheckSum'            :   self.__checksum2,
        }


###################################################################################################
# 関数定義
###################################################################################################

def julianDay(y: int, m: int, d: int, h: int, i: int, s: float) -> float:
    """グレゴリオ暦からユリウス日を求める。

    References:
        CelesTrak / Revisiting Spacetrack Report #3 - AIAA 2006-6753 - Source code (C++)
        http://www.celestrak.com/publications/AIAA/2006-6753/
        Vallado, David A., Paul Crawford, Richard Hujsak, and T.S. Kelso, "Revisiting Spacetrack Report #3," presented at the AIAA/AAS Astrodynamics Specialist Conference, Keystone, CO, 2006 August 21–24.
    Args:
        y   (int)   :   年
        m   (int)   :   月
        d   (int)   :   日
        h   (int)   :   時
        i   (int)   :   分
        s   (float) :   秒
    Returns:
        (float) :   ユリウス日（ユリウス通日）
    """
    return  367.0 * y - \
        math.floor((7 * (y + math.floor((m + 9) / 12.0))) * 0.25) + \
        math.floor(275 * m / 9.0) + d + 1721013.5 \
        + ((s / 60.0 + i) / 60.0 + h) / 24.0


def siderealTime(date: datetime.datetime) -> float:
    """指定した日時におけるグリニッジ恒星時を求める。

    References:
        Sidereal Time
        https://www.sciencedirect.com/topics/engineering/sidereal-time
        Preliminary orbit determination
        Howard D. Curtis, in Orbital Mechanics for Engineering Students (Fourth Edition), 2020
        Howard D. Curtis, in Orbital Mechanics for Engineering Students (Third Edition), 2014
        Howard D. Curtis, in Orbital Mechanics for Engineering Students (Second Edition), 2010
    Args:
        date    (datetime)  :   グリニッジ恒星時を求める対象の時刻（UTC）
    Returns:
        theta_G (float)     :   dateで指定した日時におけるグリニッジ恒星時 [deg]
    """
    y = date.year
    m = date.month
    d = date.day

    # ユリウス通日（0 h UT における）  J0
    J0 = julianDay(y, m, d, 0, 0, 0)
    
    # ユリウス世紀数（0 h UT における）    T0
    T0 = (J0 - 2451545) / 36525.0
    
    # グリニッジ恒星時（0 h UT における）  θ_G0
    theta_G0 = 100.4606184 + 36000.77004 * T0 + 0.000387933 * (T0 ** 2) - (2.58310 ** (-8)) * (T0 ** 3)
    theta_G0 -= 360.0 * int(theta_G0 / 360.0)
    if theta_G0 < 0:
        theta_G0 += 360
    
    # グリニッジ恒星時（指定した時刻における）  θ_G
    UT = date.hour + date.minute / 60.0 + date.second / 3600.0
    theta_G = theta_G0 + 360.98564724 * UT / 24.0
    theta_G -= 360.0 * int(theta_G / 360.0)
    if theta_G < 0:
        theta_G += 360
    logger.debug('J0 = {}, T0 = {}, θG0 = {}, UT = {}, θG = {}'.format(J0, T0, theta_G0, UT, theta_G))

    return theta_G


def siderealTime_wikipedia(date: datetime.datetime) -> float:
    """指定した日時におけるグリニッジ恒星時を求める。

    References:
        wikipedia / 恒星時の計算方法
        https://ja.wikipedia.org/wiki/%E6%81%92%E6%98%9F%E6%99%82#%E6%81%92%E6%98%9F%E6%99%82%E3%81%AE%E8%A8%88%E7%AE%97%E6%B3%95
    Args:
        date    (datetime)  :   グリニッジ恒星時を求める対象の時刻（UTC）
    Returns:
        theta_G (float)     :   dateで指定した日時におけるグリニッジ恒星時 [deg]
    """
    y = date.year
    m = date.month
    d = date.day
    JD = 365.25 * y // 1 \
        + y // 400 - y // 100 \
        + 30.59 * (m - 2) // 1 \
        + d + 1721088.5 \
        + date.hour / 24.0 + date.minute / 1440.0 + date.second / 86400.0
    TJD = JD - 2440000.5
    theta_G = 24 * (0.671262 + 1.0027379094 * TJD)
    return theta_G


def orbitalElementToLatLon(
    orb_ET      : datetime.datetime,
    orb_omega0  : float,
    orb_i       : float,
    orb_OMEGA0  : float,
    orb_e       : float,
    orb_M0      : float,
    orb_M1      : float,
    orb_M2      : float,
    date        : datetime.datetime
    ) -> tuple:
    """軌道要素から、ある日時における衛星位置の経緯度を求める。

    参考：
        人工衛星位置推算の実際（最終版）
        http://www.infra.kochi-tech.ac.jp/takagi/Geomatics/5Estimation2.pdf

    Args:
        orb_ET      (datetime)  :   元期ET (Epoch Time) [day]
        orb_omega0  (float)     :   近地点引数ω0 (Argument of perigee) [deg]
        orb_i       (float)     :   軌道傾斜角i (inclination angle) [deg]
        orb_OMEGA0  (float)     :   昇交点赤経Ω0 (right ascension of ascending node) [deg]
        orb_e       (float)     :   離心率e (Eccentricity) [無次元]
        orb_M0      (float)     :   平均近点角M0 (Mean Anomaly) [deg]
        orb_M1      (float)     :   平均運動M1 (Mean Motion) [rev / day]
        orb_M2      (float)     :   平均運動変化係数M2 [rev / day^2]
        date        (datetime)  :   この日時の衛星の経緯度を求める（UTC）
    Returns:
        phi         (float)     :   緯度 [deg]
        lam         (float)     :   経度 [deg]
    """

    # 定数
    orb_r = 6378.137  # 地球の半径r [km] 「GCS WGS 1984」の赤道半径
    #orb_r = 6371.0087714   # 「GCS Sphere GRS 1980 Mean Radius」の赤道半径と極半径
    EPSILON = 1.0e-10  # ニュートン・ラフソン法の収束判定の閾値
    theta_0_date = datetime.datetime(2006, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)  # ある時刻
    theta_0 = 0.276444444  # ある時刻のグリニッジ恒星時 [rev]

    # 軌道長半径aの計算
    orb_GM = 2.975537 * (10 ** 15)  # [km^3 / day^2]
    delta_t = (date - orb_ET).total_seconds() / (60 * 60 * 24)  # 元期からの経過日数Δt [day]
    logger.debug('date - orb_ET = {}, total_seconds = {}'.format(date - orb_ET, (date - orb_ET).total_seconds()))
    orb_Mm = orb_M1 + orb_M2 * delta_t  # [rev / day]
    orb_a = (orb_GM / (4.0 * (math.pi ** 2) * (orb_Mm ** 2))) ** (1.0 / 3.0)   # [km]
    logger.debug('Δt = {} [day], Mm = {} [rev / day], a = {} [km]'.format(delta_t, orb_Mm, orb_a))

    # 離心近点角Eの計算
    tmp_M = (orb_M0 / 360) + (orb_M1 * delta_t) + (0.5 * orb_M2 * (delta_t ** 2))    # 観測時刻の平均近点角M [rev]
    orb_M = (tmp_M - int(tmp_M)) * 360  # 観測時刻の平均近点角M [deg]
    logger.debug('M = {} [rev]'.format(orb_M))
    orb_E = 0
    fx = orb_E - orb_e * math.sin(math.radians(orb_E)) - orb_M
    dfx = 0
    while abs(fx) > EPSILON:    # ニュートン・ラフソン法
        fx = orb_E - orb_e * math.sin(math.radians(orb_E)) - orb_M  # f(x)
        dfx = 1 - orb_e * math.cos(math.radians(orb_E))             # f'(x)
        logger.debug('fx = {}, orb_E = {}'.format(fx, orb_E))
        orb_E -= fx / dfx
    logger.debug('E = {} [degree]'.format(orb_E))

    # 地球を中心とする人工衛星の三次元座標計算
    # 人工衛星の軌道面上の座標(U, V)
    orb_U = orb_a * math.cos(math.radians(orb_E)) - orb_a * orb_e             # [km]
    orb_V = orb_a * math.sqrt(1 - orb_e ** 2) * math.sin(math.radians(orb_E)) # [km]
    orb_omega = orb_omega0 + (180 * 0.174 * (2 - 2.5 * (math.sin(math.radians(orb_i)) ** 2))) / (math.pi * ((orb_a / orb_r) ** 3.5)) * delta_t
    orb_OMEGA = orb_OMEGA0 - (180 * 0.174 * math.cos(math.radians(orb_i))) / (math.pi * ((orb_a / orb_r) ** 3.5)) * delta_t
    logger.debug('U = {} [km], V = {} [km], ω = {} [km], Ω = {} [km]'.format(orb_U, orb_V, orb_omega, orb_OMEGA))
    mat1 = numpy.matrix([
        [math.cos(math.radians(orb_OMEGA)), -math.sin(math.radians(orb_OMEGA)), 0],
        [math.sin(math.radians(orb_OMEGA)), math.cos(math.radians(orb_OMEGA)), 0],
        [0, 0, 1]
        ])
    mat2 = numpy.matrix([
        [1, 0, 0],
        [0, math.cos(math.radians(orb_i)), -math.sin(math.radians(orb_i))],
        [0, math.sin(math.radians(orb_i)), math.cos(math.radians(orb_i))]
        ])
    mat3 = numpy.matrix([
        [math.cos(math.radians(orb_omega)), -math.sin(math.radians(orb_omega)), 0],
        [math.sin(math.radians(orb_omega)), math.cos(math.radians(orb_omega)), 0],
        [0, 0, 1]
        ])
    mat4 = numpy.matrix([
        [orb_U],
        [orb_V],
        [0]
        ])
    mat_xyz = mat1 * mat2 * mat3 * mat4
    logger.debug('(x, y, z) = {}'.format(mat_xyz))

    # 観測時刻におけるグリニッジ子午線の赤経計算
    
    delta_T = (date - theta_0_date).total_seconds() / (60 * 60 * 24)    # その時刻から観測時刻までの日数 [day]
    tmp_theta_G = theta_0 + 1.002737909 * delta_T   # [rev]
    theta_G = (tmp_theta_G - int(tmp_theta_G)) * 360  # 観測時刻のグリニッジ恒星時 [deg]
    logger.debug('θG = {} [deg]'.format(theta_G))
    
    theta_G = siderealTime(date)
    logger.debug('θG = {} [deg]'.format(theta_G))

    # 人工衛星の緯度・経度計算
    mat5 = numpy.matrix([
        [math.cos(math.radians(-theta_G)), -math.sin(math.radians(-theta_G)), 0],
        [math.sin(math.radians(-theta_G)), math.cos(math.radians(-theta_G)), 0],
        [0, 0, 1]
        ])
    mat_XYZ = mat5 * mat_xyz
    logger.debug('(X, Y, Z) = {}'.format(mat_XYZ))
    X = mat_XYZ[0, 0]
    Y = mat_XYZ[1, 0]
    Z = mat_XYZ[2, 0]
    phi = math.degrees(math.asin(Z / math.sqrt(X ** 2 + Y ** 2 + Z ** 2)))
    lam = math.degrees(math.atan2(Y, X))
    logger.debug('lat = {}, lon = {}'.format(phi, lam))

    # 地心緯度から地理緯度へ変換
    a = 6378137.0   # 赤道半径
    b = 6356752.314245179  # 極半径
    e = math.sqrt(1 - (b ** 2 / a ** 2))
    phi2 = math.degrees(math.atan2(math.tan(math.radians(phi)), (b ** 2 / a ** 2))) # http://mikeo410.minim.ne.jp/cms/~shapeearthsurfacedistance
    logger.debug('lat = {}, lon = {}'.format(phi2, lam))
    phi3 = math.degrees(math.atan2(e ** 2 * math.sin(math.radians(phi)) * math.cos(math.radians(phi)), (1 - e ** 2 * (math.sin(math.radians(phi)) ** 2)))) + phi
    logger.debug('lat = {}, lon = {}'.format(phi3, lam))

    return (phi, lam)



###################################################################################################
# テスト用関数
###################################################################################################

def __testALOS():
    logger.info('ALOS')
    '''
    • 元期ET (Epoch Time)：軌道要素を確定した時刻　2006 年120.72277529 日(UT)
    • 近地点引数ω (Argument of perigee) 　ω0 = 14.7699◦
    • 軌道傾斜角i (inclination angle) 　i = 98.2104◦
    • 昇交点赤経Ω (right ascension of ascending node) 　Ω0 = 195.1270◦
    • 離心率e (Eccentricity) 　e = 0.0001679
    • 平均近点角M0 (Mean Anomaly) 　M0 = 345.3549◦
    • 平均運動M1 (Mean Motion) 　M1 = 14.59544429(rev/day)
    • 平均運動変化係数M2 　M2 = 0.00000232(rev/day2)
    この軌道要素を用いてALOS の位置を計算する．観測時刻として2006 年5 月15 日11 時(JST)を設定し，具体的な計算例を示す．
    '''
    epoch = datetime.datetime(2006, 1, 1, 0, 0, 0, 0, datetime.timezone.utc) + datetime.timedelta(days = 120.72277529 - 1)
    t = datetime.datetime(2006, 5, 15, 11, 0, 0, 0, datetime.timezone(datetime.timedelta(hours = +9))).astimezone(datetime.timezone.utc)
    logger.info('元期 = {}, ターゲット日時 = {}'.format(epoch, t))
    latlon = orbitalElementToLatLon(
        orb_ET      = epoch,
        orb_omega0  = 14.7699,
        orb_i       = 98.2104,
        orb_OMEGA0  = 195.1270,
        orb_e       = 0.0001679,
        orb_M0      = 345.3549,
        orb_M1      = 14.59544429,
        orb_M2      = 0.00000232,
        date        = t
        )
    logger.info('(緯度, 経度) = {}'.format(latlon))

def __testALOS_list():
    beginDate = datetime.datetime(2006, 5, 15, 11, 0, 0, 0, datetime.timezone(datetime.timedelta(hours = +9))).astimezone(datetime.timezone.utc)
    endDate = beginDate + datetime.timedelta(days=46)
    pointNum = 10000
    period = endDate - beginDate
    step = period / pointNum
    logger.info('beginDate = {}, endDate = {}, period = {}, step = {}'.format(beginDate, endDate, period, step))

    with open('D:/GIS/ArcGIS_Project/衛星軌道の描画/tle.txt') as file:
        s = file.read()
    logger.info('TLE = {}'.format(s))
    tle = TwoLineElements(s)

    timeLatLonList = []
    for count in range(0, pointNum):
        t = beginDate + step * count
        latlon = orbitalElementToLatLon(
                orb_ET      = datetime.datetime(2006, 1, 1, 0, 0, 0, 0, datetime.timezone.utc) + datetime.timedelta(days = 120.72277529 - 1),
                orb_omega0  = 14.7699,
                orb_i       = 98.2104,
                orb_OMEGA0  = 195.1270,
                orb_e       = 0.0001679,
                orb_M0      = 345.3549,
                orb_M1      = 14.59544429,
                orb_M2      = 0.00000232,
                date        = t
            )
        timeLatLonList.append([t, latlon[0], latlon[1]])
        logger.debug('t = {}, lat = {}, lon = {}'.format(t, latlon[0], latlon[1]))

    filepath = 'D:/GIS/ArcGIS_Project/衛星軌道の描画/軌道.csv'
    with open(filepath, mode='w') as file:
        for i in range(0, len(timeLatLonList) - 1):
            file.write('{},{},{},{},{}\n'.format(
                timeLatLonList[i][0].strftime('%Y/%m/%d %H:%M:%S'),
                timeLatLonList[i][1], timeLatLonList[i][2],
                timeLatLonList[i + 1][1], timeLatLonList[i + 1][2]))


def __testLandsat8():
    logger.info('Landsat-8')
    '''
    LANDSAT 8               
    1 39084U 13008A   20046.06823367  .00000004  00000-0  10818-4 0  9999
    2 39084  98.1977 117.6514 0001223  88.0107 272.1236 14.57115290372734
    '''
    epoch = datetime.datetime(2020, 1, 1, 0, 0, 0, 0, datetime.timezone.utc) + datetime.timedelta(days = 46.06823367 - 1)
    #t = datetime.datetime.now(datetime.timezone.utc)
    t = datetime.datetime(2020, 3, 1, 0, 0, 0, 0, datetime.timezone.utc)
    logger.info('元期 = {}, ターゲット日時 = {}'.format(epoch, t))
    latlon = orbitalElementToLatLon(
        orb_ET      = epoch,
        orb_omega0  = 88.0107,
        orb_i       = 98.1977,
        orb_OMEGA0  = 117.6514,
        orb_e       = 0.0001223,
        orb_M0      = 272.1236,
        orb_M1      = 14.57115290,
        orb_M2      = 0.00000004,
        date        = t
        )
    logger.info('(緯度, 経度) = {}'.format(latlon))


    with open('D:/GIS/ArcGIS_Project/衛星軌道の描画/tle.txt') as file:
        s = file.read()
    logger.info('TLE = {}'.format(s))
    tle = TwoLineElements(s)
    latlon = orbitalElementToLatLon(
        orb_ET      = tle.epoch_datetime,
        orb_omega0  = tle.argumentOfPerigee_float,
        orb_i       = tle.inclination_float,
        orb_OMEGA0  = tle.raan_float,
        orb_e       = tle.eccentricity_float,
        orb_M0      = tle.meanAnomaly_float,
        orb_M1      = tle.meanMotion_float,
        orb_M2      = tle.firstDerivativeMeanMotion_float,
        date        = t
        )
    logger.info('(緯度, 経度) = {}'.format(latlon))


def __testTLE():
    with open('D:/GIS/ArcGIS_Project/衛星軌道の描画/tle.txt') as file:
        s = file.read()
    logger.info('TLE = {}'.format(s))
    
    tle1 = TwoLineElements(s)
    print(tle1.elements)

    tle2 = TwoLineElements()
    
    # 0行目
    tle2.name = tle1.name
    # 1行目
    tle2.satelliteNumber = tle1.satelliteNumber
    tle2.classification = tle1.classification
    tle2.launchYear = tle1.launchYear
    tle2.launchNumber = tle1.launchNumber
    tle2.launchPiece = tle1.launchPiece
    tle2.epochYear = tle1.epochYear
    tle2.epochDay = tle1.epochDay
    tle2.firstDerivativeMeanMotion = tle1.firstDerivativeMeanMotion
    tle2.secondDerivativeMeanMotion = tle1.secondDerivativeMeanMotion
    tle2.bstar = tle1.bstar
    tle2.ephemerisType = tle1.ephemerisType
    tle2.elementNumber = tle1.elementNumber
    # 2行目
    tle2.satelliteNumber = tle1.satelliteNumber
    tle2.inclination = tle1.inclination
    tle2.raan = tle1.raan
    tle2.eccentricity = tle1.eccentricity
    tle2.argumentOfPerigee = tle1.argumentOfPerigee
    tle2.meanAnomaly = tle1.meanAnomaly
    tle2.meanMotion = tle1.meanMotion
    tle2.revolutionAtEpoch = tle1.revolutionAtEpoch

    print(tle2.elements)

    tle3 = TwoLineElements()

    # 1行目
    tle3.satelliteNumber = tle1.satelliteNumber_int
    tle3.launchYear = tle1.launchYear_int
    tle3.launchNumber = tle1.launchNumber_int
    tle3.epochYear = tle1.epochYear_int
    tle3.epochDay = tle1.epochDay_float
    tle3.firstDerivativeMeanMotion = tle1.firstDerivativeMeanMotion_float
    tle3.secondDerivativeMeanMotion = tle1.secondDerivativeMeanMotion_float
    tle3.bstar = tle1.bstar_float
    tle3.elementNumber = tle1.elementNumber_int
    # 2行目
    tle3.inclination = tle1.inclination_float
    tle3.raan = tle1.raan_float
    tle3.eccentricity = tle1.eccentricity_float
    tle3.argumentOfPerigee = tle1.argumentOfPerigee_float
    tle3.meanAnomaly = tle1.meanAnomaly_float
    tle3.meanMotion = tle1.meanMotion_float
    tle3.revolutionAtEpoch = tle1.revolutionAtEpoch_int

    print(tle3.elements)


###################################################################################################
# main関数
###################################################################################################

def main():

    __testTLE()

    #__testALOS()

    #__testALOS_list()

    __testLandsat8()

    exit()

    #beginDate = datetime.datetime(2020, 1, 1, 9, 0, 0, 0, datetime.timezone(datetime.timedelta(hours=+9))).astimezone(datetime.timezone.utc)
    beginDate = datetime.datetime.now(datetime.timezone.utc)
    endDate = beginDate + datetime.timedelta(days = 16)
    pointNum = 10000
    period = endDate - beginDate
    step = period / pointNum
    logger.info('beginDate = {}, endDate = {}, period = {}, step = {}'.format(beginDate, endDate, period, step))

    with open('D:/GIS/ArcGIS_Project/衛星軌道の描画/tle.txt') as file:
        s = file.read()
        logger.info('TLE = {}'.format(s))

    tle = TwoLineElements(s)

    timeLatLonList = []
    for count in range(0, pointNum):
        t = beginDate + step * count
        lat, lon = orbitalElementToLatLon(
            orb_ET      = tle.epoch_datetime,
            orb_omega0  = tle.argumentOfPerigee_float,
            orb_i       = tle.inclination_float,
            orb_OMEGA0  = tle.raan_float,
            orb_e       = tle.eccentricity_float,
            orb_M0      = tle.meanAnomaly_float,
            orb_M1      = tle.meanMotion_float,
            orb_M2      = tle.firstDerivativeMeanMotion_float,
            date        = t
            )
        timeLatLonList.append([t, lat, lon])
        logger.debug('t = {}, lat = {}, lon = {}'.format(t, lat, lon))

    filepath = 'D:/GIS/ArcGIS_Project/衛星軌道の描画/軌道.csv'
    with open(filepath, mode='w') as file:
        for i in range(0, len(timeLatLonList) - 1):
            file.write('{},{},{},{},{}\n'.format(
                timeLatLonList[i][0].strftime('%Y/%m/%d %H:%M:%S'),
                timeLatLonList[i][1], timeLatLonList[i][2],
                timeLatLonList[i + 1][1], timeLatLonList[i + 1][2]))


if __name__ == '__main__':
    main()