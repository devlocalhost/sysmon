from utils.logger import create_logger


class BasePlugin:
    """base plugin, which all others are based on"""

    def __init__(self):
        """init function, defining basics"""

        self.logger = create_logger(self.__class__.__name__)
        self._opened_files = []
        # maybe this should be a function instead?
        # try opening file. if it opens, log
        # else log, plus exception. looks/feels cleaner to me

    def _seek_files(self):
        for file in self._opened_files:
            self.logger.debug(f"seeking {file.name}")
            file.seek(0)
            # maybe i should use a try except block?
            # im already handling that in the plugins though...

    def _open_file(self, file, mode="r", encoding="utf-8"):
        """modifying the default open method so i dont have to define encoding every time"""

        self.logger.debug(f"opening file {file} in {mode} mode and {encoding} encoding")

        try:
            f = open(file, mode=mode, encoding=encoding)
            self.logger.debug(f"opened  file {file}")
            
            return f

        except Exception as exc:
            self.logger.debug(f"failed opening file {file}: {exc}")
            raise

    def close_files(self):
        """
        closing any opened files. must be called
        when exiting
        """

        for file in self._opened_files:
            try:
                file.close()
                self.logger.debug(f"closing file {file.name}")

            except Exception as exc:
                self.logger.debug(f"error closing file: {exc}")

    def get_data(self):
        """
        where the magic happens. this function
        gets then returns data
        """

        pass
