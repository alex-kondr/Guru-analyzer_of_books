import requests


def check_url_exists(url):
    try:
        response = requests.get(url)
        if response.status_code // 100 == 2:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False
