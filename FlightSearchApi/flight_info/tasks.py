from celery import shared_task
from .models import Ucuslar, Havaalanlari
from datetime import datetime, timedelta
import random

@shared_task
def create_flight_info():
    """Nightly Celery beat job: adds 10 randomly generated flights (a mock feed, no external API)."""
    havaalanlari = list(Havaalanlari.objects.all())
    if len(havaalanlari) < 2:
        print("Need at least two airports.")
        return 0

    for _ in range(10):  # add 10 new flights per run
        kalkis_havaalani = random.choice(havaalanlari)
        varis_havaalani = random.choice(havaalanlari)
        
        while varis_havaalani == kalkis_havaalani:
            varis_havaalani = random.choice(havaalanlari)
        
        kalkis_zamani = datetime.now() + timedelta(days=random.randint(1, 30))
        inis_zamani = kalkis_zamani + timedelta(hours=random.randint(1, 12))
        
        Ucuslar.objects.create(
            kalkis_havaalani=kalkis_havaalani,
            varis_havaalani=varis_havaalani,
            kalkis_zamani=kalkis_zamani,
            inis_zamani=inis_zamani,
            fiyat=random.uniform(100, 1000)
        )

    print("Created 10 flights.")
    return 10
