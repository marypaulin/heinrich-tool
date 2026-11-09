# Eigenentwicklung statt kommerzieller Lösung

Datum: 2026-09-04

Status: angenommen

**Kontext:** Das Werkzeug war bis Ende 2026 befristet. Ab 2027 sollte der Kunde
auf eine kommerzielle Lösung wechseln — unter anderem wegen der ab 2028
verpflichtenden E-Rechnung. Der Kunde hat die Lösung ausprobiert und sich dagegen
entschieden. Damit stand die Fortführung dieses Projekts zur Entscheidung.

**Entscheidung:** Die Eigenentwicklung wird fortgeführt und auf mehrere Jahre
ausgelegt. Die E-Rechnung nach ZUGFeRD wird Bestandteil dieses Werkzeugs; Termin
01.01.2028.

**Die Gründe des Kunden, in seiner Gewichtung:**

1. *Umstellungsaufwand.* Die kommerzielle Lösung hätte eine Anpassung des eigenen
   Arbeitsablaufs an deren Format verlangt. Er empfand das als Einengung.
2. *Abhängigkeit von einem Abomodell.* Laufende Kosten ohne Einfluss auf die
   Preisentwicklung — die Sorge vor einer späteren Vervielfachung war explizit.
3. *Kontrolle.* Er will nachvollziehen können, was mit seinen Daten passiert, und
   bevorzugt ein lokal laufendes Werkzeug gegenüber einem ausgelagerten Dienst.

**Ausdrücklich nicht der Grund:** Die kommerzielle Lösung wurde nur kurz getestet
— nicht lange genug, um fachliche Lücken festzustellen. Es ist kein
Anwendungsfall bekannt, den sie nicht abgedeckt hätte. Dies ist eine Präferenz-
und Risikoentscheidung, keine Funktionsentscheidung. Wer diesen Eintrag später
liest, soll daraus nicht ableiten, das fremde Werkzeug habe es nicht gekonnt.

**Alternativen:** Wechsel auf die kommerzielle Lösung wie ursprünglich geplant.
Verworfen aus den drei genannten Gründen.

**Konsequenzen:**

- Der Zeithorizont ändert sich grundlegend: Entscheidungen sind ab jetzt auf
  Jahre zu bewerten, nicht auf eine Restlaufzeit. Das betrifft Testabdeckung,
  Abhängigkeiten und Versionierung.
- Die E-Rechnung wird von einer Erweiterungsidee zur Pflichtaufgabe mit hartem
  Termin.
- Der Kunde tauscht die Abhängigkeit von einem Anbieter gegen die Abhängigkeit
  von einer einzelnen Entwicklerin. Nachvollziehbarkeit, Dokumentation und
  grundsätzliche Übergebbarkeit werden damit Teil der Leistung, nicht Beiwerk.
- Die verworfene Option kann zurückkehren: Da kein fachlicher Mangel festgestellt
  wurde, verschiebt sich die Rechnung, sobald der Wartungsaufwand die Kosten
  einer Lizenz übersteigt. Kein Grund zum Handeln, aber ein Grund, den Aufwand im
  Blick zu behalten.
