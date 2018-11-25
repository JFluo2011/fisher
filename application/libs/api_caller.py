import requests


class ApiCaller:
    @staticmethod
    def get(url, return_json=True):
        r = requests.get(url)
        print(url, r.status_code)
        if r.status_code != 200:
            return {} if return_json else ''
        return r.json() if return_json else r.text
