import logging
import sys
import os.path
from uk_covid19 import Cov19API
import json
import sched
import time
from datetime import datetime
import typing
shed = sched.scheduler(time.time, time.sleep)
pending_updates = []



#start
def log()-> None:
  ''' 
  Initiates logging with the logging file log.log in directory.

  Takes no arguments and returns no arguments.
  '''
  try:
    log = logging.getLogger()
    handler = logging.FileHandler("log.log")
    handler.setFormatter(logging.Formatter("%(asctime)s, %(levelname)s, %(message)s")) 
    log.addHandler(handler)
    log.setLevel(logging.INFO)
  except:
    print("log failed to initialize")

def initilize_app():
  '''
  Calls log and checks for config, the config file used for the application.

  Takes no arguments and returns no argument.
  '''
  log()
  try:
    #config identifies if the config file is present, it will be used in most functions so I've decided it's approprate to make it global
    #checking for config file
    if os.path.exists('../config.json'):
      return
    else:
      #config file not found, logging and returning default behaviour
      logging.warning("config file not found, will use the default settings")
      return
  except:
    logging.warning("initilize_app failed")




#CSV read:

def csv_to_list(csv_filename: str) -> list:
  '''
  Takes csv_filename, the name of the CSV file the user wants to read from.

  Reads from the CSV file and appends the lines to a list.
  
  Returns a list of lines from the CSV file.
  '''
  try:
    #creating covid_csv_datas for use later 
    covid_csv_data_whole = []
    covid_csv_data = []
    
    #reading csv_file into a list, line by line
    csv_file = open(csv_filename, "r").readlines()
    for line in csv_file:
      line = (line.replace("\n", ""))
      #checks if line is empty, if not, it is appended
      if len(line) == 0:
        continue
      else:
        covid_csv_data_whole.append(line)
  
    #breaking working data into a list of lists
    for element in covid_csv_data_whole:
      data = element.split(",")
      covid_csv_data.append(data)
    return(covid_csv_data)
  except:
    logging.warning("csv_to_list failed")


def parse_csv_data(csv_filename: str) -> list:
  '''
  Takes csv_filename, the name of the CSV file the user wants to read from.

  Checks that the filename is valid (exists), 
  if the filename is invalid(doesn't exist in location) the user will be prompted to give a valid filename until it passes the check,
  once the filename is valid, the program passes the filename to covid_csv_data which returns the CSV file as a list of lines,

  Returns covid_csv_data, a list of the lines of the given csv file.
  '''
  try:
    #checking if CSV file exists/ filename is correct
    while os.path.exists(csv_filename) == False or csv_filename[-3:] != "csv":
      csv_filename = input('invalid file name, please check file name is spelt correctly, that file exists in directory and that the file is a .csv file \nenter file name: ')
    covid_csv_data = csv_to_list(csv_filename)
    return(covid_csv_data)
  except:
    logging.warning("parse_csv_data failed")


def process_covid_csv_data(covid_csv_data: list) -> typing.Tuple[int, int, int]:
  '''
  Takes covid_csv_data, a list of lines from the given csv file,

  Checks for new_daily_cases_row (index of row contatining daily cases data), current_hospital_cases_row (index of row contatining current hospital cases data)
  and deaths_total_row (index of row contatining  sum deaths) in config using search_json_file (),
  Searches through each row, identifying first non-empty row (for new_daily_cases the 2nd available row),
  Calculates sum_cas_last_7days (sum of cases of the last 7 days, not including first available day),

  Returns sum_cas_last_7days, curr_hosp_cas and cum_deaths, all int values
  '''
  try:
    #find row of daily cases from config, check if each line has int data, skip the first data holding line and get sum of the next 7
    new_daily_cases_row = (int(search_json_file("../config.json","new_daily_cases_row")) - 1)
    sum_cas_last_7days_list = 0
    daily_counter = 0
    for line in covid_csv_data:
      if daily_counter < 8:
        try:
          type_check = int(line[new_daily_cases_row])
        except:
          type_check = str
        if type(type_check) == int:
          if daily_counter > 0:
            sum_cas_last_7days_list = sum_cas_last_7days_list + (int(line[new_daily_cases_row]))
            daily_counter = daily_counter + 1
          else:
            daily_counter = daily_counter + 1
      else:
        break
      
    #find row of current hospital cases from config, check if each line has int data, return first line that holds a value
    current_hospital_cases_row = (int(search_json_file("../config.json","current_hospital_cases_row")) - 1)
    for line in covid_csv_data:
        try:
          type_check = int(line[current_hospital_cases_row])
        except:
          type_check = str
        if type(type_check) == int:
          curr_hosp_cas = int(line[current_hospital_cases_row])
          break
        else:
          pass
    #find row of accumulative deaths from config, check if each line has int data, return first line that holds a value
    accumulative_deaths_row = (int(search_json_file("../config.json","deaths_total_row")) - 1)
    for line in covid_csv_data:
        try:
          type_check = int(line[accumulative_deaths_row])
        except:
          type_check = str
        if type(type_check) == int:
          cum_deaths = int(line[accumulative_deaths_row])
          break
        else:
          pass

    return(sum_cas_last_7days_list,curr_hosp_cas,cum_deaths)
  except: 
    logging.warning("process_covid_csv_data failed, data invalid or missing, please check file contence and config")


def initilize_CSV_read():
  '''
  Asks user to enter filename and passes that to parse_csv_data, 
  takes and prints sum_cas_last_7days, curr_hosp_cas and cum_deaths from process_covid_csv_data
  returns loop
  '''
  logging.info("CSV_read initilized")
  try:
    csv_filename = input("enter file name: ")
    sum_cas_last_7days,curr_hosp_cas,cum_deaths = process_covid_csv_data(parse_csv_data(csv_filename))
    print("sum cases last 7days:",sum_cas_last_7days,"current hospital cases:",curr_hosp_cas,"cummulative deaths:",cum_deaths)
    logging.info("initilize_CSV_read finished successfully")
    return loop(sum_cas_last_7days,curr_hosp_cas,cum_deaths)
  except:
    logging.warning("initilize_CSV_read failed")


def loop(sum_cas_last_7days,curr_hosp_cas,cum_deaths: typing.Tuple[int, int, int]):
  '''
  Takes sum_cas_last_7days, curr_hosp_cas and cum_deaths from initilize_CSV_read
  Gives the user the option to extract data from another file
  returns initilize_CSV_read if repeat is selected and sum_cas_last_7days, curr_hosp_cas and cum_deaths if repeat is denied
  '''
  try:
    ans = input("Would you like to repeat [Y/n}: ")
    if ans == "Y":
      return initilize_CSV_read()
    elif ans == "n":
      return(sum_cas_last_7days,curr_hosp_cas,cum_deaths)
    else:
      print("invalid answer")
      return loop()
  except:
    logging.warning("loop failed")




#Core Covid web App:

def covid_API_request(location : str ="Exeter", location_type: str ="ltla" ) -> dict:
  '''
  Takes location(local location) and location_type, both are str

  Fetches national location and skip_lines_api (days skipped) from config,
  Uses Cov19API to fetch up-to-date covid data for the local location and national location,
  Uses data_handler to calculate local_7day_av and national_7day_av,
  Uses covid_data_handler_dead_hospitalized to caclculate national_deaths_total and national_hospital_cases_current
  
  Returns location, national_location both are str 
  and local_7day_av, national_7day_av, national_deaths_total and national_hospital_cases_current all are int
  '''
  try:
    logging.info("covid_API_request called")
    #find and download json file from API:
    nation_location = search_json_file("../config.json","nation")
    local_location = [
      f'areaType={location_type}',
      f'areaName={location}']
    national_location = [
      'areaType=nation',
      f'areaName={nation_location}']
    cases_and_deaths = {
      "date" : "date",
      "newCases": "newCasesByPublishDate",
      "cumDeaths": "cumDeaths28DaysByDeathDate",
      "hospitalCases":"hospitalCases"}
    local_API_data = Cov19API(filters=local_location, structure=cases_and_deaths).get_json()
    national_API_data = Cov19API(filters=national_location,structure=cases_and_deaths).get_json()
    #find skip_lines_api to avoid repeated calculation
    skip_lines_api = int(search_json_file("../config.json","skip_lines_api"))
    #get final data
    local_7day_av = round(data_handler((local_API_data),skip_lines_api))
    national_7day_av = round(data_handler((national_API_data),skip_lines_api))
    national_deaths_total,national_hospital_cases_current = covid_data_handler_dead_hospitalized(national_API_data,skip_lines_api)
    #make Covid_data dict
    Covid_data = {"location": location, "national_location": nation_location,"local_7day_av": local_7day_av, "national_7day_av": national_7day_av, "national_deaths_total": national_deaths_total, "national_hospital_cases_current": national_hospital_cases_current}
    return Covid_data
  except:
    logging.warning("covid_API_request failed, check internet connection")


def data_handler(data_list: list,skip_lines_api: int) -> int:
  '''
  Takes data_list (list of dicts recived from Cov19API) and skip_lines_api(lines to skip, found in config)

  Calculates av_last_7days, mean no. of people infected every day over the last 7 days (x days ago, x designated by skip_lines_api in config)

  Returns av_last_7days
  '''
  try:
    working_list = (data_list['data'])[(skip_lines_api): (skip_lines_api + 7)]
    last_7days_list = []
    for element in working_list:
      element = element['newCases']
      last_7days_list.append(int(element))
    av_last_7days = (sum(last_7days_list))/7
    return(av_last_7days)
  except:
      logging.warning("data_handler failed")
      sys.exit()


def covid_data_handler_dead_hospitalized(data_list: list,skip_lines_api: int) -> typing.Tuple[int, int]:
  '''
  Takes data_list (list of dicts recived from Cov19API) and skip_lines_api(lines to skip, found in config)

  Finds and returns national_deaths_total and national_hospital_cases_current from data_list x days ago (x is designated by skip_lines_api in config)
  '''
  try: 
    data_list = data_list["data"]
    national_deaths_total = (data_list[skip_lines_api])["cumDeaths"]
    national_hospital_cases_current = (data_list[skip_lines_api])["hospitalCases"]
    return(national_deaths_total,national_hospital_cases_current)
  except:
    logging.warning("covid_data_handler_dead_hospitalized failed")
    sys.exit()


def schedule_covid_updates(update_interval: int, update_name: str) -> typing.Tuple[sched.Event, sched.Event]:
  '''
  Takes update_interval(time in seconds until next update) and update_name

  Schedules update for get_covid_data which will refresh the covid data stored in temp file temp.json,
  Schedules repeat_covid_update with same time interval as Covid_update,

  Returns Covid_update and repeat_covid, both are id tags for the schedulers
  '''
  try:
    Covid_update = shed.enter(update_interval,1,get_covid_data)
    repeat_covid = shed.enter(update_interval,2,repeat_covid_update,(update_name,"update_Covid",Covid_update))
    return Covid_update,repeat_covid
  except:
    logging.warning("schedule_covid_updates failed")


def repeat_covid_update(update_name: str,id_location: str,update_id: str):
  '''
  Takes update_name (name of the update being repeated or removed), id_location(key for update_id in dict in pending_updates lists) and update_id(id of schedule event taken from schedule_covid_updates).

  Checks if scheduled update should be refreshed, if not then the corrisponding update lable is deleted.

  Returns schedule_covid_updates if the updated is repeated or delete_update otherwise.
  '''
  try:
    for updates in pending_updates:
      if updates[id_location] == update_id:
        if updates["repeat"]:
          schedule_covid_updates(delay(updates["time"]),update_name)
        else:
          delete_update(update_name)
  except:
    logging.warning("repeat_covid_update failed")


def check_Covid_data(Covid_data: dict) -> dict:
  '''
  Takes Covid_data (a dict of covid statistics) 
  
  Checks that the sum of all int elements are greater than zero to confirm data has been fetched from Cov19API

  If passed returns Covid_data, 
  If failed returns covid_API_request with default settings to fetch new data
  '''
  logging.info("check_Covid_data initilized")
  try:
    if sum((Covid_data['local_7day_av'],Covid_data['national_7day_av'],Covid_data["national_deaths_total"],Covid_data["national_hospital_cases_current"])) == 0:
      logging.warning("national data missing, please check location and location type are correct")
      return(covid_API_request())
    else:
        logging.info("check_Covid_data passed")
        return(Covid_data)
  except:
    logging.warning("check_Covid_data failed")
    return(covid_API_request())


def get_covid_data():
  '''
  Fetches Covid_data from covid_API_request given values fetched from config,
  Passes Covid_data through check_Covid_data, if returned then data found,
  Writes Covid_data to temp.json using write_to_temp.
  '''
  try:
    Covid_data = covid_API_request(search_json_file("../config.json","location"), search_json_file("../config.json","location_type"))
    Covid_data = check_Covid_data(Covid_data)
    return write_to_temp(Covid_data,"Covid_data","temp/temp.json","w")
  except:
    logging.warning("get_covid_data failed")


#file search or append
def search_json_file(file_name: str,search_term: str):
  '''
  Takes file_name (name of file to search) and search_term (key term).

  Searches through json files and returns data corresponding to the given key.

  Returns the fetched data.
  '''
  try:
    jason_config = open(file_name)
    jason_data = json.load(jason_config)
    if search_term in jason_data:
      data = jason_data[search_term]
      return(data)
    else:
      logging.warning(f"search_json_file search did not find: {search_term}")
      return (False)
  except:
    logging.warning("search_json_file failed file not available")
    return(False)


def write_to_temp(data:dict,name:str,file:str,open_type:str):
  '''
  takes data (dictionary to write to temp), name (key for dictionary), file (name of temp file) and open_type (open setting).

  Dumps data to temp file under name = key
  '''
  try:
    dic_data =  {name:data}
    item = json.dumps(dic_data, sort_keys=True, indent=4, separators=(',', ': '))
    open(file, open_type).write(item)
  except:
    logging.warning("write_to_temp failed")


#update processing
def pending_updates_append(update_to_append: dict):
  '''
  Takes update_to_append (dict of data from new update)

  Appends update_to_append to pending_updates (global list of dictss)
  '''
  try:
    global pending_updates
    pending_updates.append(update_to_append)
  except:
    logging.warning("pending_updates_append failed")


def delete_update(delete_update_name: str)-> None:
  '''
  Takes delete_update_name (name of update to be deleted).

  Searches for update name in pending_updates (list of all currently pending updates),
  If found the dict relating to the update and any currently active scheduled events associated with the update will be deleted.
  '''
  try:
    global pending_updates
    for updates in pending_updates:
        if delete_update_name == updates["update_note"]["title"]:
            pending_updates.remove(updates)
            try:
              shed.cancel(updates["update_Covid"])
              shed.cancel(updates["repeat_id_covid"])
            except:
              pass
              pass
            try:
              shed.cancel(updates["update_News"])
              shed.cancel(updates["repeat_id_news"])
            except:
              pass
  except:
    logging.warning("delete_update failed")


def hhmm_to_seconds( hhmm: str ) -> int:
  '''
  Takes hhmm (time in format HH:MM).

  Converts hours and minuets to seconds.

  Returns sum of the two.
  '''
  try:
    if len(hhmm.split(':')) != 2:
        print('Incorrect format. Argument must be formatted as HH:MM')
        return None
    return (int(hhmm.split(':')[0])*60*60) + (int(hhmm.split(':')[1])*60)
  except:
    logging.warning("hhmm_to_seconds failed")


def delay(update_time: int) -> int:
  '''
  Takes update_time (time at which the updater should update in HH:MM format).

  Converts update_time to seconds using hhmm_to_seconds, finds current time in seconds and subtracts current time from update time,
  
  Returns delay_time (time in seconds until scheduler should execute instructions)
  '''
  try:
      given_time = hhmm_to_seconds(update_time)
      current_time = (hhmm_to_seconds(datetime.now().strftime("%H:%M"))) + datetime.now().second
      delay_time = given_time - current_time
      if delay_time < -59:
          delay_time = delay_time + (24*60**2)
      return (delay_time)
  except:
    logging.warning("delay failed")
