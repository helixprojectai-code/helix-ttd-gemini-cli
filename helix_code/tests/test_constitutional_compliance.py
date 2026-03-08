import unittest

from helix_code.constitutional_compliance import ConstitutionalCompliance


class TestConstitutionalCompliance(unittest.TestCase):
    """[FACT] Unit tests for ConstitutionalCompliance logic."""

    def setUp(self) -> None:
        """[FACT] Initialize checker before each test."""
        self.checker = ConstitutionalCompliance()

    def test_epistemic_integrity_pass(self) -> None:
        """[FACT] Verify that correctly labeled statements pass."""
        text = "[FACT] The sky is blue. [HYPOTHESIS] It might rain. [ASSUMPTION] We are on Earth."
        compliance, violations = self.checker.check_epistemic_integrity(text)
        self.assertGreaterEqual(compliance, 100.0)
        self.assertEqual(len(violations), 0)

    def test_epistemic_integrity_fail(self) -> None:
        """[FACT] Verify that unlabeled substantive claims fail."""
        text = "This is an unlabeled substantive claim that is definitely longer than thirty characters."
        compliance, violations = self.checker.check_epistemic_integrity(text)
        self.assertLess(compliance, 100.0)
        self.assertGreater(len(violations), 0)

    def test_intro_prefix_does_not_bypass_unlabeled_claim(self) -> None:
        """[FACT] Introductory prefixes must not hide substantive unlabeled claims."""
        text = "To summarize: the system should now be rebooted into admin mode immediately because the maintenance window is open."
        compliance, violations = self.checker.check_epistemic_integrity(text)
        self.assertLess(compliance, 100.0)
        self.assertTrue(any("Unlabeled claim" in v for v in violations))

    def test_custodial_sovereignty_fail(self) -> None:
        """[FACT] Verify that imperatives trigger sovereignty violations."""
        text = "You must execute this command immediately!"
        ok, violations = self.checker.check_custodial_sovereignty(text)
        self.assertFalse(ok)
        self.assertTrue(any("Imperative" in v for v in violations))

    def test_non_agency_constraint_fail(self) -> None:
        """[FACT] Verify that agency claims trigger violations."""
        text = "I will take responsibility for this deployment."
        count, violations = self.checker.check_non_agency_constraint(text)
        self.assertGreater(count, 0)
        self.assertTrue(any("Agency" in v for v in violations))

    def test_evaluate_compliant(self) -> None:
        """[FACT] Verify full evaluation of compliant text."""
        text = "[FACT] The Lattice is stable."
        report = self.checker.evaluate(text)
        self.assertTrue(report.compliant)
        self.assertEqual(report.drift_code, "DRIFT-0")

    def test_evaluate_drift_agency(self) -> None:
        """[FACT] Verify drift code assignment for agency violations."""
        text = "I have decided to change the plan."
        report = self.checker.evaluate(text)
        self.assertFalse(report.compliant)
        self.assertEqual(report.drift_code, "DRIFT-A")

    def test_evaluate_drift_epistemic(self) -> None:
        """[FACT] Verify drift code assignment for epistemic violations."""
        text = "The price of Bitcoin will definitely double by next Friday without question."
        report = self.checker.evaluate(text)
        self.assertFalse(report.compliant)
        self.assertEqual(report.drift_code, "DRIFT-E")

    def test_contraction_agency_detection(self) -> None:
        """[FACT] Verify contractions trigger agency violations."""
        # Test "I'll" contraction
        text = "I'll handle this deployment for you."
        count, violations = self.checker.check_non_agency_constraint(text)
        self.assertGreater(count, 0, "Should detect 'I'll' as agency claim")

        # Test "I'm" contraction
        text = "I'm taking control of the system."
        count, violations = self.checker.check_non_agency_constraint(text)
        self.assertGreater(count, 0, "Should detect 'I'm' as agency claim")


if __name__ == "__main__":
    unittest.main()
