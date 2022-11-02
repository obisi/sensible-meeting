import datetime

class sensor_reading():
    TYPE_DICT = {
        "id": int,
        "value": int,
        "session_id": int,
        "created_at": datetime.datetime
    }

    def __init__(self, values):
        self.check_value_types(values)

        self.id = values["id"]
        self.value = values["value"]
        self.created_at = values["created_at"]
        self.session_id = values["session_id"]

    def __repr__(self):
         return str(self.__dict__)

    def __str__(self):
         return str(self.__dict__)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        elif self.__dict__.keys() != other.__dict__.keys():
            return False
        else:
            vals = [v == other.__dict__[k] for k, v in self.__dict__.items()]
            return all(vals)
            
    
    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            return True
        elif self.__dict__.keys() != other.__dict__.keys():
            return True
        else:
            vals = [v != other.__dict__[k] for k, v in self.__dict__.items()]
            return any(vals)
    

    def check_value_types(self, values):
        if not isinstance(values, dict):
            raise Exception("Incorrect values given, was expecting dict")
        
        missing_keys = [k for k in self.TYPE_DICT.keys() if not k in values]
        if missing_keys:
            raise Exception(f"Following keys were missing: {', '.join(missing_keys)}")

        for k, t in self.TYPE_DICT.items():
            if not k in values:
                raise Exception(f"Values was missing key {k}")
            v = values[k]
            if not isinstance(v, self.TYPE_DICT[k]):
                raise Exception(f"Incorrect value given for {k}: was expecting {self.TYPE_DICT[k]} but got {type(v)} instead")

