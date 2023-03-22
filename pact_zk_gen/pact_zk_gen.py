import argparse
import pickle
from pathlib import Path
from itertools import product

from ._version import __version__
from . import pact_zk
from .zokrates import ZoKrates_Project

class PersistantState:
    FILENAME = ".pact_zk_state"

    def __init__(self):
        self.last_module = None
        self.last_proof_type = None

    def save(self):
        with open(self.FILENAME, "wb") as fd:
            pickle.dump(self, fd)

    @classmethod
    def load(cls):
        try:
            with open(cls.FILENAME, "rb") as fd:
                return pickle.load(fd)
        except (FileNotFoundError, EOFError):
            return PersistantState()

p_state = PersistantState.load()

def locate_util_lib_dir(req_dir):
    dir = Path(req_dir).resolve()
    for d1, d2 in product( ('.', 'pact-util-lib', '.pact_util_lib', '../pact-util-lib/', '../../pact-util-lib/'),
                           ('pact/contracts', 'contracts', 'pact')):
        _dir = dir.joinpath(d1).joinpath(d2)
        if _dir.is_dir() and _dir.joinpath("util-zk.pact").is_file():
            print("pact-util-lib found:{!s}".format(_dir))
            return _dir
    else:
        raise ValueError("Unable to locate pact-util-lib")

def gen_contract(args):
    print("Generate Pact module")
    zok = ZoKrates_Project()
    pub,priv, out = zok.get_abi()
    pact_zk.gen_pact_module(args.module_name, zok.get_key(), pub + out, args.proof_type =="string")
    p_state.last_module = args.module_name
    p_state.last_proof_type = args.proof_type
    p_state.save()

def gen_test_repl(args):
    print("Generate test REPL")
    zok = ZoKrates_Project()

    if not p_state.last_module:
        raise ValueError("No module has been created")

    pub,priv, out = zok.get_abi()
    inputs = zok.get_inputs()
    proof  = zok.get_proof()

    public_abi = pub + out

    abi_len = sum(map(lambda x:x.length, public_abi))
    if abi_len != len(inputs):
        raise ValueError("The proof inputs does not match with the ABI")

    lib_dir = locate_util_lib_dir(args.util_lib_dir)

    pact_zk.gen_test_repl(lib_dir, p_state.last_module, inputs, public_abi, proof, p_state.last_proof_type =="string")

def gen_proof(args):
    zok = ZoKrates_Project()
    proof  = zok.get_proof()
    proof_type = args.proof_type if args.proof_type else p_state.last_proof_type
    print(pact_zk.gen_proof(proof, proof_type == "string"))


def _main():
    parser = argparse.ArgumentParser(prog='pact_zk_gen')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    subparsers = parser.add_subparsers(required=False, help='Action', dest='action')

    parser_gen_contract = subparsers.add_parser("gen-module", help="Generate verifier module")
    parser_gen_contract.add_argument("--proof-type", choices=['object', 'string'], default='string', help="Type of the expected proof" )
    parser_gen_contract.add_argument("--module-name", type=str, default="verifier" )
    parser_gen_contract.set_defaults(func=gen_contract)

    parser_gen_test = subparsers.add_parser("gen-test", help="Generate test REPL")
    parser_gen_test.add_argument("--util-lib-dir", type=str, default=".")
    parser_gen_test.set_defaults(func=gen_test_repl)

    parser_gen_proof = subparsers.add_parser("gen-proof", help="Generate a proof to be used in Pact")
    parser_gen_proof.add_argument("--proof-type", choices=['object', 'string'], help="Type of proof" )
    parser_gen_proof.set_defaults(func=gen_proof)

    parser_help = subparsers.add_parser("help", help="Show help")
    parser.set_defaults(func=lambda x:parser.print_help())

    args = parser.parse_args()
    args.func(args)

     #if args.action is None:
     #    parser.print_help()


if __name__ == "__main__":
    _main()
