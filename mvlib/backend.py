import os.path
import json

# 该模块目前仅用于静态配置，不提供backend.method()的接口

path_config = "$HOME/.mvlib/mvlib.json"

if os.path.exists(path_config):
    dict_conf = json.load(path_config)
else:
    dict_conf = {
        "image_data_format": "channels_last",
        "epsilon": 1e-07,
        "floatx": "float32",
        "backend": "skimage"
    }
    json.dump(dict_conf, path_config)

Backend = dict_conf["backend"]
print(f"Using 【{Backend}】 Backend")
