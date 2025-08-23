from extranet.models import LeaveRequest, TeleworkRequest


def validation_context(request):
    """Context processor pour afficher les notifications de validation dans le menu."""
    if not request.user.is_authenticated or not hasattr(request.user, "profile"):
        return {
            "validation_count": 0,
            "leave_validation_count": 0,
            "telework_validation_count": 0,
        }

    user = request.user
    role = user.profile.role
    validation_count = 0
    leave_validation_count = 0
    telework_validation_count = 0

    # Pour les managers
    if role in ["manager", "admin"]:
        # Demandes de congé en attente de validation manager
        leave_pending = LeaveRequest.objects.filter(
            status="pending", user__profile__manager=user, manager_validated=False
        ).count()
        leave_validation_count += leave_pending
        validation_count += leave_pending

        # Demandes de télétravail en attente de validation manager
        telework_pending = TeleworkRequest.objects.filter(
            status="pending", user__profile__manager=user, manager_validated=False
        ).count()
        telework_validation_count += telework_pending
        validation_count += telework_pending

    # Pour les RH
    if role in ["rh", "admin"]:
        # Demandes de congé validées par manager mais en attente RH
        leave_rh_pending = LeaveRequest.objects.filter(
            status="pending",
            user__profile__rh=user,
            manager_validated=True,
            rh_validated=False,
        ).count()
        leave_validation_count += leave_rh_pending
        validation_count += leave_rh_pending

    return {
        "validation_count": validation_count,
        "leave_validation_count": leave_validation_count,
        "telework_validation_count": telework_validation_count,
    }
