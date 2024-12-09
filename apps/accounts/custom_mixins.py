from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.http import Http404
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404
from django.http import HttpResponseForbidden


class HandleExceptionMixin:
    def handle_exception(self, request, exception):
        messages.error(request, str(exception))
        return redirect(reverse(self.get_error_redirect_view()))

    def get_error_redirect_view(self):
        # Check if the view has set an error_redirect_view attribute
        if hasattr(self, 'error_redirect_view') and self.error_redirect_view:
            return self.error_redirect_view
        raise NotImplementedError("Subclasses must implement 'error_redirect_view' variable")

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404 as e:
            return self.handle_exception(request, e)
        except Exception as e:
            return self.handle_exception(request, e)
        



class GroupRequiredMixin:
    group_required = None

    def dispatch(self, request, *args, **kwargs):
        if self.group_required is not None and not self.request.user.groups.filter(name=self.group_required).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)




class DevicePermissionMixin(UserPassesTestMixin):
    def test_func(self):
        device = self.get_object()
        user = self.request.user

        # Check if the user is in the 'Management' group or if the device belongs to the user
        return user.groups.filter(name='Management').exists() or device.user == user

    def handle_no_permission(self):
        # Redirect or raise 404 based on your requirements
        # return HttpResponseForbidden("403 Forbidden - You do not have permission to access this resource.")
        raise PermissionDenied
        if self.request.user.groups.filter(name='Customers').exists():
            raise PermissionDenied
        else:
            return super().handle_no_permission()
