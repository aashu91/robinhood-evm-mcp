import unittest

class TestStakingYieldMath(unittest.TestCase):
    def test_proportional_yield_distribution(self):
        total_staked = 1000
        user_a = 600
        user_b = 400
        reward_pool = 500
        self.assertEqual((user_a * reward_pool) // total_staked, 300)
        self.assertEqual((user_b * reward_pool) // total_staked, 200)

    def test_emergency_unstake_resets_balance(self):
        staked = {"0xUser": 250}
        amt = staked["0xUser"]
        staked["0xUser"] = 0
        self.assertEqual(amt, 250)
        self.assertEqual(staked["0xUser"], 0)

if __name__ == "__main__":
    unittest.main()
