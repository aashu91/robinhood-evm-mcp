// compileStaking.cjs
// Node.js script to compile StakingYield.sol using the native JS Solidity compiler

const path = require('path');
const fs = require('fs');
const solc = require('solc');

const contractPath = path.resolve(__dirname, 'contracts', 'StakingYield.sol');
if (!fs.existsSync(contractPath)) {
    console.error("Contract file not found at:", contractPath);
    process.exit(1);
}

const source = fs.readFileSync(contractPath, 'utf8');

const input = {
    language: 'Solidity',
    sources: {
        'StakingYield.sol': {
            content: source
        }
    },
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

console.log("Compiling contracts/StakingYield.sol... This might take a few seconds.");
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
    console.error("Failed to extract contract artifacts from compiler output.");
    process.exit(1);
}
