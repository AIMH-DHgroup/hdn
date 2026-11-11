class AuthBackend(object):

    def has_perm(self, user_obj, perm, obj=None):
        if not obj:
            return False

        # Anyone can view an object
        elif perm == 'view':
            return True

        # Only the object owner can edit an object
        elif obj.data.Owner == user_obj.pk:
            return True

        return True
