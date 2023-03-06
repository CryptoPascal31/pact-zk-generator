# Pact ZK Generator

Tool to generate Pact ZK verifiers modules and zk-SNARK proofs, for the Kadena blockchain.

Currently, a minimal set of features  are implemented.

Limitations:
  - Support only for the Groth16 verification scheme.
  - Support only for types `field` and `field[]` for inputs and outputs
  - Might have a lot of bugs. => Feel free to report.

This tool integrates with ZoKrates:
https://zokrates.github.io/

The tool allows to replace the EVM contract generation, by an equivalent in Pact.
The generated modules are very simple and uses function exposed by:
https://github.com/CryptoPascal31/pact-util-lib

## Related project

This project aims to implement in Pact two hashes algorithm used in in zk-SNARKS, to be computed on-chain:
  - MiMC
  - Poseidon

https://github.com/CryptoPascal31/pact-zk-hashes

## Requirements
ZoKrates: https://Zokrates.github.io/gettingstarted.html

Pact: https://github.com/kadena-io/pact/releases/

Pact-util-lib: https://github.com/CryptoPascal31/pact-util-lib/releases

## Installation

The easiest to install this tool is to download the wheel package and install it with pip:
`pip3 install pact_zk_generator-0.1-py3-none-any.whl`

The tool can be called directly:
```
$ pact_zk_gen
```


## Proof types:
This tool can handle 2 proofs formats:

  - Pact/JSON object, defined here: https://pact-util-lib.readthedocs.io/en/latest/util-zk.html#groth16-verify-key
  - Serialized to string, defined here: https://pact-util-lib.readthedocs.io/en/latest/util-zk.html#serialization-scheme

## Quickstart / Example:
An example is provided in the `example` sub-directory with detailed instructions.
  [Example](example/)

## Commands

### help or --help

Show the help message:

```
$ pact_zk_gen
usage: pact_zk_gen [-h] {gen-module,gen-test,gen-proof,help} ...

positional arguments:
  {gen-module,gen-test,gen-proof,help}
                        Action
    gen-module          Generate verifier module
    gen-test            Generate test REPL
    gen-proof           Generate a proof to be used in Pact
    help                Show help

optional arguments:
  -h, --help            show this help message and exit
```


### gen-module

Convert a compiled program and the file `verification.key` to a Pact module.

Optional arguments:
  - `--module-name`
  - `--proof-type`: `string` or `object`

The executions results in a Pact file, ready to be tested or deployed on-chain.

### gen-proof

Generate a proof from a computed witness and proof by ZoKrates (`proof.json`)

Optional arguments:
  - `--proof-type`: `string` or `object`

The proof is output to standard output.

### gen-test

Generate a test REPL script to check that everything is fine with the Pact module.

This can be useful as well to be used as an example for how to call the verification module.

Optional arguments:
  - `--util-lib-dir` : Directory of `pact-util-lib`
