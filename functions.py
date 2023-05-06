from enum import Enum
import mysql.connector
import datetime
import redis

# Init connections with dbs and redis
db_users_meetings = mysql.connector.connect(
    host='localhost',
    user='root',
    password='mypass', # Replace with mysql password
    auth_plugin='mysql_native_password',
    database="users_meetings"
)

db_events_log = mysql.connector.connect(
    host='localhost',
    user='root',
    password='9k"eAf|8', # Replace with mysql password
    auth_plugin='mysql_native_password',
    database="events_log"
)

# Get a redis connection
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Get the cursors for the dbs
cursor_users_meetings = db_users_meetings.cursor()
cursor_events_log = db_events_log.cursor()

# -------DATA INIT -------

users_db = []
meetings_db = []
meeting_instances_db = []
events_log_db = []

# gets the meetings table from db and fills out the meetings_db list
def get_meetings_db_data():
    cursor_users_meetings.execute("SELECT * FROM meetings")
    for row in cursor_users_meetings:
        meetings_db.append(row)

# gets the user table from db and fills out the users_db list
def get_users_db_data():
    cursor_users_meetings.execute("SELECT * FROM users")
    for row in cursor_users_meetings:
        users_db.append(row)

# gets the user table from db and fills out the users_db list
def get_meeting_instances_db_db_data():
    cursor_users_meetings.execute("SELECT * FROM meeting_instances")
    for row in cursor_users_meetings:
        meeting_instances_db.append(row)

get_users_db_data()
get_meetings_db_data()


# -------EVENTS LOG UTILS -------

# event_type can be 1 (join_meeting), 2 (leave_meeting), 3 (timeout) 
class Event_types(Enum):
    JOIN = 1
    LEAVE = 2
    TIMEOUT = 3

# init unique event id to be incremented when updating events log
event_id = 0

# updates the events_log table to emit a new event
def update_events_log(event_id, user_id, event_type, timestamp):
    SQL = "INSERT INTO events_log (event_id, userID, event_type, timestamp) VALUES ({event_id}, {userID}, {event_type}, {timestamp})".format(
        event_id=event_id, userId=user_id , event_type=event_type , timestamp=timestamp
    )
    cursor_events_log.execute(SQL)

# -------REDIS UTILS-------

# deletes everything and resets redis data
def purge_redis_data():
    r.flushall()


# -------MAIN FUNCTIONS -------

# checks if a user is eligable to join a meeting
def is_user_allowed_to_join_meeting(user_id , meeting_id):
    # search for the correct meeting
    for meeting in meetings_db:
        if meeting[0] == meeting_id:
            # if public (audience = '') anyone can join so return true
            if meeting[4] == '':
                return True
            else:
                # else check if the users email is contained in the audience comma separated string
                for user in users_db:
                    if user[0] == user_id:
                        email = user[4]
                        meeting_email_list = meeting[4].split(",")
                        if email in meeting_email_list:
                            return True
                        else:
                            return False 

# --------- 1: A user joins an active meeting instance ---------
# KEY: "meetingId:int:orderID:int:participants" VALUE: [userId1 , userId2 , ... ]
def join_meeting(user_id, meeting_id, order_id):
    # check if the meeting instance the user tries to join is active
    # construct the string to look up
    meeting_instance_id = str(meeting_id) + " " + str(order_id)
    # get a list of active meeting instaces from redis
    active_meetings_from_scheduler = r.lrange("active_meetings" , 0 , -1 )
    if meeting_instance_id in active_meetings_from_scheduler:
        print("Meeting Active. Trying to join....")
        # check if the user is allowed to join the meeting
        if is_user_allowed_to_join_meeting(user_id , meeting_id):
            key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":participants"
            value = str(user_id)
            print(key + " " + value)
            r.lpush(key , value)
            print("User: " +  str(user_id) + " joined meeting instance: " + str(meeting_instance_id) )
            # Emit join to events_log
            event_id += 1
            update_events_log(event_id , user_id , Event_types.JOIN.value , datetime.datetime.now())
        else:
            print("User: " +  str(user_id) + " not allowed to join meeting: " + str(meeting_id) )
    else:
        print("The meeting the user is trying to join is inactive , please try again")


# --------- 2: A user leaves a meeting instance ---------
def leave_meeting(user_id, meeting_id, order_id):
    print("Retriving key...")
    # retrive the key to check for active meeting participants
    meeting_instance_id = str(meeting_id) + " " + str(order_id)
    key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":participants"
    meeting_participants = r.lrange(key , 0 , -1 )
    # if the user is in the participants list remove him
    if user_id in meeting_participants:
        r.lrem(key , 0 , user_id)
        event_id += 1
        # update events_log
        update_events_log(event_id , user_id , Event_types.LEAVE.value , datetime.datetime.now())
        print("User: " +  str(user_id) + " left meeting instance: " + str(meeting_instance_id) )
    else:
        print("Error: User cannot leave a meeting he has not joined")

# --------- 3: Show meeting’s current participants ---------
def show_meeting_participants(meeting_id , order_id):
    key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":participants"
    meeting_participants_ids = r.lrange(key , 0 , -1 )
    print(meeting_participants_ids)

# --------- 4: Show active meetings ---------
def show_active_meetings():
    active_meetings_from_scheduler = r.lrange("active_meetings" , 0 , -1 )
    print("Active meetings in redis: " + str(active_meetings_from_scheduler))

# --------- 5: When a meeting ends, all participants must leave  ---------
def empty_participants_from_finished_meeting(meeting_id , order_id):
    key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":participants"
    meeting_participants_ids = r.lrange(key , 0 , -1 )
    for user_id in meeting_participants_ids:
        event_id += 1
        update_events_log(event_id , int(user_id) , Event_types.TIMEOUT.value , datetime.datetime.now())
    r.delete(key)



# -------TEST MAIN FUNCTIONS -------
show_active_meetings()
join_meeting(user_id=1 , meeting_id=1 , order_id=4)