import boto3
import requests
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('cowin_users')
current_date = datetime.today().strftime('%d-%m-%Y')


class Cowin:
    def __init__(self):
        self.base_url = "https://cdn-api.co-vin.in/api"
        self.urls = {
            "availability": {
                "district": "/v2/appointment/sessions/public/findByDistrict",
                "pin": "/v2/appointment/sessions/public/findByPin",
                "calendar": {
                    "district": "/v2/appointment/sessions/public/calendarByDistrict",
                    "pin": "/v2/appointment/sessions/public/calendarByPin",
                }
            }
        }
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, '
                                      'like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    @staticmethod
    def cleanse_centers(data):
        under45_list = []
        # print("=====Cleansing data===")
        # print(data)
        for center in data['centers']:
            under_45_sessions = [i for i in center['sessions'] if
                                 int(i.get("min_age_limit")) == 18 and int(i.get("available_capacity")) > 0]
            if under_45_sessions:
                center['sessions'] = under_45_sessions
                under45_list.extend([center])

        return under45_list

    def get_calendar_by_district(self, district_id, date):
        params = {
            "district_id": district_id,
            "date": date
        }
        url = "{}{}".format(self.base_url, self.urls['availability']['calendar']['district'])
        response = requests.get(url, params=params, headers=self.headers)
        data = response.json()
        return data

    def get_calendar_by_pin(self, pincode, date):
        params = {
            "pincode": pincode,
            "date": date
        }
        url = "{}{}".format(self.base_url, self.urls['availability']['calendar']['pin'])
        response = requests.get(url, params=params, headers=self.headers)
        data = response.json()
        return data

    def get_calendar_by_filter(self, filter, date, pincode=None, district_id=None):
        if filter == "pincode":
            data = self.get_calendar_by_pin(pincode, date)
        else:
            data = self.get_calendar_by_district(district_id, date)
        cleansed_data = self.cleanse_centers(data)
        return cleansed_data

    def get_by_pin(self, pincode, date):
        params = {
            "pincode": pincode,
            "date": date
        }
        url = "{}{}".format(self.base_url, self.urls['availability']['pin'])
        response = requests.get(url, params=params, headers=self.headers)
        data = response.json()
        return data

    def get_by_district(self, district, date):
        params = {
            "district": district,
            "date": date
        }
        url = "{}{}".format(self.base_url, self.urls['availability']['district'])
        response = requests.get(url, params=params, headers=self.headers)
        data = response.json()
        return data

    def get_by_filter(self,filter, date, pincode=None, district_id=None):
        if filter == "pincode":
            data = self.get_by_pin(pincode, date)
        else:
            data = self.get_by_district(district_id, date)
        cleansed_data = self.cleanse_centers(data)
        return cleansed_data