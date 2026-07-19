from web3_helper import *

def main():
    contract_address = '0xYourContractAddress'
    abi_file = 'StakingYield.abi.json'
    abi = load_contract_abi(abi_file)
    contract = get_contract_instance(contract_address, abi)

    account = '0xYourAccountAddress'
    private_key = 'YourPrivateKey'

    # Example usage
    print("Staking 100 tokens...")
    stake_tokens(contract, 100, account)
    print("Unstaking 50 tokens...")
    unstake_tokens(contract, 50, account)
    print("Claiming rewards...")
    claim_rewards(contract, account)
    print("Getting staking info...")
    staking_info = get_staking_info(contract, account)
    print(f"Staked: {staking_info[0]}, Pending Rewards: {staking_info[1]}, Total Staked: {staking_info[2]}")

if __name__ == "__main__":
    main()
