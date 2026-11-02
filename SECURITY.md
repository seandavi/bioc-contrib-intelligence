# Security

Please report vulnerabilities privately through GitHub's
[private vulnerability reporting](https://github.com/seandavi/bioc-contrib-intelligence/security/advisories/new),
not in a public issue.

In scope: the reviewer app (<https://bioc-reviews.seandavi.workers.dev>), in
particular sign-in, sessions, access to other reviewers' data, and anything that
could act on GitHub as a signed-in user. The app signs users in with a GitHub
App (Issues and Metadata permissions only) and keeps user tokens in an
encrypted, HttpOnly session cookie.

The data the app shows comes from public GitHub issues and r-universe, so
exposure of that data on its own isn't a vulnerability.
