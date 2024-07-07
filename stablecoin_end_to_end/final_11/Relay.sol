// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.18;

contract Relay {

    uint threshold;

    address public ward;
    mapping (address => mapping (uint => uint)) public approvals;

    constructor (address initialWard) {
        ward = initialWard;
    }

    function changeAddress(address newWard, bytes calldata signature) public returns (address) {
        bytes32 message = keccak256(abi.encodePacked(newWard));
        require(ward == recover(message, signature));
        ward = newWard;
    }

    function approve(address cctransfer, uint index, bytes calldata signature) external {
        bytes32 message = keccak256(abi.encodePacked(cctransfer, index));

        bool success = (ward == recover(message, signature));
        require(success, "Multi-Dai-Relay/invalid-address-0");

        approvals[cctransfer][index] = 1;
    }

    function isApproved(address cctransfer, uint index) external view returns (bool) {
        return approvals[cctransfer][index] > 0;
    }

       // from https://gist.github.com/BjornvdLaan/e41d292339bbdebb831d0b976e1804e8
    function recover(bytes32 hash, bytes memory sig)
        internal
        pure
        returns (address)
    {
        bytes32 r;
        bytes32 s;
        uint8 v;

        // Check the signature length
        if (sig.length != 65) {
            return (address(0));
        }

        // Divide the signature in r, s and v variables
        // ecrecover takes the signature parameters, and the only way to get them
        // currently is to use assembly.
        // solium-disable-next-line security/no-inline-assembly
        assembly {
            r := mload(add(sig, 32))
            s := mload(add(sig, 64))
            v := byte(0, mload(add(sig, 96)))
        }

        // Version of signature should be 27 or 28, but 0 and 1 are also possible versions
        if (v < 27) {
            v += 27;
        }

        // If the version is correct return the signer address
        if (v != 27 && v != 28) {
            return (address(0));
        } else {
            // solium-disable-next-line arg-overflow
            return ecrecover(hash, v, r, s);
        }
    }
}