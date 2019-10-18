import pandas as pd
import sys
sys.path.append('../src')
import unittest
import gensimwine

class TestCreateTheta(unittest.TestCase):
    def test_create_theta(self):
        self.assertEqual(gensimwine.create_theta_matrix([[(2, 0.88), (3, 0.07)],[(0, 0.88), (1, 0.073)]],4), \
                                pd.DataFrame([{'0':0, '1':0, '2':0.88, '3':0.07}, {'0':0.88, '1':0.073, '2':0, '3':0}]))

if __name__ == '__main__':
    unittest.main()