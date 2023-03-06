from .kadena_b64 import b64_encode
from datetime import datetime
import json
from string import Template
from more_itertools import take

MODULE_TEMPLATE = """
;; Generated by pact-zk-generator at $date
(module $module_name GOVERNANCE
  (use free.util-zk)

  (defcap GOVERNANCE ()
    ;The default behaviour is to create non-upgradable module but this can be changed here
    false)

  (defconst V-KEY:object{groth16-verify-key} $vkey)

  (defun verify:bool ($func_arguments)
    (let ((pub-inputs $pub_inputs)
          (_proof $proof_object))
      (verify-groth16-proof V-KEY pub-inputs _proof))
  )
)
"""

TEST_REPL_TEMPLATE = """
(begin-tx)
(module G GOV
  (defcap GOV () true)
  (defconst GUARD_SUCCESS (create-user-guard (success)))
  (defun success () true)
)
(define-namespace 'free GUARD_SUCCESS GUARD_SUCCESS)

(namespace 'free)
(load "${lib_dir}/util-lists.pact")
(load "${lib_dir}/util-strings.pact")
(load "${lib_dir}/util-zk.pact")
(commit-tx)

(begin-tx)
(load "${mod_pact}")

(let ((result
        ($mod_name.verify $arguments $proof)
     ))
  (print (format "Proof verification result: {}" [result] ))
)
"""


def flatten(proof):
    output_list = []

    def _flatten(obj):
        if isinstance(obj, list):
            for v in obj:
                _flatten(v)
        elif isinstance(obj, dict):
            for _, v in sorted(obj.items()):
                _flatten(v)
        else:
            output_list.append(obj)

    _flatten(proof)
    return output_list


def serialize_proof(proof):
    def __to_hash(x):
        return b64_encode(x.to_bytes(32, "big"))
    flat_proof = flatten(proof)
    results = "".join(map(__to_hash, flat_proof))

    return results

def gen_proof(proof, as_string):
    return '"'+ serialize_proof(proof) +'"' if as_string else json.dumps(proof)


TYPES_CAST = {"field":"integer"}

def gen_pact_module(module_name, verif_key, public_arguments, is_proof_string):
    def __format_argument(x):
        if x.length == 1:
            return "{:s}:{:s}".format(x.name, TYPES_CAST[x.type])
        else:
            return "{:s}:[{:s}]".format(x.name, TYPES_CAST[x.type])

    func_arguments = [__format_argument(x) for x in public_arguments]

    if is_proof_string:
        func_arguments.append("proof:string")
        proof_object = "(deserialize-proof proof)"
    else:
        func_arguments.append("proof:object{groth16-proof}")
        proof_object = "proof"


    func_arguments_str = " ".join(func_arguments)

    pub_inputs = []
    for arg in public_arguments:
        if arg.length == 1:
            pub_inputs.append("{:s}".format(arg.name))
        else:
            for idx in range(arg.length):
                pub_inputs.append("(at {:d} {:s})".format(idx, arg.name))

    pub_inputs_str = "[" + ", ".join(pub_inputs) + "]"

    tmpl = Template(MODULE_TEMPLATE)

    vkey_str = "\n    ".join(json.dumps(verif_key, indent=1).splitlines())

    mod_data = tmpl.substitute(date=str(datetime.now()),
                               func_arguments=func_arguments_str,
                               module_name=module_name,
                               pub_inputs=pub_inputs_str,
                               proof_object=proof_object,
                               vkey=vkey_str)
    filename = module_name+".pact"
    with open(filename, "w") as fd:
        fd.write(mod_data)
    print("{} written".format(filename))

def gen_test_repl(lib_dir, module_name, inputs, public_abi, proof, is_proof_string):
    _proof = gen_proof(proof, is_proof_string)
    _arguments = []
    _inputs = iter(inputs)

    _arguments = [ take(x.length, _inputs) for x in public_abi]
    def __render_args(x):
        return str(x[0]) if len(x) == 1 else "[" + " ".join(map(str, x)) + "]"


    tmpl = Template(TEST_REPL_TEMPLATE)
    repl_data = tmpl.substitute(lib_dir=lib_dir,
                                mod_pact=module_name +".pact",
                                mod_name=module_name,
                                arguments=" ".join(map(__render_args, _arguments)),
                                proof=_proof)

    filename = module_name+".repl"
    with open(filename, "w") as fd:
        fd.write(repl_data)
    print("{} written".format(filename))