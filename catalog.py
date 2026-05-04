"""Catalogue statique : produits, clients, canaux, templates.

Ce module est la source de vérité du tunnel commercial. Tout est typé strictement
afin que l'UI puisse boucler dessus sans surprise.

DECISION: Les templates contiennent des placeholders au format {snake_case}.
À l'affichage, ils sont rendus en `[Format Lisible]` via template_engine.humanize().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ChannelTemplate:
    """Un template prêt à l'emploi pour un (produit, client, canal[, contexte])."""

    channel: str  # ex: "email", "linkedin", "instagram_dm", "whatsapp", "facebook_messenger", "twitter_dm"
    subject: str  # vide pour les canaux sans objet
    body: str
    context: str = ""  # vide = template neutre/fallback


@dataclass(frozen=True)
class ProductContext:
    """Une situation/cas spécifique à un produit (ex: 'a déjà un site' / 'pas de site')."""

    key: str
    label: str
    description: str = ""


@dataclass(frozen=True)
class ClientTarget:
    """Un type de client cible pour un produit."""

    key: str
    label: str
    priority: int  # 1 = max, 5 = bas
    description: str
    templates: Tuple[ChannelTemplate, ...]


@dataclass(frozen=True)
class Product:
    """Un produit de l'écosystème Triskell."""

    key: str
    label: str
    tagline: str
    audience: str  # "B2B" | "B2C" | "Mixte"
    clients: Tuple[ClientTarget, ...]
    contexts: Tuple[ProductContext, ...] = ()         # situations possibles
    context_templates: Tuple[ChannelTemplate, ...] = ()  # variantes par contexte (toutes cibles confondues)


# ---------------------------------------------------------------------------
# Méta canaux
# ---------------------------------------------------------------------------

CHANNEL_LABELS: Dict[str, str] = {
    "email": "Email",
    "linkedin": "LinkedIn",
    "instagram_dm": "Instagram DM",
    "whatsapp": "WhatsApp",
    "facebook_messenger": "Facebook Messenger",
    "twitter_dm": "Twitter / X DM",
}

CHANNEL_ICONS: Dict[str, str] = {
    "email": "✉",
    "linkedin": "in",
    "instagram_dm": "◉",
    "whatsapp": "💬",
    "facebook_messenger": "f",
    "twitter_dm": "𝕏",
}


# ---------------------------------------------------------------------------
# Templates — Triskell Studio (sites web)
# ---------------------------------------------------------------------------

_T_TRISKELL_TPE_PME: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="Un site qui ressemble enfin à {nom_entreprise} ?",
        body=(
            "Bonjour {prenom},\n\n"
            "Je suis {mon_prenom} de Triskell Studio, agence digitale basée en Bretagne. "
            "En jetant un œil au site de {nom_entreprise}, j'ai remarqué quelques pistes "
            "simples qui pourraient vous faire gagner en crédibilité et en clients "
            "(chargement, mobile, mise à jour des contenus).\n\n"
            "On accompagne plusieurs entreprises {region_secteur} avec des sites premium "
            "taillés sur mesure — pas de templates copiés-collés, juste du design qui vous ressemble.\n\n"
            "Ça vous dit qu'on en discute 15 minutes cette semaine ? Je peux vous montrer "
            "2-3 pistes concrètes pour {nom_entreprise}.\n\n"
            "Bien cordialement,\n"
            "{mon_prenom} — Triskell Studio\n"
            "{lien_site} · {telephone}"
        ),
    ),
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, ravi de découvrir {nom_entreprise} dans mon réseau breton. "
            "On accompagne pas mal de dirigeants par ici sur la refonte de leur site "
            "(design premium, vraiment sur mesure). Si jamais le sujet vous trotte dans "
            "la tête, je serais content d'échanger 15 min — sans engagement. Belle journée à vous."
        ),
    ),
    ChannelTemplate(
        channel="whatsapp",
        subject="",
        body=(
            "Bonjour {prenom}, c'est {mon_prenom} de Triskell Studio (agence web bretonne). "
            "On a aidé plusieurs entreprises locales à transformer leur site en vraie machine à clients. "
            "Ça vous intéresse qu'on regarde ensemble votre site actuel ? 15 min suffisent. "
            "Je vous offre l'audit."
        ),
    ),
)

_T_TRISKELL_RESTAU: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="instagram_dm",
        subject="",
        body=(
            "Hello {prenom} 👋\n"
            "J'ai craqué sur l'univers de {nom_entreprise} sur votre feed — franchement, "
            "votre identité mérite un site à la hauteur. Je suis {mon_prenom}, on fait des "
            "sites premium pour la restau / hôtellerie chez Triskell Studio. Si ça vous parle, "
            "je vous envoie 2-3 idées concrètes pour {nom_entreprise}, sans aucun engagement."
        ),
    ),
    ChannelTemplate(
        channel="email",
        subject="L'univers de {nom_entreprise} mérite un site qui en jette",
        body=(
            "Bonjour {prenom},\n\n"
            "J'ai découvert {nom_entreprise} récemment et votre identité visuelle est top. "
            "Le souci : votre site ne reflète pas (encore) ce niveau-là.\n\n"
            "Chez Triskell Studio, on conçoit des sites premium pour les restaurants, cafés "
            "et hôtels indépendants. Réservation intégrée, menu dynamique, photos qui claquent, "
            "SEO local — tout ce qui transforme un visiteur en client.\n\n"
            "15 minutes pour un mini-audit gratuit de {lien_site} ?\n\n"
            "Cordialement,\n{mon_prenom} — Triskell Studio"
        ),
    ),
    ChannelTemplate(
        channel="whatsapp",
        subject="",
        body=(
            "Bonjour {prenom}, {mon_prenom} de Triskell Studio. J'adore l'ambiance "
            "de {nom_entreprise}. On fait des sites premium pour la restau (réservation, "
            "menu, photos). Je vous offre un mini-audit du site actuel si vous voulez ?"
        ),
    ),
)

_T_TRISKELL_ARTISANS: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="whatsapp",
        subject="",
        body=(
            "Bonjour {prenom}, c'est {mon_prenom} de Triskell Studio (agence web bretonne). "
            "On a aidé plusieurs artisans à faire passer leur site de \"carte de visite oubliée\" "
            "à vraie machine à clients. Ça vous intéresse qu'on regarde ensemble votre site actuel ? "
            "15 min suffisent. Je vous offre l'audit."
        ),
    ),
    ChannelTemplate(
        channel="facebook_messenger",
        subject="",
        body=(
            "Bonjour {prenom}, j'ai vu votre activité {metier} — beau travail. "
            "On fait des sites web premium pour les artisans, avec un focus sur la conversion "
            "(devis, prise de RDV, avis clients). Si vous voulez qu'on regarde ensemble votre site "
            "actuel, je vous offre 20 min de mini-audit. — {mon_prenom}, Triskell Studio."
        ),
    ),
    ChannelTemplate(
        channel="email",
        subject="Votre site {metier} pourrait vous ramener 3-5 devis de plus / mois",
        body=(
            "Bonjour {prenom},\n\n"
            "Votre site actuel — soyons honnêtes — est-il aujourd'hui un vrai canal de devis "
            "pour {nom_entreprise}, ou plutôt une carte de visite oubliée ?\n\n"
            "Chez Triskell Studio, on conçoit des sites taillés pour les artisans : "
            "moteur de demande de devis, photos avant/après, avis clients, SEO local. "
            "Le tout pensé pour faire entrer 3 à 5 devis qualifiés en plus chaque mois.\n\n"
            "Je vous offre un mini-audit de 15 min de {lien_site}. Vous me direz.\n\n"
            "Cordialement,\n{mon_prenom} — Triskell Studio"
        ),
    ),
)

_T_TRISKELL_COACHS: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="Votre site reflète-t-il vraiment la valeur que vous délivrez ?",
        body=(
            "Bonjour {prenom},\n\n"
            "J'ai lu {article_post_recent} — vraiment intéressant. Une question franche : "
            "est-ce que votre site web est aujourd'hui à la hauteur de ce que vous délivrez "
            "à vos clients ?\n\n"
            "Chez Triskell Studio, on conçoit des sites premium pour des coachs et consultants "
            "qui veulent que leur image en ligne reflète leur niveau réel. Design soigné, "
            "message clair, conversion optimisée.\n\n"
            "Si vous avez 15 minutes cette semaine, je vous offre un mini-audit gratuit de {lien_site}.\n\n"
            "Cordialement,\n{mon_prenom} — Triskell Studio"
        ),
    ),
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, votre contenu sur {sujet_expertise} m'a accroché. "
            "Question franche : votre site reflète-t-il aujourd'hui le niveau de valeur que "
            "vous délivrez à vos clients ? Chez Triskell Studio on bosse beaucoup avec des coachs "
            "et consultants premium. 15 min pour un mini-audit gratuit, ça vous dit ?"
        ),
    ),
    ChannelTemplate(
        channel="instagram_dm",
        subject="",
        body=(
            "Hello {prenom} 👋 vu votre contenu sur {sujet_expertise} — c'est carré. "
            "Petite question : votre site web est à la hauteur de votre niveau ? "
            "On fait du sur-mesure pour coachs / consultants chez Triskell. "
            "Mini-audit gratuit si vous voulez."
        ),
    ),
)

_T_TRISKELL_ECOM: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="facebook_messenger",
        subject="",
        body=(
            "Salut {prenom} ! Je suis {mon_prenom} de Triskell Studio. Je suis tombé sur "
            "{nom_entreprise} et je trouve que votre offre a un vrai potentiel. Le souci, "
            "c'est que le site freine un peu vos ventes (mobile, vitesse, parcours d'achat). "
            "On peut en parler ? Je vous donne 2-3 conseils gratuits, même si on bosse pas "
            "ensemble derrière."
        ),
    ),
    ChannelTemplate(
        channel="email",
        subject="3 frictions que j'ai notées sur {lien_site}",
        body=(
            "Bonjour {prenom},\n\n"
            "Je suis tombé sur {nom_entreprise} récemment — votre offre sur {produit_phare} "
            "est top. Mais j'ai aussi noté 3 frictions sur le site qui doivent vous coûter "
            "des ventes :\n\n"
            "1. {friction_1}\n"
            "2. {friction_2}\n"
            "3. {friction_3}\n\n"
            "On bosse chez Triskell Studio sur la refonte e-commerce orientée conversion. "
            "Si vous voulez qu'on en discute 20 min, je vous montre comment on traiterait "
            "ces 3 points concrètement.\n\n"
            "Cordialement,\n{mon_prenom} — Triskell Studio"
        ),
    ),
)

_T_TRISKELL_ASSOC: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, Triskell Studio accompagne des structures comme la vôtre dans "
            "la modernisation de leur présence web. On a une approche budget-friendly et orientée "
            "impact (accessibilité, SEO local, RGPD). Seriez-vous ouvert à un échange de 20 min "
            "pour explorer si on peut vous aider sur {projet_site} ?"
        ),
    ),
    ChannelTemplate(
        channel="email",
        subject="Moderniser le site de {nom_entreprise} — proposition d'échange",
        body=(
            "Bonjour {prenom},\n\n"
            "Triskell Studio est une agence digitale bretonne qui accompagne plusieurs "
            "associations et collectivités sur leur présence en ligne. Notre approche tient "
            "en trois mots : accessibilité, sobriété, impact local.\n\n"
            "Je vous propose un échange de 20 minutes pour comprendre vos enjeux sur {projet_site} "
            "et voir si nous pouvons vous être utiles. Sans engagement.\n\n"
            "Bien cordialement,\n{mon_prenom} — Triskell Studio\n{lien_site}"
        ),
    ),
)


# ---------------------------------------------------------------------------
# Templates — Eliks Studio (Growth Performance 100%)
# ---------------------------------------------------------------------------

_T_ELIKS_ECOM: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="On parle ROAS, pas factures fixes ?",
        body=(
            "Bonjour {prenom},\n\n"
            "Question directe : si on multipliait votre CA mensuel sur {nom_entreprise} "
            "*sans que vous payiez le moindre euro avant que les ventes tombent*, ça vous parlerait ?\n\n"
            "C'est exactement le modèle d'Eliks Studio : on devient votre Growth Partner, "
            "on prend en charge l'acquisition (ads, email, CRO), et on est rémunérés uniquement "
            "sur les ventes générées. Pas de retainer, pas de risque pour vous.\n\n"
            "On a actuellement 2 places ouvertes pour Q{trimestre}. Si vous êtes curieux, "
            "20 minutes avec moi suffisent à voir si c'est match.\n\n"
            "{mon_prenom} — Eliks Studio (groupe Triskell)\n{lien_site}"
        ),
    ),
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, Eliks Studio = on bosse sur votre acquisition, on est payés "
            "*uniquement* sur les ventes qu'on génère. Zéro risque côté {nom_entreprise}. "
            "On a 2 places ouvertes ce trimestre. Si le modèle vous intrigue, je vous explique "
            "tout en 20 min."
        ),
    ),
    ChannelTemplate(
        channel="whatsapp",
        subject="",
        body=(
            "Bonjour {prenom}, {mon_prenom} d'Eliks Studio. Modèle 100% perf : "
            "on s'occupe de votre acquisition, vous payez uniquement les ventes générées. "
            "2 places ouvertes ce trimestre. 20 min pour voir si c'est match ?"
        ),
    ),
)

_T_ELIKS_SAAS: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="Votre prochain euro de MRR, on le trouve ensemble ?",
        body=(
            "Bonjour {prenom},\n\n"
            "J'ai vu que {nom_entreprise} avait une vraie traction sur {segment}. "
            "La question maintenant : comment scaler l'acquisition sans flamber votre runway ?\n\n"
            "Eliks Studio propose un modèle simple : on bosse votre growth (ads, outbound, contenu), "
            "vous payez **uniquement** un % du MRR qu'on génère. Pas de cash brûlé en agence, "
            "pas de salaire de CMO à 7k€/mois.\n\n"
            "Si vous êtes ouvert à explorer ce modèle, on en parle 20 min cette semaine ?\n\n"
            "{mon_prenom} — Eliks Studio"
        ),
    ),
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, j'ai vu la traction de {nom_entreprise} — bravo. "
            "Nous chez Eliks Studio, on devient le pôle growth externalisé de SaaS comme le vôtre, "
            "payés uniquement à la perf (% du MRR généré). Zéro retainer. Si ça mérite 20 min "
            "de votre temps, je suis dispo cette semaine."
        ),
    ),
)

_T_ELIKS_DTC: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="twitter_dm",
        subject="",
        body=(
            "Hello {prenom} 👋 Vu votre dernier post sur {sujet_recent} — banger. "
            "Question rapide : vos campagnes paid sont gérées en interne ou via une agence retainer ? "
            "Chez Eliks on bosse 100% perf (rémunérés uniquement sur les ventes). Si jamais c'est "
            "intéressant pour {nom_entreprise}, on prend 15 min."
        ),
    ),
    ChannelTemplate(
        channel="email",
        subject="Votre paid media en 100 % perf ?",
        body=(
            "Bonjour {prenom},\n\n"
            "{nom_entreprise} a une marque forte. La question habituelle : est-ce que vos "
            "campagnes payantes performent autant que votre branding ?\n\n"
            "Eliks Studio prend en charge votre acquisition payante en 100 % perf. Pas de retainer, "
            "on touche un % uniquement sur les ventes effectivement générées.\n\n"
            "20 min cette semaine pour qu'on voie si c'est match ?\n\n"
            "{mon_prenom} — Eliks Studio"
        ),
    ),
)

_T_ELIKS_INFOPRO: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="whatsapp",
        subject="",
        body=(
            "Bonjour {prenom}, {mon_prenom} d'Eliks Studio. Vous vendez du {produit_programme} "
            "à {prix_moyen}€ — si on doublait vos ventes sans que vous avanciez d'euro à une agence, "
            "ça vous parlerait ? On bosse 100% à la perf. 20 min en visio cette semaine ?"
        ),
    ),
    ChannelTemplate(
        channel="instagram_dm",
        subject="",
        body=(
            "Hello {prenom} 👋 Vu que vous vendez du {produit_programme} — chez Eliks, on prend "
            "en charge l'acquisition de vos clients, payés *uniquement* sur les ventes qu'on génère. "
            "Zéro risque pour vous. 20 min pour voir si c'est match ?"
        ),
    ),
)

_T_ELIKS_AGENCES: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, remarqué que {agence} est forte sur {specialite} mais pas sur "
            "l'acquisition payante. On peut être votre pôle perf en marque blanche chez Eliks "
            "(100% à la perf, vos clients ne voient que vous). Discussion partenariat 20 min ?"
        ),
    ),
)


# ---------------------------------------------------------------------------
# Templates — SaaS Dénicheur de Créateurs
# ---------------------------------------------------------------------------

_T_DENICHEUR_AGENCES_UGC: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="Trouver 20 créateurs qualifiés en 5 minutes ?",
        body=(
            "Bonjour {prenom},\n\n"
            "Combien de temps vous passez chaque semaine à scroller Insta/TikTok pour dénicher "
            "des créateurs encore non monétisés ? 5h ? 10h ?\n\n"
            "On a construit un outil qui le fait à votre place : il identifie les créateurs avec "
            "engagement réel, audience cohérente, et **pas encore approchés par les marques**. "
            "Vous récupérez une short-list qualifiée en 5 minutes.\n\n"
            "Beta privée ouverte à 30 agences ce mois-ci. {nom_entreprise} aurait sa place. "
            "On en parle 15 min ?\n\n"
            "{mon_prenom} — Triskell Studio"
        ),
    ),
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, on a construit un outil qui identifie les créateurs encore "
            "*non monétisés* sur Insta/TikTok (engagement réel, vierges des marques). "
            "Beta privée à 30 agences ce mois-ci. 15 min pour vous montrer ?"
        ),
    ),
)

_T_DENICHEUR_DTC: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="instagram_dm",
        subject="",
        body=(
            "Hello {prenom} 👋 Question : vous avez des créateurs UGC à profusion ou vous galérez "
            "à trouver des pépites pas encore prises ? On a un outil qui sort une short-list de "
            "créateurs vierges en 5 min. Si ça vous intrigue, je vous offre une démo perso pour "
            "{nom_entreprise}."
        ),
    ),
    ChannelTemplate(
        channel="email",
        subject="Une short-list de créateurs UGC vierges en 5 min",
        body=(
            "Bonjour {prenom},\n\n"
            "Trouver des créateurs UGC qui ne soient pas déjà saturés de marques, c'est devenu "
            "un sport olympique. On a construit un SaaS qui filtre exactement ça : engagement "
            "réel, audience cohérente, **non monétisés**.\n\n"
            "Démo de 15 min cette semaine pour {nom_entreprise} ?\n\n"
            "{mon_prenom} — Triskell Studio"
        ),
    ),
)

_T_DENICHEUR_AFFIL: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="twitter_dm",
        subject="",
        body=(
            "Hello {prenom}, on a un SaaS qui détecte les créateurs micro-influence non monétisés — "
            "parfait pour booster votre pool d'affiliés. Beta privée. Vous voulez un accès test "
            "pour {nom_entreprise} ?"
        ),
    ),
)

_T_DENICHEUR_STUDIOS: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="Votre vivier de talents, sans les chasser",
        body=(
            "Bonjour {prenom},\n\n"
            "Petite idée pour {nom_entreprise} : on a un SaaS qui sort en quelques clics une "
            "liste de créateurs émergents par niche, avec stats d'engagement, format dominant et "
            "(le plus important) **pas encore approchés par les marques**.\n\n"
            "Idéal pour staffer vos prochaines campagnes ou enrichir votre roster sans démarchage manuel.\n\n"
            "15 min de démo cette semaine ?\n\n"
            "{mon_prenom} — Triskell Studio"
        ),
    ),
)


# ---------------------------------------------------------------------------
# Templates — SaaS Publication Automatisée
# ---------------------------------------------------------------------------

_T_PUBLI_CM: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="Récupérer 8h par semaine ? (pour de vrai)",
        body=(
            "Bonjour {prenom},\n\n"
            "Si vous gérez plusieurs comptes clients, vous savez où partent vos heures : "
            "programmation, recadrage, copie/colle entre plateformes.\n\n"
            "On a sorti un SaaS qui automatise tout ça **avec une vraie intelligence** "
            "(pas du Buffer like) : adaptation auto du format par réseau, planification "
            "optimale par audience, recyclage intelligent du contenu.\n\n"
            "J'offre 30 jours d'accès gratuit aux 50 premiers CM indé qui essaient. "
            "Vous voulez votre code ?\n\n"
            "{mon_prenom} — Triskell Studio"
        ),
    ),
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, si vous gérez plusieurs comptes clients, on a un SaaS qui "
            "automatise la publi avec une vraie intelligence d'adaptation par plateforme. "
            "30 jours offerts aux 50 premiers CM indé. Je vous envoie le code ?"
        ),
    ),
)

_T_PUBLI_AGENCES: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="whatsapp",
        subject="",
        body=(
            "Bonjour {prenom}, {mon_prenom} de Triskell Studio. On a un SaaS de publication "
            "automatisée pensé pour les agences (multi-comptes, multi-clients, validation interne, "
            "reporting auto). Si vous voulez un test gratuit 30 jours pour {agence}, "
            "je vous configure le compte."
        ),
    ),
    ChannelTemplate(
        channel="email",
        subject="Reporting client + multi-comptes : on automatise le pénible",
        body=(
            "Bonjour {prenom},\n\n"
            "Pour une agence comme {agence}, le pénible n'est pas la stratégie — c'est l'opérationnel : "
            "20 comptes à programmer, validation interne, reporting client.\n\n"
            "On a sorti un SaaS qui couvre exactement ces 3 douleurs (multi-comptes, validation à étages, "
            "reporting auto white-label).\n\n"
            "30 jours offerts si vous voulez tester sur 2-3 comptes clients. Je vous configure ?\n\n"
            "{mon_prenom} — Triskell Studio"
        ),
    ),
)

_T_PUBLI_SOLO: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="instagram_dm",
        subject="",
        body=(
            "Hey {prenom} ! 👋 J'imagine que tenir le rythme sur Insta + LinkedIn + TikTok, "
            "c'est l'enfer quand t'es seul·e. On a un outil qui programme tout en intelligent "
            "(adaptation par plateforme + horaires optimaux pour ton audience). "
            "Tu veux un accès gratuit 30 jours pour tester ?"
        ),
    ),
)

_T_PUBLI_COACHS: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="facebook_messenger",
        subject="",
        body=(
            "Bonjour {prenom}, j'ai vu vos contenus sur {sujet_expertise} — qualité au top. "
            "Si tenir la régularité de publi vous bouffe du temps, on a un outil qui automatise "
            "tout *intelligemment*. 30 jours offerts pour tester. Ça vous tente ?"
        ),
    ),
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, votre contenu sur {sujet_expertise} est solide. Si vous voulez "
            "garder la régularité sans y passer 5h/semaine, on a un SaaS de publi auto pensé pour "
            "les coachs. 30 jours offerts pour tester. Je vous envoie le lien ?"
        ),
    ),
)

_T_PUBLI_ECOM: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="Tenir un calendrier social sans y passer vos soirées",
        body=(
            "Bonjour {prenom},\n\n"
            "Pour {nom_entreprise}, le social media est sûrement un canal critique mais "
            "chronophage. On a sorti un SaaS de publication automatisée qui prend en compte "
            "le format, le réseau, les horaires optimaux et le recyclage intelligent.\n\n"
            "30 jours offerts pour tester. Vous voulez votre accès ?\n\n"
            "{mon_prenom} — Triskell Studio"
        ),
    ),
)


# ---------------------------------------------------------------------------
# Templates — Triskell Suite (B2C)
# ---------------------------------------------------------------------------

_T_SUITE_CADRES: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="5 apps premium au lieu de 5 abonnements",
        body=(
            "Bonjour {prenom},\n\n"
            "Combien d'abonnements payez-vous chaque mois pour bosser efficacement ? "
            "Notion + un truc PDF + un cleaner PC + Outlook + un gestionnaire photo... "
            "ça pique vite.\n\n"
            "On a sorti **Triskell Suite** : 5 applications premium en une (notes avancées, "
            "gestion photo, PDF 8-en-1, optimisation PC, mail+calendrier). Une seule licence, "
            "à vie ou en abonnement, et tout est local — vos données restent chez vous.\n\n"
            "Promo de lancement à -40% jusqu'au {date_promo}. Voici votre code : {code_promo}.\n\n"
            "{mon_prenom} — Triskell Studio\n{lien_site}"
        ),
    ),
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, on vient de sortir Triskell Suite : 5 apps premium en une "
            "(notes, photo, PDF, optimisation PC, mail+agenda). Tout local, une seule licence. "
            "-40% lancement avec {code_promo} jusqu'au {date_promo}. Je vous envoie le lien ?"
        ),
    ),
)

_T_SUITE_ETUDIANTS: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="instagram_dm",
        subject="",
        body=(
            "Hello {prenom} 👋 Si t'en as marre d'avoir 12 apps différentes pour bosser, "
            "on a sorti Triskell Suite : 5 outils premium en un (notes, PDF, photos, ménage du PC, mails). "
            "Un seul truc à installer, ça respire. -50% étudiant avec {code_promo}. 🎓"
        ),
    ),
    ChannelTemplate(
        channel="facebook_messenger",
        subject="",
        body=(
            "Salut {prenom}, on a sorti Triskell Suite : 5 apps en une (notes, photos, PDF, "
            "nettoyage PC, mails+agenda). Une licence, tout local. -50% étudiant avec {code_promo}. "
            "Je t'envoie le lien ?"
        ),
    ),
)

_T_SUITE_FREELANCES: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="L'outil qui remplace 5 abonnements de votre quotidien admin",
        body=(
            "Bonjour {prenom},\n\n"
            "Vous gérez factures, emails, scans, photos clients, classement... avec combien "
            "d'outils différents ?\n\n"
            "**Triskell Suite** réunit 5 apps premium en une seule licence : notes avancées "
            "(style Evernote), gestion photo pro (style ACDSee), PDF 8-en-1, optimisation PC, "
            "mail + calendrier. Tout local, zéro abonnement caché.\n\n"
            "Code promo lancement -40% : {code_promo}. Valable jusqu'au {date_promo}.\n\n"
            "{mon_prenom} — Triskell Studio"
        ),
    ),
)

_T_SUITE_PHOTO: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="instagram_dm",
        subject="",
        body=(
            "Hello {prenom} 📸 Vu vos clichés, ça envoie ! On a sorti une suite avec une app "
            "de gestion photo qui claque (style ACDSee mais plus moderne) + 4 autres outils utiles. "
            "Une licence, tout local. -40% lancement avec {code_promo}."
        ),
    ),
)

_T_SUITE_SENIORS: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="facebook_messenger",
        subject="",
        body=(
            "Bonjour {prenom}, on a conçu une suite d'applications **simple et tout-en-un** "
            "pour gérer notes, photos, PDF, mails et nettoyer son ordinateur — sans avoir à apprendre "
            "5 logiciels différents. Si ça vous parle, je peux vous envoyer le lien et un code "
            "de réduction. Rien d'engageant."
        ),
    ),
    ChannelTemplate(
        channel="email",
        subject="Une suite simple pour tout faire sur votre ordinateur",
        body=(
            "Bonjour {prenom},\n\n"
            "Triskell Suite réunit 5 outils essentiels en une seule application : "
            "notes, photos, PDF, ménage du PC, mails et calendrier. Conçue pour être "
            "facile à utiliser, sans abonnements multiples.\n\n"
            "Code promo : {code_promo} — valable jusqu'au {date_promo}.\n\n"
            "Bien cordialement,\n{mon_prenom} — Triskell Studio"
        ),
    ),
)

_T_SUITE_FAMILLES: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="whatsapp",
        subject="",
        body=(
            "Bonjour {prenom}, {mon_prenom} de Triskell Studio. On vient de sortir une suite de "
            "5 apps premium (notes, photos, PDF, ménage PC, mails) — une seule licence pour tout "
            "le foyer. -40% jusqu'au {date_promo} avec {code_promo}. Je vous envoie le lien ?"
        ),
    ),
)


# ---------------------------------------------------------------------------
# Templates — Bundles Mixtes
# ---------------------------------------------------------------------------

_T_BUNDLE_SOLO: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="Pack tout-en-un : votre site pro + votre boîte à outils perso",
        body=(
            "Bonjour {prenom},\n\n"
            "Solopreneur, vous portez deux casquettes : pro (visibilité, site, acquisition) "
            "et perso (productivité, admin, organisation).\n\n"
            "Chez Triskell, on propose un **bundle mixte** : votre site pro premium + Triskell Suite "
            "(5 apps perso) + accès aux SaaS de growth, à un tarif unique qui ne correspond à rien "
            "de comparable.\n\n"
            "15 min en visio pour qu'on construise *votre* bundle ensemble ? Je vous fais un devis "
            "sur mesure dans la foulée.\n\n"
            "{mon_prenom} — Triskell Studio\n{lien_site}"
        ),
    ),
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, pour les solopreneurs on propose chez Triskell un bundle "
            "(site pro + Suite 5 apps + outils growth) — un seul prestataire, un seul devis. "
            "15 min pour qu'on construise le vôtre ?"
        ),
    ),
)

_T_BUNDLE_AUTO: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, chez Triskell on propose des bundles à la carte (site pro + apps perso "
            "+ outils growth) — un seul prestataire, un seul devis, un seul interlocuteur. "
            "Si vous voulez un mini-audit gratuit de votre stack actuelle, 20 min suffisent."
        ),
    ),
)

_T_BUNDLE_EQUIPES: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="whatsapp",
        subject="",
        body=(
            "Bonjour {prenom}, {mon_prenom} de Triskell Studio. On fait des bundles pour petites "
            "équipes (site pro + Suite multi-licences + SaaS au choix). Plus simple qu'à la carte, "
            "et tarif équipe avantageux. On en parle 15 min ?"
        ),
    ),
)

# ---------------------------------------------------------------------------
# DéliNote (notes B2C — 79 €)
# ---------------------------------------------------------------------------

_T_DELINOTE_CADRES: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="Vos notes méritent mieux qu'Evernote",
        body=(
            "Bonjour {prenom},\n\n"
            "Si vos notes pro sont éparpillées entre Evernote, OneNote, des post-its et 3 docs Google, "
            "**DéliNote** centralise tout : markdown natif, recherche instantanée, sync chiffrée, "
            "pas de cloud Triskell, pas d'abonnement.\n\n"
            "79 € paiement unique, mises à jour à vie. Garantie 14 jours.\n\n"
            "{mon_prenom} — Triskell Studio\n{lien_site}"
        ),
    ),
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, vu votre activité {sujet_expertise} — vous prenez sûrement beaucoup "
            "de notes. DéliNote remplace Evernote/Notion : 100 % local, markdown natif, "
            "79 € à vie. Si ça vous parle, je vous envoie le lien."
        ),
    ),
)

_T_DELINOTE_ETUDIANTS: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="instagram_dm",
        subject="",
        body=(
            "Hey {prenom} ! Pour les notes de cours / révisions, DéliNote c'est le combo idéal : "
            "markdown natif, recherche instantanée, 100 % local. 79 € une fois, mises à jour à vie. "
            "Promo étudiant dispo. Je t'envoie le lien ?"
        ),
    ),
)


# ---------------------------------------------------------------------------
# Le Studio PDF (39 €)
# ---------------------------------------------------------------------------

_T_STUDIO_PDF_BUREAU: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="Vos PDF, sans bouger un fichier en ligne",
        body=(
            "Bonjour {prenom},\n\n"
            "Fusion, split, OCR, signature, compression — tout ce qu'on fait à des PDF, "
            "**Le Studio PDF** le fait en local sur votre machine. Aucun upload, aucun tracker, "
            "aucun abonnement.\n\n"
            "39 € paiement unique. Idéal pour la compta, les contrats, les scans sensibles.\n\n"
            "{mon_prenom} — Triskell Studio"
        ),
    ),
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, pour les pros qui manipulent des PDF sensibles (compta, contrats), "
            "Le Studio PDF est local — rien n'est uploadé. 39 € à vie. Si ça vous intéresse, "
            "je vous envoie le lien."
        ),
    ),
)


# ---------------------------------------------------------------------------
# AlphaBeast (prompts IA, 19 €)
# ---------------------------------------------------------------------------

_T_ALPHABEAST_DEV: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="linkedin",
        subject="",
        body=(
            "Bonjour {prenom}, vu que vous bossez avec Claude / GPT au quotidien — "
            "AlphaBeast combine ton prompt avec 16 Mega Prompts (Honnêteté brutale, Anti-slop, "
            "Pre-mortem, Sparring partner…) et l'envoie au provider de ton choix. 19 € à vie."
        ),
    ),
    ChannelTemplate(
        channel="twitter_dm",
        subject="",
        body=(
            "Hello {prenom} 👋 Si tu bosses avec Claude/GPT au quotidien, AlphaBeast = 16 mega prompts "
            "brandés (Honnêteté brutale, Anti-slop, Pre-mortem) à combiner. 5 providers IA. 19 € à vie."
        ),
    ),
)


# ---------------------------------------------------------------------------
# Bobeez (gestionnaire d'images B2C, 27 €)
# ---------------------------------------------------------------------------

_T_BOBEEZ_PHOTO: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="Vos photos, enfin organisées (sans cloud forcé)",
        body=(
            "Bonjour {prenom},\n\n"
            "Si vos photos s'empilent sans logique, **Bobeez** range tout : calendrier, carte GPS, "
            "tri rapide, doublons, le tout en local. Pas de Google Photos qui upload, pas d'abonnement.\n\n"
            "27 € paiement unique, mises à jour à vie.\n\n"
            "{mon_prenom} — Triskell Studio"
        ),
    ),
    ChannelTemplate(
        channel="instagram_dm",
        subject="",
        body=(
            "Hello {prenom} 📸 Bobeez = gestionnaire de photos local, calendrier + carte GPS + tri rapide, "
            "27 € à vie. Pas de cloud forcé. Tu veux le lien ?"
        ),
    ),
)


# ---------------------------------------------------------------------------
# Triskell Outils Pro (calculateurs chantier, 9 €/mois)
# ---------------------------------------------------------------------------

_T_OUTILS_BAT: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="Calculateurs chantier qui te font gagner 30 min/jour",
        body=(
            "Bonjour {prenom},\n\n"
            "Calcul carrelage, placo, peinture, béton — encore au tableur Excel ou au papier ?\n\n"
            "**Triskell Outils Pro** = calculateurs métier dédiés artisans bâtiment, "
            "9 €/mois (sans engagement). Tu poses les côtes, l'outil sort le métré + bon de commande.\n\n"
            "{mon_prenom} — Triskell Studio"
        ),
    ),
    ChannelTemplate(
        channel="whatsapp",
        subject="",
        body=(
            "Bonjour {prenom}, {mon_prenom} de Triskell. Pour le calcul carrelage / placo / peinture / béton, "
            "on a Triskell Outils Pro à 9 €/mois sans engagement. Métré + bon de commande directement. "
            "Je t'envoie le lien ?"
        ),
    ),
)


# ---------------------------------------------------------------------------
# Pack Électricien Pro (33 modèles devis/factures, 27 €)
# ---------------------------------------------------------------------------

_T_PACK_ELEC: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        subject="33 modèles devis/factures électricien + outil chantier offert",
        body=(
            "Bonjour {prenom},\n\n"
            "Marre de bricoler tes devis sur Word ?\n\n"
            "**Pack Électricien Pro** : 33 modèles devis/factures spécifiques métier électricien "
            "(branchement, mise aux normes, dépannage, rénovation totale) + outil chantier offert. "
            "27 € paiement unique, à vie.\n\n"
            "{mon_prenom} — Triskell Studio"
        ),
    ),
    ChannelTemplate(
        channel="whatsapp",
        subject="",
        body=(
            "Bonjour {prenom}, {mon_prenom} de Triskell. Pour les électriciens : pack 33 modèles "
            "devis/factures + outil chantier offert. 27 € à vie. Je t'envoie le lien ?"
        ),
    ),
)


_T_BUNDLE_COACHS: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="instagram_dm",
        subject="",
        body=(
            "Hello {prenom} 👋 Pour un coach avec offre digitale, on a un bundle qui couvre tout : "
            "site premium + 5 apps de productivité + outil de publi auto. Un seul devis, un seul "
            "prestataire. Je vous envoie une proposition perso pour {nom_entreprise} ?"
        ),
    ),
)


# ---------------------------------------------------------------------------
# Contextes / situations possibles par produit (Niveau "cas spécifique")
# ---------------------------------------------------------------------------

# Triskell Studio — sites web
CTX_HAS_SITE = ProductContext(
    key="has_site",
    label="A déjà un site",
    description="Le prospect a un site existant à refondre / améliorer.",
)
CTX_NO_SITE = ProductContext(
    key="no_site",
    label="Pas (encore) de site",
    description="Le prospect n'a pas de site, on part de zéro.",
)
CTX_OBSOLETE = ProductContext(
    key="obsolete_site",
    label="Site obsolète",
    description="Site existant clairement dépassé (mobile cassé, design années 2010).",
)

# Eliks Studio — growth perf
CTX_PAID_RUNNING = ProductContext(
    key="paid_running",
    label="Déjà du paid actif",
    description="Le prospect tourne déjà des campagnes payantes (en interne ou agence).",
)
CTX_NO_PAID = ProductContext(
    key="no_paid",
    label="Aucun paid à ce jour",
    description="Pas encore d'acquisition payante structurée.",
)

# Dénicheur de créateurs
CTX_HAS_UGC = ProductContext(
    key="has_ugc",
    label="Programme UGC en place",
    description="Le prospect fait déjà appel à des créateurs.",
)
CTX_STARTING_UGC = ProductContext(
    key="starting_ugc",
    label="Démarre l'UGC",
    description="Pas encore (ou très peu) de créateurs activés.",
)

# Publication automatisée
CTX_MANUAL_PUB = ProductContext(
    key="manual_pub",
    label="Publication manuelle",
    description="Le prospect publie à la main, sans outil dédié.",
)
CTX_OTHER_TOOL = ProductContext(
    key="other_tool",
    label="Utilise un autre outil",
    description="Buffer / Hootsuite / Later / Metricool déjà en place.",
)

# Triskell Suite — B2C
CTX_MANY_SUBS = ProductContext(
    key="many_subs",
    label="Plein d'abonnements",
    description="Le prospect cumule 4-5 abonnements logiciels.",
)
CTX_FREE_TOOLS = ProductContext(
    key="free_tools",
    label="Bricole avec du gratuit",
    description="Le prospect utilise des outils gratuits / limités.",
)

# Bundles
CTX_SOLO = ProductContext(
    key="solo",
    label="Solopreneur",
    description="Prospect seul, double casquette pro/perso.",
)
CTX_TEAM = ProductContext(
    key="team",
    label="Petite équipe",
    description="Prospect avec une mini-équipe (2-5 personnes).",
)


# ---------------------------------------------------------------------------
# Templates contextuels — accents préservés (é, à, ê, ç…)
# ---------------------------------------------------------------------------

_CTX_TEMPLATES_TRISKELL_STUDIO: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        context="has_site",
        subject="Quelques pistes pour booster {nom_entreprise} (vu votre site)",
        body=(
            "Bonjour {prenom},\n\n"
            "J'ai jeté un œil au site de {nom_entreprise} — il y a une vraie identité, c'est déjà "
            "un bon point. J'ai relevé 3 points qui pourraient sérieusement améliorer la conversion :\n\n"
            "1. {friction_1}\n"
            "2. {friction_2}\n"
            "3. {friction_3}\n\n"
            "Chez Triskell Studio, on refait justement ce genre de sites en s'attaquant directement "
            "à ce qui freine les ventes. Si vous voulez qu'on regarde ensemble votre site existant, "
            "je vous offre 20 min de mini-audit, sans engagement.\n\n"
            "Bien cordialement,\n{mon_prenom} — Triskell Studio\n{lien_site}"
        ),
    ),
    ChannelTemplate(
        channel="email",
        context="no_site",
        subject="Pas (encore) de site pour {nom_entreprise} ? On peut changer ça en 48h.",
        body=(
            "Bonjour {prenom},\n\n"
            "J'ai cherché {nom_entreprise} en ligne et… j'ai pas trouvé de site officiel. "
            "À l'heure où vos prospects cherchent forcément avant d'appeler, c'est un manque "
            "qui doit vous coûter pas mal de clients.\n\n"
            "Bonne nouvelle : chez Triskell Studio, on conçoit votre site premium *avant même* "
            "que vous le demandiez, en 3 versions personnalisées. Mise en ligne en 48h. "
            "Dès 49,97 €/mois, sans engagement long.\n\n"
            "Si vous voulez voir à quoi pourrait ressembler le site de {nom_entreprise}, "
            "je vous offre une démo perso en 15 min.\n\n"
            "Bien cordialement,\n{mon_prenom} — Triskell Studio\n{lien_site}"
        ),
    ),
    ChannelTemplate(
        channel="email",
        context="obsolete_site",
        subject="Le site de {nom_entreprise} mérite mieux que ça",
        body=(
            "Bonjour {prenom},\n\n"
            "Sans détour : le site actuel de {nom_entreprise} ne reflète plus du tout votre "
            "niveau réel. Mobile cassé, design qui sent les années 2010, vitesse… ça pénalise "
            "vraiment vos demandes entrantes (et votre SEO).\n\n"
            "Chez Triskell Studio, on refait des sites premium pour des structures comme la vôtre "
            "— design soigné, mobile-first, SEO local, conversion optimisée. Délai moyen : 2 à 3 semaines.\n\n"
            "Si ça vous parle, 20 minutes en visio cette semaine ? Je vous présente 2-3 pistes "
            "concrètes pour {nom_entreprise}.\n\n"
            "Bien cordialement,\n{mon_prenom} — Triskell Studio\n{lien_site}"
        ),
    ),
    ChannelTemplate(
        channel="linkedin",
        context="has_site",
        subject="",
        body=(
            "Bonjour {prenom}, j'ai jeté un œil au site de {nom_entreprise} — il y a des bases "
            "solides, mais aussi 2-3 frictions qui doivent vous coûter des leads. Si vous voulez "
            "20 min de mini-audit gratuit, je vous montre concrètement ce qui changerait. — "
            "{mon_prenom}, Triskell Studio."
        ),
    ),
    ChannelTemplate(
        channel="linkedin",
        context="no_site",
        subject="",
        body=(
            "Bonjour {prenom}, je n'ai pas trouvé de site officiel pour {nom_entreprise}. "
            "Chez Triskell Studio on monte un site premium en 48h, dès 49,97 €/mois. "
            "Si vous voulez voir une démo perso pour {nom_entreprise}, 15 min suffisent."
        ),
    ),
)

_CTX_TEMPLATES_ELIKS: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        context="paid_running",
        subject="Vos campagnes paid actuelles : audit gratuit, vraies pistes",
        body=(
            "Bonjour {prenom},\n\n"
            "Vous tournez déjà des campagnes payantes pour {nom_entreprise} — bien. La question "
            "qui revient : est-ce que ça performe vraiment, ou est-ce que ça brûle du cash ?\n\n"
            "Chez Eliks Studio, on prend en charge votre paid en 100 % perf : on audite ce qui "
            "tourne, on optimise, et on est rémunérés *uniquement* sur l'incrément de ventes.\n\n"
            "Si vous voulez un audit gratuit (20 min, sans engagement), je vous le boucle "
            "cette semaine.\n\n"
            "Bien cordialement,\n{mon_prenom} — Eliks Studio (groupe Triskell)"
        ),
    ),
    ChannelTemplate(
        channel="email",
        context="no_paid",
        subject="Et si on testait le paid sur {nom_entreprise}, sans risque ?",
        body=(
            "Bonjour {prenom},\n\n"
            "{nom_entreprise} a une vraie traction organique — c'est rare et précieux. "
            "Mais sans levier payant, vous laissez beaucoup de cash sur la table.\n\n"
            "Eliks Studio prend en charge votre première campagne d'acquisition payante. "
            "Notre modèle : 100 % perf. Pas de retainer, pas de budget agence à avancer — "
            "on est payés *uniquement* sur les ventes générées.\n\n"
            "Test sans risque pendant 30 jours, ça vous parle ? 20 min en visio cette semaine "
            "pour calibrer ensemble.\n\n"
            "Bien cordialement,\n{mon_prenom} — Eliks Studio"
        ),
    ),
)

_CTX_TEMPLATES_DENICHEUR: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        context="has_ugc",
        subject="Vos créateurs UGC actuels : trouver les pépites manquantes",
        body=(
            "Bonjour {prenom},\n\n"
            "Vous bossez déjà avec des créateurs UGC pour {nom_entreprise} — bravo, c'est le levier "
            "le plus sous-coté du moment. Le vrai défi maintenant : trouver des créateurs frais, "
            "encore non saturés par les marques.\n\n"
            "On a sorti un outil qui détecte exactement ça : engagement réel, audience cohérente, "
            "*non monétisés*. Idéal pour rafraîchir votre roster sans démarcher 200 profils par semaine.\n\n"
            "Démo perso pour {nom_entreprise} ? 15 minutes suffisent.\n\n"
            "Bien cordialement,\n{mon_prenom} — Triskell Studio"
        ),
    ),
    ChannelTemplate(
        channel="email",
        context="starting_ugc",
        subject="Lancer l'UGC pour {nom_entreprise} — sourcing simplifié",
        body=(
            "Bonjour {prenom},\n\n"
            "Si {nom_entreprise} envisage de se lancer dans l'UGC, le premier mur est connu : "
            "trouver les créateurs adaptés sans y passer 10h par semaine.\n\n"
            "Notre SaaS sort en quelques clics une short-list de créateurs pertinents pour votre niche, "
            "*non encore approchés par les marques*. Vous gagnez du temps, vous testez plus vite, "
            "vous payez moins cher.\n\n"
            "Démo de 15 min cette semaine pour vous montrer comment ça marche ?\n\n"
            "Bien cordialement,\n{mon_prenom} — Triskell Studio"
        ),
    ),
)

_CTX_TEMPLATES_PUBLI: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        context="manual_pub",
        subject="Récupérer 6 à 8 heures par semaine sur la publi {nom_entreprise}",
        body=(
            "Bonjour {prenom},\n\n"
            "Si la publication réseaux sociaux pour {nom_entreprise} est encore manuelle, "
            "vous savez où partent vos heures : programmation, recadrage, copie/colle entre plateformes.\n\n"
            "Notre SaaS de publication automatisée règle exactement ça : adaptation auto par réseau, "
            "horaires optimaux selon votre audience, recyclage intelligent du contenu.\n\n"
            "30 jours offerts pour tester. Je vous configure le compte ?\n\n"
            "Bien cordialement,\n{mon_prenom} — Triskell Studio"
        ),
    ),
    ChannelTemplate(
        channel="email",
        context="other_tool",
        subject="Vous utilisez {outil_actuel} ? Voici pourquoi nos clients passent chez nous",
        body=(
            "Bonjour {prenom},\n\n"
            "Beaucoup de nos clients arrivaient de {outil_actuel}. Pourquoi ils ont changé ?\n\n"
            "1. Adaptation *intelligente* du format par plateforme (pas juste un copier-coller).\n"
            "2. Horaires optimaux calculés à partir de votre audience réelle.\n"
            "3. Reporting client white-label (utile en agence).\n"
            "4. Tarif plus juste, sans surprise par compte.\n\n"
            "30 jours offerts pour comparer en parallèle. Je vous configure ça ?\n\n"
            "Bien cordialement,\n{mon_prenom} — Triskell Studio"
        ),
    ),
)

_CTX_TEMPLATES_SUITE: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        context="many_subs",
        subject="Combien d'abonnements logiciels payez-vous chaque mois ?",
        body=(
            "Bonjour {prenom},\n\n"
            "Notion, un truc PDF, un cleaner PC, Outlook, un gestionnaire photo… "
            "5 abonnements pour bosser efficacement, c'est devenu la norme. Et ça pique vite.\n\n"
            "On a sorti **Triskell Suite** : 5 applications premium en une seule licence. "
            "Notes avancées (style Evernote), gestion photo (style ACDSee), PDF 8-en-1, "
            "optimisation PC, mail + calendrier. Tout local, vos données restent chez vous.\n\n"
            "Promo lancement -40 % jusqu'au {date_promo}. Code : {code_promo}.\n\n"
            "Bien cordialement,\n{mon_prenom} — Triskell Studio\n{lien_site}"
        ),
    ),
    ChannelTemplate(
        channel="email",
        context="free_tools",
        subject="Passer du gratuit limité au pro, sans abonnement à rallonge",
        body=(
            "Bonjour {prenom},\n\n"
            "Les outils gratuits, c'est super pour démarrer. Mais arrivé à un certain point, "
            "leurs limites coûtent plus cher en temps perdu qu'un vrai outil pro.\n\n"
            "**Triskell Suite** : 5 apps premium en une licence (notes, photo, PDF, optimisation PC, mail). "
            "Pas d'abonnement caché, tout local. Une fois pour toutes.\n\n"
            "Promo lancement -40 % jusqu'au {date_promo}. Code : {code_promo}.\n\n"
            "Bien cordialement,\n{mon_prenom} — Triskell Studio"
        ),
    ),
)

_CTX_TEMPLATES_BUNDLES: Tuple[ChannelTemplate, ...] = (
    ChannelTemplate(
        channel="email",
        context="solo",
        subject="Solopreneur : un seul devis pour votre stack pro + perso",
        body=(
            "Bonjour {prenom},\n\n"
            "Solopreneur, vous portez deux casquettes : pro (visibilité, site, acquisition) "
            "et perso (productivité, admin, organisation). En général, ça finit en jonglage "
            "entre 6 prestataires différents.\n\n"
            "Chez Triskell, on construit votre **bundle solo** : site pro premium + Triskell Suite "
            "(5 apps perso) + outils growth au choix. Un seul devis, un seul interlocuteur.\n\n"
            "15 min en visio pour qu'on construise *votre* bundle ensemble ?\n\n"
            "Bien cordialement,\n{mon_prenom} — Triskell Studio\n{lien_site}"
        ),
    ),
    ChannelTemplate(
        channel="email",
        context="team",
        subject="Petite équipe : licences groupées + tarif équipe avantageux",
        body=(
            "Bonjour {prenom},\n\n"
            "Pour une petite équipe comme la vôtre, on propose un **bundle équipe** : "
            "site pro Triskell + Triskell Suite multi-licences + SaaS au choix. "
            "Plus simple qu'à la carte, et le tarif équipe est franchement avantageux.\n\n"
            "15 min en visio pour calibrer le périmètre exact ?\n\n"
            "Bien cordialement,\n{mon_prenom} — Triskell Studio\n{lien_site}"
        ),
    ),
)


# ---------------------------------------------------------------------------
# Catalogue produits
# ---------------------------------------------------------------------------

PRODUCTS: Tuple[Product, ...] = (
    Product(
        key="triskell_studio",
        label="Triskell Studio — Sites web sur mesure",
        tagline="Sites premium taillés sur mesure, design qui vous ressemble.",
        audience="B2B",
        contexts=(CTX_HAS_SITE, CTX_NO_SITE, CTX_OBSOLETE),
        context_templates=_CTX_TEMPLATES_TRISKELL_STUDIO,
        clients=(
            ClientTarget(
                key="tpe_pme",
                label="TPE / PME bretonnes",
                priority=1,
                description="Petites et moyennes entreprises locales — proximité et confiance.",
                templates=_T_TRISKELL_TPE_PME,
            ),
            ClientTarget(
                key="restau_hotels",
                label="Restaurants, cafés, hôtels indépendants",
                priority=1,
                description="Site souvent vieillissant, ROI rapide via réservation et photos.",
                templates=_T_TRISKELL_RESTAU,
            ),
            ClientTarget(
                key="artisans",
                label="Artisans & indépendants",
                priority=2,
                description="Besoin de crédibilité et de canal de devis qualifiés.",
                templates=_T_TRISKELL_ARTISANS,
            ),
            ClientTarget(
                key="coachs",
                label="Coachs & consultants",
                priority=2,
                description="Image premium attendue, message clair, conversion optimisée.",
                templates=_T_TRISKELL_COACHS,
            ),
            ClientTarget(
                key="ecom_debut",
                label="E-commerçants débutants",
                priority=3,
                description="Budget plus serré, cycle plus long mais besoin réel.",
                templates=_T_TRISKELL_ECOM,
            ),
            ClientTarget(
                key="assoc",
                label="Associations & collectivités",
                priority=3,
                description="Décision lente, panier moyen correct, accessibilité critique.",
                templates=_T_TRISKELL_ASSOC,
            ),
        ),
    ),
    Product(
        key="eliks_studio",
        label="Eliks Studio — Growth Partner 100% performance",
        tagline="On bosse votre acquisition, payés uniquement sur les ventes générées.",
        audience="B2B",
        contexts=(CTX_PAID_RUNNING, CTX_NO_PAID),
        context_templates=_CTX_TEMPLATES_ELIKS,
        clients=(
            ClientTarget(
                key="ecom_etabli",
                label="E-commerçants établis (CA 50k–500k€)",
                priority=1,
                description="Modèle perf parfaitement aligné, marge OK pour partager.",
                templates=_T_ELIKS_ECOM,
            ),
            ClientTarget(
                key="saas_b2b",
                label="SaaS B2B early-stage",
                priority=1,
                description="Besoin de croissance, pas de cash pour CMO interne.",
                templates=_T_ELIKS_SAAS,
            ),
            ClientTarget(
                key="dtc",
                label="Marques DTC ambitieuses",
                priority=2,
                description="Sensibles au ROAS, marque forte mais paid à scaler.",
                templates=_T_ELIKS_DTC,
            ),
            ClientTarget(
                key="infopreneurs",
                label="Infopreneurs & coachs premium (panier > 500€)",
                priority=2,
                description="Marges qui supportent confortablement le modèle perf.",
                templates=_T_ELIKS_INFOPRO,
            ),
            ClientTarget(
                key="agences_partenaires",
                label="Agences sans pôle perf (partenariat)",
                priority=3,
                description="Marque blanche : Eliks devient leur pôle paid en sous-traitance.",
                templates=_T_ELIKS_AGENCES,
            ),
        ),
    ),
    Product(
        key="le_denicheur",
        label="Le Dénicheur — créateurs YouTube/Twitch/Reddit",
        tagline="Identifie les créateurs UGC avec engagement réel, encore non monétisés.",
        audience="B2B",
        contexts=(CTX_HAS_UGC, CTX_STARTING_UGC),
        context_templates=_CTX_TEMPLATES_DENICHEUR,
        clients=(
            ClientTarget(
                key="agences_ugc",
                label="Agences UGC",
                priority=1,
                description="Usage quotidien, willingness to pay élevé.",
                templates=_T_DENICHEUR_AGENCES_UGC,
            ),
            ClientTarget(
                key="dtc_influence",
                label="Marques DTC qui font de l'influence",
                priority=1,
                description="Recherche permanente de créateurs frais.",
                templates=_T_DENICHEUR_DTC,
            ),
            ClientTarget(
                key="affiliation",
                label="Plateformes d'affiliation",
                priority=2,
                description="Sourcing de masse pour pool d'affiliés.",
                templates=_T_DENICHEUR_AFFIL,
            ),
            ClientTarget(
                key="studios_creatifs",
                label="Studios créatifs / Production",
                priority=2,
                description="Roster de talents, staffing campagnes.",
                templates=_T_DENICHEUR_STUDIOS,
            ),
        ),
    ),
    Product(
        key="alphacast",
        label="AlphaCast — publication multi-réseaux  ·  bientôt",
        tagline="Publication intelligente multi-réseaux, avec adaptation par plateforme.",
        audience="B2B",
        contexts=(CTX_MANUAL_PUB, CTX_OTHER_TOOL),
        context_templates=_CTX_TEMPLATES_PUBLI,
        clients=(
            ClientTarget(
                key="cm_indep",
                label="Community managers indépendants",
                priority=1,
                description="Gain de temps direct, ROI immédiat.",
                templates=_T_PUBLI_CM,
            ),
            ClientTarget(
                key="agences_smm",
                label="Agences SMM",
                priority=1,
                description="Multi-comptes, multi-clients, validation interne, reporting.",
                templates=_T_PUBLI_AGENCES,
            ),
            ClientTarget(
                key="solopreneurs",
                label="Solopreneurs / créateurs",
                priority=2,
                description="Manque de temps pour la régularité.",
                templates=_T_PUBLI_SOLO,
            ),
            ClientTarget(
                key="coachs_format",
                label="Coachs & formateurs",
                priority=2,
                description="Visibilité organique critique.",
                templates=_T_PUBLI_COACHS,
            ),
            ClientTarget(
                key="ecom_calendrier",
                label="E-commerçants",
                priority=3,
                description="Calendrier éditorial à tenir.",
                templates=_T_PUBLI_ECOM,
            ),
        ),
    ),
    Product(
        key="suite_des_heros",
        label="La Suite des Héros — 11 outils desktop",
        tagline="11 micro-outils desktop pour ranger, renommer, compresser, sécuriser tes fichiers. 27 €.",
        audience="B2C",
        contexts=(CTX_MANY_SUBS, CTX_FREE_TOOLS),
        context_templates=_CTX_TEMPLATES_SUITE,
        clients=(
            ClientTarget(
                key="cadres_remote",
                label="Cadres & pros en télétravail",
                priority=1,
                description="Besoin de productivité, budget disponible.",
                templates=_T_SUITE_CADRES,
            ),
            ClientTarget(
                key="etudiants",
                label="Étudiants",
                priority=1,
                description="Notes + PDF + bureautique très utiles, sensibles au prix.",
                templates=_T_SUITE_ETUDIANTS,
            ),
            ClientTarget(
                key="freelances_admin",
                label="Freelances administratifs",
                priority=2,
                description="Emails + factures + photos clients en quotidien.",
                templates=_T_SUITE_FREELANCES,
            ),
            ClientTarget(
                key="photo_amateurs",
                label="Photographes amateurs",
                priority=2,
                description="Gestion photo + bureautique.",
                templates=_T_SUITE_PHOTO,
            ),
            ClientTarget(
                key="seniors",
                label="Seniors actifs",
                priority=3,
                description="Simplicité d'un tout-en-un.",
                templates=_T_SUITE_SENIORS,
            ),
            ClientTarget(
                key="familles",
                label="Familles",
                priority=3,
                description="Licence partagée pour le foyer.",
                templates=_T_SUITE_FAMILLES,
            ),
        ),
    ),
    Product(
        key="bundles_mixtes",
        label="Bundles mixtes (Pro + Particulier)",
        tagline="Combinaison à la carte : site pro + Suite + outils growth.",
        audience="Mixte",
        contexts=(CTX_SOLO, CTX_TEAM),
        context_templates=_CTX_TEMPLATES_BUNDLES,
        clients=(
            ClientTarget(
                key="solo",
                label="Solopreneurs",
                priority=1,
                description="Besoin pro + perso confondus.",
                templates=_T_BUNDLE_SOLO,
            ),
            ClientTarget(
                key="auto_entrep",
                label="Auto-entrepreneurs",
                priority=1,
                description="Budget unique pour outils combinés.",
                templates=_T_BUNDLE_AUTO,
            ),
            ClientTarget(
                key="petites_equipes",
                label="Petites équipes (2-5 personnes)",
                priority=2,
                description="Licence groupée + tarif équipe.",
                templates=_T_BUNDLE_EQUIPES,
            ),
            ClientTarget(
                key="coachs_digital",
                label="Coachs / formateurs avec offre digitale",
                priority=2,
                description="Site + outils perso + publi auto.",
                templates=_T_BUNDLE_COACHS,
            ),
        ),
    ),
    # ----- DéliNote (B2C, 79 €) -----
    Product(
        key="delinote",
        label="DéliNote — notes premium 100 % locales",
        tagline="Notes synchronisées, markdown natif, recherche instantanée. 79 € à vie.",
        audience="B2C",
        clients=(
            ClientTarget(
                key="cadres_remote",
                label="Cadres & pros en télétravail",
                priority=1,
                description="Volume de notes pro élevé, marre des abonnements Notion/Evernote.",
                templates=_T_DELINOTE_CADRES,
            ),
            ClientTarget(
                key="etudiants",
                label="Étudiants",
                priority=2,
                description="Notes de cours, recherche rapide, pas envie de payer un cloud.",
                templates=_T_DELINOTE_ETUDIANTS,
            ),
        ),
    ),
    # ----- Le Studio PDF (B2C, 39 €) -----
    Product(
        key="studio_pdf",
        label="Le Studio PDF — fusion / split / OCR / signature",
        tagline="Tout pour tes PDF, en local. 39 € à vie.",
        audience="B2C",
        clients=(
            ClientTarget(
                key="bureau",
                label="Pros bureau / compta / juridique",
                priority=1,
                description="Manipulation quotidienne de PDF sensibles, refus d'upload cloud.",
                templates=_T_STUDIO_PDF_BUREAU,
            ),
        ),
    ),
    # ----- AlphaBeast (Pro, 19 €) -----
    Product(
        key="alphabeast",
        label="AlphaBeast — Mega Prompts brandés (5 IA)",
        tagline="16 Mega Prompts à combiner. Claude / GPT / Gemini / Mistral / Grok. 19 € à vie.",
        audience="B2B",
        clients=(
            ClientTarget(
                key="dev_consultants",
                label="Devs / consultants / power users IA",
                priority=1,
                description="Bossent quotidiennement avec Claude/GPT, veulent prompts calibrés.",
                templates=_T_ALPHABEAST_DEV,
            ),
        ),
    ),
    # ----- Bobeez (B2C, 27 €) -----
    Product(
        key="bobeez",
        label="Bobeez — gestionnaire d'images moderne",
        tagline="Calendrier, carte GPS, tri rapide, doublons. 27 € à vie.",
        audience="B2C",
        clients=(
            ClientTarget(
                key="photographes",
                label="Photographes amateurs / familles",
                priority=1,
                description="Pile de photos sans logique, refus du cloud forcé.",
                templates=_T_BOBEEZ_PHOTO,
            ),
        ),
    ),
    # ----- Triskell Outils Pro (artisans bâtiment, 9 €/mois) -----
    Product(
        key="outils_batiment",
        label="Triskell Outils Pro — calculateurs chantier",
        tagline="Carrelage, placo, peinture, béton. 9 €/mois sans engagement.",
        audience="B2B",
        clients=(
            ClientTarget(
                key="artisans_bat",
                label="Artisans bâtiment (carreleurs, plâtriers, peintres, maçons)",
                priority=1,
                description="Calcul métré + bon de commande, encore au papier ou Excel.",
                templates=_T_OUTILS_BAT,
            ),
        ),
    ),
    # ----- Pack Électricien Pro (27 €) -----
    Product(
        key="pack_electricien_pro",
        label="Pack Électricien Pro — 33 modèles devis/factures",
        tagline="33 modèles métier + outil chantier offert. 27 € à vie.",
        audience="B2B",
        clients=(
            ClientTarget(
                key="electriciens",
                label="Électriciens indépendants & petites entreprises",
                priority=1,
                description="Devis et factures spécifiques métier, marre de bricoler sur Word.",
                templates=_T_PACK_ELEC,
            ),
        ),
    ),
)


# ---------------------------------------------------------------------------
# Helpers de lookup
# ---------------------------------------------------------------------------

def get_product(key: str) -> Product | None:
    """Retourne le produit par clé, ou None."""
    for p in PRODUCTS:
        if p.key == key:
            return p
    return None


def get_client(product_key: str, client_key: str) -> ClientTarget | None:
    """Retourne le client cible pour un produit donné, ou None."""
    product = get_product(product_key)
    if not product:
        return None
    for c in product.clients:
        if c.key == client_key:
            return c
    return None


def get_template(
    product_key: str,
    client_key: str,
    channel: str,
    context: str = "",
) -> ChannelTemplate | None:
    """Retourne le meilleur template pour (produit, client, canal[, contexte]).

    Stratégie : si un contexte est précisé par l'utilisateur, on cherche d'abord
    une variante qui respecte ce contexte (au niveau client puis produit) avant
    de retomber sur les templates neutres.

      1. Client + canal + contexte exact      (très spécifique)
      2. Produit-level + canal + contexte exact  (respect du contexte)
      3. Client + canal neutre
      4. Produit-level + canal neutre
      5. None
    """
    product = get_product(product_key)
    client = get_client(product_key, client_key)

    if context:
        if client:
            for t in client.templates:
                if t.channel == channel and t.context == context:
                    return t
        if product:
            for t in product.context_templates:
                if t.channel == channel and t.context == context:
                    return t

    if client:
        for t in client.templates:
            if t.channel == channel and not t.context:
                return t

    if product:
        for t in product.context_templates:
            if t.channel == channel and not t.context:
                return t

    return None


def list_channels_for(product_key: str, client_key: str) -> List[str]:
    """Liste les canaux disponibles pour un (produit, client)."""
    client = get_client(product_key, client_key)
    if not client:
        return []
    return [t.channel for t in client.templates]
