# KVM statt VirtualBox für die Windows-Test-VM

Datum: 2026-10-19

Status: angenommen

**Kontext:** `scripts/setup.ps1` und `update.bat` lassen sich vollständig nur
unter Windows testen. Entwickelt wird auf Linux Mint mit einem AMD-Prozessor
und aktivem Secure Boot; die Tests laufen deshalb in einer Windows-11-VM. Der
ursprüngliche Plan sah VirtualBox vor.

Seit Linux 6.12 schaltet das Kernel-Modul `kvm_amd` die Hardware-Virtualisierung
(AMD-V) schon beim Laden ein, also beim Booten, nicht erst beim Start einer VM.
AMD-V kann nur ein Hypervisor gleichzeitig nutzen; VirtualBox bricht dann mit
`VERR_SVM_IN_USE` ab.

**Entscheidung:** Die Test-VM läuft unter KVM, verwaltet von libvirt, bedient
über virt-manager.

KVM ist Teil des Linux-Kernels, Mint liefert es mit dem Ubuntu-Kernel mit und
lädt es automatisch, sobald der Prozessor Virtualisierung unterstützt. Die
Module sind von Canonical signiert und laden deshalb auch unter Secure Boot.
Installiert werden mussten nur die Werkzeuge darüber: libvirt (Dienst, der VMs
anlegt und startet), QEMU (bildet Platte, Netzwerkkarte und Bildschirm nach),
`swtpm` (TPM 2.0, Pflicht für Windows 11), OVMF (UEFI-Firmware) und
virt-manager (Oberfläche).

**Alternativen:** VirtualBox. Verworfen, weil es zwei Eingriffe in den
Systemstart des Hosts gebraucht hätte:

- Kernel-Parameter `kvm.enable_virt_at_load=0`, damit KVM AMD-V erst bei Bedarf
  belegt.
- Eine Freigabe der VirtualBox-Module unter Secure Boot. VirtualBox nutzt AMD-V
  über eigene Kernel-Module (`vboxdrv`), die auf dem Rechner gebaut werden und
  keine Signatur von Canonical tragen. Unter Secure Boot lädt der Kernel nur
  signierte Module. Nötig wäre ein eigener Schlüssel, einmalig als Machine
  Owner Key (MOK) in der Firmware registriert; danach signiert DKMS die Module
  bei Kernel-Updates selbst.

Beides ist einmalig machbar, ändert aber den Systemstart des
Entwicklungsrechners für ein Werkzeug, das nur zum Testen dient. KVM steht ohne
solche Änderung bereit.

**Konsequenzen:**

- Das Plattenabbild der VM liegt unter `/var/lib/libvirt/images/`.
- virt-manager 4.1 kann von UEFI-VMs keine Snapshots anlegen. Der Basiszustand
  für die Tests wird stattdessen als schreibgeschütztes Plattenabbild mit einem
  qcow2-Overlay darüber gehalten; Zurücksetzen heißt Overlay neu anlegen.
- VMs ohne Root-Rechte verwalten kann nur, wer in der Gruppe `libvirt` ist.
