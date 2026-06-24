from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Post, Category, Comment, UserInfo, Skills, Jobs


class CommentInline(admin.TabularInline):
    """Post ichida commentlarni ko'rsatish"""
    model = Comment
    extra = 0
    fields = ('author', 'body', 'created', 'is_approved')
    readonly_fields = ('author', 'body', 'created')
    can_delete = True
    show_change_link = True
    classes = ('collapse',)  # Yig'iladigan qilib


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'author',
        'cat',  # Qo'shildi
        'publish',
        'status',
        'photo_preview',  # Rasm preview
        'comment_count'  # Commentlar soni
    )
    list_display_links = ('title', 'slug')
    list_filter = (
        'status',
        'publish',
        'author',
        'cat',  # Qo'shildi
    )
    list_editable = ('status',)  # Qayta ishga tushirildi
    search_fields = ('title', 'body', 'slug')
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created', 'updated', 'photo_preview')  # Qo'shildi
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'slug', 'cat', 'photo', 'photo_preview', 'body')
        }),
        ('Muallif va holat', {
            'fields': ('author', 'status', 'publish')
        }),
        ('Vaqt', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )
    inlines = [CommentInline]
    actions = ['make_published', 'make_draft']  # Qo'shildi

    def photo_preview(self, obj):
        """Rasm preview"""
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="100" height="100" style="object-fit:cover;" />')
        return "Rasm yo'q"

    photo_preview.short_description = 'Rasm preview'

    def comment_count(self, obj):
        """Commentlar soni"""
        return obj.comments.count()

    comment_count.short_description = 'Izohlar soni'

    def make_published(self, request, queryset):
        """Tanlangan postlarni publish qilish"""
        queryset.update(status='published')

    make_published.short_description = "Tanlanganlarni chop etish"

    def make_draft(self, request, queryset):
        """Tanlangan postlarni draft qilish"""
        queryset.update(status='draft')

    make_draft.short_description = "Tanlanganlarni draftga o'tkazish"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'post_count')
    list_display_links = ('name',)
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

    def post_count(self, obj):
        """Kategoriyadagi postlar soni"""
        return obj.post_set.count()

    post_count.short_description = 'Postlar soni'


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'email',
        'phone_number',
        'job',
        'works_completed',
        'years_of_experience'
    )
    list_display_links = ('full_name',)
    list_filter = ('job', 'skills')  # Filter uchun mos maydonlar
    search_fields = ('name', 'surname', 'email', 'phone_number')
    readonly_fields = ('id',)
    fieldsets = (
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('name', 'surname', 'job', 'email', 'phone_number')
        }),
        ('Professional ma\'lumotlar', {
            'fields': ('about_me', 'skills')
        }),
        ('Statistika', {
            'fields': ('works_completed', 'years_of_experience', 'total_clients', 'award_won')
        }),
    )
    filter_horizontal = ('skills',)  # ManyToMany uchun qulay
    ordering = ('-id',)

    def full_name(self, obj):
        """To'liq ism"""
        return f"{obj.name} {obj.surname}"

    full_name.short_description = 'To\'liq ism'
    full_name.admin_order_field = 'name'


@admin.register(Skills)
class SkillsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'percentage', 'user_count')
    list_display_links = ('name',)
    list_filter = ('percentage',)  # Foiz bo'yicha filter
    search_fields = ('name',)
    ordering = ('-percentage', 'name')

    def user_count(self, obj):
        """Skill egasi bo'lgan foydalanuvchilar soni"""
        return obj.user_infos.count()

    user_count.short_description = 'Foydalanuvchilar soni'


@admin.register(Jobs)
class JobsAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'user_count')
    list_display_links = ('job',)
    search_fields = ('job',)
    ordering = ('job',)

    def user_count(self, obj):
        """Bu lavozimdagi foydalanuvchilar soni"""
        return obj.user_infos.count()

    user_count.short_description = 'Foydalanuvchilar soni'


# Comment admin - agar alohida kerak bo'lsa
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'created', 'is_approved', 'short_body')
    list_display_links = ('author',)
    list_filter = ('is_approved', 'created', 'post')
    search_fields = ('author', 'body')
    actions = ['approve_comments', 'disapprove_comments']
    date_hierarchy = 'created'
    readonly_fields = ('post', 'author', 'body', 'created')
    fieldsets = (
        ('Izoh ma\'lumotlari', {
            'fields': ('post', 'author', 'body', 'created')
        }),
        ('Holat', {
            'fields': ('is_approved',)
        }),
    )

    def short_body(self, obj):
        """Qisqa matn"""
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body

    short_body.short_description = 'Matn'

    def approve_comments(self, request, queryset):
        """Commentlarni tasdiqlash"""
        queryset.update(is_approved=True)

    approve_comments.short_description = "Tanlangan izohlarni tasdiqlash"

    def disapprove_comments(self, request, queryset):
        """Commentlarni bekor qilish"""
        queryset.update(is_approved=False)

    disapprove_comments.short_description = "Tanlangan izohlarni bekor qilish"