import os
import sqlalchemy as db
import pandas as pd

import psycopg2
import sensor_reading
import datetime


class PostgreSQL_DB():

    def __init__(self):

        self.set_db_env()
        # self.connect() for sqlAlchemy
    
    def set_db_env(self):
        """Parse env variables for db connection
        """
        self.DB =  os.environ["PGDATABASE"]
        self.HOST = os.environ["PGHOST"]
        self.USER = os.environ["PGUSER"]
        self.PASSWORD = os.environ["PGPASSWORD"]
        self.PORT = os.environ["PGPORT"]
        self.DB_TYPE= "postgresql"
        self.DB_DIALECT = "" # empty or another example, "+pg8000"

    def connect(self) -> psycopg2.connection:
        """Connection to db

        Returns:
            psycopg2.connection: connection to db
        """
        conn = psycopg2.connect(
        database=self.DB, user=self.USER, password=self.PASSWORD, host=self.HOST, port=self.PORT
        )
        return conn

    def create_cursor(self) -> psycopg2.cursor:
        """Creates cursor for connection

        Returns:
            psycopg2.cursor: cursor used to execute queries
        """
        conn = self.connect()
        cursor = conn.cursor()
        return cursor



    def connectAlchemy(self):
        '''
        Connect to the database
        '''
        try:
            ## TODO: Connect to the DB
            engine = db.create_engine(f'{self.DB_TYPE}{self.DB_DIALECT}://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}')
            self.connection = engine.connect()
        except Exception as e:
            print(e)

    def save_sensor_data(self, sensor_data):
        '''
        Save a new row of sensor data into DB
        '''
        try:
            conn = self.connect()
            cursor = conn.cursor()
            SQL = "INSERT INTO  csproject_co2_reading(id, value, created_at, session_id) VALUES(%(id)s, %(value)s, %(created_at)s, %(session_id)s) RETURNING *"
            data = {
                        "id":sensor_data.id, 
                        "value": sensor_data.value, 
                        "created_at": sensor_data.created_at, 
                        "session_id": sensor_data.session_id
                    }
            cursor.execute(SQL, data)
                            
            resp = cursor.fetchall()
            field_names = self.get_field_names()
            saved_sensor_reading = self.parse_sql_to_sensor_readings(field_names, resp)

            return sensor_data == saved_sensor_reading[0]

        except Exception as e:
            print(f'[Error]: {e}')
            return False
    
    def parse_sql_to_sensor_readings(self, field_names: list, data: list) -> list:
        """Parses sql query data to list of sensor readings

        Args:
            field_names (list): field names by cursor
            data (list): data queried from table by cursor

        Returns:
            list: sensor readings found
        """
        sr_list = []
        for _data in data:
            resp_vals = { k:v for k,v in zip(field_names, list(_data))}
            sr_resp = sensor_reading(resp_vals)
            sr_list.append(sr_resp)
        return sr_list


    def get_field_names(self, cursor: psycopg2.cursor) -> list:
        """Return names from db query

        Args:
            cursor (psycopg2.cursor): cursor used for sql query

        Returns:
            list: fieldnames from queried table
        """
        return [i[0] for i in cursor.description]


    def read_session_data_relative_time(self, session_id: int, minutes: int) -> list:
        """Read timeframe from database for session.

        Args:
            session_id (int): session id for query
            minutes (int): timeframe in minutes

        Returns:
            list: sensor readings
        """
        cursor = self.create_cursor()

        timeframe = datetime.datetime.now - datetime.timedelta(minutes=minutes)

        SQL = "SELECT * FROM csproject_co2_reading WHERE session_id=%s and created_at>%s"
        data = (session_id, timeframe)
        cursor.execute(SQL, data)
        
        field_names = self.get_field_names(cursor)
        db_data = cursor.fetchall()
        sensor_readings = self.parse_sql_to_sensor_readings(field_names, db_data)
        return sensor_readings

    def read_session_data_relative_time_to_pandas(self, session_id: int, minutes: int) -> pd.DataFrame:
        """Read relative session data from db to pandas

        Args:
            session_id (int): session id for query
            minutes (int): minutes of timeframe for query

        Returns:
            pd.DataFrame: dataframe of sensor data
        """
        data = self.read_session_data_relative_time(session_id, minutes)
        df = pd.DataFrame([x.to_dict() for x in data])
        return df
    

    def read_session_data(self, session_id: int) -> list:
        """Returns all data for given sessions id

        Args:
            session_id (int): session id for data query

        Returns:
            list: list of sensor readings
        """
        cursor = self.create_cursor()

        SQL = "SELECT * FROM csproject_co2_reading WHERE session_id=%s"
        data = (session_id)
        cursor.execute(SQL, data)

        
        field_names = self.get_field_names(cursor)
        db_data = cursor.fetchall()
        sensor_readings = self.parse_sql_to_sensor_readings(field_names, db_data)
        return sensor_readings
    
    def read_session_data_to_pandas(self, session_id: int) -> pd.DataFrame:
        """Read session data from database to pandas

        Args:
            session_id (int): session id to query to db

        Returns:
            pd.DataFrame: dataframe of sensor data
        """
        data = self.read_session_data(session_id)
        df = pd.DataFrame([x.to_dict() for x in data])
        return df


    def read_all_data(self) -> list:
        """Return all data from database

        Returns:
            list: list of sensor readingds
        """
        cursor = self.create_cursor()
        cursor.execute(f"SELECT * FROM csproject_co2_reading")
        field_names = self.get_field_names()
        db_data = cursor.fetchall()
        data = self.parse_sql_to_sensor_readings(field_names, db_data)
        return data
    

    def read_all_data_to_pandas(self) -> pd.DataFrame:
        """Query all data from db and return as a pandas dataframe

        Returns:
            pd.DataFrame: dataframe of sensor readings
        """
        data = self.read_all_data()
        df = pd.DataFrame([x.to_dict() for x in data])
        return df



    def update_session_id(self, sensor_id: int, session_id: int, hours = 1) -> bool:
        """Update all data in a given timeframe

        Args:
            sensor_id (int): id of sensor where session ids should be changed
            session_id (int): new session id for readings
            hours (int, optional): timeframe for change in hours. Defaults to 1.

        Returns:
            bool: if change was succesful
        """
        try:
            one_hour_ago = datetime.dateime.now() - datetime.timedelta(hours=hours)
            cursor = self.create_cursor()
            SQL = "UPDATE csproject_co2_reading SET session_id=%s WHERE id=%s and create_at>%s"
            data = (session_id, sensor_id, one_hour_ago)
            cursor.execute(SQL, data)
            return True # Check if data was actually changes: return values changed, check all session_ids are changed
        except Exception as e:
            print(f'[Error]: {e}')
            return False


