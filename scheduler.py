import mysql.connector
import datetime
import redis


# Init connections with db and redis
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='MYPASS', # Replace with mysql password
    auth_plugin='mysql_native_password',
    database="users_meetings"
)

# Get a redis connection
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Get the cursor
cursor = db.cursor()

# Function to check if current time is inbetween meeting times
def isNowInTimePeriod(startTime, endTime, nowTime):
    if startTime < endTime: 
        return nowTime >= startTime and nowTime <= endTime 
    else: 
        #Over midnight: 
        return nowTime >= startTime or nowTime <= endTime 

# Proactively delete all previous active instances   
r.delete("active_meetings")

# Get current time as a datetime object to be compatible with mysql data
now = datetime.datetime.now()
print("Now: " + str(now))


# Get all the info for the meeting instances
SQL = "SELECT * FROM meeting_instances"
cursor.execute(SQL)

# For every meeting ckeck if it is active
for meeting in cursor:
    meetind_id = meeting[0]
    order_id = meeting[1]
    start_time = meeting[2]
    end_time = meeting[3] 
    if isNowInTimePeriod(start_time, end_time, now):
        print("Active: " + str(start_time) + " " + str(end_time))
        # and put the: meeting_ID , orderID in the active meetings list in redis
        r.lpush("active_meetings" , str(meetind_id) + " " + str(order_id) )
    else:
        print("Inactive: " + str(meetind_id) + " " + str(order_id))


print("Active instances in redis: " + str(r.lrange("active_meetings" , 0 , 3 )))


