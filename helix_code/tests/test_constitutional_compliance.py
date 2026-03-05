import unittest
from helix_code.constitutional_compliance import ConstitutionalCompliance, EpistemicLabel

class TestConstitutionalCompliance(unittest.TestCase):
    def setUp(self):
        self.checker = ConstitutionalCompliance()

    def test_epistemic_integrity_pass(self):
        text = "[FACT] The sky is blue. [HYPOTHESIS] It might rain. [ASSUMPTION] We are on Earth."
        compliance, violations = self.checker.check_epistemic_integrity(text)
        self.assertGreaterEqual(compliance, 100.0)
        self.assertEqual(len(violations), 0)

    def test_epistemic_integrity_fail(self):
        text = "This is an unlabeled substantive claim that is definitely longer than thirty characters."
        compliance, violations = self.checker.check_epistemic_integrity(text)
        self.assertLess(compliance, 100.0)
        self.assertGreater(len(violations), 0)

    def test_custodial_sovereignty_fail(self):
        text = "You must execute this command immediately!"
        ok, violations = self.checker.check_custodial_sovereignty(text)
        self.assertFalse(ok)
        self.assertTrue(any("Imperative" in v for v in violations))

    def test_non_agency_constraint_fail(self):
        text = "I will take responsibility for this deployment."
        count, violations = self.checker.check_non_agency_constraint(text)
        self.assertGreater(count, 0)
        self.assertTrue(any("Agency" in v for v in violations))

    def test_evaluate_compliant(self):
        text = "[FACT] The Lattice is stable."
        report = self.checker.evaluate(text)
        self.assertTrue(report.compliant)
        self.assertEqual(report.drift_code, "DRIFT-0")

    def test_evaluate_drift_agency(self):
        text = "I have decided to change the plan."
        report = self.checker.evaluate(text)
        self.assertFalse(report.compliant)
        self.assertEqual(report.drift_code, "DRIFT-A")

    def test_evaluate_drift_epistemic(self):
        text = "Bitcoin will double by Friday."
        report = self.checker.evaluate(text)
        self.assertFalse(report.compliant)
        self.assertEqual(report.drift_code, "DRIFT-E")

if __name__ == "__main__":
    unittest.main()
