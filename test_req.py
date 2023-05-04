import unittest
from concurrent.futures import ProcessPoolExecutor

import requests

executor = ProcessPoolExecutor()


class Tests(unittest.TestCase):

    def testReq(self):
        dtw = [23.38, 23.59, 25.23, 24.33, 24.41, 24.22, 23.89, 24.2, 23.96]
        dtw = [str(it) for it in dtw]
        resp = requests.get("http://127.0.0.1:5000/get_user_lvl", params={"lang": "en", "dtw": ",".join(dtw)},
                            headers={"Authorization": "as3sgs4s325rf2f32323"})
        print(resp.text)
