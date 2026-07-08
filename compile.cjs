// compile.cjs
// Node.js script to compile MemeFactory.sol using the native JS Solidity compiler

const path = require('path');
const fs = require('fs');
const solc = require('solc');

const contractPath = path.resolve(__dirname, 'contracts', 'MemeFactory.sol');
if (!fs.existsSync(contractPath)) {
    console.error("Contract file not found at:", contractPath);
    process.exit(1);
}

const source = fs.readFileSync(contractPath, 'utf8');

const input = {
    language: 'Solidity',
    sources: {
        'MemeFactory.sol': {
            content: source
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

console.log("Compiling contracts/MemeFactory.sol... This might take a few seconds.");
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

const factoryContract = output.contracts['MemeFactory.sol']['MemeFactory'];
const tokenContract = output.contracts['MemeFactory.sol']['MemeToken'];

if (factoryContract && tokenContract) {
    fs.writeFileSync(path.resolve(__dirname, 'MemeFactory.json'), JSON.stringify({
        abi: factoryContract.abi,
        bytecode: factoryContract.evm.bytecode.object
    }, null, 2));
    
    fs.writeFileSync(path.resolve(__dirname, 'MemeToken.json'), JSON.stringify({
        abi: tokenContract.abi,
        bytecode: tokenContract.evm.bytecode.object
    }, null, 2));
    
    console.log("✅ Successfully compiled contracts/MemeFactory.sol!");
    console.log("Saved compilation outputs to MemeFactory.json and MemeToken.json");
} else {
    console.error("Failed to extract contract artifacts from compiler output.");
    process.exit(1);
}
