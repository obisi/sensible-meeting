import psycopg2
import datetime
import pandas as pd
import numpy as np
# import sqlalchemy as db

from datetime import date, timedelta
from os.path import join, abspath, dirname
from app.setting.config import CONFIGS as cf

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
        except Exception as e:
            print(e)

    def save_sensor_data(self, sensor_data):
        '''
        Save a new row of sensor data into DB
        '''
        try:
            ## TODO: Write SQL code / Maybe use sqlalchemy to save data row
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