// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.18;

contract Relay {

    uint threshold;

    address[] public wards;
    mapping (uint => mapping (address => mapping (uint => uint))) public approvals;

    constructor () {
        wards.push(msg.sender);
        threshold = 1;
    }

    function addWard(address node) external {
        bool success = false;
        for(uint i=0;i<wards.length;i++) {
            require(wards[i] != node, "Multi-Dai-Relay/add_existing-address-0");
            if (wards[i] == msg.sender) {
                success = true;
            }
        }
        require(success, "Multi-Dai-Relay/invalid-address-0");
        wards.push(node);
        threshold = 2*((wards.length-1)/3) + 1;
    }

    function approve(address cctransfer, uint index) external {
        bool success = false;
        for(uint i=0;i<wards.length;i++) {
            if (wards[i] == msg.sender) {
                approvals[i][cctransfer][index] = 1;
                success = true;
            }
        }
        require(success, "Multi-Dai-Relay/invalid-address-0");
    }

    function isApproved(address cctransfer, uint index) external view returns (bool z) {
        uint numApprovals = 0;
        for(uint i=0;i<wards.length;i++) {
            if (approvals[i][cctransfer][index] == 1) {
                numApprovals++;
            }
        }
        z = numApprovals >= threshold;
    }
}