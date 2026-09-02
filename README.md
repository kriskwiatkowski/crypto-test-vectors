# crypto-test-vectors

A curated corpus of known-answer test vectors for cryptographic
implementations. It covers post-quantum and classical algorithms, and
combines vectors in the ACVP format, vectors imported from Project
Wycheproof, and vectors generated here for cases neither of those
covers.

The repository is data, not a test harness. It contains no
implementation of any algorithm and no test runner. The tooling under
`tools/` exists only to generate, validate and package the data.

Releases are published as a single archive, `crypto-test-vectors-<version>.zip`.


## Layout

    vectors/
      acvp/           ACVP-format vectors, organised by algorithm and revision
      wycheproof/     vendored, unmodified, from Project Wycheproof
      custom/         generated here; one directory per vector family
    tools/
      convert/        tools for converting formats of test vectors

## Imported material

`vectors/wycheproof/` are a vendored copy of upstream, refreshed by `tools/vendor/`
and never edited by hand. The upstream commit is recorded in the manifest.
A correction to imported
material belongs upstream; if a local divergence is unavoidable it is
added as a new file under `vectors/custom/` and the reason is stated in
that family's README, rather than by patching the import.

## Contributing

New vectors under `vectors/custom/` need a family README, a schema, a
generator under `tools/generate/`, and a manifest entry. A description of how
to regenerate the data or it's origin is what makes it possible to correct it later.

