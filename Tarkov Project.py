import csv
import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# =========================
# CONFIG
# =========================
FORCE_SUPPRESSOR = True
FORCE_TACTICAL = False
RANDOMIZATION_PASSES = [0.10, 0.25, 0.50]

# =========================
# WEAPON
# =========================
class Weapon:
    def __init__(self, name, base_price, base_recoil, base_ergo):
        self.name = name
        self.base_price = base_price
        self.base_recoil = base_recoil
        self.base_ergo = base_ergo

# =========================
# ATTACHMENT
# =========================
class Attachment:
    def __init__(self, name, attachment_type, price, ergo, recoil):
        self.name = name
        self.attachment_type = attachment_type
        self.price = price
        self.ergo = ergo
        self.recoil = recoil

    def __str__(self):
        return f"{self.name} ({self.attachment_type}) | ₽{self.price} | Ergo {self.ergo} | Recoil {self.recoil}"

# =========================
# BUILD
# =========================
class Build:
    def __init__(self, weapon, recoil_weight=1.0, ergo_weight=1.0):
        self.weapon = weapon
        self.recoil_weight = recoil_weight
        self.ergo_weight = ergo_weight
        self.attachments = []

        self._price = weapon.base_price
        self._ergo = weapon.base_ergo
        self._recoil = weapon.base_recoil

    # -------- stats --------
    def total_price(self): return self._price
    def total_ergo(self): return self._ergo
    def total_recoil(self): return self._recoil

    # -------- scoring --------
    def attachment_score(self, att, noise=0.0):
        base = (-att.recoil * self.recoil_weight) + (att.ergo * self.ergo_weight)
        jitter = base * random.uniform(-noise, noise)
        return base + jitter

    def score_build(self):
        recoil_gain = self.weapon.base_recoil - self.total_recoil()
        ergo_gain = self.total_ergo() - self.weapon.base_ergo
        return recoil_gain * self.recoil_weight + ergo_gain * self.ergo_weight

    # -------- attachment logic --------
    def can_add(self, att):
        if any(a.attachment_type == att.attachment_type for a in self.attachments):
            return False
        if att.attachment_type == "Suppressor":
            return any(a.name == "Muzzle Adapter" for a in self.attachments)
        return True

    def add(self, att):
        if self.can_add(att):
            self.attachments.append(att)
            self._price += att.price
            self._ergo += att.ergo
            self._recoil += self.weapon.base_recoil * (att.recoil / 100)

    def signature(self):
        return tuple(sorted(a.name for a in self.attachments))

# =========================
# OPTIMIZER
# =========================
def optimize_builds(weapon, attachments, budget, recoil_weight, ergo_weight):
    by_type = {}
    for a in attachments:
        by_type.setdefault(a.attachment_type, []).append(a)

    REQUIRED = ["Barrel", "Handguard", "Stock", "Foregrip", "Muzzle"]
    STRATEGIES = ["value", "expensive", "cheap"]

    completed_builds = []
    attempted_signatures = set()

    for slot in REQUIRED:
        for strategy in STRATEGIES:
            success = False

            for noise in RANDOMIZATION_PASSES:
                build = Build(weapon, recoil_weight, ergo_weight)

                # ---- FORCE MUZZLE + SUPPRESSOR ----
                if FORCE_SUPPRESSOR:
                    muzzle = next(a for a in by_type["Muzzle"] if a.name == "Muzzle Adapter")
                    build.add(muzzle)

                    suppressors = by_type.get("Suppressor", [])
                    if suppressors:
                        best_sup = max(
                            suppressors,
                            key=lambda a: build.attachment_score(a, noise)
                        )
                        if build.total_price() + best_sup.price <= budget:
                            build.add(best_sup)

                # ---- required slots ----
                for req in REQUIRED:
                    candidates = by_type.get(req, [])
                    if not candidates:
                        continue

                    if strategy == "value":
                        chosen = max(candidates, key=lambda a: build.attachment_score(a, noise))
                    elif strategy == "expensive":
                        chosen = max(candidates, key=lambda a: a.price)
                    else:
                        chosen = min(candidates, key=lambda a: a.price)

                    if build.total_price() + chosen.price > budget:
                        break
                    build.add(chosen)

                else:
                    sig = build.signature()
                    if sig not in attempted_signatures:
                        attempted_signatures.add(sig)
                        completed_builds.append(build)
                    success = True
                    break

            if not success:
                continue

    return completed_builds

# =========================
# LOAD DATA
# =========================
attachments = []
with open("attachments.csv", newline="") as f:
    reader = csv.DictReader(f)
    for r in reader:
        attachments.append(
            Attachment(
                r["Name"],
                r["Type"],
                int(r["Price"]),
                int(r["Ergo"]),
                float(r["Recoil"])
            )
        )

weapon = Weapon("Prototype Rifle", 45000, 200, 45)

# =========================
# GUI
# =========================
class OptimizerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weapon Build Optimizer")
        self.geometry("500x400")

        # Variables
        self.force_suppressor_var = tk.BooleanVar(value=True)
        self.force_tactical_var = tk.BooleanVar(value=False)
        self.budget_var = tk.IntVar(value=1_300_000)

        # Widgets
        ttk.Label(self, text="Options").pack(pady=5)

        ttk.Checkbutton(
            self, text="Force Suppressor", variable=self.force_suppressor_var
        ).pack(anchor="w", padx=20)
        ttk.Checkbutton(
            self, text="Force Tactical", variable=self.force_tactical_var
        ).pack(anchor="w", padx=20)

        ttk.Label(self, text="Budget (₽)").pack(pady=(10,0))
        ttk.Entry(self, textvariable=self.budget_var).pack(padx=20, fill="x")

        ttk.Button(self, text="Run Optimizer", command=self.run_optimizer).pack(pady=10)

        self.output = tk.Text(self, height=15)
        self.output.pack(padx=20, fill="both", expand=True)

    def run_optimizer(self):
        global FORCE_SUPPRESSOR, FORCE_TACTICAL

        FORCE_SUPPRESSOR = self.force_suppressor_var.get()
        FORCE_TACTICAL = self.force_tactical_var.get()
        budget = self.budget_var.get()

        try:
            builds = optimize_builds(
                weapon,
                attachments,
                budget=budget,
                recoil_weight=1.01,
                ergo_weight=1.0
            )

            self.output.delete("1.0", tk.END)

            if not builds:
                self.output.insert(tk.END, "No builds found within the budget!")
                return

            # --- DEBUG STATS ---
            unique = len({b.signature() for b in builds})
            total = len(builds)
            identical = total - unique

            self.output.insert(tk.END, f"Builds Completed : {total} / 12\n")
            self.output.insert(tk.END, f"Identical Builds : {identical} / {total}\n\n")

            # --- TOP 3 BUILDS ---
            top_builds = sorted(builds, key=lambda b: b.score_build(), reverse=True)[:3]
            for idx, build in enumerate(top_builds, 1):
                self.output.insert(tk.END, f"=== BUILD #{idx} ===\n")
                for a in build.attachments:
                    self.output.insert(tk.END, f"{a}\n")
                self.output.insert(tk.END, f"Total Price : {build.total_price()}\n")
                self.output.insert(tk.END, f"Total Ergo  : {build.total_ergo()}\n")
                self.output.insert(tk.END, f"Total Recoil: {build.total_recoil()}\n")
                self.output.insert(tk.END, f"Build Score : {build.score_build()}\n\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))

# =========================
# LAUNCH GUI
# =========================
if __name__ == "__main__":
    app = OptimizerGUI()
    app.mainloop()



