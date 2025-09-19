#def eins():
#    print (1)

#eins()

#eine funktion namens produkt, die das produkt der beiden zahlen 413 und 78 ausgibt
#def produkt():
#    print (413 * 78)   
#produkt()

#eine funktion namens zufallszahl ,die eine zufälige zahl zwischen -24 und 24 ausgibt
#import random
#def zufallszahl():
#    print (random.randint(-24, 24))
#zufallszahl()

# eine funktion namens zufallszahl_positiv, die eine zufällige zahl zwischen -24 und 48 geniriert und true ausgibt falls diese positiv ist ,ansonsten false
import random
def zufallszahl_positiv():
    zahl = random.randint(-24, 48)
    if zahl > 0:
         print(True) 
    else:
        print (False)
print(zufallszahl_positiv())
