import unittest
from concurrent.futures import ProcessPoolExecutor

import requests

executor = ProcessPoolExecutor()


class Tests(unittest.TestCase):

    def testReq(self):
        dtw = [11, 12, 14, 15.2]
        dtw = [str(it) for it in dtw]
        resp = requests.get("http://127.0.0.1:5000/get_user_lvl", params={"lang": "en", "dtw": ",".join(dtw)},
                            headers={"Authorization": "as3sgs4s325rf2f32323"})
        print(resp.text)
