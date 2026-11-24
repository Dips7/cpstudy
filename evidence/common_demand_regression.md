# Common demand geometry regression

The five-policy mobility check initially failed between fixed and receiver-aware runs using the same seed. Both produced 640 opportunities with matching acquisition timestamps and receiver sets. The first discrepancy was a coordinate of 91.789425726513 versus 91.7894257265129.

Root cause: ConstantVelocityMobilityModel advances its cached position on queries. Feedback changes the times at which propagation queries mobility, changing the order of floating-point additions. Scoring geometry therefore inherited a policy-dependent numerical history.

Correction: evaluation coordinates are pure functions of initial seeded position, lane, direction, speed, and simulation time, with explicit boundary wrapping. The radio retains its own ns-3 mobility model. The audit continues to require exact equality of exogenous opportunity records across policies, rather than ignoring coordinate differences or merely relaxing the test tolerance.

The same change puts the highway observation region away from the recycling boundary, matching the intersection's exclusion of boundary jumps.
