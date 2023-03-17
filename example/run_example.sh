 #!/bin/bash

# Extract pact-util-lib
mkdir -p .pact_util_lib
tar -C .pact_util_lib -xzf pact_util_lib_0.5.tar.gz --strip-components 1

# Compile the circuit
zokrates compile -i pedersen-multiplier.zok

# Basic setup
zokrates setup

# Generate the verifier module
pact_zk_gen gen-module --module-name pedersen-mult-verifier --proof-type string

# Compute an example
# 123456789 is the secret
# 26  is the multiplier
zokrates compute-witness -a 123456789 26
echo "Output result:" `grep out_0 witness`

# Gnerate a proof
zokrates generate-proof

# Print proof
PROOF=`pact_zk_gen gen-proof`
echo "Proof=$PROOF"

# Generate a REPL to test our verifier
pact_zk_gen gen-test --util-lib-dir ".pact_util_lib"

echo ""
echo "----------------------------------------------------"
echo "VERIFY"
echo "----------------------------------------------------"

# Run the REPL
pact pedersen-mult-verifier.repl
