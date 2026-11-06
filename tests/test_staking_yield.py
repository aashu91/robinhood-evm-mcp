import unittest

class TestStakingYieldMath(unittest.TestCase):
    """
    Validates proportional distribution math and emergency unstaking state transitions.
    """

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

    def test_reward_index_scaling_and_accumulation(self):
        scale = 10**18
        staked_a = 1000 * scale
        staked_b = 3000 * scale
        total_staked = staked_a + staked_b

        reward_deposit_1 = 1 * scale
        reward_index_1 = (reward_deposit_1 * scale) // total_staked

        user_a_pending_1 = (staked_a * reward_index_1) // scale
        user_b_pending_1 = (staked_b * reward_index_1) // scale

        self.assertEqual(user_a_pending_1, 250000000000000000)
        self.assertEqual(user_b_pending_1, 750000000000000000)
        self.assertEqual(user_a_pending_1 + user_b_pending_1, reward_deposit_1)

        reward_deposit_2 = 2 * scale
        reward_index_2 = reward_index_1 + (reward_deposit_2 * scale) // total_staked

        user_a_pending_2 = (staked_a * (reward_index_2 - reward_index_1)) // scale
        user_b_pending_total = (staked_b * reward_index_2) // scale

        self.assertEqual(user_a_pending_2, 500000000000000000)
        self.assertEqual(user_b_pending_total, 2250000000000000000)

    def test_zero_staked_deposit_handling(self):
        total_staked = 0
        reward_index = 0
        deposit_amount = 10**18
        if total_staked > 0:
            reward_index += (deposit_amount * 10**18) // total_staked
        self.assertEqual(reward_index, 0)

if __name__ == "__main__":
    unittest.main()
