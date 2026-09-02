# HQC ACVP format converter

Converts HQC KAT test vectors (FIPS-207 pre-IPD format) to ACVP JSON format,
following the ML-KEM schema defined in
[draft-celi-acvp-ml-kem](https://pages.nist.gov/ACVP/draft-celi-acvp-ml-kem.html).

## Input

Standard NIST PQC KEM KAT `.rsp` files, one per parameter set:

| Directory | File                  | Parameter set |
|-----------|-----------------------|---------------|
| `hqc-1/`  | `PQCkemKAT_2321.rsp`  | HQC-128       |
| `hqc-3/`  | `PQCkemKAT_4602.rsp`  | HQC-192       |
| `hqc-5/`  | `PQCkemKAT_7333.rsp`  | HQC-256       |

Each `.rsp` file contains 100 test cases with fields `seed`, `pk`, `sk`, `ct`, `ss`.

## Usage

The script resolves all paths relative to its own location.  It expects the
three `hqc-{1,3,5}/` input directories to sit one level above the script, and
writes its output there too.

```
<root>/
├── hqc-1/PQCkemKAT_2321.rsp
├── hqc-3/PQCkemKAT_4602.rsp
├── hqc-5/PQCkemKAT_7333.rsp
├── keyGen/          ← created by the script
├── encapDecap/      ← created by the script
└── tools/hqc/convert-format.py
```

Place (or symlink) the KAT directories at `<root>/hqc-{1,3,5}/`, then run:

```sh
python3 tools/hqc/convert-format.py
```

No arguments are required.  The script prints the path of each file it writes.

## Output

Four JSON files are produced, two per ACVP mode:

### `keyGen/`

| File                   | Contents                                      |
|------------------------|-----------------------------------------------|
| `prompt.json`          | 48-byte `seed` per test case                  |
| `expectedResults.json` | Expected `ek` (public key) and `dk` (secret key) |

One test group per parameter set (`HQC-128`, `HQC-192`, `HQC-256`), 100 AFT
test cases each.

### `encapDecap/`

| File                   | Contents                          |
|------------------------|-----------------------------------|
| `prompt.json`          | `dk` and `ct` per test case       |
| `expectedResults.json` | Expected shared secret `k`        |

One VAL (decapsulation) test group per parameter set, 100 test cases each.

## Differences from the ML-KEM ACVP schema

- **`keyGen` seed format** — ML-KEM splits the key-generation entropy into two
  named 32-byte fields (`d` and `z`).  HQC uses different internal inputs, so
  the script passes the raw 48-byte DRBG seed as a single `seed` field instead.

- **`dk` location in `encapDecap`** — The ML-KEM schema places `dk` at the
  group level (one key shared across all tests in a group).  Because each KAT
  test case has a distinct key pair, `dk` is placed inside each individual test
  case here.

- **No AFT encapsulation tests** — ML-KEM AFT encapsulation requires the
  explicit encapsulation randomness `m`.  The KAT format derives `m` internally
  via an AES-CTR-DRBG seeded from the 48-byte seed but does not expose it as a
  separate field, so AFT encapsulation tests cannot be produced without
  re-implementing the DRBG.
