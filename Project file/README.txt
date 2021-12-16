To start covid_web_app:
	insert your newsapi.org key in the api_key slot found in the config file

	must be connceted to the internet
	flask must be installed (pip install flask)
	newsapi must be installed (pip install newsapi-python)
	public health england api must be installed(pip install uk-covid19)

	run web_app in the app folder


To start csv_read application:
	run csv_reader in the app folder


Config_data:
	Can be used to edit how both csv_read and covid_web_app interpret data.
	Values dictate which row the variables data should be read from for CSV read, 
	this can be usful if someone wanted to edit the source code to add, change or remove variables.

	Can also change local and national location for covid web app, as well as news domains to search, 
	number of articles to be listed on web app, max age of articles and how recent covid data can be (skip_lines_api, 
	number of days skipped from api).

Testing:
	Must have pytest installed (pip install -U pytest)
	To run:
		open terminal in Project file location and enter: pytest
	
