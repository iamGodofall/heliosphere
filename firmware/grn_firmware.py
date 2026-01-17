#!/usr/bin/env python3
"""
GRN Firmware Simulation for Heliosphere

Simulates Ground Reception Node firmware for beam authorization.
Implements Ed25519 signatures (matching BeamAuth.sol) and heartbeat protocol.
"""

import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import hmac

class GRN:
    def __init__(self, node_id: str, private_key: ed25519.Ed25519PrivateKey):
        self.node_id = node_id
        self.private_key = private_key
        self.public_key = private_key.public_key()
        self.session_active = False
        self.last_heartbeat = 0
        self.heartbeat_interval = 0.05  # 50 ms
        self.session_key = None  # Ephemeral HMAC key derived from PUF

    def generate_beacon(self, requested_power_w: int) -> dict:
        """
        Generate beacon for beam authorization request.
        
        Message format: keccak256(node_id + requested_power_w + timestamp)
        Matches BeamAuth.sol's initiateBeamSession verification.
        """
        timestamp = str(int(time.time()))
        message = f"{self.node_id}:{requested_power_w}:{timestamp}".encode()
        signature = self.private_key.sign(message)
        
        return {
            'node_id': self.node_id,
            'requested_power_w': requested_power_w,
            'timestamp': timestamp,
            'signature': signature.hex(),
            'public_key': self.public_key.public_bytes_raw().hex()
        }

    def handle_challenge(self, nonce: str) -> dict:
        """
        Handle challenge from MOR: derive session_key and respond with HMAC.
        """
        puf_key = b'puf_secret_key_32_bytes_long!!'
        h = hmac.HMAC(puf_key, hashes.SHA256())
        h.update(nonce.encode())
        self.session_key = h.finalize()

        h_resp = hmac.HMAC(self.session_key, hashes.SHA256())
        h_resp.update(nonce.encode())
        response_hmac = h_resp.finalize()

        return {
            'node_id': self.node_id,
            'nonce': nonce,
            'response_hmac': response_hmac.hex()
        }

    def activate_session(self):
        """Activate beam session after authorization."""
        self.session_active = True
        self.last_heartbeat = time.time()

    def send_heartbeat(self) -> dict:
        """
        Send heartbeat to maintain beam.
        Called every 50ms by real firmware.
        Includes HMAC for authentication.
        """
        if not self.session_active or self.session_key is None:
            raise RuntimeError("No active session or session key not set")

        current_time = time.time()
        self.last_heartbeat = current_time

        timestamp_str = str(current_time)
        h = hmac.HMAC(self.session_key, hashes.SHA256())
        h.update(timestamp_str.encode())
        heartbeat_hmac = h.finalize()

        return {
            'node_id': self.node_id,
            'timestamp': current_time,
            'session_active': True,
            'hmac': heartbeat_hmac.hex()
        }

    def should_defocus_beam(self) -> bool:
        if not self.session_active:
            return True
        return (time.time() - self.last_heartbeat) > 0.1

    def emergency_deactivate(self):
        self.session_active = False


# Corrected standalone test
if __name__ == "__main__":
    private_key = ed25519.Ed25519PrivateKey.generate()
    grn = GRN(node_id="GRN-001", private_key=private_key)
    
    # Step 1: Generate beacon
    beacon = grn.generate_beacon(requested_power_w=1_000_000)
    print(f"Beacon generated for {beacon['node_id']}")
    print(f"Requested power: {beacon['requested_power_w']:,} W")
    
    # Step 2: Simulate challenge-response (as if from MOR)
    mock_nonce = "7f869285e68697e37f7766d1239c871b"
    response = grn.handle_challenge(mock_nonce)
    print("✅ Challenge handled")
    
    # Step 3: Activate session AFTER challenge-response
    grn.activate_session()
    
    # Step 4: Send heartbeat (now works)
    hb = grn.send_heartbeat()
    print(f"✅ Heartbeat sent at {hb['timestamp']}")
    
    # Step 5: Check status
    if grn.should_defocus_beam():
        print("⚠️  Beam should be defocused")
    else:
        print("✅ Beam remains active")