import psycopg2
import datetime
import pandas as pd
import numpy as np
# import sqlalchemy as db

from datetime import date, timedelta
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
                database = cf.PGDATABASE, 
                user = cf.PGUSER, 
                password = cf.PGPASSWORD, 
                host = cf.PGHOST, 
                port = cf.PGPORT
            )
            print(self.db)
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

    def load_sensor_data(self, session_id, from_date=date.today(), to_date=date.today()+timedelta(days=1)):
        '''
        Load sensor data in latest N minutes
        '''
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                '''
                SELECT * FROM csproject_co2_reading
                WHERE session_id = '{}'
                AND created_at > '{}'
                AND created_at < '{}'
                ORDER BY created_at
                '''.format(
                    session_id,
                    from_date,
                    to_date
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
                lambda x: datetime.datetime.timestamp(datetime.datetime.strptime(x, date_format)))
            return data
        except Exception as e:
            print('[Error]', e)
            return False

    def register_session(self, sensor_id, num_people, location):
        '''
        Save a new row of session (sensor id, the timestamp session starts)
        '''
        try:
            now_ts = datetime.datetime.now().timestamp()
            cursor = self.conn.cursor()
            session_id = cursor.execute(
                '''
                INSERT INTO session (sensor_id, start_at, num_people, location)
                VALUES ({}, {}, {}, {})
                RETURNING session_id;
                '''.format(
                    sensor_id,
                    now_ts,
                    num_people,
                    location
                )
            )
            return session_id
        except Exception as e:
            print('[Error]', e)
            return False

    def update_session(self, session_id, num_people, location, end_at):
        '''
        Save a new row of session (sensor id, the timestamp session starts)
        '''
        try:
            now_ts = datetime.datetime.now().timestamp()
            cursor = self.conn.cursor()
            cursor.execute(
                '''
                UPDATE session SET 
                    updated_at = {}
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

    def fetch_session(self, session_id):
        '''
        Fetch session by id
        '''
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                '''
                SELECT * FROM session
                WHERE session_id = '{}'
                '''.format(session_id)
            )
            field_names = [i[0] for i in cursor.description]
            session = cursor.fetchall()[0]         
            return dict(zip(field_names,session))
        except Exception as e:
            print('[Error]', e)
            return None