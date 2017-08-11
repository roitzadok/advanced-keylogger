import os


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))


class DataInfo:
    """
    handle the program's data
    """

    def __init__(self, all_data_path="", *data_types):
        self.all_data_path = CURRENT_PATH + "\\data"
        if all_data_path != "":
            self.all_data_path = all_data_path
        self.data_types = []
        if not data_types == []:
            self.data_types = data_types
        self.__ready_paths()

    def __ready_paths(self):
        """
        make sure everything we touch exists
        """
        # create path if it doesnt exist
        if not os.path.exists(self.all_data_path):
            os.makedirs(self.all_data_path)
        for my_type in self.data_types:
            # create path if it doesnt exist
            if not os.path.exists(self.get_type_path(my_type)):
                os.makedirs(self.get_type_path(my_type))

    def new_data_file(self, file, file_type=""):
        """
        if no data file exists create a new one
        """
        if file_type == "":
            # get the file's type
            file_type = file.split('.')[-1]
        if not os.path.exists(self.get_file_path_by_type(file, file_type)):
            with open(self.get_file_path_by_type(file, file_type), "w+") as f:
                pass

    def get_file_path_by_type(self, file_name, file_type=""):
        """
        assuming that the file should be with it's type give it's path
        """
        if file_type == "":
            # get the type yourself
            return self.get_type_path(file_name.split('.')[-1]) + "\\" + file_name
        return self.get_type_path(file_type) + "\\" + file_name

    def get_type_path(self, files_type):
        """
        @files_type: the given type
        return: the files' path for the given type
        """
        return self.all_data_path + "\\" + files_type

    def write_data_file_end(self, data, data_file, file_type=""):
        """
        write data to the end of a chosen file
        @param data: the data to write
        @param data_file: file to write to
        @param file_type: optional in case you would like to
        choose an invented type, for instance: screenshot
        """
        self.__ready_paths()
        if file_type == "":
            file_type = data_file.split('.')[-1]
        try:
            with open(self.get_file_path_by_type(data_file, file_type), "a") as data_file:
                data_file.write(data)
        # if the file was deleted
        except IOError:
            with open(self.get_file_path_by_type(data_file, file_type), "w+") as data_file:
                data_file.write(data)

    def delete_data_file(self, file_name, file_type=""):
        if file_type == "":
            file_type = file_name.split('.')[-1]
        try:
            os.remove(self.get_file_path_by_type(file_name, file_type))
        except OSError:
            pass

    def read_file(self, file_name, file_type=""):
        if file_type == "":
            file_type = file_name.split('.')[-1]
        file_path = self.get_file_path_by_type(file_name, file_type)
        if not os.path.exists(file_path):
            return ""
        with open(file_path, "r") as read:
            return read.read()

    def is_file(self, file_name, file_type=""):
        if file_type == "":
            file_type = file_name.split('.')[-1]
        file_path = self.get_file_path_by_type(file_name, file_type)
        if os.path.exists(file_path):
            return True
        return False