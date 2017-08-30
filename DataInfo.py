import os
import shutil

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))


class DataInfo:
    """
    handle the program's data
    """

    def __init__(self, all_data_path="", *data_types):
        """
        set and create all of the data dirs
        @param all_data_path: the chosen path to save data in
        @param data_types: list of files' type that are going to be inserted.
        unnecessary unless you would like to create special dirs
        """
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
        @param file: the file to create
        @param file_type: the file's type (optional)
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
        @param file_name: the file's name.....
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
        """
        delete a chosen file
        @param file_name: the file to delete
        """
        if file_type == "":
            file_type = file_name.split('.')[-1]
        try:
            os.remove(self.get_file_path_by_type(file_name, file_type))
        except OSError:
            pass

    def read_file(self, file_name, file_type=""):
        """
        read the content of a chosen file
        @param file_name: the file to read from
        """
        if file_type == "":
            file_type = file_name.split('.')[-1]
        file_path = self.get_file_path_by_type(file_name, file_type)
        if not os.path.exists(file_path):
            return ""
        with open(file_path, "r") as read:
            return read.read()

    def is_file(self, file_name, file_type=""):
        """
        check if a file exists
        @param file_name: the file to check if exists
        """
        if file_type == "":
            file_type = file_name.split('.')[-1]
        file_path = self.get_file_path_by_type(file_name, file_type)
        if os.path.exists(file_path):
            return True
        return False

    def zip_dir(self, dir_path="", new_zip_location=""):
        """
        create a zip file of a chosen dir
        @param dir_path: the path to the dir,
        can be left empty if you want to create zip
        of the data files
        @param new_zip_location: the path to save the new zip,
        can be left blank in order to save it in the original path
        """
        if not dir_path:
            dir_path = self.all_data_path
        if not new_zip_location:
            new_zip_location = dir_path
        return shutil.make_archive(new_zip_location, 'zip', dir_path)

    def delete_dir(self, dir_path=""):
        """
        delete a chosen dir
        @param dir_path: the path to the dir
        """
        if not dir_path:
            dir_path = self.all_data_path
        elif dir_path in self.data_types:
            dir_path = self.all_data_path + "\\" + dir_path
        shutil.rmtree(dir_path)

    def clear_dir(self, dir_name):
        """
        empty a chosen dir from its files
        @param dir_name: the dir to empty
        """
        self.delete_dir(dir_name)
        os.makedirs(self.get_type_path(dir_name))