import logging
from datetime import date, timedelta
import typing
from newsapi import NewsApiClient
from covid_data_handler import search_json_file, write_to_temp,shed,delete_update,delay,sched
blacklist = []



def news_API_request(covid_terms: str = 'Covid, COVID-19, coronavirus') -> list:
  '''
  Takes covid_terms (string of search terms for NewsApiClient).

  Uses the paramiter given in config (search terms, max age of articles, etc) to pull data from news websites (also defined in config).

  Returns covid_news (list of dicts of all articles pulled in order of relevancy).
  '''
  try:
    newsapi = NewsApiClient(api_key=search_json_file("../config.json","api_key"))
    all_articles = newsapi.get_everything(
        q=covid_terms,
        domains=search_json_file("../config.json","domains"),
        from_param= date.today(),
        to= date.today() - timedelta(days = int(search_json_file("../config.json","age_of_articles_days"))),
        language='en',
        sort_by='relevancy',
        page=1)
    return covid_news_handling(all_articles)
  except:
    logging.warning("news_API_request failed, check or re-download config.json")
    quit()


def covid_news_handling(all_articles: dict)-> list:
  '''
  Takes all_articles (dict of all articles pulled from NewsApiClient in order of relevancy).

  Processes the articles in conjunction with parameters set in config (e.g. number of articles to display).

  Returns covid_news (a list of dictionaries holding data for news updates).
  '''
  try:
    logging.info("covid_news_handling called")
    articles_list = all_articles["articles"]
    covid_news = []
    for articles in articles_list:
      if articles["title"] not in blacklist:
        dic = {"title": articles["title"], "content" : articles["description"]}
        covid_news.append(dic)
    if len(covid_news) < 5:
      slice = 0
      slice2 = len(covid_news)
    else:
      slice = 0
      slice2 = int(search_json_file("../config.json","num_of_articles"))
    covid_news = covid_news[slice:slice2]
    return(covid_news)
  except:
    logging.warning("covid_news_handling failed")
    quit()


def append_blacklist(news_response:str):
  '''
  Takes news_response (name of news article to be removed)

  Appends article name to blacklist, which is checked when adding news articles to website.
  '''
  try:
    global blacklist
    blacklist.append(news_response)
  except:
    logging.warning("append_blacklist failed")


def repeat_news_update(update_name: str,id_location:str,update_id:str)-> None:
  '''
  Takes update_name (name of update being reviewed), id_location (key of schedule event id in update dictionary) and update_id (given schedule event id to search for)

  Checks if scheduled update should be refreshed, if not then the corrisponding update lable is deleted.

  Returns update_news if the updated is repeated or delete_update otherwise.
  '''
  try:
    global pending_updates
    from covid_data_handler import pending_updates
    for updates in pending_updates:
      if updates[id_location] == update_id:
        if updates["repeat"]:
          update_news(delay(updates["time"]),update_name)
        else:
          delete_update(update_name)
  except:
    logging.warning("repeat_news_update failed")


def update_news(update_interval: int, update_name: str) -> typing.Tuple[sched.Event, sched.Event]:
  '''
  Takes update_interval(time in seconds until next update) and update_name

  Schedules update for get_news_data which will refresh the news data stored in temp file temp_news.json,
  Schedules repeat_news_update with same time interval as News_update,

  Returns News_update and repeat_news, both are id tags for the schedulers
  '''
  try:
    News_update = shed.enter(update_interval,1,get_news_data)
    repeat_news = shed.enter(update_interval,2,repeat_news_update,(update_name,"update_News",News_update))
    return News_update,repeat_news
  except:
    logging.warning("update_news failed")


def get_news_data()-> None:
  '''
  Calls covid_news_handling with news_API_request, reciving new news data, 
  Writes News_data (the list of dicts containing the news data) to temp_news.json.
  '''
  try:
    News_data = news_API_request()
    write_to_temp(News_data,"News_data","temp/temp_news.json","w")
  except:
    logging.warning("get_news_data failed")
