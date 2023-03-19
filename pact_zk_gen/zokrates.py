import json
from pprint import pprint
from collections import namedtuple
from pathlib import Path
from functools import partial

CircuitArgument = namedtuple("CircuitArgument", "name type length")

def from_hex(x):
    return int(x, 16)

class ZoKrates_Project:
    FILES = {'ABI':"abi.json",
             'PROOF': "proof.json",
             'VERIFICATION_KEY':"verification.key"}

    ALLOWED_ABI_TYPES = {'field', 'u8', 'u16', 'u32', 'u64'}


    def __init__(self,dir=None):
        self._dir = Path(dir) if dir else Path.cwd()

    def _load_json(self, file):
        with open(self._dir.joinpath(self.FILES[file])) as fd:
            return json.load(fd)

    @staticmethod
    def _check_params(zr_object):
        scheme = zr_object.get("scheme", "Unknown")
        curve = zr_object.get("curve", "Unknown")
        if scheme != "g16":
            raise ValueError("Unsuported verification_scheme:"+scheme)
        if curve != "bn128":
            raise ValueError("Unsuported curve:"+curve)

    def get_abi(self):
        abi_data = self._load_json('ABI')
        public_inputs = []
        private_inputs = []
        outputs = []


        def __to_argument(x, is_output=False):
            name = x['name'] if not is_output else "out"
            if x['type'] in self.ALLOWED_ABI_TYPES:
                return CircuitArgument(name, x['type'], 1 )
            if x['type'] == "array":
                subtype = x["components"]["type"]
                if subtype in self.ALLOWED_ABI_TYPES:
                    return CircuitArgument(name, subtype , x['components']['size'])
            if is_output and x['type'] == "tuple" and not x['components']['elements']:
                # This means no output
                return None

            raise ValueError("Only field/integers and [field/integers] types are supported")

        __to_inp_argument = partial(__to_argument, is_output=False)
        __to_outp_argument = partial(__to_argument, is_output=True)

        for inp in abi_data['inputs']:
            if inp['public']:
                public_inputs.append(__to_inp_argument(inp))
            else:
                private_inputs.append(__to_inp_argument(inp))

        outp = __to_outp_argument(abi_data['output'])
        if outp:
            outputs.append(outp)

        return public_inputs, private_inputs, outputs

    @staticmethod
    def parse_ic(zr_object, field_name):
        if field_name not in zr_object:
            raise ValueError("Error => {:s} field not present".format(field_name))
        return [{"x":from_hex(_x), "y": from_hex(_y)} for _x, _y in  zr_object[field_name]]

    @staticmethod
    def parse_g1_point(zr_object, field_name):
        if field_name not in zr_object:
            raise ValueError("Error => {:s} field not present".format(field_name))
        point_x, point_y = zr_object[field_name]
        return {"x":from_hex(point_x), "y": from_hex(point_y)}

    @staticmethod
    def parse_g2_point(zr_object, field_name):
        def __parse_list(x):
            if len(x) != 2:
                raise ValueError("Invalid point format in {:s}".format(field_name))
            return [from_hex(_x) for _x in x]

        if field_name not in zr_object:
            raise ValueError("Error => {:s} field not present".format(field_name))

        point_x, point_y = zr_object[field_name]
        return {"x": __parse_list(point_x), "y":__parse_list(point_y)}

    def get_inputs(self):
        zr_data  = self._load_json('PROOF')
        self._check_params(zr_data)
        inputs_data = zr_data.get('inputs', [])
        return [from_hex(x) for x in inputs_data]


    def get_proof(self):
        zr_data  = self._load_json('PROOF')
        self._check_params(zr_data)
        proof_data = zr_data.get('proof', {})
        proof = {}

        proof['A'] = self.parse_g1_point(proof_data, 'a')
        proof['B'] = self.parse_g2_point(proof_data, 'b')
        proof['C'] = self.parse_g1_point(proof_data, 'c')
        return proof

    def get_key(self):
        zr_data  = self._load_json('VERIFICATION_KEY')
        self._check_params(zr_data)
        pact_key = {}
        pact_key['alpha'] = self.parse_g1_point(zr_data, 'alpha')
        pact_key['beta'] =  self.parse_g2_point(zr_data, 'beta')
        pact_key['gamma'] = self.parse_g2_point(zr_data, 'gamma')
        pact_key['delta'] = self.parse_g2_point(zr_data, 'delta')
        pact_key['ic'] = self.parse_ic(zr_data, 'gamma_abc')
        return pact_key
