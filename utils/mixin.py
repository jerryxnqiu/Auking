from django.contrib.auth.decorators import login_required


# Explanation: when UserInfoView.as_view() is called, UserInfoView(LoginRequiredMixin, View) will be executed.
# However, the parent class "LoginRequiredMixin" does not have as_view(). The 2nd variable "View" is called, which
# has the as_view() function. In the end, it still execute login_required(view) function
class LoginRequiredMixin(object):
    
    @classmethod
    def as_view(cls, **initkwargs):
        # as_view from parent class
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)