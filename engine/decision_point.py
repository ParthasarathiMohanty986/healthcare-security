from .attribute_resolver import AttributeResolver
from .policy_evaluator import PolicyEvaluator
from audit.models import AuditLog


class PolicyDecisionPoint:
    """
    The main entry point for all access control decisions
    """

    def __init__(self):
        self.resolver = AttributeResolver()
        self.evaluator = PolicyEvaluator()

    def make_decision(
        self,
        user,
        resource_type: str,
        resource,
        is_emergency: bool = False,
        location: str = None
    ) -> dict:

        # Step 1: Resolve all attributes
        user_attrs = self.resolver.resolve_user_attributes(user)
        resource_attrs = self.resolver.resolve_resource_attributes(
            resource_type, resource
        )
        env_attrs = self.resolver.resolve_environment_attributes(
            is_emergency, location
        )

        # Step 2: Evaluate policy
        decision = self.evaluator.evaluate(
            user_attrs, resource_attrs, env_attrs
        )

        # Step 3: Log the decision
        AuditLog.objects.create(
            user=user,
            action=f"ACCESS_{resource_type.upper()}",
            resource_type=resource_type,
            resource_id=str(resource.id),
            access_granted=decision['access_granted'],
            is_emergency=is_emergency,
            details={
                'checks_passed': decision['checks_passed'],
                'checks_failed': decision['checks_failed'],
                'reasons': decision['reasons'],
                'user_role': user_attrs['role'],
                'user_department': user_attrs['department'],
                'clearance_level': user_attrs['clearance_level'],
                'resource_sensitivity': resource_attrs['sensitivity_level'],
            }
        )

        return {
            'access_granted': decision['access_granted'],
            'user': user_attrs,
            'resource': resource_attrs,
            'environment': env_attrs,
            'checks_passed': decision['checks_passed'],
            'checks_failed': decision['checks_failed'],
            'reasons': decision['reasons'],
        }