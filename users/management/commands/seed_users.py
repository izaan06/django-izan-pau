from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Crea usuaris de prova i opcionalment relacions de follow'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Nombre d’usuaris a crear',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina tots els usuaris que no són superusuaris abans de crear-ne de nous',
        )
        parser.add_argument(
            '--with-follows',
            action='store_true',
            help='Si s’indica, crear també relacions de follow entre usuaris',
        )

    def handle(self, *args, **options):
        num_users = options['users']
        clear = options['clear']
        with_follows = options['with_follows']

        if clear:
            # Eliminar usuaris no superusuaris un a un (compatibilitat Djongo)
            users = list(User.objects.filter(is_superuser=False))
            deleted_count = len(users)
            for user in users:
                user.delete()
            self.stdout.write(self.style.SUCCESS(f'S\'han eliminat {deleted_count} usuaris no superusuaris.'))

        # Crear nous usuaris
        created_users = []
        for _ in range(num_users):
            username = fake.user_name()
            email = fake.email()
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            user.save()
            created_users.append(user)

        self.stdout.write(self.style.SUCCESS(f'S\'han creat {num_users} usuaris nous.'))

        # Crear relacions de follow si s'ha indicat
        if with_follows:
            for user in created_users:
                # Cada usuari seguirà entre 1 i 5 usuaris aleatoris
                others = [u for u in created_users if u != user]
                to_follow = random.sample(others, min(len(others), random.randint(1, 5)))
                for u in to_follow:
                    if hasattr(user, 'following'):
                        user.following.add(u)
            self.stdout.write(self.style.SUCCESS('S\'han creat relacions de follow entre usuaris.'))
