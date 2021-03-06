# Based on: Register Code Generator/Server, [v0.1.5] 2020-01-18

import os
import uuid
import json
from datetime import date
import rsa

from utils.sock.routine import TcpClient
from .regm.protocal import RegCodeTrans
from .regm.encrypt import RsaCrypto


class ClientCrypto(RsaCrypto):
    def __init__(self):
        super().__init__()

        bytes_pub = """-----BEGIN RSA PUBLIC KEY-----
MIGJAoGBAIKaYa3tbKYKBijzGJxo3tO3+d4RyXEIeGCFkca8AwG1CcGfqdNWcHaT
VrNkR/XfAv1NwzaOneSnSc82CY65kgu1/cB8Tm9+dpT8/qigQcai38QTZ+Vwj+E4
+rtn4K0ovCHDizZ98y3r4VJWb9QJrGPgn0/1BG1++FFpFYVyTlJHAgMBAAE=
-----END RSA PUBLIC KEY-----"""
        self.key_pub = rsa.PublicKey.load_pkcs1(bytes_pub)

#####################################################################

from utils.base import singleton
@singleton
class LicenseChecker:
    def __init__(self):
        self.crypto = ClientCrypto()
        self.dict_license = None
        self.read_conf()  # 延迟读取配置

    def read_conf(self):
        from .. import conf_mgr

        self.ipaddr = conf_mgr.get("core", "server", "ipaddr")
        self.port = int(conf_mgr.get("core", "server", "port"))

        DIR_REGCONF = conf_mgr.get("core", "path", "dir_conf")
        if not os.path.exists(DIR_REGCONF):
            os.makedirs(DIR_REGCONF)
        self.path_uuid = os.path.join(DIR_REGCONF, "uuid.txt")
        self.path_cert = os.path.join(DIR_REGCONF, conf_mgr.get("core", "path", "certificate"))

    # def conn_server(self, ipaddr, port, path_cert):
    #     self.ipaddr = ipaddr
    #     self.port = port
    #     self.path_cert = path_cert

    def manual_authorize(self):
        """ 策略2: 使用本地授权 """
        with open(self.path_uuid, "w") as fp:
            machine_node = uuid.getnode()
            fp.write(str(machine_node))
        return machine_node

    def check(self, version: list):
        if not os.path.exists(self.path_cert):
            try:
                client = TcpClient((self.ipaddr, self.port))
                protocal = RegCodeTrans(self.crypto)
                protocal.set_cert_path(self.path_cert)
                client.set_protocal(protocal)

                # client.listen()
                client.protocal.register(version)  # 注册license
                client.recv_whole()
                # client.join()
                client.stop()

            except TimeoutError:
                description = f"无法连接到授权服务器【{self.ipaddr}】，无法获取授权"
                return 2, description

        status = self._check_certificate(self.path_cert)
        # self.state, self.description = status
        return status

    def _check_certificate(self, path_cert):
        """ return (state, description)
            state:
                - 0: 已授权
                - 1: 未授权，但在试用期
                - 2: 未授权，超出试用期
        """
        with open(path_cert, "r") as fp:
            lines = fp.readlines()
        # assert self.crypto.verify(lines[1], lines[0])
        if not self.crypto.verify(lines[1], lines[0]):
            return 2, "非法的证书签名，请重新申请证书"

        dict_info = json.loads(lines[1])
        self.dict_license = dict_info

        local_guid = uuid.getnode()
        # assert local_guid == dict_info["machine"]
        if local_guid != int(dict_info["machine"]):
            return 2, "持有证书与当前机器不匹配，请重新申请证书"

        trytime = self.get_trytime()
        if trytime is None:
            return 0, "永久授权"  # 不存在trytime则为永久授权

        today = date.today()
        deadline = self.get_deadline()
        if not deadline:
            return 2, f"软件未授权，限制使用【{trytime}】min"
        else:
            # assert today <= deadline,
            if today > deadline:
                return 2, f"当前的授权已过期，有效期至【{deadline}】"
            else:
                return 1, f"当前授权的有效期至【{deadline}】"

    def get_trytime(self):
        if not self.dict_license:
            return 0

        if "trytime" in self.dict_license:
            trytime = self.dict_license["trytime"]
            return float(trytime)

    def get_deadline(self):
        if not self.dict_license:
            return date(1, 1, 1)

        str_deadline = self.dict_license.get("deadline")
        if str_deadline:
            list_datestr = str_deadline.split("-")
            list_deadline = [int(x) for x in list_datestr]
            deadline = date(*list_deadline)
            return deadline


if __name__ == "__main__":
    mngr = LicenseChecker()
    mngr.conn_server("127.0.0.1", 31618, "./certificate.txt")
    state, reason = mngr.check("experienced")

    print(f"验证授权状态: {state}, {reason}")
