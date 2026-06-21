/**
 * JuriThèque — Glossaire juridique marocain bilingue FR/AR
 * 150+ termes couvrant tous les domaines du droit marocain
 */

export const GLOSSAIRE = [
  // ── A ──────────────────────────────────────────────────────────────────
  {
    term: 'Acte authentique',
    ar: 'عقد رسمي',
    definition: 'Document établi par un officier public compétent (notaire, adoul) selon les formalités légales. Il fait foi jusqu\'à inscription en faux, contrairement à l\'acte sous seing privé.',
    domain: 'civil',
  },
  {
    term: 'Acte sous seing privé',
    ar: 'عقد عرفي',
    definition: 'Document rédigé et signé par les parties elles-mêmes, sans intervention d\'un officier public. Il a force probante mais peut être contesté, contrairement à l\'acte authentique.',
    domain: 'civil',
  },
  {
    term: 'Adoul',
    ar: 'عدول',
    definition: 'Officier ministériel marocain chargé d\'établir les actes juridiques selon le droit musulman (mariage, divorce, successions, ventes immobilières). L\'intervention de deux adouls est généralement requise.',
    domain: 'civil',
  },
  {
    term: 'Appel',
    ar: 'استئناف',
    definition: 'Voie de recours permettant à une partie insatisfaite d\'un jugement de première instance de saisir la juridiction supérieure (Cour d\'appel) pour qu\'elle réexamine l\'affaire en fait et en droit.',
    domain: 'civil',
  },
  {
    term: 'Arbitrage',
    ar: 'التحكيم',
    definition: 'Mode alternatif de règlement des litiges par lequel les parties confient la résolution de leur différend à un ou plusieurs arbitres privés, dont la décision (sentence arbitrale) est contraignante.',
    domain: 'commercial',
  },
  {
    term: 'Arrêté',
    ar: 'قرار إداري',
    definition: 'Acte réglementaire ou individuel émanant d\'une autorité administrative (ministre, wali, gouverneur, président de commune). Il est inférieur en hiérarchie au décret et à la loi.',
    domain: 'administratif',
  },
  {
    term: 'Assignation',
    ar: 'استدعاء / تبليغ',
    definition: 'Acte de procédure par lequel une partie cite l\'autre à comparaître devant une juridiction. Elle doit être signifiée dans les formes légales pour être valable.',
    domain: 'civil',
  },
  {
    term: 'Astreinte',
    ar: 'غرامة تهديدية',
    definition: 'Condamnation pécuniaire prononcée par un juge pour contraindre une partie à exécuter une décision, calculée par jour ou par infraction constatée.',
    domain: 'civil',
  },
  {
    term: 'Auto-entrepreneur',
    ar: 'المقاول الذاتي',
    definition: 'Statut juridique simplifié créé par la loi n°114-13, permettant d\'exercer une activité commerciale, artisanale ou de prestation de services avec une fiscalité allégée et des formalités réduites.',
    domain: 'commercial',
  },

  // ── B ──────────────────────────────────────────────────────────────────
  {
    term: 'Bail commercial',
    ar: 'إيجار تجاري',
    definition: 'Contrat de location portant sur un local à usage commercial ou industriel. Il bénéficie d\'une protection spéciale : le locataire a un droit au renouvellement et, en cas de refus, à une indemnité d\'éviction.',
    domain: 'commercial',
  },
  {
    term: 'Bail d\'habitation',
    ar: 'عقد كراء سكني',
    definition: 'Contrat par lequel un propriétaire met un logement à la disposition d\'un locataire moyennant un loyer. Régi par la loi n°67-12, il protège le locataire contre les expulsions abusives.',
    domain: 'civil',
  },
  {
    term: 'Bulletin Officiel',
    ar: 'الجريدة الرسمية',
    definition: 'Publication officielle de l\'État marocain qui assure la publicité des textes législatifs et réglementaires, des nominations, des décisions administratives et des avis. La publication au BO est une condition d\'entrée en vigueur de la plupart des textes.',
    domain: 'administratif',
  },

  // ── C ──────────────────────────────────────────────────────────────────
  {
    term: 'Capacité juridique',
    ar: 'الأهلية القانونية',
    definition: 'Aptitude d\'une personne à être titulaire de droits et à les exercer elle-même. Au Maroc, la majorité est fixée à 18 ans. En dessous, le mineur est représenté par son tuteur légal.',
    domain: 'civil',
  },
  {
    term: 'Cassation',
    ar: 'النقض',
    definition: 'Voie de recours extraordinaire portée devant la Cour de cassation (anciennement Cour suprême) qui contrôle uniquement la bonne application du droit, sans rejuger les faits.',
    domain: 'civil',
  },
  {
    term: 'Cautionnement',
    ar: 'كفالة',
    definition: 'Engagement par lequel une personne (caution) s\'oblige à payer la dette d\'un débiteur si celui-ci ne la paye pas. La caution peut être solidaire (appelée immédiatement) ou simple (appelée après poursuite du débiteur).',
    domain: 'commercial',
  },
  {
    term: 'Charte de l\'investissement',
    ar: 'ميثاق الاستثمار',
    definition: 'Texte fondamental (Loi-cadre 03-22 de 2022) fixant le régime général des investissements privés au Maroc. Elle garantit la liberté d\'investir, le libre transfert des capitaux et des bénéfices, et la protection contre la nationalisation sans indemnisation.',
    domain: 'commercial',
  },
  {
    term: 'Chèque sans provision',
    ar: 'شيك بدون مؤونة',
    definition: 'Chèque émis pour un montant supérieur au solde disponible sur le compte bancaire. C\'est une infraction pénale au Maroc pouvant entraîner une interdiction bancaire et des sanctions pénales.',
    domain: 'penal',
  },
  {
    term: 'Circulaire',
    ar: 'منشور',
    definition: 'Instruction émise par une autorité administrative supérieure à l\'intention des agents ou services placés sous son autorité. La circulaire interprète les textes sans créer de nouvelles règles de droit opposables aux tiers.',
    domain: 'administratif',
  },
  {
    term: 'CNDP',
    ar: 'اللجنة الوطنية لمراقبة حماية المعطيات ذات الطابع الشخصي',
    definition: 'Commission Nationale de contrôle de la protection des Données à caractère Personnel. Autorité indépendante marocaine chargée de veiller au respect de la loi 09-08 relative à la protection des données personnelles.',
    domain: 'numerique',
  },
  {
    term: 'Code de la famille (Moudawwana)',
    ar: 'مدونة الأسرة',
    definition: 'Loi n°70-03 régissant le droit de la famille marocain : mariage, divorce, filiation, garde des enfants, pension alimentaire et succession. Réformée en 2004, une nouvelle réforme est en discussion depuis 2025.',
    domain: 'civil',
  },
  {
    term: 'Compensation',
    ar: 'المقاصة',
    definition: 'Mode d\'extinction d\'une obligation par lequel deux dettes réciproques s\'éteignent mutuellement à concurrence de leur montant respectif. Permet d\'éviter des paiements croisés inutiles.',
    domain: 'civil',
  },
  {
    term: 'Conciliation',
    ar: 'الصلح',
    definition: 'Mode amiable de règlement des litiges par lequel les parties, assistées ou non d\'un tiers, trouvent elles-mêmes un accord. Obligatoire avant certaines procédures judiciaires au Maroc (notamment en droit du travail).',
    domain: 'civil',
  },
  {
    term: 'Conservation foncière',
    ar: 'المحافظة العقارية',
    definition: 'Service public chargé de la tenue du Registre foncier (livre foncier) au Maroc. Toute mutation immobilière sur un bien titré doit être inscrite à la Conservation foncière pour être opposable aux tiers.',
    domain: 'civil',
  },
  {
    term: 'Contrat de travail',
    ar: 'عقد الشغل',
    definition: 'Convention par laquelle un salarié s\'engage à travailler sous la direction et l\'autorité d\'un employeur, en échange d\'une rémunération. Peut être à durée déterminée (CDD) ou indéterminée (CDI).',
    domain: 'travail',
  },
  {
    term: 'Copropriété',
    ar: 'الملكية المشتركة',
    definition: 'Régime juridique applicable aux immeubles divisés en appartements ou lots appartenant à plusieurs propriétaires, régi au Maroc par la loi n°18-00 sur la copropriété des immeubles bâtis.',
    domain: 'civil',
  },
  {
    term: 'Cour de cassation',
    ar: 'محكمة النقض',
    definition: 'Plus haute juridiction de l\'ordre judiciaire au Maroc (anciennement Cour suprême). Elle vérifie la bonne application des règles de droit sans rejuger les faits. Sa décision crée une jurisprudence.',
    domain: 'civil',
  },
  {
    term: 'CRI (Centre Régional d\'Investissement)',
    ar: 'مركز الاستثمار الجهوي',
    definition: 'Guichet unique régional pour les investisseurs. Le CRI regroupe toutes les formalités de création d\'entreprise (inscription au registre de commerce, patente, CNSS) et accompagne les projets d\'investissement.',
    domain: 'commercial',
  },

  // ── D ──────────────────────────────────────────────────────────────────
  {
    term: 'Dahir',
    ar: 'ظهير شريف',
    definition: 'Acte législatif ou réglementaire émis par le Roi du Maroc. Le dahir de promulgation donne force de loi aux textes votés par le Parlement. C\'est la forme suprême de l\'acte juridique au Maroc.',
    domain: 'constitutionnel',
  },
  {
    term: 'Décret',
    ar: 'مرسوم',
    definition: 'Acte réglementaire pris par le Chef du gouvernement (décret simple) ou par le Roi (décret royal). Les décrets d\'application précisent les modalités d\'application des lois votées par le Parlement.',
    domain: 'administratif',
  },
  {
    term: 'Délai de prescription',
    ar: 'أجل التقادم',
    definition: 'Durée au-delà de laquelle une action en justice ne peut plus être exercée. Le délai varie selon la nature de l\'action : 5 ans en droit civil de droit commun, 2 ans en droit commercial, délais spéciaux en droit pénal.',
    domain: 'civil',
  },
  {
    term: 'Divorce',
    ar: 'الطلاق',
    definition: 'Dissolution du mariage par décision judiciaire. La Moudawwana reconnaît plusieurs formes : le divorce judiciaire, le talaq (sous contrôle du juge), le khol (à l\'initiative de l\'épouse avec compensation), et le divorce pour discorde (chiqaq).',
    domain: 'civil',
  },
  {
    term: 'Dol',
    ar: 'التدليس',
    definition: 'Vice du consentement consistant en des manœuvres frauduleuses d\'une partie pour tromper l\'autre et l\'amener à contracter. Le dol entraîne la nullité relative du contrat.',
    domain: 'civil',
  },
  {
    term: 'Domicile',
    ar: 'الموطن',
    definition: 'Lieu où une personne a son principal établissement et le centre de ses intérêts. Le domicile détermine notamment la compétence territoriale des tribunaux et le lieu de signification des actes judiciaires.',
    domain: 'civil',
  },
  {
    term: 'Droit de préemption',
    ar: 'حق الشفعة',
    definition: 'Droit accordé par la loi ou par convention à une personne d\'acquérir un bien en priorité avant tout autre acheteur, dans les mêmes conditions de prix. Droit d\'origine islamique (shuf\'a) reconnu par le droit marocain.',
    domain: 'civil',
  },
  {
    term: 'Droit réel',
    ar: 'حق عيني',
    definition: 'Droit portant directement sur une chose (bien), par opposition au droit personnel (créance). Les principaux droits réels sont la propriété, l\'usufruit, le droit de superficie, les servitudes et les sûretés réelles (hypothèque, gage).',
    domain: 'civil',
  },

  // ── E ──────────────────────────────────────────────────────────────────
  {
    term: 'Enregistrement',
    ar: 'التسجيل',
    definition: 'Formalité fiscale et administrative consistant à présenter un acte à l\'administration fiscale pour qu\'elle en prenne note et perçoive les droits d\'enregistrement. Obligatoire pour les actes immobiliers, les sociétés et certains contrats.',
    domain: 'fiscal',
  },
  {
    term: 'Erreur',
    ar: 'الغلط',
    definition: 'Vice du consentement consistant en une fausse représentation de la réalité au moment de la conclusion du contrat. L\'erreur sur la substance de la chose peut entraîner la nullité du contrat.',
    domain: 'civil',
  },
  {
    term: 'Exécution forcée',
    ar: 'التنفيذ الجبري',
    definition: 'Mesure par laquelle le créancier muni d\'un titre exécutoire (jugement, acte notarié) contraint le débiteur à exécuter son obligation par la saisie de ses biens ou de ses revenus.',
    domain: 'civil',
  },
  {
    term: 'Expertise judiciaire',
    ar: 'خبرة قضائية',
    definition: 'Mesure d\'instruction par laquelle un juge désigne un expert pour lui fournir un avis technique sur une question relevant de sa spécialité (évaluation immobilière, expertise comptable, etc.).',
    domain: 'civil',
  },

  // ── F ──────────────────────────────────────────────────────────────────
  {
    term: 'Faute grave',
    ar: 'خطأ جسيم',
    definition: 'En droit du travail, faute d\'une gravité telle qu\'elle rend impossible le maintien du salarié dans l\'entreprise, même pendant la durée du préavis. Elle prive le salarié de ses indemnités de licenciement.',
    domain: 'travail',
  },
  {
    term: 'Fonds de commerce',
    ar: 'الأصل التجاري',
    definition: 'Ensemble d\'éléments mobiliers (corporels et incorporels) affectés à l\'exploitation d\'une activité commerciale : clientèle, enseigne, nom commercial, brevets, matériel... Le fonds peut être vendu ou nanti.',
    domain: 'commercial',
  },
  {
    term: 'Force majeure',
    ar: 'القوة القاهرة',
    definition: 'Événement imprévisible, irrésistible et extérieur à la volonté des parties qui empêche l\'exécution d\'une obligation. La force majeure exonère le débiteur de sa responsabilité contractuelle.',
    domain: 'civil',
  },
  {
    term: 'Forclusion',
    ar: 'السقوط بالتقادم',
    definition: 'Extinction d\'un droit ou d\'une action faute d\'avoir été exercé dans le délai imparti par la loi. Contrairement à la prescription, la forclusion n\'est pas susceptible d\'interruption ou de suspension.',
    domain: 'civil',
  },

  // ── G ──────────────────────────────────────────────────────────────────
  {
    term: 'Gage',
    ar: 'الرهن الحيازي',
    definition: 'Sûreté réelle mobilière par laquelle un débiteur remet un bien meuble à son créancier en garantie du remboursement de sa dette. Le créancier gagniste a un droit de rétention et un droit de préférence.',
    domain: 'commercial',
  },
  {
    term: 'Garde des enfants (Hadana)',
    ar: 'الحضانة',
    definition: 'Droit et devoir de garder et d\'élever l\'enfant mineur. Selon la Moudawwana, la mère a la priorité pour la garde en cas de divorce, sauf intérêt supérieur de l\'enfant. La garde est distincte de la tutelle légale.',
    domain: 'civil',
  },
  {
    term: 'Gérance',
    ar: 'التسيير',
    definition: 'Fonction consistant à diriger et administrer une société au nom et pour le compte des associés. Le gérant d\'une SARL est responsable civilement et pénalement des fautes commises dans l\'exercice de ses fonctions.',
    domain: 'commercial',
  },

  // ── H ──────────────────────────────────────────────────────────────────
  {
    term: 'Héritage (Mîrath)',
    ar: 'الإرث',
    definition: 'Transmission du patrimoine du défunt à ses héritiers selon les règles du droit islamique malékite codifiées par la Moudawwana. Les parts sont fixées par la loi selon le degré de parenté.',
    domain: 'civil',
  },
  {
    term: 'Hypothèque',
    ar: 'الرهن الرسمي',
    definition: 'Sûreté réelle immobilière accordant au créancier un droit de préférence sur un immeuble pour garantir le remboursement d\'une dette, sans dépossession du propriétaire. Elle doit être inscrite à la Conservation foncière.',
    domain: 'civil',
  },

  // ── I ──────────────────────────────────────────────────────────────────
  {
    term: 'Immatriculation',
    ar: 'التسجيل في السجل التجاري',
    definition: 'Inscription obligatoire d\'une société ou d\'un commerçant au Registre du commerce. Elle confère la personnalité morale à la société et la publicité nécessaire à sa reconnaissance par les tiers.',
    domain: 'commercial',
  },
  {
    term: 'Impôt sur les Sociétés (IS)',
    ar: 'الضريبة على الشركات',
    definition: 'Impôt direct frappant les bénéfices réalisés par les sociétés au Maroc. Le taux standard est de 20%, avec des taux réduits pour les petites entreprises et des exonérations dans certaines zones et secteurs.',
    domain: 'fiscal',
  },
  {
    term: 'Impôt sur le Revenu (IR)',
    ar: 'الضريبة على الدخل',
    definition: 'Impôt progressif frappant les revenus des personnes physiques : salaires, revenus professionnels, fonciers, agricoles et de capitaux mobiliers. Le barème progressif va de 0% à 38% selon les tranches.',
    domain: 'fiscal',
  },
  {
    term: 'Indemnité de licenciement',
    ar: 'تعويض الإعالة عن الفصل',
    definition: 'Somme versée par l\'employeur au salarié en cas de licenciement sans faute grave. Son montant est calculé selon l\'ancienneté du salarié, conformément au Code du Travail (Loi 65-99).',
    domain: 'travail',
  },
  {
    term: 'Injonction de payer',
    ar: 'أمر بالأداء',
    definition: 'Procédure simplifiée permettant au créancier d\'obtenir rapidement du tribunal un titre exécutoire contre un débiteur récalcitrant, sans débat contradictoire initial.',
    domain: 'civil',
  },

  // ── J ──────────────────────────────────────────────────────────────────
  {
    term: 'Jugement',
    ar: 'حكم',
    definition: 'Décision rendue par une juridiction de première instance (tribunal de première instance, tribunal administratif, tribunal de commerce). Il est susceptible d\'appel, sauf cas de premier et dernier ressort.',
    domain: 'civil',
  },
  {
    term: 'Jurisprudence',
    ar: 'الاجتهاد القضائي',
    definition: 'Ensemble des décisions rendues par les tribunaux qui constituent une source d\'interprétation du droit. Au Maroc, la jurisprudence de la Cour de cassation a une autorité particulière.',
    domain: 'civil',
  },

  // ── K ──────────────────────────────────────────────────────────────────
  {
    term: 'Kafala',
    ar: 'الكفالة',
    definition: 'Institution juridique islamique permettant à une famille de prendre en charge un enfant abandonné sans établir de lien de filiation. La kafala est reconnue par la loi marocaine n°15-01 comme alternative à l\'adoption, interdite par le droit marocain.',
    domain: 'civil',
  },
  {
    term: 'Khol',
    ar: 'الخلع',
    definition: 'Forme de divorce à l\'initiative de l\'épouse qui rachète sa liberté en restituant la dot (mahr) ou en versant une compensation convenue. Doit être homologué par le juge de la famille.',
    domain: 'civil',
  },

  // ── L ──────────────────────────────────────────────────────────────────
  {
    term: 'Lettre de change',
    ar: 'كمبيالة',
    definition: 'Titre de crédit par lequel un tireur donne l\'ordre à un tiré de payer une somme à une date déterminée à un bénéficiaire. Instrument de crédit commercial très utilisé dans les transactions au Maroc.',
    domain: 'commercial',
  },
  {
    term: 'Licenciement',
    ar: 'الفصل من الشغل',
    definition: 'Rupture du contrat de travail à l\'initiative de l\'employeur. Le Code du Travail marocain distingue le licenciement pour faute grave (sans indemnité), le licenciement économique et le licenciement abusif (donnant droit à indemnisation).',
    domain: 'travail',
  },
  {
    term: 'Loi',
    ar: 'قانون',
    definition: 'Texte normatif voté par le Parlement (Chambre des représentants et Chambre des conseillers) et promulgué par dahir royal. La loi occupe le deuxième rang dans la hiérarchie des normes, après la Constitution.',
    domain: 'constitutionnel',
  },
  {
    term: 'Loi de Finances',
    ar: 'قانون المالية',
    definition: 'Loi annuelle votée par le Parlement qui prévoit et autorise les ressources et les charges de l\'État pour l\'exercice budgétaire. Elle fixe notamment les taux d\'imposition et les allocations budgétaires.',
    domain: 'fiscal',
  },
  {
    term: 'Loi organique',
    ar: 'قانون تنظيمي',
    definition: 'Loi portant sur l\'organisation des pouvoirs publics, prévue expressément par la Constitution. Soumise à un contrôle obligatoire de constitutionnalité avant promulgation, elle est hiérarchiquement supérieure aux lois ordinaires.',
    domain: 'constitutionnel',
  },
  {
    term: 'Loi-cadre',
    ar: 'قانون إطار',
    definition: 'Loi fixant les orientations générales et les objectifs d\'une politique publique, sans entrer dans les détails techniques qui sont renvoyés à des textes réglementaires d\'application.',
    domain: 'constitutionnel',
  },

  // ── M ──────────────────────────────────────────────────────────────────
  {
    term: 'Mariage',
    ar: 'الزواج',
    definition: 'Contrat civil et religieux soumis à la Moudawwana. Nécessite le consentement des deux époux, un tuteur matrimonial (wali) pour la femme dans certains cas, et deux témoins. L\'âge minimum est fixé à 18 ans (dérogation possible par le juge).',
    domain: 'civil',
  },
  {
    term: 'Médiation',
    ar: 'الوساطة',
    definition: 'Mode alternatif de règlement des litiges par lequel un tiers neutre (médiateur) aide les parties à trouver elles-mêmes une solution à leur différend. Différente de l\'arbitrage, le médiateur ne tranche pas.',
    domain: 'civil',
  },
  {
    term: 'Mise en demeure',
    ar: 'الإنذار',
    definition: 'Acte par lequel le créancier demande formellement au débiteur d\'exécuter son obligation dans un délai précis. Elle est généralement requise avant toute action en justice et peut interrompre un délai de prescription.',
    domain: 'civil',
  },
  {
    term: 'Moudawwana',
    ar: 'مدونة الأسرة',
    definition: 'Voir "Code de la famille". Terme arabe désignant le Code de la famille marocain régi par la loi n°70-03, qui a réformé le statut personnel des Marocains en 2004.',
    domain: 'civil',
  },
  {
    term: 'MRE (Marocain Résidant à l\'Étranger)',
    ar: 'مغربي مقيم بالخارج',
    definition: 'Ressortissant marocain résidant régulièrement hors du territoire national. Les MRE conservent l\'intégralité de leurs droits civils, patrimoniaux et familiaux au Maroc. Ils peuvent investir, hériter et acquérir des biens immobiliers dans les mêmes conditions que les résidents.',
    domain: 'civil',
  },

  // ── N ──────────────────────────────────────────────────────────────────
  {
    term: 'Nantissement',
    ar: 'الرهن الحيازي على المنقول',
    definition: 'Sûreté portant sur un bien meuble incorporel (fonds de commerce, créances, parts sociales, brevet...). Contrairement au gage, le nantissement ne nécessite pas la dépossession physique du bien.',
    domain: 'commercial',
  },
  {
    term: 'Nationalité marocaine',
    ar: 'الجنسية المغربية',
    definition: 'Lien juridique entre une personne et l\'État marocain, régi par le Dahir de 1958 modifié par la loi 62-06. Elle se transmet par le père ou la mère (depuis 2007). Le Maroc tolère la double nationalité sans prévoir de déchéance automatique.',
    domain: 'civil',
  },
  {
    term: 'Notaire',
    ar: 'موثق',
    definition: 'Officier public chargé de recevoir les actes auxquels les parties veulent conférer le caractère authentique. Le notaire marocain authentifie les ventes immobilières, les sociétés, les successions et les actes de famille.',
    domain: 'civil',
  },
  {
    term: 'Nullité',
    ar: 'البطلان',
    definition: 'Sanction civile annulant un acte juridique qui ne respecte pas les conditions légales. La nullité absolue (ordre public) peut être invoquée par tout intéressé ; la nullité relative ne peut l\'être que par la partie protégée.',
    domain: 'civil',
  },

  // ── O ──────────────────────────────────────────────────────────────────
  {
    term: 'Office des Changes',
    ar: 'مكتب الصرف',
    definition: 'Organisme public marocain chargé de réglementer et contrôler les opérations de change et les mouvements de capitaux entre le Maroc et l\'étranger. Il garantit aux investisseurs étrangers le libre transfert de leurs capitaux et bénéfices.',
    domain: 'fiscal',
  },
  {
    term: 'Opposabilité',
    ar: 'الحجية تجاه الغير',
    definition: 'Caractère d\'un droit ou d\'un acte juridique pouvant être invoqué contre les tiers. L\'inscription au registre foncier ou au registre du commerce rend les actes opposables aux tiers.',
    domain: 'civil',
  },
  {
    term: 'Ordonnance',
    ar: 'أمر قضائي',
    definition: 'Décision judiciaire prise par un juge statuant seul, notamment en référé (urgence) ou sur requête. Également acte législatif du gouvernement pris par délégation du Parlement.',
    domain: 'civil',
  },

  // ── P ──────────────────────────────────────────────────────────────────
  {
    term: 'Pension alimentaire',
    ar: 'النفقة',
    definition: 'Obligation légale de subvenir aux besoins essentiels d\'un proche dans le besoin : conjoint, enfants mineurs, ascendants nécessiteux. Son montant est fixé par le juge selon les besoins du créancier et les ressources du débiteur.',
    domain: 'civil',
  },
  {
    term: 'Personnalité morale',
    ar: 'الشخصية المعنوية',
    definition: 'Aptitude reconnue par la loi à une entité (société, association, fondation) d\'être titulaire de droits et d\'obligations, distinctement de ses membres. Elle est acquise lors de l\'immatriculation au registre du commerce.',
    domain: 'commercial',
  },
  {
    term: 'Préavis',
    ar: 'مهلة الإشعار',
    definition: 'Délai que doit respecter la partie qui met fin à un contrat à durée indéterminée (contrat de travail, bail) avant que la rupture ne soit effective. Sa durée varie selon l\'ancienneté ou les usages professionnels.',
    domain: 'travail',
  },
  {
    term: 'Prescription acquisitive (usucapion)',
    ar: 'التقادم المكسب',
    definition: 'Mode d\'acquisition de la propriété par la possession prolongée et continue d\'un bien, dans les conditions fixées par la loi. Au Maroc, elle est régie par le Dahir des obligations et contrats (D.O.C.).',
    domain: 'civil',
  },
  {
    term: 'Procuration',
    ar: 'وكالة',
    definition: 'Acte par lequel une personne (mandant) confère à une autre (mandataire) le pouvoir d\'agir en son nom. Elle peut être générale ou spéciale. Doit être notariée et apostillée pour certains actes importants (vente immobilière, succession...).',
    domain: 'civil',
  },

  // ── R ──────────────────────────────────────────────────────────────────
  {
    term: 'Recours en annulation',
    ar: 'دعوى الإلغاء',
    definition: 'Action en justice devant le tribunal administratif visant à faire annuler une décision administrative illégale. Ce recours pour excès de pouvoir est une garantie fondamentale de l\'État de droit.',
    domain: 'administratif',
  },
  {
    term: 'Registre du commerce',
    ar: 'السجل التجاري',
    definition: 'Registre public tenu par les greffes des tribunaux de commerce, sur lequel doivent s\'immatriculer les commerçants et sociétés commerciales. L\'immatriculation est une condition de la publicité légale et de la personnalité morale.',
    domain: 'commercial',
  },
  {
    term: 'Responsabilité civile',
    ar: 'المسؤولية المدنية',
    definition: 'Obligation pour toute personne de réparer le préjudice qu\'elle cause à autrui, par sa faute ou par le fait des personnes ou des choses dont elle a la garde. Elle peut être contractuelle ou délictuelle.',
    domain: 'civil',
  },
  {
    term: 'Rétention (droit de)',
    ar: 'حق الحبس',
    definition: 'Droit reconnu à un créancier de retenir un bien appartenant à son débiteur jusqu\'au paiement de sa créance. Par exemple, le garagiste peut retenir le véhicule réparé jusqu\'au paiement de la facture.',
    domain: 'civil',
  },

  // ── S ──────────────────────────────────────────────────────────────────
  {
    term: 'SA (Société Anonyme)',
    ar: 'شركة مساهمة',
    definition: 'Forme de société dans laquelle le capital est divisé en actions et où les actionnaires ne sont responsables qu\'à concurrence de leurs apports. Elle est administrée par un conseil d\'administration. Capital minimum : 300 000 DH.',
    domain: 'commercial',
  },
  {
    term: 'Saisie-arrêt',
    ar: 'الحجز ما في ذمة الغير',
    definition: 'Procédure permettant à un créancier de bloquer les sommes qu\'un tiers (ex: employeur) doit à son débiteur. Permet notamment de saisir les salaires dans les limites légales.',
    domain: 'civil',
  },
  {
    term: 'SARL (Société à Responsabilité Limitée)',
    ar: 'شركة ذات المسؤولية المحدودة',
    definition: 'Forme juridique la plus répandue au Maroc. Les associés ne sont responsables des dettes sociales qu\'à concurrence de leurs apports. Régie par la loi n°5-96. Depuis les réformes récentes, le capital minimum symbolique est de 1 dirham.',
    domain: 'commercial',
  },
  {
    term: 'Servitude',
    ar: 'ارتفاق',
    definition: 'Charge imposée sur un immeuble (fonds servant) au profit d\'un autre immeuble (fonds dominant). Exemples : servitude de passage, de vue, d\'écoulement des eaux. Elle est attachée au fonds et non à la personne.',
    domain: 'civil',
  },
  {
    term: 'SMIG',
    ar: 'الحد الأدنى للأجور',
    definition: 'Salaire Minimum Interprofessionnel Garanti. Rémunération minimale en dessous de laquelle il est illégal de rémunérer un salarié au Maroc. Son montant est fixé par décret et régulièrement révisé.',
    domain: 'travail',
  },
  {
    term: 'Solidarité',
    ar: 'التضامن',
    definition: 'Mécanisme juridique par lequel plusieurs débiteurs sont tenus d\'une même dette et le créancier peut en réclamer le paiement intégral à n\'importe lequel d\'entre eux. Très fréquente dans les cautionnements et sociétés.',
    domain: 'civil',
  },
  {
    term: 'Succession',
    ar: 'التركة',
    definition: 'Transmission du patrimoine d\'une personne décédée à ses héritiers. Au Maroc, elle est régie par les règles de la jurisprudence islamique malékite codifiées par la Moudawwana. Les biens au Maroc sont toujours soumis au droit marocain.',
    domain: 'civil',
  },
  {
    term: 'Syndicat',
    ar: 'نقابة',
    definition: 'Organisation représentant et défendant les intérêts collectifs des travailleurs (syndicat de salariés) ou des employeurs (organisation patronale). Le droit syndical est garanti par la Constitution de 2011.',
    domain: 'travail',
  },

  // ── T ──────────────────────────────────────────────────────────────────
  {
    term: 'Talaq',
    ar: 'الطلاق بالإرادة المنفردة',
    definition: 'Forme de répudiation à l\'initiative du mari, strictement encadrée par la Moudawwana (2004). Elle doit désormais être autorisée par un juge de la famille, après tentative de conciliation et règlement des droits financiers de l\'épouse.',
    domain: 'civil',
  },
  {
    term: 'Titre foncier',
    ar: 'الرسم العقاري',
    definition: 'Document établi par la Conservation foncière qui atteste de manière incontestable la propriété d\'un bien immobilier. Le titre foncier est définitif et inattaquable, ce qui en fait la preuve la plus sûre de la propriété immobilière au Maroc.',
    domain: 'civil',
  },
  {
    term: 'Tribunal administratif',
    ar: 'المحكمة الإدارية',
    definition: 'Juridiction spécialisée compétente pour les litiges entre les citoyens et l\'administration (État, collectivités). Elle peut annuler des décisions administratives illégales et condamner l\'administration à indemniser les préjudices causés.',
    domain: 'administratif',
  },
  {
    term: 'Tribunal de commerce',
    ar: 'المحكمة التجارية',
    definition: 'Juridiction spécialisée compétente pour les litiges entre commerçants, sociétés commerciales, et les actes de commerce. Compétent aussi pour les procédures collectives (redressement et liquidation judiciaires).',
    domain: 'commercial',
  },
  {
    term: 'TVA (Taxe sur la Valeur Ajoutée)',
    ar: 'الضريبة على القيمة المضافة',
    definition: 'Impôt indirect sur la consommation, collecté par les entreprises pour le compte de l\'État. Le taux normal au Maroc est de 20%, avec des taux réduits (14%, 10%, 7%) pour certains produits et services.',
    domain: 'fiscal',
  },

  // ── U ──────────────────────────────────────────────────────────────────
  {
    term: 'Usufruit',
    ar: 'حق الانتفاع',
    definition: 'Droit réel permettant à son titulaire (usufruitier) d\'utiliser un bien appartenant à une autre personne (nu-propriétaire) et d\'en percevoir les fruits, sans pouvoir en disposer. S\'éteint généralement au décès de l\'usufruitier.',
    domain: 'civil',
  },

  // ── V ──────────────────────────────────────────────────────────────────
  {
    term: 'Vice caché',
    ar: 'عيب خفي',
    definition: 'Défaut non apparent d\'un bien vendu qui le rend impropre à l\'usage auquel il est destiné ou qui en diminue tellement l\'usage que l\'acheteur n\'aurait pas acheté ou aurait payé moins cher s\'il l\'avait connu.',
    domain: 'civil',
  },
  {
    term: 'Voies d\'exécution',
    ar: 'طرق التنفيذ',
    definition: 'Ensemble des procédures permettant à un créancier muni d\'un titre exécutoire de contraindre son débiteur à payer : saisie-vente, saisie-arrêt, saisie immobilière, expulsion...',
    domain: 'civil',
  },

  // ── W ──────────────────────────────────────────────────────────────────
  {
    term: 'Wassiya (Testament)',
    ar: 'الوصية',
    definition: 'Acte unilatéral par lequel une personne dispose de ses biens pour après sa mort. En droit marocain, le testament est limité au tiers de la succession et ne peut pas bénéficier à un héritier légal.',
    domain: 'civil',
  },
  {
    term: 'Wali (Tuteur matrimonial)',
    ar: 'الولي',
    definition: 'Personne (généralement le père ou un proche parent) qui assiste la femme lors de la conclusion du mariage. La Moudawwana de 2004 a assoupli le rôle du wali : la femme majeure peut se marier sans son accord en cas de refus injustifié.',
    domain: 'civil',
  },

  // ── Z ──────────────────────────────────────────────────────────────────
  {
    term: 'Zone d\'accélération industrielle',
    ar: 'منطقة التسريع الصناعي',
    definition: 'Zones géographiques à statut fiscal privilégié remplaçant les anciennes zones franches. Elles offrent des avantages fiscaux substantiels (exonération d\'IS pendant 5 ans, puis taux réduit) pour attirer les investisseurs industriels et de services.',
    domain: 'commercial',
  },
]

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Regrouper les termes par lettre */
export function getGlossaireByLetter() {
  const grouped = {}
  for (const entry of GLOSSAIRE) {
    const letter = entry.term[0].toUpperCase()
    if (!grouped[letter]) grouped[letter] = []
    grouped[letter].push(entry)
  }
  // Trier les termes dans chaque lettre
  for (const letter of Object.keys(grouped)) {
    grouped[letter].sort((a, b) => a.term.localeCompare(b.term, 'fr'))
  }
  return grouped
}

/** Lettres disponibles triées */
export function getAvailableLetters() {
  const letters = new Set(GLOSSAIRE.map(e => e.term[0].toUpperCase()))
  return [...letters].sort()
}

/** Recherche plein texte */
export function searchGlossaire(query) {
  if (!query || query.trim().length < 2) return []
  const q = query.toLowerCase().trim()
  return GLOSSAIRE.filter(e =>
    e.term.toLowerCase().includes(q) ||
    e.definition.toLowerCase().includes(q) ||
    e.ar.includes(q)
  )
}
