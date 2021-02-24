from django.shortcuts import render, get_object_or_404,redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import Http404
from django.views import generic
from braces.views import SelectRelatedMixin
from posts import forms
from posts import models
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

# Create your views here.

User = get_user_model()

class PostList(SelectRelatedMixin, generic.ListView):
    model = models.Post
    select_related = ("user",)

class UserPosts(generic.ListView):
    model = models.Post
    template_name = "posts/user_post_list.html"

    def get_queryset(self):
        try:
            self.post_user = User.objects.prefetch_related("posts").get(username__iexact=self.kwargs.get("username"))
        
        except User.DoesNotExist:
            raise Http404
            
        else:
            return self.post_user.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_user"] = self.post_user
        return context


class PostDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Post
    select_related = ("user",)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact = self.kwargs.get("username"))

    def get_context_data(self, **kwargs):
        data= super().get_context_data(**kwargs)

        comments_connected = models.Comment.objects.filter(blogpost=self.get_object()).order_by('-created_date')
        data['comments'] = comments_connected
        if self.request.user.is_authenticated:
            data['comment_form']=forms.CommentForm(instance=self.request.user)
        return data

    def post(self,request, *args, **kwargs):
        comment=models.Comment(text=request.POST.get('text'), author=self.request.user, blogpost=self.get_object())
        comment.save()
        return self.get(self,request, *args, **kwargs)

class CreatePost(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    fields = ('title', 'message')
    model = models.Post

    def form_valid(self,form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class DeletePost(LoginRequiredMixin, SelectRelatedMixin, generic.DeleteView):
    model = models.Post
    select_related = ("user",)
    success_url = reverse_lazy("posts:all")

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id = self.request.user.id)

    def delete(self, *args, **kwargs):
        messages.success(self.request, "Post Deleted")
        return super().delete(*args, **kwargs)



#@login_required
#def comment_remove(request,pk):
#    comment = get_object_or_404(comment,pk=pk)
#    post_pk=comment.post.pk
#    comment.delete()
#    return redirect('single', pk=post.pk)