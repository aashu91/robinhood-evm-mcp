import React, { useState, useEffect } from'react';
import { ethers } from 'ethers';

const Staking = () => {
    const [stakedAmount, setStakedAmount] = useState(0);
    const [pendingRewards, setPendingRewards] = useState(0);
    const [totalStaked, setTotalStaked] = useState(0);
    const [apy, setApy] = useState(0);
    const [amount, setAmount] = useState('');

    useEffect(() => {
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        const signer = provider.getSigner();
        const contract = new ethers.Contract(contractAddress, abi, signer);

        const fetchStakingInfo = async () => {
            const [staked, pending, total] = await contract.getStakingInfo(signer._address);
            setStakedAmount(staked.toString());
            setPendingRewards(pending.toString());
            setTotalStaked(total.toString());

            // Calculate APY (example calculation, adjust as needed)
            const blocksPerYear = 365 * 24 * 60 * 60 / 15; // Assuming 15 seconds per block
            const annualRewards = (parseInt(pending) * blocksPerYear) / (block.number - lastRewardBlock);
            const apyValue = (annualRewards / parseInt(staked)) * 100;
            setApy(apyValue.toFixed(2));
        };

        fetchStakingInfo();
    }, []);

    const stakeTokens = async () => {
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        const signer = provider.getSigner();
        const contract = new ethers.Contract(contractAddress, abi, signer);

        const tx = await contract.stake(ethers.utils.parseEther(amount));
        await tx.wait();
        setAmount('');
    };

    const unstakeTokens = async () => {
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        const signer = provider.getSigner();
        const contract = new ethers.Contract(contractAddress, abi, signer);

        const tx = await contract.unstake(ethers.utils.parseEther(amount));
        await tx.wait();
        setAmount('');
    };

    const claimRewards = async () => {
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        const signer = provider.getSigner();
        const contract = new ethers.Contract(contractAddress, abi, signer);

        const tx = await contract.claimRewards();
        await tx.wait();
    };

    return (
        <div>
            <h1>Staking Interface</h1>
            <p>APY: {apy}%</p>
            <p>Total Staked: {ethers.utils.formatEther(totalStaked)}</p>
            <p>Your Staked Amount: {ethers.utils.formatEther(stakedAmount)}</p>
            <p>Pending Rewards: {ethers.utils.formatEther(pendingRewards)}</p>
            <input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
            <button onClick={stakeTokens}>Stake</button>
            <button onClick={unstakeTokens}>Unstake</button>
            <button onClick={claimRewards}>Claim Rewards</button>
        </div>
    );
};

export default Staking;
