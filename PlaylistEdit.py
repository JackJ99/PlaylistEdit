from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import *
from tkinter import messagebox
import sys
import os
from tinytag import TinyTag

# globale variabele die bijhoudt of er iets aan de lijst is gewijzigd
# zodat er een waarschuwing kan worden gegeven het afsluiten
changesSaved = True
# globale variabele waarin het laatst gebruikte pad wordt bijgehouden
# zodat dit als default kan worden voorgesteld
# initieel de working directory
lastUsedPath = os.getcwd()

# Toon de help-info
def showHelp():
    print("nog niet geïmplementeerd" + '\n')
    return None

# geef een bestaande filenaam om deze te kunnen openen
def diropenfile(title=None, types=None):
    global lastUsedPath
    root = Tk()
    root.withdraw()
    f = askopenfilename(parent=root, initialdir = lastUsedPath, title=title, filetypes=types)
    if len(f) == 0: return None
    lastUsedPath = os.path.dirname(f)
    return f

# Open een bestaande playlist en toon de inhoud op het scherm
def openPlaylist():
    global changesSaved
    if not changesSaved:
        if not messagebox.askokcancel("Pas op!", "Hiermee verwijder je de huidige playlist"):
            return None
    f = diropenfile("Importeer afspeellijst", (("Afspeellijsten","*.m3u"),\
                    ("alle bestanden","*.*")))
    if f == None: return None
    # maak de listbox leeg
    listbox.delete(0, END)
    playlistdir = os.path.dirname(f)
    # voeg de filenamen uit de playlist toe
    pl = open(f, 'r')
    for line in pl:
        # sluit de metagegevens uit
        if line[0:4] != "#EXT":
            ap = os.path.normpath(os.path.join(playlistdir,line))
            # verwijder de EOL alvorens toe te voegen
            listbox.insert(END, ap.rstrip('\n'))
    pl.close()
    listbox.selection_clear(0, END)
    changesSaved = True
    return None

# maak de listbox op het scherm schoon
def clearPlaylist():
    global changesSaved
    if changesSaved:
        listbox.delete(0, END)
        listbox.selection_clear(0, END)
    else:
        if messagebox.askokcancel("Pas op!", "Hiermee verwijder je de huidige playlist"):
            listbox.delete(0, END)
            listbox.selection_clear(0, END)
            changesSaved = True
    return None

# geef de naam van een bestaande map
def diropenfolder(title=None):
    global lastUsedPath
    root = Tk()
    root.withdraw()
    f = askdirectory(parent=root, initialdir = lastUsedPath, title=title)
    if len(f) == 0: return None
    lastUsedPath = f
    return f

# neem de inhoud van het scherm over in een playlist en voeg meta-gegevens toe
# Geef het pad waarin de file is opgeslagen terug.
def fillPlaylist(file):
    global changesSaved
    f = open(file, 'w')
    dirf = os.path.dirname(file)
    # header voor m3u-file
    f.write("#EXTM3U" + '\n')
    for linenumber in range(listbox.size()):
        item = listbox.get(linenumber)
        if os.path.isfile(item):
            tag = TinyTag.get(item)
            f.write("#EXTINF: {: .0f}, {} ".format(tag.duration, tag.title) + '\n')
            f.write(os.path.relpath(item, dirf) + '\n')
        else:
            messagebox.showwarning("Waarschuwing", "onbekende file: " + item)
    # trailer voor m3u-file
    f.write("#EXT-X-ENDLIST" + '\n')
    f.close()
    changesSaved = True
    return dirf

# sla de playlist op
def savePlaylist():
    global lastUsedPath
    root = Tk()
    root.withdraw()
    # define options for opening
    options = {}
    options['parent'] = root
    options['defaultextension'] = ".m3u"
    options['filetypes'] = [("Muziek","*.m3u"),("alle bestanden","*.*")]
    options['initialdir'] = lastUsedPath
    options['initialfile'] = ""
    options['title'] = "Sla lijst op"
    f = asksaveasfilename(**options)
    if len(f) == 0: return None
    lastUsedPath = fillPlaylist(f)
    return None

# selecteer een bestaande playlist en importeer de filenamen in de Listbox
# op de positie van de eerste geselecteerde regel
def selectPlaylist():
    global changesSaved
    f = diropenfile("Kies afspeellijst", (("Afspeellijsten","*.m3u"), \
                    ("alle bestanden","*.*")))
    if f == None: return None
    playlistdir = os.path.dirname(f)
    pl = open(f, 'r')
    selectedFilenames = listbox.curselection()
    nmbSelectedFilenames = len(selectedFilenames)
    for line in pl:
        if line[0:4] != "#EXT":
            ap = os.path.normpath(os.path.join(playlistdir,line))
            # voeg de regels toe, haal de EOL weg
            if nmbSelectedFilenames > 0:
                listbox.insert(selectedFilenames[0], ap.rstrip('\n'))
            else:
                listbox.insert(END, ap.rstrip('\n'))
    pl.close()
    listbox.selection_clear(0, END)
    changesSaved = False
    return None

# Voeg een muziekbestand toe aan de lijst
def selectMusicFile():
    global changesSaved
    f = diropenfile("Kies muziek", [("Muziek","*.mp3" " *.flac" " *.ogg" \
                    " *.opus" " *.wma" " *.mp4" " *.m4a" " *.m4b"),\
                    ("alle bestanden","*.*")])
    if f == "": return None
    #listbox.insert(END, os.path.basename(f))
    listbox.insert(END, f)
    listbox.selection_clear(0, END)
    changesSaved = False
    return None

# Voeg de muziekfiles uit een map toe aan de lijst
def addFolder(pad):
    global changesSaved
    dl = os.listdir(pad)
    for item in dl:
        dir = os.path.join(pad, item)
        if not os.path.islink(dir):
            if os.path.isfile(dir):
                (root, ext) = os.path.splitext(dir)
                extu = ext.upper()
                if extu == ".MP3" \
                or extu == ".OGG" \
                or extu == ".OPUS" \
                or extu == ".FLAC" \
                or extu == ".WMA" \
                or extu == ".MP4" \
                or extu == ".M4A" \
                or extu == ".M4B":
                    listbox.insert(END, dir)
            else:
                if recursiveFolder.get() == 1: addFolder(dir)
    listbox.selection_clear(0, END)
    changesSaved = False
    return None

#Selecteer een map en voeg toe aan de lijst
def selectMusicFolder():
    f = diropenfolder("Kies muziekmap")
    if f ==  None: return None
    addFolder(f)
    return None

# Verplaats de geselecteerde files 1 positie naar beneden
def moveDown():
    global changesSaved
    selectedFilenames = listbox.curselection()
    if len(selectedFilenames) > 0:
        if max(selectedFilenames) < listbox.size() - 1:
            # verwerk de lijst achterstevoren zodat indices niet wijzigingen
            # vanwege de delete
            reversedFilenames = tuple(reversed(selectedFilenames))
            for i in reversedFilenames :
                keep = listbox.get(i + 1)
                listbox.delete(i + 1)
                listbox.insert(i, keep)
            changesSaved = False
    return None

# Verplaats de geselecteerde files naar het einde van de lijst
def moveBottom():
    global changesSaved
    selectedFilenames = listbox.curselection()
    if len(selectedFilenames) > 0:
        sizeListbox = listbox.size()
        if max(selectedFilenames) < sizeListbox - 1:
            # verwerk de lijst achterstevoren zodat indices niet wijzigingen
            # vanwege de delete
            reversedFilenames = tuple(reversed(selectedFilenames))
            insertPos = ""
            for i in reversedFilenames :
                move = listbox.get(i)
                if insertPos ==  "":
                    listbox.insert(END, move)
                    insertPos = sizeListbox - 1
                else:
                    listbox.insert(insertPos, move)
                    insertPos -= 1
                listbox.delete(i)
            listbox.selection_clear(0, END)
            changesSaved = False
    return None

# Verplaats de geselecteerde files naar de bovenkant van de lijst
def moveTop():
    global changesSaved
    #print("moveUp" + '\n')
    selectedFilenames = listbox.curselection()
    #print(selectedFilenames)
    #print('\n')
    if len(selectedFilenames) > 0:
        if min(selectedFilenames) > 0:
            insertPos = 0
            for i in selectedFilenames :
                move = listbox.get(i)
                listbox.insert(insertPos, move)
                insertPos += 1
                listbox.delete(i + 1)
            listbox.selection_clear(0, END)
            changesSaved = False
    return None

# Verplaats de geselecteerde files 1 positie naar boven
def moveUp():
    global changesSaved
    selectedFilenames = listbox.curselection()
    if len(selectedFilenames) > 0:
        if min(selectedFilenames) > 0:
            for i in selectedFilenames :
                keep = listbox.get(i - 1)
                listbox.delete(i - 1)
                listbox.insert(i, keep)
            changesSaved = False
    return None

# Verwijder de geselecteerde files uit de lijst
def removeFilename(event):
    global changesSaved
    selectedFilenames = listbox.curselection()
    if len(selectedFilenames) > 0:
        # verwerk de lijst achterstevoren zodat indices niet wijzigingen
        # vanwege de delete
        reversedFilenames = tuple(reversed(selectedFilenames))
        for i in reversedFilenames :
            listbox.delete(i)
        changesSaved = False
    return None

# Sluit de applicatie af
def exitApp():
    global changesSaved
    if changesSaved:
        window.quit()
    else:
        if messagebox.askokcancel("Pas op!", "Er zijn nog niet opgeslagen wijzigingen. Toch afsluiten?"):
            window.quit()
    return None

# Top level window
window = Tk()

window.title("Playlist")
window.geometry('800x320')
# Zorg dat bij klik op het kruisje de standaard afsluiting wordt geforceerd
window.protocol("WM_DELETE_WINDOW", exitApp)
# De applicatie moet op de deleteknop kunnen reageren
window.bind('<Delete>', removeFilename)

# create a menu
menu = Menu(window)
window.config(menu=menu)

filemenu = Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=lambda: clearPlaylist())
filemenu.add_command(label="Open...", command=lambda: openPlaylist())
filemenu.add_command(label="Save...", command=lambda: savePlaylist())
filemenu.add_separator()
filemenu.add_command(label="Exit", command=exitApp)

helpmenu = Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About...", command=showHelp)
# een frame toevoegen om de listbox in te plaatsen
frame = Frame(window)
ybar = Scrollbar(frame, orient=VERTICAL)
xbar = Scrollbar(frame, orient=HORIZONTAL)
frame.pack(side = LEFT)

# Create listbox
lboptions = {}
lboptions['height'] = 20
lboptions['width'] = 80
lboptions['yscrollcommand'] = ybar.set
lboptions['xscrollcommand'] = xbar.set
lboptions['exportselection'] = 0
lboptions['selectmode'] = MULTIPLE
listbox = Listbox(frame, **lboptions)
ybar.config(command=listbox.yview)
ybar.pack(side=RIGHT, fill=Y)
xbar.config(command=listbox.xview)
xbar.pack(side=BOTTOM, fill=X)
listbox.pack()
# voeg een frame toe om de buttons in te plaatsen
knoppen = Frame(window)
knoppen.pack(side = LEFT)
Label(knoppen, text="Hiermee kunt je \nmuziek toevoegen").pack(side = TOP)
Button(knoppen, text="Add folder", command=lambda: selectMusicFolder()).pack(side = TOP)
recursiveFolder = IntVar()
Checkbutton(knoppen, text="recursive", variable=recursiveFolder, onvalue=1, offvalue=0).pack(side = TOP)
Separator(knoppen, orient=HORIZONTAL).pack(fill= X, side = TOP)
Button(knoppen, text="Add file", command=lambda: selectMusicFile()).pack(side = TOP)
Separator(knoppen, orient=HORIZONTAL).pack(fill= X, side = TOP)
Button(knoppen, text="Add playlist", command=lambda: selectPlaylist()).pack(side = TOP)
Separator(knoppen, orient=HORIZONTAL).pack(fill= X, side = TOP)
Label(knoppen, text= "Hiermee kun je \nmuziek verplaatsen").pack(side = TOP)
Button(knoppen, text="Top", command=lambda: moveTop()).pack(side = TOP)
Button(knoppen, text="Up", command=lambda: moveUp()).pack(side = TOP)
Button(knoppen, text="Down", command=lambda: moveDown()).pack(side = TOP)
Button(knoppen, text="Bottom", command=lambda: moveBottom()).pack(side = TOP)

# Start de loop
window.mainloop()
