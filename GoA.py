import sys
import os
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QFile, QTextStream


class Browser(QMainWindow):
    def __init__(self):
        super(Browser, self).__init__()
        self.setWindowIcon(QIcon("Icon/Logo.png"))

        self.toolbar_area = Qt.TopToolBarArea  # Position de la barre d'outils

        # Créer un QTabWidget pour gérer les onglets
        self.onglets = QTabWidget()
        self.onglets.setTabsClosable(True)  # Permet de fermer les onglets
        self.onglets.tabCloseRequested.connect(self.fermer_onglet)
        self.onglets.currentChanged.connect(self.changer_onglet)
        self.setCentralWidget(self.onglets)
        self.showMaximized()

        # Barre de navigation
        self.navbar = self.addToolBar("Navigation")
        self.addToolBar(self.toolbar_area, self.navbar)  # Ajouter la barre d'outils à la fenêtre

        accueil_btn = QAction(QIcon("Icon/accueil.png"), "Accueil", self)
        accueil_btn.triggered.connect(self.url_accueil)
        self.navbar.addAction(accueil_btn)

        retour_btn = QAction(QIcon("Icon/retour.png"), "Retour", self)
        retour_btn.triggered.connect(self.retour_arriere)
        self.navbar.addAction(retour_btn)

        actualiser_btn = QAction(QIcon("Icon/actualiser.png"), "Actualiser", self)
        actualiser_btn.triggered.connect(self.actualiser_page)
        self.navbar.addAction(actualiser_btn)

        avancer_btn = QAction(QIcon("Icon/avancer.png"), "Avancer", self)
        avancer_btn.triggered.connect(self.avancer_page)
        self.navbar.addAction(avancer_btn)

        self.navigateur = None
        self.historique = []  # Historique des URL de l'onglet actif
        self.historique_global = []  # Historique global de toutes les URL visitées

        self.favoris = []  # Liste pour stocker les favoris

        # Barre d'URL
        self.url_bar = QLineEdit(self)
        self.url_bar.setObjectName("url_bar")  # Ajouter un ID ou une classe
        self.url_bar.returnPressed.connect(self.navigation)
        self.navbar.addWidget(self.url_bar)

        #Bonton favoris
        favoris_btn = QAction(QIcon("Icon/favoris.png"), "Ajouter aux favoris", self)
        favoris_btn.triggered.connect(self.ajouter_aux_favoris)
        self.navbar.addAction(favoris_btn)

        # Barre de recherche
        self.search_bar = QLineEdit(self)
        self.search_bar.setObjectName("bar_recherche")  # Ajouter un ID ou une classe
        self.search_bar.setFixedWidth(200)  # Modifier la longueur de la barre de recherche
        self.search_bar.returnPressed.connect(self.effectuer_recherche)
        self.navbar.addWidget(self.search_bar)

        # Bouton Nouvel onglet
        nouveau_onglet_btn = QAction(QIcon("Icon/plus.png"), "Nouvel onglet", self)
        nouveau_onglet_btn.triggered.connect(self.nouvel_onglet)
        self.navbar.addAction(nouveau_onglet_btn)

        # Menu déroulant parametres
        menu_parametres = QMenu(self)
        parametres_menu_btn = QAction(QIcon("Icon/parametres.png"), "Bidule", self)
        parametres_menu_btn.setMenu(menu_parametres)
        self.navbar.addAction(parametres_menu_btn)

        # Action Historique
        historique_action = QAction(QIcon("Icon/historique.png"), "Historique", self)
        historique_action.triggered.connect(self.afficher_historique_fenetre)
        menu_parametres.addAction(historique_action)

        # Action Favoris
        favoris_action = QAction(QIcon("Icon/favoris.png"), "Favoris", self)
        favoris_action.triggered.connect(self.afficher_favoris_fenetre)
        menu_parametres.addAction(favoris_action)

        # Chemin du fichier d'historique
        self.chemin_fichier = "historique.txt"

        # Charger l'historique à partir du fichier
        self.charger_historique()

        # Charger les favoris à partir du fichier
        self.charger_favoris()

        # Charger les styles CSS
        self.charger_css()

        # Créer le premier onglet
        self.creer_onglet("https://google.com", "Nouvel onglet")  

        self.fenetre_historique = None     

    def charger_css(self):
        with open("styles.css", "r") as fichier_css:
            style = fichier_css.read()
            self.setStyleSheet(style)

    def creer_onglet(self, url, titre):
        navigateur = QWebEngineView()
        navigateur.setUrl(QUrl(url))
        navigateur.urlChanged.connect(self.maj_url_bar)  # Connecter le signal urlChanged
        layout = QVBoxLayout()
        layout.addWidget(navigateur)
        widget = QWidget()
        widget.setLayout(layout)
        self.onglets.addTab(widget, titre)
        self.url_bar.setText(url)  # Définir l'URL dans la barre d'URL du nouvel onglet
        self.navigateur = navigateur
        self.historique.append(url)  # Ajouter l'URL à l'historique de l'onglet actif
        self.historique_global.append(url)  # Ajouter l'URL à l'historique global

    def effectuer_recherche(self):
        query = self.search_bar.text()
        if self.navigateur:
            url = "https://www.google.com/search?q=" + query  # Exemple avec une recherche Google
            self.navigateur.setUrl(QUrl(url))

    def fermer_onglet(self, index):
        if self.onglets.count() > 1:
            self.onglets.removeTab(index)
            del self.historique[index]  # Supprimer l'historique de l'onglet fermé

    def changer_onglet(self, index):
        widget = self.onglets.widget(index)
        navigateur = widget.findChild(QWebEngineView)
        if navigateur:
            self.url_bar.setText(navigateur.url().toString())
            self.navigateur = navigateur

    def url_accueil(self):
        if self.navigateur:
            self.navigateur.setUrl(QUrl("https://google.com"))

    def navigation(self):
        url = self.url_bar.text()
        self.creer_onglet(url, "Nouvel onglet")

    def actualiser_page(self):
        if self.navigateur:
            self.navigateur.reload()

    def retour_arriere(self):
        if self.navigateur:
            self.navigateur.back()

    def avancer_page(self):
        if self.navigateur:
            self.navigateur.forward()

    def maj_url_bar(self):
        index_actuel = self.onglets.currentIndex()
        widget = self.onglets.widget(index_actuel)
        navigateur = widget.findChild(QWebEngineView)
        if navigateur:
            url = navigateur.url().toString()
            self.url_bar.setText(url)
            self.historique[index_actuel] = url
            self.historique_global.append(url)  # Ajouter l'URL à l'historique global
            self.navigateur = navigateur

    def formater_lien(self, lien, max_caracteres):
        if len(lien) <= max_caracteres:
            return lien
        else:
            return lien[:max_caracteres] + "..."


    def afficher_historique_fenetre(self):
        if self.fenetre_historique is not None and self.fenetre_historique.isVisible():
            # La fenêtre d'historique est déjà ouverte, la ramener au premier plan
            self.fenetre_historique.activateWindow()
        else:
            chemin_logo = "Icon/Historique.png"
            max_caracteres = 50

            if self.fenetre_historique is None:
                # Créer la fenêtre d'historique si elle n'existe pas encore
                self.fenetre_historique = QMainWindow()
                self.fenetre_historique.setWindowTitle("Historique")

                # Créer le widget QListWidget
                liste_widget = QListWidget()

                # Ajouter chaque élément de l'historique à la liste
                for url in self.historique_global:
                    item = QListWidgetItem(url)
                    item.setToolTip(url)  # Afficher l'URL complète en tant que tooltip
                    liste_widget.addItem(item)

                # Ajouter le widget à la fenêtre
                self.fenetre_historique.setCentralWidget(liste_widget)

                # Créer la barre d'outils
                toolbar = QToolBar()
                toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)

                # Ajouter l'action pour purger l'historique
                action_purger = QAction("Purger l'historique", self)
                action_purger.triggered.connect(self.purger_historique)
                toolbar.addAction(action_purger)

                # Ajouter la barre d'outils à la fenêtre
                self.fenetre_historique.addToolBar(toolbar)

            # Changer le logo de la fenêtre
            self.fenetre_historique.setWindowIcon(QIcon(chemin_logo))

        # Réinitialiser le contenu de la liste à chaque fois que la fenêtre est affichée
        liste_widget = self.fenetre_historique.centralWidget()
        liste_widget.clear()
        for url in self.historique_global:
            item = QListWidgetItem(url)
            item.setToolTip(url)
            liste_widget.addItem(item)

        # Afficher la fenêtre
        self.fenetre_historique.show()

    def purger_historique(self):
        self.historique_global = []
        print("Historique purgé.")

         # Rafraîchir la fenêtre de l'historique
        self.afficher_historique_fenetre()

    def navigation_historique(self, url):
        index_actuel = self.onglets.currentIndex()
        self.historique[index_actuel] = url
        self.url_bar.setText(url)
        if self.navigateur:
            self.navigateur.setUrl(QUrl(url))

    def nouvel_onglet(self):
        self.creer_onglet("https://google.com", "Nouvel onglet")

    def sauvegarder_historique(self):
        with open(self.chemin_fichier, "w") as fichier:
            for url in self.historique_global:
                fichier.write(url + "\n")

    def charger_historique(self):
        if os.path.exists(self.chemin_fichier):
            with open(self.chemin_fichier, "r") as fichier:
                lignes = fichier.readlines()
                self.historique_global = [ligne.strip() for ligne in lignes]

    def closeEvent(self, event):
        self.sauvegarder_historique()
        event.accept()

    def ajouter_aux_favoris(self):
        if self.navigateur:
            url = self.navigateur.url().toString()
            nom_favori, valide = QInputDialog.getText(self, "Ajouter aux favoris", "Nom du favori :")
            if valide and nom_favori:
                favori = {"nom": nom_favori, "url": url}
                self.favoris.append(favori)
                self.sauvegarder_favoris()

    def navigation_favori(self):
        action = self.sender()  # Obtenir l'action qui a déclenché l'événement
        url = action.data()  # Obtenir l'URL associée à l'action
        self.creer_onglet(url, "Nouvel onglet")

    def afficher_favoris_fenetre(self):
        favoris_texte = "\n".join([favori["nom"] + ": " + favori["url"] for favori in self.favoris])
        chemin_logo = "Icon/favoris.png"
        self.afficher_fenetre("Favoris", favoris_texte, chemin_logo)

    def sauvegarder_favoris(self):
        with open("favoris.txt", "w") as fichier:
            for favori in self.favoris:
                ligne = f"{favori['nom']},{favori['url']}\n"
                fichier.write(ligne)

    def charger_favoris(self):
        if os.path.exists("favoris.txt"):
            with open("favoris.txt", "r") as fichier:
                lignes = fichier.readlines()
                for ligne in lignes:
                    nom, url = ligne.strip().split(",")
                    favori = {"nom": nom, "url": url}
                    self.favoris.append(favori)

    def closeEvent(self, event):
        self.sauvegarder_favoris()
        event.accept()

    def afficher_fenetre(self, titre, contenu, chemin_logo):
        fenetre = QDialog(self)
        fenetre.setWindowTitle(titre)
        fenetre.setWindowIcon(QIcon(chemin_logo))

        # Modifier la taille de la fenêtre
        fenetre.resize(400, 300)  # Remplacez les valeurs par la taille souhaitée

        layout = QVBoxLayout()
        texte = QLabel(contenu)
        layout.addWidget(texte)
        fenetre.setLayout(layout)

        fenetre.exec_()

app = QApplication(sys.argv)
QApplication.setApplicationName("GoA")
fenetre = Browser()
fenetre.charger_css()  # Appel de la méthode pour charger les styles CSS
fenetre.show()
app.exec_()
