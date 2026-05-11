# Sistema Experto Dermatológico — SE_DERM v1.0

## Dominio
Diagnóstico orientativo de enfermedades cutáneas (dermatología).  
El sistema evalúa variables clínicas observadas por el paciente y emite un diagnóstico con nivel de certeza.

## Tipo de Sistema Experto
**Híbrido**: Reglas deterministas + Lógica Difusa + Factores heurísticos.

---

## Ubicación de las Reglas de Negocio / Base de Conocimiento

Todo el conocimiento del sistema se encuentra en el archivo:

```
src/main.py
```

El SE está implementado como un **objeto** de la clase `SistemaExperto`. La clase encapsula tres módulos internos:

| Módulo | Método(s) | Descripción |
|--------|-----------|-------------|
| **Lógica Difusa** | `clasificar_picazón()` · `grados_picazón()` | Funciones de membresía para la variable lingüística "Picazón" (Nula, Leve, Moderada, Intensa) |
| **Base de Conocimiento** | `aplicar_reglas()` | 20 reglas IF-THEN evaluadas sobre los datos clínicos |
| **Motor de Inferencia** | `inferir()` | Forward chaining + post-procesamiento + acumulación de certeza |

La GUI (`AppSEDerm`) y los casos de prueba (`ejecutar_casos_prueba`) son externos a la clase e interactúan con ella a través de una instancia:

```python
se = SistemaExperto()
resultado = se.inferir(datos)
```

---

### Las 20 Reglas (Base de Conocimiento)

Definidas dentro de `aplicar_reglas()` en `src/main.py`. Cada regla tiene la estructura:

```python
{
    "id":     "R01",                         # Identificador único
    "desc":   "Condición IF en lenguaje natural",
    "activa": <expresión booleana>,          # Evaluación de la condición
    "diag":   "Diagnóstico / conclusión",   # Conclusión THEN
    "tipo":   "Determinista | Difusa | Heurística",
    "conf":   0.90,                          # Confianza base (0.0 – 1.0)
}
```

#### Resumen de reglas por diagnóstico

| ID | Diagnóstico | Tipo | Confianza base |
|----|-------------|------|:--------------:|
| R01 | Onicomicosis | Determinista | 0.90 |
| R02 | Onicomicosis | Determinista | 0.88 |
| R03 | Acné | Determinista | 0.85 |
| R04 | Acné | Determinista | 0.82 |
| R05 | Psoriasis | Determinista | 0.92 |
| R06 | Psoriasis | Determinista | 0.87 |
| R07 | Psoriasis [Brote por Estrés] | Heurística | +0.10 |
| R08 | Dishidrosis | Difusa | 0.78 |
| R09 | Dishidrosis | Determinista | 0.83 |
| R10 | Pitiriasis alba | Determinista | 0.80 |
| R11 | Pitiriasis alba | Difusa | 0.65 |
| R12 | Eccema | Difusa | 0.82 |
| R13 | Eccema | Difusa | 0.85 |
| R14 | Eccema [Origen Psicosomático] | Heurística | +0.10 |
| R15 | Estado: Agudo | Determinista | 1.00 |
| R16 | Estado: Crónico | Determinista | 1.00 |
| R17 | Recomendación: Tratamiento tópico leve | Determinista | — |
| R18 | Recomendación: Medicación sistémica | Determinista | — |
| R19 | Pitiriasis alba | Difusa | 0.72 |
| R20 | Recomendación: Derivación urgente | Determinista | — |

---

## Estructura del repositorio

```
src/
└── main.py   ← Clase SistemaExperto + GUI (AppSEDerm) + casos de prueba
```

## Cómo ejecutar

```bash
python src/main.py
```

Al iniciar, el sistema ejecuta los casos de prueba por consola y luego abre la interfaz gráfica.

---

> **Advertencia:** Este sistema es orientativo y no reemplaza la consulta con un médico especialista.
