// compileTrust.cjs
// Node.js script to compile CommunityTrust.sol and MockAsset.sol using the native JS Solidity compiler

const path = require('path');
const fs = require('fs');
const solc = require('solc');

const trustPath = path.resolve(__dirname, 'contracts', 'CommunityTrust.sol');
const mockAssetPath = path.resolve(__dirname, 'contracts', 'MockAsset.sol');

if (!fs.existsSync(trustPath) || !fs.existsSync(mockAssetPath)) {
    console.error("Contract files not found!");
    process.exit(1);
}

const trustSource = fs.readFileSync(trustPath, 'utf8');
const mockAssetSource = fs.readFileSync(mockAssetPath, 'utf8');

const input = {
    language: 'Solidity',
    sources: {
        'CommunityTrust.sol': {
            content: trustSource
        },
        'MockAsset.sol': {
            content: mockAssetSource
        }
    },
    settings: {
        outputSelection: {
            '*': {
                '*': ['abi', 'evm.bytecode']
            }
        }
    }
};

console.log("Compiling CommunityTrust.sol and MockAsset.sol... This might take a few seconds.");
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

const communityTrust = output.contracts['CommunityTrust.sol']['CommunityTrust'];
const communityTrustFactory = output.contracts['CommunityTrust.sol']['CommunityTrustFactory'];
const mockAsset = output.contracts['MockAsset.sol']['MockAsset'];

if (communityTrust && communityTrustFactory && mockAsset) {
    fs.writeFileSync(path.resolve(__dirname, 'CommunityTrust.json'), JSON.stringify({
        abi: communityTrust.abi,
        bytecode: communityTrust.evm.bytecode.object
    }, null, 2));

    fs.writeFileSync(path.resolve(__dirname, 'CommunityTrustFactory.json'), JSON.stringify({
        abi: communityTrustFactory.abi,
        bytecode: communityTrustFactory.evm.bytecode.object
    }, null, 2));

    fs.writeFileSync(path.resolve(__dirname, 'MockAsset.json'), JSON.stringify({
        abi: mockAsset.abi,
        bytecode: mockAsset.evm.bytecode.object
    }, null, 2));
    
    console.log("✅ Successfully compiled CommunityTrust.sol and MockAsset.sol!");
    console.log("Saved compilation outputs to JSON files.");
} else {
    console.error("Failed to extract contract artifacts.");
    process.exit(1);
}
