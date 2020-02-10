# encoding: utf-8

import os
import json
from datetime import date, timedelta
from utils.sock.trans import TransBase, json2dict

from utils.log import getLogger
logger = getLogger()

class RegCodeTrans(TransBase):
    """ 向服务端发送注册验证：
        {
            "type": "Register",
            "machine_id": "xxxxx",
        }
    """
    # stratergy = json.load()

    def __init__(self, rsa_crypto):
        super().__init__()

        # 通用属性
        self.crypto = rsa_crypto
        self.map_license = {}  # license: machine_id

    # def init_server(self, dir_pem):
    #     """ 如不存在pem，则生成密钥对 """
    #     if os.path.exists(dir_pem):
    #         self.crypto.load_keys(dir_pem)
    #     else:
    #         self.crypto.create_keys(dir_pem)

    # def init_client(self):
    #     """ 如不存在pem公钥，则向服务器请求公钥 """
    #     if os.path.exists(dir_pem):
    #         self.crypto.load_keys(dir_pem)
    #     else:
    #         self.ask_for_pubkey()

    def load_strategy(self):
        # 权限管理策略
        with open(os.path.join(
            os.path.dirname(__file__), "strategy.json"), "r") as fp:
            self.strategy = json.load(fp)

    ###########################################################################
    def reply(self, msg: bytes, sock1addr=None):
        # logger.debug("接收到消息：【{}】".format(msg))
        msg_head, msg_body = self.sock.msg_split(msg)

        if self.check_cmd(msg):
            dict_msg = json2dict(msg_body)
            if dict_msg["type"] == "Register":
                self.reply_register(dict_msg, sock1addr)
            # elif dict_msg["type"] == "PubKey":
            #     self.reply_pubkey(dict_msg, sock1addr)
            else:
                err = "Unkown command [{}]".format(msg)
                self.send_error(err.encode(), sock1addr)

        elif self.check_data(msg):
            pass

        else:
            err = "Unkown request [{}]".format(msg)
            self.send_error(err.encode(), sock1addr)

    def parse_reply(self, msg: bytes):
        # logger.debug("接收到回复：【{}】".format(msg))
        msg_head, msg_body = self.sock.msg_split(msg)

        if self.check_cmd(msg):
            dict_msg = json2dict(msg_body)
            if dict_msg["type"] == "Register":
                self.on_register(dict_msg)
            elif dict_msg["type"] == "PubKey":
                self.on_pubkey(dict_msg)
            else:
                print("未解析命令【{}】".format(msg))

        elif self.check_data(msg):
            pass

        else:
            logger.error("Fail to parse the message【{}】.".format(msg))

    def ask_for_pubkey(self):
        dict_msg = {
            "type": "PubKey"
        }
        self.send_cmd(dict_msg)

    def reply_pubkey(self, dict_msg, sock1addr):
        bytes_pubkey = self.crypto.get_pubkey()
        dict_msg["pubkey"] = bytes_pubkey
        self.send_cmd(dict_msg, sock1addr)

    def on_pubkey(self, dict_msg):
        bytes_pubkey = dict_msg["pubkey"]
        # 存储pubkey
        with open("./pem/public.pem", "wb") as fp:
            fp.write(bytes_pubkey)

    def register(self, version: list):
        """ version: ["triage", "v1.0.1"] """
        import uuid
        machine_code = uuid.getnode()  # int

        dict_msg = {
            "type": "Register",
            "version": version,
            "machine_id": machine_code
        }
        self.send_cmd(dict_msg)

    def reply_register(self, dict_msg, sock1addr):
        dict_msg_ret = {"type": "Register"}

        # license的唯一性(有限个机器)检查
        # machines_allowed = 1
        # if len(self.map_license[license]) >= machines_allowed:
        #     dict_msg_ret["return"] = "false"
        #     dict_msg_ret["reason"] = "license【{}】已注册".format(license)
        #     self.send_cmd(dict_msg_ret, sock1addr)
        # elif license in self.map_license:
        #     self.map_license[license].add(dict_msg["machine_id"])
        # else:
        #     self.map_license[license] = {dict_msg["machine_id"], }

        dict_msg_ret["return"] = "true"
        certificate, signature = self._make_certificate(dict_msg)
        dict_msg_ret["certificate"] = certificate
        dict_msg_ret["signature"] = signature
        self.send_cmd(dict_msg_ret, sock1addr)

    def _make_certificate(self, dict_msg):
        """ return a text """
        # 查询license有效期，在此实现有效期认证逻辑...
        dict_info = {
            "version": dict_msg["version"],
            "machine": dict_msg["machine_id"],
            "trytime": self.strategy["unauthorized"].get("trytime", "0")
        }

        version = dict_msg["version"]
        # if version in self.strategy:
        try:
            stratergy = self.strategy
            for part in version:
                stratergy = stratergy[part]

            if "trytime" in stratergy:
                dict_info["trytime"] = stratergy["trytime"]
            if "deadline" in stratergy:
                dict_info["deadline"] = stratergy["deadline"]
            elif "probation" in stratergy:
                probation = int(stratergy["probation"])
                deadline = date.today() + timedelta(days=probation)
                dict_info["deadline"] = deadline.isoformat()
        except KeyError:
            logger.error(f"未知的version:【{version}】")

        certificate = json.dumps(dict_info)
        signature = self.crypto.sign(certificate).decode()
        return certificate, signature

    def set_cert_path(self, path_certificate):
        self.path_certificate = path_certificate

    def on_register(self, dict_msg):
        if dict_msg["return"] == "false":
            reason = dict_msg["reason"]
            logger.info("注册失败 -->> {}".format(reason))
            return

        certificate = dict_msg["certificate"]
        signature = dict_msg["signature"]

        dir_ = os.path.dirname(self.path_certificate)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        with open(self.path_certificate, "w") as fp:
            lines = signature + "\n" + certificate
            fp.write(lines)

        logger.debug("已保存注册证书【{}】".format(self.path_certificate))
