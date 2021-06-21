import time
import json
import requests


class FoodPandaSpider():
    """foodpanda 爬蟲"""
    def __init__(self, longitude, latitude) -> None:
        """初始化

        :param longitude: 自身所在經度
        :param latitude: 自身所在緯度
        """
        self.longitude = longitude
        self.latitude = latitude

    def request_get(self, url, params=None, headers=None):
        """送出 GET 請求，取得回傳 JSON 資料

        :param url: 請求網址
        :param params: 傳遞參數資料
        :param headers: 傳遞 headers 資料
        :return data: requests 回應資料
        """
        r = requests.get(url, params=params, headers=headers)
        if r.status_code != requests.codes.ok:
            print(f'網頁載入發生問題：{url}')
            return None
        try:
            data = r.json()
        except Exception as e:
            print(e)
            return None
        return data

    def request_post(self, url, params=None, data=None, headers=None):
        """送出 POST 請求，取得回傳 JSON 資料

        :param url: 請求網址
        :param params: 傳遞參數資料
        :param data: 傳遞 data 資料
        :param headers: 傳遞 headers 資料
        :return data: requests 回應資料
        """
        r = requests.post(url, params=params, data=data, headers=headers)
        if r.status_code != requests.codes.ok:
            print(f'網頁載入發生問題：{url}')
            return None
        try:
            data = r.json()
        except Exception as e:
            print(e)
            return None
        return data

    def search_restaurants(self, keyword, limit=48, offset=0):
        """搜尋餐廳

        :param keyword: 餐廳關鍵字
        :return restaurants: 搜尋結果餐廳列表
        """
        url = 'https://disco.deliveryhero.io/search/api/v1/feed'
        payload = {
            'q': keyword,
            'location': {
                'point': {
                    'longitude': self.longitude,  # 經度
                    'latitude': self.latitude  # 緯度
                }
            },
            'config': 'Variant17',
            'vertical_types': ['restaurants'],
            'include_component_types': ['vendors'],
            'include_fields': ['feed'],
            'language_id': '6',
            'opening_type': 'delivery',
            'platform': 'web',
            'language_code': 'zh',
            'customer_type': 'regular',
            'limit': limit,  # 一次最多顯示幾筆(預設 48 筆)
            'offset': offset,  # 偏移值，想要獲取更多資料時使用
            'dynamic_pricing': 0,
            'brand': 'foodpanda',
            'country_code': 'tw',
            'use_free_delivery_label': False
        }
        headers = {
            'content-type': "application/json",
        }
        data = self.request_post(url=url, data=json.dumps(payload), headers=headers)
        if not data:
            print('搜尋餐廳失敗')
            return []

        try:
            restaurants = data['feed']['items'][0]['items']
        except Exception as e:
            print(f'資料格式有誤：{e}')
            return []
        return restaurants

    def get_nearby_restaurants(
            self, way='外送', sort='', cuisine='', food_characteristic='',
            budgets='', has_discount=False, limit=48, offset=0):
        """取得附近所有餐廳

        :param way: 取餐方式(外送、外帶自取、生鮮雜貨)
        :param sort: 餐廳排序(rating_desc、delivery_time_asc、distance_asc)
        :param cuisine: 料理種類
        :param food_characteristic: 特色
        :param budgets: 預算
        :param has_discount: 是否有折扣
        :return restaurants: 附近所有餐廳結果
        """
        url = 'https://disco.deliveryhero.io/listing/api/v1/pandora/vendors'
        query = {
            'longitude': self.longitude,
            'latitude': self.latitude,
            'language_id': 6,
            'include': 'characteristics',
            'dynamic_pricing': 0,
            'configuration': 'Variant1',
            'country': 'tw',
            'budgets': budgets,
            'cuisine': cuisine,
            'sort': sort,
            'food_characteristic': food_characteristic,
            'use_free_delivery_label': False,
            'vertical': 'restaurants',
            'limit': limit,
            'offset': offset,
            'customer_type': 'regular'
        }
        headers = {
            'x-disco-client-id': 'web',
        }
        # 取餐方式
        if way == '外送':
            query['vertical'] = 'restaurants'
        elif way == '外帶自取':
            query['vertical'] = 'restaurants'
            query['opening_type'] = 'pickup'
        else:
            query['vertical'] = 'shop'
        # 是否有折扣
        if has_discount:
            query['has_discount'] = 1

        data = self.request_get(url=url, params=query, headers=headers)
        if not data:
            print('取得附近所有餐廳失敗')
            return []

        try:
            restaurants = data['data']['items']
        except Exception as e:
            print(f'資料格式有誤：{e}')
            return []
        return restaurants

    def get_recommendation_restaurants(self, way='外送'):
        """取得分類推薦的餐廳

        :param way: 取餐方式(外送、外帶自取、生鮮雜貨)
        :return restaurants: 分類推薦結果
        """
        url = 'https://disco.deliveryhero.io/core/api/v1/swimlanes'
        query = {
            'longitude': self.longitude,
            'latitude': self.latitude,
            'brand': 'foodpanda',
            'language_code': 'zh',
            'language_id': 6,
            'country_code': 'tw',
            'dynamic_pricing': 0,
            'use_free_delivery_label': False,
            'customer_type': 'regular'
        }
        # 取餐方式
        if way == '外送':
            query['config'] = 'Original'
            query['vertical_type'] = 'restaurants'
            query['opening_type'] = 'delivery'
        elif way == '外帶自取':
            query['config'] = 'control'
            query['vertical_type'] = 'restaurants'
            query['opening_type'] = 'pickup'
        else:
            query['config'] = 'shops-variant'
            query['vertical_type'] = 'shop,darkstores'
            query['opening_type'] = 'delivery'

        data = self.request_get(url=url, params=query)
        if not data:
            print('取得分類推薦的餐廳失敗')
            return []

        try:
            recommendations = data['data']['items']
        except Exception as e:
            print(f'資料格式有誤：{e}')
            return []
        return recommendations

    def get_info_menu(self, restaurant_code):
        """取得餐廳基本資料與菜單

        :param restaurant_code: 餐廳代碼
        :return info_menu: 餐廳基本資料與菜單
        """
        url = f'https://tw.fd-api.com/api/v5/vendors/{restaurant_code}'
        query = {
            'include': 'menus',
            'language_id': '6',
            'dynamic_pricing': '0',
            'opening_type': 'delivery',
            'longitude': self.longitude,    # 非必要(影響顯示距離)
            'latitude': self.latitude
        }
        data = self.request_get(url=url, params=query)
        if (not data) or ('data' not in data):
            print('取得餐廳菜單失敗')
            return {}
        info_menu = data['data']
        return info_menu


if __name__ == '__main__':
    khh_station = (120.3025185, 22.639473)  # 高雄車站的經緯度
    # khh_station = (120.6452531, 24.1790234)

    foodpanda_spider = FoodPandaSpider(khh_station[0], khh_station[1])

    # 搜尋餐廳
    # restaurants = foodpanda_spider.search_restaurants('星巴克')
    # ## print(json.dumps(restaurants[0]))
    # for restaurant in restaurants[:5]:
    #     print(restaurant['name'])

    # 取得附近所有餐廳
    # restaurants = foodpanda_spider.get_nearby_restaurants(
    #     sort='rating_desc',  # 按照評分排序
    #     cuisine='164,179'  # 日韓+美式
    # )
    # for restaurant in restaurants[:5]:
    #     print(restaurant['name'])

    # 取得分類推薦的餐廳
    # recommendations = foodpanda_spider.get_recommendation_restaurants()
    # for recommendation in recommendations[:5]:
    #     print(recommendation['headline'])

    # 取得餐廳基本資料與菜單
    # info_menu = foodpanda_spider.get_info_menu('g1mk')
    # print(info_menu['name'])
