#!/usr/bin/env python3
"""
Heliosphere Beam Authorization Demo

Runs the full anti-betrayal protocol simulation:
GRN → MOR → BeamAuth.sol → Challenge-Response → Beam Activation → Heartbeat Monitoring
"""

import time
import sys
from firmware.grn_firmware import GRN
from firmware.mor_firmware import MOR
from cryptography.hazmat.primitives.asymmetric import ed25519
import sim.beam_routing as beam_routing
import sim.beam_trace as beam_trace

def main():
    print("🚀 Heliosphere Beam Authorization Demo")
    print("=" * 50)

    # Initialize nodes
    print("🔑 Initializing nodes...")
    private_key = ed25519.Ed25519PrivateKey.generate()
    grn = GRN(node_id="GRN-001", private_key=private_key)
    mor = MOR(node_id="MOR-001")
    print("✅ GRN and MOR initialized")

    # Step 1: GRN generates beacon
    print("\n📡 Step 1: GRN generates beacon")
    beacon = grn.generate_beacon(requested_power_w=1_000_000)
    print(f"   Node ID: {beacon['node_id']}")
    print(f"   Requested Power: {beacon['requested_power_w']:,} W")
    print(f"   Timestamp: {beacon['timestamp']}")
    print("✅ Beacon generated\n")

    # Step 2: MOR receives and verifies beacon
    print("\n🔍 Step 2: MOR verifies beacon")
    if mor.receive_beacon(beacon):
        print("✅ Beacon verified (mock contract call)")
    else:
        print("❌ Beacon invalid")
        return

    # Step 3: MOR sends challenge
    print("\n🎯 Step 3: MOR sends challenge")
    nonce = mor.send_challenge()
    print(f"   Nonce: {nonce}")
    print("✅ Challenge sent")

    # Step 4: GRN handles challenge and responds
    print("\n🔐 Step 4: GRN responds to challenge")
    response = grn.handle_challenge(nonce)
    print(f"   Response HMAC: {response['response_hmac'][:16]}...")
    print("✅ Response generated")

    # Step 5: MOR verifies response and activates beam
    print("\n⚡ Step 5: MOR verifies response and activates beam")
    if mor.receive_response(response):
        print("✅ Response verified, session key established")
        mor.activate_beam()
        grn.activate_session()  # Sync GRN session
        print("✅ Beam activated (sub-beam focused)")
    else:
        print("❌ Response invalid")
        return

    # Step 6: Heartbeat loop simulation
    print("\n💓 Step 6: Heartbeat monitoring (50ms intervals)")
    for i in range(5):  # Simulate 5 heartbeats
        time.sleep(0.05)  # 50ms interval

        # GRN sends heartbeat
        hb = grn.send_heartbeat()

        # MOR receives and verifies
        if mor.receive_heartbeat(hb):
            print(f"   Heartbeat {i+1}: ✅ Received and verified")
        else:
            print(f"   Heartbeat {i+1}: ❌ Invalid")
            break

        # Check beam status
        if mor.should_defocus_beam():
            print("⚠️  Beam defocused due to timeout")
            break

    print("\n🔒 Step 7: Emergency deactivation")
    mor.emergency_defocus()
    grn.emergency_deactivate()
    print("✅ Beam safely deactivated")

    # Step 8: Beam routing simulation
    print("\n🌐 Step 8: Beam routing simulation")
    try:
        # Simulate command line args for beam_routing
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--mor_power", type=float, required=True)
        parser.add_argument("--total_demand", type=float, required=True)
        parser.add_argument("--seed", type=int, default=None)
        args = parser.parse_args(["--mor_power", "2000000000", "--total_demand", "2100000000", "--seed", "42"])
        beam_routing.main(args)
        print("✅ Beam routing completed")
    except Exception as e:
        print(f"❌ Beam routing failed: {e}")

    # Step 9: Beam trace simulation
    print("\n🔬 Step 9: Beam trace simulation")
    try:
        # Simulate command line args for beam_trace
        parser = argparse.ArgumentParser()
        parser.add_argument("--ish_power", type=float, required=True)
        parser.add_argument("--distance", type=float, required=True)
        args = parser.parse_args(["--ish_power", "10000000000", "--distance", "150000000000"])
        beam_trace.main(args)
        print("✅ Beam trace completed")
    except Exception as e:
        print(f"❌ Beam trace failed: {e}")

    print("\n🎉 Full Heliosphere demo complete - From authorization to delivery!")

if __name__ == "__main__":
    main()
