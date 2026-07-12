import sys
import os

if getattr(sys, "frozen", False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(__file__)

cert_path = os.path.join(base_dir, "certifi", "cacert.pem")

class FakeCertifi:
    @staticmethod
    def where():
        return cert_path

sys.modules["certifi"] = FakeCertifi()

import requests

print("OK")