# compile.py
import os
import json
from solcx import compile_source, install_solc,set_solc_version

# Install the specific version of Solidity compiler
install_solc('0.8.20')
set_solc_version('0.8.20')
# Path to the contract
contract_path = os.path.join(os.path.dirname(__file__), 'contracts', 'HealthRecords.sol')

# Read contract source code
with open(contract_path, 'r') as file:
    source_code = file.read()

# Compile contract
compiled_sol = compile_source(source_code)
contract_interface = compiled_sol['<stdin>:HealthRecords']

# Save ABI and bytecode
with open('contract_data.json', 'w') as f:
    json.dump({
        'abi': contract_interface['abi'],
        'bytecode': contract_interface['bin']
    }, f)

print("Contract compiled successfully!")
