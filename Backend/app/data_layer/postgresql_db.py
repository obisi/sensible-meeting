import os
import sqlalchemy as db

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
            ## TODO: Connect to the DB
            engine = db.create_engine('dialect+driver://user:pass@host:port/db')
            connection = engine.connect()
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