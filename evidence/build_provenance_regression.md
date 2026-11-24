# Preventing mixed binaries within a comparison

During development, a cross-policy check began while the updated simulator was still linking. The first run used the previous binary and later runs used the rebuilt binary. Their recorded executable hashes exposed the mismatch, and that comparison was discarded. No result from this mixed-build check is used as a scientific comparison.

The launcher now verifies that the simulator source agrees with the pinned build record, captures the executable hash before process launch, and rejects a run if that hash changes during execution. The outer command snapshots implementation hashes before the run and rejects source changes during execution. The complete ten-run check was then repeated after build completion in closed-loop-checks3, with a common executable hash.
