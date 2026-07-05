import os
import tomllib


class ConfigError(Exception):
    """
    triggered when something goes wrong
    """


class Config:
    """
    config related functions
    """

    def __init__(self, config_path=None):
        self._config_file = config_path or self._get_config_file()
        # self._loaded_config = self.load_config() # used in get_value

    def _get_config_file(self):
        config_file_path = os.path.expanduser("~/.config/sysmon/config.toml")

        if not os.path.exists(config_file_path):
            raise ConfigError(
                "[_get_config_file] Config file does not exist. Did you copy 'config.toml' to '~/.config/sysmon/'?"
            )

        return config_file_path

    def load_config(self):
        """
        load the config nd return the dict
        """

        try:
            with open(self._config_file, mode="rb") as config_file:
                return tomllib.load(config_file)

        except FileNotFoundError as exc:
            raise ConfigError(
                f"[load_config] Config file '{self._config_file}' not found."
            ) from exc

    # def get_value(self, section, key):
    #     """
    #     get value from config file
    #     """

    #     # is this even useful or needed? developer can just do this
    #     # their own way, idk

    #     try:
    #         return self._loaded_config[section][key]

    #     except KeyError as exc:
    #         raise ConfigError(f"[get_value] Failed reading value: {exc}") from exc
