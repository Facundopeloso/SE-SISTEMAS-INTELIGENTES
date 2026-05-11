"""
=============================================================================
SISTEMA EXPERTO DERMATOLÓGICO - SE_DERM v1.0
=============================================================================
Dominio      : Diagnóstico orientativo de enfermedades cutáneas
Experta      : Dra. Claudia E. Alarcón (dermatóloga, +20 años de experiencia)
Tipo de SE   : HÍBRIDO — Reglas deterministas + Lógica Difusa + Factores heurísticos
Autor        : Grupo ISI 5° año
Descripción  : El sistema recibe variables clínicas observadas por el paciente
               (localización, morfología, color, picazón, antigüedad, estrés),
               aplica 20 reglas IF-THEN junto con funciones de membresía difusa
               para la variable "picazón", y emite un diagnóstico con nivel de
               certeza y la lista de reglas activadas (subsistema de explicación).
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import math


# =============================================================================
# SISTEMA EXPERTO — Clase principal (Base de Conocimiento + Motor de Inferencia)
# =============================================================================

class SistemaExperto:
    """
    Encapsula el conocimiento y el razonamiento del SE Dermatológico.

    Módulos internos:
      - Lógica Difusa        : funciones de membresía para la variable "Picazón"
      - Base de Conocimiento : 20 reglas IF-THEN (aplicar_reglas)
      - Motor de Inferencia  : forward chaining + post-procesamiento (inferir)
    """

    # -------------------------------------------------------------------------
    # MÓDULO 1: LÓGICA DIFUSA — Variable lingüística "Picazón"
    # -------------------------------------------------------------------------

    def _membresía_nula(self, x: float) -> float:
        if x <= 1:
            return 1.0
        elif x <= 3:
            return (3 - x) / 2.0
        else:
            return 0.0

    def _membresía_leve(self, x: float) -> float:
        if x <= 1 or x >= 5:
            return 0.0
        elif x <= 3:
            return (x - 1) / 2.0
        else:
            return (5 - x) / 2.0

    def _membresía_moderada(self, x: float) -> float:
        if x <= 4 or x >= 8:
            return 0.0
        elif x <= 6:
            return (x - 4) / 2.0
        else:
            return (8 - x) / 2.0

    def _membresía_intensa(self, x: float) -> float:
        if x <= 6:
            return 0.0
        elif x <= 8:
            return (x - 6) / 2.0
        else:
            return 1.0

    def clasificar_picazón(self, escala: float) -> str:
        """Defuzzificación por máximo: devuelve la etiqueta lingüística dominante."""
        grados = {
            "Nula":     self._membresía_nula(escala),
            "Leve":     self._membresía_leve(escala),
            "Moderada": self._membresía_moderada(escala),
            "Intensa":  self._membresía_intensa(escala),
        }
        return max(grados, key=grados.get)

    def grados_picazón(self, escala: float) -> dict:
        """Devuelve los grados de pertenencia de todas las etiquetas."""
        return {
            "Nula":     round(self._membresía_nula(escala), 2),
            "Leve":     round(self._membresía_leve(escala), 2),
            "Moderada": round(self._membresía_moderada(escala), 2),
            "Intensa":  round(self._membresía_intensa(escala), 2),
        }

    # -------------------------------------------------------------------------
    # GUÍA DE OPCIONES VÁLIDAS — para resaltar en la GUI sin restringir entradas
    # -------------------------------------------------------------------------

    # (loc, morf, color) — None = sin restricción. Excluye reglas puras de picazón.
    _COMBOS_GUIA = [
        ("Uñas",     None,            "Amarillento"    ),  # R01
        ("Uñas",     "Engrosamiento", None             ),  # R02
        ("Cara",     "Pápula",        None             ),  # R03
        ("Espalda",  "Pápula",        None             ),  # R04
        ("Codos",    None,            "Blanco nacarado"),  # R05
        ("Rodillas", None,            "Blanco nacarado"),  # R05
        (None,       "Escama",        "Blanco nacarado"),  # R06
        ("Manos",    None,            None             ),  # R08
        ("Pies",     "Ampolla",       None             ),  # R09
        (None,       "Mácula",        "Rosado"         ),  # R10
        ("Cara",     None,            None             ),  # R11
        ("Flexuras", None,            None             ),  # R12
        (None,       "Escama",        "Rojo"           ),  # R13
    ]

    def morfologias_sugeridas(self, loc: str) -> set:
        """Morfologías que activan al menos una regla para la localización dada."""
        todas = {"Mácula", "Pápula", "Ampolla", "Escama", "Engrosamiento"}
        coinciden = [c for c in self._COMBOS_GUIA if c[0] == loc or c[0] is None]
        if any(c[1] is None for c in coinciden):
            return todas
        return {c[1] for c in coinciden if c[1] is not None}

    def colores_sugeridos(self, loc: str, morf: str) -> set:
        """Colores que activan al menos una regla para la loc+morf dadas."""
        todos = {"Amarillento", "Blanco nacarado", "Rosado", "Rojo"}
        coinciden = [
            c for c in self._COMBOS_GUIA
            if (c[0] == loc or c[0] is None) and (c[1] == morf or c[1] is None)
        ]
        if any(c[2] is None for c in coinciden):
            return todos
        return {c[2] for c in coinciden if c[2] is not None}

    # -------------------------------------------------------------------------
    # MÓDULO 2: BASE DE CONOCIMIENTO — 20 Reglas IF-THEN
    # -------------------------------------------------------------------------

    def aplicar_reglas(self, datos: dict) -> list:
        """
        Evalúa las 20 reglas de la base de conocimiento sobre los datos clínicos.
        Retorna la lista completa de reglas con el campo 'activa' resuelto.
        """
        loc   = datos.get("localizacion", "")
        morf  = datos.get("morfologia", "")
        color = datos.get("color", "")
        pica  = datos.get("picazon_etiqueta", "")
        antig = datos.get("antiguedad", 0)

        return [
            # --- ONICOMICOSIS ---
            {
                "id": "R01",
                "desc": "Localización=uñas Y Color=amarillento → Onicomicosis",
                "activa": loc == "Uñas" and color == "Amarillento",
                "diag": "Onicomicosis",
                "tipo": "Determinista",
                "conf": 0.90,
            },
            {
                "id": "R02",
                "desc": "Localización=uñas Y Morfología=engrosamiento → Onicomicosis",
                "activa": loc == "Uñas" and morf == "Engrosamiento",
                "diag": "Onicomicosis",
                "tipo": "Determinista",
                "conf": 0.88,
            },
            # --- ACNÉ ---
            {
                "id": "R03",
                "desc": "Localización=cara Y Morfología=pápula → Acné",
                "activa": loc == "Cara" and morf == "Pápula",
                "diag": "Acné",
                "tipo": "Determinista",
                "conf": 0.85,
            },
            {
                "id": "R04",
                "desc": "Localización=espalda Y Morfología=pápula → Acné",
                "activa": loc == "Espalda" and morf == "Pápula",
                "diag": "Acné",
                "tipo": "Determinista",
                "conf": 0.82,
            },
            # --- PSORIASIS ---
            {
                "id": "R05",
                "desc": "Localización=(codos|rodillas) Y Color=blanco nacarado → Psoriasis",
                "activa": loc in ("Codos", "Rodillas") and color == "Blanco nacarado",
                "diag": "Psoriasis",
                "tipo": "Determinista",
                "conf": 0.92,
            },
            {
                "id": "R06",
                "desc": "Morfología=escama Y Color=blanco nacarado → Psoriasis",
                "activa": morf == "Escama" and color == "Blanco nacarado",
                "diag": "Psoriasis",
                "tipo": "Determinista",
                "conf": 0.87,
            },
            # --- PSORIASIS: REFORZADOR HEURÍSTICO ---
            {
                "id": "R07",
                "desc": "Diagnóstico en curso=Psoriasis Y Estrés=Sí → Confirma brote por estrés",
                "activa": False,
                "diag": "Psoriasis [Brote por Estrés]",
                "tipo": "Heurística",
                "conf": 0.10,
            },
            # --- DISHIDROSIS ---
            {
                "id": "R08",
                "desc": "Localización=manos Y Picazón=Intensa → Dishidrosis (difusa)",
                "activa": loc == "Manos" and pica == "Intensa",
                "diag": "Dishidrosis",
                "tipo": "Difusa",
                "conf": 0.78,
            },
            {
                "id": "R09",
                "desc": "Localización=pies Y Morfología=ampolla → Dishidrosis",
                "activa": loc == "Pies" and morf == "Ampolla",
                "diag": "Dishidrosis",
                "tipo": "Determinista",
                "conf": 0.83,
            },
            # --- PITIRIASIS ALBA ---
            {
                "id": "R10",
                "desc": "Color=rosado Y Morfología=mácula → Pitiriasis alba",
                "activa": color == "Rosado" and morf == "Mácula",
                "diag": "Pitiriasis alba",
                "tipo": "Determinista",
                "conf": 0.80,
            },
            {
                "id": "R11",
                "desc": "Localización=cara Y Picazón=Leve → Pitiriasis alba (difusa)",
                "activa": loc == "Cara" and pica == "Leve",
                "diag": "Pitiriasis alba",
                "tipo": "Difusa",
                "conf": 0.65,
            },
            # --- ECCEMA ---
            {
                "id": "R12",
                "desc": "Localización=flexuras Y Picazón=Intensa → Eccema (difusa)",
                "activa": loc == "Flexuras" and pica == "Intensa",
                "diag": "Eccema",
                "tipo": "Difusa",
                "conf": 0.82,
            },
            {
                "id": "R13",
                "desc": "Color=rojo Y Morfología=escama Y Picazón=Intensa → Eccema (difusa)",
                "activa": color == "Rojo" and morf == "Escama" and pica == "Intensa",
                "diag": "Eccema",
                "tipo": "Difusa",
                "conf": 0.85,
            },
            # --- ECCEMA: REFORZADOR HEURÍSTICO ---
            {
                "id": "R14",
                "desc": "Diagnóstico en curso=Eccema Y Estrés=Sí → Origen psicosomático",
                "activa": False,
                "diag": "Eccema [Origen Psicosomático]",
                "tipo": "Heurística",
                "conf": 0.10,
            },
            # --- TEMPORALIDAD (Estado) ---
            {
                "id": "R15",
                "desc": "Antigüedad < 3 meses → Estado: Agudo",
                "activa": antig < 3,
                "diag": "Estado: Agudo",
                "tipo": "Determinista",
                "conf": 1.0,
            },
            {
                "id": "R16",
                "desc": "Antigüedad > 4 meses → Estado: Crónico",
                "activa": antig > 4,
                "diag": "Estado: Crónico",
                "tipo": "Determinista",
                "conf": 1.0,
            },
            # --- RECOMENDACIONES CRUZADAS ---
            {
                "id": "R17",
                "desc": "Acné Y Estado=Agudo → Tratamiento tópico leve",
                "activa": False,
                "diag": "Recomendación: Tratamiento tópico leve",
                "tipo": "Determinista",
                "conf": 0.0,
            },
            {
                "id": "R18",
                "desc": "Dishidrosis Y Estado=Crónico → Medicación sistémica (oral)",
                "activa": False,
                "diag": "Recomendación: Evaluación para medicación sistémica",
                "tipo": "Determinista",
                "conf": 0.0,
            },
            # --- PITIRIASIS DIFUSA ADICIONAL ---
            {
                "id": "R19",
                "desc": "Picazón=Nula Y Color=rosado → Alta prob. Pitiriasis alba (difusa)",
                "activa": pica == "Nula" and color == "Rosado",
                "diag": "Pitiriasis alba",
                "tipo": "Difusa",
                "conf": 0.72,
            },
            # --- PSORIASIS CRÓNICA ---
            {
                "id": "R20",
                "desc": "Psoriasis Y Estado=Crónico → Derivación prioritaria a especialista",
                "activa": False,
                "diag": "Recomendación: Derivación urgente a dermatólogo",
                "tipo": "Determinista",
                "conf": 0.0,
            },
        ]

    # -------------------------------------------------------------------------
    # MÓDULO 3: MOTOR DE INFERENCIA — Forward chaining + post-procesamiento
    # -------------------------------------------------------------------------

    def inferir(self, datos: dict) -> dict:
        """
        Ejecuta el ciclo completo de inferencia:
          1. Clasifica picazón con lógica difusa.
          2. Evalúa las 20 reglas base.
          3. Aplica reglas de post-procesamiento (R07, R14, R17, R18, R20).
          4. Acumula confianza y selecciona el diagnóstico principal.
        """
        escala_picazon = datos.get("picazon_escala", 0)
        datos["picazon_etiqueta"] = self.clasificar_picazón(escala_picazon)
        datos["picazon_grados"]   = self.grados_picazón(escala_picazon)

        reglas = self.aplicar_reglas(datos)
        reglas_activas = [r for r in reglas if r["activa"]]

        diagnosticos_preliminares = {r["diag"] for r in reglas_activas}
        estado = None
        if "Estado: Crónico" in diagnosticos_preliminares:
            estado = "Crónico"
        elif "Estado: Agudo" in diagnosticos_preliminares:
            estado = "Agudo"

        estres = datos.get("estres", False)

        if "Psoriasis" in diagnosticos_preliminares and estres:
            r07 = next(r for r in reglas if r["id"] == "R07")
            r07["activa"] = True
            reglas_activas.append(r07)

        if "Eccema" in diagnosticos_preliminares and estres:
            r14 = next(r for r in reglas if r["id"] == "R14")
            r14["activa"] = True
            reglas_activas.append(r14)

        if "Acné" in diagnosticos_preliminares and estado == "Agudo":
            r17 = next(r for r in reglas if r["id"] == "R17")
            r17["activa"] = True
            reglas_activas.append(r17)

        if "Dishidrosis" in diagnosticos_preliminares and estado == "Crónico":
            r18 = next(r for r in reglas if r["id"] == "R18")
            r18["activa"] = True
            reglas_activas.append(r18)

        if "Psoriasis" in diagnosticos_preliminares and estado == "Crónico":
            r20 = next(r for r in reglas if r["id"] == "R20")
            r20["activa"] = True
            reglas_activas.append(r20)

        EXCLUIR_PREFIJOS = ("Estado:", "Recomendación:")
        acumulador = {}
        for r in reglas_activas:
            if r["conf"] > 0 and not any(r["diag"].startswith(p) for p in EXCLUIR_PREFIJOS):
                diag = r["diag"]
                acumulador[diag] = acumulador.get(diag, 0) + r["conf"]

        for diag in acumulador:
            acumulador[diag] = min(round(acumulador[diag], 2), 0.99)

        diagnostico_principal = None
        confianza_principal = 0.0
        if acumulador:
            diagnostico_principal = max(acumulador, key=acumulador.get)
            confianza_principal = acumulador[diagnostico_principal]

        recomendaciones = [r["diag"] for r in reglas_activas if r["conf"] == 0.0]

        return {
            "diagnostico":      diagnostico_principal,
            "confianza":        confianza_principal,
            "estado":           estado,
            "reglas_activas":   reglas_activas,
            "acumulador":       acumulador,
            "recomendaciones":  recomendaciones,
            "picazon_etiqueta": datos["picazon_etiqueta"],
            "picazon_grados":   datos["picazon_grados"],
        }


# =============================================================================
# MÓDULO 4: INTERFAZ GRÁFICA — Tkinter
# =============================================================================

class AppSEDerm(tk.Tk):
    """
    Ventana principal de la aplicación.
    Organiza la GUI en tres paneles:
      - Panel Izquierdo       : formulario de entrada de datos clínicos
      - Panel Derecho Superior: resultado y nivel de certeza
      - Panel Derecho Inferior: subsistema de explicación (reglas activadas)
    """

    COLORES = {
        "fondo":    "#F0F4F8",
        "panel":    "#FFFFFF",
        "acento":   "#2B6CB0",
        "acento2":  "#48BB78",
        "texto":    "#1A202C",
        "subtexto": "#4A5568",
        "borde":    "#CBD5E0",
        "alerta":   "#E53E3E",
        "difuso":   "#D69E2E",
        "heurist":  "#805AD5",
        "det":      "#2B6CB0",
    }

    def __init__(self):
        super().__init__()
        self.se = SistemaExperto()
        self.title("SE Dermatológico — Dra. Claudia E. Alarcón")
        self.geometry("1100x720")
        self.resizable(True, True)
        self.configure(bg=self.COLORES["fondo"])
        self._construir_ui()

    def _construir_ui(self):
        frame_titulo = tk.Frame(self, bg=self.COLORES["acento"], pady=10)
        frame_titulo.pack(fill="x")
        tk.Label(frame_titulo, text="🩺  Sistema Experto Dermatológico",
                 font=("Georgia", 17, "bold"), fg="white",
                 bg=self.COLORES["acento"]).pack()
        tk.Label(frame_titulo,
                 text="Diagnóstico orientativo — SE Híbrido (Reglas + Lógica Difusa + Heurística)",
                 font=("Georgia", 9), fg="#BEE3F8",
                 bg=self.COLORES["acento"]).pack()

        contenedor = tk.Frame(self, bg=self.COLORES["fondo"])
        contenedor.pack(fill="both", expand=True, padx=14, pady=10)

        self.panel_izq = tk.Frame(contenedor, bg=self.COLORES["panel"],
                                  relief="flat", bd=1,
                                  highlightbackground=self.COLORES["borde"],
                                  highlightthickness=1)
        self.panel_izq.pack(side="left", fill="y", padx=(0, 8))

        panel_der = tk.Frame(contenedor, bg=self.COLORES["fondo"])
        panel_der.pack(side="left", fill="both", expand=True)

        self._construir_formulario(self.panel_izq)
        self._construir_resultado(panel_der)
        self._construir_explicacion(panel_der)

    def _lbl_sec(self, parent, texto):
        tk.Label(parent, text=texto, font=("Helvetica", 10, "bold"),
                 fg=self.COLORES["acento"], bg=self.COLORES["panel"],
                 anchor="w").pack(fill="x", padx=16, pady=(12, 2))

    def _combo(self, parent, opciones, var):
        cb = ttk.Combobox(parent, textvariable=var, values=opciones,
                          state="readonly", width=28, font=("Helvetica", 9))
        cb.pack(padx=16, pady=(0, 4), fill="x")
        return cb

    def _construir_formulario(self, parent):
        tk.Label(parent, text="Datos del Caso Clínico",
                 font=("Georgia", 12, "bold"),
                 fg=self.COLORES["texto"], bg=self.COLORES["panel"]).pack(pady=(14, 2))
        tk.Frame(parent, bg=self.COLORES["borde"], height=1).pack(fill="x", padx=16)

        self._lbl_sec(parent, "📍 Localización de la lesión")
        self.var_loc = tk.StringVar()
        self._combo(parent, ["Cara", "Espalda", "Codos", "Rodillas",
                              "Manos", "Pies", "Uñas", "Flexuras"], self.var_loc)

        self._lbl_sec(parent, "🔬 Morfología")
        self.var_morf = tk.StringVar()
        self.cb_morf = self._combo(parent, ["Mácula", "Pápula", "Ampolla",
                                            "Escama", "Engrosamiento"], self.var_morf)

        self._lbl_sec(parent, "🎨 Coloración predominante")
        self.var_color = tk.StringVar()
        self.cb_color = self._combo(parent, ["Amarillento", "Blanco nacarado",
                                             "Rosado", "Rojo"], self.var_color)

        self.var_loc.trace_add("write", self._on_loc_change)
        self.var_morf.trace_add("write", self._on_morf_change)

        self._lbl_sec(parent, "😣 Intensidad de picazón (0 = nula, 10 = máxima)")
        self.var_picazon = tk.IntVar(value=0)
        frame_slider = tk.Frame(parent, bg=self.COLORES["panel"])
        frame_slider.pack(fill="x", padx=16)
        tk.Scale(frame_slider, from_=0, to=10, orient="horizontal",
                 variable=self.var_picazon, bg=self.COLORES["panel"],
                 fg=self.COLORES["texto"], highlightthickness=0,
                 troughcolor=self.COLORES["borde"], font=("Helvetica", 8),
                 command=self._actualizar_etiqueta_picazon).pack(fill="x")
        self.lbl_picazon_etiq = tk.Label(parent, text="Etiqueta difusa: Nula",
                                         font=("Helvetica", 8, "italic"),
                                         fg=self.COLORES["difuso"],
                                         bg=self.COLORES["panel"])
        self.lbl_picazon_etiq.pack(padx=16, anchor="w")

        self._lbl_sec(parent, "📅 Antigüedad de la lesión (meses)")
        self.var_antig = tk.IntVar(value=1)
        frame_antig = tk.Frame(parent, bg=self.COLORES["panel"])
        frame_antig.pack(fill="x", padx=16)
        tk.Scale(frame_antig, from_=0, to=36, orient="horizontal",
                 variable=self.var_antig, bg=self.COLORES["panel"],
                 fg=self.COLORES["texto"], highlightthickness=0,
                 troughcolor=self.COLORES["borde"],
                 font=("Helvetica", 8)).pack(fill="x")

        self._lbl_sec(parent, "🧠 ¿Presentó estrés previo al brote?")
        self.var_estres = tk.BooleanVar(value=False)
        frame_estres = tk.Frame(parent, bg=self.COLORES["panel"])
        frame_estres.pack(fill="x", padx=16, pady=(0, 8))
        tk.Radiobutton(frame_estres, text="Sí", variable=self.var_estres,
                       value=True, bg=self.COLORES["panel"],
                       font=("Helvetica", 9)).pack(side="left")
        tk.Radiobutton(frame_estres, text="No", variable=self.var_estres,
                       value=False, bg=self.COLORES["panel"],
                       font=("Helvetica", 9)).pack(side="left", padx=8)

        tk.Frame(parent, bg=self.COLORES["borde"], height=1).pack(fill="x", padx=16)

        tk.Button(parent, text="🔍  Diagnosticar",
                  command=self._ejecutar_diagnostico,
                  font=("Helvetica", 11, "bold"),
                  bg=self.COLORES["acento"], fg="white",
                  relief="flat", pady=8, cursor="hand2",
                  activebackground="#2C5282",
                  activeforeground="white").pack(fill="x", padx=16, pady=12)

        tk.Button(parent, text="↺  Limpiar", command=self._limpiar,
                  font=("Helvetica", 9), bg=self.COLORES["borde"],
                  fg=self.COLORES["texto"], relief="flat", pady=4,
                  cursor="hand2").pack(fill="x", padx=16, pady=(0, 12))

    def _construir_resultado(self, parent):
        frame = tk.Frame(parent, bg=self.COLORES["panel"],
                         highlightbackground=self.COLORES["borde"],
                         highlightthickness=1)
        frame.pack(fill="x", pady=(0, 8))

        tk.Label(frame, text="Resultado del Diagnóstico",
                 font=("Georgia", 11, "bold"),
                 fg=self.COLORES["texto"],
                 bg=self.COLORES["panel"]).pack(anchor="w", padx=16, pady=(10, 4))
        tk.Frame(frame, bg=self.COLORES["borde"], height=1).pack(fill="x", padx=16)

        self.lbl_diagnostico = tk.Label(frame, text="—",
                                        font=("Georgia", 20, "bold"),
                                        fg=self.COLORES["acento"],
                                        bg=self.COLORES["panel"])
        self.lbl_diagnostico.pack(pady=(10, 2))

        self.lbl_certeza_texto = tk.Label(frame, text="Nivel de certeza: —",
                                          font=("Helvetica", 9),
                                          fg=self.COLORES["subtexto"],
                                          bg=self.COLORES["panel"])
        self.lbl_certeza_texto.pack()

        frame_barra = tk.Frame(frame, bg=self.COLORES["panel"])
        frame_barra.pack(pady=(2, 6), padx=30, fill="x")
        self.canvas_barra = tk.Canvas(frame_barra, height=16,
                                      bg=self.COLORES["borde"],
                                      highlightthickness=0)
        self.canvas_barra.pack(fill="x")

        row = tk.Frame(frame, bg=self.COLORES["panel"])
        row.pack(pady=(0, 10))
        self.lbl_estado = tk.Label(row, text="Estado: —",
                                   font=("Helvetica", 9, "bold"),
                                   fg=self.COLORES["acento2"],
                                   bg=self.COLORES["panel"])
        self.lbl_estado.pack(side="left", padx=12)
        self.lbl_difuso = tk.Label(row, text="Picazón difusa: —",
                                   font=("Helvetica", 9, "italic"),
                                   fg=self.COLORES["difuso"],
                                   bg=self.COLORES["panel"])
        self.lbl_difuso.pack(side="left", padx=12)

    def _construir_explicacion(self, parent):
        frame = tk.Frame(parent, bg=self.COLORES["panel"],
                         highlightbackground=self.COLORES["borde"],
                         highlightthickness=1)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="📋  Subsistema de Explicación — Reglas Activadas",
                 font=("Georgia", 11, "bold"),
                 fg=self.COLORES["texto"],
                 bg=self.COLORES["panel"]).pack(anchor="w", padx=16, pady=(10, 2))
        tk.Label(frame, text="¿Por qué el sistema llegó a esa conclusión?",
                 font=("Helvetica", 8, "italic"),
                 fg=self.COLORES["subtexto"],
                 bg=self.COLORES["panel"]).pack(anchor="w", padx=16)
        tk.Frame(frame, bg=self.COLORES["borde"], height=1).pack(fill="x", padx=16, pady=4)

        self.texto_explicacion = scrolledtext.ScrolledText(
            frame, font=("Courier", 9), fg=self.COLORES["texto"],
            bg="#F7FAFC", wrap="word", relief="flat", state="disabled")
        self.texto_explicacion.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.texto_explicacion.tag_config("det",    foreground=self.COLORES["det"])
        self.texto_explicacion.tag_config("difusa", foreground=self.COLORES["difuso"])
        self.texto_explicacion.tag_config("heur",   foreground=self.COLORES["heurist"])
        self.texto_explicacion.tag_config("rec",    foreground=self.COLORES["acento2"])
        self.texto_explicacion.tag_config("header", font=("Courier", 9, "bold"))
        self.texto_explicacion.tag_config("alerta", foreground=self.COLORES["alerta"])

    _MARKER = "► "
    _TODAS_MORF    = ["Mácula", "Pápula", "Ampolla", "Escama", "Engrosamiento"]
    _TODOS_COLORES = ["Amarillento", "Blanco nacarado", "Rosado", "Rojo"]

    def _valor_limpio(self, val: str) -> str:
        return val.replace(self._MARKER, "")

    def _con_marcas(self, opciones: list, sugeridas: set) -> list:
        return [
            (self._MARKER + o if o in sugeridas else o)
            for o in opciones
        ]

    def _on_loc_change(self, *_):
        loc = self._valor_limpio(self.var_loc.get())
        if not loc:
            return
        sug = self.se.morfologias_sugeridas(loc)
        self.cb_morf["values"] = self._con_marcas(self._TODAS_MORF, sug)
        self.var_morf.set("")
        self.cb_color["values"] = self._TODOS_COLORES
        self.var_color.set("")

    def _on_morf_change(self, *_):
        loc  = self._valor_limpio(self.var_loc.get())
        morf = self._valor_limpio(self.var_morf.get())
        if not loc or not morf:
            return
        sug = self.se.colores_sugeridos(loc, morf)
        self.cb_color["values"] = self._con_marcas(self._TODOS_COLORES, sug)
        self.var_color.set("")

    def _actualizar_etiqueta_picazon(self, _=None):
        etiq = self.se.clasificar_picazón(self.var_picazon.get())
        self.lbl_picazon_etiq.config(text=f"Etiqueta difusa: {etiq}")

    def _ejecutar_diagnostico(self):
        loc  = self._valor_limpio(self.var_loc.get())
        morf = self._valor_limpio(self.var_morf.get())
        color = self._valor_limpio(self.var_color.get())
        if not loc or not morf or not color:
            messagebox.showwarning("Datos incompletos",
                                   "Por favor completá: Localización, Morfología y Color.")
            return
        datos = {
            "localizacion":   loc,
            "morfologia":     morf,
            "color":          color,
            "picazon_escala": float(self.var_picazon.get()),
            "antiguedad":     self.var_antig.get(),
            "estres":         self.var_estres.get(),
        }
        self._mostrar_resultado(self.se.inferir(datos), datos)

    def _mostrar_resultado(self, res: dict, datos: dict):
        diag = res["diagnostico"] or "Sin diagnóstico con los datos ingresados"
        self.lbl_diagnostico.config(text=diag)

        certeza = res["confianza"]
        self.lbl_certeza_texto.config(text=f"Nivel de certeza: {certeza * 100:.0f}%")

        self.canvas_barra.update_idletasks()
        ancho = self.canvas_barra.winfo_width()
        self.canvas_barra.delete("all")
        color_barra = (self.COLORES["acento2"] if certeza >= 0.75 else
                       self.COLORES["difuso"]  if certeza >= 0.50 else
                       self.COLORES["alerta"])
        self.canvas_barra.create_rectangle(0, 0, int(ancho * certeza), 16,
                                           fill=color_barra, outline="")

        self.lbl_estado.config(text=f"Estado: {res['estado'] or 'Indeterminado'}")

        g = res["picazon_grados"]
        self.lbl_difuso.config(
            text=f"Picazón difusa: {res['picazon_etiqueta']} "
                 f"(N={g['Nula']} L={g['Leve']} M={g['Moderada']} I={g['Intensa']})")

        self._escribir_explicacion(res, datos)

    def _escribir_explicacion(self, res: dict, datos: dict):
        txt = self.texto_explicacion
        txt.config(state="normal")
        txt.delete("1.0", "end")

        txt.insert("end", "=" * 62 + "\n", "header")
        txt.insert("end", " TRAZABILIDAD DEL RAZONAMIENTO\n", "header")
        txt.insert("end", "=" * 62 + "\n\n", "header")

        txt.insert("end", "▸ ENTRADAS RECIBIDAS:\n", "header")
        txt.insert("end",
                   f"  Localización : {datos['localizacion']}\n"
                   f"  Morfología   : {datos['morfologia']}\n"
                   f"  Color        : {datos['color']}\n"
                   f"  Picazón      : {datos['picazon_escala']:.0f}/10 "
                   f"→ [{res['picazon_etiqueta']}]\n"
                   f"  Antigüedad   : {datos['antiguedad']} mes(es)\n"
                   f"  Estrés       : {'Sí' if datos['estres'] else 'No'}\n\n")

        g = res["picazon_grados"]
        txt.insert("end", "▸ LÓGICA DIFUSA — Membresías de picazón:\n", "header")
        txt.insert("end",
                   f"  Nula={g['Nula']}  Leve={g['Leve']}  "
                   f"Moderada={g['Moderada']}  Intensa={g['Intensa']}\n\n", "difusa")

        txt.insert("end", "▸ REGLAS ACTIVADAS:\n", "header")
        for r in res["reglas_activas"]:
            tipo = r["tipo"]
            tag  = ("det"    if tipo == "Determinista" else
                    "difusa" if tipo == "Difusa" else
                    "heur"   if tipo == "Heurística" else "rec")
            aporte = f"+{r['conf']:.2f}" if r["conf"] > 0 else "(recomendación)"
            txt.insert("end", f"\n  [{r['id']}] {tipo}\n", tag)
            txt.insert("end", f"  SI:    {r['desc']}\n  CONCL: {r['diag']}  {aporte}\n")

        if not res["reglas_activas"]:
            txt.insert("end",
                       "  Ninguna regla se activo con los datos ingresados.\n"
                       "  Sugestion: revisa los campos o consulta a un especialista.\n",
                       "alerta")

        if res["recomendaciones"]:
            txt.insert("end", "\n▸ RECOMENDACIONES GENERADAS:\n", "header")
            for rec in res["recomendaciones"]:
                txt.insert("end", f"  → {rec}\n", "rec")

        txt.insert("end", "\n▸ CERTEZA ACUMULADA POR DIAGNÓSTICO:\n", "header")
        for diag, conf in sorted(res["acumulador"].items(),
                                  key=lambda x: x[1], reverse=True):
            barra = "█" * int(conf * 20)
            txt.insert("end", f"  {diag:<30} {conf*100:5.1f}%  {barra}\n")

        txt.insert("end", "\n" + "=" * 62 + "\n", "header")
        txt.insert("end",
                   "ADVERTENCIA: Este sistema es orientativo.\n"
                   "No reemplaza la consulta con un medico especialista.\n", "alerta")
        txt.config(state="disabled")

    def _limpiar(self):
        self.var_loc.set("")
        self.var_morf.set("")
        self.var_color.set("")
        self.var_picazon.set(0)
        self.var_antig.set(1)
        self.var_estres.set(False)
        self.lbl_picazon_etiq.config(text="Etiqueta difusa: Nula")
        self.lbl_diagnostico.config(text="—")
        self.lbl_certeza_texto.config(text="Nivel de certeza: —")
        self.lbl_estado.config(text="Estado: —")
        self.lbl_difuso.config(text="Picazón difusa: —")
        self.canvas_barra.delete("all")
        self.texto_explicacion.config(state="normal")
        self.texto_explicacion.delete("1.0", "end")
        self.texto_explicacion.config(state="disabled")


# =============================================================================
# MÓDULO 5: CASOS DE PRUEBA (para validación sin GUI)
# =============================================================================

def ejecutar_casos_prueba():
    se = SistemaExperto()

    casos = [
        {
            "nombre": "Caso 1 - Psoriasis cronica con estres",
            "datos": {"localizacion": "Codos", "morfologia": "Escama",
                      "color": "Blanco nacarado", "picazon_escala": 7,
                      "antiguedad": 8, "estres": True},
            "esperado": "Psoriasis",
        },
        {
            "nombre": "Caso 2 - Acne agudo en cara",
            "datos": {"localizacion": "Cara", "morfologia": "Pápula",
                      "color": "Rojo", "picazon_escala": 2,
                      "antiguedad": 1, "estres": False},
            "esperado": "Acné",
        },
        {
            "nombre": "Caso 3 - Dishidrosis en pies",
            "datos": {"localizacion": "Pies", "morfologia": "Ampolla",
                      "color": "Rosado", "picazon_escala": 8,
                      "antiguedad": 2, "estres": False},
            "esperado": "Dishidrosis",
        },
        {
            "nombre": "Caso 4 - Pitiriasis alba sin picazon",
            "datos": {"localizacion": "Cara", "morfologia": "Mácula",
                      "color": "Rosado", "picazon_escala": 1,
                      "antiguedad": 5, "estres": False},
            "esperado": "Pitiriasis alba",
        },
        {
            "nombre": "Caso 5 - Onicomicosis en unas",
            "datos": {"localizacion": "Uñas", "morfologia": "Engrosamiento",
                      "color": "Amarillento", "picazon_escala": 0,
                      "antiguedad": 10, "estres": False},
            "esperado": "Onicomicosis",
        },
        {
            "nombre": "Caso 6 - Eccema en flexuras con estres",
            "datos": {"localizacion": "Flexuras", "morfologia": "Escama",
                      "color": "Rojo", "picazon_escala": 8,
                      "antiguedad": 2, "estres": True},
            "esperado": "Eccema",
        },
    ]

    print("\n" + "=" * 60)
    print("  CASOS DE PRUEBA - SE Dermatologico")
    print("=" * 60)

    for caso in casos:
        res = se.inferir(caso["datos"])
        ok  = "[OK]" if res["diagnostico"] == caso["esperado"] else "[FAIL]"
        print(f"\n{ok}  {caso['nombre']}")
        print(f"   Diagnostico: {res['diagnostico']}  ({res['confianza']*100:.0f}% certeza)")
        print(f"   Estado:      {res['estado']}")
        print(f"   Picazon:     {res['picazon_etiqueta']}")
        print(f"   Reglas:      {[r['id'] for r in res['reglas_activas']]}")

    print("\n" + "=" * 60 + "\n")


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    ejecutar_casos_prueba()
    app = AppSEDerm()
    app.mainloop()
