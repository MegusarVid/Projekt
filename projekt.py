from tkinter import *
import os
import random

g = 9.8 * 10  # 1 meter = 10 točk na zaslonu

dt = 0.01
širina = 500
višina = 410
radij_top = 6
radij_metk = 3
hitrost_metka = 40
radij_krogla = 20
cilj = 5


class Animacija:
    def __init__(self, master):

        self.stevec_strelov = 0
        self.stevec_zadetkov = 0
        self.dt = dt


        # Naredimo področje za streljanje
        self.canvas = Canvas(master, width=širina, height=višina)
        self.canvas.grid(row=1, column=0, columnspan=2)

        #dodamo ozadje
        self.image = PhotoImage(file="12.png")
        self.canvas.create_image(0, 0, anchor=NW, image=self.image, tags="bg_img")

        #dodamo števec strelov, števec zadetkov in navodila
        self.napis_streli = Label(master, text='stevilo poskusov: {}'.format(self.stevec_strelov))
        self.napis_streli.grid(row=2, column=0)

        self.napis_zadetki = Label(master, text='stevilo zadetkov: {}'.format(self.stevec_zadetkov))
        self.napis_zadetki.grid(row=2, column=1)

        self.navodilo = Label(master, text='Cilj igre je {}x zadeti veliko kroglo.'.format(cilj))
        self.navodilo.grid(row=0, column=0, columnspan=2)

        #Ustvarimo in premikamo top
        self.canvas.bind("<Motion>", self.prestavi)
        self.top = self.canvas.create_rectangle(širina / 2 - radij_top, višina, širina / 2 - radij_top, višina - 2 * radij_top, fill='red')

        #ustvarimo in ustrelimo metk
        self.metk = Metk(radij_metk, 10, višina - 2 * radij_top)
        self.canvas.bind("<Button-1>", self.ustreli)

        #naredimo kroglo, ki jo bomo streljali
        self.energija = DoubleVar(master)
        self.dt = dt
        self.krogla = Krogla(radij_krogla, širina, višina)
        self.krogla_id = self.canvas.create_oval(self.krogla.x - self.krogla.r,
                                                 self.krogla.y - self.krogla.r,
                                                 self.krogla.x + self.krogla.r,
                                                 self.krogla.y + self.krogla.r,
                                                 fill = "green")
        self.animacija_krogla()

    #funkcija za prestaljanje topa
    def prestavi(self, event):
        (x, y) = (event.x, event.y)
        self.canvas.coords(self.top, x-radij_top, višina, x+radij_top, višina - 2 * radij_top)

    #funkcija za strel
    def ustreli(self, event):
            self.stevec_strelov += 1
            self.napis_streli['text'] = 'stevilo poskusov: {}'.format(self.stevec_strelov)
            (x, y) = (event.x, event.y)
            self.metk = Metk(radij_metk, x, višina - 2 * radij_top)
            self.metk_id = self.canvas.create_oval(self.metk.x - self.metk.r,
                                                     self.metk.y - self.metk.r,
                                                     self.metk.x + self.metk.r,
                                                     self.metk.y + self.metk.r,
                                                     fill = "red")
            self.animacija_metk()

    #funkcija za gibanje in uničenje metka
    def animacija_metk(self):
        self.metk.premakni(self.dt)
        self.canvas.coords(self.metk_id,
                           self.metk.x - self.metk.r,
                           self.metk.y - self.metk.r,
                           self.metk.x + self.metk.r,
                           self.metk.y + self.metk.r)

        if (abs(self.metk.x - self.krogla.x)) ** 2 + (abs(self.metk.y - self.krogla.y)) ** 2 < (radij_krogla + radij_metk) ** 2:
            self.stevec_zadetkov += 1
            if self.stevec_zadetkov == cilj:
                root.quit()
                with open('rezultat.txt', 'wt', encoding='utf8') as self.f:
                    self.f.write('Zadeli ste {} žogic v {} poskusih, vaša natančnost je {}%'.format(cilj, self.stevec_strelov, round(cilj / self.stevec_strelov * 100), 2))
                os.startfile('rezultat.txt')
            self.napis_zadetki['text'] = 'stevilo zadetkov: {}'.format(self.stevec_zadetkov)

            self.canvas.delete('all')
            self.canvas.create_image(0, 0, anchor=NW, image=self.image, tags="bg_img")
            self.canvas.bind("<Motion>", self.prestavi)
            self.top = self.canvas.create_rectangle(širina/2 - radij_top, višina, širina/2 - radij_top, višina - 2 * radij_top, fill='red')
            self.canvas.bind("<Button-1>", self.ustreli)
            self.krogla = Krogla(radij_krogla, širina, višina)
            self.krogla_id = self.canvas.create_oval(self.krogla.x - self.krogla.r,
                                                     self.krogla.y - self.krogla.r,
                                                     self.krogla.x + self.krogla.r,
                                                     self.krogla.y + self.krogla.r,
                                                     fill = "green")

        elif self.metk.y < -10:
            self.canvas.delete(self.metk)
            self.canvas.bind("<Button-1>", self.ustreli)
        else:
            self.canvas.after(int(self.dt*100), self.animacija_metk)
            self.canvas.unbind("<Button-1>")

    #funkcija, ki skrbi za gibanje krogle
    def animacija_krogla(self):
        self.krogla.premakni(self.dt)
        self.energija.set(self.krogla.energija())
        self.canvas.coords(self.krogla_id,
                           self.krogla.x - self.krogla.r,
                           self.krogla.y - self.krogla.r,
                           self.krogla.x + self.krogla.r,
                           self.krogla.y + self.krogla.r)

        self.canvas.after(int(self.dt*500), self.animacija_krogla)



class Metk():
    #kroglica, ki jo ustreli top

    def __init__(self, r, x, y):

        self.r = r
        # Začetna pozicija
        self.x = x
        self.y = y
        # Začetna hitrost
        self.vy = hitrost_metka

    #metoda za izračun nove pozicije metka po času dt
    def premakni(self, dt):
        self.y = self.y - self.vy * dt

class Krogla():
    #Krogla, ki se premika po polju in jo moramo zadeti

    def __init__(self, r, width, height):
        self.width = širina
        self.height = višina
        self.r = r
        # Začetna pozicija
        self.x = random.uniform(r, width - r)
        self.y = random.uniform(r, height - r)
        # Začetna hitrost
        self.vx = random.uniform(-width/3, width/3)
        self.vy = random.uniform(height/4, height/3)

    def energija(self):
        return 0.5 * (self.vx * self.vx + self.vy * self.vy) - g * self.y

    #metoda, ki skrbi za gibanje krogle
    def premakni(self, dt):
        '''Izračunaj novo stanje krogle po preteku časa dt.'''
        self.x = self.x + self.vx * dt
        self.y = self.y + self.vy * dt + 0.5 * g * dt * dt
        # Preverimo odboje
        if self.x - self.r < 0:
            #self.x = self.r
            self.vx = -self.vx
        if self.x + self.r > self.width:
            #self.x = self.width - self.r
            self.vx = -self.vx
        if self.y - self.r < 0:
            #self.y = self.r
            self.vy = -self.vy
        if self.y + self.r > self.height:
            #self.y = self.height - self.r
            self.vy = -self.vy
        self.vy = self.vy + g * dt        # os y kaže navzdol!

root = Tk()
Animacija(root)
mainloop()
