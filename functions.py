from enum import Enum
import mysql.connector
import datetime
import redis

# Init connections with dbs and redis
db_users_meetings = mysql.connector.connect(
    host='127.0.0.1',
    user='localhostusername',
    password='password',
    database="users_meetings"
)

db_events_log = mysql.connector.connect(
    host='127.0.0.1',
    user='localhostusername',
    password='password',
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

# updates the events_log table to emit a new event
def update_events_log(event_id, user_id, event_type, timestamp):
    SQL = "INSERT INTO events_log (event_id, userID, event_type, timestamp) VALUES ({event_id}, {userID}, {event_type}, NOW())".format(
        event_id=event_id, userID=user_id , event_type=event_type , timestamp=timestamp
    )
    cursor_events_log.execute(SQL)
    db_events_log.commit()

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
                        
# checks if a user has already joined a meeting
def is_user_already_in_the_meeting_instance(user_id, meeting_id, order_id):
    key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":participants"
    meeting_participants_ids = r.lrange(key , 0 , -1 )
    if str(user_id) in meeting_participants_ids:
        return True

# initializes the eventId in redis in order to use it for the events_log db inserts
def initialize_event_id():
    r.set('currentEventID',0)

# --------- 1: A user joins an active meeting instance ---------
# KEY: "meetingId:int:orderID:int:participants" VALUE: [userId1 , userId2 , ... ]
def join_meeting(user_id, meeting_id, order_id):
    # check if the meeting instance the user tries to join is active
    # construct the string to look up
    meeting_instance_id = str(meeting_id) + " " + str(order_id)
    event_id = int(r.get('currentEventID'))
    # get a list of active meeting instaces from redis
    active_meetings_from_scheduler = r.lrange("active_meetings" , 0 , -1 )
    if meeting_instance_id in active_meetings_from_scheduler:
        print("Meeting:" + str(meeting_id) + " " + str(order_id) + " Active. Trying to join....")
        # check if the user is allowed to join the meeting
        if is_user_allowed_to_join_meeting(user_id , meeting_id):
            if not is_user_already_in_the_meeting_instance(user_id, meeting_id, order_id): #we suppose a user cannot join a meeting they are already in
                # add user to the participants list of the meeting
                key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":participants"
                value = str(user_id)
                # print(key + " " + value)
                # each newly joined user goes to the right (end) of the list
                r.rpush(key , value)
                join_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # print("User: " +  str(user_id) + " joined meeting instance: " + str(meeting_instance_id) + "at:" + join_timestamp)
                # Emit join to events_log
                event_id +=1
                r.set('currentEventID',event_id)
                update_events_log(event_id , user_id , Event_types.JOIN.value , join_timestamp)
                print(r.lrange(key , 0 , -1 ))
                print()
                # store the user join timestamp to the active meeting's participants' list
                key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":userId:" + str(user_id) + ":joinTimestamp"
                value = join_timestamp
                # print(key + " " + value)
                r.set(key, value)
            else:
                print("User: " +  str(user_id) + " has already joined the meeting: " + str(meeting_id) + "\n")
        else:
            print("User: " +  str(user_id) + " not allowed to join meeting: " + str(meeting_id) + "\n" )
    else:
        print("The meeting the user is trying to join is inactive , please try again" + "\n")


# --------- 2: A user leaves a meeting instance ---------
def leave_meeting(user_id, meeting_id, order_id):
    print("Retriving key...")
    # retrive the key to check for active meeting participants
    meeting_instance_id = str(meeting_id) + " " + str(order_id)
    key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":participants"
    meeting_participants = r.lrange(key , 0 , -1 )
    event_id = int(r.get('currentEventID'))
    # if the user is in the participants list remove him
    if str(user_id) in meeting_participants:
        # remove the user from the participants list
        r.lrem(key , 0 , user_id)
        # remove the key-value pair containing the join timestamp of the user for the meeting
        key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":userId:" + str(user_id) + ":joinTimestamp"
        r.delete(key)
        # update events_log
        event_id += 1
        r.set('currentEventID',event_id)
        update_events_log(event_id , user_id , Event_types.LEAVE.value , datetime.datetime.now())
        print("User: " +  str(user_id) + " left meeting instance: " + str(meeting_instance_id) + "\n")
    else:
        print("Error: User cannot leave a meeting he has not joined" + "\n")

# --------- 3: Show meeting’s current participants ---------
def show_meeting_participants(meeting_id , order_id):
    print("Loading meeting: " + str(meeting_id) + " " + str(order_id) + " participants....")
    key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":participants"
    meeting_participants_ids = r.lrange(key , 0 , -1 )
    print(meeting_participants_ids)
    print()
    return meeting_participants_ids

# --------- 4: Show active meetings ---------
def show_active_meetings():
    print("Loading active meetings....")
    active_meetings_from_scheduler = r.lrange("active_meetings" , 0 , -1 )
    print("Active meetings in redis: " + str(active_meetings_from_scheduler) + "\n")

# --------- 5: When a meeting ends, all participants must leave  ---------
def empty_participants_from_finished_meeting(meeting_id , order_id):
    key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":participants"
    meeting_participants_ids = r.lrange(key , 0 , -1 )
    event_id = int(r.get('currentEventID'))
    print("Removing meeting's participants....\n")
    for user_id in meeting_participants_ids:
        event_id += 1
        r.set('currentEventID',event_id)
        update_events_log(event_id , int(user_id) , Event_types.TIMEOUT.value , datetime.datetime.now())
    r.delete(key)

# --------- 6: A user posts a chat message ---------
# Hypothesis: suppose that a comment belongs to a meeting instance, not a meeting in general
def post_message(user_id, meeting_id, order_id, message): 
    #first check if the user is eligible to post a chat message
    if is_user_allowed_to_join_meeting(user_id,meeting_id):
        meeting_instance_id = str(meeting_id) + " " + str(order_id)
        # first put the message on the meeting's chat list 
        key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":messages"
        value = str(message)
        #print(key+" "+value)
        r.rpush(key , value)
        # then put the message on the user's meetings' chat list
        key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":userID:" + str(user_id) + ":messages"
        value = str(message)
        r.rpush(key , value)
        print("User: " +  str(user_id) + " just commented on the meeting instance: " + str(meeting_instance_id) + ": " + str(message) + "\n")
    else:
        print("User: " +  str(user_id) + " does not have the right to comment in meeting: " + str(meeting_id) + "\n")

# --------- 7: Show meeting’s chat messages in chronological order (the oldest comes first) ---------
def show_meeting_messages_chronologically(meeting_id, order_id):
    print("Fetching meeting's messages....")
    key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":messages"
    # because the chat messages are inserted with rpush, the earliest one will apear first, the latest one will be in the end...
    meeting_chat_messages = r.lrange(key , 0, -1 )
    print(meeting_chat_messages)
    print()

# --------- 8: Show for each active meeting when (timestamp) current participants joined ---------
# Hypothesis: suppose that the timestamp is held for the meeting instance, not for the meeting as a whole.
def show_all_meetings_current_users_join_timestamp():
    # get all the active meetings
    active_meetings_from_scheduler = r.lrange("active_meetings" , 0 , -1 )
    for meeting_instance_id in active_meetings_from_scheduler:
        print("Fetching current users' join timestamps for the meeting instance: " + meeting_instance_id + "....")
        meeting_instance_details = meeting_instance_id.split(" ")
        meeting_participants = show_meeting_participants(meeting_instance_details[0],meeting_instance_details[1])
        key = "meetingId:" + meeting_instance_details[0] + ":orderId:" + meeting_instance_details[1]
        for i in range(len(meeting_participants)):
            key = "meetingId:" + meeting_instance_details[0] + ":orderId:" + meeting_instance_details[1] + ":userId:" + str(meeting_participants[i]) + ":joinTimestamp"
            user_join_timestamp = r.get(key)
            print("User:" + meeting_participants[i] + " joined the meeting instance:" + meeting_instance_id + " at:" + user_join_timestamp)
    print("\n")        


# --------- 9: Show for an active meeting and a user his/her chat messages ---------
def show_active_meeting_messages_of_user(user_id ,meeting_id, order_id):
    print("Trying to fetch meeting's user messages...")
    active_meetings_from_scheduler = r.lrange("active_meetings" , 0 , -1 )
    meeting_instance_id = str(meeting_id) + " " + str(order_id)
    if meeting_instance_id in active_meetings_from_scheduler:
        key = "meetingId:" + str(meeting_id) + ":orderId:" + str(order_id) + ":userID:" + str(user_id) + ":messages"
        meeting_user_chat_messages = r.lrange(key , 0, -1 )
        if len(meeting_user_chat_messages)==0:
            print("The user:" + str(user_id) + " has not left any comments in the meeting:  " + meeting_instance_id + " ..." + "\n")
        else:    
            print(meeting_user_chat_messages)
            print()
    else:
        print("Meeting Is not active!" + str(active_meetings_from_scheduler) + "\n")


# -------TEST MAIN FUNCTIONS -------
# Note1: The commented out commands are there to use them in case you want to run the script multiple times, in order to clean up previous actions!
# Note2: Please use the initialize_event_id() function ONCE! Otherwise it will try to insert duplicate eventIds causing Primary key constrain breaks

initialize_event_id()
#r.delete("meetingId:1:orderId:1:currentUsersJoinTimeStamps")

show_active_meetings()

meeting_participants = show_meeting_participants(1,1)
meeting_participants = show_meeting_participants(1,2)

join_meeting(user_id=1 , meeting_id=1 , order_id=1)
join_meeting(user_id=2 , meeting_id=1 , order_id=1)
join_meeting(user_id=3 , meeting_id=1 , order_id=1)
leave_meeting(user_id=1 , meeting_id=1 , order_id=1)
meeting_participants = show_meeting_participants(1,1)

#r.delete("meetingId:1:orderId:1:messages")
#r.delete("meetingId:1:orderId:1:userID:2:messages")
#r.delete("meetingId:1:orderId:1:userID:3:messages")

post_message(2,1,1,"hello redis")
post_message(3,1,1,"goodbye redis")
show_meeting_messages_chronologically(1,1)
show_active_meeting_messages_of_user(2,1,1)
show_active_meeting_messages_of_user(1,10,1)

show_all_meetings_current_users_join_timestamp()

empty_participants_from_finished_meeting(1,1)
