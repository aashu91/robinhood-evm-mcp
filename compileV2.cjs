// compileV2.cjs
// Node.js script to compile MemeFactoryV2.sol using the native JS Solidity compiler

const path = require('path');
const fs = require('fs');
const solc = require('solc');

const contractPath = path.resolve(__dirname, 'contracts', 'MemeFactoryV2.sol');
if (!fs.existsSync(contractPath)) {
    console.error("Contract file not found at:", contractPath);
    process.exit(1);
}

const source = fs.readFileSync(contractPath, 'utf8');

const input = {
    language: 'Solidity',
    sources: {
        'MemeFactoryV2.sol': {
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

console.log("Compiling contracts/MemeFactoryV2.sol... This might take a few seconds.");
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

const factoryContract = output.contracts['MemeFactoryV2.sol']['MemeFactoryV2'];
const tokenContract = output.contracts['MemeFactoryV2.sol']['MemeToken'];

if (factoryContract && tokenContract) {
    fs.writeFileSync(path.resolve(__dirname, 'MemeFactoryV2.json'), JSON.stringify({
        abi: factoryContract.abi,
        bytecode: factoryContract.evm.bytecode.object
    }, null, 2));
    
    console.log("✅ Successfully compiled contracts/MemeFactoryV2.sol!");
    console.log("Saved compilation outputs to MemeFactoryV2.json");
} else {
    console.error("Failed to extract contract artifacts from compiler output.");
    process.exit(1);
}
