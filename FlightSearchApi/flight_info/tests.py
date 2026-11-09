from datetime import datetime, timedelta

from django.test import TestCase
from rest_framework.test import APIClient

from flight_info.models import Havaalanlari, Ucuslar
from flight_info.tasks import create_flight_info


class FlightSearchApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ist = Havaalanlari.objects.create(sehir="Istanbul", code="IST")
        self.esb = Havaalanlari.objects.create(sehir="Ankara", code="ESB")
        self.ayt = Havaalanlari.objects.create(sehir="Antalya", code="AYT")
        self.day = datetime(2026, 12, 1, 9, 0)
        Ucuslar.objects.create(kalkis_havaalani=self.ist, varis_havaalani=self.esb, kalkis_zamani=self.day,
                               inis_zamani=self.day + timedelta(hours=1), fiyat=450)
        Ucuslar.objects.create(kalkis_havaalani=self.ist, varis_havaalani=self.ayt, kalkis_zamani=self.day,
                               inis_zamani=self.day + timedelta(hours=1, minutes=20), fiyat=900)
        Ucuslar.objects.create(kalkis_havaalani=self.esb, varis_havaalani=self.ist,
                               kalkis_zamani=self.day + timedelta(days=1),
                               inis_zamani=self.day + timedelta(days=1, hours=1), fiyat=300)

    def login(self):
        self.client.post("/api/register/", {"username": "pilot", "email": "pilot@example.com",
                                            "password": "Cockpit-2026!", "first_name": "A", "last_name": "B"})
        r = self.client.post("/api/login/", {"email": "pilot@example.com", "password": "Cockpit-2026!"})
        self.assertEqual(r.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")

    def flight(self, origin, dest, dep, arr):
        return {"kalkis_havaalani": origin, "varis_havaalani": dest, "kalkis_zamani": dep, "inis_zamani": arr,
                "fiyat": "500.00"}

    def test_search_by_route_date_and_price(self):
        self.assertEqual(len(self.client.get("/api/ucuslar/", {"from": "IST"}).data), 2)
        self.assertEqual(len(self.client.get("/api/ucuslar/", {"from": "ist", "to": "ESB"}).data), 1)
        self.assertEqual(len(self.client.get("/api/ucuslar/", {"date": "2026-12-02"}).data), 1)
        self.assertEqual(len(self.client.get("/api/ucuslar/", {"from": "IST", "max_price": "500"}).data), 1)

    def test_bad_search_parameters_return_400(self):
        self.assertEqual(self.client.get("/api/ucuslar/", {"date": "01-12-2026"}).status_code, 400)
        self.assertEqual(self.client.get("/api/ucuslar/", {"max_price": "cheap"}).status_code, 400)

    def test_writing_needs_a_token(self):
        r = self.client.post("/api/ucuslar/", self.flight("IST", "ESB", "2026-12-03T10:00", "2026-12-03T11:00"))
        self.assertEqual(r.status_code, 401)

    def test_create_flight_with_jwt_and_validation(self):
        self.login()
        ok = self.client.post("/api/ucuslar/", self.flight("IST", "ESB", "2026-12-03T10:00", "2026-12-03T11:00"))
        self.assertEqual(ok.status_code, 201)
        same = self.client.post("/api/ucuslar/", self.flight("IST", "IST", "2026-12-03T10:00", "2026-12-03T11:00"))
        self.assertEqual(same.status_code, 400)
        backwards = self.client.post("/api/ucuslar/", self.flight("IST", "ESB", "2026-12-03T10:00", "2026-12-03T09:00"))
        self.assertEqual(backwards.status_code, 400)

    def test_airport_lookup_by_code(self):
        r = self.client.get("/api/airport/", {"code": "ay"})
        self.assertEqual([a["code"] for a in r.data], ["AYT"])

    def test_nightly_job_adds_ten_valid_flights(self):
        before = Ucuslar.objects.count()
        self.assertEqual(create_flight_info(), 10)
        new = Ucuslar.objects.order_by("-id")[:10]
        self.assertEqual(Ucuslar.objects.count(), before + 10)
        for f in new:
            self.assertNotEqual(f.kalkis_havaalani, f.varis_havaalani)
            self.assertGreater(f.inis_zamani, f.kalkis_zamani)
