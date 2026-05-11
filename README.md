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

## Casos de Prueba

El sistema incluye 6 casos de prueba, uno por cada diagnóstico posible. Se ejecutan automáticamente al iniciar y también pueden cargarse desde la interfaz gráfica con un click.

| # | Caso | Localización | Morfología | Color | Picazón | Antigüedad | Estrés | Diagnóstico esperado |
|---|------|-------------|------------|-------|:-------:|:----------:|:------:|---------------------|
| 1 | Psoriasis crónica | Codos | Escama | Blanco nacarado | 7/10 | 8 meses | Sí | Psoriasis |
| 2 | Acné agudo | Cara | Pápula | Rojo | 2/10 | 1 mes | No | Acné |
| 3 | Dishidrosis | Pies | Ampolla | Rosado | 8/10 | 2 meses | No | Dishidrosis |
| 4 | Pitiriasis alba | Cara | Mácula | Rosado | 1/10 | 5 meses | No | Pitiriasis alba |
| 5 | Onicomicosis | Uñas | Engrosamiento | Amarillento | 0/10 | 10 meses | No | Onicomicosis |
| 6 | Eccema con estrés | Flexuras | Escama | Rojo | 8/10 | 2 meses | Sí | Eccema |

---

## Funcionalidades de la Interfaz

- **Barra de casos de prueba**: botones en la parte superior (`C1`–`C6`) que cargan automáticamente todos los campos del formulario con los datos del caso correspondiente.
- **Guía visual `►`**: al seleccionar una localización, las morfologías válidas según las reglas se marcan con `►` en el desplegable. Al elegir morfología, se marcan los colores válidos.
- **Subsistema de explicación**: muestra las reglas activadas, el tipo de lógica aplicada y la certeza acumulada por diagnóstico.

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

Al iniciar, el sistema ejecuta los 6 casos de prueba por consola y luego abre la interfaz gráfica.

---

> **Advertencia:** Este sistema es orientativo y no reemplaza la consulta con un médico especialista.
