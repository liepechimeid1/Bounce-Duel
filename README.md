# Bounce Duel

Een 1v1 Pong-achtig spel gebouwd met Pygame voor de informatica schoolopdracht.

## Beschrijving

Bounce Duel is een interactief spel waarbij twee spelers tegen elkaar spelen. Elke speler bestuurt een paddle (muur) aan de zijkant van het scherm om een bal heen en weer te slaan. De bal versnelt naarmate de ronde vordert, waardoor het spel steeds uitdagender wordt.

### Besturing

- **Speler 1 (Links, Cyaan):**
  - `W` - Paddle omhoog
  - `S` - Paddle omlaag

- **Speler 2 (Rechts, Magenta):**
  - `↑` (Pijltje omhoog) - Paddle omhoog
  - `↓` (Pijltje omlaag) - Paddle omlaag

- **Game Over scherm:**
  - `R` - Spel opnieuw starten

## Vereisten
- Space background assets (https://ansimuz.itch.io/space-background)
    Logo is inbegrepen met repository. Logo is zelf gemaakt
- Python
- Pygame

## Spelregels

1. **Doel:** Zorg dat de bal voorbij de paddle van je tegenstander gaat
2. **HP Systeem:** Elke speler begint met 5 HP (hartjes)
3. **Punten:** Als je tegenstander de bal mist, verliest hij/zij 1 HP
4. **Winnen:** De eerste speler wiens HP op 0 komt, verliest
5. **Snelheid:** De bal versnelt naarmate een ronde vordert
6. **Reset:** De snelheid wordt gereset wanneer iemand scoort
