# Testen dieses Updates (ESP-IDF-Umstieg, Timing-Kalibrierung)

Dieser Branch stellt das Projekt von ESPHome-Deprecations auf einen aktuellen
Stand um und erzwingt (wie ESPHome es seit dem Wegfall der Arduino-Framework
Unterstützung verlangt) das ESP-IDF-Framework. Dabei wurde ein empirisch für
Arduino kalibrierter Timing-Wert (`TIMING_DELAY`, siehe
[PHCController.h](components/PHCController/PHCController.h)) unverändert
übernommen, aber nicht auf ESP-IDF neu vermessen. Bevor dieser Branch nach
`main` gemerged wird, sollte er auf echter Hardware getestet werden. Ein
Oszilloskop ist dafür in der Regel **nicht** nötig.

## 1. Debug-Logging gezielt aktivieren

Wichtig: Der globale `level:` ist keine reine Laufzeit-Einstellung, sondern
setzt zur **Compile-Zeit** die Obergrenze für alle `ESP_LOGD`-Aufrufe (auch
unser TX-Latenz-Log). Ein `logs:`-Override pro Komponente kann diese Grenze
nur nach **unten** verschieben, nie nach oben — `level: WARN` mit
`phc_controller: DEBUG` lässt ESPHome deshalb mit einem Konfigurationsfehler
abbrechen ("must not be less severe than the global log level").

Der globale Level muss also mindestens `DEBUG` sein. Um trotzdem nicht in
WLAN/API-Logs zu ersaufen, drosselt man stattdessen gezielt die eigentlich
lauten Standard-Komponenten:

```yaml
logger:
  level: DEBUG
  logs:
    wifi: WARN
    api: WARN
    api.connection: WARN
    mdns: WARN
    preferences: WARN
```

Die Liste ist ein Startpunkt, keine vollständige Aufzählung — je nach deiner
Config können weitere Komponenten (z. B. `sensor`, `text_sensor`) mit eigenem
DEBUG-Output dazukommen; bei Bedarf einfach mit demselben Muster ergänzen.

## 2. Die zwei eigentlichen Erfolgs-Kriterien beobachten

Das sind die Signale, die wirklich zählen, nicht die reine Latenzzahl:

- `"Device not responding! Is the device connected to the bus?"`
  ([AMD.cpp](components/AMD/AMD.cpp), [JRM.cpp](components/JRM/JRM.cpp)) —
  ein Modul hat nach `MAX_RESENDS` (20) Versuchen nie geantwortet. Das ist das
  harte Fehlersignal.
- `"Recieved bad message (checksum missmatch)"`
  ([PHCController.cpp](components/PHCController/PHCController.cpp)) — ein
  Frame kam korrupt an, oft ein Symptom von Timing-/Echo-Problemen.

Schalte im Normalbetrieb ein paar Lichter/Rollläden, warte etwas. Wenn diese
beiden Zeilen **nicht** auftauchen, passt das Timing bereits so wie es ist —
fertig, keine weiteren Schritte nötig.

## 3. Falls doch Probleme auftauchen: TIMING_DELAY kalibrieren

Das Debug-Log gibt dir die Stellschraube:

```
TX latency since last RX frame: 187 us
```

Das ist die komplette Software-Zeit vom letzten empfangenen Byte bis kurz vor
dem Losschicken der Antwort — **inklusive** des aktuellen `TIMING_DELAY`
(geloggt in `write_array()`, siehe
[PHCController.cpp](components/PHCController/PHCController.cpp)).

- Ziehe den reinen Verarbeitungs-Overhead ab: `gemessener Wert − aktueller
  TIMING_DELAY`.
- Der Zielwert ist ~250µs Gesamtlaufzeit (Richtwert des Original-STM-Controllers,
  keine hardware-exakte Spezifikation — die PHC-Module dürften Toleranz haben,
  wofür auch die Resend-Logik existiert).
- Passe `TIMING_DELAY` in
  [PHCController.h](components/PHCController/PHCController.h) in kleinen
  Schritten an (z. B. ±30µs), flashe neu, beobachte wieder Schritt 2.
  Iterativ, ohne zusätzliche Hardware.

## 4. Wann doch Mess-Hardware sinnvoll ist

Nur wenn Schritt 2+3 nicht zur Stabilität führen und unklar bleibt, ob die
Antwort zu früh oder zu spät kommt: ein günstiger USB-Logic-Analyzer (z. B.
mit PulseView/sigrok, ~10€) an A/B-Leitung und am Flow-Control-Pin als
Trigger reicht meist aus — einfacher als ein Oszilloskop, da es sich um ein
digitales Protokoll handelt, keine analoge Signalform. Ein echtes
Oszilloskop ist eigentlich nur nötig, wenn die Signalqualität am RS-485-Bus
selbst (Reflexionen, Pegel) geprüft werden soll, nicht fürs reine Timing.

## Kurzfassung

1. Global `level: DEBUG`, laute Standard-Komponenten (wifi, api, mdns, ...)
   gezielt auf WARN drosseln.
2. Auf "Device not responding" / "checksum missmatch" achten.
3. Keine Fehler → fertig. Fehler → `TIMING_DELAY` anhand des
   Latenz-Logs iterativ nachjustieren.
4. Logic-Analyzer nur als letzter Ausweg.
