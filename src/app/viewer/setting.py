import os.path

from utils.base import singleton
from utils.settings import IniConfigSettings

PATH_SETTING = "config/settings.ini"

@singleton
class PluginSettings(IniConfigSettings):
    def __init__(self):
        super().__init__()
        # 载入项目固定路径的配置，实例化时则无需关心是否load
        path_curr_file = os.path.dirname(__file__)
        # path_ini = os.path.abspath(PATH_SETTING)  # 相对工程目录的路径
        path_ini = os.path.join(path_curr_file, PATH_SETTING)  # 相对当前文件的路径
        self.load(path_ini)
