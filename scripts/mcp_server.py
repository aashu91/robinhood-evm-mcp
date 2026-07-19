from web3_helper import *

def main():
    account = '0xYourAccountAddress'
    
    # Stake tokens
    print("Staking tokens...")
    receipt = stake_tokens(account, 1000000000000000000)  # 1 token
    print(f"Staked: {receipt}")
    
    # Unstake tokens
    print("Unstaking tokens...")
    receipt = unstake_tokens(account, 1000000000000000000)  # 1 token
    print(f"Unstaked: {receipt}")
    
    # Claim rewards
    print("Claiming rewards...")
    receipt = claim_rewards(account)
    print(f"Rewards claimed: {receipt}")
    
    # Get staking info
    staked_amount, pending_rewards, total_staked = get_staking_info(account)
    print(f"Staked Amount: {staked_amount}")
    print(f"Pending Rewards: {pending_rewards}")
    print(f"Total Staked: {total_staked}")

if __name__ == "__main__":
    main()
