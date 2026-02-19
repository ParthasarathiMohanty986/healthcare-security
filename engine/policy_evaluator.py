class PolicyEvaluator:
    """
    Evaluates whether access should be granted
    based on user, resource, and environment attributes
    """

    def evaluate(
        self,
        user_attrs: dict,
        resource_attrs: dict,
        env_attrs: dict
    ) -> dict:

        reasons = []
        checks_passed = []
        checks_failed = []

        # ── Check 1: Clearance Level ──
        user_clearance = user_attrs.get('clearance_level', 0)
        required_clearance = resource_attrs.get('required_clearance_level', 1)

        if user_clearance >= required_clearance:
            checks_passed.append(
                f"✅ Clearance Level: {user_clearance} >= {required_clearance}"
            )
        else:
            checks_failed.append(
                f"❌ Clearance Level: {user_clearance} < {required_clearance} required"
            )
            reasons.append("Insufficient clearance level")

        # ── Check 2: Department ──
        required_dept = resource_attrs.get('required_department')
        if required_dept:
            user_dept = user_attrs.get('department')
            user_role = user_attrs.get('role')

            if user_dept == required_dept or user_role in ['admin', 'emergency_staff']:
                checks_passed.append(
                    f"✅ Department: {user_dept} matches {required_dept}"
                )
            else:
                checks_failed.append(
                    f"❌ Department: {user_dept} != {required_dept} required"
                )
                reasons.append("Wrong department for this record")

        # ── Check 3: Patient Consent ──
        patient_consent = resource_attrs.get('patient_consent', True)
        if patient_consent:
            checks_passed.append("✅ Patient Consent: Granted")
        else:
            checks_failed.append("❌ Patient Consent: Not granted")
            reasons.append("Patient has not given consent")

        # ── Check 4: Emergency Override ──
        is_emergency = env_attrs.get('is_emergency', False)
        if is_emergency and user_attrs.get('is_emergency_authorized'):
            checks_passed.append("✅ Emergency Override: Authorized")
            # Emergency overrides clearance and department
            checks_failed = [
                c for c in checks_failed
                if 'Clearance' not in c and 'Department' not in c
            ]
            reasons = [
                r for r in reasons
                if 'clearance' not in r.lower() and 'department' not in r.lower()
            ]

        # ── Check 5: Role-based access ──
        role = user_attrs.get('role')
        sensitivity = resource_attrs.get('sensitivity_level', 1)

        role_min_clearance = {
            'doctor': 3,
            'nurse': 1,
            'admin': 5,
            'emergency_staff': 4,
            'lab_technician': 2,
            'receptionist': 1,
        }

        role_clearance = role_min_clearance.get(role, 1)
        if sensitivity <= role_clearance or user_clearance >= sensitivity:
            checks_passed.append(f"✅ Role Access: {role} can access sensitivity {sensitivity}")
        else:
            checks_failed.append(
                f"❌ Role Access: {role} cannot access sensitivity {sensitivity}"
            )
            reasons.append(f"Role {role} insufficient for sensitivity level {sensitivity}")

        # ── Final Decision ──
        access_granted = len(checks_failed) == 0

        return {
            'access_granted': access_granted,
            'checks_passed': checks_passed,
            'checks_failed': checks_failed,
            'reasons': reasons,
            'is_emergency': is_emergency,
        }