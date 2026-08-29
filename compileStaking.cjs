// compileStaking.cjs
// Node.js script to compile StakingYield.sol and EcosystemTreasury.sol using solc

const path = require('path');
const fs = require('fs');
const solc = require('solc');

const stakingPath = path.resolve(__dirname, 'contracts', 'StakingYield.sol');
const treasuryPath = path.resolve(__dirname, 'contracts', 'EcosystemTreasury.sol');

if (!fs.existsSync(stakingPath)) {
    console.error("Contract file not found at:", stakingPath);
    process.exit(1);
}

const stakingSource = fs.readFileSync(stakingPath, 'utf8');
const treasurySource = fs.existsSync(treasuryPath) ? fs.readFileSync(treasuryPath, 'utf8') : null;

const sources = {
    'StakingYield.sol': {
        content: stakingSource
    }
};

if (treasurySource) {
    sources['EcosystemTreasury.sol'] = {
        content: treasurySource
    };
}

const input = {
    language: 'Solidity',
    sources: sources,
    settings: {
        optimizer: {
            enabled: true,
            runs: 200
        },
        outputSelection: {
            '*': {
                '*': ['abi', 'evm.bytecode']
            }
        }
    }
};

console.log("Compiling contracts/StakingYield.sol...");
const output = JSON.parse(solc.compile(JSON.stringify(input)));

let hasErrors = false;
if (output.errors) {
    output.errors.forEach(err => {
        if (err.severity === 'error') {
            console.error("Error:", err.formattedMessage);
            hasErrors = true;
        } else {
            console.log("Warning:", err.formattedMessage);
        }
    });
}

if (hasErrors) {
    console.error("Compilation failed due to errors.");
    process.exit(1);
}

const stakingContract = output.contracts['StakingYield.sol']['StakingYield'];

if (stakingContract) {
    fs.writeFileSync(path.resolve(__dirname, 'StakingYield.json'), JSON.stringify({
        abi: stakingContract.abi,
        bytecode: stakingContract.evm.bytecode.object
    }, null, 2));
    
    console.log("✅ Successfully compiled contracts/StakingYield.sol!");
    console.log("Saved compilation output to StakingYield.json");
} else {
    console.error("Failed to extract StakingYield artifacts from compiler output.");
    process.exit(1);
}

if (sources['EcosystemTreasury.sol']) {
    const treasuryContract = output.contracts['EcosystemTreasury.sol']['EcosystemTreasury'];
    if (treasuryContract) {
        fs.writeFileSync(path.resolve(__dirname, 'EcosystemTreasury.json'), JSON.stringify({
            abi: treasuryContract.abi,
            bytecode: treasuryContract.evm.bytecode.object
        }, null, 2));
        console.log("✅ Successfully compiled contracts/EcosystemTreasury.sol!");
        console.log("Saved compilation output to EcosystemTreasury.json");
    }
}
