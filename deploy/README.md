# Deploy sul VPS

Pattern identico a MKRemote/FBOPortal: repo separato, utente di sistema dedicato,
venv proprio, sottodominio proprio. Differenza rispetto a FBOPortal: FBOAIGate è
ASGI (Channels/Daphne, per il terminale WebSocket in Fase 2), non WSGI.

## Stato attuale in produzione

Deployato su `https://aigate.fbosolution.it/` (VPS `94.177.161.127`, stesso VPS
di MKRemote/FBOPortal, hub WireGuard `wg1` separato — vedi STATO.md). Certificato
**Let's Encrypt vero** dal 2026-08-14 (rinnovo automatico via certbot, scade
2026-11-12). Il primo deploy (stesso giorno) era partito con un self-signed
provvisorio perché il DNS non era ancora propagato — l'accesso provvisorio via
IP:porta usato in quella finestra è stato rimosso appena confermato il DNS.

## Provisioning iniziale (una tantum, già fatto il 2026-08-14)

```
# da root sul VPS
adduser --system --group --home /opt/fboaigate fboaigate
mkdir -p /opt/fboaigate/app
chown fboaigate:fboaigate /opt/fboaigate/app

sudo -u fboaigate git clone https://github.com/lomax73/FBOAIGate.git /opt/fboaigate/app
cd /opt/fboaigate/app
sudo -u fboaigate python3 -m venv venv
sudo -u fboaigate venv/bin/pip install -r requirements.txt

# Postgres
sudo -u postgres psql -c "CREATE USER fboaigate WITH PASSWORD '...';" \
                        -c "CREATE DATABASE fboaigate OWNER fboaigate;"

# Chiave SSH di servizio della console (Fase 2), generata sul VPS stesso,
# poi autorizzata su ogni Target (~/.ssh/authorized_keys dell'utente ssh_user)
sudo -u fboaigate mkdir -p /opt/fboaigate/.ssh
sudo -u fboaigate ssh-keygen -t ed25519 -f /opt/fboaigate/.ssh/console_service -N ""

cp .env.example .env   # poi valorizzare DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS=aigate.fbosolution.it,
                        # DB_*, CONSOLE_SSH_PRIVATE_KEY_PATH=/opt/fboaigate/.ssh/console_service
                        # CHANNELS_REDIS_URL vuoto: un solo processo Daphne, basta il layer in-memory
sudo -u fboaigate venv/bin/python manage.py migrate
sudo -u fboaigate venv/bin/python manage.py collectstatic --noinput
sudo -u fboaigate venv/bin/python manage.py createsuperuser

cp deploy/fboaigate-web.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now fboaigate-web.service

# Certificato self-signed provvisorio (finché il DNS non è pronto)
mkdir -p /etc/ssl/fboaigate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/fboaigate/selfsigned.key -out /etc/ssl/fboaigate/selfsigned.crt \
  -subj '/CN=aigate.fbosolution.it'

cp deploy/nginx-fboaigate.conf /etc/nginx/sites-available/fboaigate
cp deploy/nginx-fboaigate-80.conf /etc/nginx/sites-available/fboaigate-80
ln -s /etc/nginx/sites-available/fboaigate /etc/nginx/sites-enabled/fboaigate
ln -s /etc/nginx/sites-available/fboaigate-80 /etc/nginx/sites-enabled/fboaigate-80
nginx -t && systemctl reload nginx
# poi, quando il DNS è pronto: certbot --nginx -d aigate.fbosolution.it
```

Porte 443/80 già aperte su UFW (condivise con le altre app, nessuna regola
nuova necessaria).

## Deploy di un aggiornamento

```
ssh mkremote-vps
cd /opt/fboaigate/app
sudo -u fboaigate git pull origin main
sudo -u fboaigate venv/bin/pip install -r requirements.txt
sudo -u fboaigate venv/bin/python manage.py migrate
sudo -u fboaigate venv/bin/python manage.py collectstatic --noinput
systemctl restart fboaigate-web.service
```

## Onboarding di un nuovo Target (host)

Per ogni nuovo `Target` (es. una futura VPS), la chiave pubblica della console
(`/opt/fboaigate/.ssh/console_service.pub`) va aggiunta manualmente a
`~/.ssh/authorized_keys` dell'utente `ssh_user` di quel Target — finché non
esisterà il pulsante di onboarding automatico in UI (vedi fase_8).

**`tmux` deve essere installato sul Target** (`apt install tmux`): il
terminale della console si aggancia a una sessione tmux persistente
(`console/consumers.py:TMUX_SESSION_COMMAND`), così un processo lanciato
dentro (es. `claude` mentre elabora) sopravvive alla chiusura del
WebSocket/scheda del browser.
