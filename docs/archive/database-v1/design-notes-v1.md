1. Metric
   Aktuell feste Felder:
   cpu_usage
   ram_usage
   storage_usage
   temperature
   uptime

   → Für V1 super.
   → Später prüfen wir, ob jedes Device wirklich alle diese Werte besitzt.

2. Interface
   ip_address direkt am Interface
   → reicht erstmal.
   → mehrere IPs pro Interface wären später eine Erweiterung.

3. Location
   aktuell String am Device
   → reicht erstmal.
   → könnte später eigene Entität werden:
     Campus → Gebäude → Raum → Rack

4. Event.type
   aktuell einfach Attribut
   → später wahrscheinlich Enum/definierte Event-Typen.

5. User.role
   aktuell direkt beim User
   → reicht für ADMIN/USER o. Ä. vollkommen.
   → eigene Rollen-/Rechtetabellen wären aktuell Overkill.
