import datetime

from pyorbital.orbital import Orbital
from pyorbital.tlefile import Tle


# TLEの読み込み
aqua_tle = Tle('LANDSAT 8', 'D:/GIS/ArcGIS_Project/衛星軌道の描画/tle.txt')
aqua_orbit = Orbital('LANDSAT 8', line1=aqua_tle.line1, line2=aqua_tle.line2)

#now = datetime.datetime.utcnow()
now = t = datetime.datetime(2020, 3, 1, 0, 0, 0, 0, datetime.timezone.utc)

# 現在の緯度、経度、高度を取得
lon, lat, alt = aqua_orbit.get_lonlatalt(now)
print('Aquaの現在地')
print('経度: ', lon)
print('緯度: ', lat)
print('高度[km]: ', alt)
print('')

# 24時間以内に東京タワーから衛星が見える時間を計算
pass_time_list = (aqua_orbit.get_next_passes(utc_time=now, length=24,
                                             lon=139.75, lat=35.66, alt=0.333))
print('次にAquaが到来する時刻[UTC]: ',
      pass_time_list[0][0].strftime('%Y/%m/%d %H:%M:%S'))


#exit()


#beginDate = datetime.datetime(2020, 1, 1, 9, 0, 0, 0, datetime.timezone(datetime.timedelta(hours=+9))).astimezone(datetime.timezone.utc)
beginDate = datetime.datetime.now(datetime.timezone.utc)
endDate = beginDate + datetime.timedelta(days = 16)
pointNum = 10000
period = endDate - beginDate
step = period / pointNum
#logger.info('beginDate = {}, endDate = {}, period = {}, step = {}'.format(beginDate, endDate, period, step))

with open('D:/GIS/ArcGIS_Project/衛星軌道の描画/tle.txt') as file:
    s = file.read()
    #logger.info('TLE = {}'.format(s))

#tle = TwoLineElements(s)

timeLatLonList = []
for count in range(0, pointNum):
    t = beginDate + step * count

    lon, lat, alt = aqua_orbit.get_lonlatalt(t)
    
    timeLatLonList.append([t, lat, lon])
    #logger.debug('t = {}, lat = {}, lon = {}'.format(t, lat, lon))

filepath = 'D:/GIS/ArcGIS_Project/衛星軌道の描画/軌道2.csv'
with open(filepath, mode='w') as file:
    for i in range(0, len(timeLatLonList) - 1):
        file.write('{},{},{},{},{}\n'.format(
            timeLatLonList[i][0].strftime('%Y/%m/%d %H:%M:%S'),
            timeLatLonList[i][1], timeLatLonList[i][2],
            timeLatLonList[i + 1][1], timeLatLonList[i + 1][2]))