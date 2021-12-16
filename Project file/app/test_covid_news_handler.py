from covid_news_handler import news_API_request, update_news
import pytest

def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid, COVID-19, coronavirus') == news_API_request()
    covid_news = news_API_request('Covid, COVID-19, coronavirus')
    assert type(covid_news) == list
    assert type(covid_news[0]) == dict
    assert covid_news[0]["title"]

def test_update_news():
    update_news(10, 'test')
