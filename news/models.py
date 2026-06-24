from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError


def validate_image_extension(value):
    """Rasm faylini tekshirish"""
    ext = value.name.split('.')[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        raise ValidationError('Faqat rasm fayllar yuklang (jpg, png, gif, webp)')


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Jobs(models.Model):
    job = models.CharField(max_length=150, verbose_name='Lavozim')

    class Meta:
        verbose_name = 'Lavozim'
        verbose_name_plural = 'Lavozimlar'

    def __str__(self):
        return self.job


class Skills(models.Model):
    name = models.CharField(max_length=50, verbose_name='Skill nomi')
    percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Foiz'
    )

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

    def __str__(self):
        return self.name


class UserInfo(models.Model):
    name = models.CharField(max_length=50, verbose_name='Ism')
    surname = models.CharField(max_length=50, verbose_name='Familiya')
    job = models.ForeignKey(
        Jobs,
        on_delete=models.PROTECT,  # DELETE CASCADE emas, PROTECT yaxshiroq
        related_name='user_infos',
        verbose_name='Lavozim'
    )
    email = models.EmailField(unique=True, verbose_name='Email')
    phone_number = models.CharField(max_length=50, verbose_name='Telefon')
    about_me = models.TextField(verbose_name="O'zim haqimda")
    skills = models.ManyToManyField(  # ManyToMany bo'lishi kerak
        Skills,
        related_name='user_infos',
        verbose_name='Skills'
    )
    works_completed = models.PositiveIntegerField(
        default=0,
        verbose_name='Bajarilgan ishlar'
    )
    years_of_experience = models.PositiveIntegerField(
        default=0,
        verbose_name='Tajriba yillari'
    )
    total_clients = models.PositiveIntegerField(
        default=0,
        verbose_name='Mijozlar soni'
    )
    award_won = models.PositiveIntegerField(
        default=0,
        verbose_name='Yutuqlar'
    )

    class Meta:
        verbose_name = 'Foydalanuvchi ma\'lumoti'
        verbose_name_plural = 'Foydalanuvchilar ma\'lumotlari'

    def __str__(self):
        return f'{self.name} {self.surname}'


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Kategoriya')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL')

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        ordering = ['id']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )

    title = models.CharField(max_length=250, verbose_name='Sarlavha')
    slug = models.SlugField(
        max_length=250,
        unique=True,  # Qo'shildi
        unique_for_date='publish',
        verbose_name='URL'
    )
    cat = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name='Kategoriya'
    )
    photo = models.ImageField(
        upload_to='photos/%Y/%m/%d/',
        validators=[validate_image_extension],
        verbose_name='Rasm'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name='Muallif'
    )
    body = RichTextField(verbose_name='Matn')
    publish = models.DateTimeField(default=timezone.now, verbose_name='Nashr vaqti')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    updated = models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqt')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Holat'
    )

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ('-publish',)
        indexes = [  # Performance uchun
            models.Index(fields=['-publish']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[
            self.publish.year,
            self.publish.month,
            self.publish.day,
            self.slug
        ])


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Post'
    )
    author = models.CharField(
        max_length=150,
        verbose_name='Muallif'
    )
    body = models.TextField(verbose_name='Matn')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    is_approved = models.BooleanField(default=False, verbose_name='Tasdiqlangan')  # Qo'shildi

    class Meta:
        verbose_name = 'Izoh'
        verbose_name_plural = 'Izohlar'
        ordering = ['created']

    def __str__(self):
        return f'{self.post.title} - {self.author}'

    def get_absolute_url(self):
        return reverse('post_list')