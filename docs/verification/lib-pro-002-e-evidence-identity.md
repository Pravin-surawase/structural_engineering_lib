# LIB-PRO-002-E evidence and source identity

**State:** implementation evidence; not release authorization or professional approval
**Controlled review ID:** `LIB-PRO-002-E-BEAM-AMENDMENT-REVIEW`

The bounded `design_beam_is456` strength route is bound to the controlled
IS 456:2000 consolidated-through-Amendment-5 source and the controlled June
2024 Amendment 6 artifact using their existing SHA-256 identities. Review of
the controlled Amendment 6 change set found no calculation change to the
implemented beam flexure/shear strength clauses. Runtime evidence therefore
records `REVIEWED_NO_CALCULATION_CHANGE` for this route. This decision does not
apply to unlisted routes; an unknown route-specific applicability state must
remain `UNKNOWN` and force `HOLD`.

Evidence schema `3.0` separately binds:

- normalized calculation-bearing inputs and calculation identity;
- exact installed library content identity;
- controlled base/amendment identities and applicability review;
- import artifact and normalization-ledger metadata when supplied; and
- a deterministic replay-receipt hash.

Presentation-only metadata changes the provenance and replay identities but
does not change the arithmetic input or calculation identity. Footing basis
origins (`provided`, `assumed`, or `verified`) remain distinct from approval
flags; an approved value whose origin is `assumed` remains assumed and holds
an otherwise passing result pending verification.
