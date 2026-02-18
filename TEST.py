import sys
import random
import pygame
import euclid
import math

# Définition de la résolution de l'écran
screen_size = screen_width, screen_height = 1200, 600

# Définition de l'écran
screen = pygame.display.set_mode(screen_size)
# Définition du timer et du titre de la fenêtre
clock = pygame.time.Clock()
pygame.display.set_caption("Astro Balls")

G = 100
vitesse_simulation = 1

class Objets:

    @staticmethod
    def terre():
        terre = {
            "masse" : 10,
            "rayon" : 10,
            "couleur" : (0,0,255),
            "position" : euclid.Vector2(800, 100),
            "vitesse" : euclid.Vector2(0,0)
        }
        return terre

    @staticmethod
    def lune():
        lune = {
            "masse" : 1,
            "rayon" : 2,
            "couleur" : (200,200,200),
            "position" : euclid.Vector2(815, 85),
            "vitesse" : euclid.Vector2(0,0)
        }
        return lune

    @staticmethod
    def soleil():
        soleil = {
            "masse" : 500,
            "rayon" : 50,
            "couleur" : (255,222,0),
            "position" : euclid.Vector2(600, 300),
            "vitesse" : euclid.Vector2(0,0)
            }
        return soleil


class Display:
    def __init__(self, position, couleur, rayon, vitesse = euclid.Vector2(0,0)):
        self.position = position
        self.vitesse = vitesse
        self.couleur = couleur
        self.rayon = rayon

    def mouvement(self, acceleration, dtemps):
        self.vitesse += acceleration * dtemps
        self.position += self.vitesse * dtemps

    def display(self):
        rx, ry = int(self.position.x), int(self.position.y)
        pygame.draw.circle(screen, self.couleur, (rx,ry), self.rayon)


def force_gravitationnelle(obj1, obj2):
    d_vecteur = obj2["position"] - obj1["position"]
    distance = d_vecteur.magnitude()
    distance = max(distance, 1)
    d_vecteur.normalize()

    acceleration = d_vecteur*(G * obj2["masse"] / distance**2)

    return acceleration

def vitesse_gravitationnelle(obj1, obj2):
    d_vecteur = obj2["position"] - obj1["position"]
    distance = d_vecteur.magnitude()
    d_vecteur.normalize()
    tangente = euclid.Vector2(-d_vecteur.y, d_vecteur.x)

    v_orbitale = math.sqrt(G * obj1["masse"] / distance)
    v_orbitale = v_orbitale * tangente

    return v_orbitale

"""ICI TRÈS IMPORTANT"""
"""ICI TRÈS IMPORTANT"""

terre = Objets.terre()
soleil = Objets.soleil()
lune = Objets.lune()
terre["vitesse"] = vitesse_gravitationnelle(soleil, terre)
lune["vitesse"] = vitesse_gravitationnelle(terre, lune) + terre["vitesse"]

"""ICI TRÈS IMPORTANT"""
"""ICI TRÈS IMPORTANT"""

display_terre = Display(terre["position"], terre["couleur"], terre["rayon"], terre["vitesse"])
display_lune = Display(lune["position"], lune["couleur"], lune["rayon"], lune["vitesse"])
display_soleil = Display(soleil["position"], soleil["couleur"], soleil["rayon"], soleil["vitesse"])


# Définition des paramètres de la fenêtre
tick_direction = 0.0
fps_limit = 120
running = True
while running:
    dtemps_ms = clock.tick(fps_limit)
    dtemps = dtemps_ms/1000 * vitesse_simulation

    tick_direction += dtemps
    if tick_direction > 1:
        tick_direction = 0.0


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    acceleration_terre = force_gravitationnelle(terre, soleil)
    acceleration_lune = force_gravitationnelle(lune, terre) + force_gravitationnelle(lune, soleil)

    # Mise à jour positions dictionnaire
    terre["vitesse"] += acceleration_terre * dtemps
    terre["position"] += terre["vitesse"] * dtemps

    lune["vitesse"] += acceleration_lune * dtemps
    lune["position"] += lune["vitesse"] * dtemps

    # Synchroniser display avec dictionnaire
    display_terre.position = terre["position"]
    display_terre.vitesse = terre["vitesse"]

    display_lune.position = lune["position"]
    display_lune.vitesse = lune["vitesse"]

    screen.fill((0, 0, 0))

    display_soleil.display()
    display_terre.display()
    display_lune.display()


    # Afficher tout sur l'écran
    pygame.display.flip()

#Quitter
pygame.quit()
sys.exit()


