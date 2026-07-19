const web3 = new Web3(window.web3.currentProvider);
const contractABI = JSON.parse(document.getElementById('contract-abi').textContent);
const contractAddress = '0xYourContractAddress';
const contract = new web3.eth.Contract(contractABI, contractAddress);

document.getElementById('stake-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const amount = document.getElementById('stake-amount').value;
    await stakeTokens(amount);
});

document.getElementById('unstake-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const amount = document.getElementById('unstake-amount').value;
    await unstakeTokens(amount);
});

document.getElementById('claim-rewards').addEventListener('click', async () => {
    await claimRewards();
});

async function stakeTokens(amount) {
    const accounts = await web3.eth.getAccounts();
    const tx = contract.methods.stake(web3.utils.toWei(amount, 'ether'));
    await tx.send({ from: accounts[0] });
    updateStakingInfo();
}

async function unstakeTokens(amount) {
    const accounts = await web3.eth.getAccounts();
    const tx = contract.methods.unstake(web3.utils.toWei(amount, 'ether'));
    await tx.send({ from: accounts[0] });
    updateStakingInfo();
}

async function claimRewards() {
    const accounts = await web3.eth.getAccounts();
    const tx = contract.methods.claimRewards();
    await tx.send({ from: accounts[0] });
    updateStakingInfo();
}

async function updateStakingInfo() {
    const accounts = await web3.eth.getAccounts();
    const [stakedAmount, pendingRewards, totalStaked] = await contract.methods.getStakingInfo(accounts[0]).call();
    document.getElementById('your-staked-amount').textContent = web3.utils.fromWei(stakedAmount, 'ether');
    document.getElementById('pending-rewards').textContent = web3.utils.fromWei(pendingRewards, 'ether');
    document.getElementById('total-staked').textContent = web3.utils.fromWei(totalStaked, 'ether');
}

window.addEventListener('load', async () => {
    await updateStakingInfo();
});
