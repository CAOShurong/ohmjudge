# Security policy

## Supported versions

Only the latest release is supported with security fixes during the alpha stage.

## Reporting

Do not open a public issue for a credential leak or a vulnerability that could
expose a user's unpublished tasks or model responses. Contact the repository
owner privately through their GitHub profile and include:

- affected version and operating system;
- a minimal description of the impact;
- reproduction steps that do not contain real credentials;
- any suggested mitigation.

## Credential model

OhmJudge reads optional API keys from environment variables. It does not persist
or print their values. Generated HTML files contain tasks and evaluation data;
treat a lab built from a private task file as sensitive until the evaluation is
finished.
