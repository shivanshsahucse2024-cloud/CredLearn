from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.views import View
from django.urls import reverse_lazy, reverse
from django.db.models import Count, Q, Sum, Case, When, IntegerField

from .models import Thread, Comment, Vote, Report

class ThreadListView(ListView):
    model = Thread
    template_name = 'discussion/thread_list.html' # Need to create this
    context_object_name = 'threads'
    ordering = ['-created_at'] # Default sort

    def get_queryset(self):
        queryset = super().get_queryset()
        sort = self.request.GET.get('sort', 'new')
        
        # Annotate with vote score
        queryset = queryset.annotate(
            upvotes=Count('votes', filter=Q(votes__value=1)),
            downvotes=Count('votes', filter=Q(votes__value=-1))
        ).annotate(
            vote_score=Case(
                When(upvotes__isnull=True, then=0),
                default=models.F('upvotes') - models.F('downvotes'),
                output_field=models.IntegerField()
            )
        )

        if sort == 'top':
            queryset = queryset.order_by('-vote_score', '-created_at')
        elif sort == 'hot':
            # Naive 'hot' sort: score + recency (simplified)
            # For real hot sort, we'd need a more complex algorithm or DB function
            # Here we just order by score for now, user can refine
            queryset = queryset.order_by('-vote_score', '-created_at') 
        else: # 'new'
            queryset = queryset.order_by('-created_at')
            
        return queryset

class ThreadDetailView(DetailView):
    model = Thread
    template_name = 'discussion/thread_detail.html' # Need to create this
    context_object_name = 'thread'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch top-level comments
        context['comments'] = self.object.comments.filter(parent__isnull=True).order_by('-created_at')
        return context

class ThreadCreateView(LoginRequiredMixin, CreateView):
    model = Thread
    fields = ['title', 'content']
    template_name = 'discussion/thread_form.html' # Need to create this
    success_url = reverse_lazy('discussion:thread_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, thread_id):
        thread = get_object_or_404(Thread, pk=thread_id)
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if content:
            parent_comment = None
            if parent_id:
                parent_comment = get_object_or_404(Comment, pk=parent_id)
            
            Comment.objects.create(
                thread=thread,
                author=request.user,
                content=content,
                parent=parent_comment
            )
        return redirect('discussion:thread_detail', pk=thread_id)

class VoteView(LoginRequiredMixin, View):
    def post(self, request):
        object_id = request.POST.get('object_id')
        content_type_model = request.POST.get('content_type') # 'thread' or 'comment'
        value = int(request.POST.get('value')) # 1 or -1
        
        if content_type_model == 'thread':
            model = Thread
        elif content_type_model == 'comment':
            model = Comment
        else:
            return JsonResponse({'error': 'Invalid content type'}, status=400)
            
        content_type = ContentType.objects.get_for_model(model)
        
        # Check if vote already exists
        vote, created = Vote.objects.get_or_create(
            user=request.request.user,
            content_type=content_type,
            object_id=object_id,
            defaults={'value': value}
        )
        
        if not created:
            if vote.value == value:
                # Toggle off if same value
                vote.delete()
            else:
                # Change vote
                vote.value = value
                vote.save()
        
        # Recalculate score to return
        obj = model.objects.get(pk=object_id)
        return JsonResponse({'score': obj.score})

class ReportView(LoginRequiredMixin, View):
    def post(self, request):
        # Implementation for simple reporting
        object_id = request.POST.get('object_id')
        content_type_model = request.POST.get('content_type')
        reason = request.POST.get('reason')
        
        if content_type_model == 'thread':
            model = Thread
        elif content_type_model == 'comment':
            model = Comment
        else:
            return JsonResponse({'error': 'Invalid content type'}, status=400)
            
        content_type = ContentType.objects.get_for_model(model)
        
        Report.objects.create(
            created_by=request.user,
            content_type=content_type,
            object_id=object_id,
            reason=reason
        )
        return JsonResponse({'status': 'success'})
