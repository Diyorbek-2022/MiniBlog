from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, TemplateView  # TemplateView qo'shildi
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.db import models  # Qo'shildi - SearchListView uchun
from .models import Post, Category, Comment, UserInfo, Skills, Jobs
from .forms import CommentForm
from django.views.generic import TemplateView
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from .forms import ContactForm


# ============================================
# INDEX VIEW (Bosh sahifa)
# ============================================
class IndexTemplateView(TemplateView):
    """Bosh sahifa - UserInfo ma'lumotlarini ko'rsatish"""
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Birinchi UserInfo obyektini olish (yoki barchasini)
        try:
            context['user_info'] = UserInfo.objects.first()
        except UserInfo.DoesNotExist:
            context['user_info'] = None

        # Qo'shimcha ma'lumotlar
        context['skills'] = Skills.objects.all().order_by('-percentage')
        context['jobs'] = Jobs.objects.all()
        context['posts'] = Post.published.all()[:3]  # Oxirgi 3 ta post
        return context


# ============================================
# NEWS LIST VIEW (Postlar ro'yxati)
# ============================================
class NewsListView(ListView):
    """Barcha published postlar ro'yxati"""
    model = Post
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 4
    template_name = 'list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Kategoriyalar ro'yxati (filter uchun)
        context['categories'] = Category.objects.all()
        return context


# ============================================
# POST DETAIL VIEW (Post batafsil)
# ============================================
def post_detail(request, year, month, day, post):
    """Post batafsil ko'rish va comment qo'shish"""
    # Postni olish
    post = get_object_or_404(
        Post,
        slug=post,
        status="published",
        publish__year=year,
        publish__month=month,
        publish__day=day
    )

    # Commentlar (faqat tasdiqlanganlari)
    comments = post.comments.filter(is_approved=True)

    # Comment form
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            # Agar user login qilgan bo'lsa
            if request.user.is_authenticated:
                comment.author = request.user.username
            else:
                comment.author = "Anonim"  # yoki boshqa default qiymat
            comment.save()
            messages.success(request, 'Izohingiz qo\'shildi va tekshirilmoqda!')
            return HttpResponseRedirect(request.path)  # Sahifani yangilash
    else:
        form = CommentForm()

    # Qo'shimcha postlar (shu kategoriyadagi)
    related_posts = Post.published.filter(cat=post.cat).exclude(id=post.id)[:3]

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'related_posts': related_posts,
        'comment_count': comments.count(),
    }
    return render(request, 'detail.html', context)


# ============================================
# POST CREATE VIEW (Yangi post qo'shish)
# ============================================
class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Yangi post yaratish (faqat superuser)"""
    model = Post
    template_name = 'new_post.html'
    fields = ['title', 'slug', 'cat', 'photo', 'body', 'status']
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.publish = timezone.now()  # Hozirgi vaqt
        messages.success(self.request, 'Post muvaffaqiyatli yaratildi!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Post yaratishda xatolik yuz berdi!')
        return super().form_invalid(form)

    def test_func(self):
        """Faqat superuser yaratishi mumkin"""
        return self.request.user.is_superuser

    def handle_no_permission(self):
        """Ruxsat bo'lmasa"""
        messages.error(self.request, 'Sizda post yaratish uchun ruxsat yo\'q!')
        return HttpResponseRedirect(reverse_lazy('post_list'))


# ============================================
# POST UPDATE VIEW (Postni tahrirlash)
# ============================================
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Postni tahrirlash (faqat author yoki superuser)"""
    model = Post
    template_name = 'edit_post.html'
    fields = ['title', 'slug', 'cat', 'photo', 'body', 'status']
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        form.instance.updated = timezone.now()
        messages.success(self.request, 'Post muvaffaqiyatli yangilandi!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Post yangilashda xatolik yuz berdi!')
        return super().form_invalid(form)

    def test_func(self):
        """Author yoki superuser tahrirlashi mumkin"""
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.is_superuser

    def handle_no_permission(self):
        """Ruxsat bo'lmasa"""
        messages.error(self.request, 'Sizda bu postni tahrirlash uchun ruxsat yo\'q!')
        return HttpResponseRedirect(reverse_lazy('post_list'))


# ============================================
# POST DELETE VIEW (Postni o'chirish)
# ============================================
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Postni o'chirish (faqat author yoki superuser)"""
    model = Post
    template_name = 'delete_post.html'
    success_url = reverse_lazy('post_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post muvaffaqiyatli o\'chirildi!')
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        """Author yoki superuser o'chirishi mumkin"""
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.is_superuser

    def handle_no_permission(self):
        """Ruxsat bo'lmasa"""
        messages.error(self.request, 'Sizda bu postni o\'chirish uchun ruxsat yo\'q!')
        return HttpResponseRedirect(reverse_lazy('post_list'))


# ============================================
# ADD COMMENT VIEW (Izoh qo'shish)
# ============================================
class AddCommentView(LoginRequiredMixin, CreateView):
    """Postga izoh qo'shish (faqat login qilganlar)"""
    model = Comment
    form_class = CommentForm
    template_name = 'add_comment.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        form.instance.post_id = self.kwargs['pk']
        form.instance.author = self.request.user.username
        form.instance.is_approved = False  # Admin tasdiqlashigacha
        messages.success(self.request, 'Izohingiz qo\'shildi! Admin tomonidan tekshirilgach chiqariladi.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Izoh qo\'shishda xatolik yuz berdi!')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=self.kwargs['pk'])
        return context


# ============================================
# CATEGORY VIEW (Kategoriya bo'yicha postlar)
# ============================================
class CategoryListView(ListView):
    """Kategoriya bo'yicha postlar ro'yxati"""
    model = Post
    template_name = 'category_list.html'  # Bu faylni yaratishingiz kerak
    context_object_name = 'posts'
    paginate_by = 4

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['cat_slug'])
        return Post.published.filter(cat=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


# ============================================
# 404 PAGE NOT FOUND (Xatolik sahifasi)
# ============================================
def pageNotFound(request, exception):
    """404 sahifa topilmadi"""
    return render(request, '404.html', status=404)


# ============================================
# 403 PAGE FORBIDDEN (Ruxsat yo'q)
# ============================================
def pageForbidden(request, exception=None):
    """403 ruxsat yo'q"""
    return render(request, '403.html', status=403)


# ============================================
# 500 PAGE ERROR (Server xatosi)
# ============================================
def pageError(request, exception=None):
    """500 server xatosi"""
    return render(request, '500.html', status=500)


# views.py ga qo'shimcha

# ContactView ni to'g'rilash


class ContactView(LoginRequiredMixin, FormView):
    """Bog'lanish formasi"""
    template_name = 'contact.html'  # bu template yaratilishi kerak
    form_class = ContactForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Bu yerda xabarni qayta ishlang: email yuborish, saqlash va h.k.
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']

        # Masalan: send_mail(subject, message, email, ['admin@example.com'])
        # Yoki ma'lumotlarni bazaga saqlash (Contact modeli kerak)

        messages.success(self.request, 'Xabaringiz muvaffaqiyatli yuborildi!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.')
        return super().form_invalid(form)


# ============================================
# SEARCH VIEW (Qidiruv)
# ============================================
class SearchListView(ListView):
    """Postlar ichidan qidirish"""
    model = Post
    template_name = 'search_results.html'  # Bu faylni yaratishingiz kerak
    context_object_name = 'posts'
    paginate_by = 4

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Post.published.filter(
                models.Q(title__icontains=query) |
                models.Q(body__icontains=query) |
                models.Q(author__username__icontains=query)
            )
        return Post.published.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
