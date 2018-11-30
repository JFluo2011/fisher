import requests


class ApiCaller:

    @staticmethod
    def get(url, headers=None, params=None, return_json=True):
        try:
            r = requests.get(url, headers=headers, params=params)
        except Exception as err:
            print(str(err))
            return {} if return_json else ''

        if r.status_code != 200:
            return {} if return_json else ''
        return r.json() if return_json else r.text

    @staticmethod
    def post(url, headers=None, data=None, params=None, return_json=True):
        pass
