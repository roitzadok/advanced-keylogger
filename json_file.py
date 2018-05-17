import json
import os


class JsonFile(object):
    """
    class to manage json files
    """
    def __init__(self, file_name):
        """
        creates json file if doesn't exists
        @param file_name: json file name to manage
        """
        self.__file_name = file_name
        if not os.path.exists(file_name):
            with open(file_name, "w+") as f:
                pass

    def __read_file(self):
        """
        read json file and return the data
        """
        try:
            with open(self.__file_name, "r") as json_file:
                data = json.load(json_file)
        except ValueError:
            return {}
        return data

    @property
    def read(self):
        """
        when read called from outside
        """
        return self.__read_file()

    def add_to_file(self, key, value):
        """
        add something to the json file
        @param key: the key of the new object
        @param value: the value of the new object
        """
        key = str(key)
        data = self.__read_file()
        if key in data:
            lst = data[key]
            lst.append(value)
            data[key] = lst
            self.__dump(data)
            return
        data[key] = [value]
        self.__dump(data)

    def __dump(self, data):
        """
        dump to the file
        @param data: data to dump
        """
        with open(self.__file_name, "w") as json_file:
            json.dump(data, json_file)

    def print_file(self):
        """
        printing method
        """
        print self.__read_file()

    def __str__(self):
        """
        str conversion
        """
        string = ""
        data = self.__read_file()
        for item in enumerate(data):
            print item
            string += str(item[1]) + " : " + str(data[item[1]]) + "\n"
        return string
