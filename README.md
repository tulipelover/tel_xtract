# tel_xtract

## Description
Tel_xtract est un programme à base de Python ayant pour vocation l'extraction de supports mobiles tournant sous Android 
de manière forensique. Ce logiciel cible plus particulièrement les membres de la communauté des forces l'ordre 
spécialement formés aux investigations numériques et à l'analyse criminalistique de supports informatiques cependant 
il n'en reste pas moins open source.  
Ce logiciel n’a pas pour but de concurrencer les solutions payantes de grosses entreprises. Il permet à l'enquêteur 
d'extraire de manière forensique les données élémentaires d'un téléphone et ce avec le moins d'effort possible de la 
part de l'utilisateur.  
Le résultat de l'exploitation est un dossier contenant des fichiers au format CSV facilement exploitables par d'autres 
outils et un rapport au format HTML.  
A l'heure actuelle, le logiciel arrive, dans le plupart des cas, à extraire, les contacts, les journaux d'appels, les 
applications, les SMS, les MMS et les images contenues dans les dossiers "DCIM" et "Pictures". Avec le temps, ce 
programme tentera d'extraire de plus en plus de données.

## Installation
Aucune installation n’est nécessaire. L'application est totalement portable sous Windows pour le moment.

## Utilisation
### A faire avant d'utiliser le programme :
Il est indispensable d’activer le mode ADB (« Android Debug Bridge »). Pour ce faire n’hésitez pas à vous reporter aux 
informations du constructeur. (en effet selon les versions d’Android et les modèles d’appareils, les manipulations sont 
différentes).

### Le programme
Pour démarrer le programme, il suffit d’exécuter le fichier **_tel_xtract.bat_**. Cette action fera apparaître 
une interface graphique vous demandant de renseigner des informations en lien avec le dossier en cours. Il s'agira
ensuite de choisir si l'extraction des images contenues dans le DCIM et dans le dossier Pictures est souhaitée (tous les renseignements concernant le
dossier sont optionnels). Cliquer ensuite sur "Valider" pour lancer l'extraction.  
Une fois l'extraction lancée, le déroulé des différentes étapes s'affiche en haut à gauche de l'écran dans un bandeau
noir. Cette information vous permet de vous situer par rapport à l'avancée de l'extraction. Il suffit ensuite de se 
laisser guider par le programme.  
A la fin du programme, un popup "Terminé!" s'affichera sur l'écran afin de vous signaler la fin de l'extraction

### Exploitation des résultats
Le programme peut créer trois types de résultats stockés dans le dossier "Résultats" à la source du programme: 
un dossier nommé "Fichiers CSV", un dossier nommé 'Rapport HTML' et un fichier "tel_xtract.log".

#### tel_xtract.log
Ce fichier contient le log de l'extraction avec la date et l'heure de chaque opération. Il indiquera également toutes 
les erreurs survenues lors de l'extraction.

#### Fichiers CSV
Si l'extraction est entièrement réussie, vous trouverez dans ce dossier les éléments suivants:
* **Resources/**: Dossier contenant tous les éléments MMS extraits du téléphone.
* **CallLog Calls.csv**:  Contient toutes les données des journaux d'appels.  
* **Contacts Phones.csv**: Contient toutes les données des contacts stockés physiquement sur le téléphone.  
* **info.xml**: Contient toutes les données liées au caractéristiques du téléphone et aux applications installées.  
* **Informations.txt**: Contient toutes les données de traçabilité liées à l'exploitation.  
* **MMS.csv**: Contient toutes les métadonnées liées aux MMS.  
* **MMSParts.csv**: Contient toutes les données liées au contenu des MMS.  
* **Numéros_comm.csv**: Contient tous les numéros de téléphone avec lesquels le téléphone a communiqué.  
* **SMS.csv**: Contient toutes les données liées aux SMS.  

#### Rapport HTML
Si l'extraction est entièrement réussie, vous trouverez dans ce dossier les éléments suivants:
* **Internal**: Dossier contenant tous les fichiers nécessaires à l'affichage des icônes du rapport HTML.
* **Resources**: Dossier contenant tous les éléments MMS extraits du téléphone.
* **Applications.html**: Fichier HTML contenant la liste des applications extraites du téléphone.
* **Contacts.html**: Fichier HTML contenant la liste des contacts.
* **Index.html**: Fichier HTML contenant l'index du rapport. En toute logique, ce fichier est le point de départ du 
rapport.
* **Infos Tel.html**: Fichier HTML contenant les informations propres au téléphone.
* **Journaux d'Appels.html**: Fichier HTML contenant les journaux d'appels du téléphone.
* **MMS.html**: Fichier HTML contenant la liste des MMS extraits ainsi que leur pièce(s) jointes(s).
* **SMS.html**: Fichier HTML contenant la liste des MMS extraits.
* **Images.html**: Fichier HTML contenant la liste de toutes les images extraites. Cette page ne sera présente que si 
l'option "Extraire les images" est cochée sur l'interface graphique.

## Contribution
Nous ne demandons pas d'argent pour l'avancement de l'application. Cependant, ceux qui souhaitent contribuer au bon 
développement du programme peuvent nous envoyer le dossier "_forensics_" de l'extraction contenu dans le dossier 
source de l'application suite à une exploitation.  
**ATTENTION**: Le dossier "_forensics_" contient toutes les données brutes extraites du téléphone. En contribuant de 
cette manière vous nous remettez toutes les informations sur votre téléphone. Nous précisons que ces données ont pour 
seul but l'avancement du développement de l'application et que le contenu sémantique nous importe peu. Cependant, 
l'avertissement s'impose.

## Licence
Ce logiciel est fourni sous licence GNU GPL3. Pour plus d'information concernant cette licence, voir le fichier 
"_LICENSE_" du répertoire source de l'application.

## FAQ
**Q**: Le programme ne démarre pas, que faire?  
**R**: L'application ne nécessite aucun module ou programme externe pour fonctionner. Toutes les composantes nécessaires
sont fournies dans le zip. Il peut cependant arriver que les antivirus n'apprécient pas l'ADB. Dans ce cas,
il faudra soit ajouter une exception à votre antivirus, soit le désactiver le temps de l'extraction.  

**Q**: L'extraction s'est bien déroulée, j'ai tous mes fichiers dans les dossier "Résultats", "Fichiers CSV" et
Rapport HTML. Pourquoi est-ce que certaines catégories du rapport sont vides?  
**R**: A l'heure actuelle, la copie des données depuis les bases de données de la partition "Data" du téléphone se fait
via l'APK open source "_AFLogical_". Ce dernier tente, dans la mesure de sa programmation, d'extraire les données 
contenues dans les bases de données. Sur certains téléphones récents, les bases de données peuvent être légérement 
modifiées ce qui peut créer des erreurs lors de l'extraction. Tel_xtract exploite toutes les données sorties par 
AFLogical. Dans le cas où les données extraites sont inexploitables ou absentes, le programme est conçu pour ignorer 
ces erreurs et exploiter tout ce qui est exploitable. Les données détaillées de l'extraction se trouve dans le fichier 
_tel_xtract.log_ dans le dossier "Résultats". La moindre erreur rencontrée par le logiciel sera loggée dans ce fichier.

**Q**: Je rencontre un problème avec le logiciel qui ne figure pas dans cette section. Comment puis-je vous le signaler?  
**R**: C'est simple! Il suffit de nous le signaler dans la section "Issues" sur GitHub. Tous les problèmes signalés
dans cette section seront traités dès que possible. Pareillement, toutes les suggestions sont bienvenues. Il suffit de
nous les signaler dans la catégorie "Issues". Notre but est de parfaire le programme afin qu'il puisse être utile au
plus grand nombre.

## Téléphones Testés et Problèmes Connus
### Problèmes connus
Support pour Android 9 ajouté. Les téléphones déjà testés sous Android 9 et qui causaient problème vont être retestés.  
Cette liste sera mise à jour au fur et à mesure des retours "terrains" et des tests effectués. Pour le moment, les tests
montrent que sur certains téléphones sous Android 9, le contacts ne sont pas extraits. Des tests sont en cours pour y 
remédier.

### Téléphones testés
#### Samsung
* S8 (Android 8): Extraction complète réussie
* S9 (Android 9)
  * SMS et MMS, applications, journaux d'appels et infos du téléphone: Réussite
  * Contacts: Echec
* S9+ (Android 9)
  * SMS et MMS, applications, journaux d'appels et infos du téléphone: Réussite
  * Contacts: Echec
  
#### Huawei
* Huawei Mate 9 (Android 8): Extraction complète réussite
* Huawei Mate 9 (Android 9): Extraction complète réussite

#### Autres
* Umidigi S2 Lite (Android 7): Extraction complète réussite  
