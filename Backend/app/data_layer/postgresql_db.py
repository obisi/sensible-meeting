import psycopg2
# import datetime
import pandas as pd
import numpy as np
# import sqlalchemy as db

from datetime import datetime, timezone, date, timedelta
from os.path import join, abspath, dirname
from Backend.app.setting.config import CONFIGS as cf

class PostgreSQL_DB():

    def __init__(self):
        self.connect()

    def connect(self):
        '''
        Connect to the database
        '''
        try:
            self.conn = psycopg2.connect(
                database = 'railway',# cf.PGDATABASE, 
                user = 'postgres', # cf.PGUSER, 
                password = 'oVElIg2jo16d4xvDMUmX', # cf.PGPASSWORD, 
                host = 'containers-us-west-33.railway.app', # cf.PGHOST, 
                port = 7747 # cf.PGPORT
            )
            self.conn.autocommit = True
        except Exception as e:
            print(e)

    def save_sensor_data(self, sensor_id, value, created_at, session_id):
        '''
        Save a new row of sensor data into DB
        '''
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                '''
                INSERT INTO csproject_co2_reading (id, value, craeted_at, session_id)
                VALUES ({}, {}, {}, {});
                '''.format(
                    sensor_id,
                    value,
                    created_at,
                    session_id
                )
            )
            return True
        except Exception as e:
            print('[Error]', e)
            return False

    def load_sensor_data(self, sensor_id, from_date, to_date=datetime.now().timestamp()):
        '''
        Load sensor data in latest N minutes
        '''
        try:
            cursor = self.conn.cursor()
            from_date_filter=''
            to_date_filter=''
            if from_date:
                from_date = datetime.fromtimestamp(from_date, tz=timezone.utc)
                from_date_filter = "AND created_at >= '{}'".format(from_date)
            if to_date:
                to_date = datetime.fromtimestamp(to_date, tz=timezone.utc)
                to_date_filter = "AND created_at <= '{}'".format(to_date)
            cursor.execute(
                '''
                SELECT * FROM csproject_co2_reading
                WHERE sensor_id = '{}'
                {} {}
                ORDER BY created_at
                '''.format(
                    sensor_id,
                    from_date_filter,
                    to_date_filter
                )
            )
            field_names = [i[0] for i in cursor.description]
            db_data = cursor.fetchall()
            date_format = '%Y-%m-%d %H:%M:%S.%f'
            data = pd.DataFrame.from_records(db_data, columns=field_names)
            data = data.drop(columns=['id'])
            data['created_at'] = data['created_at'].astype(str)
            data[data['value'] < 3000 ]['value'] = None
            data[data['value'] > 180 ]['value'] = None
            data['value'] = data['value'].fillna((data['value'].shift() + data['value'].shift(-1))/2)
            data['timestamp'] = data['created_at'].apply(
                lambda x: datetime.timestamp(datetime.strptime(x, date_format)))
            return data
        except Exception as e:
            print('[Error]', e)
            return False

    def register_session(self, sensor_id, num_people, location):
        '''
        Save a new row of csproject_sessions (sensor id, the timestamp session starts)
        Terminate prev session of the same sensor id
        '''
        try:
            now_ts = datetime.now().timestamp()
            cursor = self.conn.cursor()
            # update running session with same sensor_id
            cursor.execute(
                '''
                UPDATE csproject_sessions SET 
                    updated_at = {},
                    end_at = {}
                WHERE sensor_id = '{}' 
                AND end_at IS NULL
                '''.format(now_ts, now_ts, sensor_id)
            )

            # register new session
            now_ts = datetime.now().timestamp()
            cursor.execute(
                '''
                INSERT INTO csproject_sessions (sensor_id, start_at, num_people, location)
                VALUES ({}, {}, {}, '{}')
                RETURNING session_id;
                '''.format(
                    sensor_id,
                    now_ts,
                    num_people,
                    location
                )
            )
            session_id = cursor.fetchall()[0][0]
            return session_id
        except Exception as e:
            print('[Error]', e)
            return False

    def update_session(self, session_id, num_people, location, end_at):
        '''
        Save a new row of csproject_sessions (sensor id, the timestamp session starts)
        '''
        try:
            now_ts = datetime.now().timestamp()
            cursor = self.conn.cursor()
            cursor.execute(
                '''
                UPDATE csproject_sessions SET 
                    updated_at = {},
                    end_at = {},
                    num_people = {},
                    location = '{}'
                WHERE session_id = '{}'
                '''.format(now_ts, end_at, num_people, location, session_id)
            )
            # return "Session terminated successfully"
            return True
        except Exception as e:
            print('[Error]', e)
            return False

    def fetch_session(self, session_id, from_date=None):
        '''
        Fetch session by id
        '''
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                '''
                SELECT * FROM csproject_sessions
                WHERE session_id = '{}'
                '''.format(session_id)
            )
            field_names = [i[0] for i in cursor.description]
            session_tuple = cursor.fetchall()[0]
            session = dict(zip(field_names, session_tuple))
            if session:
                session_sensor_id = session.get('sensor_id')
                if from_date is None:
                    from_date = session.get('start_at')
                session_sensor_data = self.load_sensor_data(
                    sensor_id=session_sensor_id, from_date=from_date, to_date=None
                ).to_dict('records')
                session_data = session.copy()
                session_data['sensor_records'] = session_sensor_data
                return session_data
            else:
                return None
        except Exception as e:
            print('[Error]', e)
            return None