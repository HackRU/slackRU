letsmake_man = """
Letsmake - The Projects Board
@letsmake -pn [project-name] -pd [project-description] -sh [skills-possessed] -sw [skills-wanted] -sz [team-size]
    Posts a request for a team

@letsmake list-projects
    Lists all open projects

    -a List all projects including those not open
    -m List all projects posted by current user
    -q List all projects that match query (au:[author-name], tu:[posted x hrs prior] pn:[project name contains these words]
        sh:[poster has these skills] sw:[poster wants these skills] sl:[Find projects seeking x or fewer people]
        sg:[find projects seeking x or more people] -s (a|t|u|o)i Sorts list of projects alphabetically (a), timestamp (t), username (u), open status (o), invert order (i)

@letsmake status ([project-id]|all) [status]
    Change project status
    all - applies status change to all projects
    STATUSES
    open - Project needs more hands (0)
    fulfilled - Project has enough hands (1)
    noneed - Decision to not proceed with project (2)

NOTE: When entering skills, do not use spaces. If you need to, use underscores (e.g. Python3 OR Python_3)
"""

from slackclient import SlackClient
from enum import Enum
import random as rnd
import config
import time
import sqlite3
import re
from modules.tools import tools 

slack_client = SlackClient(config.apiT)
slack_web_client = SlackClient(config.oauthT)
BOTID = config.botID
BOTNAME = "U7ET9GFD1"
CHANNEL = "#general"
AT_BOT = "<@" + BOTNAME + ">"

SQL_CONN = sqlite3.connect('projects.db')
PROJECT_PRIMARY_KEY_SIZE = 5
PROJECT_TABLE_NAME = "projects"

class Message:
    def __init__(self, botname='', userid='', username='', text='', timestamp='', _type=''):
        self.botname = botname
        self.userid = userid
        self.username = username
        self.text = text
        self.timestamp = timestamp
        self.type = _type

class Project:
    def __init__(self, pid='', pn='', pd='', sh=[], sw=[], sz=3, author='', authorid='',
                        timestamp=int(round(time.time() * 1000)), status=0):
        self.id = pid
        self.project_name = pn
        self.project_desc = pd
        self.skills_have = sh
        self.skills_wanted = sw
        self.team_size = sz
        self.author = author
        self.authorid = authorid
        self.timestamp = timestamp
        self.status = status

#######################################################################################
#######################################################################################
#######################################################################################
                                # DATABASE #
#######################################################################################
#######################################################################################
#######################################################################################

KEYS = [key for key in Project().__dict__]
def execute(query):
    conn = SQL_CONN.cursor()
    conn.execute(query)
    SQL_CONN.commit()
    return conn

def gather(data):
    tuples = []
    for datum in data:
        tuples.append(dict([(x, y) for x, y in zip(KEYS, datum)]))
    return tuples

def create_tables():
    # creating users table
    table_create = 'CREATE TABLE IF NOT EXISTS users('
    fields = {
        'id': 'CHAR(9)',
        'username': 'VARCHAR(100)'
    }
    table_create += ','.join(['%s %s' % (k, t) for k, t in fields.items()]) + ',PRIMARY KEY (id));'
    print("CREATING TABLE users")
    execute(table_create)
    
    # creating projects table
    table_create = "CREATE TABLE IF NOT EXISTS projects("
    fields = {
        'id': 'CHAR(5)',
        'project_name': 'VARCHAR(500)',
        'project_desc': 'VARCHAR(3000)',
        'authorid': 'CHAR(9) NOT NULL',
        'author': 'VARCHAR(300)',
        'skills_have': 'VARCHAR(1000)',
        'skills_wanted': 'VARCHAR(1000)',
        'team_size': 'INTEGER',
        'timestamp': 'FLOAT',
        'status': 'INTEGER'
    }
    table_create += ','.join(['%s %s' % (k, t) for k, t in fields.items()]) + ',PRIMARY KEY (id), FOREIGN KEY (authorid) REFERENCES users(id));'
    print("CREATING TABLE projects")
    execute(table_create)

#### DATABASE QUERY ####
def query_projects(queries, keys=['*']):
    conn = SQL_CONN.cursor()
    query_params = []
    for k,v in queries.items():
        key = k
        select_type, select_query = v
        select = '='
        if select_type == SQL.IS:
            select = 'IS'
        elif select_type == SQL.LIKE:
            select = 'LIKE'
        elif select_type == SQL.BETWEEN:
            select = 'BETWEEN'
            select_query = '%d AND %d' % (select_query[0], select_query[1])
        query_params.append('%s %s "%s"' % (key, select, select_query))
    query_str = ' AND '.join(query_params)
    keys = ','.join(KEYS)
    sql_query = 'SELECT %s FROM %s WHERE %s' % (keys, PROJECT_TABLE_NAME, query_str)
    conn.execute(sql_query)
    SQL_CONN.commit()
    return gather(conn.fetchall())
    
def get_all_projects():
    conn = execute('SELECT %s FROM %s' % (','.join(KEYS), PROJECT_TABLE_NAME))
    return gather(conn.fetchall())

def get_project_by_id(proj_id):
    return query_projects({'id': (SQL.EQL, proj_id)})

def get_project_by_name(proj_name):
    return query_projects({'project_name': (SQL.EQL, proj_name)})

def get_project_by_user(username):
    return query_projects({'author': (SQL.EQL, username)})

def get_project_by_needed_skill(skills):
    skill_str = '%%' + '%%'.join(skills) + '%%'
    return query_projects({'skills_wanted': (SQL.LIKE, skill_str)})

def get_project_by_skill(skills):
    skill_str = '%%' + '%%'.join(skills) + '%%'
    return query_projects({'skills_have': (SQL.LIKE, skill_str)})

def get_project_from_timerange(stime, etime):
    return query_projects({'timestamp': (SQL.BETWEEN, (stime, etime))})

def insert_project(proj):
    keys, values = [], []
    for k,v in proj.__dict__.items():
        if not v:
            continue
        keys.append(k)
        if isinstance(v, str):
            values.append('"%s"' % v)
        else:
            values.append(str(v))
    keys_str = ', '.join(keys)
    values_str = ', '.join(values)
    sql_insert = 'INSERT INTO %s (%s) VALUES (%s)' % (PROJECT_TABLE_NAME, keys_str, values_str)
    execute(sql_insert)

def generate_project_id():
    while True:
        _id = ''.join([chr(ord('a') + rnd.randint(0, 25)) for x in range(PROJECT_PRIMARY_KEY_SIZE)])
        if not get_project_by_id(_id):
            return _id

def search_userid_or_update(uid):
    data = execute('SELECT username FROM users WHERE id = "%s"' % uid).fetchone()
    if not data:
        members = slack_client.api_call('users.list')['members']
        members_list = []
        for member in members:
            members_list.append((member['id'], member['name']))
            if member['id'] == uid:
                data = member['name']
        conn = SQL_CONN.cursor()
        conn.executemany("INSERT OR REPLACE INTO users (id, username) VALUES (?, ?);", members_list)
        SQL_CONN.commit()
    return data if isinstance(data, str) else data[0]

#######################################################################################
#######################################################################################
#######################################################################################
                                    # SLACK #
#######################################################################################
#######################################################################################
#######################################################################################

MESSAGE_TYPE = 'message'

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    messages = []
    output_list = filter(lambda out: 'type' in out and out['type'] == MESSAGE_TYPE and AT_BOT in out['text'],
                         slack_rtm_output)
    for out in output_list:
        userid = out['user']
        username = search_userid_or_update(userid)
        text = out['text']
        timestamp = out['ts']
        _type = out['type']
        messages.append(Message(BOTNAME, userid, username, text, timestamp, _type))
    return messages

class SQL(Enum):
    EQL = 0
    IS = 1
    LIKE = 2
    BETWEEN = 3

def send_message(msg, user):
    slack_client.api_call(
        "chat.postEphemeral",
        channel=CHANNEL,
        text=msg,
        user=user)

def send_projects_to_user(projects, user):
    for project in projects:
        data = '''\t----------------------------------------------------------------------------------------
        Project Name: %s
        Project Description: %s
        Project Submitter: %s
        Seeking Team Size: %d
        Skills Needed: %s
        Skills Team Has: %s
        -----------------------------------------------------------------------------------
        ''' % ( project['project_name'], project['project_desc'], project['project_desc'],
                project['team_size'], project['skills_wanted'].replace('|', ', ') if project['skills_wanted'] else '',
                project['skills_have'].replace('|', ', ') if project['skills_have'] else '' )
        send_message(data, user)

#######################################################################################
#######################################################################################
#######################################################################################
                            # COMMAND PROCESSING #
#######################################################################################
#######################################################################################
#######################################################################################

# Processes the post into proper format so it can be inserted into SQLite3
def process_posting(msg):
    posting = [w.strip() for w in re.split('\s+', msg.text)][1:] # eliminates that @ reference
    project = Project()
    info = {}
    curr_key = None
    arg_pattern = re.compile('^-[a-z]{2}$')
    # iterates over text, and if it encounters arg_pattern, updates curr_key and append all text to that kv-pair
    # in info
    for w in posting:
        if arg_pattern.match(w):
            arg = w[1:]
            if not curr_key or arg != curr_key:
                curr_key = arg
            if curr_key not in info:
                info[curr_key] = []
        elif curr_key != None:
            info[curr_key].append(w)
    # refining data
    if 'sh' in info:
        info['sh'] = [w.strip() for w in tools.flatten([re.split(',|;', skill.strip()) for skill in info['sh']]) if w]
    if 'sw' in info:
        info['sw'] = [w.strip() for w in tools.flatten([re.split(',|;', skill.strip()) for skill in info['sw']]) if w]
    # if key is in dictionary, return dictionary[key], else return default value
    if_in_else = lambda k, d, dv: d[k] if k in d else dv # k: key, d: dictionary, dv: default value
    # inflating project
    if 'pn' not in info:
        return (400, 'Please specify a project name. Use @letsmake help to see usage.')
    if 'pd' not in info:
        return (400, 'Please specify a project description. Use @letsmake help to see usage.')
    project.project_name = ' '.join(info['pn']) if 'pn' in info else project.project_name
    project.project_desc = ' '.join(info['pd']).lower() if 'pd' in info else project.project_desc
    project.skills_have = '|'.join(info['sh']).lower() if 'sh' in info else None
    project.skills_wanted = '|'.join(info['sw']).lower() if 'sw' in info else None
    project.team_size = int(info['sz'][0]) if 'sz' in info else 3
    project.id = generate_project_id()
    project.authorid = msg.userid
    project.author = msg.username
    insert_project(project)
    return (200, 'Project submission successful!')

# Lists projects according to user specification
def list_projects(msg):
    posting = [w.strip() for w in re.split('\s+', msg.text)][2:] # elimintes '@letsmake list-projects' string
    arg_pattern = re.compile('^-(a|m|q|s)$')
    info = {}
    criteria = []
    curr_key = None
    for w in posting:
        if arg_pattern.match(w):    
            arg = w[1]
            if not curr_key or arg != curr_key:
                curr_key = arg
            if curr_key not in info:
                info[curr_key] = []
        elif curr_key != None:
            info[curr_key].append(w)
    # RESULT ORDERING
    ordering = None
    invert_order = 'ASC'
    if not 'a' in info:
        criteria.append('status = 0')
    if 'm' in info:
        criteria.append('authorid = "%s"' % msg.userid)
    if 's' in info:
        order_type = info['s'][0][0]
        if order_type == 'o':
            ordering = 'status'
        elif order_type == 'u':
            ordering = 'author'
        elif order_type == 't':
            ordering = 'timestamp'
        elif order_type == 'a':
            ordering = 'project_name'
        if len(info['s'][0]) == 2 and info['s'][0][1] == 'i':
            invert_order = 'DESC'
    if 'q' in info:
        qs = info['q']
        search_keys = {}
        curr_key = None
        q_pattern = re.compile('[a-z]{2}:.+')
        for q in qs:
            if q_pattern.match(q):
                arg = q[:2] # xx:yyyy, only gets xx
                rem = q[3:] # xx:yyyy, gets yyyy
                if not curr_key or arg != curr_key:
                    curr_key = arg
                if curr_key not in search_keys:
                    search_keys[curr_key] = []
                search_keys[curr_key].append(rem)
            elif curr_key != None:
                search_keys[curr_key].append(q)
        for k, v in search_keys.items():
            if k == 'au':
                criteria.append('author LIKE "%%%s%%"' % '%'.join(v.lower()))
            elif k == 'tu':
                deltaT = 1000 * 3600 * int(v[0])
                target = int(time.time() * 1000) - deltaT
                criteria.append('timestamp >= %d' % target)
            elif k == 'pn':
                criteria.append('project_name LIKE "%%%s%%"' % '%'.join(v))
            elif k == 'sh':
                criteria.append('skills_have LIKE "%%%s%%"' % '%'.join(v.lower()))
            elif k == 'sw':
                criteria.append('skills_wanted LIKE "%%%s%%"' % '%'.join(v.lower()))
            elif k == 'sl':
                cnt = int(v[0])
                criteria.append('team_size <= %d' % cnt)
            elif k == 'sg':
                cnt = int(v[0])
                criteria.append('team_size >= %d' % cnt)
    filter_query = ' AND '.join(criteria)
    sql_query = 'SELECT %s FROM %s' % (','.join(KEYS), PROJECT_TABLE_NAME)
    if len(criteria) > 0:
        sql_query += ' WHERE %s %s' % (filter_query, 'ORDER BY %s %s' % (ordering, invert_order) if ordering else '')
    return gather(execute(sql_query).fetchall())

def modify_status(msg):
    posting = [w.strip() for w in re.split('\s+', msg.text) if w][2:] # eliminates "@letsmake status" string
    status_str = posting[-1].lower()
    status = 0
    if status_str == 'fulfilled':
        status = 1
    elif status_str == 'closed':
        status = 2
    elif status_str != 'open':
        return
    projects = posting[:len(posting)-1]
    sql_query = ''
    if 'all' in projects:
        sql_query = 'UPDATE %s SET status = %d WHERE authorid = %s' % (PROJECT_TABLE_NAME, status, msg.userid)
    else:
        update_constraint = 'id IN (%s)' % ','.join(['"%s"' % _id.lower() for _id in projects])
        sql_query = 'UPDATE %s SET status = %d WHERE authorid = "%s" AND %s' % (PROJECT_TABLE_NAME, status.lower(), msg.userid, update_constraint)
    execute(sql_query)

# Handles commands given by the user
def central_dispatch(msg):
    cmd = re.split('\s+', msg.text.strip())[1]
    if cmd == 'list-projects':
        send_projects_to_user(list_projects(msg), msg.userid)
    elif cmd == 'status':
        modify_status(msg)
    elif cmd == 'help':
        send_message(letsmake_man, msg.userid)
    else:
        resp = process_posting(msg)
        send_message(resp[1], msg.userid)

#sends message to a channel
if __name__ == "__main__":
    create_tables()
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            messages = parse_slack_output(slack_client.rtm_read())
            for msg in messages:
                central_dispatch(msg)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
