# Report Builder 3
## A Python web interface for creating client facing reports for LinkedIn and GoogleAds Campaigns

## Contents
* [Introduction](#introduction)
* [Dependencies and Technology](#dependencies)
* [Video Demo of the Report Builder in Action](#viddemo)
* [How it works](#howitworks)

## Introduction<a name="Introduction"></a>
This project is a demo of an app I built to help my marketing consultancy streamline reporting of their LinkedIn Organic, LinkedIn Sponsored and Google Ads advertising campaigns. It is, in roughly equal parts; a useful tool, a demo of my skills and a platform I used to explore technologies such as Docker, Docker Compose and matplotlib with which I had limited experience. For this reason there are places in which the project could be approached more simply but would have provided fewer learning experiences. 

As this is a tool that was also built to provide proprietary reports for clients of an active marketing agency, all the references to that agency and their clients have been stripped out along with connection details to the Linkedin and Google Ads advertising APIs. For this reason, if you wish to get this working in your own right, you will need access to both these APIs (details in the [dependencies](#dependencies) section) and some deliberately omited config files. Please feel free to reach out to me if you would like to get this working for yourself and I will do my best to help you.


## Dependencies and Technology<a name="dependencies"></a>
* [LinkedIn Advertisers API](https://docs.microsoft.com/en-us/linkedin/)
* [Google Ads API](https://developers.google.com/google-ads/api/docs/start?hl=en_US)
* [MySQL](https://hub.docker.com/_/mysql)
* [Docker](https://www.docker.com/)
* [Docker Compose](https://docs.docker.com/compose/)
* [CRON](https://help.ubuntu.com/community/CronHowto)
* [google-ads 13.0.0](https://pypi.org/project/google-ads/12.0.0/)
* [mysql-connector-python 8.0.25](https://pypi.org/project/mysql-connector-python/8.0.25/)
* [requests 2.25.1](https://pypi.org/project/requests/2.25.1/)
* [pyyaml 5.4.1](https://pypi.org/project/PyYAML/5.4.1/)
* [flask 2.0.1](https://pypi.org/project/Flask/2.0.1)
* [flask_httpauth 4.4.0](https://pypi.org/project/Flask-HTTPAuth/4.4.0)
* [pyAesCrypt 6.0.0](https://pypi.org/project/pyAesCrypt/6.0.0)
* [gunicorn 20.1.0](https://pypi.org/project/gunicorn/20.1.0)
* [matplotlib 3.4.3](https://pypi.org/project/matplotlib/3.4.3)
* [grpcio 1.38.1](https://pypi.org/project/grpcio/1.38.1)

## Video Demo of the Report Builder in Action<a name="viddemo"></a>
[LINK TO THE VIDEO](link)

## How it works <a name="howitworks"></a>
The main docker-compose.yaml file spins up 4 Docker containers and a shared volume for managing the 4 major aspects of the app; the frontend, the calls to the api, the database itself and a config server. 

#### Frontend
The frontend container is a Flask server that serves a dynamic output webpage with advertising stats that come from the database, allows the users (typically an account manager for a marketing agency or consultancy) to upload images and enter their own text input and finally export all this to a PDF that can be delivered to the client. 

#### API-Call
The API-call container queries the LinkedIn Advertiser API and the Google Ads API for a selection of commonly used stats for evaluating the performance of online marketing campaigns at midnight every night (thanks to CRONJOBS.) This data is then saved to the MySQL database in the Database container.

#### Database
This container creates and maintains the MySQL database that contains all the data obtained from the LinkedIn and Google Ads APIs.

#### Config
Probably the most superfluous container, Config contains a lot of the functionality for creating and updating the settings for the output in Frontend as well as the settings for obtaining the correct data from API-Call. This is where all the security sensitive information such as access tokens, encryption/decryption technology is stored. Originally, this container and it's docker network was concieved as a way to digitally separate the frontend from the more sensitive API access tokens and the API-Call container. Ultimately this didn't succeed in the way that I was hoping (yet) but allowed me to think a bit more deeply about security in Dev Ops on web apps.






