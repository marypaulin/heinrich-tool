# Decimal statt float für Geldbeträge

Datum: 2026-09-25

Status: angenommen

**Kontext:** Beträge und Stunden liefen als `float` durch die Anwendung. Gerundet
wurde kaufmännisch nur bei Nettosumme und Umsatzsteuer (`_round_cents` in
`models.py`); die Zeilenbeträge blieben ungerundet, und `format_price` rundete
beim Drucken nebenbei über `:.2f` — nach dem Binärwert des Floats, nicht
kaufmännisch. Bei einem Stundensatz mit ungeradem Cent-Betrag widerspricht sich
das Dokument dann um einen Cent: 60,15 € × 0,5 h ergibt in der Zeile 30,07 €,
in der Nettosumme 30,08 €. Bei den heutigen Sätzen tritt das nicht auf, aber nur
zufällig — die Sätze stehen in der Konfiguration und können sich ändern.
Die Rundung war damit schon einmal Thema; `_round_cents` hatte das Problem nur
verschoben.

**Entscheidung:** Geldbeträge und Stunden sind durchgehend `Decimal`, von
Konfiguration und CSV bis zum gedruckten Dokument.

- Die Cent-Genauigkeit steht an genau einer Stelle: `money.py` mit `CENT` und
  `round_cents` (kaufmännisch, halbe Cents aufwärts).
- Gerundet wird dort, wo ein Betrag berechnet wird — nur bei Produkten
  (Zeilenbetrag, Umsatzsteuer). Summen von Cent-Beträgen bleiben exakt.
- `format_price` rundet nie. Einen ungerundeten Betrag lehnt es mit Fehler ab;
  das fängt vergessenes Runden in künftigem Code.
- Der CSV-Loader lehnt Stundensatz und Material mit mehr als zwei
  Nachkommastellen sowie Stunden außerhalb halber Schritte als Tippfehler ab,
  mit Zeilennummer, statt still zu runden.

**Alternativen:** `float` behalten und jeden Betrag an seiner Entstehungsstelle
mit `_round_cents` runden. Das genügt rechnerisch, hängt aber an Disziplin: Jede
neue Berechnung muss daran denken, und jede Rundung wandelt über `str` in
`Decimal` und zurück. Verworfen, weil es um Rechnungsbeträge geht und die
Genauigkeit vom Typ getragen werden soll, nicht von Sorgfalt.

**Konsequenzen:**

- `money.py` ist ein eigenes Modul, weil `models` `formatting` importiert und
  `formatting` `round_cents` braucht.
- `Decimal` und `float` lassen sich nicht mischen; neuer Code muss `Decimal`
  verwenden. Werte aus Daten werden aus Strings gebaut, Konstanten aus
  Ganzzahlen — nie aus Floats.
- Tests schreiben Beträge als `Decimal`-Literale. Ein Float würde in einem
  Vergleich trotzdem als gleich gelten, deshalb prüft ein Loader-Test den Typ
  ausdrücklich.
- Eine CSV mit drei Nachkommastellen bei Stundensatz oder Material bricht die
  Erzeugung ab. Ob das beim Kunden je absichtlich vorkommt, ist gefragt; falls ja,
  fällt diese Prüfung wieder weg.
