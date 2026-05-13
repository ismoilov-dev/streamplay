from django.db import models
from django.utils.text import slugify


class Genre(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Janr'
        verbose_name_plural = 'Janrlar'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Actor(models.Model):
    full_name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    biography = models.TextField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='actors/', blank=True, null=True)

    class Meta:
        verbose_name = 'Aktyor'
        verbose_name_plural = 'Aktyorlar'
        ordering = ['full_name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.full_name)
            slug = base
            idx = 1
            while Actor.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                idx += 1
                slug = f"{base}-{idx}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class ContentBase(models.Model):
    """Film va Serial uchun umumiy maydonlar."""

    AGE_RATINGS = [
        ('G', 'G — Hammabop'),
        ('PG', 'PG — Ota-ona nazorati tavsiya etiladi'),
        ('PG-13', 'PG-13 — 13+'),
        ('R', 'R — 17+'),
        ('NC-17', 'NC-17 — 18+'),
    ]

    title = models.CharField(max_length=255, verbose_name='Nomi')
    original_title = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    release_year = models.PositiveIntegerField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=50, blank=True, default='en')
    age_rating = models.CharField(max_length=10, choices=AGE_RATINGS, default='PG-13')
    imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    trailer_url = models.URLField(blank=True)
    is_premium = models.BooleanField(default=False, verbose_name='Premium (obuna kerak)')
    is_published = models.BooleanField(default=True)
    views_count = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    genres = models.ManyToManyField(Genre, blank=True, related_name='%(class)ss')
    actors = models.ManyToManyField(Actor, blank=True, related_name='%(class)ss')

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:270] or 'item'
            slug = base
            idx = 1
            Klass = type(self)
            while Klass.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                idx += 1
                slug = f"{base}-{idx}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Movie(ContentBase):
    duration_minutes = models.PositiveIntegerField(blank=True, null=True, verbose_name='Davomiyligi (daqiqa)')
    director = models.CharField(max_length=150, blank=True)

    class Meta(ContentBase.Meta):
        verbose_name = 'Film'
        verbose_name_plural = 'Filmlar'


class Series(ContentBase):
    STATUS_CHOICES = [
        ('ongoing', 'Davom etmoqda'),
        ('completed', 'Tugagan'),
        ('cancelled', 'Bekor qilingan'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    total_seasons = models.PositiveIntegerField(default=0)
    total_episodes = models.PositiveIntegerField(default=0)

    class Meta(ContentBase.Meta):
        verbose_name = 'Serial'
        verbose_name_plural = 'Seriallar'


class Season(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='seasons')
    number = models.PositiveIntegerField(verbose_name='Fasl raqami')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    release_year = models.PositiveIntegerField(blank=True, null=True)
    poster = models.ImageField(upload_to='seasons/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Fasl'
        verbose_name_plural = 'Fasllar'
        unique_together = ('series', 'number')
        ordering = ['series', 'number']

    def __str__(self):
        return f"{self.series.title} — Fasl {self.number}"


class Episode(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes')
    number = models.PositiveIntegerField(verbose_name='Epizod raqami')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='episodes/', blank=True, null=True)
    air_date = models.DateField(blank=True, null=True)
    views_count = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Epizod'
        verbose_name_plural = 'Epizodlar'
        unique_together = ('season', 'number')
        ordering = ['season', 'number']

    def __str__(self):
        return f"{self.season} — Ep {self.number}: {self.title}"


class VideoFile(models.Model):
    """Video fayl va uning turli sifatdagi variantlari."""

    QUALITY_CHOICES = [
        ('360p', '360p'),
        ('480p', '480p'),
        ('720p', '720p HD'),
        ('1080p', '1080p Full HD'),
        ('1440p', '1440p 2K'),
        ('2160p', '2160p 4K'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Kutmoqda'),
        ('processing', 'Qayta ishlanmoqda'),
        ('ready', 'Tayyor'),
        ('failed', 'Xatolik'),
    ]

    # Film yoki epizodga tegishli (ikkisidan biri)
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name='video_files', blank=True, null=True,
    )
    episode = models.ForeignKey(
        Episode, on_delete=models.CASCADE, related_name='video_files', blank=True, null=True,
    )

    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES)
    file = models.FileField(upload_to='videos/', blank=True, null=True)
    hls_manifest_url = models.URLField(blank=True, help_text='HLS .m3u8 playlist URL')
    dash_manifest_url = models.URLField(blank=True, help_text='DASH .mpd manifest URL')
    size_bytes = models.BigIntegerField(default=0)
    duration_seconds = models.PositiveIntegerField(default=0)
    bitrate_kbps = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_encrypted = models.BooleanField(default=False, verbose_name='DRM shifrlangan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Video fayl'
        verbose_name_plural = 'Video fayllar'
        ordering = ['-created_at']

    def __str__(self):
        target = self.movie or self.episode or 'Noma\'lum'
        return f"{target} — {self.quality}"


class Subtitle(models.Model):
    video_file = models.ForeignKey(VideoFile, on_delete=models.CASCADE, related_name='subtitles')
    language = models.CharField(max_length=10, help_text="ISO 639-1 kodi, masalan: uz, en, ru")
    language_name = models.CharField(max_length=50, blank=True)
    file = models.FileField(upload_to='subtitles/', help_text='.vtt yoki .srt fayli')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Subtitr'
        verbose_name_plural = 'Subtitrlar'
        ordering = ['language']

    def __str__(self):
        return f"{self.video_file} — {self.language}"


class AudioTrack(models.Model):
    video_file = models.ForeignKey(VideoFile, on_delete=models.CASCADE, related_name='audio_tracks')
    language = models.CharField(max_length=10)
    language_name = models.CharField(max_length=50, blank=True)
    file = models.FileField(upload_to='audio/', blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Audio trek'
        verbose_name_plural = 'Audio treklar'
        ordering = ['language']

    def __str__(self):
        return f"{self.video_file} — {self.language}"
