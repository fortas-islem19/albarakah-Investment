"""Builds the trilingual (FR / AR / EN) MOSTALIFE quote with USD + DZD prices.
Usage: python3 tools/build_quote.py tools/tower.jpg MOSTALIFE_Website_Quote.html
"""
import base64
import html
import math
import re
import sys

tower_path, out_path = sys.argv[1], sys.argv[2]
TOWER = base64.b64encode(open(tower_path, "rb").read()).decode()

RATE = 135  # default DZD per 1 USD; editable in the page toolbar
LANGS = ["fr", "ar", "en"]
DIR = {"fr": "ltr", "ar": "rtl", "en": "ltr"}
CUR = {"en": "DZD", "fr": "DA", "ar": "دج"}


def T(en, fr, ar):
    return {"en": en, "fr": fr, "ar": ar}


# ---------------------------------------------------------------- money
def group(n, lang, dec=0):
    s = f"{n:,.{dec}f}"
    if lang == "fr":
        s = s.replace(",", " ").replace(".", ",")
    return s


def dzd_val(usd):
    v = usd * RATE
    return math.floor(v / 100 + 0.5) * 100 if v >= 1000 else math.floor(v + 0.5)


def usd_txt(n, lang):
    s = group(n, lang, 0 if float(n).is_integer() else 2)
    return f"${s}" if lang == "en" else f"{s} $"


def D(n, lang, unit=True):
    """DZD amount, recomputed live by the page when the rate changes."""
    num = group(dzd_val(n), lang)
    if unit:
        return f'<bdi class="dzd" data-usd="{n}">{num} {CUR[lang]}</bdi>'
    return f'<bdi class="dzd" data-usd="{n}" data-nounit="1">{num}</bdi>'


def U(n, lang):
    return f"<bdi>{usd_txt(n, lang)}</bdi>"


def M(n, lang):
    return f'{U(n, lang)} <span class="dz">(≈ {D(n, lang)})</span>'


def R(a, b, lang):
    da, db = group(a, lang, 0 if float(a).is_integer() else 2), group(b, lang, 0 if float(b).is_integer() else 2)
    u = f"${da}–{db}" if lang == "en" else f"{da}–{db} $"
    return f'<bdi>{u}</bdi> <span class="dz">(≈ {D(a, lang, False)}–{D(b, lang)})</span>'


def RATE_SPAN():
    return f'<bdi class="rate-val">{RATE}</bdi>'


def fmt(text, lang):
    """Escape text, then expand **bold**, {m:N}, {r:A:B}, {rate}."""
    s = html.escape(text, quote=False)
    if lang == "fr":
        s = s.replace(" :", " :").replace(" ;", " ;").replace("« ", "« ").replace(" »", " »")
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\{m:([\d.]+)\}", lambda m: M(float(m.group(1)) if "." in m.group(1) else int(m.group(1)), lang), s)
    s = re.sub(r"\{r:([\d.]+):([\d.]+)\}", lambda m: R(*(float(x) if "." in x else int(x) for x in m.groups()), lang), s)
    s = s.replace("{rate}", RATE_SPAN())
    return s


def t(d, lang):
    return fmt(d[lang], lang)


# ---------------------------------------------------------------- content
W = {  # shared words
    "plan": T("Plan", "Formule", "الباقة"),
    "included": T("Included", "Inclus", "مشمول"),
    "total": T("Total", "Total", "المجموع"),
    "all_feat": T("All {} features", "Toutes les fonctionnalités de la formule {}", "جميع ميزات باقة {}"),
    "feature": T("Feature", "Fonctionnalité", "الميزة"),
    "details": T("Details", "Détails", "التفاصيل"),
    "price_usd": T("Price (USD)", "Prix (USD)", "السعر (دولار)"),
    "price_dzd": T("Price (DZD)", "Prix (DA)", "السعر (دج)"),
    "recommended": T("Recommended", "Recommandée", "موصى بها"),
    "capability": T("Capability", "Fonctionnalité", "الميزة"),
    "service": T("Service", "Service", "الخدمة"),
    "price": T("Price", "Prix", "السعر"),
    "month": T("/ month", "/ mois", "/ شهريًا"),
    "hour": T("/ hour", "/ heure", "/ للساعة"),
    "on_quote": T("On quote", "Sur devis", "حسب الطلب"),
    "week": T("Week", "Semaine", "الأسبوع"),
    "step": T("Step", "Étape", "المرحلة"),
}

PLANS = [
    {
        "key": "1", "letter": "E", "price": 600,
        "name": T("Essential", "Essentielle", "الأساسية"),
        "sub": T("Premium landing page", "Page vitrine premium", "صفحة عرض فاخرة"),
        "time": T("1–2 weeks", "1 à 2 semaines", "من أسبوع إلى أسبوعين"),
        "target": T("Launch fast and start collecting leads", "Lancer vite et collecter des prospects", "انطلاق سريع وجمع الزبائن المحتملين"),
        "desc": T(
            "A one-page luxury website presenting Résidence El Charika, built to turn visitors from Facebook, Instagram and WhatsApp into qualified leads.",
            "Un site d'une page au design haut de gamme pour présenter la Résidence El Charika, conçu pour transformer les visiteurs venus de Facebook, Instagram et WhatsApp en prospects qualifiés.",
            "موقع من صفحة واحدة بتصميم فاخر لتقديم إقامة El Charika، مصمم لتحويل الزوار القادمين من فيسبوك وإنستغرام وواتساب إلى زبائن محتملين مؤهلين.",
        ),
        "cards": [
            T("One-page luxury design", "Design luxe sur une page", "تصميم فاخر من صفحة واحدة"),
            T("Apartments & duplexes showcase", "Présentation appartements & duplex", "عرض الشقق والدوبلكس"),
            T("Lead form + WhatsApp", "Formulaire de contact + WhatsApp", "استمارة تواصل + واتساب"),
            T("Catalogue download (lead capture)", "Téléchargement du catalogue (prospects)", "تحميل الكتالوج (جمع الزبائن)"),
            T("French + Arabic", "Français + arabe", "الفرنسية + العربية"),
        ],
        "features": [
            (T("Premium one-page design", "Design premium sur une page", "تصميم فاخر من صفحة واحدة"),
             T("Design in MOSTALIFE’s identity (navy, cream, gold, serif typography), mobile-first",
               "Design à l'identité MOSTALIFE (bleu nuit, crème, or, typographie à empattements), pensé d'abord pour le mobile",
               "تصميم بهوية MOSTALIFE (الأزرق الداكن، الكريمي، الذهبي، خطوط كلاسيكية)، مُهيأ للهاتف أولًا"), 150),
            (T("Project sections", "Sections du projet", "أقسام المشروع"),
             T("Hero, the project, architecture, services floor (pool, SPA, restaurant, prayer room), prestations, security",
               "Accueil, le projet, architecture, étage de services (piscine, SPA, restaurant, salle de prière), prestations, sécurité",
               "الواجهة، المشروع، الهندسة المعمارية، طابق الخدمات (مسبح، سبا، مطعم، قاعة صلاة)، المواصفات، الأمن"), 90),
            (T("Typologies showcase", "Présentation des typologies", "عرض أنواع الوحدات"),
             T("F3, F4 and duplex cards with surface, plan and 3D renders",
               "Fiches F3, F4 et duplex avec surface, plan et rendus 3D",
               "بطاقات F3 وF4 والدوبلكس مع المساحة والمخطط والصور ثلاثية الأبعاد"), 100),
            (T("Photo gallery", "Galerie photos", "معرض الصور"),
             T("Full-screen viewer for 3D renders and plans",
               "Visionneuse plein écran des rendus 3D et des plans",
               "عارض بملء الشاشة للصور ثلاثية الأبعاد والمخططات"), 30),
            (T("Location", "Localisation", "الموقع"),
             T("Interactive map + key distances: Sablettes beach 2.8 km, city centre 3.4 km, RN11",
               "Carte interactive + distances clés : plage des Sablettes 2,8 km, centre-ville 3,4 km, RN11",
               "خريطة تفاعلية + المسافات الرئيسية: شاطئ صابلات 2.8 كم، وسط المدينة 3.4 كم، الطريق الوطني رقم 11"), 30),
            (T("Lead capture", "Captation de prospects", "جمع الزبائن المحتملين"),
             T("“Request price / visit” form → email + WhatsApp, click-to-call button",
               "Formulaire « Demander le prix / une visite » → e-mail + WhatsApp, bouton d'appel direct",
               "استمارة «اطلب السعر / زيارة» ← بريد إلكتروني + واتساب، زر اتصال مباشر"), 70),
            (T("Catalogue download", "Téléchargement du catalogue", "تحميل الكتالوج"),
             T("Catalogue sent in exchange for name + phone number (lead generation)",
               "Catalogue envoyé contre nom + numéro de téléphone (génération de prospects)",
               "يُرسل الكتالوج مقابل الاسم ورقم الهاتف (جمع الزبائن المحتملين)"), 40),
            (T("Bilingual", "Bilingue", "ثنائي اللغة"),
             T("French + Arabic (right-to-left)", "Français + arabe (de droite à gauche)", "الفرنسية + العربية (من اليمين إلى اليسار)"), 60),
            (T("Tracking & SEO basics", "Suivi & référencement de base", "التتبع وأساسيات تحسين الظهور"),
             T("Google Analytics, Meta (Facebook / Instagram) Pixel, Search Console, meta tags",
               "Google Analytics, Pixel Meta (Facebook / Instagram), Search Console, balises meta",
               "Google Analytics، Meta Pixel (فيسبوك / إنستغرام)، Search Console، الوسوم الوصفية"), 30),
            (T("Launch", "Mise en ligne", "الإطلاق"),
             T("Put online with SSL, speed optimization, 1-hour handover",
               "Mise en ligne avec SSL, optimisation de la vitesse, 1 h de prise en main",
               "النشر مع شهادة SSL، تحسين السرعة، ساعة تدريب"), 0),
        ],
        "not": T("**Not included:** individual unit pages, availability management, admin panel.",
                 "**Non inclus :** pages par logement, gestion des disponibilités, panneau d'administration.",
                 "**غير مشمول:** صفحات الوحدات الفردية، إدارة التوفر، لوحة الإدارة."),
    },
    {
        "key": "2", "letter": "S", "price": 1200,
        "name": T("Starter", "Démarrage", "الانطلاق"),
        "sub": T("Showcase & reservation requests", "Vitrine & demandes de réservation", "العرض وطلبات الحجز"),
        "time": T("3 weeks", "3 semaines", "3 أسابيع"),
        "target": T("Present every unit and receive reservation requests", "Présenter chaque logement et recevoir des demandes de réservation", "عرض كل وحدة واستقبال طلبات الحجز"),
        "desc": T(
            "Everything in Essential, plus a full multi-page website with a page for every unit type, live availability and reservation requests.",
            "Tout le contenu de la formule Essentielle, plus un site complet de plusieurs pages avec une page par type de logement, les disponibilités en direct et les demandes de réservation.",
            "كل ما في الباقة الأساسية، بالإضافة إلى موقع متكامل متعدد الصفحات مع صفحة لكل نوع وحدة، والتوفر المباشر، وطلبات الحجز.",
        ),
        "cards": [
            T("Page for each of the 9 unit types", "Une page par type de logement (×9)", "صفحة لكل نوع من الوحدات (9)"),
            T("Availability: available / reserved / sold", "Disponibilité : libre / réservé / vendu", "التوفر: متاح / محجوز / مُباع"),
            T("Visit appointment booking", "Prise de rendez-vous de visite", "حجز موعد الزيارة"),
            T("Reservation requests", "Demandes de réservation", "طلبات الحجز"),
            T("Admin panel", "Panneau d'administration", "لوحة الإدارة"),
        ],
        "features": [
            (T("Multi-page website", "Site multi-pages", "موقع متعدد الصفحات"),
             T("Home, Project, Apartments, Duplexes, Commercial spaces, Services & wellness, Parking, Location, Contact",
               "Accueil, Projet, Appartements, Duplex, Espaces commerciaux, Services & bien-être, Stationnement, Localisation, Contact",
               "الرئيسية، المشروع، الشقق، الدوبلكس، المساحات التجارية، الخدمات والرفاهية، الركن، الموقع، اتصل بنا"), 120),
            (T("Unit type pages (×9)", "Pages par type de logement (×9)", "صفحات أنواع الوحدات (9)"),
             T("F3A, F3B, F4A, F4B, F4C and duplexes F3C, F4D, F5A, F5C: plan, surfaces, façades, views (sea / city / mountain), renders",
               "F3A, F3B, F4A, F4B, F4C et duplex F3C, F4D, F5A, F5C : plan, surfaces, façades, vues (mer / ville / montagne), rendus",
               "F3A وF3B وF4A وF4B وF4C والدوبلكس F3C وF4D وF5A وF5C: المخطط، المساحات، الواجهات، الإطلالات (بحر / مدينة / جبل)، الصور"), 130),
            (T("Availability table", "Tableau des disponibilités", "جدول التوفر"),
             T("Status per unit: available / reserved / sold, updated from the admin panel",
               "Statut par logement : libre / réservé / vendu, mis à jour depuis l'administration",
               "حالة كل وحدة: متاحة / محجوزة / مُباعة، تُحدَّث من لوحة الإدارة"), 100),
            (T("Visit booking", "Réservation de visite", "حجز الزيارات"),
             T("Buyer picks a slot to visit the sales office or the site; team confirms",
               "L'acheteur choisit un créneau pour visiter le bureau de vente ou le chantier ; l'équipe confirme",
               "يختار المشتري موعدًا لزيارة مكتب البيع أو الورشة، ويؤكد الفريق الموعد"), 80),
            (T("Reservation request", "Demande de réservation", "طلب الحجز"),
             T("“Reserve this unit” form with status tracking (new / contacted / reserved)",
               "Formulaire « Réserver ce logement » avec suivi du statut (nouveau / contacté / réservé)",
               "استمارة «احجز هذه الوحدة» مع تتبع الحالة (جديد / تم الاتصال / محجوز)"), 80),
            (T("Admin panel", "Panneau d'administration", "لوحة الإدارة"),
             T("Manage units, prices (displayed or “price on request”), photos and requests",
               "Gestion des logements, des prix (affichés ou « prix sur demande »), des photos et des demandes",
               "إدارة الوحدات، الأسعار (ظاهرة أو «السعر عند الطلب»)، الصور والطلبات"), 90),
        ],
    },
    {
        "key": "3", "letter": "B", "price": 2500, "recommended": True,
        "name": T("Business", "Business", "الأعمال"),
        "sub": T("Interactive sales platform", "Plateforme de vente interactive", "منصة بيع تفاعلية"),
        "time": T("5–6 weeks", "5 à 6 semaines", "من 5 إلى 6 أسابيع"),
        "target": T("Turn the website into a real sales tool", "Faire du site un véritable outil de vente", "تحويل الموقع إلى أداة بيع حقيقية"),
        "desc": T(
            "Everything in Starter, plus an interactive building selector, parking and commercial-space modules, buyer accounts and a CRM for the sales team.",
            "Tout le contenu de la formule Démarrage, plus un sélecteur interactif de l'immeuble, des modules parking et espaces commerciaux, des comptes acheteurs et un CRM pour l'équipe commerciale.",
            "كل ما في باقة الانطلاق، بالإضافة إلى مُحدِّد تفاعلي للعمارة، ووحدات خاصة بالركن والمساحات التجارية، وحسابات للمشترين، ونظام لإدارة الزبائن لفريق المبيعات.",
        ),
        "cards": [
            T("Interactive building / floor selector", "Sélecteur interactif immeuble / étage", "مُحدِّد تفاعلي للعمارة والطوابق"),
            T("Parking (67 spaces) & commercial modules", "Modules parking (67 places) & commerces", "وحدتا الركن (67 مكانًا) والمحلات"),
            T("Buyer accounts", "Comptes acheteurs", "حسابات المشترين"),
            T("CRM for the sales team", "CRM pour l'équipe commerciale", "إدارة الزبائن لفريق المبيعات"),
            T("Payment plan simulator", "Simulateur d'échéancier", "محاكي جدول الدفع"),
            T("PDF reservation forms", "Fiches de réservation PDF", "استمارات حجز PDF"),
        ],
        "features": [
            (T("Interactive building selector", "Sélecteur interactif de l'immeuble", "مُحدِّد تفاعلي للعمارة"),
             T("Click a floor on the tower → floor plan → unit; units colored by status (available / reserved / sold)",
               "Clic sur un étage de la tour → plan d'étage → logement ; logements colorés selon leur statut (libre / réservé / vendu)",
               "انقر على طابق في البرج ← مخطط الطابق ← الوحدة؛ الوحدات ملوّنة حسب حالتها (متاحة / محجوزة / مُباعة)"), 400),
            (T("Parking module", "Module stationnement", "وحدة الركن"),
             T("67 spaces on 3 basement levels (19 / 23 / 25), reservable with an apartment",
               "67 places sur 3 niveaux de sous-sol (19 / 23 / 25), réservables avec un appartement",
               "67 مكانًا على 3 طوابق تحت أرضية (19 / 23 / 25)، قابلة للحجز مع الشقة"), 150),
            (T("Commercial spaces module", "Module espaces commerciaux", "وحدة المساحات التجارية"),
             T("Ground floor 633.29 m² + mezzanine 580.37 m²: sale / rental inquiries for brands and investors",
               "RDC 633,29 m² + mezzanine 580,37 m² : demandes d'achat / location pour enseignes et investisseurs",
               "الطابق الأرضي 633.29 م² + الميزانين 580.37 م²: طلبات الشراء / الإيجار للعلامات التجارية والمستثمرين"), 100),
            (T("Buyer accounts", "Comptes acheteurs", "حسابات المشترين"),
             T("Sign-up, favorites, reservation history", "Inscription, favoris, historique des réservations", "التسجيل، المفضلة، سجل الحجوزات"), 150),
            (T("Mini CRM", "Mini CRM", "نظام مصغر لإدارة الزبائن"),
             T("Lead pipeline, source (Facebook, Instagram, website, walk-in), notes, follow-up reminders",
               "Suivi des prospects, source (Facebook, Instagram, site, visite directe), notes, rappels de relance",
               "تتبع الزبائن المحتملين، المصدر (فيسبوك، إنستغرام، الموقع، زيارة مباشرة)، الملاحظات، تذكيرات المتابعة"), 200),
            (T("Payment plan simulator", "Simulateur d'échéancier", "محاكي جدول الدفع"),
             T("Down payment + installments for sale on plan (VSP)",
               "Apport + échéances pour la vente sur plan (VSP)",
               "الدفعة الأولى + الأقساط للبيع على التصاميم (VSP)"), 100),
            (T("Automatic PDF documents", "Documents PDF automatiques", "وثائق PDF تلقائية"),
             T("Reservation form and receipt on MOSTALIFE letterhead",
               "Fiche de réservation et reçu à l'en-tête MOSTALIFE",
               "استمارة الحجز والوصل بترويسة MOSTALIFE"), 100),
            (T("Notifications", "Notifications", "الإشعارات"),
             T("Email & WhatsApp alerts to the buyer and the sales team",
               "Alertes e-mail & WhatsApp à l'acheteur et à l'équipe commerciale",
               "تنبيهات عبر البريد الإلكتروني وواتساب للمشتري وفريق المبيعات"), 50),
            (T("English (3rd language)", "Anglais (3e langue)", "الإنجليزية (لغة ثالثة)"),
             T("For the diaspora and foreign investors", "Pour la diaspora et les investisseurs étrangers", "للجالية والمستثمرين الأجانب"), 50),
        ],
    },
    {
        "key": "4", "letter": "P", "price": 5000,
        "name": T("Professional", "Professionnelle", "الاحترافية"),
        "sub": T("Online reservation & buyer portal", "Réservation en ligne & espace acquéreur", "الحجز عبر الإنترنت وفضاء المشتري"),
        "time": T("8–10 weeks", "8 à 10 semaines", "من 8 إلى 10 أسابيع"),
        "target": T("Buyers reserve and pay a deposit online", "Les acheteurs réservent et versent un acompte en ligne", "يحجز المشترون ويدفعون العربون عبر الإنترنت"),
        "desc": T(
            "Everything in Business, plus online deposit payment, automatic unit locking, a buyer portal with installments and construction progress, and sales reporting.",
            "Tout le contenu de la formule Business, plus le paiement de l'acompte en ligne, le blocage automatique des logements, un espace acquéreur avec échéancier et avancement des travaux, et des rapports de vente.",
            "كل ما في باقة الأعمال، بالإضافة إلى دفع العربون عبر الإنترنت، والحجز التلقائي للوحدات، وفضاء للمشتري يضم الأقساط وتقدم الأشغال، وتقارير المبيعات.",
        ),
        "cards": [
            T("Online deposit: CIB / Edahabia", "Acompte en ligne : CIB / Edahabia", "دفع العربون: CIB / الذهبية"),
            T("Diaspora card payments", "Paiement par carte pour la diaspora", "الدفع بالبطاقة للجالية"),
            T("Buyer portal & installments", "Espace acquéreur & échéancier", "فضاء المشتري والأقساط"),
            T("Construction progress updates", "Suivi de l'avancement des travaux", "متابعة تقدم الأشغال"),
            T("Sales dashboard", "Tableau de bord des ventes", "لوحة متابعة المبيعات"),
            T("360° virtual tour", "Visite virtuelle 360°", "جولة افتراضية 360°"),
        ],
        "features": [
            (T("Online deposit payment", "Paiement de l'acompte en ligne", "دفع العربون عبر الإنترنت"),
             T("CIB / Edahabia through a SATIM-approved gateway (e.g. Chargily)",
               "CIB / Edahabia via une passerelle agréée SATIM (ex. Chargily)",
               "CIB / الذهبية عبر بوابة دفع معتمدة من SATIM (مثل Chargily)"), 450),
            (T("International card payment", "Paiement international par carte", "الدفع الدولي بالبطاقة"),
             T("For diaspora buyers (subject to gateway availability)",
               "Pour les acheteurs de la diaspora (selon disponibilité de la passerelle)",
               "لمشتري الجالية (حسب توفر بوابة الدفع)"), 200),
            (T("Automatic unit lock", "Blocage automatique du logement", "الحجز التلقائي للوحدة"),
             T("Unit marked reserved once the deposit is paid; auto-released if the file is not completed in time",
               "Logement marqué réservé dès le versement de l'acompte ; libéré automatiquement si le dossier n'est pas complété à temps",
               "تُعلَّم الوحدة محجوزة فور دفع العربون، وتُحرَّر تلقائيًا إذا لم يُستكمل الملف في الآجال"), 150),
            (T("Buyer portal", "Espace acquéreur", "فضاء المشتري"),
             T("Contract documents, installment schedule, receipts, payment reminders",
               "Documents du contrat, échéancier, reçus, rappels de paiement",
               "وثائق العقد، جدول الأقساط، الوصولات، تذكيرات الدفع"), 450),
            (T("Construction progress", "Avancement des travaux", "تقدم الأشغال"),
             T("Photo / video updates by phase, notification to all buyers",
               "Mises à jour photo / vidéo par phase, notification à tous les acquéreurs",
               "تحديثات بالصور والفيديو لكل مرحلة، مع إشعار جميع المشترين"), 200),
            (T("Sales team roles", "Rôles de l'équipe commerciale", "أدوار فريق المبيعات"),
             T("Admin, sales agent, accountant; lead assignment",
               "Administrateur, commercial, comptable ; attribution des prospects",
               "مسؤول، مندوب مبيعات، محاسب؛ توزيع الزبائن المحتملين"), 200),
            (T("Sales dashboard", "Tableau de bord des ventes", "لوحة متابعة المبيعات"),
             T("Units sold, revenue, reservations, lead sources; Excel export",
               "Logements vendus, chiffre d'affaires, réservations, sources des prospects ; export Excel",
               "الوحدات المُباعة، رقم الأعمال، الحجوزات، مصادر الزبائن؛ تصدير Excel"), 250),
            (T("360° virtual tour", "Visite virtuelle 360°", "جولة افتراضية 360°"),
             T("Integration of the show apartment / duplex tour",
               "Intégration de la visite de l'appartement / duplex témoin",
               "دمج جولة الشقة / الدوبلكس النموذجي"), 200),
            (T("SMS notifications", "Notifications SMS", "إشعارات SMS"),
             T("Visit, payment and installment reminders (SMS fees extra)",
               "Rappels de visite, de paiement et d'échéance (frais SMS en sus)",
               "تذكيرات الزيارة والدفع والأقساط (رسوم الرسائل إضافية)"), 100),
            (T("Security & data protection", "Sécurité & protection des données", "الأمن وحماية المعطيات"),
             T("Daily backups, access logs, compliance with Law 18-07 on personal data",
               "Sauvegardes quotidiennes, journaux d'accès, conformité à la loi 18-07 sur les données personnelles",
               "نسخ احتياطي يومي، سجلات الدخول، الامتثال للقانون 18-07 المتعلق بالمعطيات الشخصية"), 150),
            (T("News & advanced SEO", "Actualités & référencement avancé", "الأخبار وتحسين الظهور المتقدم"),
             T("Project news / blog, structured data, fast loading",
               "Actualités du projet / blog, données structurées, chargement rapide",
               "أخبار المشروع / مدونة، بيانات منظمة، تحميل سريع"), 150),
        ],
    },
    {
        "key": "5", "letter": "X", "price": 10000,
        "name": T("Premium", "Premium", "المتميزة"),
        "sub": T("Multi-project platform + mobile app", "Plateforme multi-projets + application mobile", "منصة متعددة المشاريع + تطبيق جوال"),
        "time": T("3–4 months", "3 à 4 mois", "من 3 إلى 4 أشهر"),
        "target": T("One platform for all MOSTALIFE projects", "Une plateforme pour tous les projets MOSTALIFE", "منصة واحدة لكل مشاريع MOSTALIFE"),
        "desc": T(
            "Everything in Professional, plus iOS and Android apps, a multi-project platform for future MOSTALIFE residences, e-signature and AI-powered lead handling.",
            "Tout le contenu de la formule Professionnelle, plus des applications iOS et Android, une plateforme multi-projets pour les futures résidences MOSTALIFE, la signature électronique et une gestion des prospects assistée par l'IA.",
            "كل ما في الباقة الاحترافية، بالإضافة إلى تطبيقات iOS وAndroid، ومنصة متعددة المشاريع لإقامات MOSTALIFE المستقبلية، والتوقيع الإلكتروني، وإدارة الزبائن المحتملين بالذكاء الاصطناعي.",
        ),
        "cards": [
            T("iOS + Android apps", "Applications iOS + Android", "تطبيقات iOS + Android"),
            T("Multi-project platform", "Plateforme multi-projets", "منصة متعددة المشاريع"),
            T("E-signature", "Signature électronique", "التوقيع الإلكتروني"),
            T("AI assistant FR / AR / EN", "Assistant IA FR / AR / EN", "مساعد ذكي بثلاث لغات"),
            T("WhatsApp Business API", "WhatsApp Business API", "WhatsApp Business API"),
            T("Marketing automation", "Marketing automatisé", "التسويق الآلي"),
        ],
        "features": [
            (T("Mobile app iOS + Android", "Application mobile iOS + Android", "تطبيق جوال iOS + Android"),
             T("Browse, availability, reservation, buyer portal, push notifications; store publication",
               "Navigation, disponibilités, réservation, espace acquéreur, notifications push ; publication sur les stores",
               "التصفح، التوفر، الحجز، فضاء المشتري، إشعارات فورية؛ النشر على المتاجر"), 2600),
            (T("Multi-project platform", "Plateforme multi-projets", "منصة متعددة المشاريع"),
             T("Add future MOSTALIFE projects without new development",
               "Ajout des futurs projets MOSTALIFE sans nouveau développement",
               "إضافة مشاريع MOSTALIFE المستقبلية دون تطوير جديد"), 700),
            (T("Electronic signature", "Signature électronique", "التوقيع الإلكتروني"),
             T("Online signature of reservation documents", "Signature en ligne des documents de réservation", "توقيع وثائق الحجز عبر الإنترنت"), 400),
            (T("AI assistant", "Assistant IA", "مساعد ذكي"),
             T("On website & WhatsApp, FR / AR / EN: answers questions and qualifies leads 24/7 (AI usage fees extra)",
               "Sur le site & WhatsApp, FR / AR / EN : répond aux questions et qualifie les prospects 24 h/24 (frais d'utilisation IA en sus)",
               "على الموقع وواتساب، بالفرنسية والعربية والإنجليزية: يجيب عن الأسئلة ويؤهل الزبائن على مدار الساعة (رسوم استخدام الذكاء الاصطناعي إضافية)"), 500),
            (T("WhatsApp Business API", "WhatsApp Business API", "WhatsApp Business API"),
             T("Automated confirmations, reminders and broadcasts to leads",
               "Confirmations, rappels et diffusions automatiques aux prospects",
               "تأكيدات وتذكيرات ورسائل جماعية آلية للزبائن المحتملين"), 300),
            (T("Marketing automation", "Marketing automatisé", "التسويق الآلي"),
             T("Email / SMS campaigns, buyer segments for retargeting",
               "Campagnes e-mail / SMS, segments d'acheteurs pour le reciblage",
               "حملات البريد الإلكتروني / SMS، تقسيم المشترين لإعادة الاستهداف"), 300),
            (T("Advanced analytics", "Analyses avancées", "تحليلات متقدمة"),
             T("Conversion funnel, ad campaign attribution",
               "Tunnel de conversion, attribution des campagnes publicitaires",
               "مسار التحويل، نسب النتائج إلى الحملات الإعلانية"), 200),
        ],
    },
]

# Every plan = previous plan + its own features; fail loudly if a price drifts.
prev = 0
for p in PLANS:
    total = prev + sum(f[2] for f in p["features"])
    assert total == p["price"], (p["name"]["en"], total, p["price"])
    p["base"] = prev
    prev = p["price"]

Y, N_ = T("✓", "✓", "✓"), T("—", "—", "—")
L2, L3 = T("FR · AR", "FR · AR", "FR · AR"), T("FR · AR · EN", "FR · AR · EN", "FR · AR · EN")
TBL = T("Table", "Tableau", "جدول")
TOW = T("Interactive tower", "Tour interactive", "برج تفاعلي")
M1, M3, M6 = T("1 month", "1 mois", "شهر واحد"), T("3 months", "3 mois", "3 أشهر"), T("6 months", "6 mois", "6 أشهر")
MATRIX = [
    (T("Luxury design in MOSTALIFE identity", "Design luxe à l'identité MOSTALIFE", "تصميم فاخر بهوية MOSTALIFE"), [Y, Y, Y, Y, Y]),
    (T("Languages", "Langues", "اللغات"), [L2, L2, L3, L3, L3]),
    (T("Lead form, WhatsApp, catalogue download", "Formulaire, WhatsApp, téléchargement du catalogue", "الاستمارة، واتساب، تحميل الكتالوج"), [Y, Y, Y, Y, Y]),
    (T("Page per unit type (×9)", "Page par type de logement (×9)", "صفحة لكل نوع وحدة (9)"), [N_, Y, Y, Y, Y]),
    (T("Availability per unit", "Disponibilité par logement", "التوفر لكل وحدة"), [N_, TBL, TOW, TOW, TOW]),
    (T("Visit booking & reservation requests", "Visites & demandes de réservation", "حجز الزيارات وطلبات الحجز"), [N_, Y, Y, Y, Y]),
    (T("Admin panel", "Panneau d'administration", "لوحة الإدارة"), [N_, Y, Y, Y, Y]),
    (T("Parking & commercial-space modules", "Modules parking & commerces", "وحدتا الركن والمحلات"), [N_, N_, Y, Y, Y]),
    (T("Buyer accounts & CRM", "Comptes acheteurs & CRM", "حسابات المشترين وإدارة الزبائن"), [N_, N_, Y, Y, Y]),
    (T("Payment plan simulator & PDF forms", "Simulateur d'échéancier & fiches PDF", "محاكي الدفع واستمارات PDF"), [N_, N_, Y, Y, Y]),
    (T("Online deposit payment", "Acompte en ligne", "دفع العربون عبر الإنترنت"), [N_, N_, N_, Y, Y]),
    (T("Buyer portal & construction progress", "Espace acquéreur & avancement des travaux", "فضاء المشتري وتقدم الأشغال"), [N_, N_, N_, Y, Y]),
    (T("Sales dashboard & team roles", "Tableau de bord & rôles de l'équipe", "لوحة المبيعات وأدوار الفريق"), [N_, N_, N_, Y, Y]),
    (T("Mobile apps iOS + Android", "Applications iOS + Android", "تطبيقات iOS + Android"), [N_, N_, N_, N_, Y]),
    (T("Multi-project, e-signature, AI assistant", "Multi-projets, signature électronique, assistant IA", "تعدد المشاريع، التوقيع الإلكتروني، المساعد الذكي"), [N_, N_, N_, N_, Y]),
    (T("Free warranty after launch", "Garantie gratuite après lancement", "ضمان مجاني بعد الإطلاق"), [M1, M3, M3, M3, M6]),
]

SUGGESTIONS = [
    (T("Live availability builds urgency", "La disponibilité en direct crée l'urgence", "التوفر المباشر يخلق الإلحاح"),
     T("Showing which units are already reserved or sold, floor by floor, pushes hesitant buyers to decide and saves the sales team from answering the same question all day.",
       "Afficher, étage par étage, les logements déjà réservés ou vendus pousse les acheteurs hésitants à se décider et évite à l'équipe commerciale de répondre toute la journée à la même question.",
       "إظهار الوحدات المحجوزة أو المبيعة طابقًا بطابق يدفع المشترين المترددين إلى اتخاذ القرار، ويوفّر على فريق المبيعات الإجابة عن السؤال نفسه طوال اليوم.")),
    (T("A light, trackable catalogue", "Un catalogue léger et mesurable", "كتالوج خفيف وقابل للتتبع"),
     T("The current PDF catalogue is about 23 MB, heavy to send on WhatsApp. The website shows the same content instantly on any phone and tells you who looked at which unit.",
       "Le catalogue PDF actuel pèse environ 23 Mo, trop lourd pour WhatsApp. Le site affiche le même contenu instantanément sur tout téléphone et vous indique qui a consulté quel logement.",
       "يبلغ حجم الكتالوج الحالي بصيغة PDF حوالي 23 ميغابايت، وهو ثقيل للإرسال عبر واتساب. يعرض الموقع المحتوى نفسه فورًا على أي هاتف ويُعلمكم بمن اطّلع على أي وحدة.")),
    (T("Every visitor becomes a lead", "Chaque visiteur devient un prospect", "كل زائر يصبح زبونًا محتملًا"),
     T("Prices “on request” and the catalogue download ask for a name and phone number, so each interested person lands in your list instead of disappearing.",
       "Les prix « sur demande » et le téléchargement du catalogue demandent un nom et un numéro de téléphone : chaque personne intéressée rejoint votre liste au lieu de disparaître.",
       "الأسعار «عند الطلب» وتحميل الكتالوج يتطلبان الاسم ورقم الهاتف، فينضم كل مهتم إلى قائمتكم بدل أن يضيع.")),
    (T("Target the diaspora", "Cibler la diaspora", "استهداف الجالية"),
     T("Algerians living abroad are a strong market for sea-view property. French + English pages, WhatsApp contact, video-call visits and online deposits make buying from abroad easy.",
       "Les Algériens résidant à l'étranger sont un marché important pour l'immobilier avec vue sur mer. Des pages en français et en anglais, WhatsApp, des visites par appel vidéo et l'acompte en ligne facilitent l'achat à distance.",
       "الجزائريون المقيمون في الخارج سوق مهمة للعقارات المطلة على البحر. صفحات بالفرنسية والإنجليزية، وواتساب، وزيارات عبر مكالمات الفيديو، ودفع العربون عبر الإنترنت تسهّل الشراء عن بُعد.")),
    (T("Sell the commercial spaces separately", "Commercialiser les locaux à part", "تسويق المحلات التجارية بشكل منفصل"),
     T("1,213 m² of shops and mezzanine is a B2B product. A dedicated page for brands, franchises and investors reaches a different audience than apartment buyers.",
       "Les 1 213 m² de commerces et de mezzanine sont un produit B2B. Une page dédiée aux enseignes, franchises et investisseurs touche un public différent de celui des acheteurs de logements.",
       "تمثل مساحة 1,213 م² من المحلات والميزانين منتجًا موجهًا للشركات. صفحة مخصصة للعلامات التجارية والامتيازات والمستثمرين تصل إلى جمهور مختلف عن مشتري الشقق.")),
    (T("Put the hotel-style services first", "Mettre en avant les services hôteliers", "إبراز الخدمات الفندقية"),
     T("The 943 m² services floor (indoor pool, SPA, restaurant, prayer room) and the duplexes with private pools are what sets El Charika apart. They deserve their own pages, photos and video.",
       "L'étage de services de 943 m² (piscine couverte, SPA, restaurant, salle de prière) et les duplex avec piscine privée distinguent El Charika. Ils méritent leurs propres pages, photos et vidéos.",
       "طابق الخدمات بمساحة 943 م² (مسبح مغطى، سبا، مطعم، قاعة صلاة) والدوبلكس بمسابح خاصة هي ما يميّز El Charika، وتستحق صفحاتها وصورها وفيديوهاتها الخاصة.")),
    (T("Show construction progress", "Montrer l'avancement des travaux", "عرض تقدم الأشغال"),
     T("For a sale on plan, regular photo and video updates build trust with buyers and reassure new prospects that the project is moving.",
       "Pour une vente sur plan, des mises à jour régulières en photos et vidéos renforcent la confiance des acquéreurs et rassurent les nouveaux prospects sur l'avancement du projet.",
       "في البيع على التصاميم، التحديثات المنتظمة بالصور والفيديو تعزز ثقة المشترين وتطمئن الزبائن الجدد بأن المشروع يتقدم.")),
    (T("Measure every advertising dinar", "Mesurer chaque dinar publicitaire", "قياس كل دينار يُصرف على الإعلان"),
     T("Meta Pixel and Google Analytics from day one show which Facebook / Instagram ads bring real buyers, and allow retargeting of people who visited a unit page.",
       "Le Pixel Meta et Google Analytics dès le premier jour montrent quelles publicités Facebook / Instagram amènent de vrais acheteurs, et permettent de recibler les personnes qui ont consulté un logement.",
       "يُظهر Meta Pixel وGoogle Analytics منذ اليوم الأول أيّ إعلانات فيسبوك وإنستغرام تجلب مشترين حقيقيين، ويتيحان إعادة استهداف من زاروا صفحة وحدة.")),
    (T("Ready for the next projects", "Prêt pour vos prochains projets", "جاهز لمشاريعكم القادمة"),
     T("Built on a scalable base, the same platform can host future MOSTALIFE residences, so the investment keeps paying off.",
       "Construite sur une base évolutive, la même plateforme pourra accueillir les futures résidences MOSTALIFE : l'investissement continue de rapporter.",
       "بفضل بنيتها القابلة للتوسع، يمكن للمنصة نفسها استضافة إقامات MOSTALIFE المستقبلية، فيستمر الاستثمار في تحقيق العائد.")),
    (T("Your own domain and email", "Votre nom de domaine et vos e-mails", "نطاق وبريد إلكتروني خاص بكم"),
     T("A domain such as mostalife.com or mostalife.dz (subject to availability) with professional email addresses strengthens trust with buyers and banks.",
       "Un domaine comme mostalife.com ou mostalife.dz (sous réserve de disponibilité) avec des adresses e-mail professionnelles renforce la confiance des acheteurs et des banques.",
       "نطاق مثل mostalife.com أو mostalife.dz (حسب التوفر) مع عناوين بريد إلكتروني مهنية يعزز ثقة المشترين والبنوك.")),
]

# (label, usd or None for "on quote", unit key or None)
ADDONS = [
    (T("Extra language", "Langue supplémentaire", "لغة إضافية"), 50, None),
    (T("Extra landing page for an ad campaign", "Page d'atterrissage pour une campagne", "صفحة هبوط إضافية لحملة إعلانية"), 80, None),
    (T("Light WhatsApp catalogue (PDF under 5 MB)", "Catalogue allégé pour WhatsApp (PDF de moins de 5 Mo)", "كتالوج خفيف لواتساب (PDF أقل من 5 ميغابايت)"), 30, None),
    (T("Teaser video from the 3D renders (30–60 s, Reels / TikTok)", "Vidéo teaser à partir des rendus 3D (30–60 s, Reels / TikTok)", "فيديو تشويقي من الصور ثلاثية الأبعاد (30–60 ثانية، Reels / TikTok)"), 120, None),
    (T("Social media launch kit (10 posts + 10 stories)", "Kit réseaux sociaux de lancement (10 posts + 10 stories)", "حزمة إطلاق لمواقع التواصل (10 منشورات + 10 قصص)"), 150, None),
    (T("Facebook / Instagram ads setup", "Mise en place des publicités Facebook / Instagram", "إعداد إعلانات فيسبوك / إنستغرام"), 100, None),
    (T("Ads management (ad budget not included)", "Gestion des publicités (budget publicitaire non inclus)", "إدارة الإعلانات (ميزانية الإعلان غير مشمولة)"), 150, "month"),
    (T("Google Business Profile & Google Maps listing", "Fiche Google Business & Google Maps", "ملف Google Business والظهور على خرائط Google"), 30, None),
    (T("Drone video of the site / construction", "Vidéo drone du site / chantier", "فيديو بالدرون للموقع / الورشة"), None, None),
    (T("360° shooting of the show apartment", "Tournage 360° de l'appartement témoin", "تصوير 360° للشقة النموذجية"), None, None),
    (T("Extra work outside the agreed scope", "Travaux hors périmètre convenu", "أعمال خارج النطاق المتفق عليه"), 15, "hour"),
]

MAINTENANCE = [
    (T("Basic", "Basique", "الأساسية"), 20, [
        T("Hosting monitoring & security updates", "Surveillance de l'hébergement & mises à jour de sécurité", "مراقبة الاستضافة وتحديثات الأمان"),
        T("Weekly backups", "Sauvegardes hebdomadaires", "نسخ احتياطي أسبوعي"),
        T("1 h of changes / month", "1 h de modifications / mois", "ساعة تعديلات شهريًا"),
    ]),
    (T("Standard", "Standard", "القياسية"), 45, [
        T("Everything in Basic", "Tout le contenu de Basique", "كل ما في الأساسية"),
        T("Daily backups", "Sauvegardes quotidiennes", "نسخ احتياطي يومي"),
        T("We update availability & prices for you", "Nous mettons à jour disponibilités et prix pour vous", "نحدّث التوفر والأسعار نيابة عنكم"),
        T("3 h of changes / month", "3 h de modifications / mois", "3 ساعات تعديلات شهريًا"),
    ]),
    (T("Premium", "Premium", "المتميزة"), 90, [
        T("Everything in Standard", "Tout le contenu de Standard", "كل ما في القياسية"),
        T("Priority WhatsApp support", "Support prioritaire sur WhatsApp", "دعم ذو أولوية عبر واتساب"),
        T("Monthly traffic & leads report", "Rapport mensuel trafic & prospects", "تقرير شهري عن الزيارات والزبائن"),
        T("6 h of changes / month", "6 h de modifications / mois", "6 ساعات تعديلات شهريًا"),
    ]),
]

S = {  # all other static text
    "title": T("Website Quote — MOSTALIFE · Résidence El Charika", "Devis site web — MOSTALIFE · Résidence El Charika", "عرض سعر موقع إلكتروني — MOSTALIFE · إقامة El Charika"),
    "company": T("[Your Company Name]", "[Nom de votre société]", "[اسم شركتكم]"),
    "addr": T("[Address] · [City], Algeria", "[Adresse] · [Ville], Algérie", "[العنوان] · [المدينة]، الجزائر"),
    "contact": T("[Phone] · [Email] · [Website]", "[Téléphone] · [E-mail] · [Site web]", "[الهاتف] · [البريد الإلكتروني] · [الموقع]"),
    "ids": T("RC: [ ] · NIF: [ ]", "RC : [ ] · NIF : [ ]", "السجل التجاري: [ ] · رقم التعريف الجبائي: [ ]"),
    "eyebrow": T("Quote", "Devis", "عرض سعر"),
    "date": T("Date", "Date", "التاريخ"),
    "date_l": T("Date:", "Date :", "التاريخ:"),
    "valid": T("Valid until", "Valable jusqu'au", "صالح إلى غاية"),
    "currency": T("Currency", "Devise", "العملة"),
    "currency_v": T("USD · DZD", "USD · DA", "دولار · دينار"),
    "h1": T("A website that sells<br>Résidence El Charika", "Un site web qui vend<br>la Résidence El Charika", "موقع إلكتروني يبيع<br>إقامة El Charika"),
    "subtitle": T(
        "Five plans, from $600 to $10,000, to showcase, reserve and sell the apartments, duplexes, commercial spaces and parking of MOSTALIFE’s seafront residence in Mostaganem.",
        "Cinq formules, de 600 $ à 10 000 $, pour présenter, réserver et vendre les appartements, duplex, locaux commerciaux et places de parking de la résidence en bord de mer de MOSTALIFE à Mostaganem.",
        "خمس باقات، من 600 إلى 10,000 دولار، لعرض وحجز وبيع الشقق والدوبلكس والمحلات التجارية وأماكن الركن في إقامة MOSTALIFE المطلة على البحر في مستغانم."),
    "for": T("PREPARED FOR", "PRÉPARÉ POUR", "مُعَدّ لـ"),
    "client_name": T("MOSTALIFE — Promotion Immobilière", "MOSTALIFE — Promotion Immobilière", "MOSTALIFE — الترقية العقارية"),
    "client": T("Client", "Client", "العميل"),
    "client_addr": T("[Client address], Mostaganem", "[Adresse du client], Mostaganem", "[عنوان العميل]، مستغانم"),
    "client_contact": T("Contact: [Name] · [Phone] · [Email]", "Contact : [Nom] · [Téléphone] · [E-mail]", "جهة الاتصال: [الاسم] · [الهاتف] · [البريد الإلكتروني]"),
    "project": T("Project", "Projet", "المشروع"),
    "project_name": T("Résidence El Charika", "Résidence El Charika", "إقامة El Charika"),
    "project_desc": T(
        "Seafront residence on the RN11, Mostaganem: F3 & F4 apartments (95.70–128.10 m²), 4 duplexes with private pools, 1,213 m² of commercial space, 943 m² services floor, 67 parking spaces.",
        "Résidence en bord de mer sur la RN11, Mostaganem : appartements F3 et F4 (95,70 à 128,10 m²), 4 duplex avec piscine privée, 1 213 m² d'espaces commerciaux, étage de services de 943 m², 67 places de stationnement.",
        "إقامة مطلة على البحر على الطريق الوطني رقم 11، مستغانم: شقق F3 وF4 (من 95.70 إلى 128.10 م²)، 4 دوبلكس بمسابح خاصة، 1,213 م² من المساحات التجارية، طابق خدمات بمساحة 943 م²، 67 مكان ركن."),
    "note": T(
        "Prices excluding taxes (HT), in US dollars and Algerian dinars at **1 USD = {rate} DZD** (rate fixed on signature). Each plan includes **everything in the previous plan**.",
        "Prix hors taxes (HT), en dollars américains et en dinars algériens au taux de **1 USD = {rate} DA** (taux fixé à la signature). Chaque formule inclut **tout le contenu de la formule précédente**.",
        "الأسعار خارج الرسوم (HT)، بالدولار الأمريكي وبالدينار الجزائري بسعر صرف **1 دولار = {rate} دج** (يُثبَّت سعر الصرف عند التوقيع). كل باقة تشمل **كل ما في الباقة السابقة**."),
    "s1": T("Plans at a glance", "Les formules en un coup d'œil", "الباقات في لمحة"),
    "s2": T("Compare the plans", "Comparatif des formules", "مقارنة الباقات"),
    "s8": T("Our suggestions for Résidence El Charika", "Nos suggestions pour la Résidence El Charika", "اقتراحاتنا لإقامة El Charika"),
    "s8_lead": T("Ideas from studying your catalogue, to help the website sell faster. All of them fit into the plans above.",
                 "Des idées issues de l'étude de votre catalogue, pour que le site vende plus vite. Toutes s'intègrent aux formules ci-dessus.",
                 "أفكار استخلصناها من دراسة كتالوجكم لتسريع البيع عبر الموقع، وكلها مدمجة في الباقات أعلاه."),
    "s9": T("Marketing & extra services", "Marketing & services complémentaires", "التسويق والخدمات الإضافية"),
    "s9_lead": T("Optional, can be added to any plan.", "En option, compatibles avec toutes les formules.", "اختيارية، ويمكن إضافتها إلى أي باقة."),
    "s10": T("Maintenance plans", "Formules de maintenance", "باقات الصيانة"),
    "yearly": T("Yearly running costs (paid to providers)", "Coûts annuels (payés aux fournisseurs)", "التكاليف السنوية (تُدفع للمزودين)"),
    "yearly_items": [
        T("Domain name: ≈ {m:15} / year (.com) — .dz on quote", "Nom de domaine : ≈ {m:15} / an (.com) — .dz sur devis", "اسم النطاق: ≈ {m:15} سنويًا (.com) — .dz حسب الطلب"),
        T("Hosting: {m:60} / year (Plans 1–2) to {m:300} / year (Plans 4–5)", "Hébergement : {m:60} / an (formules 1–2) à {m:300} / an (formules 4–5)", "الاستضافة: من {m:60} سنويًا (الباقتان 1–2) إلى {m:300} سنويًا (الباقتان 4–5)"),
        T("SSL certificate: free", "Certificat SSL : gratuit", "شهادة SSL: مجانية"),
        T("Apple + Google developer accounts (Plan 5): ≈ {m:125} / year", "Comptes développeur Apple + Google (formule 5) : ≈ {m:125} / an", "حسابات مطوري Apple وGoogle (الباقة 5): ≈ {m:125} سنويًا"),
    ],
    "ppu": T("Pay-per-use (billed directly to the client)", "Coûts à l'usage (facturés directement au client)", "تكاليف حسب الاستخدام (تُفوتر مباشرة للعميل)"),
    "ppu_items": [
        T("Payment fees: per the gateway contract (SATIM / Chargily, international gateway)", "Frais de paiement : selon le contrat de la passerelle (SATIM / Chargily, passerelle internationale)", "رسوم الدفع: حسب عقد بوابة الدفع (SATIM / Chargily، بوابة دولية)"),
        T("SMS: ≈ {r:0.02:0.05} per message", "SMS : ≈ {r:0.02:0.05} par message", "الرسائل القصيرة: ≈ {r:0.02:0.05} للرسالة"),
        T("WhatsApp Business API: per conversation (Meta pricing)", "WhatsApp Business API : par conversation (tarifs Meta)", "WhatsApp Business API: حسب المحادثة (تسعيرة Meta)"),
        T("AI assistant: ≈ {r:20:100} / month depending on traffic", "Assistant IA : ≈ {r:20:100} / mois selon le trafic", "المساعد الذكي: ≈ {r:20:100} شهريًا حسب حجم الزيارات"),
    ],
    "s11": T("Timeline & payment terms", "Planning & modalités de paiement", "الجدول الزمني وشروط الدفع"),
    "timeline": T("Timeline — Plan 3 Business (6 weeks)", "Planning — Formule 3 Business (6 semaines)", "الجدول الزمني — باقة الأعمال 3 (6 أسابيع)"),
    "timeline_rows": [
        ("1", T("Kick-off, unit list, content collection", "Lancement, liste des logements, collecte des contenus", "الانطلاق، قائمة الوحدات، جمع المحتوى")),
        ("2", T("Design mockups in MOSTALIFE identity", "Maquettes graphiques à l'identité MOSTALIFE", "النماذج التصميمية بهوية MOSTALIFE")),
        ("3–4", T("Development: pages, building selector, admin", "Développement : pages, sélecteur de l'immeuble, administration", "التطوير: الصفحات، مُحدِّد العمارة، لوحة الإدارة")),
        ("5", T("Parking, commercial, CRM, PDF, notifications", "Parking, commerces, CRM, PDF, notifications", "الركن، المحلات، إدارة الزبائن، PDF، الإشعارات")),
        ("6", T("Testing, training, launch", "Tests, formation, mise en ligne", "الاختبار، التدريب، الإطلاق")),
    ],
    "pay": T("Payment schedule", "Échéancier de paiement", "جدول الدفع"),
    "pay_rows": [
        (T("Plans 1–2: on signature", "Formules 1–2 : à la signature", "الباقتان 1–2: عند التوقيع"), "50"),
        (T("Plans 1–2: on launch", "Formules 1–2 : à la mise en ligne", "الباقتان 1–2: عند الإطلاق"), "50"),
        (T("Plans 3–5: on signature", "Formules 3–5 : à la signature", "الباقات 3–5: عند التوقيع"), "30"),
        (T("Plans 3–5: design approved", "Formules 3–5 : validation des maquettes", "الباقات 3–5: عند المصادقة على التصميم"), "30"),
        (T("Plans 3–5: test version delivered", "Formules 3–5 : livraison de la version de test", "الباقات 3–5: عند تسليم النسخة التجريبية"), "30"),
        (T("Plans 3–5: launch", "Formules 3–5 : mise en ligne", "الباقات 3–5: عند الإطلاق"), "10"),
    ],
    "provides": T("MOSTALIFE provides", "MOSTALIFE fournit", "تقدم MOSTALIFE"),
    "provides_items": [
        T("Logo in vector format (AI, SVG or PDF)", "Logo en format vectoriel (AI, SVG ou PDF)", "الشعار بصيغة متجهة (AI أو SVG أو PDF)"),
        T("Full list of units: number, floor, type, status, price (or “on request”)", "Liste complète des logements : numéro, étage, type, statut, prix (ou « sur demande »)", "القائمة الكاملة للوحدات: الرقم، الطابق، النوع، الحالة، السعر (أو «عند الطلب»)"),
        T("HD 3D renders and plans (from the catalogue)", "Rendus 3D et plans en HD (issus du catalogue)", "الصور ثلاثية الأبعاد والمخططات بدقة عالية (من الكتالوج)"),
        T("Payment terms for sale on plan (down payment, installments)", "Conditions de paiement de la vente sur plan (apport, échéances)", "شروط الدفع للبيع على التصاميم (الدفعة الأولى، الأقساط)"),
        T("Legal info: RC, NIF, terms of sale, privacy policy", "Informations légales : RC, NIF, conditions de vente, politique de confidentialité", "المعلومات القانونية: السجل التجاري، رقم التعريف الجبائي، شروط البيع، سياسة الخصوصية"),
        T("Payment gateway merchant account (Plans 4–5)", "Compte marchand de paiement (formules 4–5)", "حساب تاجر لدى بوابة الدفع (الباقتان 4–5)"),
        T("One contact person to validate each step", "Un interlocuteur unique pour valider chaque étape", "شخص واحد للتواصل والمصادقة على كل مرحلة"),
    ],
    "guar": T("Guarantees & conditions", "Garanties & conditions", "الضمانات والشروط"),
    "guar_items": [
        T("Free bug fixes after launch: 1 month (Plan 1), 3 months (Plans 2–4), 6 months (Plan 5)", "Correction gratuite des bugs après lancement : 1 mois (formule 1), 3 mois (formules 2–4), 6 mois (formule 5)", "تصحيح مجاني للأعطال بعد الإطلاق: شهر (الباقة 1)، 3 أشهر (الباقات 2–4)، 6 أشهر (الباقة 5)"),
        T("Website, domain and content belong to MOSTALIFE after full payment", "Le site, le domaine et les contenus appartiennent à MOSTALIFE après paiement complet", "الموقع والنطاق والمحتوى ملك لـ MOSTALIFE بعد الدفع الكامل"),
        T("Changes outside the agreed scope: {m:15} / hour or quoted separately", "Modifications hors périmètre : {m:15} / heure ou sur devis", "التعديلات خارج النطاق المتفق عليه: {m:15} للساعة أو حسب عرض منفصل"),
        T("Not included: paid ads budget, third-party fees, legal drafting of contracts", "Non inclus : budget publicitaire, frais de tiers, rédaction juridique des contrats", "غير مشمول: ميزانية الإعلانات، رسوم الأطراف الثالثة، الصياغة القانونية للعقود"),
    ],
    "s12": T("Launch offer", "Offre de lancement", "عرض الإطلاق"),
    "bonus_t": T("For a signature before [date]", "Pour toute signature avant le [date]", "عند التوقيع قبل [التاريخ]"),
    "bonus": [
        T("**Free domain name & hosting for the first year** (Plans 2–5)", "**Nom de domaine & hébergement offerts la première année** (formules 2–5)", "**اسم النطاق والاستضافة مجانًا للسنة الأولى** (الباقات 2–5)"),
        T("**1 month of Standard maintenance free**", "**1 mois de maintenance Standard offert**", "**شهر من الصيانة القياسية مجانًا**"),
        T("**Light WhatsApp version of the catalogue** (PDF under 5 MB) free", "**Version allégée du catalogue pour WhatsApp** (PDF de moins de 5 Mo) offerte", "**نسخة خفيفة من الكتالوج لواتساب** (PDF أقل من 5 ميغابايت) مجانًا"),
        T("**Upgrade credit:** 100% of the amount paid is deducted if MOSTALIFE moves to a higher plan within 6 months", "**Crédit de montée en gamme :** 100 % du montant payé est déduit si MOSTALIFE passe à une formule supérieure dans les 6 mois", "**رصيد الترقية:** يُخصم 100% من المبلغ المدفوع إذا انتقلت MOSTALIFE إلى باقة أعلى خلال 6 أشهر"),
    ],
    "s13": T("Acceptance — “Bon pour accord”", "Bon pour accord", "الموافقة على العرض"),
    "selected": T("Selected plan:", "Formule choisie :", "الباقة المختارة:"),
    "options": T("Options:", "Options :", "الخيارات:"),
    "for_provider": T("For the provider", "Pour le prestataire", "عن مقدم الخدمة"),
    "for_client": T("For the client", "Pour le client", "عن العميل"),
    "name": T("Name:", "Nom :", "الاسم:"),
    "sign": T("Signature & stamp:", "Signature et cachet :", "الإمضاء والختم:"),
    "footer": T("[Your Company Name] · [Address] · [Phone] · [Email] — Quote N° DEV-2026-002 — Prices excluding taxes (HT).",
                "[Nom de votre société] · [Adresse] · [Téléphone] · [E-mail] — Devis N° DEV-2026-002 — Prix hors taxes (HT).",
                "[اسم شركتكم] · [العنوان] · [الهاتف] · [البريد الإلكتروني] — عرض السعر رقم DEV-2026-002 — الأسعار خارج الرسوم (HT)."),
}

PCT = {"en": "{}%", "fr": "{} %", "ar": "{}%"}


# ---------------------------------------------------------------- render
def pname(p, lang):
    return f'{t(W["plan"], lang)} {p["key"]} — {t(p["name"], lang)}'


def plan_cards(lang):
    out = []
    for p in PLANS:
        feats = "".join(f"<li>{t(c, lang)}</li>" for c in p["cards"])
        rec = " featured" if p.get("recommended") else ""
        badge = f'<span class="badge">{t(W["recommended"], lang)}</span>' if p.get("recommended") else ""
        out.append(f'''
      <div class="card{rec}">{badge}
        <div class="tier">{t(W["plan"], lang)} {p["key"]}</div>
        <div class="cname">{t(p["name"], lang)}</div>
        <div class="csub">{t(p["sub"], lang)}</div>
        <div class="price">{U(p["price"], lang)}</div>
        <div class="cdzd">≈ {D(p["price"], lang)}</div>
        <div class="time">{t(p["time"], lang)}</div>
        <ul>{feats}</ul>
        <div class="target">{t(p["target"], lang)}</div>
      </div>''')
    return "".join(out)


def matrix(lang):
    head = "".join(
        f'<th class="c">{t(p["name"], lang)}<br><span>{U(p["price"], lang)}</span><br><small>{D(p["price"], lang)}</small></th>'
        for p in PLANS)
    rows = []
    for label, vals in MATRIX:
        cells = []
        for v in vals:
            cls = " yes" if v is Y else (" no" if v is N_ else "")
            cells.append(f'<td class="c{cls}">{t(v, lang)}</td>')
        rows.append(f'<tr><td class="feat">{t(label, lang)}</td>{"".join(cells)}</tr>')
    return f'''
    <div class="table-wrap">
    <table class="t matrix">
      <thead><tr><th>{t(W["capability"], lang)}</th>{head}</tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
    </div>'''


def plan_section(i, p, lang):
    rows = []
    if p["base"]:
        pp = PLANS[i - 1]
        all_feat = fmt(W["all_feat"][lang].format(pp["name"][lang]), lang)
        rows.append(f'<tr class="base"><td class="id">—</td><td class="feat">{pname(pp, lang)}</td><td>{all_feat}</td>'
                    f'<td class="amt">{U(p["base"], lang)}</td><td class="amt">{D(p["base"], lang)}</td></tr>')
    for n, (name, det, price) in enumerate(p["features"], 1):
        if price:
            usd_c, dzd_c = U(price, lang), D(price, lang)
        else:
            usd_c = dzd_c = f'<span class="muted">{t(W["included"], lang)}</span>'
        rows.append(f'<tr><td class="id">{p["letter"]}{n}</td><td class="feat">{t(name, lang)}</td><td>{t(det, lang)}</td>'
                    f'<td class="amt">{usd_c}</td><td class="amt">{dzd_c}</td></tr>')
    note = f'<p class="excl">{t(p["not"], lang)}</p>' if p.get("not") else ""
    return f'''
    <h2 class="page-break"><span class="num">{i + 3:02d}</span>{pname(p, lang)} <em>{t(p["sub"], lang)}</em></h2>
    <div class="offer-head">
      <div class="desc">{t(p["desc"], lang)}</div>
      <div class="pill">{U(p["price"], lang)}<small>≈ {D(p["price"], lang)} · {t(p["time"], lang)}</small></div>
    </div>
    <div class="table-wrap">
    <table class="t">
      <thead><tr><th>#</th><th>{t(W["feature"], lang)}</th><th>{t(W["details"], lang)}</th><th class="amt">{t(W["price_usd"], lang)}</th><th class="amt">{t(W["price_dzd"], lang)}</th></tr></thead>
      <tbody>{"".join(rows)}</tbody>
      <tfoot><tr class="total"><td colspan="3" class="lbl">{t(W["total"], lang)} — {pname(p, lang)}</td><td class="amt">{U(p["price"], lang)}</td><td class="amt">{D(p["price"], lang)}</td></tr></tfoot>
    </table>
    </div>{note}'''


def addon_price(usd, unit, lang):
    if usd is None:
        return f'<span class="muted">{t(W["on_quote"], lang)}</span>'
    suffix = f" {t(W[unit], lang)}" if unit else ""
    return f'{U(usd, lang)}{suffix}<br><small class="dz">{D(usd, lang)}{suffix}</small>'


def addons(lang):
    half = (len(ADDONS) + 1) // 2
    left, right = ADDONS[:half], ADDONS[half:]
    rows = []
    for k in range(half):
        a = left[k]
        cells = f'<td>{t(a[0], lang)}</td><td class="amt">{addon_price(a[1], a[2], lang)}</td>'
        if k < len(right):
            b = right[k]
            cells += f'<td>{t(b[0], lang)}</td><td class="amt">{addon_price(b[1], b[2], lang)}</td>'
        else:
            cells += "<td></td><td></td>"
        rows.append(f"<tr>{cells}</tr>")
    hdr = f'<th>{t(W["service"], lang)}</th><th class="amt">{t(W["price"], lang)}</th>'
    return f'''
    <div class="table-wrap">
    <table class="t">
      <thead><tr>{hdr}{hdr}</tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
    </div>'''


def maintenance(lang):
    out = []
    for name, usd, items in MAINTENANCE:
        lis = "".join(f"<li>{t(x, lang)}</li>" for x in items)
        out.append(f'<div class="mplan"><div class="mname">{t(name, lang)}</div>'
                   f'<div class="mprice">{U(usd, lang)}<span> {t(W["month"], lang)}</span></div>'
                   f'<div class="mdzd">≈ {D(usd, lang)} {t(W["month"], lang)}</div><ul>{lis}</ul></div>')
    return "".join(out)


def ul(items, lang):
    return "<ul>" + "".join(f"<li>{t(x, lang)}</li>" for x in items) + "</ul>"


def render_doc(lang):
    s = lambda k: t(S[k], lang)
    sugs = "".join(
        f'<div class="sug"><div class="sn">{i:02d}</div><div><h4>{t(a, lang)}</h4><p>{t(b, lang)}</p></div></div>'
        for i, (a, b) in enumerate(SUGGESTIONS, 1))
    tl = "".join(f'<tr><td class="id">{w}</td><td>{t(x, lang)}</td></tr>' for w, x in S["timeline_rows"])
    pay = "".join(f'<tr><td>{t(x, lang)}</td><td class="amt">{PCT[lang].format(v)}</td></tr>' for x, v in S["pay_rows"])
    sel = " &nbsp; ".join(f'☐ {p["key"]} {t(p["name"], lang)}' for p in PLANS)
    return f'''
<main class="doc" data-lang="{lang}" lang="{lang}" dir="{DIR[lang]}">
  <header class="hero">
    <div class="hero-text">
      <div class="hero-top">
        <div class="provider">
          <div class="logo">LOGO</div>
          <div class="name">{s("company")}</div>
          <div class="small">{s("addr")}</div>
          <div class="small">{s("contact")}</div>
          <div class="small">{s("ids")}</div>
        </div>
        <div class="quote-meta">
          <span class="eyebrow">{s("eyebrow")}</span>
          <div class="big"><bdi>N° DEV-2026-002</bdi></div>
          <table>
            <tr><td>{s("date")}</td><td><b><bdi>28/10/2026</bdi></b></td></tr>
            <tr><td>{s("valid")}</td><td><b><bdi>27/11/2026</bdi></b></td></tr>
            <tr><td>{s("currency")}</td><td><b>{s("currency_v")}</b></td></tr>
          </table>
        </div>
      </div>
      <h1>{S["h1"][lang]}</h1>
      <p class="subtitle">{s("subtitle")}</p>
      <div class="for"><b>{s("for")}</b> &nbsp;{s("client_name")}</div>
    </div>
    <div class="hero-img" role="img" aria-label="Résidence El Charika"></div>
  </header>

  <div class="content">
    <section class="parties">
      <div class="party">
        <h4>{s("client")}</h4>
        <div class="pname">{s("client_name")}</div>
        <p>{s("client_addr")}</p>
        <p>{s("client_contact")}</p>
      </div>
      <div class="party">
        <h4>{s("project")}</h4>
        <div class="pname">{s("project_name")}</div>
        <p>{s("project_desc")}</p>
      </div>
    </section>

    <p class="note">{s("note")}</p>

    <h2><span class="num">01</span>{s("s1")}</h2>
    <div class="cards">{plan_cards(lang)}
    </div>

    <h2 class="page-break"><span class="num">02</span>{s("s2")}</h2>
    {matrix(lang)}

    {"".join(plan_section(i, p, lang) for i, p in enumerate(PLANS))}

    <h2 class="page-break"><span class="num">08</span>{s("s8")}</h2>
    <p class="lead">{s("s8_lead")}</p>
    <div class="sugs">{sugs}</div>

    <h2 class="page-break"><span class="num">09</span>{s("s9")}</h2>
    <p class="lead">{s("s9_lead")}</p>
    {addons(lang)}

    <h2><span class="num">10</span>{s("s10")}</h2>
    <div class="mplans">{maintenance(lang)}</div>
    <div class="two" style="margin-top:14px">
      <div class="box"><h3>{s("yearly")}</h3>{ul(S["yearly_items"], lang)}</div>
      <div class="box"><h3>{s("ppu")}</h3>{ul(S["ppu_items"], lang)}</div>
    </div>

    <h2 class="page-break"><span class="num">11</span>{s("s11")}</h2>
    <div class="two">
      <div class="box">
        <h3>{s("timeline")}</h3>
        <table class="t"><thead><tr><th>{t(W["week"], lang)}</th><th>{t(W["step"], lang)}</th></tr></thead><tbody>{tl}</tbody></table>
      </div>
      <div class="box">
        <h3>{s("pay")}</h3>
        <table class="t"><tbody>{pay}</tbody></table>
      </div>
    </div>
    <div class="two" style="margin-top:14px">
      <div class="box"><h3>{s("provides")}</h3>{ul(S["provides_items"], lang)}</div>
      <div class="box"><h3>{s("guar")}</h3>{ul(S["guar_items"], lang)}</div>
    </div>

    <h2 class="page-break"><span class="num">12</span>{s("s12")}</h2>
    <div class="bonus">
      <h3>{s("bonus_t")}</h3>
      {ul(S["bonus"], lang)}
    </div>

    <h2><span class="num">13</span>{s("s13")}</h2>
    <p class="lead">{s("selected")} {sel} &nbsp;— {s("options")} ______________________</p>
    <div class="signs">
      <div class="sign">
        <h4>{s("for_provider")}</h4>
        <p>{s("company")}</p>
        <div class="line">{s("name")}</div>
        <div class="line">{s("date_l")}</div>
        <div class="line">{s("sign")}</div>
      </div>
      <div class="sign">
        <h4>{s("for_client")}</h4>
        <p>{s("client_name")}</p>
        <div class="line">{s("name")}</div>
        <div class="line">{s("date_l")}</div>
        <div class="line">{s("sign")}</div>
      </div>
    </div>

    <div class="doc-footer">{s("footer")}</div>
  </div>
</main>'''


CSS = r"""
  /* ==========================================================
     TEMPLATE SETTINGS — brand colors (matched to the MOSTALIFE catalogue)
     ========================================================== */
  :root {
    --navy: #0f1d2e;
    --navy-2: #1b2f47;
    --gold: #b08a5a;
    --gold-soft: #f3ece0;
    --cream: #f6f1e8;
    --ink: #1a2230;
    --muted: #616b78;
    --line: #e4ded3;
    --bg: #ebe5da;
    --paper: #ffffff;
    --row-alt: #faf7f2;
    --red: #a8402f;
    --serif: "Cormorant Garamond", "Playfair Display", Georgia, "Times New Roman", serif;
    --sans: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  }
  * { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; }
  body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--sans); font-size: 14px; line-height: 1.5; }

  /* Arabic version */
  .doc[dir="rtl"] { --serif: "Amiri", "Noto Naskh Arabic", serif; --sans: "Tajawal", "Noto Sans Arabic", system-ui, sans-serif; font-family: var(--sans); font-size: 15px; }
  .doc[dir="rtl"] * { letter-spacing: 0 !important; }

  /* Only the selected language is shown (and printed) */
  .doc { display: none; }
  body[data-lang="fr"] .doc[data-lang="fr"],
  body[data-lang="ar"] .doc[data-lang="ar"],
  body[data-lang="en"] .doc[data-lang="en"] { display: block; }

  /* Toolbar (not printed) */
  .toolbar { position: sticky; top: 0; z-index: 10; display: flex; gap: 8px; justify-content: center; align-items: center; flex-wrap: wrap; padding: 10px 16px; background: rgba(15,29,46,.96); color: #fff; font-family: "Inter", "Tajawal", system-ui, sans-serif; }
  .toolbar button { font: inherit; font-weight: 600; font-size: 13px; padding: 8px 14px; border-radius: 6px; cursor: pointer; border: 1px solid rgba(255,255,255,.35); background: transparent; color: #fff; }
  .toolbar .langs { display: inline-flex; border: 1px solid rgba(255,255,255,.35); border-radius: 6px; overflow: hidden; }
  .toolbar .langs button { border: 0; border-radius: 0; padding: 8px 12px; }
  .toolbar .langs button[aria-pressed="true"] { background: var(--gold); }
  .toolbar button.primary { background: var(--gold); border-color: var(--gold); }
  .toolbar #editBtn[aria-pressed="true"] { background: #fff; color: var(--navy); }
  .toolbar label { font-size: 13px; display: inline-flex; align-items: center; gap: 6px; }
  .toolbar input { width: 76px; font: inherit; font-size: 13px; padding: 6px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,.35); background: rgba(255,255,255,.08); color: #fff; }
  .toolbar .hint { flex-basis: 100%; text-align: center; font-size: 12px; opacity: .75; }
  body.editing .doc *:hover { outline: 1px dashed var(--gold); outline-offset: 2px; }

  .doc { max-width: 1000px; margin: 24px auto; background: var(--paper); box-shadow: 0 2px 24px rgba(15,29,46,.12); border-radius: 10px; overflow: hidden; }
  .content { padding: 32px 40px 40px; }

  /* Header */
  .hero { display: grid; grid-template-columns: 1fr 230px; background: var(--navy); color: #fff; position: relative; }
  .hero::after { content: ""; position: absolute; inset-inline: 0; bottom: 0; height: 3px; background: var(--gold); }
  .hero-text { padding: 30px 40px; }
  .hero-img { background: center / cover no-repeat; min-height: 100%; background-image: url('data:image/jpeg;base64,__TOWER__'); }
  .hero-top { display: flex; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
  .provider .logo { width: 52px; height: 46px; border-radius: 8px; border: 1px solid var(--gold); color: var(--gold); display: grid; place-items: center; font-weight: 700; font-size: 11px; letter-spacing: .1em; margin-bottom: 8px; font-family: "Inter", sans-serif; }
  .provider .name { font-size: 16px; font-weight: 700; }
  .provider .small { font-size: 12px; opacity: .8; }
  .quote-meta { text-align: end; }
  .eyebrow { display: inline-block; font-size: 11px; font-weight: 600; letter-spacing: .22em; color: var(--gold); text-transform: uppercase; }
  .quote-meta .big { font-family: var(--serif); font-size: 26px; font-weight: 600; margin: 0 0 4px; }
  .quote-meta table { margin-inline-start: auto; border-collapse: collapse; font-size: 12.5px; }
  .quote-meta td { padding-block: 1px; padding-inline: 12px 0; }
  .quote-meta td:first-child { opacity: .7; }
  .hero h1 { font-family: var(--serif); font-weight: 500; font-size: 38px; line-height: 1.15; margin: 26px 0 6px; }
  .hero .subtitle { margin: 0; opacity: .85; font-size: 14px; max-width: 540px; }
  .hero .for { margin-top: 18px; font-size: 12.5px; opacity: .85; }
  .hero .for b { color: var(--gold); font-weight: 600; letter-spacing: .04em; }

  .parties { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
  .party { border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; background: var(--row-alt); }
  .party h4 { margin: 0 0 6px; font-size: 10.5px; letter-spacing: .18em; text-transform: uppercase; color: var(--gold); }
  .party .pname { font-family: var(--serif); font-weight: 600; font-size: 19px; }
  .party p { margin: 2px 0; color: var(--muted); font-size: 13px; }

  .note { background: var(--gold-soft); border-inline-start: 3px solid var(--gold); padding: 10px 14px; border-radius: 6px; font-size: 13px; color: #5b4527; margin: 0 0 20px; }

  h2 { font-family: var(--serif); font-weight: 600; font-size: 26px; margin: 38px 0 14px; color: var(--navy); display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; line-height: 1.25; break-after: avoid; page-break-after: avoid; }
  h2 .num { font-family: "Inter", sans-serif; flex: none; font-size: 12px; font-weight: 700; color: var(--gold); letter-spacing: .1em; border: 1px solid var(--gold); border-radius: 20px; padding: 2px 9px; align-self: center; }
  h2 em { font-style: italic; font-weight: 500; color: var(--gold); font-size: 21px; }
  .doc[dir="rtl"] h2 em { font-style: normal; }
  h3 { font-size: 15px; margin: 0 0 8px; color: var(--navy); }
  p.lead { color: var(--muted); margin: -6px 0 14px; }

  /* Plan cards */
  .cards { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
  .card { border: 1px solid var(--line); border-radius: 10px; padding: 16px 12px 12px; display: flex; flex-direction: column; position: relative; break-inside: avoid; page-break-inside: avoid; }
  .card.featured { border: 2px solid var(--gold); background: #fffcf6; }
  .card .badge { position: absolute; top: -10px; inset-inline-start: 12px; background: var(--gold); color: #fff; font-size: 10px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; padding: 3px 8px; border-radius: 20px; }
  .card .tier { font-size: 10.5px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: var(--gold); }
  .card .cname { font-family: var(--serif); font-size: 22px; font-weight: 600; color: var(--navy); line-height: 1.15; margin-top: 2px; }
  .card .csub { font-size: 12px; color: var(--muted); min-height: 34px; line-height: 1.35; margin: 2px 0 8px; }
  .card .price { font-size: 25px; font-weight: 800; color: var(--ink); line-height: 1.1; }
  .card .cdzd { font-size: 12px; font-weight: 600; color: var(--gold); margin-top: 2px; }
  .card .time { font-size: 11.5px; color: var(--navy-2); font-weight: 600; margin: 2px 0 10px; }
  .card ul { margin: 0; padding: 0; list-style: none; font-size: 12px; }
  .card li { padding-block: 3px; padding-inline: 16px 0; position: relative; border-top: 1px solid var(--line); line-height: 1.35; }
  .card li::before { content: "✓"; position: absolute; inset-inline-start: 1px; color: var(--gold); font-weight: 700; }
  .card .target { margin-top: auto; padding-top: 10px; font-size: 11.5px; color: var(--muted); font-style: italic; }

  .offer-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; background: var(--cream); border: 1px solid var(--line); border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; break-after: avoid; page-break-after: avoid; }
  .offer-head .desc { color: var(--muted); font-size: 13px; max-width: 600px; }
  .pill { background: var(--navy); color: #fff; border-radius: 30px; padding: 6px 16px; font-weight: 700; white-space: nowrap; font-size: 15px; }
  .pill small { font-weight: 500; opacity: .8; margin-inline-start: 8px; font-size: 12px; }

  /* Tables */
  .table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  table.t { width: 100%; border-collapse: collapse; font-size: 13px; }
  table.t th { background: var(--navy); color: #fff; text-align: start; font-weight: 600; padding: 8px 10px; font-size: 12px; }
  table.t td { padding: 7px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
  table.t tbody tr:nth-child(even) td { background: var(--row-alt); }
  table.t tr { break-inside: avoid; page-break-inside: avoid; }
  table.t thead { display: table-header-group; }
  table.t .id { color: var(--gold); font-weight: 700; white-space: nowrap; width: 40px; }
  table.t .feat { font-weight: 600; width: 24%; }
  table.t .amt { text-align: end; white-space: nowrap; font-variant-numeric: tabular-nums; width: 96px; }
  table.t td.amt small { font-size: 11px; }
  .muted, .dz { color: var(--muted); }
  table.t tr.base td { font-style: italic; color: var(--muted); }
  table.t tfoot td { border-bottom: none; padding: 9px 10px 6px; font-variant-numeric: tabular-nums; }
  table.t tfoot .lbl { text-align: end; }
  table.t tfoot tr.total td { font-weight: 800; font-size: 14.5px; color: var(--navy); border-top: 2px solid var(--navy); }
  table.matrix th.c { text-align: center; font-size: 11.5px; }
  table.matrix th.c span { color: var(--gold); font-weight: 700; }
  table.matrix th.c small { font-weight: 500; opacity: .75; font-size: 10.5px; }
  table.matrix td.c { text-align: center; font-size: 12px; }
  table.matrix td.yes { color: var(--gold); font-weight: 700; font-size: 14px; }
  table.matrix td.no { color: #c3bcb0; }
  table.matrix .feat { width: 28%; }
  .excl { font-size: 12.5px; color: var(--muted); margin: 8px 0 0; }
  .excl b { color: var(--red); }

  /* Suggestions */
  .sugs { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 18px; }
  .sug { display: grid; grid-template-columns: 38px 1fr; gap: 10px; padding: 10px 0; border-top: 1px solid var(--line); break-inside: avoid; page-break-inside: avoid; }
  .sug .sn { font-family: "Cormorant Garamond", Georgia, serif; font-size: 26px; color: var(--gold); line-height: 1; }
  .sug h4 { margin: 0 0 3px; font-size: 14px; color: var(--navy); }
  .sug p { margin: 0; font-size: 12.5px; color: var(--muted); }

  .two { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  .box { border: 1px solid var(--line); border-radius: 8px; padding: 14px 18px; break-inside: avoid; page-break-inside: avoid; }
  .box ul, .bonus ul { margin: 0; padding-inline-start: 18px; }
  .box li, .bonus li { margin: 3px 0; }

  .mplans { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .mplan { border: 1px solid var(--line); border-radius: 8px; padding: 12px 14px; break-inside: avoid; page-break-inside: avoid; }
  .mname { font-family: var(--serif); font-size: 19px; font-weight: 600; color: var(--navy); }
  .mprice { font-size: 20px; font-weight: 800; }
  .mprice span { font-size: 12px; font-weight: 500; color: var(--muted); }
  .mdzd { font-size: 12px; color: var(--gold); font-weight: 600; margin-bottom: 6px; }
  .mplan ul { margin: 0; padding-inline-start: 16px; font-size: 12.5px; }

  .bonus { border: 2px dashed var(--gold); border-radius: 10px; padding: 14px 18px; background: #fffcf6; break-inside: avoid; page-break-inside: avoid; }
  .bonus h3 { font-family: var(--serif); font-size: 22px; font-weight: 600; margin-bottom: 6px; }

  .signs { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 14px; break-inside: avoid; page-break-inside: avoid; }
  .sign { border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; }
  .sign h4 { margin: 0 0 4px; font-size: 13px; color: var(--navy); }
  .sign p { margin: 0 0 6px; font-size: 12px; color: var(--muted); }
  .sign .line { border-bottom: 1px dotted #a39b8e; height: 26px; margin-top: 4px; font-size: 12px; color: var(--muted); }

  .doc-footer { margin-top: 28px; padding-top: 12px; border-top: 1px solid var(--line); font-size: 11.5px; color: var(--muted); text-align: center; }

  @media (max-width: 900px) { .cards { grid-template-columns: repeat(3, 1fr); } }
  @media (max-width: 680px) {
    .doc { margin: 0; border-radius: 0; }
    .content { padding: 20px 16px 28px; }
    .hero { grid-template-columns: 1fr; }
    .hero-img { min-height: 220px; order: -1; }
    .hero-text { padding: 22px 16px; }
    .quote-meta { text-align: start; }
    .quote-meta table { margin-inline-start: 0; }
    .quote-meta td { padding-inline: 0 12px; }
    .hero h1 { font-size: 30px; }
    .parties, .two, .signs, .sugs, .mplans { grid-template-columns: 1fr; }
    .cards { grid-template-columns: 1fr 1fr; }
    table.t { min-width: 600px; }
    .toolbar .hint { display: none; }
  }
  @media (max-width: 420px) { .cards { grid-template-columns: 1fr; } }

  @page { size: A4; margin: 12mm 11mm 13mm; }
  @media print {
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    body { background: #fff; font-size: 11.5px; }
    .doc[dir="rtl"] { font-size: 12.5px; }
    .toolbar { display: none !important; }
    .doc { box-shadow: none; margin: 0; max-width: none; border-radius: 0; }
    .content { padding: 16px 2px 0; }
    .hero { grid-template-columns: 1fr 170px; }
    .hero-text { padding: 16px 20px; }
    .hero h1 { font-size: 26px; margin-top: 10px; }
    .party p { font-size: 11.5px; }
    .hero .subtitle { font-size: 12px; }
    .quote-meta .big { font-size: 21px; }
    .parties { margin-bottom: 12px; }
    .party { padding: 9px 12px; }
    .note { margin-bottom: 4px; padding: 7px 12px; font-size: 11px; }
    h2 { font-size: 22px; margin: 18px 0 10px; }
    h2 em { font-size: 17px; }
    .cards { grid-template-columns: repeat(5, 1fr); gap: 6px; }
    .card { padding: 13px 8px 9px; }
    .card .cname { font-size: 18px; }
    .card .csub { font-size: 10.5px; min-height: 28px; }
    .card .price { font-size: 19px; }
    .card .cdzd { font-size: 10.5px; }
    .card ul { font-size: 10px; }
    .card li { padding-block: 2px; padding-inline: 13px 0; }
    .card .target { display: none; }
    .parties, .two, .signs, .sugs { grid-template-columns: 1fr 1fr; }
    .mplans { grid-template-columns: repeat(3, 1fr); }
    table.t { font-size: 10.5px; min-width: 0; }
    table.t td { padding: 5px 7px; }
    .table-wrap { overflow: visible; }
    .page-break { break-before: page; page-break-before: always; }
    .sug { padding: 7px 0; }
    .sign .line { height: 22px; }
    .doc-footer { margin-top: 14px; padding-top: 8px; }
  }
""".replace("__TOWER__", TOWER)

JS = r"""
(function () {
  var UI = {
    fr: { edit: '✎ Modifier le texte', done: '✓ Terminer', print: '⎙ Imprimer / PDF', rate: 'Taux : 1 $ =', hint: 'Choisissez la langue, cliquez sur « Modifier le texte » pour remplir les [crochets], ajustez le taux de change, puis imprimez.' },
    ar: { edit: '✎ تعديل النص', done: '✓ إنهاء', print: '⎙ طباعة / PDF', rate: 'سعر الصرف: 1 $ =', hint: 'اختر اللغة، ثم انقر على «تعديل النص» لملء الحقول بين [معقوفين]، واضبط سعر الصرف، ثم اطبع.' },
    en: { edit: '✎ Edit text', done: '✓ Done editing', print: '⎙ Print / Save as PDF', rate: 'Rate: 1 $ =', hint: 'Pick a language, click “Edit text” to fill in the [brackets], set the exchange rate, then print.' }
  };
  var CUR = { en: 'DZD', fr: 'DA', ar: 'دج' };
  var body = document.body, editBtn = document.getElementById('editBtn'), rateIn = document.getElementById('rate');
  var editing = false;

  function group(n, lang) {
    var s = Math.round(n).toLocaleString('en-US');
    return lang === 'fr' ? s.replace(/,/g, ' ') : s;
  }
  function dzdVal(usd, rate) {
    var v = usd * rate;
    return v >= 1000 ? Math.floor(v / 100 + 0.5) * 100 : Math.floor(v + 0.5);
  }
  function applyRate() {
    var rate = parseFloat(String(rateIn.value).replace(',', '.'));
    if (!(rate > 0)) return;
    document.querySelectorAll('.dzd[data-usd]').forEach(function (el) {
      var lang = el.closest('.doc').dataset.lang;
      var txt = group(dzdVal(parseFloat(el.dataset.usd), rate), lang);
      el.textContent = el.dataset.nounit ? txt : txt + ' ' + CUR[lang];
    });
    document.querySelectorAll('.rate-val').forEach(function (el) { el.textContent = String(rate); });
  }
  function setLang(lang) {
    if (!UI[lang]) lang = 'fr';
    body.dataset.lang = lang;
    document.documentElement.lang = lang;
    document.querySelectorAll('[data-setlang]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.setlang === lang));
    });
    editBtn.textContent = editing ? UI[lang].done : UI[lang].edit;
    document.getElementById('printBtn').textContent = UI[lang].print;
    document.getElementById('rateLbl').textContent = UI[lang].rate;
    document.getElementById('hint').textContent = UI[lang].hint;
    document.title = document.querySelector('.doc[data-lang="' + lang + '"]').dataset.title;
    if (location.hash !== '#' + lang) history.replaceState(null, '', '#' + lang);
  }
  function setEditing(on) {
    editing = on;
    editBtn.setAttribute('aria-pressed', String(on));
    document.querySelectorAll('.doc').forEach(function (d) { d.contentEditable = on ? 'true' : 'false'; });
    body.classList.toggle('editing', on);
    setLang(body.dataset.lang);
  }
  document.querySelectorAll('[data-setlang]').forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.dataset.setlang); });
  });
  editBtn.addEventListener('click', function () { setEditing(!editing); });
  document.getElementById('printBtn').addEventListener('click', function () { window.print(); });
  rateIn.addEventListener('input', applyRate);
  setLang((location.hash || '#fr').slice(1));
})();
"""

docs = "".join(render_doc(l).replace('<main class="doc"', f'<main class="doc" data-title="{html.escape(S["title"][l])}"', 1) for l in LANGS)

page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(S["title"]["fr"])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Inter:wght@400;500;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body data-lang="fr">

<div class="toolbar" role="toolbar" aria-label="Document actions">
  <div class="langs" role="group" aria-label="Language">
    <button type="button" data-setlang="fr" aria-pressed="true">FR</button>
    <button type="button" data-setlang="ar" aria-pressed="false">العربية</button>
    <button type="button" data-setlang="en" aria-pressed="false">EN</button>
  </div>
  <label><span id="rateLbl">Taux : 1 $ =</span> <input id="rate" type="number" min="1" step="0.01" value="{RATE}" inputmode="decimal"> DA</label>
  <button type="button" id="editBtn" aria-pressed="false">✎ Modifier le texte</button>
  <button type="button" class="primary" id="printBtn">⎙ Imprimer / PDF</button>
  <span class="hint" id="hint"></span>
</div>
{docs}
<script>{JS}</script>
</body>
</html>
"""

open(out_path, "w").write(page)
print("ok", [(p["name"]["en"], p["price"], dzd_val(p["price"])) for p in PLANS])
