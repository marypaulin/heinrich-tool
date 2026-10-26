# Manuelle Tests

Testfälle für das, was die automatischen Tests (`uv run pytest`) nicht
abdecken. Jeder Fall: Vorbereitung, Aktion, erwartetes Ergebnis.

## Setup-Skript

Prüft `scripts/setup.ps1` und `update.bat`. Nach jeder Änderung an einer der
beiden Dateien durchgehen.

Zwei Umgebungen:

- **Linux, `pwsh`:** nur der Update-Weg. Ordner-Dialog, winget und
  Verknüpfungen gibt es dort nicht; der Lauf endet bei den Verknüpfungen mit
  „Unerwarteter Fehler“ (`$env:WINDIR` fehlt). Das ist erwartet. Die Fälle
  sind so geschrieben, dass ein Agent sie selbstständig abarbeiten kann.
- **Windows-VM:** alles. Windows PowerShell 5.1, nicht `pwsh` — so läuft es
  beim Kunden. Ein Mensch führt die Fälle in der VM aus; vieles lässt sich nur
  ansehen (UAC-Abfrage, Ordner-Dialog, Umlaute, Icons, Browser-Tabs). Ein
  Agent auf dem Linux-Host kann anleiten, Ausgaben auswerten und die VM
  zurücksetzen, läuft aber nicht in der VM: Er bräuchte dort Git, und W1 setzt
  ein Windows ohne Git voraus.

**Voraussetzung für beide:** lokaler Working Tree sauber, alles committet und
gepusht (`git status`, `git log origin/main..`). Das Skript holt den Stand von
GitHub, nicht den lokalen. Sonst nicht testen, sondern erst committen und
pushen — nach Zustimmung, mit dem Skill `commit-work`. Keine Dateien in den
Klon kopieren, keine Commits im Klon.

### Linux (`pwsh`)

Arbeitsordner: ein Wegwerf-Klon von GitHub, nie das eigene Repo — das Skript
holt und synchronisiert den Ordner, in dem es liegt.

```bash
git clone https://github.com/marypaulin/heinrich-tool.git <tmp>/heinrich-tool
```

#### L1 — Update ohne Neues

- **Vorbereitung:** Klon auf dem Stand von `origin/main`.
- **Aktion:** `pwsh -NoProfile -File <tmp>/heinrich-tool/scripts/setup.ps1`
- **Erwartet:** Kein Git-/uv-Installationsschritt, kein Ordner-Dialog.
  `Already up to date.`, danach `uv sync` legt `.venv` an bzw. meldet nichts
  Neues. Ende mit „Unerwarteter Fehler“ bei den Verknüpfungen (s. o.).

#### L2 — Update mit neuem Commit

- **Vorbereitung:** Klon einen Commit zurücksetzen (`git reset --hard HEAD~1`).
  Braucht mindestens einen Commit auf `main` nach `e787de5`, sonst fehlt
  `setup.ps1` nach dem Zurücksetzen. Ändert der neueste Commit das Skript,
  läuft die alte Fassung und holt die neue — wie beim Kunden.
- **Aktion:** wie L1.
- **Erwartet:** `pull` spult vor (`Fast-forward`), `HEAD` danach gleich
  `origin/main`. Rest wie L1.

#### L3 — Lokale Änderung

- **Vorbereitung:** `echo test >> README.md` im Klon.
- **Aktion:** wie L1.
- **Erwartet:** Abbruch mit „Im Programmordner wurden Dateien geändert:“,
  darunter ` M README.md`, dann „Das Update wurde abgebrochen …“. Kein
  `pull`, kein `uv sync`; `HEAD` unverändert. Kein „Unerwarteter Fehler“.

### Windows-VM einrichten

KVM mit libvirt und virt-manager, Begründung in
`decisions/2026-10-19_kvm-statt-virtualbox.md`.

**Host:** Pakete `virt-manager`, `ovmf` (UEFI-Firmware) und `swtpm`
(TPM-Emulator); der eigene Benutzer in der Gruppe `libvirt` (wirkt nach dem
nächsten Login).

**ISO:** Windows 11 von Microsoft, **deutsche** Fassung — die Systemsprache
bestimmt die Codepage der Konsole, sonst sagt der Umlaut-Test in W1 nichts
über den Rechner des Kunden. Prüfsumme gegen Microsofts Angabe prüfen. Liegt
die ISO im Home-Verzeichnis, bietet virt-manager an, dem Benutzer
`libvirt-qemu` Zugriff zu geben; das ist nötig.

**VM `win11`** — im Assistenten „Customize configuration before install“
anhaken:

| Einstellung | Wert | Grund |
|---|---|---|
| Arbeitsspeicher | 6144 MiB | Windows 11 braucht mindestens 4 GB; der Host behält genug für sich |
| CPUs | 4 | Minimum ist 2; mehr beschleunigt Installation und Updates |
| Platte | 64 GiB, SATA | Mindestgröße von Windows 11; die Datei wächst erst mit dem Inhalt. Für SATA hat Windows eigene Treiber, für virtio nicht |
| Chipset | Q35 | |
| Firmware | `OVMF_CODE_4M.ms.fd` | UEFI mit Secure Boot und schon hinterlegten Microsoft-Schlüsseln. Bei `secboot.fd` wäre Secure Boot ohne Schlüssel inaktiv |
| TPM | Emulated, CRB, 2.0 | Pflicht für Windows 11 |
| Netzwerk | NAT, Modell `e1000e` | Windows bringt den Treiber mit |
| Kanal `org.qemu.guest_agent.0` | Typ `unix`, virtio | Ohne ihn bricht die Installation der Gast-Tools ab (s. u.); damit kann der Host Windows sauber herunterfahren |

virt-manager 4.1 legt den Kanal für den Guest Agent nicht an. Nachträglich,
bei ausgeschalteter VM:

```bash
cat > guest-agent-channel.xml <<'EOF'
<channel type='unix'>
  <target type='virtio' name='org.qemu.guest_agent.0'/>
</channel>
EOF
virsh -c qemu:///system attach-device win11 guest-agent-channel.xml --config
```

Nach „Begin Installation“ erscheint kurz „Press any key to boot from CD or
DVD…“ — sofort eine Taste drücken, sonst startet eine UEFI-Shell.

**Windows-Setup:**

- „Ich habe keinen Product Key“, Windows 11 Pro. Läuft unaktiviert mit
  Wasserzeichen.
- Gerätename `win11`.
- Microsoft-Konto: Ohne geht die Einrichtung nicht, W5 (OneDrive) braucht es
  ohnehin. Ein Konto, dessen OneDrive leer ist — neu angelegt, die Mailadresse
  darf schon existieren —, nicht das des Kunden. Der Benutzerordner heißt nach
  den ersten fünf Zeichen der Adresse (`C:\Users\<Name>`).
- „Synchronisieren Sie Ihr Microsoft-Konto mit Windows“ → „Nein, nicht
  synchronisieren“, damit die Test-VM nichts ins Konto zurückschreibt.
- OneDrive-Sicherung von Desktop und Dokumenten ablehnen.
- Testmonat von Microsoft 365 ablehnen: Der Word-Pfad wird hier nicht
  getestet, und der Testmonat verlängert sich kostenpflichtig.

**Danach:**

- Netzwerkverbindung in Windows auf „Getaktete Verbindung“ stellen, damit
  Windows nach jedem Zurücksetzen nicht dieselben Updates neu lädt.
- Gast-Tools von Fedora installieren — ohne sie kein Kopieren und Einfügen
  zwischen Host und VM:
  `https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-0.1.302-1/virtio-win-guest-tools.exe`
  (SHA-256 `d8ae9ea1e943384ac195e012cd36f82c3161620e5fc9529be4e42e6f420e222d`).
  Der Installer ist unsigniert, die UAC-Abfrage zeigt „Herausgeber:
  Unbekannt“. Die versionierte Adresse nehmen: `latest-virtio/` leitet auf
  `http://` weiter, und Edge blockt den Download. Die älteren
  `spice-guest-tools` von spice-space.org (2018) taugen nicht, ihre Treiber
  laden unter Windows 11 mit Secure Boot nicht. Kontrolle: Im Geräte-Manager
  hat „VirtIO Serial Driver“ kein Warndreieck, und
  `virsh -c qemu:///system qemu-agent-command win11 '{"execute":"guest-ping"}'`
  antwortet. Der Guest Agent erscheint nicht unter „Installierte Apps“, der
  Installer blendet seine Teilpakete dort aus.
- Nach der Installation die ISO auswerfen („SATA CDROM 1“ → „Disconnect“),
  sonst startet die VM nicht mehr, sobald die ISO gelöscht ist.

**Basiszustand:** virt-manager 4.1 kann von UEFI-VMs keine Snapshots anlegen.
Stattdessen wird das Plattenabbild der fertig eingerichteten VM zur
schreibgeschützten Basis `win11-base.qcow2`; die VM läuft auf einem
qcow2-Overlay unter dem alten Namen `win11.qcow2`, die VM-Konfiguration bleibt
unverändert. UEFI-Variablen (NVRAM) und TPM-Zustand liegen nicht im
Plattenabbild und ändern sich bei jedem Lauf; sie bekommen Basiskopien neben
dem Abbild und werden beim Zurücksetzen mit zurückgeholt.

Einmalig, bei ausgeschalteter VM:

```bash
sudo bash -s <<'EOF'
set -euo pipefail
cd /var/lib/libvirt/images
uuid=$(virsh -c qemu:///system domuuid win11)
[ "$(virsh -c qemu:///system domstate win11)" = "shut off" ] || { echo "VM läuft"; exit 1; }
[ ! -e win11-base.qcow2 ] || { echo "Basis existiert schon"; exit 1; }
mv win11.qcow2 win11-base.qcow2
chmod 444 win11-base.qcow2
qemu-img create -q -f qcow2 -b win11-base.qcow2 -F qcow2 win11.qcow2
chown --reference=win11-base.qcow2 win11.qcow2
cp -a /var/lib/libvirt/qemu/nvram/win11_VARS.fd win11-base_VARS.fd
cp -a "/var/lib/libvirt/swtpm/$uuid" win11-base-tpm
qemu-img info --backing-chain win11.qcow2
EOF
```

**Herunterfahren** über den Guest Agent — sauber, ohne in Windows zu klicken:

```bash
virsh -c qemu:///system shutdown win11 --mode agent
```

**Zurücksetzen** auf den Basiszustand, bei ausgeschalteter VM. Verwirft alles
seit dem Einfrieren; die Basis bleibt unberührt:

```bash
sudo bash -s <<'EOF'
set -euo pipefail
cd /var/lib/libvirt/images
uuid=$(virsh -c qemu:///system domuuid win11)
[ "$(virsh -c qemu:///system domstate win11)" = "shut off" ] || { echo "VM läuft"; exit 1; }
rm -f win11.qcow2
qemu-img create -q -f qcow2 -b win11-base.qcow2 -F qcow2 win11.qcow2
chown --reference=win11-base.qcow2 win11.qcow2
cp -a win11-base_VARS.fd /var/lib/libvirt/qemu/nvram/win11_VARS.fd
rm -rf "/var/lib/libvirt/swtpm/$uuid/tpm2"
cp -a win11-base-tpm/tpm2 "/var/lib/libvirt/swtpm/$uuid/tpm2"
EOF
```

**Netz trennen (W8):** in virt-manager bei der Netzwerkkarte den Haken
„Link state: active“ entfernen.

### Windows-VM

Ausgangszustand für W1: Basiszustand, also frisches Windows-Konto ohne Git,
ohne uv, ohne Installation von Heinrich Tool. Danach bauen die Fälle
aufeinander auf.

#### W1 — Erstlauf per Einzeiler

- **Aktion:** „Windows PowerShell“ aus dem Startmenü öffnen (nicht als
  Administrator), einfügen:
  `(irm https://raw.githubusercontent.com/marypaulin/heinrich-tool/main/scripts/setup.ps1).TrimStart([char]0xFEFF) | iex`
- **Erwartet:**
  - Kein roter Fehler vor dem ersten Schritt. Ohne `TrimStart` erscheint dort
    „Die Benennung "#" wurde nicht … erkannt“: `irm` behält den BOM als
    Zeichen vor der ersten Zeile.
  - Git wird per winget installiert (UAC-Abfrage), danach uv.
  - Ordner-Dialog öffnet **vor** dem PowerShell-Fenster.
  - Nach Wahl von z. B. `C:\Users\<Name>`: Klon nach
    `C:\Users\<Name>\heinrich-tool`, `uv sync` lädt Python 3.14.
  - „Fertig. Heinrich Tool startet …“ in Grün.
  - Das PowerShell-Fenster bleibt offen.
  - **Umlaute** in allen Meldungen richtig („wählen“, „Verknüpfungen“).

#### W2 — Verknüpfungen

- **Erwartet nach W1:**
  - Desktop: „Heinrich Tool“ mit App-Icon.
  - Startmenü: „Heinrich Tool“ und „Heinrich Tool aktualisieren“.
  - „Heinrich Tool“ startet die App (`scripts/run_windows.bat`), der Browser
    öffnet genau einen Tab.
  - Zweiter Klick bei laufender App: nur der Browser öffnet.

#### W3 — Update per `update.bat`

- **Aktion:** Doppelklick auf `update.bat` im Projektordner, danach auch über
  „Heinrich Tool aktualisieren“ im Startmenü.
- **Erwartet:** Keine Execution-Policy-Warnung, kein Ordner-Dialog,
  `Already up to date.`, `uv sync`, Verknüpfungen, „Fertig“. Fenster wartet auf
  Tastendruck. Umlaute richtig (Weg über `-File`, BOM).

#### W4 — Abbruch im Ordner-Dialog

- **Aktion:** Einzeiler, im Dialog „Abbrechen“.
- **Erwartet:** „Kein Ordner gewählt. Es wurde nichts installiert.“ Kein neuer
  Ordner. Kein „Unerwarteter Fehler“.

#### W5 — Ordner in OneDrive

- **Vorbereitung:** OneDrive in der VM angemeldet (sonst fehlt `$env:OneDrive`
  und der Fall ist nicht prüfbar).
- **Aktion:** Einzeiler, im Dialog einen Ordner unter OneDrive wählen.
- **Erwartet:** Ablehnung mit „Der Ordner liegt in OneDrive: …“. Nichts
  installiert.

#### W6 — Erneuter Einzeiler auf bestehende Installation

- **Aktion:** Einzeiler, im Dialog denselben Ort wie in W1 wählen.
- **Erwartet:** Kein Git-/uv-Schritt, kein neuer Klon, sondern Update wie W3.

#### W7 — Fremder Ordner mit dem Namen `heinrich-tool`

- **Vorbereitung:** leeren Ordner `heinrich-tool` (ohne `.git`) z. B. unter
  `C:\Temp` anlegen.
- **Aktion:** Einzeiler, im Dialog `C:\Temp` wählen.
- **Erwartet:** „Der Ordner … existiert schon, ist aber keine Installation …“.
  Ordner unverändert. Kein „Unerwarteter Fehler“.

#### W8 — Kein Netz

- **Vorbereitung:** Netz der VM trennen (s. o.).
- **Aktion:** `update.bat`.
- **Erwartet:** „Das Update konnte nicht geholt werden. Besteht eine
  Internetverbindung? …“. Kein „Unerwarteter Fehler“. Danach startet die App
  über die Verknüpfung trotzdem.

#### W9 — Update bei laufender App

Nur unter Windows prüfbar: Unter Linux fehlt `Get-NetTCPConnection`, das Skript
überspringt den Schritt dort.

- **Vorbereitung:** App über die Verknüpfung starten, Browser-Tab offen lassen.
  Ein neuer Commit auf `main` (sonst wie W3 ohne Neues).
- **Aktion:** `update.bat`.
- **Erwartet:** „Heinrich Tool wird beendet“ vor „Neueste Version wird geholt“,
  dann `Fast-forward`, „Fertig“. Danach startet die App über die Verknüpfung
  in der neuen Fassung, nicht nur der Browser.
