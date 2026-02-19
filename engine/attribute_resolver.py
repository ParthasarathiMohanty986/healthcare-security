from datetime import datetime
from authentication.models import User


class AttributeResolver:
    """
    Resolves all attributes of a user in real-time
    """

    def resolve_user_attributes(self, user: User) -> dict:
        now = datetime.now()
        current_time = now.time()

        # Check if within working hours
        within_working_hours = True
        if user.working_hours_start and user.working_hours_end:
            within_working_hours = (
                user.working_hours_start
                <= current_time <=
                user.working_hours_end
            )

        return {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'department': user.department,
            'specialization': user.specialization,
            'clearance_level': user.clearance_level,
            'certifications': user.get_certifications_list(),
            'is_emergency_authorized': user.is_emergency_authorized,
            'current_location': user.current_location,
            'within_working_hours': within_working_hours,
            'current_time': str(current_time),
            'current_date': str(now.date()),
        }

    def resolve_resource_attributes(self, resource_type: str, resource) -> dict:
        """
        Resolves attributes of the resource being accessed
        """
        base = {
            'resource_type': resource_type,
            'sensitivity_level': getattr(resource, 'sensitivity_level', 1),
            'required_clearance_level': getattr(
                resource, 'required_clearance_level', 1
            ),
            'required_department': getattr(
                resource, 'required_department', None
            ),
            'patient_consent': getattr(resource, 'patient_consent', True),
        }

        if resource_type == 'ehr':
            base['record_type'] = resource.record_type

        return base

    def resolve_environment_attributes(
        self, is_emergency: bool = False,
        location: str = None
    ) -> dict:
        """
        Resolves environmental/contextual attributes
        """
        now = datetime.now()
        hour = now.hour

        # Determine time of day
        if 6 <= hour < 14:
            shift = 'morning'
        elif 14 <= hour < 22:
            shift = 'evening'
        else:
            shift = 'night'

        return {
            'is_emergency': is_emergency,
            'location': location,
            'current_shift': shift,
            'timestamp': str(now),
        }