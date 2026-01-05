## Escape from Tarkov – Weapon Build Optimiser

A **heuristic-based weapon configuration optimiser** for *Escape from Tarkov*.  
The project explores how to generate **strong, competitive weapon builds** under real constraints (budget limits, attachment compatibility, stat trade-offs) without relying on brute-force search.

### Key Highlights
- **System modelling with interacting domain objects**  
  Weapons, attachments, and builds are modelled explicitly, with enforced compatibility rules and slot constraints.
- **Heuristic decision-making over a massive solution space**  
  Uses weighted scoring, strategy-based selection, and controlled randomness to consistently produce high-quality builds without exhaustive enumeration.
- **Real data handling**  
  Attachment data is loaded from external CSV files and converted into domain objects, keeping data representation separate from optimisation logic.
- **Usable tooling, not just a script**  
  Includes a minimal Tkinter GUI to adjust constraints, run the optimiser, and inspect top candidate builds interactively.

This project is intentionally **not** a brute-force or mathematically optimal solution. Instead, it focuses on **engineering judgement**, trade-offs, and practical problem-solving.

For a detailed explanation of the system design, heuristic approach, assumptions, limitations, and future improvements, see **`README.pdf`**.

