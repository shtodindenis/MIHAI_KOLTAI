from __future__ import annotations
from dataclasses import dataclass

@dataclass
class CalcState:
    is_running: bool = False
    display: str = "0"
    expression: str = ""
    operand: float | None = None
    operator: str | None = None
    needs_clear: bool = False

    def reset(self) -> None:
        self.is_running = False
        self.clear_all()

    def clear_all(self) -> None:
        self.display = "0"
        self.expression = ""
        self.operand = None
        self.operator = None
        self.needs_clear = False

    def input_char(self, char: str) -> None:
        if char == "C":
            self.clear_all()
            return

        if char == "±":
            if self.display != "0" and self.display != "Error":
                if self.display.startswith("-"):
                    self.display = self.display[1:]
                else:
                    self.display = "-" + self.display
            return

        if char == "%":
            try:
                val = float(self.display) / 100.0
                self.display = self._format_number(val)
                self.needs_clear = True
            except ValueError:
                self.display = "Error"
            return

        if char in ("+", "-", "*", "/"):
            if self.display == "Error":
                return
            if self.operand is not None and not self.needs_clear:
                self._calculate()
            self.operand = float(self.display)
            self.operator = char
            self.expression = f"{self._format_number(self.operand)} {char}"
            self.needs_clear = True
            return

        if char == "=":
            self._calculate()
            self.expression = ""
            self.operand = None
            self.operator = None
            self.needs_clear = True
            return

        if self.needs_clear:
            self.display = ""
            self.needs_clear = False

        if char == ".":
            if "." not in self.display:
                self.display += "." if self.display else "0."
            return

        if self.display == "0" or self.display == "Error":
            self.display = char
        else:
            self.display += char

    def _calculate(self) -> None:
        if self.operator and self.operand is not None:
            try:
                current_val = float(self.display)
                if self.operator == "+":
                    res = self.operand + current_val
                elif self.operator == "-":
                    res = self.operand - current_val
                elif self.operator == "*":
                    res = self.operand * current_val
                elif self.operator == "/":
                    if current_val == 0:
                        self.display = "Error"
                        return
                    res = self.operand / current_val
                else:
                    res = current_val
                self.display = self._format_number(res)
            except Exception:
                self.display = "Error"

    def _format_number(self, num: float) -> str:
        if num.is_integer():
            return str(int(num))
        res = str(round(num, 8))
        return res.rstrip("0").rstrip(".") if "." in res else res