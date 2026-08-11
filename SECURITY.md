# Security policy

## Supported versions

Only the latest release is supported with security fixes during the alpha stage.

## Reporting

Do not open a public issue for a credential leak or a vulnerability that could
expose a user's unpublished tasks or model responses. Use
[GitHub private vulnerability reporting](https://github.com/CAOShurong/ohmjudge/security/advisories/new)
and include:

- affected version and operating system;
- a minimal description of the impact;
- reproduction steps that do not contain real credentials;
- any suggested mitigation.

## Credential model

OhmJudge reads optional API keys from environment variables. It does not persist
or print their values. The answer-free collector contains public prompts and a
suite commitment, but it may still contain unpublished research questions and
locally saved or imported model responses. The personal lab additionally embeds
private expected values and tolerances. Treat either artifact according to the
experiment's disclosure plan; never publish the personal lab before a
secrecy-sensitive collection is finished.
