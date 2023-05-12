# Redis-Teams
A simulation of data flow in an online meeting environment using Redis and mySQL.
<br />
The program was developed and tested on an **Ubuntu 22.04** machine.

### [Contents](#)
1. [**Description**](#descr)
2. [Installing & Configuring requirements locally ](#inst)
3. [Setup](#setup)
4. [Running the functions](#run)
5. [Results](#results)
6. [Notes](#notes)

### [**Description**](#) <a name="descr"></a>

This project simulates how data could be stored and retrieved from Redis in an online meeting environment (ex. Zoom , Ms Teams) from the use of 9 specific functions. The data are initially loaded from a local mySQL server and then cached into Redis to make adjustments.

**Assumptions** <br/>
We assume that the input for each function , that is critical in order to run properly is provided by a front-end when the user makes an action that triggers that specific function. 

### [**Installing & Configuring Requirements**](#) <a name="inst"></a>
### Ubuntu
1.Clone the repo
``` shell
$ git clone https://github.com/TeoSkondras/Redis-Teams.git
```
2.Install mysql server and make sure the process is running
``` shell
$ sudo apt update
$ sudo apt-get install mysql-server
$ systemctl is-active mysql
```
3.Install Redis and run locally 
``` shell
$ curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

$ echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

$ sudo apt-get update
$ sudo apt-get install redis
$ redis-cli
```
or using snap:
``` shell
$ sudo snap install redis
```

### [**Setup**](#) <a name="setup"></a>

### Before you start
You need to create the schema shown below with the test data and start the scheduler.
<img src="https://github.com/TeoSkondras/Redis-Teams/blob/main/images/schema.png" height="370"/>

1.Create schema and add test data
In the terminal connect to the mysql local instance and enter your password
``` shell
$ mysql -uroot -p
```
Once inside, use the source or \. command followed by the absolute path to the SQL file ```queries.sql``` from the repo as shown below:
``` shell
$ mysql> source <your-path-here>/queries.sql
```
This should create the tables and add the data.
Alternatively you can use a GUI such as a [mySql Workbench](https://linuxhint.com/installing_mysql_workbench_ubuntu/) and excecute the queries here.

2.Start the sceduler to activate and deactivate meetings every 1 minute.
To do this we will use a cronjob.
<br/>
Edit the cronjobs file
``` shell
$ crontab -e
```
And at the last line copy and paste
``` shell
$ * * * * * <Path-To-Python> <Path-To-scheduler.py>
```
Example:
``` shell
$ * * * * *  /usr/bin/python3 /home/user/Projects/Redis-Teams/scheduler.py
```

### [**Running the functions**](#) <a name="run"></a>
Navigate to the project and run the functions.py file
All functions run sequentually for demo purposes. Feel free to test them yourself.
``` shell
$ cd Redis-Teams
$ python functions.py
```
A brief overview of what each function implements.
* Function: a user joins an active meeting instance – if it is public, always, otherwise only if s/he
is allowed, i.e. his email is in audience (eventsLog is updated)
* Function: a user leaves a meeting that has joined (eventsLog is updated)
* Function: show meeting’s current participants
* Function: show active meetings
* Function: when a meeting ends, all participants must leave (eventsLog is updated)
* Function: a user posts a chat message
* Function: show meeting’s chat messages in chronological order
* Function: show for each active meeting when (timestamp) current participants joined
* Function: show for an active meeting and a user his/her chat messages

### [**Results**](#) <a name="results"></a>
After running the output should be something like this
<br/>
**Note that since meetings are activated and deactivated all the time your output might differ.**
<img src="https://github.com/TeoSkondras/Redis-Teams/blob/main/images/output.png" height="750"/>
<br/>
To test the scheduler is working you can try
``` shell
$ python scheduler.py
```
<br/>
And get an output similar to this.
<img src="https://github.com/TeoSkondras/Redis-Teams/blob/main/images/output_scheduler.png" height="400"/>


### [**Notes**](#) <a name="notes"></a>
This project was made as an assignement of the Big Data Management Systems course at DMST AUEB.
<br />
<br />
***Team members***
<br />
Nikolaos Katsios 8200071
<br />
Theodoros Skondras Mexis 8200156

