### 🔑 **Key Improvements**

| Component | Before | After |
|---------|--------|-------|
| **Identity** | Software pubkey | **PUF-derived hardware identity** |
| **Session Key** | Encrypted secret | **Ephemeral HMAC with PUF key** |
| **Validation** | Off-chain registry | **On-chain `BeamAuth.sol` contract** |
| **Safety** | MOR-enforced limit | **On-chain power density validation** |

---

### 🛡️ **Why This Is Betrayal-Proof**

- **Hardware root of trust** prevents firmware tampering  
- **PUF binding** stops node impersonation  
- **On-chain validation** enforces safety rules universally  
- **Heartbeat timeout** is **hard-coded in MOR firmware** (no override)  
- **All code auditable** — no hidden paths

This protocol ensures that **energy flows only where the community consents**—and stops instantly if that consent is withdrawn.

Would you like the **companion firmware implementation** that matches this spec?
