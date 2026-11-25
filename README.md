# "Mira Monte" railway station simulator (Python)

Console program that simulates one day of operation at a small railway station: train arrivals and departures through a single platform, a last-in-first-out train yard, and a VIP ticket office whose passengers are assigned to departing trains. It reads a scenario from CSV files and writes the results to CSV files.

Academic group project for the *Algorithms and Data Structures* course (CTeSP in Web and Mobile Development, IPLUSO — Instituto Politécnico da Lusofonia, Lisbon), developed by a group of students that included Pedro Caldeira. Written in Python, using only the standard library.

## What it does

- **Train operations:** for each scheduled arrival or departure, computes how long the platform is occupied (entering the platform, disembarking or boarding, moving to or from the yard) and checks each operation against the previous one for **overlapping platform use**. Conflicts, a full yard on arrival or an empty yard on departure are written to `erro.txt`.
- **Train yard:** modelled as a **stack** (`Parque`) — trains enter and leave through the same track, so the last train parked is the first to leave. Departures take the train at the top of the stack; arrivals park on top.
- **Ticket office:** modelled as a **queue** (`Bilheteira`) — passengers are served in order of arrival, after the office opens, with a fixed service time. Each passenger is then assigned to the first departure they can still reach that has a free VIP seat; passengers who cannot be placed are marked as having no seat.
- **Station board:** builds a timeline of which passengers are at the station at each relevant moment.
- **"Who follows whom":** each passenger may list people they follow; the program answers questions of the form "does A follow B?".

## Project structure

```
main.py              loads the scenario, runs the simulation, writes outputs, prints a summary
entidades.py         classes: Viagem, Parque (stack), Operacao, Pergunta, Passageiro, Bilheteira (queue)
operacoes.py         time conversion, platform occupation and conflict checks, passenger allocation, board
nome_do_problema.txt name of the scenario folder to run
Input/<scenario>/    parametros.csv, parque.csv, passageiros.csv, viagens.csv, questoes_seguidores.csv
```

Two scenarios are included: `problema_simples` and `problema_complexo`.

## Run

Requires Python 3.8+ (no external packages).

```bash
echo -n problema_simples > nome_do_problema.txt   # or problema_complexo
python main.py
```

Results are written to `Output/<scenario>/` (`viagens.csv`, `parque.csv`, `passageiros.csv`, `placar.csv`, `questoes_seguidores.csv` and `erro.txt`) and a summary is printed. Output of `problema_simples`:

```
============================================================
ESTACAO 'MIRA MONTE' - PROBLEMA_SIMPLES
============================================================

RESUMO:
  Viagens: 3 | Passageiros: 3 | Parque: 2

VIAGENS:
  10:00 | Chegada  | C04
  10:15 | Partida  | C04
  10:40 | Partida  | C01

PASSAGEIROS:
  09:55 Ana          -> 10:15
  09:56 Bernardo     -> 10:15
  09:57 Celia        -> 10:40

PARQUE FINAL: ['C03', 'C02']

SEGUIDORES:
  [SIM] Ana -> Bernardo
  [NAO] Bernardo -> Ana
  [SIM] Celia -> Ana
  [NAO] Celia -> Bernardo
```

In `problema_complexo` (16 operations, 18 passengers) the program places 16 passengers, reports two without a seat and logs one platform conflict between two arrivals.

## Input format

| File | Content |
|---|---|
| `parametros.csv` | `key,value` pairs: opening and closing times, yard capacity, VIP seats per train and the durations (in minutes) of each step |
| `parque.csv` | trains initially in the yard, one per line (the last line is the top of the stack) |
| `viagens.csv` | `time,Chegada|Partida,driver_id[,train]` |
| `passageiros.csv` | `arrival_time,name[,followed_name...]` |
| `questoes_seguidores.csv` | `follower,followed` pairs to check |

## Verification

Both scenarios were run with Python 3.13; the files generated in `Output/` were identical to the result files submitted with the project. There are no automated tests.

## Limitations

- The scenario is chosen by editing `nome_do_problema.txt` rather than by a command-line argument.
- Input files are assumed to be well formed; there is little validation of their contents.
- User-facing text, identifiers and file names are in Portuguese.
