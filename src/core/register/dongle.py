import json

from .regm.encrypt import RsaCrypto, rsa
from .regm.protocal import RegCodeTrans

class ServerCrypto(RsaCrypto):
    def __init__(self):
        super().__init__()

        bytes_pub = """-----BEGIN RSA PUBLIC KEY-----
MIGJAoGBAIKaYa3tbKYKBijzGJxo3tO3+d4RyXEIeGCFkca8AwG1CcGfqdNWcHaT
VrNkR/XfAv1NwzaOneSnSc82CY65kgu1/cB8Tm9+dpT8/qigQcai38QTZ+Vwj+E4
+rtn4K0ovCHDizZ98y3r4VJWb9QJrGPgn0/1BG1++FFpFYVyTlJHAgMBAAE=
-----END RSA PUBLIC KEY-----"""
        self.key_pub = rsa.PublicKey.load_pkcs1(bytes_pub)

        bytes_priv = """-----BEGIN RSA PRIVATE KEY-----
MIICYQIBAAKBgQCCmmGt7WymCgYo8xicaN7Tt/neEclxCHhghZHGvAMBtQnBn6nT
VnB2k1azZEf13wL9TcM2jp3kp0nPNgmOuZILtf3AfE5vfnaU/P6ooEHGot/EE2fl
cI/hOPq7Z+CtKLwhw4s2ffMt6+FSVm/UCaxj4J9P9QRtfvhRaRWFck5SRwIDAQAB
AoGAE0nXqUdKZ49Nb5jPhrIaTqx6M6ju1knI9YBkkjRMQWFKapU5EKRQgcKq6F2k
HxTrrRth/Fm9yfpG9Vpmo3jaaeG/ZS0LrD8AZj7Kw2lu0KGpOCWVpGiB3mJoMMjl
GiW7YfsVcVWQdwwh57vDTIc1igHMe3ZWizap0QUkk9j/3kECRQCRdmtiYUtNas10
pkNHQ7lQ/9UznQLU/57DIESdTrYQ0Rkh9/CuNuZ9EiZ4O1JTgwc2BgcB5N0Y/ZMm
DK6rOpe0SsTloQI9AOXZQ01FH2qu0ujG9MfpeaxAfO6/39UFHydQgS+KwmBsATBh
P6YkUBak4Kb2xtI8ZLQFlTneEcdK6RJe5wJFAItFsnMzbIHnLGfveKMW+KvRBzSv
tDJzvHJextNGtZNMYJ/hYJOtBOnjIuojAiPrZFAZXUQ2+Gog/26C3gobw3xfyj2B
Aj0Al7vVsizvkH3YvdKZxV9b81qfHv2LxhSbfFio77mql/y0zDtmyUcvl8NAivhe
SGuWD0GgQZNYKThKpNYBAkRkUswJHkuoMzljpuUei97ueFVgU8iwosh0ntIb0Ai4
2qadoaf/Dbcc5sQQVyofxfnBgknvp/8sO5wVQOFCy67JT63Q/w==
-----END RSA PRIVATE KEY-----"""
        self.key_priv = rsa.PrivateKey.load_pkcs1(bytes_priv)


def getopt():
    import argparse

    parser = argparse.ArgumentParser("MVTool加密狗", description="")
    parser.add_argument("uuid", action="store", help="注册机器的UUID编码")
    parser.add_argument("-t", "--trytime", action="store", default=1, help="试运行的时长")
    parser.add_argument("-d", "--deadline", action="store", default="2020-01-30", help="授权截止日期")
    return parser.parse_args()


if __name__ == "__main__":

    crypto = ServerCrypto()
    protocal = RegCodeTrans(crypto)
    args = getopt()

    # import uuid
    # machine_code = uuid.getnode()  # int

    dict_info = {
        "license": "triage_v0.2",
        "machine": args.uuid,
        "trytime": args.trytime,
        "deadline": args.deadline
    }
    certificate = json.dumps(dict_info)
    signature = crypto.sign(certificate).decode()

    with open("certificate.txt", "w") as fp:
        lines = signature + "\n" + certificate
        fp.write(lines)

    print("已生成授权证书")
