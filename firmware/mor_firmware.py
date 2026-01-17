#!/usr/bin/env python3
"""
MOR Firmware Simulation for Heliosphere

Simulates Mirror Orbital Receiver firmware for beam authorization.
Implements challenge-response protocol and heartbeat monitoring.
"""

import time
import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import hmac

class MOR:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.beam_active = False
        self.last_heartbeat = 0
        self.heartbeat_timeout = 0.1  # 100ms timeout
        self.session_key = None  # Derived from challenge-response
        self.pending_challenge = None  # For tracking challenge-response

    def receive_beacon(self, beacon: dict) -> bool:
        """
        Receive and verify beacon from GRN.
        Mock contract call for verification.
        """
        # Mock contract verification: assume valid if node_id matches and power <= 1MW
        if beacon['node_id'] != 'GRN-001' or beacon['requested_power_w'] > 1_000_000:
            return False

        # Verify signature (mock for simulation)
        # In real implementation, call BeamAuth.sol verifyNode
        return True

    def send_challenge(self) -> str:
        """
        Send challenge to GRN: generate nonce.
        """
        nonce = secrets.token_hex(16)  # 32 hex chars
        self.pending_challenge = nonce
        return nonce

    def receive_response(self, response: dict) -> bool:
        """
        Receive and verify response from GRN.
        Derive session_key and verify HMAC.
        """
        if response['nonce'] != self.pending_challenge:
            return False

        # Derive session_key: HMAC_SHA256(puf_key, nonce)
        puf_key = b'puf_secret_key_32_bytes_long!!'  # Same as GRN
        h = hmac.HMAC(puf_key, hashes.SHA256())
        h.update(response['nonce'].encode())
        self.session_key = h.finalize()

        # Verify response HMAC: HMAC_SHA256(nonce, session_key)
        h_verify = hmac.HMAC(self.session_key, hashes.SHA256())
        h_verify.update(response['nonce'].encode())
        expected_hmac = h_verify.finalize()

        if expected_hmac.hex() != response['response_hmac']:
            return False

        self.pending_challenge = None
        return True

    def activate_beam(self):
        """Activate beam after successful authorization."""
        self.beam_active = True
        self.last_heartbeat = time.time()

    def receive_heartbeat(self, heartbeat: dict) -> bool:
        """
        Receive and verify heartbeat from GRN.
        """
        if not self.beam_active or self.session_key is None:
            return False

        # Verify HMAC of timestamp
        timestamp_str = str(heartbeat['timestamp'])
        h = hmac.HMAC(self.session_key, hashes.SHA256())
        h.update(timestamp_str.encode())
        expected_hmac = h.finalize()

        if expected_hmac.hex() != heartbeat['hmac']:
            return False

        self.last_heartbeat = time.time()
        return True

    def should_defocus_beam(self) -> bool:
        """
        Check if beam should be defocused due to heartbeat timeout.
        """
        if not self.beam_active:
            return True

        return (time.time() - self.last_heartbeat) > self.heartbeat_timeout

    def emergency_defocus(self):
        """Emergency defocus beam."""
        self.beam_active = False


# Example usage
if __name__ == "__main__":
    # Create MOR instance
    mor = MOR(node_id="MOR-001")

    # Simulate beacon reception
    beacon = {
        'node_id': 'GRN-001',
        'requested_power_w': 1_000_000,
        'timestamp': str(int(time.time())),
        'signature': 'mock_signature',
        'public_key': 'mock_public_key'
    }

    if mor.receive_beacon(beacon):
        print("✅ Beacon verified")
        nonce = mor.send_challenge()
        print(f"Challenge sent: {nonce}")

        # Simulate GRN response
        from grn_firmware import GRN
        private_key = ed25519.Ed25519PrivateKey.generate()
        grn = GRN(node_id="GRN-001", private_key=private_key)
        response = grn.handle_challenge(nonce)

        if mor.receive_response(response):
            print("✅ Response verified, activating beam")
            mor.activate_beam()
            grn.activate_session()  # Activate GRN session too

            # Simulate heartbeat
            hb = grn.send_heartbeat()
            if mor.receive_heartbeat(hb):
                print("✅ Heartbeat received")
            else:
                print("❌ Heartbeat invalid")

            # Check beam status
            if mor.should_defocus_beam():
                print("⚠️  Beam should be defocused")
            else:
                print("✅ Beam remains active")
        else:
            print("❌ Response invalid")
    else:
        print("❌ Beacon invalid")
