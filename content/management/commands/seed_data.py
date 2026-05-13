"""
Demo ma'lumotlar yaratish uchun command:
    python manage.py seed_data

Yaratadi:
- Admin foydalanuvchi (admin / admin123)
- Oddiy foydalanuvchi (user1 / user12345)
- 3 ta obuna rejasi
- 10 ta janr
- 12 ta aktyor
- 10 ta film
- 4 ta serial, har birida fasllar va epizodlar
- Har bir film/epizodga VideoFile
"""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from content.models import Genre, Actor, Movie, Series, Season, Episode, VideoFile
from subscriptions.models import SubscriptionPlan

User = get_user_model()


class Command(BaseCommand):
    help = "StreamPlay uchun demo ma'lumotlarni yaratadi."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("🎬 StreamPlay demo ma'lumotlarni yaratish boshlandi...\n"))

        self._create_users()
        self._create_plans()
        genres = self._create_genres()
        actors = self._create_actors()
        self._create_movies(genres, actors)
        self._create_series(genres, actors)

        self.stdout.write(self.style.SUCCESS("\n✅ Demo ma'lumotlar muvaffaqiyatli yaratildi!"))
        self.stdout.write(self.style.SUCCESS("\nLogin ma'lumotlari:"))
        self.stdout.write("  Admin:  admin / admin123")
        self.stdout.write("  User:   user1 / user12345")
        self.stdout.write(self.style.SUCCESS("\nSwagger: http://127.0.0.1:8000/api/docs/"))
        self.stdout.write(self.style.SUCCESS("Admin:   http://127.0.0.1:8000/admin/"))

    def _create_users(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin', email='admin@streamplay.uz', password='admin123',
                first_name='Admin', last_name='User',
            )
            self.stdout.write("  • Admin yaratildi: admin / admin123")
        if not User.objects.filter(username='user1').exists():
            User.objects.create_user(
                username='user1', email='user1@streamplay.uz', password='user12345',
                first_name='Ali', last_name='Valiyev',
            )
            self.stdout.write("  • User yaratildi: user1 / user12345")

    def _create_plans(self):
        plans_data = [
            {
                'name': 'Basic', 'slug': 'basic',
                'description': 'Asosiy reja — 1 ta qurilmada 720p sifatda ko\'rish.',
                'price': Decimal('39000'), 'currency': 'UZS',
                'period': 'monthly', 'duration_days': 30,
                'max_quality': '720p', 'max_concurrent_streams': 1,
                'allows_downloads': False,
            },
            {
                'name': 'Standard', 'slug': 'standard',
                'description': 'Standart reja — 2 ta qurilmada 1080p.',
                'price': Decimal('69000'), 'currency': 'UZS',
                'period': 'monthly', 'duration_days': 30,
                'max_quality': '1080p', 'max_concurrent_streams': 2,
                'allows_downloads': True,
            },
            {
                'name': 'Premium', 'slug': 'premium',
                'description': "Premium reja — 4 ta qurilmada 4K va ko'chirib olish.",
                'price': Decimal('119000'), 'currency': 'UZS',
                'period': 'monthly', 'duration_days': 30,
                'max_quality': '2160p', 'max_concurrent_streams': 4,
                'allows_downloads': True,
            },
        ]
        for data in plans_data:
            SubscriptionPlan.objects.get_or_create(slug=data['slug'], defaults=data)
        self.stdout.write(f"  • {len(plans_data)} ta obuna rejasi yaratildi")

    def _create_genres(self):
        names = [
            'Drama', 'Komediya', 'Jangari', 'Fantastika', 'Qo\'rqinchli',
            'Detektiv', 'Romantik', 'Tarixiy', 'Animatsiya', 'Hujjatli',
        ]
        genres = []
        for name in names:
            g, _ = Genre.objects.get_or_create(name=name)
            genres.append(g)
        self.stdout.write(f"  • {len(genres)} ta janr yaratildi")
        return genres

    def _create_actors(self):
        names = [
            'Leonardo DiCaprio', 'Brad Pitt', 'Scarlett Johansson', 'Tom Hanks',
            'Morgan Freeman', 'Meryl Streep', 'Robert Downey Jr.', 'Natalie Portman',
            'Denzel Washington', 'Emma Stone', 'Christian Bale', 'Anne Hathaway',
        ]
        actors = []
        for name in names:
            a, _ = Actor.objects.get_or_create(
                full_name=name,
                defaults={
                    'biography': f"{name} — mashhur aktyor.",
                    'birth_date': date(1970, 1, 1),
                },
            )
            actors.append(a)
        self.stdout.write(f"  • {len(actors)} ta aktyor yaratildi")
        return actors

    def _create_movies(self, genres, actors):
        movies_data = [
            ('Inception', 'Inception', 2010, 148, 'Christopher Nolan', 'PG-13', Decimal('8.8'), False,
             "Tushlar ichiga kirib, sirli g'oyalarni o'g'irlovchi jamoa haqidagi fantastik film."),
            ('The Shawshank Redemption', 'The Shawshank Redemption', 1994, 142, 'Frank Darabont', 'R',
             Decimal('9.3'), False, "Shawshank qamoqxonasida ikki mahbusning do'stligi haqida."),
            ('Pulp Fiction', 'Pulp Fiction', 1994, 154, 'Quentin Tarantino', 'R', Decimal('8.9'), True,
             "Los-Anjelesdagi jinoyat olami hikoyalari."),
            ('The Dark Knight', 'The Dark Knight', 2008, 152, 'Christopher Nolan', 'PG-13',
             Decimal('9.0'), False, "Betmen Gothamdagi Joker ga qarshi kurashadi."),
            ('Forrest Gump', 'Forrest Gump', 1994, 142, 'Robert Zemeckis', 'PG-13', Decimal('8.8'), False,
             "Sodda yurakli Forrest Gumpning hayot yo'li."),
            ('Interstellar', 'Interstellar', 2014, 169, 'Christopher Nolan', 'PG-13',
             Decimal('8.6'), True, "Insoniyatni qutqarish uchun kosmosga sayohat."),
            ('Parasite', 'Parasite', 2019, 132, 'Bong Joon-ho', 'R', Decimal('8.5'), True,
             "Ikki koreys oilasi o'rtasidagi sinfiy qarama-qarshilik."),
            ('The Godfather', 'The Godfather', 1972, 175, 'Francis Ford Coppola', 'R',
             Decimal('9.2'), False, "Italyan-amerikalik mafia oilasi haqida."),
            ('Fight Club', 'Fight Club', 1999, 139, 'David Fincher', 'R', Decimal('8.8'), True,
             "Ikki kishi yer osti jangchilar klubini tashkil qiladi."),
            ('La La Land', 'La La Land', 2016, 128, 'Damien Chazelle', 'PG-13',
             Decimal('8.0'), False, "Los-Anjelesdagi musiqachi va aktrisa sevgisi."),
        ]

        for i, (title, orig, year, duration, director, rating, imdb, premium, desc) in enumerate(movies_data):
            movie, created = Movie.objects.get_or_create(
                title=title,
                defaults={
                    'original_title': orig,
                    'description': desc,
                    'short_description': desc[:150],
                    'release_year': year,
                    'country': 'USA',
                    'language': 'en',
                    'duration_minutes': duration,
                    'director': director,
                    'age_rating': rating,
                    'imdb_rating': imdb,
                    'is_premium': premium,
                    'is_published': True,
                    'views_count': (i + 1) * 1000,
                },
            )
            if created:
                movie.genres.set([genres[i % len(genres)], genres[(i + 3) % len(genres)]])
                movie.actors.set([actors[i % len(actors)], actors[(i + 2) % len(actors)]])
                # Video fayllar
                for quality in ['480p', '720p', '1080p']:
                    VideoFile.objects.create(
                        movie=movie,
                        quality=quality,
                        hls_manifest_url=f'https://cdn.streamplay.uz/{movie.slug}/{quality}/master.m3u8',
                        duration_seconds=duration * 60,
                        bitrate_kbps={'480p': 1500, '720p': 3000, '1080p': 5000}[quality],
                        status='ready',
                    )
        self.stdout.write(f"  • {len(movies_data)} ta film yaratildi")

    def _create_series(self, genres, actors):
        series_data = [
            ('Breaking Bad', 'Breaking Bad', 2008, 'completed', 5,
             "Kimyo o'qituvchisi giyohvand moddalar ishlab chiqarishni boshlaydi.", Decimal('9.5')),
            ('Game of Thrones', 'Game of Thrones', 2011, 'completed', 8,
             "Westeros qit'asida temir taxt uchun kurash.", Decimal('9.2')),
            ('Stranger Things', 'Stranger Things', 2016, 'ongoing', 4,
             "1980-yillarda sirli voqealar bolalar orqali ochiladi.", Decimal('8.7')),
            ('The Witcher', 'The Witcher', 2019, 'ongoing', 3,
             "Maxluqlar ovchisi Geraltning sarguzashtlari.", Decimal('8.1')),
        ]

        for i, (title, orig, year, status, season_count, desc, imdb) in enumerate(series_data):
            series, created = Series.objects.get_or_create(
                title=title,
                defaults={
                    'original_title': orig,
                    'description': desc,
                    'short_description': desc[:150],
                    'release_year': year,
                    'country': 'USA',
                    'language': 'en',
                    'status': status,
                    'total_seasons': season_count,
                    'age_rating': 'R',
                    'imdb_rating': imdb,
                    'is_premium': i % 2 == 0,
                    'is_published': True,
                    'views_count': (i + 1) * 5000,
                },
            )
            if created:
                series.genres.set([genres[i], genres[(i + 2) % len(genres)]])
                series.actors.set([actors[(i * 2) % len(actors)], actors[(i * 2 + 1) % len(actors)]])

                total_eps = 0
                for s_num in range(1, season_count + 1):
                    season = Season.objects.create(
                        series=series,
                        number=s_num,
                        title=f"Fasl {s_num}",
                        release_year=year + s_num - 1,
                    )
                    ep_count = 8 + (s_num % 3)
                    for e_num in range(1, ep_count + 1):
                        episode = Episode.objects.create(
                            season=season,
                            number=e_num,
                            title=f"Epizod {e_num}",
                            description=f"{title} — Fasl {s_num}, Epizod {e_num}.",
                            duration_minutes=45,
                            air_date=date(year + s_num - 1, 1, 1) + timedelta(days=e_num * 7),
                            views_count=(i + 1) * 100,
                        )
                        total_eps += 1
                        # Har bir epizodga HLS manifest
                        VideoFile.objects.create(
                            episode=episode,
                            quality='1080p',
                            hls_manifest_url=f'https://cdn.streamplay.uz/{series.slug}/s{s_num}/e{e_num}/master.m3u8',
                            duration_seconds=45 * 60,
                            bitrate_kbps=5000,
                            status='ready',
                        )
                series.total_episodes = total_eps
                series.save(update_fields=['total_episodes'])

        self.stdout.write(f"  • {len(series_data)} ta serial yaratildi")
