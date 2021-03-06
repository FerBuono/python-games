import csv
import gamelib
import os
import random

ANCHO_TABLERO = 400
ALTO_TABLERO = 400
TAM_CASILLERO = ANCHO_TABLERO // 8
CASILLEROS = 8
VACIO = ''
PIEZA_ACTIVA = 'activa'
PIEZA_POSIBLE = 'posible'
SANGRIA_TEXTO = TAM_CASILLERO * 0.5
RUTA_MOVIMIENTOS = 'movimientos.csv'
RUTA_GUARDADO = 'guardado.csv'
RESPUESTAS_PROMPT = {'si': True, 'no': False}


def cargar_juego():
    '''
        Devuelve el tablero del juego guardado en guardado.csv, y el respectivo nivel
    '''
    juego = [['' for j in range(CASILLEROS)] for i in range(CASILLEROS)]
    nivel = 0

    with open(RUTA_GUARDADO) as guardado:
        for fila in csv.reader(guardado):
            posicion, pieza, estado = fila
            fil, col = posicion.split(';')
            juego[int(fil)][int(col)] = (pieza, estado)
            nivel += 1
            
    return juego, nivel - 2


def guardar_juego(juego):
    with open(RUTA_GUARDADO, "w", newline = '') as guardado:
        guardado = csv.writer(guardado)
        for fil in range(len(juego)):
            for col in range(len(juego[fil])):
                if juego[fil][col] != VACIO:
                    pieza, estado = juego[fil][col]
                    guardado.writerow([f'{fil};{col}', pieza, estado])


def cargar_movimientos_piezas():
    '''
        Devuelve un diccionario con las piezas como clave y una lista de sus posibles movimientos como valor
    '''
    movimientos = {}

    with open(RUTA_MOVIMIENTOS) as movs:
        for linea in csv.reader(movs):
            pieza, extensible = linea[0], linea[2]
            direccion = linea[1].split(';')

            if extensible == 'true':
                for i in range(1, CASILLEROS + 1):
                    movimientos[pieza] = movimientos.get(pieza, []) + [tuple(i * int(x) for x in direccion)]
            else:
                movimientos[pieza] = movimientos.get(pieza, []) + [tuple(int(x) for x in direccion)]
    
    return movimientos


def juego_nuevo(movimientos, nivel):
    '''
        Crea un juego nuevo dependiendo el nivel pasado, con su pieza activa y las posibles
    '''
    juego = [['' for j in range(CASILLEROS)] for i in range(CASILLEROS)]
    
    pos_x_original, pos_y_original = random.randint(0, CASILLEROS - 1), random.randint(0, CASILLEROS - 1)
    pieza_original = random.choice(list(movimientos))
    
    juego[pos_y_original][pos_x_original] = (pieza_original, PIEZA_ACTIVA)
    
    pieza = pieza_original
    pos_x, pos_y = pos_x_original, pos_y_original
    
    for i in range(1, nivel + 2):
        while True:

            dir_x, dir_y = random.choice(movimientos[pieza])
            suma_x, suma_y = pos_x + dir_x, pos_y + dir_y

            if suma_x in range(CASILLEROS) and suma_y in range(CASILLEROS) and juego[suma_y][suma_x] == VACIO:
            
                pieza = random.choice(list(movimientos))
                pos_x, pos_y = suma_x, suma_y 

                juego[pos_y][pos_x] = (pieza, '')
                
                if (dir_x, dir_y) in movimientos[pieza_original]:
                    juego[pos_y][pos_x] = (pieza, PIEZA_POSIBLE)
                    
                break

    guardar_juego(juego)
    return juego


def actualizacion_pieza_activa(juego, pieza, casillero_x, casillero_y):
    # Busco la posici??n de la pieza activa y borro el estado de todas
    pos_x_activa, pos_y_activa = '', ''

    for fil in range(len(juego)):
        for col in range(len(juego[fil])):
            if juego[fil][col] != VACIO:
                if juego[fil][col][1] == PIEZA_ACTIVA:
                    pos_x_activa, pos_y_activa = col, fil

                juego[fil][col] = (juego[fil][col][0], '')

    juego[casillero_y][casillero_x] = (pieza, PIEZA_ACTIVA)
    juego[pos_y_activa][pos_x_activa] = VACIO


def actualizacion_piezas_posibles(juego, pieza, casillero_x, casillero_y, movimientos):
    # Cambio el estado de las nuevas piezas posibles
    for direccion in movimientos[pieza]:
        dir_x, dir_y = direccion

        for fil in range(len(juego)):
            for col in range(len(juego[fil])):
                suma_x, suma_y = dir_x + casillero_x, dir_y + casillero_y
                if suma_x == col and suma_y == fil and juego[fil][col] != VACIO:
                    juego[fil][col] = (juego[fil][col][0], PIEZA_POSIBLE)

def juego_actualizar(movimientos, juego, x, y):
    '''
        Actualiza el juego y el estado de las piezas dependiendo del movimiento realizado
    '''
    casillero_x, casillero_y = x // TAM_CASILLERO, y // TAM_CASILLERO
    
    if not casillero_x in range(CASILLEROS) or not casillero_y in range(CASILLEROS) or juego[casillero_y][casillero_x] == VACIO:
        return juego

    pieza, estado = juego[casillero_y][casillero_x]

    if estado != PIEZA_POSIBLE:
        return juego
    
    actualizacion_pieza_activa(juego, pieza, casillero_x, casillero_y)
    actualizacion_piezas_posibles(juego, pieza, casillero_x, casillero_y, movimientos)

    return juego


def juego_mostrar(juego, nivel):
    '''
        Dibuja el tablero de ajedr??z con las piezas en sus estados correspondientes
    '''
    gamelib.draw_begin()

    gamelib.draw_rectangle(0, 0, ANCHO_TABLERO, ALTO_TABLERO + 75, fill="black")

    for casillero_x in range(CASILLEROS):
        for casillero_y in range(CASILLEROS):
            
            if (casillero_x + casillero_y) % 2 == 0:
                gamelib.draw_rectangle(casillero_x * TAM_CASILLERO + 2, casillero_y * TAM_CASILLERO + 2, TAM_CASILLERO * (casillero_x + 1) - 2, TAM_CASILLERO * (casillero_y + 1) - 2, fill='#2D2D3F')
            else:
                gamelib.draw_rectangle(casillero_x * TAM_CASILLERO + 2, casillero_y * TAM_CASILLERO + 2, TAM_CASILLERO * (casillero_x + 1) - 2, TAM_CASILLERO * (casillero_y + 1) - 2, fill='#171717')

            if juego[casillero_y][casillero_x] != VACIO:
                pieza, estado = juego[casillero_y][casillero_x]

                if estado == PIEZA_ACTIVA:
                    gamelib.draw_image(f"img/{pieza}_rojo.gif", (casillero_x * TAM_CASILLERO) + 3, (casillero_y * TAM_CASILLERO) + 3)
                elif estado == PIEZA_POSIBLE:
                    gamelib.draw_rectangle(casillero_x * TAM_CASILLERO + 3, casillero_y * TAM_CASILLERO + 3, TAM_CASILLERO * (casillero_x + 1) - 2, TAM_CASILLERO * (casillero_y + 1) - 2, fill = '', outline = 'red', width = '2')
                    gamelib.draw_image(f"img/{pieza}_blanco.gif", (casillero_x * TAM_CASILLERO) + 3, (casillero_y * TAM_CASILLERO) + 3)
                elif estado == '':
                    gamelib.draw_image(f"img/{pieza}_blanco.gif", (casillero_x * TAM_CASILLERO) + 3, (casillero_y * TAM_CASILLERO) + 3)

    gamelib.draw_text('SHAPE SHIFTER CHESS', SANGRIA_TEXTO, ALTO_TABLERO + 15, size = 10, bold = True, anchor = 'nw')
    gamelib.draw_text(f'Nivel: {nivel}', SANGRIA_TEXTO, ALTO_TABLERO + 40, size = 10, bold = True, anchor = 'nw')
    gamelib.draw_text('Salir: Esc', SANGRIA_TEXTO + ANCHO_TABLERO // 2, ALTO_TABLERO + 15, size = 10, bold = True, anchor = 'nw')
    gamelib.draw_text('Reintentar: Z', SANGRIA_TEXTO + ANCHO_TABLERO // 2, ALTO_TABLERO + 40, size = 10, bold = True, anchor = 'nw')

    gamelib.draw_end()

def main():
    movimientos = cargar_movimientos_piezas()
    juego = []
    nivel = 0 
    cargar = None
    
    # Verifico si hay un juego guardado para cargar
    if os.path.exists(RUTA_GUARDADO):
        while True:
            cargar = gamelib.input('??Quiere continuar el juego guardado? (Si/No)')
            if cargar == None:
                return
            if cargar.lower() in RESPUESTAS_PROMPT:
                cargar = RESPUESTAS_PROMPT[cargar.lower()]
                break

    if cargar:
        juego, nivel = cargar_juego()
    else:
        nivel = 1
        juego = juego_nuevo(movimientos, nivel)
    
    gamelib.title("Shape Shifter Chess")
    gamelib.resize(ANCHO_TABLERO, ALTO_TABLERO + 75)

    while gamelib.is_alive():
        juego_mostrar(juego, nivel)

        ev = gamelib.wait()
        if not ev:
            break

        if ev.type == gamelib.EventType.ButtonPress and ev.mouse_button == 1:
            # Chequear si se sigue pas?? el nivel dependiendo de las piezas en el tablero
            x, y = ev.x, ev.y
            juego = juego_actualizar(movimientos, juego, x, y)
                
            piezas_tablero = [juego[fil][col] for fil in range(len(juego)) for col in range(len(juego[fil])) if juego[fil][col] != VACIO ]
            
            if len(piezas_tablero) == 1:
                nivel += 1
                juego = juego_nuevo(movimientos, nivel)
            
        elif ev.type == gamelib.EventType.KeyPress:

            if ev.key == 'Escape':
                # Finalizar juego
                break

            if ev.key == 'z' or ev.key == 'Z':
                # Reiniciar juego
                juego, nivel = cargar_juego()

gamelib.init(main)