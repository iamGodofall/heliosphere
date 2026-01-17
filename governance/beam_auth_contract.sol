// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.19;

/**
 * Beam Authorization Smart Contract for Heliosphere
 *
 * Manages cryptographic beam authorization between MOR and GRN nodes.
 * Implements 2-of-3 consent: GRN + MOR + DAO Council.
 *
 * Architecture:
 * - On-chain: Registration, session initiation, emergency deactivation
 * - Off-chain: Real-time heartbeat verification (handled by MOR firmware)
 *
 * Deployed on Ethereum L2 (OP Stack) or Celestia DA for low-cost verification.
 */

import "@openzeppelin/contracts/access/Ownable2Step.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

contract BeamAuth is Ownable2Step {
    using ECDSA for bytes32;
    using EnumerableSet for EnumerableSet.AddressSet;

    // ===== STRUCTS =====
    struct Node {
        uint256 registeredAt;
        bool isActive;
        uint8 nodeType; // 0: GRN, 1: MOR, 2: DAO
        uint256 areaM2; // Physical area in square meters
    }

    struct BeamSession {
        address grnId;
        address morId;
        uint256 startedAt;
        bool isActive;
        uint256 powerAllocatedW; // Allocated power in watts
    }

    // ===== STORAGE =====
    mapping(address => Node) public nodes;
    mapping(bytes32 => BeamSession) public sessions;
    mapping(address => bytes32) public activeSessions; // GRN -> sessionId

    // DAO Council Management
    EnumerableSet.AddressSet private _daoCouncil;
    uint256 public constant MIN_DAO_SIGNATURES = 2;

    // Safety Limits
    uint256 public constant MAX_POWER_DENSITY_WPM2 = 1000; // 1 kW/m²

    // ===== EVENTS =====
    event NodeRegistered(address indexed nodeId, uint8 nodeType, uint256 areaM2);
    event BeamSessionInitiated(bytes32 indexed sessionId, address grnId, address morId);
    event BeamAuthorized(bytes32 indexed sessionId);
    event BeamDeactivated(bytes32 indexed sessionId, string reason);
    event DAOCouncilUpdated(address indexed member, bool isAdded);

    // ===== MODIFIERS =====
    modifier onlyActiveNode() {
        require(nodes[msg.sender].isActive, "BeamAuth: Node not registered");
        _;
    }

    modifier onlyGRN() {
        require(nodes[msg.sender].nodeType == 0, "BeamAuth: Caller not GRN");
        _;
    }

    modifier onlyMOR() {
        require(nodes[msg.sender].nodeType == 1, "BeamAuth: Caller not MOR");
        _;
    }

    // ===== DAO COUNCIL MANAGEMENT =====
    function addToDAOCouncil(address member) external onlyOwner {
        require(member != address(0), "BeamAuth: Invalid address");
        require(_daoCouncil.add(member), "BeamAuth: Already in council");
        emit DAOCouncilUpdated(member, true);
    }

    function removeFromDAOCouncil(address member) external onlyOwner {
        require(_daoCouncil.remove(member), "BeamAuth: Not in council");
        emit DAOCouncilUpdated(member, false);
    }

    function getDAOCouncilSize() external view returns (uint256) {
        return _daoCouncil.length();
    }

    function isDAOMember(address account) external view returns (bool) {
        return _daoCouncil.contains(account);
    }

    // ===== NODE REGISTRATION =====
    function registerNode(
        address nodeId,
        uint8 nodeType,
        uint256 areaM2
    ) external onlyOwner {
        require(nodeType <= 2, "BeamAuth: Invalid node type");
        require(areaM2 > 0, "BeamAuth: Area must be positive");
        require(!nodes[nodeId].isActive, "BeamAuth: Node already registered");

        nodes[nodeId] = Node({
            registeredAt: block.timestamp,
            isActive: true,
            nodeType: nodeType,
            areaM2: areaM2
        });

        emit NodeRegistered(nodeId, nodeType, areaM2);
    }

    // ===== BEAM SESSION INITIATION (GRN → MOR) =====
    function initiateBeamSession(
        address grnId,
        uint256 requestedPowerW,
        bytes memory signature
    ) external onlyMOR returns (bytes32 sessionId) {
        // Validate GRN
        require(nodes[grnId].isActive && nodes[grnId].nodeType == 0, "BeamAuth: Invalid GRN");

        // Validate power density
        uint256 powerDensity = requestedPowerW / nodes[grnId].areaM2;
        require(powerDensity <= MAX_POWER_DENSITY_WPM2, "BeamAuth: Power density exceeds safety limit");

        // Verify GRN signature (raw signing - matches firmware)
        bytes32 messageHash = keccak256(abi.encodePacked(grnId, requestedPowerW, block.timestamp));
        address recoveredSigner = ECDSA.recover(messageHash, signature);
        require(recoveredSigner == grnId, "BeamAuth: Invalid signature");

        // Create session
        sessionId = keccak256(abi.encodePacked(grnId, msg.sender, block.timestamp));
        sessions[sessionId] = BeamSession({
            grnId: grnId,
            morId: msg.sender,
            startedAt: block.timestamp,
            isActive: false,
            powerAllocatedW: requestedPowerW
        });

        emit BeamSessionInitiated(sessionId, grnId, msg.sender);
        return sessionId;
    }

    // ===== BEAM AUTHORIZATION (2-of-3 CONSENT) =====
    function authorizeBeam(
        bytes32 sessionId,
        bytes memory morSignature,
        bytes[] memory daoSignatures
    ) external {
        BeamSession storage session = sessions[sessionId];
        require(!session.isActive, "BeamAuth: Session already active");
        require(block.timestamp - session.startedAt <= 300, "BeamAuth: Session expired"); // 5 min

        // Verify MOR signature
        bytes32 authHash = keccak256(abi.encodePacked(sessionId, "authorize"));
        address morSigner = ECDSA.recover(authHash, morSignature);
        require(morSigner == session.morId, "BeamAuth: Invalid MOR signature");

        // Verify DAO signatures (2-of-council)
        require(daoSignatures.length >= MIN_DAO_SIGNATURES, "BeamAuth: Insufficient DAO signatures");
        
        uint256 validSignatures;
        mapping(address => bool) signed;
        
        for (uint256 i = 0; i < daoSignatures.length; i++) {
            address daoSigner = ECDSA.recover(authHash, daoSignatures[i]);
            if (_daoCouncil.contains(daoSigner) && !signed[daoSigner]) {
                signed[daoSigner] = true;
                validSignatures++;
            }
        }
        
        require(validSignatures >= MIN_DAO_SIGNATURES, "BeamAuth: Insufficient valid DAO signatures");

        // Activate session
        session.isActive = true;
        activeSessions[session.grnId] = sessionId;
        emit BeamAuthorized(sessionId);
    }

    // ===== EMERGENCY DEACTIVATION =====
    function emergencyDeactivate(
        bytes32 sessionId,
        string memory reason
    ) external onlyActiveNode {
        BeamSession storage session = sessions[sessionId];
        require(session.isActive, "BeamAuth: Session not active");

        session.isActive = false;
        delete activeSessions[session.grnId];
        emit BeamDeactivated(sessionId, reason);
    }

    // ===== READ FUNCTIONS =====
    function getActiveSession(address grnId) external view returns (bytes32) {
        return activeSessions[grnId];
    }

    function getSessionDetails(bytes32 sessionId) external view returns (
        address grnId,
        address morId,
        uint256 startedAt,
        bool isActive,
        uint256 powerAllocatedW
    ) {
        BeamSession memory session = sessions[sessionId];
        return (
            session.grnId,
            session.morId,
            session.startedAt,
            session.isActive,
            session.powerAllocatedW
        );
    }

    function getNodeDetails(address nodeId) external view returns (
        uint256 registeredAt,
        bool isActive,
        uint8 nodeType,
        uint256 areaM2
    ) {
        Node memory node = nodes[nodeId];
        return (
            node.registeredAt,
            node.isActive,
            node.nodeType,
            node.areaM2
        );
    }
}