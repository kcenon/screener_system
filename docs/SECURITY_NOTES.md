# Security Notes

## Known Vulnerabilities With No Fix

### ecdsa 0.19.1 - Minerva Timing Attack (GHSA-wj6h-64fc-37mp)

**Package**: `ecdsa`
**Current Version**: 0.19.1
**Vulnerability**: Minerva timing attack on P-256 curve
**Severity**: Moderate
**Status**: ⚠️ **No fix planned by maintainers**

#### Details

python-ecdsa is subject to a Minerva timing attack on the P-256 curve. Using the `ecdsa.SigningKey.sign_digest()` API function, an attacker with precise timing measurements can potentially leak the internal nonce, which may allow for private key discovery.

**Affected Operations**:
- ECDSA signature generation
- Key generation
- ECDH operations

**Not Affected**:
- ECDSA signature verification

#### Project Maintainer Response

The python-ecdsa project considers **side-channel attacks out of scope** for the project and there is no planned fix.

#### Risk Assessment for Our Application

**Current Risk**: ⚠️ **LOW-MODERATE**

**Rationale**:
1. **Limited Exposure**: We use `ecdsa` as a transitive dependency via `python-jose[cryptography]`
2. **Use Case**: Only used for JWT signature operations in `python-jose`
3. **Attack Requirements**:
   - Attacker needs precise timing measurements (microsecond level)
   - Requires ability to request many signatures with chosen inputs
   - Must be able to measure server-side processing time accurately
4. **Mitigations in Place**:
   - JWT signing happens behind FastAPI/uvicorn with variable network latency
   - Rate limiting on authentication endpoints (if configured)
   - HTTPS encryption masks some timing information

#### Recommended Actions

1. **Short Term** (Current):
   - ✅ Document the vulnerability and risk assessment
   - ✅ Monitor for updates to `python-jose` that might switch to alternative crypto library
   - ⏳ Consider rate limiting on authentication endpoints
   - ⏳ Add monitoring for unusual authentication patterns

2. **Medium Term** (Optional):
   - Consider migrating from `python-jose` to `pyjwt` or `authlib`
   - Both alternatives use `cryptography` library which has better side-channel protection
   - Evaluate if the migration effort justifies the moderate risk reduction

3. **Long Term** (If higher security required):
   - Use hardware security modules (HSM) for JWT signing
   - Implement additional authentication factors (2FA/MFA)
   - Use short-lived JWTs with refresh tokens

#### Alternative JWT Libraries

If migration is desired in the future:

| Library | Pros | Cons |
|---------|------|------|
| **PyJWT** | Widely used, well-maintained, uses `cryptography` | Simpler API, fewer features |
| **authlib** | Comprehensive OAuth/OpenID support, uses `cryptography` | Heavier dependency |
| **josepy** | ACME protocol support, uses `cryptography` | Less documentation |

#### References

- **Advisory**: https://github.com/advisories/GHSA-wj6h-64fc-37mp
- **Minerva Attack**: https://minerva.crocs.fi.muni.cz/
- **python-ecdsa Issue**: https://github.com/tlsfuzzer/python-ecdsa/issues/277

---

## Monitoring Recommendations

Monitor the following for suspicious patterns that might indicate exploitation attempts:

1. **High Volume of Failed JWT Validation**: Could indicate timing attack attempts
2. **Unusual Authentication Patterns**: Many rapid authentication requests from same source
3. **Timing Analysis Tools**: Watch for requests with timing measurement characteristics

---

**Last Updated**: 2025-11-11
**Next Review**: 2026-02-11 (quarterly)
**Risk Owner**: Security Team
