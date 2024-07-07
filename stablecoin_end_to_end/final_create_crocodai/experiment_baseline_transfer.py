from solcx import compile_standard, install_solc
import json
import os
from web3 import Web3

private_keys = [
    "0d9fb7ddd8a2e3c19b9c57166f6dce352c5c021fe79e6dd9654b3adfbfbaad26",
    "74e853dc72b18efb576929ccc84903c0d5044ee2445661e884033bf69eec2638",
    "d14fa190b8cbd656fa4f8fe9acbe531cc19ed8b80a39f1e40205816885f80753",
    "05f6739e9a66796ddb57310f2142b0534d10937a22475f744994ffc76953ce70",
    "9620e18cde7eae53c810ec7a80fd49e5b418dba6870958ed4f2ed15f2479022f",
    "57bee8409f420f3e8e7f1993b64f27fd6bc03368db749956550932304502a884",
    "0b087981241722083ebf113ef6d062f0b8af82c593cb92e3b3612ee54a2cece9",
    "dd45d7f2ce48c6aa6a61989eeac6ee744f371054ae89a1dc4982fe12a0d222ab",
    "1ae07aee2dede3a67e0f2e193e49481819d8701d9830e19bb57812c831ba963f",
    "f148c3fbdc45fa2554a97e7498b6112ab04ceeef87debb61b6624ce7fdee2e05",
    "d1ee0eadf33442ed9c61b6da201975d473dc0e019c172024caf6945040f78792",
    "a0fc20c4cb3b197716e42e4062a8a8e01cc5dd6759fe728fc2c5880a3573e494",
    "e000975a7ba4b2c010d0e98850632b1510cd7858a2db0ef9019370cce7cff5ce",
    "3855a3046094b021b0710e1d9ae3987f82d91837ba326c698ac172d57a5c8e83",
    "7a169b606afaccdccc397e49a44d56a68a2cfbb7f8f544376658554409121728",
    "249705240d48de99e7272441057c93559fe0663538f7385a0581a1936310a939",
]

# sig_dir = "C:/Users/dani3/Dropbox/utwente backup/research/programmatuur/rust/multi-party-ecdsa/target/release/examples/";

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

install_solc("0.8.18")

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
node_address = w3.eth.accounts[0]
node_private_key = private_keys[0]

wrapped_basecoin_id = bytearray(map(ord, "BSCN"))
wrapped_basecoin_id.extend(bytearray(28))

line_bytes = bytearray(map(ord, "line"))
line_bytes.extend(bytearray(28))

Line_bytes = bytearray(map(ord, "Line"))
Line_bytes.extend(bytearray(28))

spot_bytes = bytearray(map(ord, "spot"))
spot_bytes.extend(bytearray(28))

###################
### DEPLOY COIN ###
###################

with open(os.path.join(__location__, "Coin.sol"), "r") as file:
    coin_contract_file = file.read()

compiled_coin_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Coin.sol": {"content": coin_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_coin_sol, file)

## get bytecode
coin_bytecode = compiled_coin_sol["contracts"]["Coin.sol"]["Coin"]["evm"][
    "bytecode"
]["object"]

# ## get abi
coin_abi = json.loads(
    compiled_coin_sol["contracts"]["Coin.sol"]["Coin"]["metadata"]
)["output"]["abi"]

# create the contract in Python
coin_contract = w3.eth.contract(abi=coin_abi, bytecode=coin_bytecode)
# get the latest transaction
coin_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_coin_transaction = coin_contract.constructor(chain_id).build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": coin_nonce}
)

# sign the transaction
signed_deploy_coin_transaction = w3.eth.account.sign_transaction(deploy_coin_transaction, private_key=node_private_key)
print(f"Start Deploying Coin Contract!")
# send the transaction
deploy_coin_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_coin_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_coin_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_coin_transaction_hash)
coin_address = deploy_coin_transaction_receipt.contractAddress
print(f"Done! Contract Coin deployed to {coin_address}")

deployed_coin_contract = w3.eth.contract(coin_address, abi=coin_abi)

#######################
### DEPLOY BASECOIN ###
#######################

with open(os.path.join(__location__, "ERC20.sol"), "r") as file:
    basecoin_contract_file = file.read()

compiled_basecoin_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ERC20.sol": {"content": basecoin_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_basecoin_sol, file)

## get bytecode
basecoin_bytecode = compiled_basecoin_sol["contracts"]["ERC20.sol"]["ERC20"]["evm"][
    "bytecode"
]["object"]

# ## get abi
basecoin_abi = json.loads(
    compiled_basecoin_sol["contracts"]["ERC20.sol"]["ERC20"]["metadata"]
)["output"]["abi"]

# create the contract in Python
basecoin_contract = w3.eth.contract(abi=basecoin_abi, bytecode=basecoin_bytecode)
# get the latest transaction
basecoin_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_basecoin_transaction = basecoin_contract.constructor("BaseCoin","BSCN").build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": basecoin_nonce}
)

# sign the transaction
signed_deploy_basecoin_transaction = w3.eth.account.sign_transaction(deploy_basecoin_transaction, private_key=node_private_key)
print(f"Start Deploying BaseCoin Contract!")
# send the transaction
deploy_basecoin_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_basecoin_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_basecoin_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_basecoin_transaction_hash)
basecoin_address = deploy_basecoin_transaction_receipt.contractAddress
print(f"Done! Contract BaseCoin deployed to {basecoin_address}")

deployed_basecoin_contract = w3.eth.contract(basecoin_address, abi=basecoin_abi)

###############################
### DEPLOY WRAPPED BASECOIN ###
###############################

with open(os.path.join(__location__, "ERC20.sol"), "r") as file:
    wrapped_basecoin_contract_file = file.read()

compiled_wrapped_basecoin_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ERC20.sol": {"content": wrapped_basecoin_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_wrapped_basecoin_sol, file)

## get bytecode
wrapped_basecoin_bytecode = compiled_wrapped_basecoin_sol["contracts"]["ERC20.sol"]["ERC20"]["evm"][
    "bytecode"
]["object"]

# ## get abi
wrapped_basecoin_abi = json.loads(
    compiled_wrapped_basecoin_sol["contracts"]["ERC20.sol"]["ERC20"]["metadata"]
)["output"]["abi"]

# create the contract in Python
wrapped_basecoin_contract = w3.eth.contract(abi=wrapped_basecoin_abi, bytecode=wrapped_basecoin_bytecode)
# get the latest transaction
wrapped_basecoin_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_wrapped_basecoin_transaction = wrapped_basecoin_contract.constructor("Wrapped BaseCoin","WBSN").build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": wrapped_basecoin_nonce}
)

# sign the transaction
signed_deploy_wrapped_basecoin_transaction = w3.eth.account.sign_transaction(deploy_wrapped_basecoin_transaction, private_key=node_private_key)
print(f"Start Deploying Wrapped BaseCoin Contract!")
# send the transaction
deploy_wrapped_basecoin_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_wrapped_basecoin_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_wrapped_basecoin_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_wrapped_basecoin_transaction_hash)
wrapped_basecoin_address = deploy_wrapped_basecoin_transaction_receipt.contractAddress
print(f"Done! Contract Wrapped BaseCoin deployed to {wrapped_basecoin_address}")

deployed_wrapped_basecoin_contract = w3.eth.contract(wrapped_basecoin_address, abi=wrapped_basecoin_abi)

#################################
### DEPLOY WRAPPED STABLECOIN ###
#################################

with open(os.path.join(__location__, "ERC20.sol"), "r") as file:
    wrapped_stablecoin_contract_file = file.read()

compiled_wrapped_stablecoin_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ERC20.sol": {"content": wrapped_stablecoin_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_wrapped_stablecoin_sol, file)

## get bytecode
wrapped_stablecoin_bytecode = compiled_wrapped_stablecoin_sol["contracts"]["ERC20.sol"]["ERC20"]["evm"][
    "bytecode"
]["object"]

# ## get abi
wrapped_stablecoin_abi = json.loads(
    compiled_wrapped_stablecoin_sol["contracts"]["ERC20.sol"]["ERC20"]["metadata"]
)["output"]["abi"]

# create the contract in Python
wrapped_stablecoin_contract = w3.eth.contract(abi=wrapped_stablecoin_abi, bytecode=wrapped_stablecoin_bytecode)
# get the latest transaction
wrapped_stablecoin_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_wrapped_stablecoin_transaction = wrapped_stablecoin_contract.constructor("Wrapped Stablecoin","WDAI").build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": wrapped_stablecoin_nonce}
)

# sign the transaction
signed_deploy_wrapped_stablecoin_transaction = w3.eth.account.sign_transaction(deploy_wrapped_stablecoin_transaction, private_key=node_private_key)
print(f"Start Deploying Wrapped Stablecoin Contract!")
# send the transaction
deploy_wrapped_stablecoin_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_wrapped_stablecoin_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_wrapped_stablecoin_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_wrapped_stablecoin_transaction_hash)
wrapped_stablecoin_address = deploy_wrapped_stablecoin_transaction_receipt.contractAddress
print(f"Done! Contract Wrapped Stablecoin deployed to {wrapped_stablecoin_address}")

deployed_wrapped_stablecoin_contract = w3.eth.contract(wrapped_stablecoin_address, abi=wrapped_stablecoin_abi)

##################################################
### DEPLOY WRAPPED STABLECOIN 2 (SECOND CHAIN) ###
##################################################

with open(os.path.join(__location__, "ERC20.sol"), "r") as file:
    wrapped_stablecoin_2_contract_file = file.read()

compiled_wrapped_stablecoin_2_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ERC20.sol": {"content": wrapped_stablecoin_2_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_wrapped_stablecoin_2_sol, file)

## get bytecode
wrapped_stablecoin_2_bytecode = compiled_wrapped_stablecoin_2_sol["contracts"]["ERC20.sol"]["ERC20"]["evm"][
    "bytecode"
]["object"]

# ## get abi
wrapped_stablecoin_2_abi = json.loads(
    compiled_wrapped_stablecoin_2_sol["contracts"]["ERC20.sol"]["ERC20"]["metadata"]
)["output"]["abi"]

# create the contract in Python
wrapped_stablecoin_2_contract = w3.eth.contract(abi=wrapped_stablecoin_2_abi, bytecode=wrapped_stablecoin_2_bytecode)
# get the latest transaction
wrapped_stablecoin_2_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_wrapped_stablecoin_2_transaction = wrapped_stablecoin_2_contract.constructor("Wrapped Stablecoin","WDAI").build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": wrapped_stablecoin_2_nonce}
)

# sign the transaction
signed_deploy_wrapped_stablecoin_2_transaction = w3.eth.account.sign_transaction(deploy_wrapped_stablecoin_2_transaction, private_key=node_private_key)
print(f"Start Deploying Wrapped Stablecoin Contract!")
# send the transaction
deploy_wrapped_stablecoin_2_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_wrapped_stablecoin_2_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_wrapped_stablecoin_2_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_wrapped_stablecoin_2_transaction_hash)
wrapped_stablecoin_2_address = deploy_wrapped_stablecoin_2_transaction_receipt.contractAddress
print(f"Done! Contract Wrapped Stablecoin deployed to {wrapped_stablecoin_2_address}")

deployed_wrapped_stablecoin_2_contract = w3.eth.contract(wrapped_stablecoin_2_address, abi=wrapped_stablecoin_2_abi)

##########################
### DEPLOY VAULT (VAT) ###
##########################

with open(os.path.join(__location__, "Vat.sol"), "r") as file:
    vat_contract_file = file.read()

compiled_vat_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Vat.sol": {"content": vat_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_vat_sol, file)

## get bytecode
vat_bytecode = compiled_vat_sol["contracts"]["Vat.sol"]["Vat"]["evm"][
    "bytecode"
]["object"]

# ## get abi
vat_abi = json.loads(
    compiled_vat_sol["contracts"]["Vat.sol"]["Vat"]["metadata"]
)["output"]["abi"]

# create the contract in Python
vat_contract = w3.eth.contract(abi=vat_abi, bytecode=vat_bytecode)
# get the latest transaction
vat_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_vat_transaction = vat_contract.constructor().build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": vat_nonce}
)

# sign the transaction
signed_deploy_vat_transaction = w3.eth.account.sign_transaction(deploy_vat_transaction, private_key=node_private_key)
print(f"Start Deploying Vat Contract!")
# send the transaction
deploy_vat_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_vat_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_vat_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_vat_transaction_hash)
vat_address = deploy_vat_transaction_receipt.contractAddress
print(f"Done! Contract Vat deployed to {vat_address}")

deployed_vat_contract = w3.eth.contract(vat_address, abi=vat_abi)

##############################
### DEPLOY VAULT (GEMJOIN) ###
##############################

with open(os.path.join(__location__, "Join.sol"), "r") as file:
    gemjoin_contract_file = file.read()

compiled_gemjoin_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Join.sol": {"content": gemjoin_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_gemjoin_sol, file)

## get bytecode
gemjoin_bytecode = compiled_gemjoin_sol["contracts"]["Join.sol"]["GemJoin"]["evm"][
    "bytecode"
]["object"]

# ## get abi
gemjoin_abi = json.loads(
    compiled_gemjoin_sol["contracts"]["Join.sol"]["GemJoin"]["metadata"]
)["output"]["abi"]

# create the contract in Python
gemjoin_contract = w3.eth.contract(abi=gemjoin_abi, bytecode=gemjoin_bytecode)
# get the latest transaction
gemjoin_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_gemjoin_transaction = gemjoin_contract.constructor(vat_address,wrapped_basecoin_id,wrapped_basecoin_address).build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": gemjoin_nonce}
)

# sign the transaction
signed_deploy_gemjoin_transaction = w3.eth.account.sign_transaction(deploy_gemjoin_transaction, private_key=node_private_key)
print(f"Start Deploying GemJoin Contract!")
# send the transaction
deploy_gemjoin_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_gemjoin_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_gemjoin_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_gemjoin_transaction_hash)
gemjoin_address = deploy_gemjoin_transaction_receipt.contractAddress
print(f"Done! Contract GemJoin deployed to {gemjoin_address}")

deployed_gemjoin_contract = w3.eth.contract(gemjoin_address, abi=gemjoin_abi)

##############################
### DEPLOY VAULT (DAIJOIN) ###
##############################

with open(os.path.join(__location__, "Join.sol"), "r") as file:
    daijoin_contract_file = file.read()

compiled_daijoin_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Join.sol": {"content": daijoin_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_daijoin_sol, file)

## get bytecode
daijoin_bytecode = compiled_daijoin_sol["contracts"]["Join.sol"]["DaiJoin"]["evm"][
    "bytecode"
]["object"]

# ## get abi
daijoin_abi = json.loads(
    compiled_daijoin_sol["contracts"]["Join.sol"]["DaiJoin"]["metadata"]
)["output"]["abi"]

# create the contract in Python
daijoin_contract = w3.eth.contract(abi=daijoin_abi, bytecode=daijoin_bytecode)
# get the latest transaction
daijoin_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_daijoin_transaction = daijoin_contract.constructor(vat_address,coin_address).build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": daijoin_nonce}
)

# sign the transaction
signed_deploy_daijoin_transaction = w3.eth.account.sign_transaction(deploy_daijoin_transaction, private_key=node_private_key)
print(f"Start Deploying DaiJoin Contract!")
# send the transaction
deploy_daijoin_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_daijoin_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_daijoin_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_daijoin_transaction_hash)
daijoin_address = deploy_daijoin_transaction_receipt.contractAddress
print(f"Done! Contract DaiJoin deployed to {daijoin_address}")

deployed_daijoin_contract = w3.eth.contract(daijoin_address, abi=daijoin_abi)


################################
### DEPLOY BRIDGE (BASECOIN) ###
################################

with open(os.path.join(__location__, "Bridge.sol"), "r") as file:
    basecoin_bridge_contract_file = file.read()

compiled_basecoin_bridge_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Bridge.sol": {"content": basecoin_bridge_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_basecoin_bridge_sol, file)

## get bytecode
basecoin_bridge_bytecode = compiled_basecoin_bridge_sol["contracts"]["Bridge.sol"]["Bridge"]["evm"][
    "bytecode"
]["object"]

# ## get abi
basecoin_bridge_abi = json.loads(
    compiled_basecoin_bridge_sol["contracts"]["Bridge.sol"]["Bridge"]["metadata"]
)["output"]["abi"]

# create the contract in Python
basecoin_bridge_contract = w3.eth.contract(abi=basecoin_bridge_abi, bytecode=basecoin_bridge_bytecode)
# get the latest transaction
basecoin_bridge_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_basecoin_bridge_transaction = basecoin_bridge_contract.constructor("BaseCoin", "BSCN", basecoin_address).build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": basecoin_bridge_nonce}
)

# sign the transaction
signed_deploy_basecoin_bridge_transaction = w3.eth.account.sign_transaction(deploy_basecoin_bridge_transaction, private_key=node_private_key)
print(f"Start Deploying BaseCoin Bridge Contract!")
# send the transaction
deploy_basecoin_bridge_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_basecoin_bridge_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_basecoin_bridge_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_basecoin_bridge_transaction_hash)
basecoin_bridge_address = deploy_basecoin_bridge_transaction_receipt.contractAddress
print(f"Done! Contract BaseCoin Bridge deployed to {basecoin_bridge_address}")

deployed_basecoin_bridge_contract = w3.eth.contract(basecoin_bridge_address, abi=basecoin_bridge_abi)

################################
### DEPLOY BRIDGE (DAI) ###
################################

with open(os.path.join(__location__, "Bridge.sol"), "r") as file:
    dai_bridge_contract_file = file.read()

compiled_dai_bridge_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Bridge.sol": {"content": dai_bridge_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_dai_bridge_sol, file)

## get bytecode
dai_bridge_bytecode = compiled_dai_bridge_sol["contracts"]["Bridge.sol"]["Bridge"]["evm"][
    "bytecode"
]["object"]

# ## get abi
dai_bridge_abi = json.loads(
    compiled_dai_bridge_sol["contracts"]["Bridge.sol"]["Bridge"]["metadata"]
)["output"]["abi"]

# create the contract in Python
dai_bridge_contract = w3.eth.contract(abi=dai_bridge_abi, bytecode=dai_bridge_bytecode)
# get the latest transaction
dai_bridge_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_dai_bridge_transaction = dai_bridge_contract.constructor("BaseCoin", "BSCN", coin_address).build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": dai_bridge_nonce}
)

# sign the transaction
signed_deploy_dai_bridge_transaction = w3.eth.account.sign_transaction(deploy_dai_bridge_transaction, private_key=node_private_key)
print(f"Start Deploying Dai Bridge Contract!")
# send the transaction
deploy_dai_bridge_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_dai_bridge_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_dai_bridge_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_dai_bridge_transaction_hash)
dai_bridge_address = deploy_dai_bridge_transaction_receipt.contractAddress
print(f"Done! Contract Dai Bridge deployed to {dai_bridge_address}")

deployed_dai_bridge_contract = w3.eth.contract(dai_bridge_address, abi=dai_bridge_abi)

###########################################
### DEPLOY BRIDGE (DAI 2, SECOND CHAIN) ###
###########################################

with open(os.path.join(__location__, "Bridge.sol"), "r") as file:
    dai_bridge_2_contract_file = file.read()

compiled_dai_bridge_2_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Bridge.sol": {"content": dai_bridge_2_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_dai_bridge_2_sol, file)

## get bytecode
dai_bridge_2_bytecode = compiled_dai_bridge_2_sol["contracts"]["Bridge.sol"]["Bridge"]["evm"][
    "bytecode"
]["object"]

# ## get abi
dai_bridge_2_abi = json.loads(
    compiled_dai_bridge_2_sol["contracts"]["Bridge.sol"]["Bridge"]["metadata"]
)["output"]["abi"]

# create the contract in Python
dai_bridge_2_contract = w3.eth.contract(abi=dai_bridge_2_abi, bytecode=dai_bridge_2_bytecode)
# get the latest transaction
dai_bridge_2_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_dai_bridge_2_transaction = dai_bridge_2_contract.constructor("BaseCoin", "BSCN", coin_address).build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": dai_bridge_2_nonce}
)

# sign the transaction
signed_deploy_dai_bridge_2_transaction = w3.eth.account.sign_transaction(deploy_dai_bridge_2_transaction, private_key=node_private_key)
print(f"Start Deploying Dai Bridge Contract!")
# send the transaction
deploy_dai_bridge_2_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_dai_bridge_2_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_dai_bridge_2_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_dai_bridge_2_transaction_hash)
dai_bridge_2_address = deploy_dai_bridge_2_transaction_receipt.contractAddress
print(f"Done! Contract Dai Bridge deployed to {dai_bridge_2_address}")

deployed_dai_bridge_2_contract = w3.eth.contract(dai_bridge_2_address, abi=dai_bridge_2_abi)

##############################################
####### Set up the contract parameters #######
##############################################

### --- set up the DSS contracts --- ###

### DaiJoin as a ward for Dai ###

print("Add DaiJoin as a ward for Dai...")
nonce = w3.eth.get_transaction_count(node_address)
deployed_coin_contract.functions.rely(daijoin_address).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Added DaiJoin as a ward for Dai")

### Add GemJoin and DaiJoin as wards for Vat ###

print("Add GemJoin as a ward for Vat...")
nonce = w3.eth.get_transaction_count(node_address)
deployed_vat_contract.functions.rely(gemjoin_address).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Added GemJoin as a ward for Vat")

print("Add DaiJoin as a ward for Vat...")
nonce = w3.eth.get_transaction_count(node_address)
deployed_vat_contract.functions.rely(daijoin_address).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Added DaiJoin as a ward for Vat")

### Initialize Wrapped BaseCoin on Vat ###

print("Initialize Wrapped BaseCoin on the Vat...")
nonce = w3.eth.get_transaction_count(node_address)
deployed_vat_contract.functions.init(wrapped_basecoin_id).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Initialized Wrapped BaseCoin on the Vat")

### Set Wrapped BaseCoin's debt ceiling in Vat ###

wrapped_basecoin_ceiling = 10 ** 30

print("File Wrapped BaseCoin debt ceiling on Vat...")
nonce = w3.eth.get_transaction_count(node_address)
deployed_vat_contract.functions.file(wrapped_basecoin_id, line_bytes, wrapped_basecoin_ceiling).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Filed Wrapped BaseCoin debt ceiling on the Vat")

### Set Vat's total debt ceiling

total_ceiling = 10 ** 31

print("File total debt ceiling on Vat...")
nonce = w3.eth.get_transaction_count(node_address)
deployed_vat_contract.functions.file(Line_bytes, total_ceiling).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Filed total debt ceiling on the Vat")

### Set the spot price for Wrapped BaseCoin

spot_price = 1

print("File Wrapped BaseCoin spot price on Vat...")
nonce = w3.eth.get_transaction_count(node_address)
deployed_vat_contract.functions.file(wrapped_basecoin_id, spot_bytes, total_ceiling).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Filed Wrapped BaseCoin spot price on Vat")

### --- set up BaseCoin --- ###

### Create some BaseCoins ###

print("Create some BaseCoins...")
nonce = w3.eth.get_transaction_count(node_address)
deployed_basecoin_contract.functions.mint(node_address, 200).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Created some BaseCoins")

balance = deployed_basecoin_contract.functions.balanceOf(node_address).call()
print(f"Balance of node 0: {balance} (should be 200)")

### --- prepare the scenario --- ###

### Send 100 BaseCoins to the bridge ###

print("Send 100 BaseCoins to the bridge...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_basecoin_contract.functions.transfer(basecoin_bridge_address, 100).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Sent 100 BaseCoins to the bridge")

### Mint 100 Wrapped BaseCoins ###

print("Mint 100 Wrapped BaseCoins...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_wrapped_basecoin_contract.functions.mint(node_address, 100).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Minted 100 Wrapped BaseCoins")

### Allow GemJoin to withdraw 100 Wrapped BaseCoins ###

print("Allow GemJoin to withdraw 100 Wrapped BaseCoins...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_wrapped_basecoin_contract.functions.approve(gemjoin_address, 100).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! GemJoin can now withdraw 100 Wrapped BaseCoins")

### Create a CDP with 100 Wrapped BaseCoins on GemJoin ###

print("Create a CDP with 100 Wrapped BaseCoins on GemJoin...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_gemjoin_contract.functions.join(node_address, 100).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done!  Created a CDP with 100 Wrapped BaseCoins on GemJoin")

### Create 10 Dai using the CDP ###

print("Create 10 Dai using the CDP...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_vat_contract.functions.frob(wrapped_basecoin_id, node_address, node_address, node_address, 10, 10).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done!  Created 10 Dai using the CDP")

### Send the 10 Dai to the user's wallet using DaiJoin ###

print("Allow GemJoin to withdraw from Vat...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_vat_contract.functions.hope(daijoin_address).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! GemJoin can now withdraw from Vat")

print("Send the 10 Dai to the user's wallet using DaiJoin...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_daijoin_contract.functions.exit(node_address, 10).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done!  Sent the 10 Dai to the user's wallet using DaiJoin")

### Send the 10 Dai to the Dai Bridge ###

print("Allow Bridge to receive 10 Dai...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_coin_contract.functions.approve(dai_bridge_address,10).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Allowed Bridge to receive 10 Dai")

print("Send 10 Dai to the bridge...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_dai_bridge_contract.functions.deposit(10,"Chain B",node_address).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Sent 10 Dai to the bridge")

### Mint 10 Wrapped Dai ###

print("Mint 10 Wrapped Dai...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_wrapped_stablecoin_contract.functions.mint(node_address, 10).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Minted 10 Wrapped Dai")

### --- execute the scenario --- ###

print("Burn 10 Wrapped Dai...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_wrapped_stablecoin_contract.functions.burn(10).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Burned 10 Wrapped Dai")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Gas use (step 1): {receipt.gasUsed}")
step1_gas = receipt.gasUsed

### Relay sends the 10 Dai back from the Dai Bridge to the user ###

balance = deployed_coin_contract.functions.balanceOf(node_address).call()
print(f"Balance of node 0: {balance} (should be 0)")
balance = deployed_coin_contract.functions.balanceOf(dai_bridge_address).call()
print(f"Balance of Dai bridge: {balance} (should be 10)")

print("Send 10 Dai from bridge to user...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_dai_bridge_contract.functions.withdraw(node_address, 10).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Sent 10 Dai from bridge to user")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Gas use (step 2): {receipt.gasUsed}")
step2_gas = receipt.gasUsed

balance = deployed_coin_contract.functions.balanceOf(node_address).call()
print(f"Balance of node 0: {balance} (should be 10)")
balance = deployed_coin_contract.functions.balanceOf(dai_bridge_address).call()
print(f"Balance of Dai bridge: {balance} (should be 0)")

### Send the 10 Dai to the Second Dai Bridge (for Chain B) ###

print("Allow Bridge to receive 10 Dai...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_coin_contract.functions.approve(dai_bridge_2_address,10).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Allowed Bridge to receive 10 Dai")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Gas use: {receipt.gasUsed}")
step3_gas = receipt.gasUsed

print("Send 10 Dai to the bridge...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_dai_bridge_2_contract.functions.deposit(10,"Chain B",node_address).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Sent 10 Dai to the bridge")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Gas use: {receipt.gasUsed}")
step3_gas += receipt.gasUsed

print(f"Total gas use (step 3): {step3_gas}")

### Mint 10 Wrapped Dai on the second chain ###

print("Mint 10 Wrapped Dai...")
nonce = w3.eth.get_transaction_count(node_address)
tx_hash = deployed_wrapped_stablecoin_2_contract.functions.mint(node_address, 10).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": nonce})
print(f"Done! Minted 10 Wrapped Dai")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Gas use (step 4): {receipt.gasUsed}")
step4_gas = receipt.gasUsed

print(f"Total gas use (step 1): {step1_gas}")
print(f"Total gas use (step 2): {step2_gas}")
print(f"Total gas use (step 3): {step3_gas}")
print(f"Total gas use (step 4): {step4_gas}")

print(f"Total gas use (coins: {step1_gas + step4_gas}")
print(f"Total gas use (relay): {step2_gas + step3_gas}")