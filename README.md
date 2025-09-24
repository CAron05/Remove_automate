# Proyecto: Limpieza de Archivos en Python

Script sencillo en Python para borrar o mover archivos viejos de una carpeta.  
Está pensado para limpiar la carpeta **Descargas** de Windows, pero sirve en cualquier otra.

Por defecto solo hace una **simulación** (no borra nada).  
Si se añade la opción `--confirm` entonces sí borra o mueve los archivos.

---

## Requisitos
- Python 3.8 o superior
- Funciona en Windows (probado en `C:\Users\alvar\Downloads`)

---

## Ejemplos de uso

### Simulación (no borra nada)
```bash
python cleanup.py --path "C:\Users\alvar\Downloads" --extensions .tmp,.log --older-than 7
```

### Borrado real (añadir --confirm)
```bash
python cleanup.py --path "C:\Users\alvar\Downloads" --pattern "*.iso" --older-than 30 --confirm
```

### Mover a carpeta "papelera"
```bash
python cleanup.py --path "C:\Users\alvar\Downloads" --extensions .bak --older-than 10 --trash "C:\Users\alvar\Downloads\.papelera" --confirm
```
