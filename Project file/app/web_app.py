from flask import Flask, render_template, request
from covid_data_handler import get_covid_data, log, search_json_file,schedule_covid_updates,delete_update,shed,delay,pending_updates,pending_updates_append, logging
from covid_news_handler import get_news_data,append_blacklist,update_news
import json



def delete_news_items(delete_news:str)->None:
    '''
    Takes delete_news (title of article to be removed)

    Appends delete_news to blacklist using append_blacklist
    '''
    append_blacklist(delete_news)
    global News_data
    News_data = get_news_data()


def check_update_namespace(update_name:str) -> bool:
    '''
    Takes update_name (title of article to be removed)

    Checks if name is already being used for an update
    '''
    try:
        for dic in pending_updates:
            if dic["update_note"]["title"] == update_name:
                return False
        return True
    except:
        logging.warning("check_update_namespace failed")


def process_updates(update_name:str,update_time,repeat,covid_data_request,news_request)-> None:
    '''
    Takes update_name, update_time, repeat, covid_data_request and news_request

    Calls valid update and news schedulers using schedule_covid_updates, update_news and pending_updates_append
    '''
    global News_data
    global Covid_data
    #check if time has been entered
    try:
        if update_time:
            time_delay = delay(update_time)
        else:
            return False
        #check if update name is already being used
        if check_update_namespace(update_name):
            #check one of the two update options has been selected
            if covid_data_request or news_request:
                #If both updates have been called
                if covid_data_request and news_request:
                    Covid_update,repeat_id_covid = schedule_covid_updates(time_delay,update_name)
                    News_update,repeat_id_news = update_news(time_delay,update_name)
                    pending_updates_append({"update_note": {"title": update_name, "content": f"updating covid data and news at {update_time}"},
                    "update_Covid":Covid_update ,"update_News":News_update, "repeat":repeat,"repeat_id_news":repeat_id_news,"repeat_id_covid":repeat_id_covid,"time":update_time})
                else:
                    #if only covid data has been called
                    if covid_data_request:
                        Covid_update,repeat_id_covid = schedule_covid_updates(time_delay,update_name)
                        pending_updates_append({"update_note": {"title": update_name, "content": f"updating covid data at {update_time}"}, "update_Covid":Covid_update ,
                        "update_News":"False", "repeat":repeat,"repeat_id_news":False,"repeat_id_covid":repeat_id_covid,"time":update_time })
                    #if only covid news has been called
                    elif news_request:
                        News_update,repeat_id_news = update_news(time_delay,update_name)
                        pending_updates_append({"update_note": {"title": update_name, "content": f"updating news at {update_time}"}, "update_Covid":"False","update_News":News_update,
                        "repeat":repeat,"repeat_id_news":repeat_id_news,"repeat_id_covid":False,"time":update_time })
            else:
                return False
        else:
            return False
    except:
        logging.warning("process_updates failed")


def list_of_dic(search_term:str,dic_list:list)-> list:
    try:
        new_dic_list = []
        for dic in dic_list:
            new_dic_list.append(dic[search_term])
        return (new_dic_list)
    except:
        logging.warning("list_of_dic failed")


#flask app
app = Flask(__name__)
@app.route("/")
@app.route("/index")
def init():
    '''
    Updates and fetches data from web app
    '''
    if request.args.get("notif"):
        delete_news_items(request.args.get("notif"))
    if request.args.get("update_item"):
        delete_update(request.args.get("update_item"))
    if request.args.get("two"):
        process_updates(request.args.get("two"),request.args.get("update"),request.args.get("repeat"),
        request.args.get("covid-data"),request.args.get("news"))
    shed.run(blocking= False)
    Covid_data = search_json_file("temp/temp.json","Covid_data")
    News_data =search_json_file("temp/temp_news.json","News_data")
    from covid_data_handler import pending_updates
    return render_template(
        'index.html',
        title = "Daily updates",
        location = Covid_data["location"],
        nation_location = Covid_data["national_location"],
        local_7day_infections = Covid_data["local_7day_av"],
        national_7day_infections = Covid_data["national_7day_av"],
        deaths_total = Covid_data["national_deaths_total"],
        hospital_cases =  Covid_data["national_hospital_cases_current"],
        image = image_name,
        news_articles = News_data,
        updates = list_of_dic("update_note",pending_updates)
    )
if __name__ == "__main__":
    get_covid_data()
    get_news_data()
    log()
    logging.info("web app running")
    image_name = search_json_file("../config.json","image")
    app.run()