import os.path as osp
from utils.base import singleton
from utils.settings import JsonSettings, IniConfigSettings

@singleton
class ConfigManager:
    """ 多层级配置体系（系统、App、项目、user） """
    def __init__(self):
        self.dict_conf = {}  # "config_series": [sys_settings,
                             #  app_settings, user_settings]

    def load_conf(self, series, level, path_file):
        """ 支持导入ini/json文件 """
        if not osp.exists(path_file):
            # logger.warning(f"为找到配置文件：【{path_file}】")
            return

        ext = osp.splitext(path_file)[1]
        if ext == ".ini":
            settings = IniConfigSettings()
        elif ext == ".json":
            settings = JsonSettings()
        else:
            raise Exception(f"不支持的配置文件格式: 【{ext}】")
        settings.load(path_file)

        if series not in self.dict_conf:
            self.dict_conf[series] = [None, None, None]

        assert self.dict_conf[series][level] is None, f"请勿重复设定【{series}】【{level}】等级配置"
        self.dict_conf[series][level] = settings

    def load_configs(self, series, list_files):
        for idx, path_file in enumerate(list_files):
            self.load_conf(series, idx, path_file)

    def get(self, series, top_key, options):  # , default=None
        """ 所有配置都应该至少在一个层级显式定义过，故不再提供default选项 """
        list_levels = self.dict_conf[series]
        for level_settings in reversed(list_levels):
            if level_settings is None:
                continue
            value = level_settings.get(top_key, options)
            if value is not None:
                break
            # else:  # debug
            #     if hasattr(self, "times"):
            #         self.times += 1
            #     else:
            #         self.times = 1
            #     print(f"第【{self.times}】次查询： 未找到【{top_key}】-【{options}】")
            #     if self.times == 3:
            #         del self.times
        assert value is not None, f"未定义的【{top_key}】-【{options}】配置项"
        return value

# 对于core配置，允许直接将ini设定为等级2，即不能通过user重新配置：
# 原因：类似log的目录，可能在载入user设定之前，配置项已经应用，修改造成前后分裂
# conf_mgr.load_conf("core", 2, rpath2curr("config/settings.ini"))
