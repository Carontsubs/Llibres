# Monitor de Còmics - Norma Còmics 📚

Aquest script de Python monitoritza una sèrie específica de la web de Norma Còmics (en aquest cas, *Monstress*) i envia una notificació per **Telegram** quan detecta que s'ha publicat un nou volum.

## 🚀 Com funciona
1. Utilitza `undetected-chromedriver` per navegar per la web esquivant les proteccions anti-bot (Cloudflare).
2. Compara els títols trobats amb una llista guardada localment a `llibres_vistos.json`.
3. Si troba títols nous, t'envia un missatge detallat per Telegram amb l'enllaç directe.

## 🛠️ Instal·lació

1. **Clona o descarrega** aquest repositori.
2. **Instal·la les dependències** necessàries:
   ```bash
   pip install -r requirements.txt