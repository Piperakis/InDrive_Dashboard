#Author @Piperakis

# This work is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-nd/4.0/.

import math
import sys
import pygame as pg
import random
import time

pg.init()

#set size of screen
size = width, height = 800, 480

screen = pg.display.set_mode(size)

#Voltage Threshold
maxLV = 14
minLV = 11

maxHV = 588
minHV = 380

warnCurrent = 3
warnAmps = 80

#Temp Thresholds
maxMotorTemp = 45
maxBatteryTemp = 45
maxIGPTTemp = 50

#Rpm Threshold
maxRPM = 5000

#Car parameters to calculate RPM
wheel_diameter_m = 0.5  # Wheel diameter in meters (500 mm)
gear_ratio = 1  # Gear ratio
final_drive_ratio = 3.5  # Final drive ratio

#Import Assets
panelOK = pg.image.load('Assets/MainOK.png')
RPM = pg.image.load('Assets/RPM.png')

BatNOK =  pg.image.load('Assets/BatteriesNotOK.png')
BatOK =  pg.image.load('Assets/BatteriesOK.png')

TempsOK =  pg.image.load('Assets/TempsOK.png')
TempsNotOK =  pg.image.load('Assets/TempsNotOK.png')

PackOK =  pg.image.load('Assets/PackOK.png')
PackNotOK =  pg.image.load('Assets/PackNotOK.png')

AppsOK =  pg.image.load('Assets/APPSOk.png')
AppsNotOK =  pg.image.load('Assets/APPSNotOk.png')

AmpsOk = pg.image.load('Assets/AmpOK.png')
AmpsNotOk = pg.image.load('Assets/AmpNotOK.png')

#Set Colors and Fonts
FONT = pg.font.Font(None, 36)
BACKGROUND_COLOR = (37, 225, 192)
BLUE = (199, 199, 199)
GRAY = (0, 0, 55)
BLACK = (0, 0, 0)

# Function to draw centered text based on text length
def draw_centered_text(text, base_x, y, color, size):
    font = pg.font.Font('Assets/MYRIADPRO-REGULAR.OTF', size)
    text_surface = font.render(text, True, color)
    text_width = text_surface.get_width()
    screen.blit(text_surface, (base_x - text_width // 2, y))

#Func for printing text on screen
#Parameters Text, x,y position, color and text size
def draw_text(text, x, y, color, size):
    font = pg.font.Font('Assets/MYRIADPRO-REGULAR.OTF', size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def draw_right_aligned_text(text, base_x, y, color, size):
    font = pg.font.Font('Assets/MYRIADPRO-REGULAR.OTF', size)
    text_surface = font.render(text, True, color)
    text_width = text_surface.get_width()
    screen.blit(text_surface, (base_x - text_width, y))

#Used for vertical progress bars - HV, LV
class ProgressBar:
    def __init__(self, x, y, width, height, color, outline_color=(0, 0, 0)):
        self.rect = pg.Rect(x, y, width, height)
        self.color = color
        self.outline_color = outline_color
        self.progress = 0

    def update_progress(self, progress):
        self.progress = min(max(progress, 0), 100)  # Clamp progress between 0 and 100

    def draw(self, screen):
        temp_surface = pg.Surface(self.rect.size).convert_alpha()
        temp_surface.fill((0, 0, 0, 0))  # Transparent background

        inner_rect = pg.Rect(0, 0, self.rect.width * (self.progress / 100), self.rect.height)  # Draw on temp surface
        pg.draw.rect(temp_surface, self.color, inner_rect)
        pg.draw.rect(temp_surface, self.outline_color, inner_rect, 2)

        # Flip the temporary surface horizontally
        flipped_surface = pg.transform.flip(temp_surface, True, False) 

        # Blit the flipped surface to the screen
        screen.blit(flipped_surface, self.rect)


#Used for horizontal progress bars - RPM
class Bar():
    def __init__(self, rect, bar=BLACK, outline=GRAY):
        self.rect = pg.Rect(rect)
        self.bar = bar
        self.outline = outline
        self.value = 0

    def draw(self, surf):
        length = round((100 - self.value) * self.rect.height / 100)  # Inverted calculation
        top = self.rect.y  # Draw from the top of the Rect
        pg.draw.rect(surf, self.bar, (self.rect.x, top, self.rect.width, length))
        pg.draw.rect(surf, self.outline, self.rect, 2)

def calculate_rpm(speed_kmh, wheel_diameter_m, gear_ratio, final_drive_ratio):
    # Convert speed from km/h to m/s
    speed_mps = speed_kmh * 1000 / 3600
    
    # Calculate the wheel circumference in meters
    wheel_circumference = wheel_diameter_m * math.pi
    
    # Calculate the wheel RPM
    wheel_rpm = speed_mps / wheel_circumference * 60
    
    # Calculate the engine RPM
    engine_rpm = wheel_rpm * gear_ratio * final_drive_ratio
    
    return engine_rpm


def drawSpeed(speed):
    #Draw RPM
    RPMs = calculate_rpm(speed,wheel_diameter_m,gear_ratio,final_drive_ratio)
    surface.blit(RPM, (17, 25)) 
    RPMpercentage = int((RPMs/maxRPM) * 100)
    

    my_progress_bar.update_progress(100-RPMpercentage)
    my_progress_bar.draw(screen)
    surface.blit(panelOK, (-1, -1)) 

    draw_right_aligned_text("{:.0f}".format(speed), 400, 100, (255, 255, 255), 100)
    draw_right_aligned_text("{:.0f}".format(RPMs), 400, 206, (255, 255, 255), 60)


def drawLow(volt):
    # Calculate battery percentage
    percentage = int(((volt - minLV) / (maxLV - minLV))*100)

    # Visualization of Battery Percentage
    BatteryLV.value = percentage
    BatteryLV.draw(screen)

    # Battery percentage (centered)
    draw_centered_text(f"{percentage}%", 732, 390, (255, 255, 255), 28)
    draw_centered_text(f"{volt:.2f}v", 732, 415, (255, 255, 255), 28)

def drawHigh(volt):
    # Calculate battery percentage
    percentage = int(((volt - minHV) / (maxHV - minHV))*100)

    # Visualization of Battery Percentage
    BatteryHV.value = percentage
    BatteryHV.draw(screen)

    # Battery percentage (centered)
    draw_centered_text(f"{percentage}%", 644, 390, (255, 255, 255), 28)
    draw_centered_text(f"{volt:.0f}v", 644, 415, (255, 255, 255), 28)


def drawVoltages(LV, HV):
    drawHigh(HV)
    drawLow(LV)

    pHV = int(((HV - minHV) / (maxHV - minHV))*100)
    pLV = int(((LV - minLV) / (maxLV - minLV))*100)

    if(pHV > 20 and pLV > 20):
        surface.blit(BatOK, (592, 140)) 
    else:
        surface.blit(BatNOK, (592, 140)) 


def drawTemps(MT, BT, IGPT):
    if(MT < maxMotorTemp and BT < maxBatteryTemp and IGPT < maxIGPTTemp):
        surface.blit(TempsOK, (20, 140))
    else:
       surface.blit(TempsNotOK, (20, 140)) 

    draw_text("Motor", 34, 164, (255, 255, 255), 32)
    draw_text("Battery", 34, 219, (255, 255, 255), 32)
    draw_text("IGBT", 34, 274, (255, 255, 255), 32)

    draw_text(str("{:.0f}".format(MT)) + "°", 134, 155, (255, 255, 255), 55)
    draw_text(str("{:.0f}".format(BT)) + "°", 134, 209, (255, 255, 255), 55)
    draw_text(str("{:.0f}".format(IGPT)) + "°", 134, 264, (255, 255, 255), 55)

def drawPackC(current):
    if(current > warnCurrent):
        surface.blit(PackOK, (20, 376))
    else:
        surface.blit(PackNotOK, (20, 376))
    draw_centered_text(str("{:.1f}".format(current))+"v", 118, 382, (255, 255, 255), 70)

def drawAPPS(APPS):
    if APPS:
        surface.blit(AppsOK, (290, 374))
    else:
        surface.blit(AppsNotOK, (290, 374))

def DrawApms(Amps):
    if Amps < warnAmps:
        surface.blit(AmpsOk, (290, 280))
    else:
        surface.blit(AppsNotOK, (290, 376))
    
    draw_centered_text(str("{:.1f}".format(Amps))+" A", 410, 287, (255, 255, 255), 65)


BatteryHV = Bar((608, 160, 65, 227)) #1,2: x,y landmarks 2,3 x,y size
BatteryLV = Bar((699, 160, 65, 227))

my_progress_bar = ProgressBar(17, 0, 765, 100, BLACK)

done = False

surface= pg.display.set_mode((width, height)) 
pg.display.set_caption('InDrive Dash')

while True:
    drawSpeed(random.uniform(0, 120))# speed, RPM


    drawTemps(random.uniform(11, 55),random.uniform(11, 55), random.uniform(11, 55))

    # Draw Battery Percentages
    drawVoltages(random.uniform(11, 14), random.randrange(380,588))

    drawPackC(149.9)

    drawAPPS(False)
    DrawApms(39.1)

    pg.display.flip()
    
    # event of quiting
    for event in pg.event.get() :    
        if event.type == pg.QUIT : 
            pg.quit()  
            quit() 
        pg.display.update()


    time.sleep(0.9) 