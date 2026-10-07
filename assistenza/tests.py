from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Cliente, Postazione


class AssistenzaTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser('admin', password='x')
        self.normale = User.objects.create_user('utente', password='x')
        self.cliente = Cliente.objects.create(nome='Rossi Srl')
        self.pc = Postazione.objects.create(cliente=self.cliente, nome='Segreteria', rustdesk_id='123456789')

    def test_utente_non_superuser_negato(self):
        self.client.force_login(self.normale)
        self.assertEqual(self.client.get(reverse('assistenza-list')).status_code, 403)
        self.assertEqual(self.client.post(reverse('assistenza-connetti', args=[self.pc.pk])).status_code, 403)

    def test_anonimo_rimandato_al_login(self):
        self.assertEqual(self.client.get(reverse('assistenza-list')).status_code, 302)

    def test_lista_e_ricerca(self):
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse('assistenza-list')), 'Segreteria')
        self.assertNotContains(self.client.get(reverse('assistenza-list'), {'q': 'zzz'}), 'Segreteria')

    def test_connetti_registra_e_rimanda_a_rustdesk(self):
        self.client.force_login(self.admin)
        r = self.client.post(reverse('assistenza-connetti', args=[self.pc.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r['Location'], 'rustdesk://123456789')
        self.pc.refresh_from_db()
        self.assertIsNotNone(self.pc.ultima_connessione)

    def test_connetti_rifiuta_get(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('assistenza-connetti', args=[self.pc.pk])).status_code, 405)

    def test_id_non_valido(self):
        from django.core.exceptions import ValidationError
        p = Postazione(cliente=self.cliente, nome='x', rustdesk_id="1;rm -rf")
        with self.assertRaises(ValidationError):
            p.full_clean()

    @override_settings(RUSTDESK_ID_SERVER='rd.example.it', RUSTDESK_PUBLIC_KEY='KEY123=')
    def test_script_contengono_server_e_chiave(self):
        self.client.force_login(self.admin)
        for sistema in ('windows', 'linux'):
            r = self.client.get(reverse('assistenza-script', args=[sistema]))
            body = r.content.decode()
            self.assertIn('rd.example.it', body)
            self.assertIn('KEY123=', body)

    @override_settings(RUSTDESK_ID_SERVER='', RUSTDESK_PUBLIC_KEY='')
    def test_script_non_configurato_rimanda(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('assistenza-script', args=['windows'])).status_code, 302)


class StatoOnlineTests(TestCase):
    def test_classificazione_risposte_hbbs(self):
        from . import services
        # risposte reali di hbbs osservate in produzione
        self.assertFalse(services._classify(b'Z\x02\x18\x02'))   # OFFLINE
        self.assertFalse(services._classify(b'Z\x00'))            # ID_NOT_EXIST
        self.assertIsNone(services._classify(b'Z\x02\x18\x03'))   # LICENSE_MISMATCH
        self.assertTrue(services._classify(b'Z\x05\n\x03abc'))    # risposta di successo

    def test_frame_e_varint(self):
        from . import services
        self.assertEqual(services._frame(b'abcd'), b'\x10abcd')
        self.assertEqual(services._varint(300), b'\xac\x02')

    @override_settings(RUSTDESK_ID_SERVER='127.0.0.1', RUSTDESK_PUBLIC_KEY='K=')
    def test_lista_mostra_stato(self):
        from unittest import mock
        admin = get_user_model().objects.create_superuser('a2', password='x')
        c = Cliente.objects.create(nome='C')
        Postazione.objects.create(cliente=c, nome='Acceso', rustdesk_id='111111111')
        Postazione.objects.create(cliente=c, nome='Spento', rustdesk_id='222222222')
        async def finto(ids):
            return {'111111111': True, '222222222': False}
        self.client.force_login(admin)
        with mock.patch('assistenza.services.fetch_online_states', finto):
            r = self.client.get(reverse('assistenza-list'))
        self.assertContains(r, 'Online')
        self.assertContains(r, 'Offline')
        self.assertIsNotNone(Postazione.objects.get(rustdesk_id='111111111').ultimo_online)
        self.assertIsNone(Postazione.objects.get(rustdesk_id='222222222').ultimo_online)
