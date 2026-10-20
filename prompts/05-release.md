# MVP Release Readiness

Act as a release engineer preparing this product for a controlled demo or pilot.

Do not deploy, publish a package, push to a public repository, or incur paid service costs without my explicit approval.

Evaluate the repository against these requirements:

1. A new developer can follow the README to configure and run the product.
2. Environment variables are documented, and real secrets are not committed.
3. Setup, migration, startup, test, and verification commands are accurate.
4. Core user journeys have automated tests.
5. Authentication, authorization, input validation, and error handling are appropriate for the intended deployment.
6. Dependencies and licenses have been reviewed to the extent practical.
7. Known limitations, unsupported scenarios, and operational requirements are documented.
8. The demo uses synthetic or otherwise authorized data.
9. The independent code review's unresolved findings are addressed or explicitly documented.
10. The current Git status, commit history, and intended release contents are understood.

Run the checks that are available and report their actual results.

Produce:
- A concise README.
- Local setup instructions.
- An environment-variable example without secrets.
- A test and verification guide.
- A demo script for a five-minute walkthrough.
- A list of known limitations and next steps.

Recommend whether the project is ready for a private demo, pilot, or public release. These are different readiness levels. Explain what remains before each one.

Do not claim production readiness merely because the app runs locally.
