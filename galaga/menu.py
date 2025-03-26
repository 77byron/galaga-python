# Importaciones del juego
import pygame, random
# Enrutamiento de imágenes y archivos en la carpeta assets
import os

# TAMAÑO DEL LIENZO
WIDTH = 800
HEIGHT = 600
BLACK = (0, 0, 0) 
WHITE = (255, 255, 255)
ROOT_DIR = os.path.dirname(__file__)
IMAGE_DIR = os.path.join(ROOT_DIR, 'assets')

# Inicialización de Pygame
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('GALAGA')
clock = pygame.time.Clock()

# Fuente para mostrar la puntuación
font = pygame.font.SysFont('Arial', 36)

# Clase para la nave
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(IMAGE_DIR, 'nave.png')).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10 
        self.speed_x = 0
        self.mask = pygame.mask.from_surface(self.image)  # Máscara de colisión para la nave
        
    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -5
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        self.mask = pygame.mask.from_surface(self.image)  # Actualizar la máscara de colisión

# Clase para los meteoritos
class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(IMAGE_DIR, 'meteoro.png'))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 10)
        self.speedx = random.randrange(-5, 5) 
        self.mask = pygame.mask.from_surface(self.image)  # Máscara de colisión para el meteorito
        
    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        # Si el meteorito sale de la pantalla, se reposiciona arriba
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 25:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 10)
        self.mask = pygame.mask.from_surface(self.image)  # Actualizar la máscara de colisión

# Clase para los disparos
class Disparo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(os.path.join(IMAGE_DIR, 'disparos.png')).convert()  # Asegúrate de tener 'disparos.png'
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10  # Velocidad del disparo (hacia arriba)

    def update(self):
        self.rect.y += self.speedy
        # Eliminar el disparo si sale de la pantalla
        if self.rect.bottom < 0:
            self.kill()

# Clase para la explosión
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.images = []  # Lista para almacenar los frames de la explosión
        for i in range(9):  # Supongamos que tienes 9 frames de explosión
            img = pygame.image.load(os.path.join(IMAGE_DIR, f'explosion.png')).convert()
            img.set_colorkey(BLACK)
            self.images.append(img)
        self.image = self.images[0]  # Empezar con el primer frame
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0  # Frame actual
        self.last_update = pygame.time.get_ticks()  # Tiempo del último cambio de frame
        self.frame_rate = 30  # Reducir este valor para que la explosión dure menos (ms por frame)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.images):  # Si se llegó al último frame
                self.kill()  # Eliminar la explosión
            else:
                center = self.rect.center
                self.image = self.images[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# Cargar el fondo y la imagen del corazón
background = pygame.image.load(os.path.join(IMAGE_DIR, 'espacio.jpg')).convert()
corazon_img = pygame.image.load(os.path.join(IMAGE_DIR, 'corazon.jpg')).convert()  # Asegúrate de tener 'corazon.png'
corazon_img.set_colorkey(BLACK)

# Grupos de sprites
all_sprites = pygame.sprite.Group()
meteor_list = pygame.sprite.Group()
disparos = pygame.sprite.Group()  # Nuevo grupo para los disparos

# Crear el jugador
player = Player()
all_sprites.add(player)

# Crear meteoritos iniciales
for i in range(8):
    meteor = Meteor()
    all_sprites.add(meteor)
    meteor_list.add(meteor)

# Variables para las vidas y puntuación
vidas = 3  # Número inicial de vidas
puntuacion = 0  # Puntuación inicial

# Bucle principal del juego
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Disparar cuando se presiona la tecla Espacio
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                disparo = Disparo(player.rect.centerx, player.rect.top)  # Crear un disparo
                all_sprites.add(disparo)  # Añadir el disparo al grupo de sprites
                disparos.add(disparo)  # Añadir el disparo al grupo de disparos

    # Detectar colisiones entre disparos y meteoritos
    colisiones = pygame.sprite.groupcollide(disparos, meteor_list, True, True)
    # Si hay colisiones, se eliminan tanto los disparos como los meteoritos
    for disparo, meteoritos in colisiones.items():
        for meteorito in meteoritos:
            # Crear una explosión en la posición del meteorito
            explosion = Explosion(meteorito.rect.center)
            all_sprites.add(explosion)
            puntuacion += 100  # Sumar 100 puntos por cada meteorito destruido

    # Detectar colisiones entre la nave y los meteoritos (usando máscaras)
    for meteor in meteor_list:
        if pygame.sprite.collide_mask(player, meteor):  # Colisión precisa con máscaras
            vidas -= 1  #    Restar una vida
            meteor.kill()  # Eliminar el meteorito
            if vidas == 0:  # Si se quedan sin vidas
                running = False  # Terminar el juego

    # Reponer meteoritos si se destruyen o salen de la pantalla
    if len(meteor_list) < 8:  # Mantener un mínimo de 8 meteoritos
        meteor = Meteor()
        all_sprites.add(meteor)
        meteor_list.add(meteor)

    # Actualizar todos los sprites
    all_sprites.update()

    # Dibujar el fondo   
    screen.blit(background, [0, 0])

    # Dibujar todos los sprites
    all_sprites.draw(screen)

    # Mostrar las vidas  
    for i in range(vidas):  # Dibujar un corazón por cada vida restante
        screen.blit(corazon_img, (10 + i * 40, 10))  # Espaciado de 40 píxeles entre corazones

    # Mostrar la puntuación en la pantalla
    texto_puntuacion = font.render(f'Puntuación: {puntuacion}', True, WHITE)
    screen.blit(texto_puntuacion, (WIDTH - 250, 10))  # Posición en la esquina superior derecha

    # Actualizar la pantalla
    pygame.display.flip()

# Mensaje de fin de juego
if vidas == 0:
    print(f"¡Game Over! Te quedaste sin vidas. Puntuación final: {puntuacion}")
pygame.quit()            

