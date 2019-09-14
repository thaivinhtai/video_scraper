import requests
import time
from requests.exceptions import HTTPError


class Episode:
    def __init__(
        self,
        title,
        page_url,
        image_url,
        broadcasting_date,
        **kwargs
    ):
        self.__title = title
        self.__page_url = page_url
        self.__image_url = image_url
        self.__broadcasting_date = broadcasting_date
        self.__duration = kwargs['duration']
        self.__episode_id = kwargs['episode_id']

    @property
    def title(self):
        """return value of self.__tittle"""
        return self.__title

    @property
    def page_url(self):
        """return value of self.__page_url"""
        return self.__page_url

    @property
    def image_url(self):
        """return value of self.__image_url"""
        return self.__image_url

    @property
    def broadcasting_date(self):
        """return value of self.__broadcasting_date"""
        return self.__broadcasting_date

    @property
    def duration(self):
        """return value of self.__duration"""
        return self.__duration

    @property
    def episode_id(self):
        """return value of self.__episode_id"""
        return self.__episode_id

    @staticmethod
    def __parse_episode_id(url):
        """Find episode identifier.

        """
        return url[(url.find("images/") + 7):(len(url) - 4)]

    @staticmethod
    def from_json(payload):
        payload["url"] = f'http://www.tv5monde.com{payload["url"]}'
        return Episode(
            title=payload["title"],
            page_url=payload["url"],
            image_url=payload["image"],
            broadcasting_date=payload["date"],
            duration=payload["duration"],
            episode_id=Episode.__parse_episode_id(payload["image"])
        )


def read_data_from_url(url):
    headers = {
        'User-Agent': ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" +
                       "(KHTML, like Gecko) Chrome/51.0.2704.106" +
                       "Safari/537.36 OPR/38.0.2220.41"),
        'From': "contact@intek.edu.vn",
    }
    return requests.get(url, headers=headers)


def read_url(
        url,
        maximum_attempt_count=3,
        sleep_duration_between_attempts=10):
    """
    Return data fetched from a HTTP endpoint.


    :param url: A Uniform Resource Locator (URL) that references the
        endpoint to open and read data from.

    :param maximum_attempt_count: Maximal number of failed attempts to
        fetch data from the specified URL before the function raises an
        exception.

    :param sleep_duration_between_attempts: Time in seconds during which
        the current thread is suspended after a failed attempt to fetch
         data from the specified URL, before a next attempt.


    :return: The data read from the specified URL.


    :raise HTTPError: If an error occurs when trying unsuccessfully
        several times to fetch data from the specified URL, after
    """
    data_from_server = read_data_from_url(url)
    if data_from_server.status_code in range(400, 500):
        raise HTTPError(f'HTTP Error {data_from_server.status_code}')
    if data_from_server.status_code == 200:
        print("OK")
        data_from_server.encoding = 'utf-8'
        return data_from_server.json()
    while maximum_attempt_count > 0:
        time.sleep(sleep_duration_between_attempts)
        read_url(url=url, maximum_attempt_count=maximum_attempt_count - 1,
                 sleep_duration_between_attempts=10)
    raise HTTPError(f'HTTP Error {data_from_server.status_code}')


def fetch_episodes(url):
    json_content = read_url(url)
    list_episodes_in_json = json_content['episodes']
    max_page = json_content['numPages']
    for page in range(2, max_page + 1):
        json_content = read_url(f'{url}?page={page}')
        list_episodes_in_json += json_content['episodes']
    list_episodes = []
    for ep in list_episodes_in_json:
        list_episodes.append(Episode.from_json(ep))
    return list_episodes


if __name__ == "__main__":
    list_episodes =\
        fetch_episodes("http://www.tv5monde.com/emissions/episodes/merci-professeur.json")
    for ep in list_episodes:
        print(ep.title)
    print(len(list_episodes))
