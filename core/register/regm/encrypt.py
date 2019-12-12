import os
import base64

from util.expy import path_expand
path_expand("runtime", __file__)
import rsa

from util.log import getLogger
logger = getLogger()

PUBKEY_FILE = 'public.pem'
PRIVKEY_FILE = 'private.pem'

def create_keys(nbits, dir_pem):
    """ 生成公钥和私钥 """
    if not os.path.exists(dir_pem):
        os.makedirs(dir_pem)
    path_pub = os.path.join(dir_pem, PUBKEY_FILE)
    path_priv = os.path.join(dir_pem, PRIVKEY_FILE)

    key_pub, key_priv = rsa.newkeys(nbits)

    bytes_pub = key_pub.save_pkcs1()
    with open(path_pub, 'wb') as fp:
        fp.write(bytes_pub)

    bytes_priv = key_priv.save_pkcs1()
    with open(path_priv, 'wb') as fp:
        fp.write(bytes_priv)


class RsaCrypto:
    def __init__(self):
        self.key_pub = None
        self.key_priv = None

    def create_keys(self, nbits, dir_pem):
        """ 生成公钥和私钥 """
        if not os.path.exists(dir_pem):
            os.makedirs(dir_pem)
        self.path_pub = os.path.join(dir_pem, PUBKEY_FILE)
        self.path_priv = os.path.join(dir_pem, PRIVKEY_FILE)

        self.key_pub, self.key_priv = rsa.newkeys(nbits)

        bytes_pub = self.key_pub.save_pkcs1()
        with open(self.path_pub, 'wb') as fp:
            fp.write(bytes_pub)

        bytes_priv = self.key_priv.save_pkcs1()
        with open(self.path_priv, 'wb') as fp:
            fp.write(bytes_priv)

    def load_keys(self, dir_pem):
        if not os.path.exists(dir_pem):
            raise Exception("不存在目录【{}】".format(dir_pem))

        path_pub = os.path.join(dir_pem, PUBKEY_FILE)
        if os.path.exists(path_pub):
            self.path_pub = path_pub
            bytes_pub = self.get_pubkey()
            self.key_pub = rsa.PublicKey.load_pkcs1(bytes_pub)

        path_priv = os.path.join(dir_pem, PRIVKEY_FILE)
        if os.path.exists(path_priv):
            self.path_priv = path_priv
            bytes_priv = self._get_privkey()
            self.key_priv = rsa.PrivateKey.load_pkcs1(bytes_priv)

    def get_pubkey(self):
        with open(self.path_pub, "rb") as fp:
            bytes_pub = fp.read()
        return bytes_pub

    def _get_privkey(self):
        with open(self.path_priv, "rb") as fp:
            bytes_priv = fp.read()
        return bytes_priv

    def encrypt(self, text):
        """ 注意：每次加密生成的密文并不相同 """
        if isinstance(text, str):
            text = text.encode()
        bytes_crypt = rsa.encrypt(text, self.key_pub)
        return bytes_crypt

    def decrypt(self, crypt_text):
        """ 注意，这里返回的类型为bytes
            如解密失败，raise rsa.pkcs1.DecryptionError
        """
        bytes_text = rsa.decrypt(crypt_text, self.key_priv)
        # text = bytes_text.decode()
        return bytes_text

    def sign(self, message):
        if isinstance(message, str):
            message = message.encode()
        # 使用SHA-1方法进行签名（也可以使用MD5）
        signature = rsa.sign(message, self.key_priv, 'SHA-1')
        # 签名之后，需要转义后输出
        sign_base64 = base64.b64encode(signature)
        return sign_base64

    def verify(self, message: str, signature: bytes):
        if isinstance(message, str):
            message = message.encode()
        if isinstance(signature, str):
            signature = signature.encode()

        signature = base64.b64decode(signature)
        try:
            hash_method = rsa.verify(message, signature, self.key_pub)
            logger.debug("验证签证【{}】".format(hash_method))
            return True
        except rsa.pkcs1.VerificationError:
            return False


if __name__ == "__main__":
    text = "This is just a test!\nBye."

    crypto = RsaCrypto()
    crypto.load_keys("./pem")
    bytes_crypt = crypto.encrypt(text)
    print("密文：", bytes_crypt)
    bytes_text = crypto.decrypt(bytes_crypt)
    print("解密：", bytes_text.decode())

    signature = crypto.sign(text)
    print("签名：", signature)
    bool_ = crypto.verify(text, signature)
    print("验证签名：", bool_)
