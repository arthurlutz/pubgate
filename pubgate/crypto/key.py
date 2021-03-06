import os
import re
import base64
from Crypto.PublicKey import RSA
from Crypto.Util import number
from typing import Any
from typing import Dict
from typing import Optional

from pubgate import KEY_DIR


class Key(object):
    DEFAULT_KEY_SIZE = 2048

    def __init__(self, owner: str) -> None:
        self.owner = owner
        self.privkey_pem: Optional[str] = None
        self.pubkey_pem: Optional[str] = None
        self.privkey: Optional[Any] = None
        self.pubkey: Optional[Any] = None

    def load_pub(self, pubkey_pem: str) -> None:
        self.pubkey_pem = pubkey_pem
        self.pubkey = RSA.importKey(pubkey_pem)

    def load(self, privkey_pem: str) -> None:
        self.privkey_pem = privkey_pem
        self.privkey = RSA.importKey(self.privkey_pem)
        self.pubkey_pem = self.privkey.publickey().exportKey("PEM").decode("utf-8")

    def new(self) -> None:
        k = RSA.generate(self.DEFAULT_KEY_SIZE)
        self.privkey_pem = k.exportKey("PEM").decode("utf-8")
        self.pubkey_pem = k.publickey().exportKey("PEM").decode("utf-8")
        self.privkey = k

    def key_id(self) -> str:
        return f"{self.owner}#main-key"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.key_id(),
            "owner": self.owner,
            "publicKeyPem": self.pubkey_pem,
        }

    def to_magic_key(self) -> str:
        mod = base64.urlsafe_b64encode(
            number.long_to_bytes(self.privkey.n)  # type: ignore
        ).decode("utf-8")
        pubexp = base64.urlsafe_b64encode(
            number.long_to_bytes(self.privkey.e)  # type: ignore
        ).decode("utf-8")
        return f"data:application/magic-public-key,RSA.{mod}.{pubexp}"


def get_key(owner: str) -> Key:
    """"Loads or generates an RSA key."""
    k = Key(owner)
    user = re.sub('[^\w\d]', "_", owner)
    key_path = os.path.join(KEY_DIR, f"key_{user}.pem")
    if os.path.isfile(key_path):
        with open(key_path) as f:
            privkey_pem = f.read()
            k.load(privkey_pem)
    else:
        k.new()
        with open(key_path, "w") as f:
            f.write(k.privkey_pem)

    return k



