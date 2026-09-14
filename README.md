# ComplianceBench

An open evaluation of how AI models handle real compliance casework:
business and consumer onboarding, screening decisions, transaction
monitoring investigations, and regulatory gap analysis.

## Why it can exist

The right answer in a compliance case depends on the law plus the
institution's own confidential framework: its risk assessment, its risk
appetite, its rules. The same customer can be correctly approved at one
institution and correctly declined at another. That is why no compliance
test could ever publish its answer key: the key was confidential.

ComplianceBench removes the confidentiality, not the realism. Mynta AB is
a complete fictional Swedish e-money institution. Its entire framework is
in this repository, in `pack/`. Because the institution is fictional, its
confidential layer is public, and every case ships with a full answer key
that anyone can check against the same documents the model saw.

The cases were ruled on and corrected by Brayns' compliance professionals,
the same people whose judgement runs in the Brayns product. Their rulings
changed the cases, the rubrics and in places the framework itself.

Credits. Compliance adjudication: Augustinas Bilota, Anilla Lone Brannstrom.
Programme: Tara Abdi. Benchmark production: Brayns.
