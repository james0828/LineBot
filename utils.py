import requests
import json
import re
import datetime

class UTILS:
  @staticmethod
  def highway_crawler(param={}):
    def verify_date(strr):
      if len(strr) != 10: return False
      format = "%Y/%m/%d"
      print(strr)
      try:
        datetime.datetime.strptime(strr, format)
        return True
      except ValueError as e:
        print(e)
        return False

    def verify_time(strr):
      if len(strr) != 5: return False
      format = '%H:%M'
      try:
        datetime.datetime.strptime(strr, format)
        return True
      except ValueError:
        return False
    
    stations = {
      '南港': 'NanGang',
      '台北': 'TaiPei',
      '板橋': 'BanQiao',
      '桃園': 'TaoYuan',
      '新竹': 'XinZhu',
      '苗栗': 'MiaoLi',
      '台中': 'TaiZhong',
      '彰化': 'ZhangHua',
      '雲林': 'YunLin',
      '嘉義': 'JiaYi',
      '台南': 'TaiNan',
      '左營': 'ZuoYing'
    }

    # verify data
    if not (param.get('start_station', '') in stations and param.get('return_station', '') in stations
      and verify_date(param.get('start_date', '')) and verify_time(param.get('start_time', ''))):
      return False

    if param.get('search_type', '') == 'R':
      if not (verify_date(param.get('return_date', '')) and verify_time(param.get('return_time', ''))):
        return False
      

    payloads = {
      "StartStation": stations[param.get('start_station', '')],
      "EndStation": stations[param.get('return_station', '')],
      "OutWardSearchDate": param.get('start_date', ''),
      "OutWardSearchTime": param.get('start_time', ''),
      "ReturnSearchDate": param.get('return_date', ''),
      "ReturnSearchTime": param.get('return_time', ''),
      "SearchType": param.get('search_type', ''),
      "Lang": "TW"
    }

    url = 'https://www.thsrc.com.tw/TimeTable/Search'
    res = requests.post(url, json=payloads)

    if res.status_code >= 400:
      return False

    data = res.json()

    trainItem = data['data']['DepartureTable']['TrainItem']
    train_list = []
    messages = []

    messages.append('去程')

    message = '起始站: {}, 終點站: {}\n'.format(data['data']['DepartureTable']['Title']['StartStationName'], data['data']['DepartureTable']['Title']['EndStationName'])
    message += '車次 發車時間-到站時間 總長\n'

    for item in data['data']['DepartureTable']['TrainItem'][:10]:
      message += '{} {}-{} {}\n'.format(item['TrainNumber'], item['DepartureTime'], item['DestinationTime'], item['Duration'])
    
    messages.append(message)

    if param.get('search_type', '') == 'R':
      messages.append('回程')
      message = '起始站: {}, 終點站: {}\n'.format(data['data']['DestinationTable']['Title']['StartStationName'], data['data']['DestinationTable']['Title']['EndStationName'])
      message += '車次 發車時間-到站時間 總長\n'

      for item in data['data']['DestinationTable']['TrainItem'][:10]:
        message += '{} {}-{} {}\n'.format(item['TrainNumber'], item['DepartureTime'], item['DestinationTime'], item['Duration'])

      messages.append(message)
    
    return messages