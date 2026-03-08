from utils.logger import create_logger


class BasePlugin:
    """base plugin, which all others are based on"""

    def __init__(self):
        """init function, defining basics"""

        self.logger = create_logger(self.__class__.__name__)
        self._opened_files = []

    def _seek_files(self):
        for file in self._opened_files:
            self.logger.debug(f"seeking {file.name}")
            
            try:
                file.seek(0)

            except Exception as exc:
                self.logger.debug(f"error seeking file: {exc}")

    def _open_file(self, file, mode="r", encoding="utf-8"):
        """modifying the default open method so i dont have to define encoding every time"""

        return open(file, mode=mode, encoding=encoding)

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
