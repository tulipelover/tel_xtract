# tel_xtract

## Description
Tel_xtract est un programme à base de Python ayant pour vocation l'extraction de supports mobiles tournant sous Android de manière 
forensique. Ce logiciel cible plus particulièrement les membres de la communauté des forces l'ordre spécialement formés
aux investigations numériques et à l'analyse criminalistique de supports informatiques cependant il n'en reste pas 
moins open source.  
Ce logiciel n’a pas pour but de concurrencer les solutions payantes de grosses entreprises. Il permet à l'enquêteur 
d'extraire de manière forensique les données élémentaires d'un téléphone et ce avec le moins d'effort possible de la 
part de l'utilisateur.  
Le résultat de l'exploitation est un dossier contenant des fichiers au format CSV facilement exploitables par d'autres 
outils et un rapport au format HTML. Ce dernier reprend toutes les données contenues dans ces fichiers CSV.

## Utilisation
### A faire avant d'utiliser le programme :
Il et indispensable d’activer le mode ADB (« Android Debug Bridge »). Pour ce faire n’hésitez pas à vous reporter aux 
informations du constructeur. (en effet selon les versions d’Android et les modèles d’appareils, les manipulations sont 
différentes).

### Le programme
Pour démarrer le programme, il suffit d’exécuter le fichier **_tel_xtract.bat_**. Cette action fera apparaître 
une interface graphique vous demandant de renseigner des informations en lien avec le dossier en cours. Il s'agira
ensuite de choisir si la création d'un rapport au format HTML est souhaitée (tous les renseignements concernant le
dossier sont optionnels. Cependant, si la case "rapport" est cochée, il faudra obligatoirement remplir à minima la 
marque et le modèle du téléphone exploité). Cliquer ensuite sur "Valider" pour lancer l'extraction.  
Une fois l'extraction lancée, le déroulé des différentes étapes s'affiche en haut à gauche de l'écran dans un bandeau
noir. Cette information vous permet de vous situer par rapport à l'avancée de l'extraction. Il suffit ensuite de se 
laisser guider par le programme.  
A la fin du programme, un popup "Terminé!" s'affichera sur l'écran afin de vous signaler la fin de l'extraction

### Exploitation des résultats
Coming Soon

## Installation
Aucune installation n’est nécessaire. Le paquet est totalement portable sous Windows pour le moment.

## FAQ
**Q**: Le programme ne démarre pas, que faire?  
**R**: L'application ne nécessite aucun module ou pragramme externe pour fonctionner. Toutes les composantes nécessaires
sont fournies dans le zip. Il peut cependant arriver que les antivirus n'apprécient pas forcément l'ADB. Dans ce cas,
il faudra soit ajouter une exception à votre antivirus, soit le désactiver le temps de l'extraction.  

**Q**: L'extraction s'est bien déroulée, j'ai tous mes fichiers dans les dossier "Résultats", "Fichiers CSV" et
Rapport HTML. Pourquoi est-ce que certaines catégories du rapport sont vides?  
**R**: A l'heure actuelle, la copie des données depuis les bases de données de la partition "Data" du téléphone se fait
via l'APK open source AFLogical. Ce dernier tente, dans la mesure de sa programmation, d'extraire les données contenues
dans les bases de données. Sur certains téléphones récents, les bases de données peuvent être légérement modifiées ce qui
peut créer des erreurs lors de l'extraction. Tel_xtract exploite toutes les données sorties par AFLogical. Dans le cas 
où les données extraites sont inexploitables ou absentes, le programme est conçu pour ignorer ces erreurs et exploiter
tout ce qui est exploitable. Les données détaillées de l'extraction se trouve dans le fichier _tel_xtract.log_ dans le
dossier "Résultats". La moindre erreur rencontrée par le logiciel sera visible dans ce fichier.

**Q**: Je rencontre un problème avec le logiciel qui ne figure pas dans cette section. Comment puis-je vous le signaler?  
**R**: C'est simple! Il suffit de nous le signaler dans la section "Issues" sur GitHub. Tous les problèmes signalés
dans cette section seront traités dès que possible. Pareillement, toutes les suggestions sont bienvenues. Il suffit de
nous les signaler dans la catégorie "Issues". Notre but est de parfaire le programme afin qu'il puisse être utile au
plus grand nombre.

## Téléphones Testés
Cette liste sera mise à jour au fur et à mesure des retours "terrains" et des tests effectués.

### Samsung
* Samsung S9
  * SMS et MMS: Réussite
  * Tout le reste: Echec
  
### Huawei
* Huawei Mate 9: Extraction complète réussie

### Autres
* Umidigi S2 Lite: Extraction complète réussie  
