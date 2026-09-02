#!/usr/bin/env python3
"""
Converts HQC KAT test vectors (FIPS-207-pre-ipd) to ACVP JSON format.

Input:  ../{hqc-1,hqc-3,hqc-5}/PQCkemKAT_*.rsp
Output: ../keyGen/{prompt,expectedResults}.json
        ../encapDecap/{prompt,expectedResults}.json

The ACVP format mirrors ML-KEM (draft-celi-acvp-ml-kem):
  keyGen  - AFT: seed -> ek, dk
  encapDecap - VAL (decapsulation): dk + ct -> k

Note: encapDecap AFT (encapsulation) tests are not generated because the
KAT format does not expose the encapsulation randomness (m) separately
from the 48-byte DRBG seed.
"""

import os
import re
import json

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

PARAM_SETS = [
    ("hqc-1", "HQC-128", "PQCkemKAT_2321.rsp"),
    ("hqc-3", "HQC-192", "PQCkemKAT_4602.rsp"),
    ("hqc-5", "HQC-256", "PQCkemKAT_7333.rsp"),
]

VS_ID = 42


def parse_kat(path):
    """Parse a NIST PQC KEM KAT .rsp file into a list of test-case dicts."""
    with open(path) as f:
        content = f.read()
    cases = []
    for block in re.split(r"\n\s*\n", content):
        block = block.strip()
        if not block or block.startswith("#"):
            continue
        tc = {}
        for line in block.splitlines():
            if "=" in line:
                k, _, v = line.partition("=")
                tc[k.strip()] = v.strip()
        if "count" in tc:
            cases.append(tc)
    return cases


def build_keygen(param_sets):
    """Build keyGen prompt and expectedResults structures."""
    prompt = {
        "vsId": VS_ID,
        "algorithm": "HQC",
        "mode": "keyGen",
        "revision": "FIPS207",
        "isSample": False,
        "testGroups": [],
    }
    results = {
        "vsId": VS_ID,
        "algorithm": "HQC",
        "mode": "keyGen",
        "revision": "FIPS207",
        "isSample": False,
        "testGroups": [],
    }

    for tg_id, (param_dir, param_set, kat_file) in enumerate(param_sets, start=1):
        cases = parse_kat(os.path.join(BASE_DIR, param_dir, kat_file))

        prompt["testGroups"].append({
            "tgId": tg_id,
            "testType": "AFT",
            "parameterSet": param_set,
            "tests": [
                {"tcId": i + 1, "seed": tc["seed"]}
                for i, tc in enumerate(cases)
            ],
        })
        results["testGroups"].append({
            "tgId": tg_id,
            "tests": [
                {"tcId": i + 1, "ek": tc["pk"], "dk": tc["sk"]}
                for i, tc in enumerate(cases)
            ],
        })

    return prompt, results


def build_encapdecap(param_sets):
    """Build encapDecap prompt and expectedResults structures.

    Generates VAL (decapsulation) groups only.  Each KAT test case provides a
    unique dk, so dk is included per-test rather than at group level (a minor
    deviation from the ML-KEM ACVP schema necessitated by the KAT format).
    """
    prompt = {
        "vsId": VS_ID,
        "algorithm": "HQC",
        "mode": "encapDecap",
        "revision": "FIPS207",
        "isSample": False,
        "testGroups": [],
    }
    results = {
        "vsId": VS_ID,
        "algorithm": "HQC",
        "mode": "encapDecap",
        "revision": "FIPS207",
        "isSample": False,
        "testGroups": [],
    }

    for tg_id, (param_dir, param_set, kat_file) in enumerate(param_sets, start=1):
        cases = parse_kat(os.path.join(BASE_DIR, param_dir, kat_file))

        prompt["testGroups"].append({
            "tgId": tg_id,
            "testType": "VAL",
            "parameterSet": param_set,
            "function": "decapsulation",
            "tests": [
                {"tcId": i + 1, "dk": tc["sk"], "ct": tc["ct"]}
                for i, tc in enumerate(cases)
            ],
        })
        results["testGroups"].append({
            "tgId": tg_id,
            "tests": [
                {"tcId": i + 1, "k": tc["ss"]}
                for i, tc in enumerate(cases)
            ],
        })

    return prompt, results


def write_json(directory, filename, data):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Wrote {path}")


def main():
    kg_prompt, kg_results = build_keygen(PARAM_SETS)
    ed_prompt, ed_results = build_encapdecap(PARAM_SETS)

    keygen_dir = os.path.join(BASE_DIR, "keyGen")
    encapdecap_dir = os.path.join(BASE_DIR, "encapDecap")

    write_json(keygen_dir, "prompt.json", kg_prompt)
    write_json(keygen_dir, "expectedResults.json", kg_results)
    write_json(encapdecap_dir, "prompt.json", ed_prompt)
    write_json(encapdecap_dir, "expectedResults.json", ed_results)


if __name__ == "__main__":
    main()
