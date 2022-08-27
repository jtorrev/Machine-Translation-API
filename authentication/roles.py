from django.contrib.auth.models import Group

def create_a_role(name):
    role, _ = Group.objects.get_or_create(name=name)
    return role

class ROLES:
    APP_ROLES = {
        "ADMINISTRATOR": create_a_role(name="ADMINISTRATOR"),
        "USER": create_a_role(name="USER"),
    }

    @staticmethod
    def set_role(user, role):
        ROLES.APP_ROLES[role].user_set.add(user)
