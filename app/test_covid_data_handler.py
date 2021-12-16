from covid_data_handler import parse_csv_data, process_covid_csv_data,covid_API_request, schedule_covid_updates
import pytest
import sched

def test_parse_csv_data():
    data = parse_csv_data('nation_2021-10-28.csv' )
    assert len(data) == 639

def test_process_covid_csv_data():
    last7days_cases , current_hospital_cases , total_deaths = process_covid_csv_data(parse_csv_data('nation_2021-10-28.csv'))
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)
    assert data['location'] == 'Exeter'
    assert data['national_deaths_total'] > 0


def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name='update test')
    Covid_update,repeat_covid = schedule_covid_updates(3,"name")
    assert type(Covid_update) == sched.Event
    assert type(repeat_covid) == sched.Event
    assert "priority=1" in str(Covid_update)
    assert "priority=2" in str(repeat_covid)
