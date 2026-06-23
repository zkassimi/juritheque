/**
 * JuriThèque — Configuration des pages SEO par intention de recherche
 * ─────────────────────────────────────────────────────────────────────
 * Chaque entrée définit un guide thématique basé sur les textes
 * disponibles dans Supabase.
 *
 * RÈGLE : ne jamais inventer de règles juridiques dans ce fichier.
 * Les intro/faq sont généraux et informatifs — les détails viennent
 * des textes liés récupérés depuis Supabase.
 */

export const SEO_INTENT_PAGES = [
  // ── Droit du Travail ────────────────────────────────────────────────
  {
    lastUpdated:     '2026-06',
    slug:            'code-du-travail-maroc',
    category:        'travail',
    title:           'Code du Travail au Maroc : textes et lois applicables',
    title_ar:        'مدونة الشغل بالمغرب : النصوص والقوانين المطبقة',
    metaDescription: 'Consultez les textes juridiques du Code du Travail marocain : contrat de travail, congés, licenciement, syndicats, inspection du travail.',
    metaDescription_ar: 'اطلع على النصوص القانونية لمدونة الشغل المغربية: عقد العمل، الإجازات، الفصل من العمل، النقابات، تفتيش الشغل.',
    h1:              'Code du Travail au Maroc',
    h1_ar:           'مدونة الشغل بالمغرب',
    intro:           'Le droit du travail marocain encadre les relations entre employeurs et salariés du secteur privé. Cette page regroupe les principaux textes disponibles dans JuriThèque sur le droit du travail.',
    intro_ar:        'تنظم مدونة الشغل المغربية العلاقات بين أصحاب العمل والأجراء في القطاع الخاص. تجمع هذه الصفحة أهم النصوص المتاحة في JuriThèque المتعلقة بقانون الشغل.',
    legalDomain:     'travail',
    keywords:        ['code du travail', 'contrat de travail', 'licenciement', 'congés payés', 'SMIG', 'syndicats', 'inspection du travail', 'convention collective'],
    keywords_ar:     ['مدونة الشغل', 'عقد الشغل', 'الفصل من العمل', 'الأجر الأدنى', 'النقابات', 'تفتيش الشغل', 'الإجازة السنوية', 'الاتفاقية الجماعية'],
    searchTerms:     ['code travail', 'contrat travail', 'salarié'],
    relatedSlugs:    ['licenciement-maroc', 'procedure-civile-maroc'],
    faq: [
      {
        question: 'Quel est le texte principal du droit du travail au Maroc ?',
        answer:   'Le droit du travail marocain est principalement régi par la Loi n°65-99 relative au Code du Travail. Cette page liste les textes disponibles dans JuriThèque en lien avec ce code.',
      },
      {
        question: 'Où trouver les textes officiels du Code du Travail ?',
        answer:   'JuriThèque recense les textes officiels publiés par les sources gouvernementales marocaines (SGG, MMSP). Vous pouvez consulter et télécharger les PDFs disponibles depuis cette page.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو النص الأساسي لقانون الشغل بالمغرب؟',
        answer:   'يُنظَّم قانون الشغل المغربي أساساً بموجب القانون رقم 65-99 المتعلق بمدونة الشغل. تسرد هذه الصفحة النصوص المتاحة في JuriThèque المرتبطة بهذه المدونة.',
      },
      {
        question: 'أين أجد النصوص الرسمية لمدونة الشغل؟',
        answer:   'تُحصي JuriThèque النصوص الرسمية الصادرة عن الجهات الحكومية المغربية (الأمانة العامة للحكومة، وزارة الشغل). يمكنك الاطلاع على ملفات PDF المتاحة وتنزيلها من هذه الصفحة.',
      },
    ],
    sections: [
      {
        h2:      'Les textes fondamentaux du droit du travail',
        content: [
          'Le droit du travail marocain repose principalement sur la Loi n°65-99 relative au Code du Travail, promulguée par le Dahir du 11 septembre 2003. Ce texte régit les relations entre employeurs et salariés dans le secteur privé.',
          'Il est complété par des textes spécifiques sur la sécurité sociale, les conventions collectives sectorielles et les décrets d\'application.',
        ],
        bullets: [
          'Loi n°65-99 : Code du Travail (contrats, salaires, congés, rupture)',
          'Dahir n°1-72-184 : régime de sécurité sociale (CNSS)',
          'Conventions collectives sectorielles (BTP, hôtellerie, transports…)',
          'Décrets sur le SMIG et les heures supplémentaires',
        ],
      },
      {
        h2:      'Points clés pour employeurs et salariés',
        content: 'Le Code du Travail encadre l\'ensemble du cycle de la relation de travail, de l\'embauche à la rupture du contrat.',
        bullets: [
          'Durée légale : 44 heures/semaine dans le secteur non agricole',
          'Congé annuel payé : minimum 18 jours ouvrables par an',
          'SMIG révisé périodiquement par décret',
          'Préavis obligatoire en cas de licenciement ou démission',
          'Indemnité de licenciement calculée selon l\'ancienneté (art. 53)',
          'Délégués des salariés obligatoires à partir de 10 salariés',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'licenciement-maroc',
    category:        'travail',
    title:           'Licenciement au Maroc : droits, procédures et textes',
    title_ar:        'الفصل من العمل بالمغرب : الحقوق والإجراءات والنصوص',
    metaDescription: 'Textes juridiques sur le licenciement au Maroc : licenciement abusif, indemnités, préavis, procédure disciplinaire et recours.',
    metaDescription_ar: 'النصوص القانونية المتعلقة بالفصل من العمل بالمغرب : الفصل التعسفي، التعويضات، الإشعار المسبق، الإجراء التأديبي والطعن.',
    h1:              'Licenciement au Maroc',
    h1_ar:           'الفصل من العمل بالمغرب',
    intro:           'Le licenciement est strictement encadré par le Code du Travail marocain. Cette page regroupe les textes disponibles dans JuriThèque sur les procédures et droits liés au licenciement.',
    intro_ar:        'يخضع الفصل من العمل بالمغرب لأحكام صارمة يضمنها قانون الشغل. تجمع هذه الصفحة النصوص المتاحة في JuriThèque حول إجراءات وحقوق الفصل من العمل.',
    legalDomain:     'travail',
    keywords:        ['licenciement', 'licenciement abusif', 'indemnité de licenciement', 'préavis', 'faute grave', 'procédure disciplinaire', 'réintégration'],
    keywords_ar:     ['الفصل من العمل', 'الفصل التعسفي', 'تعويض الفصل', 'الإشعار المسبق', 'الخطأ الجسيم', 'المسطرة التأديبية', 'إعادة الإدماج'],
    searchTerms:     ['licenciement', 'rupture contrat travail', 'indemnité'],
    relatedSlugs:    ['code-du-travail-maroc', 'procedure-civile-maroc'],
    faq: [
      {
        question: 'Quelle indemnité en cas de licenciement abusif au Maroc ?',
        answer:   'Le Code du Travail prévoit des indemnités spécifiques en cas de licenciement abusif. Consultez les textes disponibles dans JuriThèque ou posez votre question à l\'assistant IA pour une orientation.',
      },
      {
        question: 'Quelle est la procédure de licenciement au Maroc ?',
        answer:   'La procédure inclut une convocation, un entretien préalable et le respect des délais de préavis. Les détails figurent dans le Code du Travail accessible sur JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو التعويض في حالة الفصل التعسفي من العمل بالمغرب؟',
        answer:   'ينص قانون الشغل على تعويضات محددة في حالة الفصل التعسفي. يمكن الاطلاع على النصوص المتاحة في JuriThèque أو طرح سؤالك على المساعد الذكي للحصول على توجيه.',
      },
      {
        question: 'ما هي مسطرة الفصل من العمل بالمغرب؟',
        answer:   'تشمل المسطرة الاستدعاء للاستماع، ثم احترام آجال الإشعار المسبق. تجد التفاصيل في قانون الشغل المتاح على JuriThèque.',
      },
    ],
    sections: [
      {
        h2:      'Motifs légaux de licenciement au Maroc',
        content: [
          'Le Code du Travail marocain (Loi n°65-99) distingue deux grandes catégories de licenciement : le licenciement disciplinaire (pour faute) et le licenciement économique (pour motif économique ou technologique). Tout licenciement doit reposer sur un motif réel et sérieux.',
          'La faute grave — abandon de poste, violence, vol, divulgation de secrets professionnels — peut justifier un licenciement immédiat sans préavis ni indemnité.',
        ],
        bullets: [
          'Faute grave (art. 39) : licenciement sans préavis ni indemnité',
          'Faute non grave : licenciement avec préavis et indemnité de licenciement',
          'Motif économique : suppression de poste pour raisons structurelles ou technologiques',
          'Maladie prolongée : sous conditions strictes et autorisation de l\'inspecteur du travail',
          'Licenciement sans motif valable = licenciement abusif ouvrant droit à réparation',
        ],
      },
      {
        h2:      'Procédure et délais de préavis',
        content: [
          'Tout licenciement disciplinaire doit respecter une procédure précise : convocation écrite du salarié, tenue d\'un entretien contradictoire, puis notification écrite de la décision motivée dans un délai de 48 heures.',
          'Le préavis varie selon la catégorie du salarié et son ancienneté. Son non-respect entraîne le versement d\'une indemnité compensatrice.',
        ],
        bullets: [
          'Cadres et assimilés : préavis de 1 à 3 mois selon ancienneté',
          'Employés et ouvriers : préavis de 8 jours à 1 mois selon ancienneté',
          'Indemnité de licenciement (art. 53) : calculée sur 96 heures par année pour les 5 premières années',
          'Notification écrite obligatoire : sous 48h après l\'entretien (art. 62)',
          'Absence de procédure = licenciement abusif, même si le motif est valable',
        ],
      },
      {
        h2:      'Recours et droits du salarié licencié',
        content: [
          'Le salarié qui conteste son licenciement dispose d\'un délai de 90 jours pour saisir le tribunal du travail compétent. En cas de licenciement abusif reconnu, le juge peut ordonner la réintégration ou allouer des dommages-intérêts.',
          'En parallèle, le salarié licencié peut bénéficier de l\'indemnité de perte d\'emploi auprès de la CNSS, sous conditions d\'ancienneté et de cotisation.',
        ],
        bullets: [
          'Délai de recours : 90 jours devant le tribunal du travail (art. 65)',
          'Réintégration ou indemnisation : au choix du juge selon les circonstances',
          'Indemnité de perte d\'emploi (CNSS) : pour les salariés ayant cotisé au moins 780 jours',
          'Solde de tout compte : doit être signé et remis au moment de la rupture',
          'Certificat de travail : droit du salarié, obligatoire à la fin du contrat',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'الأسباب القانونية للفصل من العمل بالمغرب',
        content: [
          'يميز قانون الشغل المغربي (القانون رقم 65-99) بين نوعين رئيسيين من الفصل: الفصل التأديبي (بسبب خطأ) والفصل الاقتصادي (لأسباب اقتصادية أو تكنولوجية). ويجب أن يستند كل فصل إلى سبب حقيقي وجدي.',
          'يمكن أن يبرر الخطأ الجسيم — التغيب عن العمل، والعنف، والسرقة، وإفشاء الأسرار المهنية — الفصل الفوري دون إشعار مسبق أو تعويض.',
        ],
        bullets: [
          'الخطأ الجسيم (المادة 39): الفصل دون إشعار مسبق أو تعويض',
          'الخطأ غير الجسيم: الفصل مع الإشعار المسبق وتعويض الفصل',
          'السبب الاقتصادي: إلغاء المنصب لأسباب هيكلية أو تكنولوجية',
          'المرض المطوّل: وفق شروط صارمة وإذن مفتش الشغل',
          'الفصل بدون سبب مشروع = فصل تعسفي يستوجب التعويض',
        ],
      },
      {
        h2:      'المسطرة وآجال الإشعار المسبق',
        content: [
          'يجب أن تحترم كل عملية فصل تأديبي مسطرة محددة: استدعاء كتابي للأجير، وعقد مقابلة تواجهية، ثم إشعار كتابي بالقرار المعلل في غضون 48 ساعة.',
          'يتفاوت أجل الإشعار المسبق حسب فئة الأجير وأقدميته، ويترتب على عدم احترامه أداء تعويض تعادلي.',
        ],
        bullets: [
          'الأطر وما في حكمهم: إشعار مسبق من شهر إلى ثلاثة أشهر حسب الأقدمية',
          'الموظفون والعمال: إشعار مسبق من 8 أيام إلى شهر حسب الأقدمية',
          'تعويض الفصل (المادة 53): يُحسب على أساس 96 ساعة لكل سنة من السنوات الخمس الأولى',
          'الإشعار الكتابي الإجباري: في غضون 48 ساعة من المقابلة (المادة 62)',
          'غياب المسطرة = فصل تعسفي حتى وإن كان السبب مشروعاً',
        ],
      },
      {
        h2:      'الطعن وحقوق الأجير المفصول',
        content: [
          'يتوفر الأجير الذي يطعن في فصله على أجل 90 يوماً للتقدم إلى المحكمة الاجتماعية المختصة. وفي حالة ثبوت الفصل التعسفي، يمكن للقاضي أن يأمر بإعادة الإدماج أو يحكم بالتعويضات.',
          'إلى جانب ذلك، يمكن للأجير المفصول أن يستفيد من تعويض فقدان الشغل لدى الصندوق الوطني للضمان الاجتماعي، وفق شروط الأقدمية والانخراط.',
        ],
        bullets: [
          'أجل الطعن: 90 يوماً أمام المحكمة الاجتماعية (المادة 65)',
          'إعادة الإدماج أو التعويض: وفق تقدير القاضي للملابسات',
          'تعويض فقدان الشغل (الصندوق الوطني للضمان الاجتماعي): للأجراء المنخرطين لمدة 780 يوماً على الأقل',
          'شهادة العمل: حق الأجير، إلزامية عند انتهاء العقد',
          'بيان الحساب الختامي: يجب تسليمه وقت إنهاء العلاقة الشغلية',
        ],
      },
    ],
  },

  // ── Droit Commercial ────────────────────────────────────────────────
  {
    lastUpdated:     '2026-06',
    slug:            'code-de-commerce-maroc',
    category:        'commercial',
    title:           'Code de Commerce au Maroc : lois et textes applicables',
    title_ar:        'مدونة التجارة بالمغرب : القوانين والنصوص المطبقة',
    metaDescription: 'Accédez aux textes du Code de Commerce marocain : sociétés commerciales, actes de commerce, effets de commerce, faillite, registre du commerce.',
    metaDescription_ar: 'اطلع على نصوص مدونة التجارة المغربية : الشركات التجارية، الأعمال التجارية، أوراق الدفع، الإفلاس، السجل التجاري.',
    h1:              'Code de Commerce au Maroc',
    h1_ar:           'مدونة التجارة بالمغرب',
    intro:           'Le droit commercial marocain encadre les activités des commerçants, des sociétés et des actes de commerce. Retrouvez ici les textes disponibles dans JuriThèque.',
    intro_ar:        'ينظم القانون التجاري المغربي أنشطة التجار والشركات والأعمال التجارية. اعثر هنا على النصوص المتاحة في JuriThèque.',
    legalDomain:     'commercial',
    keywords:        ['code de commerce', 'actes de commerce', 'commerçant', 'registre du commerce', 'faillite', 'effets de commerce', 'lettre de change'],
    keywords_ar:     ['مدونة التجارة', 'الأعمال التجارية', 'التاجر', 'السجل التجاري', 'الإفلاس', 'أوراق الدفع', 'الكمبيالة'],
    searchTerms:     ['code commerce', 'société commerciale', 'commerçant'],
    relatedSlugs:    ['sarl-maroc', 'bail-commercial-maroc', 'creation-societe-maroc', 'cheque-sans-provision-maroc'],
    faq: [
      {
        question: 'Quel est le principal texte du droit commercial marocain ?',
        answer:   'Le Code de Commerce marocain est régi par la Loi n°15-95 promulguée par le Dahir du 1er août 1996. Cette page regroupe les textes liés disponibles dans JuriThèque.',
      },
      {
        question: 'Le Code de Commerce s\'applique-t-il aux auto-entrepreneurs ?',
        answer:   'Certaines dispositions peuvent s\'appliquer. Consultez les textes disponibles dans JuriThèque ou posez votre question à l\'assistant IA pour obtenir des orientations.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو النص الأساسي للقانون التجاري المغربي؟',
        answer:   'تُنظَّم مدونة التجارة المغربية بموجب القانون رقم 15-95 الصادر بالظهير الشريف المؤرخ في 1 أغسطس 1996. تجمع هذه الصفحة النصوص المرتبطة المتاحة في JuriThèque.',
      },
      {
        question: 'هل تسري مدونة التجارة على المقاولين الذاتيين؟',
        answer:   'قد تسري بعض الأحكام عليهم. راجع النصوص المتاحة في JuriThèque أو اطرح سؤالك على المساعد الذكي للحصول على توجيهات.',
      },
    ],
    sections: [
      {
        h2:      'Le commerçant et le fonds de commerce',
        content: [
          'Le Code de Commerce marocain (Loi n°15-95) définit le commerçant comme toute personne qui accomplit des actes de commerce à titre habituel et professionnel. L\'immatriculation au registre du commerce (RC) est une obligation légale permettant l\'opposabilité aux tiers.',
          'Le fonds de commerce est un ensemble d\'éléments corporels (matériel, marchandises) et incorporels (clientèle, enseigne, brevets) exploités pour l\'exercice d\'une activité commerciale.',
        ],
        bullets: [
          'Registre du commerce (RC) : immatriculation obligatoire auprès du tribunal de commerce',
          'Actes de commerce par nature : achat-revente, opérations bancaires, transport, assurances…',
          'Fonds de commerce : comprend clientèle, enseigne, brevet, matériel et stocks',
          'Cession du fonds de commerce : soumise à des formalités légales strictes',
          'Nantissement du fonds : mise en garantie possible auprès d\'un créancier',
        ],
      },
      {
        h2:      'Les sociétés commerciales au Maroc',
        content: [
          'Le Code de Commerce et la Loi n°17-95 sur la SA et la Loi n°5-96 sur les autres formes organisent les différents types de sociétés commerciales. Chaque forme a ses propres règles de constitution, de gouvernance et de responsabilité.',
          'Le choix de la forme sociale dépend du nombre d\'associés, du capital disponible, du secteur d\'activité et de la volonté de limiter ou non la responsabilité des associés.',
        ],
        bullets: [
          'SARL : société la plus répandue, capital librement fixé, responsabilité limitée aux apports',
          'SA : pour les grandes structures, capital minimum 300 000 MAD, gouvernance par conseil d\'administration',
          'SNC : associés indéfiniment et solidairement responsables des dettes sociales',
          'SCA : mêle associés commandités (responsabilité illimitée) et commanditaires (apporteurs de capital)',
          'Auto-entrepreneur : statut simplifié, immatriculation sans RC classique',
        ],
      },
      {
        h2:      'Obligations comptables et fiscales du commerçant',
        content: [
          'Tout commerçant est tenu de tenir une comptabilité régulière. Le Code de Commerce impose la tenue du livre-journal, du grand livre et du bilan annuel. Ces obligations visent à assurer la transparence des transactions commerciales.',
          'Sur le plan fiscal, le commerçant est soumis à l\'Impôt sur le Revenu (IR) ou à l\'Impôt sur les Sociétés (IS) selon sa forme juridique, ainsi qu\'à la Taxe sur la Valeur Ajoutée (TVA) selon son chiffre d\'affaires.',
        ],
        bullets: [
          'Livre-journal et grand livre : tenus régulièrement, conservation 10 ans',
          'Bilan annuel : obligatoire et déposé au greffe du tribunal de commerce',
          'IS : 20 % standard (PME), jusqu\'à 31 % pour les grandes entreprises',
          'TVA : 20 % standard — exonération partielle pour certains secteurs',
          'Déclaration annuelle du bénéfice : au plus tard le 31 mars de l\'année suivante',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'التاجر والأصل التجاري',
        content: [
          'تُعرِّف مدونة التجارة المغربية (القانون رقم 15-95) التاجرَ بأنه كل شخص يزاول أعمالاً تجارية باعتبارها حرفةً معتادة. والتقييد في السجل التجاري التزام قانوني يتيح الاحتجاج بالحق تجاه الغير.',
          'الأصل التجاري هو مجموع العناصر المادية (التجهيزات والبضائع) والمعنوية (الزبناء والشعار والبراءات) التي تُستثمَر في مزاولة النشاط التجاري.',
        ],
        bullets: [
          'السجل التجاري: التقييد إلزامي لدى المحكمة التجارية',
          'الأعمال التجارية بطبيعتها: الشراء والبيع، العمليات البنكية، النقل، التأمين...',
          'الأصل التجاري: يشمل الزبناء والشعار والبراءات والتجهيزات والمخزون',
          'نقل الأصل التجاري: يخضع لشكليات قانونية صارمة',
          'رهن الأصل التجاري: يمكن تقديمه ضماناً لدى الدائن',
        ],
      },
      {
        h2:      'الشركات التجارية بالمغرب',
        content: [
          'تُنظِّم مدونة التجارة والقانون رقم 17-95 المتعلق بشركة المساهمة والقانون رقم 5-96 المتعلق بالأشكال الأخرى مختلفَ أنواع الشركات التجارية. ولكل شكل قواعده الخاصة في التأسيس والتسيير والمسؤولية.',
          'يعتمد اختيار الشكل القانوني على عدد الشركاء ورأس المال المتاح والقطاع الذي تنشط فيه الشركة.',
        ],
        bullets: [
          'الشركة ذات المسؤولية المحدودة (ش.ذ.م.م): الأكثر شيوعاً، رأس المال حر، المسؤولية محدودة بالحصص',
          'شركة المساهمة: للهياكل الكبرى، رأس مال أدنى 300 ألف درهم، تُدار بمجلس إدارة',
          'شركة التضامن: يكون الشركاء مسؤولين بصفة شخصية وتضامنية عن ديون الشركة',
          'شركة التوصية: تجمع شركاء متضامنين وشركاء موصين (مُقدِّمو رأس المال)',
          'المقاول الذاتي: نظام مبسط بدون سجل تجاري كلاسيكي',
        ],
      },
      {
        h2:      'الالتزامات المحاسبية والجبائية للتاجر',
        content: [
          'يلتزم كل تاجر بمسك محاسبة منتظمة. تُوجب مدونة التجارة مسك دفتر اليومية والدفتر الكبير والميزانية السنوية، وذلك لضمان الشفافية في المعاملات التجارية.',
          'على الصعيد الجبائي، يخضع التاجر لضريبة الدخل أو ضريبة الشركات وفق شكله القانوني، فضلاً عن الضريبة على القيمة المضافة بحسب رقم أعماله.',
        ],
        bullets: [
          'دفتر اليومية والدفتر الكبير: تُمسك بانتظام وتُحفظ لمدة 10 سنوات',
          'الميزانية السنوية: إلزامية وتُودَع لدى كتابة ضبط المحكمة التجارية',
          'ضريبة الشركات: 20% معدل عام للمقاولات الصغرى وحتى 31% للشركات الكبرى',
          'الضريبة على القيمة المضافة: 20% معدل عام مع إعفاء جزئي لبعض القطاعات',
          'التصريح السنوي بالنتيجة: في أجل أقصاه 31 مارس من السنة الموالية',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'sarl-maroc',
    category:        'commercial',
    title:           'SARL au Maroc : lois, règles et textes applicables',
    title_ar:        'الشركة ذات المسؤولية المحدودة بالمغرب : القوانين والنصوص المطبقة',
    metaDescription: 'Consultez les textes juridiques applicables à la SARL au Maroc : création, gérance, associés, obligations légales et dissolution.',
    metaDescription_ar: 'اطلع على النصوص القانونية المطبقة على الشركة ذات المسؤولية المحدودة بالمغرب: التأسيس، التسيير، الشركاء، الالتزامات القانونية والحل.',
    h1:              'SARL au Maroc',
    h1_ar:           'الشركة ذات المسؤولية المحدودة بالمغرب',
    intro:           'La Société à Responsabilité Limitée (SARL) est la forme juridique la plus répandue au Maroc. Cette page regroupe les textes disponibles dans JuriThèque liés à ce type de société.',
    intro_ar:        'تُعدّ الشركة ذات المسؤولية المحدودة (ش.ذ.م.م) الشكل القانوني الأكثر شيوعاً بالمغرب. تجمع هذه الصفحة النصوص المتاحة في JuriThèque المرتبطة بهذا النوع من الشركات.',
    legalDomain:     'commercial',
    keywords:        ['SARL', 'société à responsabilité limitée', 'gérance', 'associés', 'capital social', 'dissolution', 'statuts SARL'],
    keywords_ar:     ['الشركة ذات المسؤولية المحدودة', 'ش.ذ.م.م', 'المدير', 'الشركاء', 'رأس المال الاجتماعي', 'حل الشركة', 'النظام الأساسي'],
    searchTerms:     ['SARL', 'société responsabilité limitée'],
    relatedSlugs:    ['creation-societe-maroc', 'code-de-commerce-maroc', 'bail-commercial-maroc'],
    faq: [
      {
        question: 'Quels textes encadrent la SARL au Maroc ?',
        answer:   'La SARL est principalement régie par la Loi n°5-96 sur la société en nom collectif, la commandite simple, la commandite par actions et la SARL. Cette page liste les textes disponibles dans JuriThèque.',
      },
      {
        question: 'Quel est le capital minimum pour créer une SARL au Maroc ?',
        answer:   'Pour une information précise et à jour, consultez les textes disponibles dans JuriThèque ou posez votre question à l\'assistant IA.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هي النصوص التي تنظم الشركة ذات المسؤولية المحدودة بالمغرب؟',
        answer:   'تخضع الشركة ذات المسؤولية المحدودة أساساً للقانون رقم 5-96 المتعلق بشركة التضامن والتوصية البسيطة والتوصية بالأسهم والشركة ذات المسؤولية المحدودة. تُدرج هذه الصفحة النصوص المتاحة في JuriThèque.',
      },
      {
        question: 'ما هو الحد الأدنى لرأس المال لتأسيس شركة ذات مسؤولية محدودة بالمغرب؟',
        answer:   'للحصول على معلومات دقيقة ومحيّنة، راجع النصوص المتاحة في JuriThèque أو اطرح سؤالك على المساعد الذكي.',
      },
    ],
    sections: [
      {
        h2:      'Capital social et associés de la SARL',
        content: [
          'La SARL marocaine est régie par la Loi n°5-96 telle que modifiée. Depuis la réforme de 2006, le capital minimum n\'est plus fixé par la loi et peut être librement déterminé par les associés, même à 1 dirham. En pratique, les banques exigent souvent un capital plus conséquent pour l\'ouverture d\'un compte professionnel.',
          'La SARL peut être constituée par 1 à 50 associés. Au-delà de 50 associés, elle doit être transformée en société anonyme (SA). Les parts sociales ne sont pas librement cessibles sans l\'accord des associés.',
        ],
        bullets: [
          'Capital minimum : librement fixé (pas de minimum légal depuis 2006)',
          'Nombre d\'associés : 1 (SARL à associé unique) à 50 maximum',
          'Parts sociales : non cotées en bourse, cession soumise à agrément des associés',
          'Apports en numéraire : libérés à hauteur d\'au moins 1/4 à la constitution',
          'Apports en nature : évalués par un commissaire aux apports si > 60 000 MAD',
        ],
      },
      {
        h2:      'Gouvernance et gérance de la SARL',
        content: [
          'La SARL est gérée par un ou plusieurs gérants, personnes physiques, associés ou non. Le gérant est nommé par les associés dans les statuts ou par une décision collective. Il dispose des pouvoirs les plus étendus pour agir au nom de la société.',
          'Les décisions collectives sont prises en assemblée générale ou par voie de consultation écrite. Certaines décisions importantes exigent une majorité qualifiée ou l\'unanimité.',
        ],
        bullets: [
          'Gérant : désigné dans les statuts ou par AGO — peut être révoqué par majorité des parts',
          'AGO annuelle : approbation des comptes dans les 6 mois suivant la clôture',
          'Majorité simple (> 50 % des parts) : décisions de gestion courante',
          'Majorité des 3/4 : modification des statuts, augmentation ou réduction de capital',
          'Rapport de gestion : établi par le gérant, présenté annuellement aux associés',
        ],
      },
      {
        h2:      'Fiscalité et obligations comptables de la SARL',
        content: [
          'La SARL est soumise à l\'Impôt sur les Sociétés (IS). Elle doit tenir une comptabilité conforme au Code Général de Normalisation Comptable (CGNC), déposer ses états de synthèse annuels et régler ses obligations déclaratives.',
          'Le gérant associé majoritaire est considéré comme salarié pour la CNSS mais ses rémunérations sont soumises à l\'IR selon les règles de la rémunération des dirigeants.',
        ],
        bullets: [
          'IS : 20 % sur les bénéfices (PME), barème progressif pour les grandes entreprises',
          'TVA : 20 % standard — déclaration mensuelle ou trimestrielle selon le CA',
          'Déclaration annuelle IS : au plus tard le 31 mars de l\'année suivante',
          'CNSS gérant : cotisations sociales obligatoires pour le gérant rémunéré',
          'Commissaire aux comptes obligatoire si CA > 50 millions MAD ou + de 50 salariés',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'رأس المال الاجتماعي وشركاء الشركة ذات المسؤولية المحدودة',
        content: [
          'تخضع الشركة ذات المسؤولية المحدودة المغربية للقانون رقم 5-96 المعدَّل. ومنذ إصلاح 2006، لم يعد الحد الأدنى لرأس المال مقيداً بنص قانوني، ويمكن تحديده بحرية من قبل الشركاء، ولو بدرهم واحد. غير أن البنوك كثيراً ما تشترط رأس مال أعلى لفتح الحسابات المهنية.',
          'يمكن تأسيس الشركة ذات المسؤولية المحدودة من طرف 1 إلى 50 شريكاً. وإن تجاوز عدد الشركاء 50، وجب تحويلها إلى شركة مساهمة.',
        ],
        bullets: [
          'الحد الأدنى لرأس المال: حر (لا حد أدنى قانوني منذ 2006)',
          'عدد الشركاء: من 1 (شريك وحيد) إلى 50 كحد أقصى',
          'الحصص الاجتماعية: غير مدرجة في البورصة، وتخضع نقلَ ملكيتها لموافقة الشركاء',
          'الحصص النقدية: تُحرَّر بما لا يقل عن ربعها عند التأسيس',
          'الحصص العينية: يُقيِّمها مراقب الحصص إن تجاوزت 60 ألف درهم',
        ],
      },
      {
        h2:      'التسيير والإدارة في الشركة ذات المسؤولية المحدودة',
        content: [
          'تُدار الشركة ذات المسؤولية المحدودة من طرف مدير أو أكثر من الأشخاص الطبيعيين، سواء أكانوا شركاء أم لا. يُعيِّن الشركاء المديرَ في النظام الأساسي أو بقرار جماعي، وتكون له أوسع الصلاحيات للتصرف باسم الشركة.',
          'تُتخذ القرارات الجماعية في الجمعية العامة أو بالمشاورة الكتابية، وتستلزم بعض القرارات الهامة أغلبية مؤهَّلة أو الإجماع.',
        ],
        bullets: [
          'المدير: يُعيَّن في النظام الأساسي أو بالجمعية العامة العادية — قابل للعزل بأغلبية الحصص',
          'الجمعية العامة العادية السنوية: المصادقة على الحسابات في أجل 6 أشهر من إقفال السنة المالية',
          'الأغلبية البسيطة (أكثر من 50% من الحصص): للقرارات التسييرية الجارية',
          'أغلبية الثلاثة أرباع: لتعديل النظام الأساسي وزيادة أو تخفيض رأس المال',
          'تقرير التسيير: يعده المدير ويعرضه سنوياً على الشركاء',
        ],
      },
      {
        h2:      'الجباية والالتزامات المحاسبية للشركة ذات المسؤولية المحدودة',
        content: [
          'تخضع الشركة ذات المسؤولية المحدودة لضريبة الشركات، وعليها مسك محاسبة وفق المدونة العامة لتطبيع المحاسبة، وإيداع قوائمها المالية السنوية والوفاء بالتزاماتها التصريحية.',
          'يُعتبر المدير الشريك المسيطر أجيراً لدى الصندوق الوطني للضمان الاجتماعي، غير أن مكافآته تخضع لضريبة الدخل وفق أحكام تقدير مكافآت المسيرين.',
        ],
        bullets: [
          'ضريبة الشركات: 20% على الأرباح (المقاولات الصغرى)، سلم تدريجي للشركات الكبرى',
          'الضريبة على القيمة المضافة: 20% معدل عام — تصريح شهري أو ربعي حسب رقم الأعمال',
          'التصريح السنوي بضريبة الشركات: في أجل أقصاه 31 مارس من السنة الموالية',
          'اشتراكات الصندوق الوطني للضمان الاجتماعي: إلزامية للمدير المأجور',
          'مراقب الحسابات: إلزامي إذا تجاوز رقم الأعمال 50 مليون درهم أو عدد المستخدمين 50',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'bail-commercial-maroc',
    category:        'commercial',
    title:           'Bail Commercial au Maroc : textes et droits applicables',
    title_ar:        'الكراء التجاري بالمغرب : النصوص والحقوق المطبقة',
    metaDescription: 'Trouvez les textes juridiques sur le bail commercial au Maroc : droit au renouvellement, indemnité d\'éviction, loyer, résiliation.',
    metaDescription_ar: 'اطلع على النصوص القانونية للكراء التجاري بالمغرب : حق التجديد، تعويض الإفراغ، الكراء، فسخ العقد.',
    h1:              'Bail Commercial au Maroc',
    h1_ar:           'الكراء التجاري بالمغرب',
    intro:           'Le bail commercial est encadré par des textes spécifiques protégeant le fonds de commerce. Retrouvez les textes disponibles dans JuriThèque sur ce sujet.',
    intro_ar:        'ينظم الكراء التجاري بالمغرب نصوص قانونية خاصة تحمي الأصل التجاري. تجمع هذه الصفحة النصوص المتاحة في JuriThèque المتعلقة بهذا الموضوع.',
    legalDomain:     'commercial',
    keywords:        ['bail commercial', 'fonds de commerce', 'loyer commercial', 'indemnité d\'éviction', 'renouvellement du bail', 'résiliation bail'],
    keywords_ar:     ['الكراء التجاري', 'الأصل التجاري', 'واجب الكراء', 'تعويض الإفراغ', 'تجديد عقد الكراء', 'فسخ الكراء'],
    searchTerms:     ['bail commercial', 'fonds commerce', 'loyer commercial'],
    relatedSlugs:    ['code-de-commerce-maroc', 'recouvrement-maroc'],
    faq: [
      {
        question: 'Quel texte régit le bail commercial au Maroc ?',
        answer:   'Le bail commercial est encadré par le Dahir du 24 mai 1955 et les dispositions du Code de Commerce. Consultez les textes disponibles dans JuriThèque.',
      },
      {
        question: 'Le propriétaire peut-il refuser le renouvellement d\'un bail commercial ?',
        answer:   'Des règles spécifiques encadrent le renouvellement et l\'indemnité d\'éviction. Consultez les textes disponibles ou posez la question à l\'assistant IA.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو النص القانوني الذي يحكم الكراء التجاري بالمغرب؟',
        answer:   'ينظم الكراء التجاري ظهير 24 ماي 1955 وأحكام مدونة التجارة. يمكن الاطلاع على النصوص المتاحة في JuriThèque.',
      },
      {
        question: 'هل يمكن للمالك رفض تجديد عقد الكراء التجاري؟',
        answer:   'تحكم قواعد خاصة شروط التجديد وتعويض الإفراغ. راجع النصوص المتاحة أو اطرح سؤالك على المساعد الذكي.',
      },
    ],
    sections: [
      {
        h2:      'Le cadre juridique du bail commercial',
        content: [
          'Le bail commercial au Maroc est encadré par le Dahir du 24 mai 1955 relatif aux baux commerciaux et les articles 232 à 270 du Code de Commerce. Ces textes confèrent au locataire commerçant une protection particulière fondée sur la valeur de son fonds de commerce.',
          'L\'objectif est de protéger l\'investissement du commerçant dans son local et d\'éviter une éviction arbitraire pouvant détruire sa clientèle.',
        ],
        bullets: [
          'Dahir du 24 mai 1955 : bail à usage commercial, industriel ou artisanal',
          'Loi n°15-95 (Code de Commerce) : dispositions complémentaires',
          'Code des Obligations et Contrats (COC) : droit commun du bail',
        ],
      },
      {
        h2:      'Droits et protections essentiels du locataire',
        content: 'Le bail commercial crée des droits spécifiques au profit du locataire, notamment un droit au renouvellement encadré par la loi.',
        bullets: [
          'Droit au renouvellement : le locataire peut exiger le renouvellement du bail',
          'Indemnité d\'éviction : si le bailleur refuse sans motif grave, il doit une indemnité',
          'Révision du loyer : selon clauses contractuelles ou accord des parties',
          'Sous-location et cession : interdites sans accord écrit du bailleur',
          'Propriété commerciale : le locataire peut opposer ses droits au bailleur',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'recouvrement-maroc',
    category:        'commercial',
    title:           'Recouvrement de créances au Maroc : textes et procédures',
    title_ar:        'استخلاص الديون بالمغرب : النصوص والإجراءات',
    metaDescription: 'Trouvez les textes sur le recouvrement de créances au Maroc : injonction de payer, saisie, opposition, délai de prescription.',
    metaDescription_ar: 'اطلع على النصوص المتعلقة باستخلاص الديون بالمغرب : الأمر بالأداء، الحجز، التعرض، أجل التقادم.',
    h1:              'Recouvrement de créances au Maroc',
    h1_ar:           'استخلاص الديون بالمغرب',
    intro:           'Le recouvrement des créances au Maroc peut se faire par voie amiable ou judiciaire. Cette page regroupe les textes disponibles dans JuriThèque sur ce sujet.',
    intro_ar:        'يمكن استخلاص الديون بالمغرب بصورة ودية أو قضائية. تجمع هذه الصفحة النصوص المتاحة في JuriThèque حول هذا الموضوع.',
    legalDomain:     'commercial',
    keywords:        ['recouvrement', 'créances', 'injonction de payer', 'saisie', 'huissier', 'mise en demeure', 'exécution forcée'],
    keywords_ar:     ['استخلاص الديون', 'الأمر بالأداء', 'الحجز', 'المفوض القضائي', 'الإنذار', 'التنفيذ الجبري', 'الدين التجاري'],
    searchTerms:     ['recouvrement', 'injonction payer', 'créance'],
    relatedSlugs:    ['procedure-civile-maroc', 'cheque-sans-provision-maroc', 'delai-de-prescription-maroc'],
    faq: [
      {
        question: 'Comment recouvrer une créance au Maroc ?',
        answer:   'La procédure d\'injonction de payer est le moyen le plus courant. Elle est encadrée par le Code de Procédure Civile. Consultez les textes disponibles dans JuriThèque.',
      },
      {
        question: 'Quel est le délai de prescription pour une créance commerciale au Maroc ?',
        answer:   'Les délais varient selon la nature de la créance. Consultez les textes de référence disponibles dans JuriThèque ou posez votre question à l\'assistant IA.',
      },
    ],
    faq_ar: [
      {
        question: 'كيف يمكن استخلاص دين بالمغرب؟',
        answer:   'تُعدّ مسطرة الأمر بالأداء الوسيلة الأكثر شيوعاً، وتُنظِّمها قواعد قانون المسطرة المدنية. راجع النصوص المتاحة في JuriThèque.',
      },
      {
        question: 'ما هو أجل التقادم بالنسبة للديون التجارية بالمغرب؟',
        answer:   'تتفاوت الآجال حسب طبيعة الدين. راجع النصوص المرجعية المتاحة في JuriThèque أو اطرح سؤالك على المساعد الذكي.',
      },
    ],
    sections: [
      {
        h2:      'Les voies amiables de recouvrement',
        content: [
          'Avant toute action judiciaire, la loi marocaine encourage le règlement amiable des dettes. Le créancier adresse une mise en demeure par lettre recommandée avec accusé de réception, accordant au débiteur un délai raisonnable pour payer. En cas d\'échec, une négociation directe ou le recours à un médiateur peuvent être envisagés.',
          'La mise en demeure est un préalable important : elle interrompt le délai de prescription et constitue une preuve de la démarche amiable en cas de recours judiciaire ultérieur.',
        ],
        bullets: [
          'Mise en demeure écrite : lettre recommandée AR — interrompt la prescription',
          'Médiation commerciale : possible devant le Centre de Médiation et d\'Arbitrage',
          'Plan d\'apurement : accord amiable sur un échéancier de remboursement',
          'Protocole transactionnel : accord écrit homologable par le tribunal',
          'Délai de réponse conseillé : 8 à 15 jours avant passage en phase judiciaire',
        ],
      },
      {
        h2:      'La procédure d\'injonction de payer',
        content: [
          'L\'injonction de payer est la procédure judiciaire la plus rapide pour recouvrer une créance liquide et exigible. Elle est régie par les articles 155 à 165 du Code de Procédure Civile marocain. Le créancier dépose une requête auprès du président du tribunal compétent, sans audience contradictoire préalable.',
          'Si la requête est fondée, le juge rend une ordonnance d\'injonction de payer. Le débiteur dispose ensuite d\'un délai de 15 jours pour former opposition, délai pendant lequel l\'exécution est suspendue.',
        ],
        bullets: [
          'Créances visées : sommes d\'argent liquides, exigibles et de montant déterminé',
          'Tribunal compétent : tribunal de commerce si créance commerciale, tribunal de première instance sinon',
          'Requête unilatérale : pas d\'audience contradictoire au stade de l\'obtention',
          'Délai d\'opposition : 15 jours à compter de la signification par huissier',
          'Défaut d\'opposition : ordonnance rendue exécutoire par le greffe',
          'Opposition formée : renvoi en procédure contradictoire ordinaire',
        ],
      },
      {
        h2:      'Les saisies et l\'exécution forcée',
        content: [
          'En possession d\'un titre exécutoire (ordonnance d\'injonction, jugement, acte notarié), le créancier peut engager des mesures d\'exécution forcée via un huissier de justice. Plusieurs types de saisies sont prévus par le Code de Procédure Civile.',
          'L\'huissier joue un rôle central dans l\'exécution : il signifie les actes, pratique les saisies et procède aux ventes aux enchères si nécessaire. Les frais d\'exécution sont en principe à la charge du débiteur.',
        ],
        bullets: [
          'Saisie-arrêt : blocage des fonds du débiteur chez un tiers (banque, employeur)',
          'Saisie mobilière : appréhension des biens meubles du débiteur',
          'Saisie immobilière : procédure longue sur les biens immobiliers, vente aux enchères judiciaires',
          'Saisie des rémunérations : encadrée, plafonnée selon quotité saisissable',
          'Huissier de justice : seul habilité à pratiquer les saisies après titre exécutoire',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'مسالك الاستخلاص الودي',
        content: [
          'قبل أي إجراء قضائي، يُشجع القانون المغربي على التسوية الودية للديون. يُوجّه الدائن إنذاراً بالأداء بواسطة رسالة مضمونة مع الإشعار بالتوصل، مانحاً للمدين أجلاً معقولاً للأداء. وفي حالة الفشل، يمكن اللجوء إلى التفاوض المباشر أو الوساطة.',
          'يُعدّ الإنذار بالأداء إجراءً أولياً بالغ الأهمية: فهو يقطع أجل التقادم ويُشكِّل دليلاً على المسعى الودي في حالة اللجوء لاحقاً إلى القضاء.',
        ],
        bullets: [
          'الإنذار الكتابي: رسالة مضمونة مع الإشعار بالتوصل — يقطع التقادم',
          'الوساطة التجارية: ممكنة أمام مركز الوساطة والتحكيم',
          'جدولة الديون: اتفاق ودي على أجدول للأداء',
          'البروتوكول التصالحي: اتفاق كتابي قابل للمصادقة القضائية',
          'أجل الرد المنصوح به: 8 إلى 15 يوماً قبل الانتقال إلى المرحلة القضائية',
        ],
      },
      {
        h2:      'مسطرة الأمر بالأداء',
        content: [
          'تُعدّ مسطرة الأمر بالأداء المسطرةَ القضائية الأسرع لاستخلاص دين محدد وحال الأداء. تُنظِّمها المواد من 155 إلى 165 من قانون المسطرة المدنية المغربي. يُودع الدائن مقالاً لدى رئيس المحكمة المختصة دون حضور تواجهي مسبق.',
          'إذا ثبتت جدية المقال، أصدر القاضي أمراً بالأداء، ويتوفر المدين على أجل 15 يوماً للتعرض، يتوقف خلاله التنفيذ.',
        ],
        bullets: [
          'الديون المعنية: مبالغ نقدية محددة وحالّة الأداء',
          'المحكمة المختصة: المحكمة التجارية إن كان الدين تجارياً، وإلا المحكمة الابتدائية',
          'مقال من جانب واحد: دون جلسة تواجهية في مرحلة الحصول على الأمر',
          'أجل التعرض: 15 يوماً من تاريخ التبليغ بواسطة المفوض القضائي',
          'غياب التعرض: يُجعل الأمر قابلاً للتنفيذ من قبل كتابة الضبط',
          'التعرض المقدَّم: إحالة القضية إلى مسطرة عادية تواجهية',
        ],
      },
      {
        h2:      'الحجوز والتنفيذ الجبري',
        content: [
          'بامتلاك سند تنفيذي (أمر بالأداء، حكم، عقد رسمي)، يمكن للدائن المضيّ في إجراءات التنفيذ الجبري بواسطة المفوض القضائي. ويُتيح قانون المسطرة المدنية أنواعاً متعددة من الحجوز.',
          'يضطلع المفوض القضائي بدور محوري في التنفيذ: يُبلِّغ الوثائق ويُجري الحجوز ويتولى البيع بالمزاد العلني عند الاقتضاء. وتقع مصاريف التنفيذ في الأصل على عاتق المدين.',
        ],
        bullets: [
          'حجز ما للمدين لدى الغير: تجميد أموال المدين عند ثالث (بنك، صاحب عمل)',
          'الحجز المنقول: الاستيلاء على الأموال المنقولة للمدين',
          'الحجز العقاري: مسطرة مطوّلة على الأموال غير المنقولة، بيع بالمزاد القضائي',
          'حجز الأجور: محدود بسقف قابل للحجز وفق ما يُقرره القانون',
          'المفوض القضائي: الجهة الوحيدة المؤهلة لإجراء الحجوز بعد الحصول على السند التنفيذي',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'cheque-sans-provision-maroc',
    category:        'commercial',
    title:           'Chèque sans provision au Maroc : sanctions et textes',
    title_ar:        'الشيك بدون مؤونة بالمغرب : العقوبات والنصوص',
    metaDescription: 'Consultez les textes juridiques sur le chèque sans provision au Maroc : sanctions pénales, interdiction bancaire, régularisation.',
    metaDescription_ar: 'اطلع على النصوص القانونية المتعلقة بالشيك بدون مؤونة بالمغرب: العقوبات الجنائية، الحظر البنكي، التسوية.',
    h1:              'Chèque sans provision au Maroc',
    h1_ar:           'الشيك بدون مؤونة بالمغرب',
    intro:           'L\'émission d\'un chèque sans provision est une infraction pénale au Maroc. Cette page regroupe les textes disponibles dans JuriThèque sur ce sujet.',
    intro_ar:        'يُعدّ إصدار شيك بدون مؤونة جريمة جنائية بالمغرب. تجمع هذه الصفحة النصوص المتاحة في JuriThèque حول هذا الموضوع.',
    legalDomain:     'penal',
    keywords:        ['chèque sans provision', 'chèque impayé', 'interdiction bancaire', 'sanctions pénales', 'régularisation chèque'],
    keywords_ar:     ['الشيك بدون مؤونة', 'الشيك الضائع', 'الحظر البنكي', 'العقوبات الجنائية', 'تسوية الشيك', 'بروتيستو'],
    searchTerms:     ['chèque sans provision', 'chèque impayé', 'interdiction bancaire'],
    relatedSlugs:    ['recouvrement-maroc', 'code-de-commerce-maroc'],
    faq: [
      {
        question: 'Quelles sont les sanctions pour un chèque sans provision au Maroc ?',
        answer:   'L\'émission d\'un chèque sans provision peut entraîner une interdiction bancaire et des sanctions pénales. Consultez les textes disponibles dans JuriThèque pour les détails.',
      },
      {
        question: 'Comment régulariser un chèque sans provision au Maroc ?',
        answer:   'La régularisation passe par l\'approvisionnement du compte et le paiement du chèque. Consultez les textes disponibles ou posez la question à l\'assistant IA.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هي عقوبات الشيك بدون مؤونة بالمغرب؟',
        answer:   'قد يُفضي إصدار شيك بدون مؤونة إلى الحظر البنكي وعقوبات جنائية. راجع النصوص المتاحة في JuriThèque للاطلاع على التفاصيل.',
      },
      {
        question: 'كيف يمكن تسوية وضعية الشيك بدون مؤونة بالمغرب؟',
        answer:   'تمر التسوية عبر تزويد الحساب بالمؤونة وأداء قيمة الشيك. راجع النصوص المتاحة أو اطرح السؤال على المساعد الذكي.',
      },
    ],
    sections: [
      {
        h2:      'Cadre juridique du chèque sans provision',
        content: [
          'Au Maroc, le chèque est régi par le Code de Commerce (Loi n°15-95, articles 239 à 323). L\'émission d\'un chèque sans provision suffisante et disponible est constitutive d\'une infraction pénale en vertu de l\'article 316 du Code Pénal marocain. Cette qualification distingue le Maroc de certains pays où le chèque sans provision n\'est qu\'un litige civil.',
          'Le chèque doit être provisionné au moment de son émission et non à sa présentation. Le tireur doit maintenir la provision jusqu\'au paiement effectif du chèque.',
        ],
        bullets: [
          'Code de Commerce (Loi 15-95) : articles 239 à 323 sur le chèque',
          'Article 316 du Code Pénal : infraction pénale, amende et prison',
          'Provision obligatoire au moment de l\'émission du chèque',
          'Bank Al-Maghrib : gère le fichier des interdits bancaires',
          'Délai de présentation : 20 jours pour les chèques émis et payables au Maroc',
        ],
      },
      {
        h2:      'Sanctions et interdiction bancaire',
        content: [
          'L\'émission d\'un chèque sans provision expose son auteur à des sanctions pénales et à une interdiction d\'émettre des chèques. La banque du tiré est tenue de refuser le paiement et d\'émettre un certificat de refus (protêt) à la demande du porteur.',
          'L\'interdiction bancaire est inscrite au fichier central des incidents de paiement tenu par Bank Al-Maghrib. Elle concerne tous les comptes du titulaire dans l\'ensemble des banques marocaines.',
        ],
        bullets: [
          'Amende pénale : de 6 000 à 20 000 MAD selon le montant du chèque',
          'Peine d\'emprisonnement : 1 à 5 ans en cas de récidive ou de fraude caractérisée',
          'Interdiction bancaire : injonction de restituer tous les chéquiers',
          'Inscription au fichier BAM : visible par toutes les banques marocaines',
          'Protêt (certificat de refus) : établi par huissier, nécessaire pour la poursuite pénale',
          'Clôture de compte possible par la banque en cas d\'incidents répétés',
        ],
      },
      {
        h2:      'Régularisation et sortie d\'interdiction bancaire',
        content: [
          'La régularisation d\'un chèque sans provision implique d\'approvisionner le compte et de permettre le paiement du chèque au bénéficiaire. Une fois tous les chèques impayés réglés, le tireur peut demander la mainlevée de l\'interdiction bancaire auprès de sa banque.',
          'La mainlevée n\'est pas automatique : elle doit être demandée formellement et Bank Al-Maghrib doit être informée. Un délai de traitement est à prévoir.',
        ],
        bullets: [
          '1. Approvisionner le compte à hauteur du montant du chèque impayé',
          '2. Contacter le bénéficiaire pour paiement direct ou encaissement',
          '3. Obtenir un certificat de paiement ou de renonciation du bénéficiaire',
          '4. Présenter les justificatifs à la banque pour demande de mainlevée',
          '5. La banque informe Bank Al-Maghrib — levée de l\'interdiction sous quelques jours',
          '6. En cas de poursuite pénale déjà engagée, un accord amiable peut arrêter les poursuites',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'الإطار القانوني للشيك بدون مؤونة',
        content: [
          'يخضع الشيك بالمغرب لمدونة التجارة (القانون رقم 15-95، المواد 239 إلى 323). ويُعدّ إصدار شيك بدون مؤونة كافية ومتاحة جريمة جنائية بموجب الفصل 316 من القانون الجنائي المغربي. هذا التكييف يُميّز المغرب عن بعض الدول التي لا تتجاوز فيه هذه المسألة حدود النزاع المدني.',
          'يجب أن تكون المؤونة متوفرة لحظة إصدار الشيك لا لحظة تقديمه. ويلتزم الساحب بالحفاظ عليها إلى غاية الأداء الفعلي.',
        ],
        bullets: [
          'مدونة التجارة (القانون 15-95): المواد 239 إلى 323 المتعلقة بالشيك',
          'الفصل 316 من القانون الجنائي: جريمة جنائية تستوجب الغرامة والسجن',
          'المؤونة: واجبة عند إصدار الشيك',
          'بنك المغرب: يُدير ملف الممنوعين من إصدار الشيكات',
          'أجل التقديم: 20 يوماً للشيكات الصادرة والمستحقة الأداء بالمغرب',
        ],
      },
      {
        h2:      'العقوبات والحظر البنكي',
        content: [
          'يتعرض مُصدِر الشيك بدون مؤونة لعقوبات جنائية وحظر من إصدار الشيكات. ويلتزم بنك المسحوب عليه برفض الأداء وإصدار شهادة رفض الأداء (البروتيستو) بطلب من الحامل.',
          'يُقيَّد الحظر البنكي في ملف حوادث الأداء المركزي لدى بنك المغرب، ويشمل جميع حسابات المعني لدى مختلف البنوك المغربية.',
        ],
        bullets: [
          'الغرامة الجنائية: من 6000 إلى 20000 درهم حسب مبلغ الشيك',
          'عقوبة السجن: من سنة إلى 5 سنوات في حالة العود أو الغش الصريح',
          'الحظر البنكي: إلزام بإرجاع جميع دفاتر الشيكات',
          'التقييد في ملف بنك المغرب: مرئي لجميع البنوك المغربية',
          'البروتيستو: تُحرره المفوض القضائي، ضروري للمتابعة الجنائية',
          'إمكانية إغلاق الحساب من قِبَل البنك في حالة الحوادث المتكررة',
        ],
      },
      {
        h2:      'التسوية والخروج من الحظر البنكي',
        content: [
          'تستلزم تسوية وضعية الشيك بدون مؤونة تزويد الحساب بالمبلغ اللازم وتمكين المستفيد من استخلاص قيمة الشيك. وبعد تسوية جميع الشيكات غير المؤداة، يمكن للساحب طلب رفع الحظر البنكي من بنكه.',
          'رفع الحظر ليس تلقائياً: لا بد من طلب صريح، مع إخبار بنك المغرب، مع الأخذ بعين الاعتبار آجال المعالجة.',
        ],
        bullets: [
          '1. تزويد الحساب بمبلغ الشيك غير المؤدى',
          '2. التواصل مع المستفيد لأداء الشيك أو صرفه',
          '3. الحصول على شهادة الأداء أو تنازل المستفيد',
          '4. تقديم الوثائق للبنك لطلب رفع الحظر',
          '5. يُخبر البنك بنكَ المغرب — رفع الحظر في غضون أيام',
          '6. في حالة وجود متابعة جنائية، يمكن للاتفاق الودي إيقاف المتابعة',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'creation-societe-maroc',
    category:        'commercial',
    title:           'Création de société au Maroc : démarches et textes juridiques',
    title_ar:        'تأسيس الشركات بالمغرب : الإجراءات والنصوص القانونية',
    metaDescription: 'Consultez les textes juridiques pour créer une société au Maroc : SARL, SA, SNC, formalités, registre du commerce, capital minimum.',
    metaDescription_ar: 'اطلع على النصوص القانونية لتأسيس شركة بالمغرب: ش.ذ.م.م، شركة المساهمة، شركة التضامن، الشكليات، السجل التجاري، الحد الأدنى لرأس المال.',
    h1:              'Création de société au Maroc',
    h1_ar:           'تأسيس شركة بالمغرب',
    intro:           'La création d\'une société au Maroc est encadrée par plusieurs textes juridiques. Cette page regroupe les textes disponibles dans JuriThèque sur les formes sociales et les démarches.',
    intro_ar:        'يخضع تأسيس الشركات بالمغرب لعدة نصوص قانونية. تجمع هذه الصفحة النصوص المتاحة في JuriThèque حول أشكال الشركات والإجراءات المتبعة.',
    legalDomain:     'commercial',
    keywords:        ['création société', 'SARL', 'SA', 'SNC', 'registre du commerce', 'immatriculation', 'statuts', 'CRI'],
    keywords_ar:     ['تأسيس شركة', 'ش.ذ.م.م', 'شركة المساهمة', 'شركة التضامن', 'السجل التجاري', 'التقييد', 'النظام الأساسي', 'مراكز الاستثمار الجهوية'],
    searchTerms:     ['création société', 'immatriculation', 'registre commerce'],
    relatedSlugs:    ['sarl-maroc', 'code-de-commerce-maroc', 'bail-commercial-maroc'],
    faq: [
      {
        question: 'Quelles sont les formes de sociétés au Maroc ?',
        answer:   'Le droit marocain prévoit plusieurs formes : SARL, SA, SNC, SCA, SCS. Chaque forme est régie par des textes spécifiques disponibles dans JuriThèque.',
      },
      {
        question: 'Quelles sont les étapes pour créer une société au Maroc ?',
        answer:   'La création passe par la rédaction des statuts, l\'immatriculation au registre du commerce et les publications légales. Consultez les textes disponibles dans JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هي أشكال الشركات المتاحة بالمغرب؟',
        answer:   'يتيح القانون المغربي عدة أشكال: ش.ذ.م.م، وشركة المساهمة، وشركة التضامن، وشركة التوصية بالأسهم. تُنظِّم كل شكل نصوص قانونية خاصة متاحة في JuriThèque.',
      },
      {
        question: 'ما هي مراحل تأسيس شركة بالمغرب؟',
        answer:   'يمر التأسيس بمرحلة صياغة النظام الأساسي، ثم التقييد في السجل التجاري والنشر القانوني. راجع النصوص المتاحة في JuriThèque.',
      },
    ],
    sections: [
      {
        h2:      'Choisir la forme juridique adaptée',
        content: [
          'Le choix de la forme juridique est une étape stratégique pour tout entrepreneur au Maroc. Il détermine le niveau de responsabilité, les règles de gouvernance, les obligations fiscales et la crédibilité de la structure auprès des partenaires et des banques.',
          'La SARL est la forme la plus souple et la plus répandue pour les PME. La SA convient aux grandes structures ou aux projets nécessitant une levée de fonds. Le statut d\'auto-entrepreneur est adapté aux activités individuelles à faible chiffre d\'affaires.',
        ],
        bullets: [
          'SARL : de 1 à 50 associés, capital libre, idéale pour TPE/PME',
          'SA : à partir de 5 actionnaires, capital minimum 300 000 MAD, gouvernance formalisée',
          'SNC : associés responsables indéfiniment et solidairement — peu utilisée',
          'Auto-entrepreneur : CA plafonné (500 000 MAD services / 2 M MAD commerce), pas de RC classique',
          'SARL à associé unique (SAU) : parfaite pour les indépendants souhaitant une structure sociétale',
        ],
      },
      {
        h2:      'Étapes de création auprès du CRI',
        content: [
          'La création d\'une société au Maroc se fait principalement via le Centre Régional d\'Investissement (CRI) ou en ligne sur la plateforme Rokhas. Le guichet unique du CRI centralise toutes les formalités : rédaction des statuts, immatriculation, publication et affiliation à la CNSS.',
          'Depuis la réforme de la loi 89-17, la création est totalement dématérialisée et peut être réalisée en 24 à 48 heures pour une SARL.',
        ],
        bullets: [
          '1. Rédaction et signature des statuts (notaire recommandé)',
          '2. Dépôt de la demande en ligne sur le portail Rokhas ou au CRI',
          '3. Immatriculation au registre du commerce (RC) au tribunal de commerce',
          '4. Inscription à l\'identifiant fiscal (IF) et à la patente',
          '5. Affiliation à la CNSS et ouverture d\'un compte bancaire professionnel',
          '6. Publication légale au journal d\'annonces légales et au Bulletin Officiel',
        ],
      },
      {
        h2:      'Obligations post-création',
        content: [
          'Une fois la société créée, plusieurs obligations légales et fiscales doivent être remplies dans les premières semaines d\'activité. Leur non-respect peut engager la responsabilité du gérant et entraîner des pénalités.',
          'La tenue d\'une comptabilité régulière dès le premier jour est essentielle pour les déclarations fiscales et la relation avec les banques.',
        ],
        bullets: [
          'Ouverture d\'un compte bancaire professionnel : obligatoire pour les transactions de la société',
          'Tenue de la comptabilité : livre-journal, grand livre, bilan annuel',
          'Déclaration d\'existence à la DGI : dans les 30 jours suivant le début d\'activité',
          'Adhésion à la CNSS : déclaration des salariés dès le premier recrutement',
          'Assemblée générale constitutive : approbation des statuts et nomination du gérant',
          'Assurances professionnelles : selon le secteur d\'activité',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'اختيار الشكل القانوني المناسب',
        content: [
          'يُعدّ اختيار الشكل القانوني خطوةً استراتيجية لكل مقاول بالمغرب، إذ يحدد مستوى المسؤولية وقواعد التسيير والالتزامات الجبائية ومصداقية الهيكل أمام الشركاء والبنوك.',
          'تُعدّ الشركة ذات المسؤولية المحدودة الشكلَ الأمثل والأكثر انتشاراً لدى المقاولات الصغيرة والمتوسطة. أما شركة المساهمة فتناسب الهياكل الكبيرة والمشاريع التي تستلزم جذب التمويل. وينسجم وضع المقاول الذاتي مع الأنشطة الفردية ذات رقم الأعمال المحدود.',
        ],
        bullets: [
          'ش.ذ.م.م: من 1 إلى 50 شريكاً، رأس مال حر، مثالية للمقاولات الصغرى والمتوسطة',
          'شركة المساهمة: ابتداءً من 5 مساهمين، رأس مال أدنى 300 ألف درهم، تسيير مقنَّن',
          'شركة التضامن: شركاء مسؤولون بصفة شخصية وتضامنية — نادرة الاستخدام',
          'المقاول الذاتي: رقم أعمال محدد بسقف (500 ألف درهم للخدمات / مليونا درهم للتجارة)، بدون سجل تجاري كلاسيكي',
          'ش.ذ.م.م بشريك وحيد: مثالية للمستقلين الراغبين في هيكل شركاتي',
        ],
      },
      {
        h2:      'مراحل التأسيس لدى مراكز الاستثمار الجهوية',
        content: [
          'يتم تأسيس الشركة بالمغرب أساساً عبر مركز الاستثمار الجهوي (CRI) أو على الإنترنت عبر منصة "رخصة". تُجمِّع نافذة الاستقبال الواحدة لدى المركز جميع الإجراءات: صياغة النظام الأساسي، والتقييد في السجل، والنشر، والانخراط في الصندوق الوطني للضمان الاجتماعي.',
          'منذ إصلاح القانون 89-17، أصبح التأسيس رقمياً بالكامل وبات بالإمكان إتمامه في 24 إلى 48 ساعة بالنسبة لشركة ذات مسؤولية محدودة.',
        ],
        bullets: [
          '1. صياغة النظام الأساسي والتوقيع عليه (يُنصح بتوثيق عدلي)',
          '2. تقديم طلب التأسيس عبر منصة "رخصة" أو لدى مركز الاستثمار الجهوي',
          '3. التقييد في السجل التجاري بالمحكمة التجارية',
          '4. التسجيل في المعرّف الجبائي والضريبة المهنية',
          '5. الانخراط في الصندوق الوطني للضمان الاجتماعي وفتح حساب بنكي مهني',
          '6. النشر القانوني في جريدة الإعلانات القانونية والجريدة الرسمية',
        ],
      },
      {
        h2:      'الالتزامات بعد التأسيس',
        content: [
          'بمجرد تأسيس الشركة، يتعين الوفاء بعدة التزامات قانونية وجبائية في الأسابيع الأولى من النشاط، إذ قد يُعرِّض إغفالها المدير للمسؤولية ويُفضي إلى غرامات.',
          'يُعدّ مسك محاسبة منتظمة منذ اليوم الأول أمراً جوهرياً للتصريحات الجبائية وبناء علاقة ثقة مع البنوك.',
        ],
        bullets: [
          'فتح حساب بنكي مهني: إلزامي لمعاملات الشركة',
          'مسك المحاسبة: دفتر اليومية والدفتر الكبير والميزانية السنوية',
          'التصريح بالوجود لدى المديرية العامة للضرائب: في أجل 30 يوماً من بدء النشاط',
          'الانخراط في الصندوق الوطني للضمان الاجتماعي: تصريح المستخدمين فور أول تشغيل',
          'الجمعية العامة التأسيسية: المصادقة على النظام الأساسي وتعيين المدير',
          'التأمينات المهنية: حسب قطاع النشاط',
        ],
      },
    ],
  },

  // ── Droit de la Famille ─────────────────────────────────────────────
  {
    lastUpdated:     '2026-06',
    slug:            'code-de-la-famille-maroc',
    category:        'famille',
    title:           'Code de la Famille au Maroc (Moudawwana) : textes juridiques',
    title_ar:        'مدونة الأسرة بالمغرب (المدونة) : النصوص القانونية',
    metaDescription: 'Consultez les textes du Code de la Famille marocain (Moudawwana) : mariage, divorce, garde des enfants, succession, pension alimentaire.',
    metaDescription_ar: 'اطلع على نصوص مدونة الأسرة المغربية (المدونة) : الزواج، الطلاق، حضانة الأطفال، الإرث، النفقة.',
    h1:              'Code de la Famille au Maroc',
    h1_ar:           'مدونة الأسرة بالمغرب',
    intro:           'La Moudawwana (Code de la Famille) réforme le statut personnel des Marocains. Cette page regroupe les textes disponibles dans JuriThèque sur le droit de la famille.',
    intro_ar:        'تُنظِّم مدونة الأسرة المغربية (المدونة) الأحوال الشخصية للمغاربة. تجمع هذه الصفحة النصوص المتاحة في JuriThèque المتعلقة بقانون الأسرة.',
    legalDomain:     'civil',
    keywords:        ['moudawwana', 'code de la famille', 'mariage', 'divorce', 'garde des enfants', 'succession', 'pension alimentaire', 'kafala'],
    keywords_ar:     ['مدونة الأسرة', 'المدونة', 'الزواج', 'الطلاق', 'حضانة الأطفال', 'الإرث', 'النفقة', 'الكفالة'],
    searchTerms:     ['code famille', 'moudawwana', 'mariage'],
    relatedSlugs:    ['divorce-maroc', 'delai-de-prescription-maroc'],
    faq: [
      {
        question: 'Qu\'est-ce que la Moudawwana ?',
        answer:   'La Moudawwana est le Code de la Famille marocain, réformé en 2004 par la Loi n°70-03. Elle régit le mariage, le divorce, la filiation, la garde des enfants et les successions.',
      },
      {
        question: 'Où trouve-t-on le texte officiel du Code de la Famille ?',
        answer:   'Le texte officiel est publié au Bulletin Officiel du Maroc. JuriThèque recense les versions disponibles en français et en arabe.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هي مدونة الأسرة المغربية؟',
        answer:   'مدونة الأسرة هي قانون الأحوال الشخصية المغربي، الذي أُصلح سنة 2004 بموجب القانون رقم 70-03. تنظم الزواج والطلاق والنسب وحضانة الأطفال والإرث.',
      },
      {
        question: 'أين أجد النص الرسمي لمدونة الأسرة؟',
        answer:   'يُنشر النص الرسمي في الجريدة الرسمية للمملكة المغربية. تُوفر JuriThèque النسخ المتاحة باللغتين الفرنسية والعربية.',
      },
    ],
    sections: [
      {
        h2:      'La Moudawwana : réforme de 2004',
        content: [
          'La Moudawwana (مدونة الأسرة) est le Code de la Famille marocain, réformé en profondeur en 2004 par la Loi n°70-03. Cette réforme a marqué une avancée majeure dans l\'équilibre des droits au sein de la famille marocaine.',
          'Avant 2004, la Moudawwana de 1957-58 (droit malikite codifié) régissait les relations familiales. La réforme a substantiellement modifié les droits des époux, notamment en reconnaissant davantage d\'autonomie à la femme.',
        ],
        bullets: [
          'Capacité juridique de la femme : sans tuteur matrimonial obligatoire',
          'Âge légal du mariage : 18 ans (dérogation possible par le juge)',
          'Polygamie : conditions très restrictives, accord de la première épouse',
          'Divorce : reconnu à la femme sur demande (divorce pour discorde — shiqaq)',
          'Garde des enfants : intérêt supérieur de l\'enfant comme critère central',
        ],
      },
      {
        h2:      'Les domaines couverts par la Moudawwana',
        content: 'Le Code de la Famille traite de l\'ensemble des relations familiales, de la célébration du mariage jusqu\'à la succession.',
        bullets: [
          'Le mariage : conditions, effets, droits et obligations',
          'La dissolution : talaq, khol, divorce judiciaire (shiqaq)',
          'La filiation et la reconnaissance d\'enfant',
          'La garde des enfants (hadana) et le droit de visite',
          'La pension alimentaire (nafaqa)',
          'La succession et les héritages',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'مدونة الأسرة: إصلاح 2004',
        content: [
          'مدونة الأسرة المغربية هي قانون الأحوال الشخصية، الذي عُدِّل تعديلاً جوهرياً عام 2004 بموجب القانون رقم 70-03. وقد أحدث هذا الإصلاح تحولاً نوعياً في توازن الحقوق داخل الأسرة المغربية.',
          'قبل عام 2004، كانت مدونة الأسرة لعامَي 1957-1958 (الفقه المالكي المُدوَّن) تحكم العلاقات الأسرية. فجاء الإصلاح ليُعدِّل جوهرياً حقوق الزوجين، ولا سيما بمنح المرأة قدراً أوسع من الاستقلالية.',
        ],
        bullets: [
          'الأهلية القانونية للمرأة: دون اشتراط ولي في الزواج',
          'سن الزواج القانوني: 18 سنة (مع إمكانية الاستثناء القضائي)',
          'تعدد الزوجات: شروط تقييدية صارمة وموافقة الزوجة الأولى',
          'الطلاق: حق مكفول للمرأة بطلب (الشقاق)',
          'حضانة الأطفال: مصلحة الطفل الفضلى معياراً أساسياً',
        ],
      },
      {
        h2:      'المجالات التي تُنظِّمها مدونة الأسرة',
        content: 'تُعالج مدونة الأسرة جميع العلاقات الأسرية، من انعقاد الزواج إلى الإرث والتركة.',
        bullets: [
          'الزواج: شروطه وآثاره وحقوق الزوجين والتزاماتهما',
          'حل الرابطة الزوجية: الطلاق والشقاق والخلع والتطليق',
          'النسب والاعتراف بالطفل',
          'حضانة الأطفال وحق الزيارة',
          'النفقة',
          'الإرث والتركة',
        ],
      },
      {
        h2:      'مستجدات مدونة الأسرة: مسار الإصلاح 2025',
        content: [
          'أطلق جلالة الملك محمد السادس عام 2023 مسار مراجعة مدونة الأسرة، بتكليف هيئة متخصصة بإعداد تقرير يتضمن مقترحات للإصلاح. وتشمل المحاور الرئيسية قيد الدراسة: مساواة الذكور والإناث في الإرث، وإلغاء تعدد الزوجات، وتعزيز حقوق الأطفال المولودين خارج إطار الزواج، ووضع نظام لتقسيم الأموال المكتسبة خلال الزواج.',
          'تُجري هذه الإصلاحات المحتملة في سياق نقاش مجتمعي واسع يُوازن بين المرجعيات الدينية الإسلامية ومتطلبات المعايير الدولية لحقوق الإنسان.',
        ],
        bullets: [
          'الإرث: احتمال تحقيق المساواة بين الجنسين في بعض الحالات',
          'تعدد الزوجات: دراسة إمكانية تقييده أو إلغائه',
          'حقوق الأطفال: تعزيز الحماية بصرف النظر عن الوضع الزوجي',
          'الأموال المكتسبة: وضع نظام قانوني لتقسيم الثروة المكتسبة خلال الزواج',
          'الحضانة: مراجعة سن التحويل ومعايير المنح',
          'الكفالة: توسيع إمكانيات التبني أو تعزيز الكفالة',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'divorce-maroc',
    category:        'famille',
    title:           'Divorce au Maroc : procédures et textes juridiques',
    title_ar:        'الطلاق بالمغرب : الإجراءات والنصوص القانونية',
    metaDescription: 'Consultez les textes sur le divorce au Maroc : divorce judiciaire, talaq, khol, consentement mutuel, garde des enfants, pension.',
    metaDescription_ar: 'اطلع على النصوص المتعلقة بالطلاق بالمغرب: الطلاق القضائي، التطليق، الخلع، التراضي، حضانة الأطفال، النفقة.',
    h1:              'Divorce au Maroc',
    h1_ar:           'الطلاق بالمغرب',
    intro:           'La procédure de divorce au Maroc est encadrée par le Code de la Famille (Moudawwana). Cette page regroupe les textes disponibles dans JuriThèque sur ce sujet.',
    intro_ar:        'تُنظِّم مدونة الأسرة المغربية (المدونة) مساطر الطلاق بالمغرب. تجمع هذه الصفحة النصوص المتاحة في JuriThèque المتعلقة بهذا الموضوع.',
    legalDomain:     'civil',
    keywords:        ['divorce', 'talaq', 'khol', 'divorce judiciaire', 'garde des enfants', 'pension alimentaire', 'moudawwana', 'consentement mutuel'],
    keywords_ar:     ['الطلاق', 'الشقاق', 'التطليق', 'الخلع', 'الطلاق بالتراضي', 'الحضانة', 'النفقة', 'مدونة الأسرة'],
    searchTerms:     ['divorce', 'talaq', 'séparation'],
    relatedSlugs:    ['code-de-la-famille-maroc', 'procedure-civile-maroc'],
    faq: [
      {
        question: 'Quels types de divorce existent au Maroc ?',
        answer:   'La Moudawwana prévoit plusieurs formes : le divorce judiciaire, le talaq (répudiation encadrée), le khol (divorce à l\'initiative de l\'épouse), et le divorce par consentement mutuel.',
      },
      {
        question: 'Comment se déroule une procédure de divorce au Maroc ?',
        answer:   'La procédure se déroule devant le tribunal de la famille. Pour les détails, consultez les textes disponibles dans JuriThèque ou posez votre question à l\'assistant IA.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هي أنواع الطلاق الموجودة بالمغرب؟',
        answer:   'تنص مدونة الأسرة على عدة أشكال: الطلاق بالشقاق، والتطليق (بطلب من الزوجة)، والخلع، والطلاق بالتراضي.',
      },
      {
        question: 'كيف تسير مسطرة الطلاق بالمغرب؟',
        answer:   'تجري المسطرة أمام محكمة الأسرة. وللاطلاع على التفاصيل، راجع النصوص المتاحة في JuriThèque أو اطرح سؤالك على المساعد الذكي.',
      },
    ],
    sections: [
      {
        h2:      'Les types de divorce en droit marocain',
        content: [
          'Le Code de la Famille marocain (Moudawwana, Loi n°70-03 de 2004) consacre plusieurs voies pour dissoudre le mariage. La réforme de 2004 a profondément équilibré les droits des deux époux, en accordant à la femme des voies propres pour demander le divorce.',
          'Chaque forme de divorce produit des effets différents en termes d\'indemnisation, de pension et de garde des enfants.',
        ],
        bullets: [
          'Talaq (الطلاق) : à l\'initiative du mari, contrôlé par le juge, indemnité obligatoire à l\'épouse',
          'Shiqaq (الشقاق) : divorce pour discorde, à l\'initiative de l\'un ou l\'autre époux — le plus utilisé',
          'Khol\' (الخلع) : divorce à l\'initiative de l\'épouse contre restitution de la dot ou compensation financière',
          'Divorce judiciaire (التطليق) : prononcé par le juge pour manquements graves (abandon, violence, défaut d\'entretien)',
          'Divorce par consentement mutuel : accord des deux époux sur toutes les modalités',
        ],
      },
      {
        h2:      'Procédure devant le Tribunal de la Famille',
        content: [
          'Tout divorce au Maroc passe obligatoirement par le tribunal de la famille compétent (tribunal de première instance). Le juge de la famille tente d\'abord une conciliation entre les époux, puis désigne si nécessaire deux arbitres (hakam) de chaque famille.',
          'La durée moyenne d\'une procédure de divorce varie de 1 à 6 mois selon le type et la complexité du dossier. La présence d\'un avocat n\'est pas obligatoire mais fortement recommandée.',
        ],
        bullets: [
          'Dépôt de la requête : au tribunal de la famille du lieu du domicile conjugal',
          'Tentative de conciliation obligatoire : 1 à 2 séances devant le juge',
          'Désignation de hakam (arbitres familiaux) si nécessaire pour le shiqaq',
          'Ordonnance de référé : pension provisoire et domicile des enfants pendant la procédure',
          'Jugement de divorce : acte définitif enregistré et notifié aux parties',
          'Transcription à l\'état civil : obligatoire pour l\'opposabilité aux tiers',
        ],
      },
      {
        h2:      'Effets du divorce : garde, pension et biens communs',
        content: [
          'Le divorce entraîne des conséquences importantes sur la situation des enfants et les droits financiers des ex-époux. La Moudawwana place l\'intérêt supérieur de l\'enfant comme critère central pour la garde (hadana).',
          'La pension alimentaire (nafaqa) est fixée par le juge en fonction des revenus du père et des besoins des enfants. Elle est révisable à tout moment si la situation change.',
        ],
        bullets: [
          'Garde (hadana) : accordée à la mère en priorité jusqu\'à 7 ans (filles) / 15 ans (garçons) puis choix de l\'enfant',
          'Droit de visite du père : régulier, encadré par le jugement',
          'Nafaqa (pension alimentaire) : à la charge du père, inclut logement, alimentation et scolarité',
          'Mout\'a (indemnité de consolation) : versée par le mari en cas de talaq ou shiqaq sans faute de l\'épouse',
          'Partage des biens : selon le régime matrimonial choisi ou négociation entre les parties',
          'Iddah (délai de viduité) : 3 mois après le divorce, obligatoire pour la femme',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'أنواع الطلاق في القانون المغربي',
        content: [
          'تُرسي مدونة الأسرة المغربية (القانون رقم 70-03 لعام 2004) عدة مسالك لحل رابطة الزوجية. وقد أحدث إصلاح 2004 توازناً جوهرياً بين حقوق الزوجين، بمنح المرأة مسالك خاصة لطلب الطلاق.',
          'ويُفضي كل شكل من أشكال الطلاق إلى آثار مختلفة من حيث التعويض والنفقة وحضانة الأطفال.',
        ],
        bullets: [
          'الطلاق: بمبادرة من الزوج، يُراقبه القاضي، ويستوجب أداء تعويض للزوجة',
          'الشقاق: طلاق للشقاق بمبادرة من أي الزوجين — الأكثر استخداماً',
          'الخلع: طلاق بمبادرة من الزوجة مقابل رد الصداق أو تعويض مالي',
          'التطليق القضائي: يُصدره القاضي لإخلالات جسيمة (الهجر، والعنف، وعدم الإنفاق)',
          'الطلاق بالتراضي: اتفاق الزوجين على جميع التفاصيل',
        ],
      },
      {
        h2:      'المسطرة أمام محكمة الأسرة',
        content: [
          'يمر كل طلاق بالمغرب وجوباً عبر محكمة الأسرة المختصة (المحكمة الابتدائية). يسعى قاضي الأسرة أولاً إلى الإصلاح بين الزوجين، ثم يُعيِّن عند الاقتضاء حكمين من أسرة كل طرف.',
          'يتراوح متوسط مدة مسطرة الطلاق بين شهر وستة أشهر حسب النوع وتعقيد الملف. وحضور محامٍ غير إلزامي لكنه موصى به بشدة.',
        ],
        bullets: [
          'تقديم الطلب: إلى محكمة الأسرة في مكان السكن الزوجي',
          'محاولة الإصلاح الإلزامية: جلسة أو جلستان أمام القاضي',
          'تعيين الحكمين (من أسرة كل زوج): عند الاقتضاء في طلاق الشقاق',
          'أمر استعجالي: نفقة مؤقتة ومسكن الأطفال إبان المسطرة',
          'حكم الطلاق: وثيقة نهائية تُسجَّل وتُبلَّغ للطرفين',
          'التسجيل في الحالة المدنية: إلزامي لمواجهة الغير',
        ],
      },
      {
        h2:      'آثار الطلاق: الحضانة والنفقة والأموال المشتركة',
        content: [
          'يُفضي الطلاق إلى تداعيات جسيمة على وضع الأطفال والحقوق المالية للزوجين السابقين. وتجعل مدونة الأسرة مصلحة الطفل الفضلى معياراً محورياً في الحضانة (الحضانة).',
          'يُحدد القاضي النفقة بحسب دخل الأب واحتياجات الأطفال، وهي قابلة للمراجعة في أي وقت متى تغيرت الأوضاع.',
        ],
        bullets: [
          'الحضانة: تُمنح للأم أولاً حتى سن 7 سنوات (البنات) / 15 سنة (الأولاد)، ثم يختار الطفل',
          'حق الزيارة للأب: منتظم ومنظَّم بموجب الحكم القضائي',
          'النفقة: تقع على عاتق الأب وتشمل السكن والطعام والتعليم',
          'المتعة: تُؤدَّى من قِبل الزوج في حالة الطلاق أو الشقاق دون خطأ من الزوجة',
          'تقسيم الأموال: وفق نظام الزواج المختار أو بالتفاوض بين الطرفين',
          'العدة: ثلاثة أشهر بعد الطلاق، واجبة على الزوجة',
        ],
      },
    ],
  },

  // ── Droit Civil & Procédures ────────────────────────────────────────
  {
    lastUpdated:     '2026-06',
    slug:            'delai-de-prescription-maroc',
    category:        'civil',
    title:           'Délais de prescription au Maroc : textes juridiques',
    title_ar:        'آجال التقادم بالمغرب : النصوص القانونية',
    metaDescription: 'Consultez les textes sur les délais de prescription au Maroc : prescription civile, commerciale, pénale, comment interrompre la prescription.',
    metaDescription_ar: 'اطلع على النصوص المتعلقة بآجال التقادم بالمغرب: التقادم المدني والتجاري والجنائي وكيفية قطع التقادم.',
    h1:              'Délais de prescription au Maroc',
    h1_ar:           'آجال التقادم بالمغرب',
    intro:           'La prescription est un mécanisme juridique qui éteint les droits ou les actions après un certain délai. Cette page regroupe les textes disponibles dans JuriThèque.',
    intro_ar:        'التقادم آليةٌ قانونية تُسقط الحقوق أو الدعاوى بعد انقضاء أجل معين. تجمع هذه الصفحة النصوص المتاحة في JuriThèque.',
    legalDomain:     'civil',
    keywords:        ['prescription', 'délai de prescription', 'prescription civile', 'prescription commerciale', 'prescription pénale', 'interruption de prescription', 'forclusion'],
    keywords_ar:     ['التقادم', 'أجل التقادم', 'التقادم المدني', 'التقادم التجاري', 'التقادم الجنائي', 'قطع التقادم', 'السقوط'],
    searchTerms:     ['prescription', 'délai prescription', 'forclusion'],
    relatedSlugs:    ['procedure-civile-maroc', 'recouvrement-maroc', 'code-de-la-famille-maroc'],
    faq: [
      {
        question: 'Quel est le délai de prescription de droit commun au Maroc ?',
        answer:   'Le délai de prescription varie selon la nature de l\'action (civile, commerciale, pénale). Consultez les textes disponibles dans JuriThèque pour les délais applicables.',
      },
      {
        question: 'Comment interrompre un délai de prescription au Maroc ?',
        answer:   'La prescription peut être interrompue par certains actes juridiques comme une mise en demeure ou une action judiciaire. Consultez les textes disponibles dans JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو أجل التقادم العام بالمغرب؟',
        answer:   'يتفاوت أجل التقادم بحسب طبيعة الدعوى (مدنية، تجارية، جنائية). راجع النصوص المتاحة في JuriThèque للاطلاع على الآجال المطبقة.',
      },
      {
        question: 'كيف يمكن قطع أجل التقادم بالمغرب؟',
        answer:   'يمكن قطع التقادم ببعض الأعمال القانونية كالإنذار بالأداء أو رفع دعوى قضائية. راجع النصوص المتاحة في JuriThèque.',
      },
    ],
    sections: [
      {
        h2:      'La prescription civile et commerciale',
        content: [
          'En droit marocain, la prescription extinctive est régie principalement par le Dahir des obligations et contrats (DOC). Le délai de droit commun est de 15 ans pour les actions personnelles et mobilières. Mais de nombreuses prescriptions spéciales plus courtes s\'appliquent selon la matière.',
          'En matière commerciale, le Code de Commerce (Loi 15-95) prévoit un délai de prescription de 5 ans pour les obligations commerciales entre commerçants, réduit à 2 ans pour certaines créances (salaires, loyers commerciaux).',
        ],
        bullets: [
          'Prescription de droit commun (DOC) : 15 ans pour les actions civiles',
          'Obligations commerciales entre commerçants : 5 ans (Code de Commerce)',
          'Créances salariales : 2 ans à compter de l\'exigibilité',
          'Responsabilité délictuelle : 5 ans à compter de la connaissance du dommage',
          'Actions en garantie des vices cachés : 1 an à compter de la découverte',
          'Loyers et intérêts : prescription quinquennale (5 ans)',
        ],
      },
      {
        h2:      'La prescription pénale',
        content: [
          'En matière pénale, la prescription de l\'action publique éteint le droit de poursuivre une infraction après un certain délai. Le Code de Procédure Pénale marocain (Loi n°01-22) fixe ces délais selon la gravité de l\'infraction.',
          'La prescription pénale court à compter du jour de la commission de l\'infraction (ou de sa découverte pour les infractions clandestines). Elle est interrompue par tout acte de poursuite ou d\'instruction.',
        ],
        bullets: [
          'Crimes : 15 ans à compter de la commission',
          'Délits : 5 ans à compter de la commission',
          'Contraventions : 1 an à compter de la commission',
          'Infractions continues (recel, abandon de famille) : délai court à compter de la cessation',
          'Infractions clandestines : délai court à compter de la découverte',
          'Actes interruptifs : tout acte de poursuite, d\'instruction ou de citation à comparaître',
        ],
      },
      {
        h2:      'Interruption et suspension de la prescription',
        content: [
          'La prescription peut être interrompue ou suspendue. L\'interruption efface le délai écoulé et fait courir un nouveau délai identique. La suspension arrête temporairement le délai sans l\'effacer — il reprend son cours à la fin de la cause de suspension.',
          'Ces mécanismes sont essentiels en pratique : une action engagée in extremis peut sauver un droit sur le point d\'être prescrit.',
        ],
        bullets: [
          'Causes d\'interruption : mise en demeure, action judiciaire, reconnaissance de dette par le débiteur',
          'Causes de suspension : minorité du créancier, force majeure, moratoire légal',
          'Effet de l\'interruption : repart à zéro pour la même durée',
          'Effet de la suspension : le délai reprend là où il était arrêté',
          'Reconnaissance de dette : même partielle, interrompt la prescription',
          'Renonciation à la prescription acquise : possible, expresse ou tacite',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'التقادم المدني والتجاري',
        content: [
          'يخضع التقادم المسقط في القانون المغربي أساساً لأحكام ظهير الالتزامات والعقود (ق.ل.ع). ويبلغ أجل التقادم العام 15 سنة للدعاوى الشخصية والمنقولة، غير أن تقادمات خاصة أقصر تُطبَّق حسب الموضوع.',
          'في المادة التجارية، تنص مدونة التجارة (القانون 15-95) على أجل تقادم قدره 5 سنوات للالتزامات التجارية بين التجار، ويُخفَّض إلى سنتين لبعض الديون (الأجور، الإيجارات التجارية).',
        ],
        bullets: [
          'التقادم العام (ق.ل.ع): 15 سنة للدعاوى المدنية',
          'الالتزامات التجارية بين التجار: 5 سنوات (مدونة التجارة)',
          'الديون الأجرية: سنتان من تاريخ الاستحقاق',
          'المسؤولية التقصيرية: 5 سنوات من يوم العلم بالضرر',
          'دعاوى ضمان العيوب الخفية: سنة واحدة من تاريخ الاكتشاف',
          'الأكرية والفوائد: تقادم خمسي (5 سنوات)',
        ],
      },
      {
        h2:      'التقادم الجنائي',
        content: [
          'في المادة الجنائية، يُسقط تقادم الدعوى العمومية حق المتابعة على جريمة ما بعد انقضاء أجل معين. يُحدد قانون المسطرة الجنائية المغربي (القانون 01-22) هذه الآجال حسب درجة خطورة الجريمة.',
          'يسري التقادم الجنائي من يوم ارتكاب الجريمة (أو يوم اكتشافها للجرائم الخفية). وينقطع بأي إجراء للمتابعة أو التحقيق.',
        ],
        bullets: [
          'الجنايات: 15 سنة من تاريخ الارتكاب',
          'الجنح: 5 سنوات من تاريخ الارتكاب',
          'المخالفات: سنة واحدة من تاريخ الارتكاب',
          'الجرائم المستمرة (إخفاء الأشياء، الإهمال الأسري): الأجل يسري من يوم التوقف',
          'الجرائم الخفية: الأجل يسري من يوم الاكتشاف',
          'الأعمال القاطعة للتقادم: أي إجراء للمتابعة أو التحقيق أو الاستدعاء للمثول',
        ],
      },
      {
        h2:      'قطع التقادم ووقفه',
        content: [
          'يمكن قطع التقادم أو إيقافه. القطع يمحو الأجل المنقضي ويبدأ أجل جديد مماثل. أما الوقف فيُعلِّق الأجل مؤقتاً دون محوه — ويستأنف سريانه عند زوال سبب الوقف.',
          'هذان المفهومان بالغا الأهمية من الناحية العملية: إذ يمكن للدعوى المرفوعة في اللحظة الأخيرة أن تُنقذ حقاً على وشك السقوط.',
        ],
        bullets: [
          'أسباب القطع: الإنذار بالأداء، رفع الدعوى القضائية، اعتراف المدين بالدين',
          'أسباب الوقف: قصر الدائن، القوة القاهرة، الوقف القانوني للتنفيذ',
          'أثر القطع: يُعاد احتساب الأجل من الصفر بنفس المدة',
          'أثر الوقف: يستأنف الأجل من حيث توقف',
          'الاعتراف بالدين: ولو جزئياً، يقطع التقادم',
          'التنازل عن التقادم المكتسب: ممكن، صراحةً أو ضمناً',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'procedure-civile-maroc',
    category:        'civil',
    title:           'Procédure civile au Maroc : textes et règles applicables',
    title_ar:        'قانون المسطرة المدنية بالمغرب : النصوص والقواعد المطبقة',
    metaDescription: 'Consultez les textes sur la procédure civile marocaine : compétence des tribunaux, délais, appel, cassation, exécution des jugements.',
    metaDescription_ar: 'اطلع على النصوص المتعلقة بقانون المسطرة المدنية المغربية: اختصاص المحاكم، الآجال، الاستئناف، النقض، تنفيذ الأحكام.',
    h1:              'Procédure civile au Maroc',
    h1_ar:           'قانون المسطرة المدنية بالمغرب',
    intro:           'La procédure civile encadre le déroulement des procès devant les tribunaux civils marocains. Cette page regroupe les textes disponibles dans JuriThèque.',
    intro_ar:        'تُؤطر المسطرة المدنية سير الدعاوى أمام المحاكم المدنية المغربية. تجمع هذه الصفحة النصوص المتاحة في JuriThèque.',
    legalDomain:     'civil',
    keywords:        ['procédure civile', 'tribunal', 'compétence', 'appel', 'cassation', 'délais procéduraux', 'exécution jugement', 'signification'],
    keywords_ar:     ['المسطرة المدنية', 'المحكمة', 'الاختصاص', 'الاستئناف', 'النقض', 'الآجال الإجرائية', 'تنفيذ الحكم', 'التبليغ'],
    searchTerms:     ['procédure civile', 'code procédure civile', 'tribunal'],
    relatedSlugs:    ['recouvrement-maroc', 'delai-de-prescription-maroc', 'divorce-maroc'],
    faq: [
      {
        question: 'Quel est le texte de base de la procédure civile marocaine ?',
        answer:   'La procédure civile est régie par le Code de Procédure Civile marocain. Les textes disponibles sont consultables dans JuriThèque.',
      },
      {
        question: 'Quels sont les délais d\'appel au Maroc ?',
        answer:   'Les délais d\'appel varient selon le type de décision. Consultez les textes disponibles dans JuriThèque ou posez votre question à l\'assistant IA.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو النص الأساسي لقانون المسطرة المدنية بالمغرب؟',
        answer:   'تخضع المسطرة المدنية لقانون المسطرة المدنية المغربي. النصوص المتاحة متاحة للاطلاع في JuriThèque.',
      },
      {
        question: 'ما هي آجال الاستئناف بالمغرب؟',
        answer:   'تتفاوت آجال الاستئناف حسب نوع القرار. راجع النصوص المتاحة في JuriThèque أو اطرح سؤالك على المساعد الذكي.',
      },
    ],
    sections: [
      {
        h2:      'Organisation des tribunaux civils marocains',
        content: [
          'Le système judiciaire civil marocain est organisé en trois degrés. Le premier degré comprend les tribunaux de première instance (TPI) et les tribunaux de commerce pour les litiges commerciaux. Les cours d\'appel constituent le deuxième degré, et la Cour de Cassation le degré suprême.',
          'Depuis la réforme de l\'organisation judiciaire (Loi n°38-15 de 2015), les tribunaux administratifs et les cours d\'appel administratives ont été institutionnalisés pour traiter les litiges avec l\'administration.',
        ],
        bullets: [
          'Tribunaux de première instance (TPI) : litiges civils, familiaux, immobiliers',
          'Tribunaux de commerce : litiges commerciaux entre commerçants ou sociétés',
          'Cours d\'appel : second degré de juridiction, réexamen des jugements',
          'Cour de Cassation : contrôle de la légalité, ne rejuge pas les faits',
          'Tribunaux administratifs : contentieux administratif (marchés, permis, fonctionnaires)',
          'Centres de justice de proximité : litiges de faible valeur, état civil simple',
        ],
      },
      {
        h2:      'Les étapes d\'une procédure civile',
        content: [
          'Une procédure civile au Maroc commence par le dépôt d\'une requête ou d\'une assignation au greffe du tribunal compétent. Le juge désigné convoque les parties, entend leurs arguments et les preuves, puis rend son jugement.',
          'La durée d\'une procédure civile varie de quelques mois à plusieurs années selon la complexité et le tribunal. Les parties peuvent être représentées par un avocat, dont la présence est obligatoire devant la Cour de Cassation.',
        ],
        bullets: [
          '1. Dépôt de la requête au greffe avec paiement des frais de justice',
          '2. Convocation des parties par voie de signification (huissier ou greffe)',
          '3. Instruction : échange de conclusions, preuves, expertises si nécessaire',
          '4. Audience de plaidoirie : arguments oraux des avocats',
          '5. Délibéré : le tribunal rend son jugement (délai variable)',
          '6. Signification du jugement aux parties pour faire courir les délais de recours',
        ],
      },
      {
        h2:      'Les voies de recours : appel et cassation',
        content: [
          'Tout jugement peut faire l\'objet d\'un appel devant la cour d\'appel compétente. L\'appel doit être interjeté dans un délai de 30 jours à compter de la signification du jugement (1 mois pour les jugements commerciaux). Il a un effet suspensif, sauf en référé.',
          'Le pourvoi en cassation devant la Cour de Cassation n\'est pas un troisième degré de juridiction : il contrôle uniquement la légalité de la décision, pas les faits. Le délai est de 30 jours à compter de la signification de l\'arrêt d\'appel.',
        ],
        bullets: [
          'Délai d\'appel : 30 jours à compter de la signification (en général)',
          'Appel en matière de référé : 15 jours',
          'Effet suspensif de l\'appel : l\'exécution du jugement est suspendue sauf exception',
          'Pourvoi en cassation : 30 jours, délai de rigueur — ministère d\'avocat obligatoire',
          'Arrêt de cassation : renvoie devant une autre juridiction de même rang',
          'Tierce opposition : recours ouvert aux tiers lésés par un jugement',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'تنظيم المحاكم المدنية بالمغرب',
        content: [
          'يتكون الجهاز القضائي المدني المغربي من ثلاث درجات. وتضم الدرجة الأولى المحاكم الابتدائية والمحاكم التجارية للنزاعات التجارية. وتشكل محاكم الاستئناف الدرجة الثانية، فيما تمثل محكمة النقض الدرجة العليا.',
          'منذ إصلاح التنظيم القضائي (القانون 38-15 لعام 2015)، أُُسِّست المحاكم الإدارية ومحاكم الاستئناف الإدارية للنظر في النزاعات مع الإدارة.',
        ],
        bullets: [
          'المحاكم الابتدائية: النزاعات المدنية والأسرية والعقارية',
          'المحاكم التجارية: النزاعات التجارية بين التجار أو الشركات',
          'محاكم الاستئناف: الدرجة الثانية للتقاضي، مراجعة الأحكام',
          'محكمة النقض: مراقبة المشروعية، لا تُعيد النظر في الوقائع',
          'المحاكم الإدارية: النزاعات الإدارية (الصفقات، الرخص، الموظفون)',
          'مراكز العدالة القريبة: النزاعات الصغيرة ومسائل الحالة المدنية البسيطة',
        ],
      },
      {
        h2:      'مراحل سير الدعوى المدنية',
        content: [
          'تبدأ الدعوى المدنية بالمغرب بإيداع مقال أو استدعاء لدى كتابة ضبط المحكمة المختصة. يُعيِّن رئيس المحكمة قاضياً يُستدعى بموجبه الطرفان، ويستمع إلى حججهما وأدلتهما ثم يُصدر حكمه.',
          'تتراوح مدة الدعوى المدنية بين أشهر وسنوات حسب التعقيد والمحكمة. يمكن للأطراف الاستعانة بمحامٍ، وهو إلزامي أمام محكمة النقض.',
        ],
        bullets: [
          '1. إيداع المقال لدى كتابة الضبط مع أداء الرسوم القضائية',
          '2. استدعاء الأطراف عبر التبليغ (المفوض القضائي أو كتابة الضبط)',
          '3. التحقيق: تبادل المذكرات والأدلة والخبرات عند الاقتضاء',
          '4. جلسة المرافعة: الحجج الشفهية للمحامين',
          '5. المداولة: تُصدر المحكمة حكمها (أجل متغير)',
          '6. تبليغ الحكم للأطراف لإسراء آجال الطعن',
        ],
      },
      {
        h2:      'طرق الطعن: الاستئناف والنقض',
        content: [
          'يجوز الطعن في أي حكم بالاستئناف أمام محكمة الاستئناف المختصة. يجب تقديم الاستئناف داخل أجل 30 يوماً من تاريخ تبليغ الحكم (شهر واحد للأحكام التجارية). وله أثر موقف إلا في قضايا الاستعجال.',
          'الطعن بالنقض أمام محكمة النقض ليس درجة ثالثة للتقاضي: إذ يراقب مشروعية القرار فقط دون الوقائع. وأجله 30 يوماً من تاريخ تبليغ قرار الاستئناف.',
        ],
        bullets: [
          'أجل الاستئناف: 30 يوماً من تاريخ التبليغ (بوجه عام)',
          'الاستئناف في القضايا الاستعجالية: 15 يوماً',
          'الأثر الموقف للاستئناف: يُعلَّق تنفيذ الحكم إلا استثناءً',
          'الطعن بالنقض: 30 يوماً، أجل قاطع — نيابة المحامي إلزامية',
          'قرار النقض: يُحيل القضية إلى محكمة أخرى من نفس الدرجة',
          'تعرض الغير الخارج عن الخصومة: طريق طعن متاح للأغيار المتضررين من حكم',
        ],
      },
    ],
  },

  // ── Collectivités Territoriales ─────────────────────────────────────
  {
    lastUpdated:     '2026-06',
    slug:            'collectivites-territoriales-maroc',
    category:        'collectivites',
    title:           'Collectivités Territoriales au Maroc : lois et textes applicables',
    title_ar:        'الجماعات الترابية بالمغرب : القوانين والنصوص المطبقة',
    metaDescription: 'Consultez les textes juridiques sur les collectivités territoriales au Maroc : Lois Organiques (LOC), régions, communes, préfectures, élus locaux et finances locales.',
    metaDescription_ar: 'اطلع على النصوص القانونية للجماعات الترابية بالمغرب : القوانين التنظيمية، الجهات، الجماعات، العمالات، المنتخبون المحليون والمالية المحلية.',
    h1:              'Collectivités Territoriales au Maroc',
    h1_ar:           'الجماعات الترابية بالمغرب',
    intro:           'Depuis la réforme de régionalisation avancée de 2015, les collectivités territoriales (régions, préfectures/provinces, communes) disposent d\'un cadre juridique propre fondé sur trois Lois Organiques. Cette page regroupe les textes disponibles dans JuriThèque sur ce domaine.',
    intro_ar:        'منذ إصلاح الجهوية المتقدمة عام 2015، تتوفر الجماعات الترابية (الجهات، العمالات/الأقاليم، الجماعات) على إطار قانوني خاص مؤسَّس على ثلاثة قوانين تنظيمية. تجمع هذه الصفحة النصوص المتاحة في JuriThèque في هذا المجال.',
    legalDomain:     'collectivites',
    keywords:        ['collectivités territoriales', 'LOC 111-14', 'LOC 112-14', 'LOC 113-14', 'régions Maroc', 'communes Maroc', 'préfectures', 'élu local', 'conseil régional', 'conseil communal', 'régionalisation avancée', 'budget communal', 'finances locales'],
    keywords_ar:     ['الجماعات الترابية', 'القانون التنظيمي 111-14', 'القانون التنظيمي 113-14', 'الجهات المغرب', 'الجماعات المغرب', 'العمالات', 'المنتخب المحلي', 'المجلس الجهوي', 'المجلس الجماعي', 'الجهوية المتقدمة', 'الميزانية الجماعية', 'المالية المحلية'],
    searchTerms:     ['collectivités territoriales', 'communes maroc', 'régions maroc', 'loi organique collectivités'],
    relatedSlugs:    ['revocation-elu-maroc', 'procedure-civile-maroc'],
    faq: [
      {
        question: 'Quels sont les textes fondamentaux des collectivités territoriales au Maroc ?',
        answer:   'La réforme de 2015 a produit trois Lois Organiques : la LOC 111-14 relative aux Régions, la LOC 112-14 relative aux Préfectures et Provinces, et la LOC 113-14 relative aux Communes. Ces textes sont disponibles dans JuriThèque.',
      },
      {
        question: 'Quels sont les pouvoirs d\'une commune au Maroc ?',
        answer:   'Les communes exercent des compétences propres, partagées et transférables dans les domaines du développement local, de l\'urbanisme, des services de base et des finances locales. Consultez la LOC 113-14 disponible dans JuriThèque.',
      },
      {
        question: 'Comment fonctionne le conseil régional au Maroc ?',
        answer:   'Le conseil régional est l\'organe délibérant de la région. Son fonctionnement, ses attributions et son mode d\'élection sont définis par la LOC 111-14. Consultez les textes disponibles dans JuriThèque.',
      },
      {
        question: 'Qu\'est-ce que la révocation d\'un élu local au Maroc ?',
        answer:   'La révocation (ou éviction) est une procédure permettant de mettre fin au mandat d\'un élu local dans des cas prévus par la loi. Les conditions et procédures sont définies dans les Lois Organiques. Consultez le guide dédié sur JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هي النصوص الأساسية للجماعات الترابية بالمغرب؟',
        answer:   'أفرز إصلاح 2015 ثلاثة قوانين تنظيمية : القانون 111-14 المتعلق بالجهات، والقانون 112-14 المتعلق بالعمالات والأقاليم، والقانون 113-14 المتعلق بالجماعات. هذه النصوص متاحة في JuriThèque.',
      },
      {
        question: 'ما هي صلاحيات الجماعة بالمغرب؟',
        answer:   'تمارس الجماعات اختصاصات ذاتية ومشتركة وقابلة للنقل في مجالات التنمية المحلية والتعمير والخدمات الأساسية والمالية المحلية. راجع القانون 113-14 المتاح في JuriThèque.',
      },
      {
        question: 'كيف يعمل المجلس الجهوي بالمغرب؟',
        answer:   'المجلس الجهوي هو الهيئة التداولية للجهة. يُحدد القانون 111-14 طريقة عمله واختصاصاته ونمط انتخابه. راجع النصوص المتاحة في JuriThèque.',
      },
      {
        question: 'ما هو مسطرة إعفاء المنتخب المحلي بالمغرب؟',
        answer:   'الإعفاء مسطرة تُنهى بموجبها عهدة المنتخب المحلي في الحالات المنصوص عليها قانوناً. تُحدد القوانين التنظيمية الشروط والإجراءات. راجع الدليل المخصص في JuriThèque.',
      },
    ],
    sections: [
      {
        h2:      'La réforme de 2015 : trois lois organiques',
        content: [
          'La réforme constitutionnelle de 2011 a consacré le principe de la régionalisation avancée. Trois Lois Organiques adoptées en 2015 constituent le nouveau cadre juridique des collectivités territoriales, remplaçant la Charte Communale de 2002.',
        ],
        bullets: [
          'LOC n°111-14 : relative aux Régions (16 régions depuis la réforme)',
          'LOC n°112-14 : relative aux Préfectures et Provinces',
          'LOC n°113-14 : relative aux Communes (urbaines et rurales)',
        ],
      },
      {
        h2:      'Compétences et gouvernance locale',
        content: 'Chaque collectivité dispose de compétences propres, partagées et transférables, gérées dans le cadre du principe de libre administration.',
        bullets: [
          'Compétences propres : exercées de manière exclusive par la collectivité',
          'Compétences partagées : avec l\'État et d\'autres niveaux territoriaux',
          'Compétences transférables : progressivement déléguées par l\'État',
          'Libre administration : les collectivités gèrent librement leurs affaires',
          'Contrôle de légalité : exercé a posteriori par le wali ou gouverneur',
          'Finances locales : budget propre, fiscalité locale, dotations de l\'État',
        ],
      },
      {
        h2:      'Finances locales et budget des collectivités',
        content: [
          'Les collectivités territoriales disposent de ressources financières propres pour assurer leurs missions. Leurs finances sont encadrées par la Loi Organique relative aux finances des collectivités territoriales et par les décrets d\'application.',
          'La Trésorerie Générale du Royaume (TGR) assure le contrôle et l\'exécution financière des budgets locaux, garantissant la régularité des dépenses et recettes.',
        ],
        bullets: [
          'Ressources fiscales propres : taxe professionnelle, taxe d\'habitation, taxes locales',
          'Dotations de l\'État : TVA partagée, Fonds de Mise à Niveau Sociale (FMNS)',
          'Emprunts : autorisés sous conditions pour les investissements structurants',
          'Budget primitif voté en session d\'octobre par le conseil',
          'Contrôle a priori de la TGR sur les dépenses d\'engagement',
          'Cour Régionale des Comptes : contrôle a posteriori de la gestion financière',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'إصلاح 2015 : ثلاثة قوانين تنظيمية',
        content: [
          'كرّس الإصلاح الدستوري لعام 2011 مبدأ الجهوية المتقدمة. وتُشكِّل القوانين التنظيمية الثلاثة المعتمدة عام 2015 الإطار القانوني الجديد للجماعات الترابية، خلفاً للميثاق الجماعي لعام 2002.',
        ],
        bullets: [
          'القانون التنظيمي رقم 111-14: المتعلق بالجهات (16 جهة منذ الإصلاح)',
          'القانون التنظيمي رقم 112-14: المتعلق بالعمالات والأقاليم',
          'القانون التنظيمي رقم 113-14: المتعلق بالجماعات (الحضرية والقروية)',
        ],
      },
      {
        h2:      'الاختصاصات والحكامة المحلية',
        content: 'تتمتع كل جماعة ترابية باختصاصات ذاتية ومشتركة وقابلة للنقل، يُمارَس تدبيرها في إطار مبدأ التدبير الحر.',
        bullets: [
          'الاختصاصات الذاتية: تمارسها الجماعة الترابية بصفة حصرية',
          'الاختصاصات المشتركة: مع الدولة وغيرها من مستويات التراب',
          'الاختصاصات القابلة للنقل: تُفوَّض تدريجياً من الدولة',
          'التدبير الحر: تُدبِّر الجماعات شؤونها بحرية',
          'مراقبة المشروعية: تُمارَس بعدياً من قِبَل الوالي أو العامل',
          'المالية المحلية: ميزانية خاصة، جبايات محلية، مخصصات الدولة',
        ],
      },
      {
        h2:      'المالية المحلية وميزانية الجماعات الترابية',
        content: [
          'تتوفر الجماعات الترابية على موارد مالية خاصة لأداء مهامها. تُؤطر ماليتها القانونُ التنظيمي للمالية المحلية والمراسيم التطبيقية.',
          'تضطلع الخزينة العامة للمملكة بمراقبة وتنفيذ الميزانيات المحلية، ضماناً لانتظام النفقات والمداخيل.',
        ],
        bullets: [
          'الموارد الجبائية الذاتية: الضريبة المهنية وضريبة السكن والرسوم المحلية',
          'مخصصات الدولة: حصة من الضريبة على القيمة المضافة وصندوق التأهيل الاجتماعي',
          'الاقتراض: مسموح به وفق شروط للاستثمار في البنيات التحتية',
          'الميزانية الأولية: تُصادق عليها الجلسة الاستثنائية لأكتوبر',
          'الرقابة القبلية للخزينة العامة: على نفقات الالتزام',
          'المجلس الجهوي للحسابات: رقابة بعدية على التدبير المالي',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'revocation-elu-maroc',
    category:        'collectivites',
    title:           'Révocation d\'un élu local au Maroc : procédure et textes',
    metaDescription: 'Textes juridiques sur la révocation, l\'éviction et l\'exclusion d\'un élu dans les collectivités territoriales au Maroc : conditions, procédure et recours.',
    h1:              'Révocation d\'un élu dans les collectivités territoriales',
    intro:           'La révocation (ou éviction) d\'un élu est une procédure d\'exception encadrée strictement par les Lois Organiques de 2015. Elle peut concerner le président d\'un conseil régional, communal ou préfectoral, ainsi que les membres de ces conseils. Cette page regroupe les textes applicables disponibles dans JuriThèque.',
    legalDomain:     'collectivites',
    keywords:        ['révocation élu', 'éviction élu', 'exclusion élu', 'déchéance mandat', 'collectivités territoriales', 'LOC 111-14', 'LOC 113-14', 'président conseil communal', 'mandat élu local', 'procédure révocation'],
    searchTerms:     ['révocation élu maroc', 'éviction élu collectivité', 'déchéance mandat local'],
    relatedSlugs:    ['collectivites-territoriales-maroc', 'procedure-civile-maroc'],
    featuredVideoIds: ['JtJ4LqtOPGc'],
    faq: [
      {
        question: 'Dans quels cas un élu local peut-il être révoqué au Maroc ?',
        answer:   'Les Lois Organiques de 2015 prévoient des cas de révocation : comportement contraire à l\'honneur, condamnation pénale, abandon de poste, perte des conditions d\'éligibilité. Les détails figurent dans les textes disponibles dans JuriThèque.',
      },
      {
        question: 'Qui peut initier une procédure de révocation d\'un élu local ?',
        answer:   'La procédure peut être initiée par le ministre de l\'Intérieur ou le wali/gouverneur selon les cas, sur la base des dispositions des Lois Organiques 111-14, 112-14 ou 113-14.',
      },
      {
        question: 'Quelle est la différence entre révocation, éviction et exclusion d\'un élu ?',
        answer:   'Ces termes désignent des procédures distinctes : la révocation met fin au mandat pour faute, l\'éviction résulte d\'une inéligibilité survenue en cours de mandat, et l\'exclusion sanctionne un comportement spécifique. Consultez les textes disponibles dans JuriThèque.',
      },
    ],
  },

  // ── Hub MRE — Marocains Résidant à l'Étranger ──────────────────────────
  {
    lastUpdated:     '2026-06',
    slug:            'mre-droits-juridiques-maroc',
    category:        'mre',
    title:           'MRE : Vos droits juridiques au Maroc en 2026',
    metaDescription: 'Vous êtes Marocain de l\'étranger ? Découvrez vos droits en matière de propriété, héritage, famille et investissement au Maroc. Textes officiels inclus.',
    h1:              'MRE : Vos droits juridiques au Maroc',
    intro:           'Les Marocains Résidant à l\'Étranger (MRE) conservent l\'intégralité de leurs droits civils, patrimoniaux et familiaux au Maroc. Cette page synthétise les droits essentiels garantis par la loi marocaine, avec les textes officiels disponibles dans JuriThèque.',
    legalDomain:     'civil',
    keywords:        ['droits MRE', 'Marocains résidant étranger', 'droits juridiques diaspora', 'loi MRE Maroc', 'protection juridique diaspora marocaine', 'nationalité marocaine étranger'],
    searchTerms:     ['nationalité marocaine', 'code famille', 'droits réels'],
    specificNumbers: ['62-06', '70-03', '39-08', '65-99', '18-00'],
    relatedSlugs:    ['heritage-succession-mre-maroc', 'investir-maroc-mre', 'achat-immobilier-maroc-mre', 'double-nationalite-droit-maroc'],
    sections: [
      {
        icon: '👤',
        h2:   'Qui est considéré MRE selon la loi marocaine ?',
        content: [
          'La notion de Marocain Résidant à l\'Étranger (MRE) désigne tout ressortissant marocain résidant de façon régulière hors du Maroc, qu\'il soit immigré de première génération ou descendant de Marocains nés à l\'étranger ayant conservé la nationalité marocaine.',
          'Le Dahir du 6 septembre 1958 portant Code de la nationalité marocaine (modifié par la loi 62-06) précise les conditions d\'acquisition et de conservation de la nationalité marocaine, qui constitue le fondement de tous les droits au Maroc.',
        ],
        bullets: [
          'Marocains nés au Maroc ayant émigré à l\'étranger',
          'Enfants de Marocains nés à l\'étranger ayant conservé la nationalité',
          'Marocaines mariées à des étrangers (la nationalité marocaine se transmet par les deux parents depuis 2007)',
          'Personnes ayant acquis la nationalité d\'un autre pays sans perdre la nationalité marocaine',
        ],
      },
      {
        icon: '🏠',
        h2:   'Droit à la propriété immobilière au Maroc',
        content: [
          'Tout Marocain, qu\'il réside au Maroc ou à l\'étranger, peut librement acquérir, posséder et vendre des biens immobiliers sur le territoire marocain. Ce droit est garanti par la Constitution de 2011 et le Code des droits réels (Loi 39-08).',
          'Les MRE bénéficient en outre de facilités bancaires spécifiques : les banques marocaines proposent des crédits immobiliers adaptés, et le transfert des fonds depuis l\'étranger est facilité par l\'Office des Changes sous réserve de respecter la réglementation des changes.',
        ],
        bullets: [
          'Aucune restriction d\'acquisition pour les ressortissants marocains',
          'Transfert des fonds autorisé via le système bancaire agréé',
          'Exonération de la TVA sur la première acquisition d\'un logement social sous conditions',
          'Possibilité de rapatrier le produit de la vente dans la devise d\'origine',
        ],
      },
      {
        icon: '⚖️',
        h2:   'Droits de succession et héritage pour les MRE',
        content: [
          'Le droit successoral marocain s\'applique aux nationaux marocains quel que soit leur lieu de résidence. La succession des biens situés au Maroc est régie par le droit marocain, qui suit les règles de la jurisprudence islamique (fiqh) codifiées par la Moudawwana (Loi 70-03).',
          'Les MRE héritent et transmettent leurs biens selon les mêmes règles que les Marocains résidant au Maroc. La procédure de succession peut être gérée par procuration, ce qui permet aux MRE de traiter les formalités à distance.',
        ],
      },
      {
        icon: '🗳️',
        h2:   'Droits politiques et consulaires',
        content: [
          'Les MRE disposent du droit de vote aux élections législatives et locales marocaines. Depuis les réformes constitutionnelles de 2011, la représentation des MRE a été renforcée. Les ambassades et consulats marocains constituent le premier point de contact pour les démarches administratives.',
        ],
        bullets: [
          'Droit de vote aux élections (inscription obligatoire au Maroc ou via les consulats)',
          'Possibilité d\'obtenir un passeport biométrique marocain dans les consulats',
          'Actes d\'état civil (naissance, mariage, décès) enregistrables dans les consulats',
          'Légalisation de documents pour usage au Maroc',
        ],
      },
      {
        icon: '💼',
        h2:   'Comment faire valoir vos droits depuis l\'étranger ?',
        content: [
          'Les MRE peuvent exercer la quasi-totalité de leurs droits au Maroc via des mandataires (procuration notariée), les services consulaires ou directement lors de séjours au Maroc. La procuration est l\'outil juridique clé : établie chez un notaire dans le pays de résidence et légalisée, elle permet à un représentant d\'agir en votre nom pour une vente immobilière, une succession, ou tout acte juridique.',
        ],
        bullets: [
          'Procuration générale ou spéciale établie chez un notaire local + légalisation',
          'Apostille pour les pays signataires de la Convention de La Haye',
          'Fondation Mohammed V pour les MRE : assistance et orientation',
          'Ministère chargé des MRE pour les questions institutionnelles',
        ],
      },
    ],
    faq: [
      {
        question: 'Un MRE peut-il voter au Maroc ?',
        answer:   'Oui. Les Marocains résidant à l\'étranger peuvent voter aux élections législatives et locales marocaines. Ils doivent être inscrits sur les listes électorales, soit au Maroc lors d\'un séjour, soit via les représentations diplomatiques.',
      },
      {
        question: 'Un MRE perd-il sa nationalité s\'il acquiert une autre nationalité ?',
        answer:   'Non, en règle générale. Le Maroc tolère la double nationalité en pratique. La loi sur la nationalité (Dahir 1958 modifié) ne prévoit pas la déchéance automatique en cas d\'acquisition d\'une nationalité étrangère pour les Marocains d\'origine.',
      },
      {
        question: 'Comment un MRE peut-il gérer ses biens au Maroc à distance ?',
        answer:   'Via une procuration notariée établie dans le pays de résidence, légalisée et apostillée. Cette procuration permet à un mandataire de gérer, vendre ou acheter des biens en votre nom au Maroc.',
      },
      {
        question: 'La succession d\'un MRE décédé à l\'étranger est-elle soumise au droit marocain ?',
        answer:   'Les biens situés au Maroc sont soumis au droit successoral marocain. Pour les biens à l\'étranger, c\'est le droit du pays de résidence ou de situation des biens qui s\'applique généralement.',
      },
      {
        question: 'Quels organismes peuvent aider les MRE dans leurs démarches juridiques ?',
        answer:   'La Fondation Mohammed V pour la Solidarité, le Ministère délégué chargé des Marocains résidant à l\'étranger, ainsi que les services consulaires marocains proposent des orientations et accompagnements pour les démarches juridiques et administratives.',
      },
    ],
    title_ar:           'المغاربة المقيمون بالخارج: حقوقكم القانونية في المغرب 2026',
    metaDescription_ar: 'هل أنتم من المغاربة المقيمين بالخارج؟ تعرفوا على حقوقكم في مجال الملكية والميراث والأسرة والاستثمار في المغرب، مع النصوص القانونية الرسمية.',
    h1_ar:              'المغاربة المقيمون بالخارج: حقوقكم القانونية في المغرب',
    intro_ar:           'يحتفظ المغاربة المقيمون بالخارج بكامل حقوقهم المدنية والمالية والأسرية في المغرب. تُلخِّص هذه الصفحة الحقوق الأساسية التي يكفلها القانون المغربي، مع النصوص الرسمية المتاحة على منصة جوريتيك.',
    keywords_ar:        ['حقوق المغاربة المقيمين بالخارج', 'حقوق الجالية المغربية', 'قانون الجنسية المغربية', 'تحويل الأموال المغرب', 'الإرث والتركة للمغاربة بالخارج', 'الملكية العقارية للمغاربة بالخارج'],
    faq_ar: [
      {
        question: 'هل يحق للمغاربة المقيمين بالخارج التصويت في المغرب؟',
        answer:   'نعم. يحق للمغاربة المقيمين بالخارج المشاركة في الانتخابات التشريعية والمحلية المغربية، شريطة التسجيل في اللوائح الانتخابية داخل المغرب أو عبر التمثيليات الدبلوماسية.',
      },
      {
        question: 'هل يفقد المغربي جنسيته إذا اكتسب جنسية أجنبية؟',
        answer:   'لا، في الغالب. يتسامح المغرب عملياً مع ازدواجية الجنسية. إذ لا ينص ظهير الجنسية لعام 1958 (المعدَّل) على إسقاطها تلقائياً عن المغاربة الأصليين الذين يكتسبون جنسية أجنبية.',
      },
      {
        question: 'كيف يمكن للمغربي المقيم بالخارج تدبير أملاكه في المغرب عن بُعد؟',
        answer:   'عبر توكيل رسمي محرَّر لدى موثق في بلد الإقامة، ومُصادَق عليه ومختوم بالأبوستيل. يُخوِّل هذا التوكيلُ المنابَ بتدبير أملاكه أو بيعها أو شرائها نيابةً عنه في المغرب.',
      },
      {
        question: 'هل تخضع تركة المغربي المتوفى في الخارج للقانون المغربي؟',
        answer:   'تخضع الأموال الموجودة في المغرب لأحكام قانون الإرث المغربي. أما الأموال الموجودة في الخارج فيُطبَّق عليها في الغالب قانون دولة الإقامة أو الموقع.',
      },
      {
        question: 'ما الجهات التي تُساعد المغاربة المقيمين بالخارج في إجراءاتهم القانونية؟',
        answer:   'تُقدِّم مؤسسة محمد الخامس للتضامن والوزارة المكلفة بالمغاربة المقيمين بالخارج والخدمات القنصلية المغربية التوجيهَ والمواكبةَ اللازمَين للإجراءات القانونية والإدارية.',
      },
    ],
    sections_ar: [
      {
        icon: '👤',
        h2:   'من هو المغربي المقيم بالخارج وفق القانون المغربي؟',
        content: [
          'يُقصَد بالمغربي المقيم بالخارج كلُّ مواطن مغربي يقيم بصفة منتظمة خارج أرض الوطن، سواء كان من الجيل الأول المهاجر أو من المنحدرين من آباء مغاربة وُلدوا في الخارج واحتفظوا بالجنسية المغربية.',
          'يُحدِّد ظهير السادس من سبتمبر 1958 المتعلق بالجنسية المغربية (المعدَّل بالقانون 62-06) شروط اكتسابها والحفاظ عليها، إذ تُشكِّل هذه الجنسية الأساسَ الذي تقوم عليه جميع الحقوق داخل المغرب.',
        ],
        bullets: [
          'المغاربة المولودون في المغرب والمهاجرون إلى الخارج',
          'أبناء المغاربة المولودون في الخارج والحاملون للجنسية المغربية',
          'المرأة المغربية المتزوجة من أجنبي (تنتقل الجنسية عبر كلا الأبوين منذ عام 2007)',
          'الأشخاص الذين اكتسبوا جنسية دولة أخرى دون فقدان الجنسية المغربية',
        ],
      },
      {
        icon: '🏠',
        h2:   'حق الملكية العقارية في المغرب',
        content: [
          'يحق لكل مغربي، سواء أقام داخل المغرب أو خارجه، اقتناء الأموال العقارية في المغرب وامتلاكها والتصرف فيها بيعاً وشراءً بكامل الحرية. ويكفل هذا الحقَّ دستورُ 2011 وقانون الحقوق العينية (القانون 39-08).',
          'ويستفيد المغاربة المقيمون بالخارج علاوةً على ذلك من تسهيلات مصرفية خاصة؛ إذ تطرح البنوك المغربية قروضاً عقارية ملائمة، كما يُيسِّر مكتب الصرف تحويل الأموال القادمة من الخارج وفق الضوابط المنظِّمة لذلك.',
        ],
        bullets: [
          'لا قيود على الاقتناء بالنسبة للمواطنين المغاربة',
          'تحويل الأموال مسموح به عبر الجهاز المصرفي المرخَّص',
          'إعفاء من الضريبة على القيمة المضافة عند الاقتناء الأول للسكن الاجتماعي وفق الشروط المحددة',
          'إمكانية إرجاع مقابل البيع بعملة الإقامة',
        ],
      },
      {
        icon: '⚖️',
        h2:   'حقوق الإرث والتركة للمغاربة المقيمين بالخارج',
        content: [
          'يسري قانون الإرث المغربي على المواطنين المغاربة أينما كان موطنهم. وتخضع تركة الأموال الواقعة في المغرب للقانون المغربي الذي يُعمِّق أحكام الفقه الإسلامي المُقنَّنة في مدونة الأسرة (القانون 70-03).',
          'يَرِث المغاربة المقيمون بالخارج ويُوِّرثون أموالهم وفق القواعد ذاتها المطبَّقة على المقيمين داخل المغرب. ويمكن تسيير مسطرة التركة بموجب توكيل رسمي، مما يُتيح للمغاربة في الخارج إتمام الإجراءات عن بُعد.',
        ],
        bullets: [
          'تُطبَّق مدونة الأسرة على التركات المغربية بصرف النظر عن بلد الإقامة',
          'الأموال الموجودة في المغرب خاضعة حصراً للإرث الإسلامي',
          'التوكيل الرسمي الموثَّق يُخوِّل المنابَ تسوية التركة بشكل قانوني',
          'يُمارَس حق الشفعة داخل الآجال القانونية المنصوص عليها في مدونة الحقوق العينية',
        ],
      },
      {
        icon: '🗳️',
        h2:   'الحقوق السياسية والقنصلية',
        content: [
          'يتمتع المغاربة المقيمون بالخارج بحق التصويت في الانتخابات التشريعية والمحلية المغربية. وقد عُزِّز تمثيل الجالية في أعقاب الإصلاحات الدستورية لعام 2011، فيما تُمثِّل السفارات والقنصليات المغربية المرجعَ الأول للإجراءات الإدارية.',
        ],
        bullets: [
          'حق التصويت في الانتخابات (مع ضرورة التسجيل في المغرب أو عبر القنصليات)',
          'إمكانية استخراج جواز السفر البيومتري المغربي من القنصليات',
          'تسجيل وثائق الحالة المدنية (الولادة والزواج والوفاة) لدى القنصليات',
          'تصديق الوثائق الموجهة للاستعمال في المغرب',
        ],
      },
      {
        icon: '💼',
        h2:   'كيف تُمارسون حقوقكم من الخارج؟',
        content: [
          'يستطيع المغاربة المقيمون بالخارج ممارسة جُلِّ حقوقهم في المغرب بواسطة وكلاء (توكيل رسمي موثَّق) أو عبر الخدمات القنصلية أو بالحضور الشخصي أثناء الزيارات. ويُعدُّ التوكيل الرسمي الأداةَ القانونية الأساسية؛ إذ يُحرَّر لدى موثق في بلد الإقامة ويُصادَق عليه، ويُخوِّل المنابَ التصرف نيابةً عن الموكِّل في البيع العقاري أو تسوية التركة أو سائر الأعمال القانونية.',
        ],
        bullets: [
          'التوكيل العام أو الخاص المحرَّر لدى الموثق المحلي مع التصديق عليه',
          'الأبوستيل للدول الموقِّعة على اتفاقية لاهاي',
          'مؤسسة محمد الخامس للتضامن: مساعدة وتوجيه للمغاربة في الخارج',
          'الوزارة المكلفة بشؤون المغاربة المقيمين بالخارج للمسائل المؤسسية',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'heritage-succession-mre-maroc',
    category:        'mre',
    title:           'Héritage et succession au Maroc pour les MRE : guide complet 2026',
    metaDescription: 'MRE : comment se déroule un héritage au Maroc ? Règles de succession islamique, parts héréditaires, procédures depuis l\'étranger, notaire, Moudawwana.',
    h1:              'Héritage et succession au Maroc pour les MRE',
    intro:           'La question de l\'héritage est l\'une des plus fréquentes chez les Marocains de la diaspora. Voici un guide clair sur les règles successorales marocaines et les démarches à suivre depuis l\'étranger.',
    legalDomain:     'civil',
    keywords:        ['héritage Maroc MRE', 'succession Maroc', 'héritage islamique Maroc', 'part héréditaire', 'succession MRE', 'notaire Maroc succession', 'moudawwana succession'],
    searchTerms:     ['succession héritage', 'moudawwana famille', 'droits réels immobilier'],
    specificNumbers: ['70-03', '39-08', '58-376', '07-03'],
    relatedSlugs:    ['mre-droits-juridiques-maroc', 'achat-immobilier-maroc-mre', 'double-nationalite-droit-maroc', 'code-de-la-famille-maroc'],
    sections: [
      {
        icon: '📜',
        h2:   'Quel droit s\'applique à la succession d\'un Marocain ?',
        content: [
          'La succession des biens situés au Maroc est régie par le droit marocain, quelle que soit la nationalité ou le lieu de résidence du défunt ou des héritiers. La Moudawwana (Code de la Famille — Loi 70-03) et le droit islamique malékite constituent le cadre légal applicable.',
          'Pour un MRE décédé à l\'étranger, les biens immobiliers et mobiliers au Maroc seront partagés selon les règles de la succession islamique telles que codifiées au Maroc, indépendamment du droit du pays de résidence.',
        ],
      },
      {
        icon: '⚖️',
        h2:   'Les règles de partage de l\'héritage (farâ\'id)',
        content: [
          'Le droit successoral marocain, inspiré de la jurisprudence islamique malékite, définit des parts héréditaires précises selon le lien de parenté avec le défunt.',
        ],
        bullets: [
          'Conjoint survivant : 1/4 si pas d\'enfants, 1/8 en présence d\'enfants',
          'Filles : 1/2 pour une seule fille, 2/3 pour deux filles ou plus (en l\'absence de fils)',
          'Fils et filles ensemble : le fils reçoit le double de la part de la fille (règle \'asabiyya)',
          'Mère : 1/6 en présence d\'enfants, 1/3 en leur absence',
          'Père : 1/6 en présence d\'enfants (et reçoit le reste en tant qu\'asab)',
          'Frères et sœurs : parts variables selon la configuration familiale',
        ],
      },
      {
        icon: '📋',
        h2:   'Procédure de succession depuis l\'étranger',
        content: [
          'Un MRE peut initier et suivre une procédure de succession depuis l\'étranger, mais devra généralement mandater un représentant au Maroc ou se déplacer pour certaines étapes clés. La procédure standard comprend plusieurs étapes.',
        ],
        bullets: [
          '1. Obtenir le certificat de décès et le faire légaliser/apostiller',
          '2. Établir l\'acte de notoriété héréditaire chez un adoul ou notaire marocain',
          '3. Inventaire des biens : immobilier (titre foncier), comptes bancaires, véhicules...',
          '4. Règlement des dettes et charges de la succession (frais funéraires, impôts)',
          '5. Partage notarié ou amiable entre héritiers',
          '6. Transcription au Registre foncier pour les biens immobiliers',
        ],
      },
      {
        icon: '📁',
        h2:   'Documents nécessaires pour la succession',
        content: [
          'Rassembler les bons documents en amont évite des délais inutiles. Voici les pièces généralement requises pour une succession au Maroc.',
        ],
        bullets: [
          'Acte de décès du défunt (traduit en arabe si établi à l\'étranger)',
          'Acte de naissance des héritiers',
          'Acte de mariage (si conjoint survivant)',
          'Titre(s) de propriété des biens immobiliers',
          'Relevés bancaires et attestations de portefeuille',
          'CIN ou passeport de tous les héritiers',
          'Procuration notariée pour les héritiers résidant à l\'étranger',
        ],
      },
      {
        icon: '⚠️',
        h2:   'Points d\'attention pour les MRE',
        content: [
          'Plusieurs situations particulières peuvent compliquer une succession pour les MRE.',
        ],
        bullets: [
          'Bien non titré (melkiya) : plus complexe à partager que les biens avec titre foncier',
          'Héritiers de nationalités différentes : le droit applicable peut varier selon les traités bilatéraux',
          'Délais : les successions non réglées peuvent générer des complications fiscales et juridiques',
          'Legs (wassiya) : limité au tiers de la succession en droit marocain, ne peut pas avantager un héritier légal',
        ],
      },
    ],
    faq: [
      {
        question: 'Une fille hérite-t-elle autant qu\'un fils au Maroc ?',
        answer:   'Non selon le droit islamique marocain actuel : le fils reçoit le double de la part de la fille. Cependant, la réforme de la Moudawwana en discussion en 2025 pourrait modifier certaines règles successorales.',
      },
      {
        question: 'Un MRE peut-il renoncer à sa part d\'héritage ?',
        answer:   'Oui, un héritier peut renoncer à sa part (tanazul). Cette renonciation doit être formalisée devant un notaire ou adoul marocain, et peut nécessiter une procuration si l\'héritier est à l\'étranger.',
      },
      {
        question: 'Peut-on faire un testament au Maroc pour avantager un enfant ?',
        answer:   'Le testament (wassiya) en droit marocain ne peut porter que sur le tiers de la succession et ne peut pas bénéficier à un héritier légal. Il peut en revanche avantager une personne non héritière (conjoint de nationalité étrangère non musulman, par exemple).',
      },
      {
        question: 'Que se passe-t-il si les héritiers ne s\'entendent pas ?',
        answer:   'En cas de désaccord, l\'un des héritiers peut saisir le tribunal de la famille compétent au Maroc pour demander le partage judiciaire (qisma qadhaiya). Le tribunal désigne un expert pour évaluer les biens et procéder au partage.',
      },
      {
        question: 'Les droits de succession sont-ils élevés au Maroc ?',
        answer:   'Les transmissions entre parents directs (père/mère/enfants) sont exonérées de droits d\'enregistrement en ligne directe. Pour les autres cas, des droits de mutation s\'appliquent selon un barème progressif. Consultez un notaire marocain pour le calcul précis.',
      },
    ],
    title_ar:           'الإرث والتركة في المغرب للمغاربة المقيمين بالخارج: دليل شامل 2026',
    metaDescription_ar: 'دليل متكامل للمغاربة المقيمين بالخارج حول الإرث في المغرب: قواعد التركة الإسلامية، الحصص الإرثية، الإجراءات من الخارج، الموثق، ومدونة الأسرة.',
    h1_ar:              'الإرث والتركة في المغرب للمغاربة المقيمين بالخارج',
    intro_ar:           'يُعدُّ موضوع الإرث من أكثر المواضيع شيوعاً في أسئلة الجالية المغربية بالخارج. إليكم دليلاً واضحاً حول قواعد التركة المغربية والإجراءات الواجب اتباعها من خارج المغرب.',
    keywords_ar:        ['الإرث في المغرب للمغاربة بالخارج', 'تركة المغرب', 'الإرث الإسلامي المغرب', 'الحصص الإرثية', 'الإرث للمغاربة المقيمين بالخارج', 'موثق المغرب التركة', 'مدونة الأسرة الإرث'],
    faq_ar: [
      {
        question: 'هل ترث البنت مثل الابن في المغرب؟',
        answer:   'لا، وفق أحكام الإرث الإسلامي المعمول به حالياً في المغرب: يحصل الابن على ضعف نصيب البنت. غير أن إصلاح مدونة الأسرة قيد الدراسة عام 2025 قد يُغيِّر بعض قواعد التوارث.',
      },
      {
        question: 'هل يمكن للمغربي المقيم بالخارج التنازل عن نصيبه في الإرث؟',
        answer:   'نعم، يحق للوارث التنازل عن نصيبه (التنازل). ويجب إثبات هذا التنازل أمام موثق أو عدلَين مغربيَّين، وقد يستلزم توكيلاً رسمياً إذا كان الوارث خارج المغرب.',
      },
      {
        question: 'هل يُمكن تحرير وصية في المغرب لإيثار أحد الأبناء؟',
        answer:   'لا تسري الوصية في القانون المغربي إلا في حدود ثلث التركة، ولا يجوز أن يكون الموصى له وارثاً شرعياً. غير أنها تصح لصالح شخص ليس من الورثة (كالزوج الأجنبي غير المسلم مثلاً).',
      },
      {
        question: 'ماذا يحدث إذا اختلف الورثة فيما بينهم؟',
        answer:   'عند الخلاف، يحق لأي وارث اللجوء إلى المحكمة الأسرية المختصة بالمغرب طلباً للقسمة القضائية. تُعيِّن المحكمة خبيراً لتقييم الأموال وإجراء القسمة.',
      },
      {
        question: 'هل رسوم التوارث مرتفعة في المغرب؟',
        answer:   'تُعفى النقل بين الأصول والفروع (الآباء والأبناء) من رسوم التسجيل في الخط المباشر. أما الحالات الأخرى فتخضع لرسوم انتقال وفق جدول تصاعدي. يُستحسن استشارة موثق مغربي لحساب المبالغ بدقة.',
      },
    ],
    sections_ar: [
      {
        icon: '📜',
        h2:   'أي قانون يُطبَّق على تركة المغربي؟',
        content: [
          'تخضع تركة الأموال الواقعة في المغرب للقانون المغربي، أياً كانت جنسية المتوفى أو الورثة أو محل إقامتهم. وتُشكِّل مدونة الأسرة (القانون 70-03) والفقه المالكي الإطارَ القانوني المرجعي المطبَّق.',
          'وفي حالة وفاة مغربي مقيم بالخارج، تُقسَّم أمواله العقارية والمنقولة في المغرب وفق أحكام الإرث الإسلامي المقنَّنة في المغرب، بصرف النظر عن قانون بلد الإقامة.',
        ],
      },
      {
        icon: '⚖️',
        h2:   'قواعد تقسيم الإرث (الفرائض)',
        content: [
          'يُحدِّد قانون التوارث المغربي المستوحى من الفقه الإسلامي المالكي حصصاً إرثية دقيقة بحسب درجة القرابة من المتوفى.',
        ],
        bullets: [
          'الزوج الباقي: الربع دون أولاد، والثمن مع وجود الأولاد',
          'البنت: النصف لبنت واحدة، والثلثان لبنتين فأكثر (في غياب الأبناء الذكور)',
          'الأبناء والبنات معاً: للذكر مثل حظ الأنثيين (العصبة)',
          'الأم: السدس مع وجود الأولاد، والثلث في غيابهم',
          'الأب: السدس مع وجود الأولاد (ويأخذ الباقي عصبةً)',
          'الإخوة والأخوات: حصصهم متفاوتة بحسب الوضع الأسري',
        ],
      },
      {
        icon: '📋',
        h2:   'مسطرة التوارث من الخارج',
        content: [
          'يستطيع المغربي المقيم بالخارج المبادرة بإجراءات التركة ومتابعتها من الخارج، غير أنه في الغالب يحتاج إلى توكيل ممثِّل في المغرب أو الحضور الشخصي لبعض المراحل الأساسية. وتتضمن المسطرة القياسية الخطوات التالية:',
        ],
        bullets: [
          '1. استخراج شهادة الوفاة وتوثيقها/التثبيت بالأبوستيل عليها',
          '2. تحرير رسم الإرث لدى عدول أو موثق مغربي',
          '3. جرد الأموال: العقارات (الرسم العقاري)، الحسابات البنكية، السيارات...',
          '4. تسديد ديون التركة وتكاليفها (مصاريف الجنازة، الضرائب)',
          '5. القسمة الرضائية أو الرسمية أمام الموثق بين الورثة',
          '6. التقييد في السجل العقاري بالنسبة للعقارات',
        ],
      },
      {
        icon: '📁',
        h2:   'الوثائق اللازمة للتركة',
        content: [
          'يُتيح جمع الوثائق الصحيحة مسبقاً تجنُّبَ التأخيرات غير الضرورية. وفيما يلي الوثائق المطلوبة عموماً في مسطرة التركة بالمغرب:',
        ],
        bullets: [
          'عقد وفاة المتوفى (مترجَم إلى العربية إذا كان محرَّراً بالخارج)',
          'عقود ازدياد الورثة',
          'عقد الزواج (في حالة وجود زوج باقٍ على قيد الحياة)',
          'رسوم الملكية العقارية',
          'كشوف حسابات بنكية وشهادات المحفظة',
          'بطاقة التعريف الوطنية أو جواز السفر لجميع الورثة',
          'التوكيل الرسمي للورثة المقيمين خارج المغرب',
        ],
      },
      {
        icon: '⚠️',
        h2:   'نقاط انتباه للمغاربة المقيمين بالخارج',
        content: [
          'ثمة وضعيات بعينها قد تُعقِّد مسطرة التركة بالنسبة للمغاربة المقيمين بالخارج:',
        ],
        bullets: [
          'الملك غير المحفَّظ (الملكية): تقسيمه أعقد من العقارات ذات الرسوم العقارية',
          'ورثة من جنسيات متعددة: قد يتباين القانون المطبَّق بحسب الاتفاقيات الثنائية',
          'الآجال: قد تُفضي التركات غير المُصفَّاة إلى تعقيدات جبائية وقانونية',
          'الوصية: محدودة بثلث التركة ولا تصح لصالح وارث شرعي',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'investir-maroc-mre',
    category:        'mre',
    title:           'Investir au Maroc depuis l\'étranger : guide MRE 2026',
    metaDescription: 'Guide complet pour les MRE qui souhaitent investir au Maroc : cadre légal, formes juridiques, avantages fiscaux, procédures et rapatriement des bénéfices.',
    h1:              'Investir au Maroc depuis l\'étranger (MRE)',
    intro:           'Le Maroc offre aux Marocains de la diaspora un cadre privilégié pour investir au pays. Entre avantages fiscaux, facilités bancaires dédiées et cadre légal protecteur, voici ce que vous devez savoir avant de vous lancer.',
    legalDomain:     'commercial',
    keywords:        ['investir Maroc MRE', 'investissement MRE Maroc', 'créer entreprise Maroc MRE', 'transfert fonds Maroc', 'avantages fiscaux MRE', 'rapatriement bénéfices Maroc'],
    searchTerms:     ['investissement charte', 'création société SARL', 'code général impôts'],
    specificNumbers: ['03-22', '5-96', '17-95', '15-95', '47-06'],
    relatedSlugs:    ['investissement-etranger-maroc', 'mre-droits-juridiques-maroc', 'creation-societe-maroc', 'achat-immobilier-maroc-mre'],
    sections: [
      {
        icon: '📊',
        h2:   'Pourquoi investir au Maroc en tant que MRE ?',
        content: [
          'Le Maroc constitue une destination attractive pour les investissements de la diaspora. Le pays bénéficie d\'une stabilité politique, d\'une croissance économique régulière et d\'un cadre légal progressivement aligné sur les standards internationaux.',
        ],
        bullets: [
          'Convertibilité partielle du dirham et facilités de transfert pour les MRE',
          'Exonérations fiscales sur les revenus rapatriés sous certaines conditions',
          'Accès aux financements bancaires marocains (CDG, CIH, Barid Bank — produits MRE)',
          'Marché immobilier dynamique avec potentiel locatif',
          'Secteurs porteurs : tourisme, agro-alimentaire, NTIC, énergies renouvelables',
        ],
      },
      {
        icon: '🏢',
        h2:   'Créer une entreprise au Maroc depuis l\'étranger',
        content: [
          'Un MRE peut créer une société au Maroc sans être physiquement présent, via procuration notariée donnée à un représentant. La SARL (Société à Responsabilité Limitée) est la forme la plus utilisée pour les petits et moyens investissements.',
          'Depuis 2019, le capital minimum pour une SARL a été supprimé (symboliquement 1 dirham possible), et les démarches de création se font en ligne via le Registre du Commerce (portail CRI).',
        ],
        bullets: [
          'SARL : forme idéale pour un investissement individuel ou familial',
          'SA : pour les projets nécessitant plus de 3 actionnaires ou un capital élevé',
          'Auto-entrepreneur : pour les activités indépendantes légères',
          'Société civile immobilière (SCI) : pour la gestion de patrimoine immobilier',
        ],
      },
      {
        icon: '💰',
        h2:   'Transfert de fonds et rapatriement des bénéfices',
        content: [
          'L\'Office des Changes marocain réglemente les transferts internationaux. Les MRE bénéficient d\'une réglementation favorable : les fonds transférés via le système bancaire agréé sont présumés réguliers et peuvent être rapatriés dans la même devise à tout moment.',
          'Les bénéfices des sociétés peuvent être rapatriés après paiement de l\'impôt sur les sociétés (IS). Pour les revenus locatifs, la retenue à la source de 10% s\'applique, avec possibilité d\'optimisation via les conventions fiscales bilatérales.',
        ],
      },
      {
        icon: '🧾',
        h2:   'Avantages fiscaux pour les MRE investisseurs',
        content: [
          'Le Code Général des Impôts marocain prévoit plusieurs dispositifs favorables aux MRE investisseurs.',
        ],
        bullets: [
          'Exonération d\'IS pendant 5 ans pour les nouvelles entreprises dans certaines zones',
          'Réduction d\'IS de 50% pour les sociétés exportatrices sur le CA à l\'export',
          'Exonération de droits d\'enregistrement pour les apports en capital',
          'TVA à 0% sur les équipements importés pour certains secteurs',
          'Conventions fiscales bilatérales évitant la double imposition (France, Espagne, Belgique, Canada, etc.)',
        ],
      },
    ],
    faq: [
      {
        question: 'Un MRE peut-il ouvrir un compte en devises au Maroc ?',
        answer:   'Oui. Les banques marocaines proposent des comptes en devises (euros, dollars) et des comptes convertibles spécialement dédiés aux MRE. Ces comptes permettent de conserver les fonds dans la devise étrangère et de les rapatrier librement.',
      },
      {
        question: 'Faut-il être présent au Maroc pour créer une entreprise ?',
        answer:   'Non. La création peut se faire par procuration. Un notaire dans votre pays de résidence établit une procuration que vous faites apostiller, puis votre mandataire au Maroc effectue les démarches auprès du CRI (Centre Régional d\'Investissement).',
      },
      {
        question: 'Les bénéfices d\'une entreprise marocaine sont-ils imposés dans mon pays de résidence ?',
        answer:   'Cela dépend de la convention fiscale bilatérale entre le Maroc et votre pays. La plupart des conventions évitent la double imposition. En général, les bénéfices de sociétés marocaines sont imposés au Maroc, et seuls les dividendes rapatriés peuvent être soumis à une imposition dans le pays de résidence.',
      },
      {
        question: 'Quels secteurs sont prioritaires pour l\'investissement MRE ?',
        answer:   'Le gouvernement marocain encourage l\'investissement dans le tourisme, l\'agro-alimentaire, les énergies renouvelables, les NTIC et l\'immobilier. Ces secteurs bénéficient souvent d\'avantages spécifiques dans le cadre de la Charte de l\'investissement.',
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'achat-immobilier-maroc-mre',
    category:        'mre',
    title:           'Acheter un bien immobilier au Maroc en tant que MRE : guide 2026',
    metaDescription: 'MRE : comment acheter un appartement ou une maison au Maroc ? Procédures, financement, titre foncier, frais et rapatriement du produit de la vente.',
    h1:              'Acheter un bien immobilier au Maroc en tant que MRE',
    intro:           'L\'achat immobilier au Maroc est l\'un des investissements les plus courants de la diaspora marocaine. Voici le guide complet de la procédure, des frais et des droits applicables.',
    legalDomain:     'civil',
    keywords:        ['achat immobilier Maroc MRE', 'acheter appartement Maroc étranger', 'titre foncier Maroc', 'crédit immobilier MRE', 'frais achat immobilier Maroc', 'vente immobilier Maroc MRE'],
    searchTerms:     ['titre foncier propriété', 'conservation foncière', 'droits réels immeuble'],
    specificNumbers: ['39-08', '18-00', '44-00', '07-16', '12-90'],
    relatedSlugs:    ['mre-droits-juridiques-maroc', 'investir-maroc-mre', 'heritage-succession-mre-maroc'],
    sections: [
      {
        icon: '🔑',
        h2:   'Droits d\'un MRE pour acheter au Maroc',
        content: [
          'Tout ressortissant marocain résidant à l\'étranger peut librement acquérir des biens immobiliers au Maroc, qu\'il s\'agisse d\'un appartement, d\'une villa, d\'un terrain ou d\'un local commercial. Ce droit est garanti par le Code des droits réels (Loi 39-08) et la Constitution de 2011.',
          'Les étrangers non marocains peuvent également acheter au Maroc, mais les MRE bénéficient de conditions plus favorables, notamment pour les financements bancaires et les transferts de fonds.',
        ],
      },
      {
        icon: '📋',
        h2:   'Étapes de l\'achat immobilier au Maroc',
        content: [
          'La procédure d\'achat immobilier au Maroc suit un processus structuré en plusieurs étapes, depuis la recherche du bien jusqu\'à la transcription au titre foncier.',
        ],
        bullets: [
          '1. Recherche et visite du bien (possible en personne ou via un mandataire)',
          '2. Promesse de vente (compromis) signée chez un notaire ou adoul — versement d\'une avance (10% généralement)',
          '3. Vérification juridique : titre foncier, absence de charges, permis de construire',
          '4. Obtention du financement (crédit MRE si besoin)',
          '5. Acte de vente définitif chez le notaire',
          '6. Paiement des droits d\'enregistrement et frais de notaire',
          '7. Transcription au Registre Foncier (Conservation Foncière)',
        ],
      },
      {
        icon: '💳',
        h2:   'Financement et transfert de fonds',
        content: [
          'Les banques marocaines proposent des produits de crédit immobilier spécifiquement conçus pour les MRE, avec des taux généralement compétitifs et des procédures adaptées aux non-résidents. Le Crédit Immobilier et Hôtelier (CIH), la CDG, Barid Bank et la quasi-totalité des banques marocaines ont des offres MRE.',
          'Les fonds transférés depuis l\'étranger via le système bancaire sont présumés réguliers et donnent droit au rapatriement du produit de la vente future dans la même devise.',
        ],
        bullets: [
          'Taux d\'intérêt : entre 4% et 6% selon les banques et la durée',
          'Apport personnel requis : généralement 20% à 30% du prix',
          'Durée maximale : jusqu\'à 25 ans',
          'Revenus étrangers pris en compte pour le calcul de la capacité d\'emprunt',
        ],
      },
      {
        icon: '🧾',
        h2:   'Frais et taxes à prévoir',
        content: [
          'L\'achat immobilier au Maroc génère plusieurs frais qu\'il convient d\'anticiper dans votre budget.',
        ],
        bullets: [
          'Droits d\'enregistrement : 4% du prix de vente (logement social : réduit)',
          'Conservation foncière (transcription) : 1% du prix',
          'Honoraires du notaire : environ 1% du prix (réglementé)',
          'TVA : 20% sur les honoraires du notaire',
          'Taxe sur les profits immobiliers (TPI) : supportée par le vendeur (20% sur la plus-value)',
          'Budget total à prévoir : environ 6 à 7% du prix d\'achat en frais',
        ],
      },
    ],
    faq: [
      {
        question: 'Peut-on acheter au Maroc sans se déplacer ?',
        answer:   'Oui, via une procuration notariée légalisée et apostillée, un représentant peut signer l\'acte de vente en votre nom. Il est cependant conseillé de visiter le bien en personne avant la signature.',
      },
      {
        question: 'Comment rapatrier le produit d\'une vente immobilière au Maroc ?',
        answer:   'Si les fonds d\'achat ont été transférés depuis l\'étranger via le circuit bancaire, le produit de la vente peut être rapatrié dans la même devise. Il faut conserver toutes les preuves de transfert initial (attestations bancaires) pour faciliter le rapatriement.',
      },
      {
        question: 'Y a-t-il une différence entre "titre foncier" et "melkiya" ?',
        answer:   'Oui, importante. Le titre foncier (réservé à la Conservation Foncière) offre une sécurité juridique maximale et est incontestable. La melkiya (acte adoulaire) est une preuve de propriété traditionnelle, moins sécurisée et plus difficile à défendre en cas de litige. Privilégiez les biens avec titre foncier.',
      },
      {
        question: 'Quelle est la fiscalité sur les revenus locatifs pour un MRE ?',
        answer:   'Les revenus locatifs de source marocaine sont soumis à l\'IR marocain (barème progressif ou abattement de 40% sur les revenus bruts). Une retenue à la source de 10% peut s\'appliquer. Des conventions fiscales bilatérales peuvent éviter la double imposition dans votre pays de résidence.',
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'double-nationalite-droit-maroc',
    category:        'mre',
    title:           'Double nationalité et droit marocain : ce qu\'il faut savoir',
    metaDescription: 'Double nationalité et droit marocain : le Maroc reconnaît-il la double nationalité ? Impacts sur les droits, le service militaire, les successions et les voyages.',
    h1:              'Double nationalité et droit marocain',
    intro:           'Des millions de Marocains de la diaspora détiennent une double nationalité. Voici ce que dit réellement le droit marocain sur ce sujet et ses implications pratiques.',
    legalDomain:     'civil',
    keywords:        ['double nationalité Maroc', 'binational marocain', 'nationalité marocaine étranger', 'perte nationalité marocaine', 'passeport marocain double nationalité', 'droits binationaux Maroc'],
    searchTerms:     ['nationalité marocaine dahir', 'code nationalité', 'acquisition nationalité'],
    specificNumbers: ['62-06', '1-58-250', '23-08'],
    relatedSlugs:    ['mre-droits-juridiques-maroc', 'heritage-succession-mre-maroc', 'investir-maroc-mre'],
    sections: [
      {
        icon: '🌍',
        h2:   'Le Maroc reconnaît-il officiellement la double nationalité ?',
        content: [
          'Le Maroc n\'a pas signé de convention interdisant la double nationalité et ne prévoit pas de déchéance automatique de la nationalité marocaine en cas d\'acquisition d\'une nationalité étrangère. En pratique, le Maroc tolère et même encourage la double nationalité pour maintenir les liens avec sa diaspora.',
          'Le Dahir du 6 septembre 1958 portant Code de la nationalité marocaine (modifié par la Loi 62-06 de 2007) ne contient aucune disposition imposant la renonciation à la nationalité marocaine lors de l\'acquisition d\'une nationalité étrangère.',
        ],
      },
      {
        icon: '📌',
        h2:   'Implications pratiques de la double nationalité',
        content: [
          'Sur le territoire marocain, les autorités marocaines considèrent le binational d\'abord comme Marocain. Cela a des implications importantes.',
        ],
        bullets: [
          'Entrée au Maroc : les binationaux peuvent entrer avec leur passeport marocain ou étranger — mais le passeport marocain est recommandé pour éviter des complications',
          'Service militaire : les binationaux sont théoriquement soumis aux obligations militaires marocaines, bien que le service national obligatoire ait été suspendu',
          'Droit de la famille : soumis au droit marocain pour le mariage, le divorce et la succession des biens au Maroc',
          'Propriété : mêmes droits qu\'un Marocain résident pour l\'achat immobilier',
          'Fiscalité : le critère de résidence fiscale prime sur la nationalité',
        ],
      },
      {
        icon: '👶',
        h2:   'Transmission de la nationalité marocaine aux enfants',
        content: [
          'Depuis la réforme de 2007 (Loi 62-06), la nationalité marocaine peut être transmise par la mère marocaine mariée à un étranger, en plus de la transmission traditionnelle par le père. Cette avancée majeure permet à de nombreux enfants nés à l\'étranger d\'obtenir la nationalité marocaine.',
        ],
        bullets: [
          'Enfant né de père marocain : nationalité marocaine de plein droit',
          'Enfant né de mère marocaine et père étranger : peut demander la nationalité marocaine à la naissance ou jusqu\'à sa majorité',
          'Enfant né à l\'étranger de deux parents marocains : nationalité marocaine automatique',
          'Démarche : déclaration aux consulats marocains ou lors d\'un séjour au Maroc',
        ],
      },
    ],
    faq: [
      {
        question: 'Peut-on perdre la nationalité marocaine ?',
        answer:   'Oui, dans des cas très spécifiques prévus par le Code de la nationalité : répudiation volontaire de la nationalité marocaine (après autorisation de l\'État), ou déchéance prononcée par décret pour certains actes graves (trahison, engagement au service d\'un État étranger en conflit avec le Maroc). Ces cas restent exceptionnels.',
      },
      {
        question: 'Dois-je utiliser mon passeport marocain pour entrer au Maroc ?',
        answer:   'Légalement, les autorités marocaines peuvent exiger l\'utilisation du passeport marocain pour les binationaux. En pratique, l\'entrée est généralement acceptée avec les deux passeports, mais pour éviter toute complication, le passeport marocain est recommandé.',
      },
      {
        question: 'La double nationalité affecte-t-elle les droits de succession ?',
        answer:   'Non directement. C\'est la localisation des biens qui détermine le droit applicable : les biens au Maroc sont soumis au droit successoral marocain, quelle que soit la nationalité du défunt ou des héritiers.',
      },
      {
        question: 'Mon enfant né en France peut-il avoir la nationalité marocaine ?',
        answer:   'Oui, si l\'un des parents est de nationalité marocaine. Depuis la réforme de 2007, la transmission se fait par les deux parents. Les démarches se font aux consulats marocains ou au Maroc.',
      },
    ],
  },

  // ── Hub Investissement — Étrangers & Entreprises ────────────────────────
  {
    lastUpdated:     '2026-06',
    slug:            'investissement-etranger-maroc',
    category:        'investissement',
    title:           'Investissement étranger au Maroc : cadre légal et procédures 2026',
    metaDescription: 'Cadre juridique complet pour investir au Maroc : Charte de l\'investissement, zones franches, protection des investisseurs, AMDIE, rapatriement des bénéfices.',
    h1:              'Investissement étranger au Maroc : cadre légal complet',
    intro:           'Le Maroc s\'est doté d\'un cadre légal attractif pour les investisseurs étrangers. Nouvelle Charte de l\'investissement (2022), zones d\'accélération industrielle, conventions de protection des investissements et incitations fiscales substantielles — voici tout ce que les investisseurs internationaux doivent savoir.',
    legalDomain:     'commercial',
    keywords:        ['investissement étranger Maroc', 'charte investissement Maroc', 'zones franches Maroc', 'CFC Casablanca', 'Tanger Med', 'AMDIE Maroc', 'rapatriement bénéfices Maroc', 'protection investisseurs Maroc'],
    searchTerms:     ['charte investissement', 'zone franche accélération', 'code général impôts investissement'],
    specificNumbers: ['03-22', '19-94', '53-95', '5-96', '17-95', '47-06', '15-95'],
    relatedSlugs:    ['investir-maroc-mre', 'creation-societe-maroc', 'sarl-maroc', 'code-de-commerce-maroc'],
    sections: [
      {
        icon: '🏛️',
        h2:   'La nouvelle Charte de l\'investissement (Loi 03-22)',
        content: [
          'Le Maroc a adopté en 2022 une nouvelle Charte de l\'investissement (Loi-cadre 03-22) qui remplace le dispositif de 1995. Ce texte fondamental définit le cadre général des investissements privés au Maroc et les garanties accordées aux investisseurs, nationaux et étrangers.',
          'La nouvelle Charte fixe un objectif ambitieux : atteindre 550 milliards de dirhams d\'investissement annuel d\'ici 2026, dont 50% du secteur privé. Elle introduit des mécanismes d\'incitation renforcés et simplifie les procédures.',
        ],
        bullets: [
          'Garanties fondamentales : libre transfert des capitaux investis et des bénéfices',
          'Protection contre la nationalisation sans indemnisation équitable',
          'Traitement non-discriminatoire entre investisseurs nationaux et étrangers',
          'Accès aux ressources naturelles et aux marchés publics sur un pied d\'égalité',
          'Possibilité de recourir à l\'arbitrage international en cas de litige',
        ],
      },
      {
        icon: '🏭',
        h2:   'Zones d\'accélération industrielle et zones franches',
        content: [
          'Le Maroc dispose d\'un réseau de zones à statut fiscal privilégié qui offrent des avantages substantiels aux investisseurs. Ces zones constituent l\'un des attraits majeurs du territoire marocain pour les investisseurs internationaux.',
        ],
        bullets: [
          'Casablanca Finance City (CFC) : hub financier africain, exonération d\'IS à 15% pendant 5 ans puis 15% à vie',
          'Zones d\'Accélération Industrielle (ZAI) : exonération d\'IS pendant 5 ans, puis 15% — remplace les anciennes zones franches',
          'Zone Franche de Tanger (Free Zone) : exonération d\'IS pendant 5 ans, 8,75% ensuite',
          'Zone Franche d\'Agadir et d\'autres villes industrielles',
          'Statut d\'Auto-Entrepreneur pour les petites activités : fiscalité simplifiée',
        ],
      },
      {
        icon: '🤝',
        h2:   'Conventions bilatérales de protection des investissements',
        content: [
          'Le Maroc a signé plus de 60 accords bilatéraux de protection des investissements (API) avec des pays partenaires. Ces conventions garantissent aux investisseurs étrangers une protection renforcée contre les risques non commerciaux (expropriation, nationalisation, troubles politiques).',
          'Parmi les partenaires liés par un API avec le Maroc : France, Allemagne, Espagne, Italie, Pays-Bas, Belgique, États-Unis, Canada, Chine, Arabie Saoudite, et la plupart des pays africains. Ces accords prévoient le recours à l\'arbitrage international (CIRDI) en cas de litige avec l\'État marocain.',
        ],
      },
      {
        icon: '💰',
        h2:   'Rapatriement des bénéfices et des capitaux',
        content: [
          'L\'un des atouts majeurs du Maroc pour les investisseurs étrangers est la liberté de transfert des capitaux et des bénéfices. L\'Office des Changes marocain garantit ce droit, sous réserve du respect de la réglementation des changes.',
        ],
        bullets: [
          'Libre transfert des dividendes et bénéfices après paiement de l\'IS',
          'Rapatriement du capital initial dans la même devise à tout moment',
          'Transfert du produit de cession des participations',
          'Délais de traitement : généralement 5 à 10 jours ouvrables via le système bancaire',
          'Retenue à la source sur dividendes versés aux non-résidents : 10% (réductible par convention fiscale)',
        ],
      },
      {
        icon: '🏢',
        h2:   'AMDIE et accompagnement des investisseurs',
        content: [
          'L\'Agence Marocaine de Développement des Investissements et des Exportations (AMDIE) est le guichet unique officiel pour les investisseurs étrangers. Elle propose un accompagnement personnalisé, de la phase de prospection jusqu\'à l\'installation.',
        ],
        bullets: [
          'Information sur le cadre légal, fiscal et sectoriel',
          'Identification des opportunités d\'investissement et des partenaires locaux',
          'Facilitation des procédures administratives (CRI — Centres Régionaux d\'Investissement)',
          'Aide à la négociation des conventions d\'investissement avec l\'État',
          'Suivi post-investissement et résolution de blocages administratifs',
        ],
      },
      {
        icon: '📊',
        h2:   'Secteurs porteurs pour l\'investissement étranger',
        content: [
          'Certains secteurs bénéficient d\'une attention particulière des autorités marocaines et d\'incitations spécifiques.',
        ],
        bullets: [
          'Énergies renouvelables : objectif 52% d\'électricité verte d\'ici 2030 — appels d\'offres réguliers',
          'Automobile et aéronautique : écosystèmes développés autour de Tanger et Casablanca',
          'Tourisme : zones touristiques avec avantages fonciers et fiscaux',
          'Agriculture et agro-industrie : foncier agricole accessible aux étrangers sous conditions',
          'NTIC et offshoring : hub technologique en développement, compétences anglophones disponibles',
          'Infrastructure et BTP : marché de la construction très actif',
        ],
      },
    ],
    faq: [
      {
        question: 'Un étranger peut-il posséder 100% d\'une société marocaine ?',
        answer:   'Oui, dans la plupart des secteurs. La loi marocaine autorise la participation étrangère à 100% du capital dans la majorité des secteurs. Certains secteurs stratégiques (banque, assurance, médias) imposent des restrictions ou nécessitent des autorisations spécifiques.',
      },
      {
        question: 'Faut-il un associé marocain pour créer une société au Maroc ?',
        answer:   'Non, depuis les réformes des années 2000, un investisseur étranger peut créer et détenir seul une SARL ou une SA au Maroc. Un associé local n\'est pas obligatoire, même si cela peut faciliter certaines démarches pratiques.',
      },
      {
        question: 'Quels sont les délais pour créer une société au Maroc ?',
        answer:   'Avec le Centre Régional d\'Investissement (CRI), la création d\'une société peut être réalisée en 24 à 72 heures. Les CRI offrent un guichet unique regroupant toutes les formalités : statuts, immatriculation, patente, affiliation CNSS.',
      },
      {
        question: 'Comment résoudre un litige avec l\'État marocain en tant qu\'investisseur étranger ?',
        answer:   'Les investisseurs étrangers couverts par un accord bilatéral de protection des investissements peuvent recourir à l\'arbitrage international (CIRDI — Centre International pour le Règlement des Différends relatifs aux Investissements). Hors accord bilatéral, les tribunaux marocains sont compétents.',
      },
      {
        question: 'Le Maroc est-il stable politiquement pour investir ?',
        answer:   'Le Maroc bénéficie d\'une stabilité politique reconnue dans la région et d\'une continuité institutionnelle depuis des décennies. La Banque Mondiale et l\'OCDE classent régulièrement le Maroc parmi les destinations les plus attractives d\'Afrique pour l\'investissement direct étranger.',
      },
      {
        question: 'Y a-t-il des restrictions sur les secteurs accessibles aux étrangers ?',
        answer:   'Quelques secteurs sont partiellement restreints : le secteur bancaire et les assurances nécessitent des autorisations spéciales, les médias audiovisuels ont des règles de participation étrangère limitée, et l\'agriculture impose des conditions particulières pour le foncier. Pour la majorité des secteurs économiques, aucune restriction n\'existe.',
      },
    ],
  },

  // ── Marchés Publics ────────────────────────────────────────────────
  {
    lastUpdated:     '2026-06',
    slug:            'marches-publics-maroc',
    category:        'administratif',
    title:           'Marchés Publics au Maroc : textes et procédures applicables 2026',
    title_ar:        'الصفقات العمومية بالمغرب : النصوص والمساطر المطبقة 2026',
    metaDescription: 'Consultez les textes juridiques sur les marchés publics au Maroc : décret n°2-22-431 de 2023, appel d\'offres, cahier des charges, contrôle, contentieux.',
    metaDescription_ar: 'اطلع على النصوص القانونية للصفقات العمومية بالمغرب : مرسوم 2023 رقم 2-22-431، طلب العروض، دفتر التحملات، المراقبة، النزاعات.',
    h1:              'Marchés Publics au Maroc',
    h1_ar:           'الصفقات العمومية بالمغرب',
    intro:           'Les marchés publics au Maroc sont régis par le Décret n°2-22-431 du 8 mars 2023, qui a abrogé et remplacé le décret de 2013. Ce nouveau cadre réglementaire définit les procédures d\'appel d\'offres, les cahiers des charges et les modalités d\'exécution et de contrôle des marchés. Cette page regroupe les textes disponibles dans JuriThèque sur ce domaine.',
    intro_ar:        'تُنظَّم الصفقات العمومية بالمغرب بموجب المرسوم رقم 2-22-431 الصادر في 8 مارس 2023، الذي نسخ وعوض مرسوم 2013. يُحدد هذا الإطار التنظيمي الجديد مساطر طلب العروض ودفاتر التحملات وشروط تنفيذ الصفقات ومراقبتها. تجمع هذه الصفحة النصوص المتاحة في JuriThèque في هذا المجال.',
    legalDomain:     'administratif',
    keywords:        ['marchés publics', 'appel d\'offres', 'cahier des charges', 'décret marchés publics', 'soumissionnaire', 'attributaire', 'bon de commande', 'contrôle marchés', 'TGR', 'maîtrise d\'ouvrage'],
    keywords_ar:     ['الصفقات العمومية', 'طلب العروض', 'دفتر التحملات', 'مرسوم الصفقات', 'المتنافس', 'الإسناد', 'أمر بالخدمة', 'مراقبة الصفقات', 'الخزينة العامة', 'صاحب المشروع'],
    searchTerms:     ['marchés publics maroc', 'appel offres maroc', 'décret marchés publics'],
    relatedSlugs:    ['passation-marches-publics-maroc', 'execution-marche-public-maroc', 'controle-marches-publics-maroc', 'collectivites-territoriales-maroc', 'depenses-personnel-maroc'],
    faq: [
      {
        question: 'Quel est le texte de base des marchés publics au Maroc ?',
        answer:   'Depuis 2023, les marchés publics de l\'État sont régis par le Décret n°2-22-431 du 8 mars 2023, qui a abrogé l\'ancien décret de 2013. Les collectivités territoriales disposent de leurs propres règlements. Consultez les textes disponibles dans JuriThèque.',
      },
      {
        question: 'Quels sont les types de procédures de passation au Maroc ?',
        answer:   'Le décret prévoit plusieurs procédures : appel d\'offres ouvert, appel d\'offres restreint, concours, et bon de commande pour les petits montants. Consultez les textes disponibles dans JuriThèque pour les seuils applicables.',
      },
      {
        question: 'Comment contester l\'attribution d\'un marché public au Maroc ?',
        answer:   'Un soumissionnaire écarté peut saisir la Commission des Marchés ou le juge administratif. Les voies de recours sont définies dans le décret marchés publics et le Code de Procédure Administrative. Consultez les textes dans JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو النص الأساسي للصفقات العمومية بالمغرب؟',
        answer:   'منذ 2023، تخضع صفقات الدولة للمرسوم رقم 2-22-431 الصادر في 8 مارس 2023، الذي نسخ مرسوم 2013. وتتوفر الجماعات الترابية على أنظمتها الخاصة. راجع النصوص المتاحة في JuriThèque.',
      },
      {
        question: 'ما هي أنواع مساطر إبرام الصفقات بالمغرب؟',
        answer:   'يتضمن المرسوم عدة مساطر: طلب العروض المفتوح والمحدود والمباراة وأمر الخدمة للمبالغ الصغيرة. راجع النصوص المتاحة في JuriThèque للاطلاع على الحدود المالية المطبقة.',
      },
      {
        question: 'كيف يمكن الطعن في إسناد صفقة عمومية بالمغرب؟',
        answer:   'يحق للمتنافس المُقصى اللجوء إلى لجنة الصفقات أو القضاء الإداري. تُحدد مسالك الطعن في مرسوم الصفقات وقانون المسطرة الإدارية. راجع النصوص في JuriThèque.',
      },
    ],
    sections: [
      {
        h2:      'Cadre juridique : le Décret n°2-22-431 de 2023',
        content: [
          'Les marchés publics de l\'État sont désormais régis par le Décret n°2-22-431 du 8 mars 2023, qui a abrogé l\'ancien Décret n°2-12-349 de 2013. Ce nouveau texte modernise les règles de passation, d\'exécution, de contrôle et de règlement des marchés en intégrant la dématérialisation et des exigences de transparence renforcées. Les collectivités territoriales disposent de leurs propres règlements intérieurs adoptés conformément aux Lois Organiques de 2015.',
        ],
        bullets: [
          'Décret n°2-22-431 du 8 mars 2023 : marchés de l\'État (texte en vigueur)',
          'Règlements intérieurs des collectivités territoriales (LOC 2015)',
          'Cahier des Clauses Administratives Générales (CCAG)',
          'Circulaires de la Direction du Budget et de la TGR',
        ],
      },
      {
        h2: 'Acteurs et définitions clés de la commande publique',
        content: [
          'La commande publique marocaine met en scène plusieurs acteurs dont les rôles sont précisément définis. Au centre se trouve le maître d\'ouvrage, qui est l\'autorité publique pour le compte de laquelle les prestations sont réalisées. Il peut s\'agir de l\'État, d\'une collectivité territoriale ou d\'un établissement public. Le maître d\'ouvrage est responsable de la préparation, de la passation, du suivi de l\'exécution et de l\'approbation du marché. Pour l\'assister dans ces missions complexes, il peut désigner un maître d\'ouvrage délégué, qui peut être une autre administration, une société d\'État ou une de ses filiales. Cette délégation, encadrée par une décision, permet de confier certaines prérogatives tout en maintenant la responsabilité finale du maître d\'ouvrage initial.',
          'Le processus de passation d\'un marché public implique une terminologie précise pour qualifier les entreprises à chaque étape. Initialement, toute personne physique ou morale qui participe à un appel à la concurrence est un "concurrent". Lorsqu\'elle dépose une offre, elle devient un "soumissionnaire". À l\'issue de l\'évaluation des offres, le soumissionnaire dont la proposition est jugée la plus avantageuse est désigné "attributaire" du marché. Ce statut est provisoire jusqu\'à la notification de l\'approbation du marché par l\'autorité compétente. C\'est seulement après cette notification que l\'attributaire acquiert la qualité de "titulaire" du marché, devenant ainsi le cocontractant officiel de l\'administration et étant légalement tenu d\'exécuter les prestations convenues.',
          'Un principe fondamental de la gestion des finances publiques, consacré par le Décret Royal n°330-66 portant règlement général de la comptabilité publique (RGCP), est la séparation des fonctions d\'ordonnateur et de comptable public. L\'ordonnateur, qui peut être un ministre, un président de collectivité ou un directeur d\'établissement public, a le pouvoir d\'engager, de constater, de liquider et d\'ordonner le paiement des dépenses. Le comptable public, quant à lui, est le seul habilité à manier les fonds publics. Il exécute les ordres de paiement après avoir exercé un contrôle de régularité sur la dépense (disponibilité des crédits, validité de la créance, etc.). Cette incompatibilité des fonctions vise à prévenir les abus et à garantir une saine gestion des deniers publics.',
        ],
        bullets: [
          'Maître d\'ouvrage : L\'entité publique (État, collectivité territoriale, établissement public) pour le compte de laquelle le marché est conclu.',
          'Ordonnateur : Personne ayant qualité, au nom d\'un organisme public, pour engager, liquider et ordonner le paiement d\'une dépense.',
          'Comptable public : Agent public chargé d\'exécuter les opérations de recettes et de dépenses, exerçant un contrôle de régularité et soumis à une responsabilité personnelle et pécuniaire.',
          'Concurrent : Toute personne physique ou morale participant à un appel à la concurrence avant la remise des offres.',
          'Attributaire : Le concurrent dont l\'offre a été retenue par le maître d\'ouvrage avant la notification de l\'approbation du marché.',
          'Titulaire : L\'attributaire auquel l\'approbation du marché a été notifiée, devenant ainsi le cocontractant de l\'administration.',
        ],
      },
      {
        h2: 'Typologie des marchés : nature des prestations et modes d\'exécution',
        content: [
          'Les marchés publics sont classifiés principalement selon la nature de leur objet. On distingue trois grandes catégories. Les marchés de travaux concernent l\'exécution de travaux liés à la construction, la reconstruction, la démolition, la réparation ou la rénovation d\'un bâtiment ou d\'un ouvrage, y compris des prestations accessoires comme les études ou l\'installation d\'équipements. Les marchés de fournitures ont pour objet l\'achat, la location ou la location avec option d\'achat de produits ou de matériels ; ils peuvent inclure à titre accessoire des travaux de pose. Enfin, les marchés de services couvrent toutes les prestations qui ne sont ni des travaux ni des fournitures, telles que les études, la maîtrise d\'œuvre, la formation, l\'entretien, le gardiennage ou la location sans option d\'achat.',
          'Parmi les modes d\'exécution spécifiques, le marché-cadre, régi par l\'article 6 du décret de 2023, est utilisé pour des prestations à caractère prévisible et permanent dont la quantité et le rythme d\'exécution ne peuvent être entièrement déterminés à l\'avance. Le maître d\'ouvrage fixe un minimum et un maximum en valeur ou en quantité pour une période n\'excédant pas l\'année budgétaire. Ces marchés peuvent être conclus pour une durée maximale de trois ans, ou cinq ans pour certaines prestations spécifiques. Ils sont reconduits tacitement d\'une année à l\'autre, sauf décision de non-reconduction par le maître d\'ouvrage. Le maximum des prestations ne peut excéder le double du minimum, garantissant un cadre budgétaire maîtrisé.',
          'Les marchés reconductibles sont un autre mode d\'exécution destiné à couvrir des besoins à caractère prévisible, répétitif et permanent, mais pour lesquels les quantités peuvent être déterminées à l\'avance. Comme pour les marchés-cadre, ils sont conclus pour une durée d\'un an et peuvent être reconduits tacitement dans une limite totale de trois ou cinq ans. La non-reconduction par le maître d\'ouvrage entraîne la résiliation du marché. La principale différence avec le marché-cadre réside dans la détermination préalable des quantités. Une liste de prestations éligibles à ce type de marché est fixée par la réglementation. Ce mode d\'exécution offre une flexibilité pour la gestion des contrats portant sur des besoins récurrents comme la maintenance ou le nettoyage.',
        ],
        bullets: [
          'Marchés de travaux : Contrats pour la construction, rénovation ou entretien d\'ouvrages, incluant les prestations accessoires nécessaires.',
          'Marchés de fournitures : Contrats pour l\'achat ou la location (avec ou sans option d\'achat) de produits, pouvant inclure leur installation.',
          'Marchés de services : Contrats pour des prestations intellectuelles (études, assistance) ou des services courants (gardiennage, nettoyage).',
          'Marché-cadre (Art. 6) : Pour des besoins permanents à exécution échelonnée, avec un minimum et un maximum en valeur ou quantité, pour une durée maximale de 3 ou 5 ans.',
          'Marché reconductible : Pour des prestations répétitives dont les quantités sont connues, reconduit tacitement chaque année dans une limite de 3 ou 5 ans.',
          'Modification du marché-cadre : Possibilité d\'ajuster par avenant le minimum (baisse jusqu\'à 25%) et le maximum (hausse jusqu\'à 10%) sur la durée totale du marché.',
        ],
      },
      {
        h2:      'Les étapes clés d\'un marché public',
        content: 'La passation d\'un marché public suit une procédure stricte garantissant la transparence, la concurrence et l\'égalité des soumissionnaires.',
        bullets: [
          '1. Planification : inscription au plan de passation des marchés (PPM)',
          '2. Lancement : publication de l\'avis (Journal Officiel, portail marchés)',
          '3. Soumission : dépôt des offres technique et financière dans les délais',
          '4. Examen par la commission d\'appel d\'offres',
          '5. Notification de l\'attribution et délai de recours',
          '6. Visa de la TGR selon les seuils de contrôle',
          '7. Exécution, réception provisoire puis définitive',
        ],
      },
      {
        h2: 'Les procédures spécifiques aux prestations architecturales',
        content: [
          'Les prestations architecturales constituent une catégorie particulière de marchés de services, formalisées par un "contrat d\'architecte" qui fixe les clauses administratives, techniques et financières. Elles se distinguent par leur mode de rémunération, qui est généralement un prix à pourcentage. Ce prix est déterminé par un taux appliqué au montant hors taxes des travaux réellement exécutés, sans inclure la révision des prix ou les pénalités. De plus, ces marchés sont conclus à prix ferme, ce qui signifie que les honoraires de l\'architecte ne peuvent être modifiés pendant la durée d\'exécution du contrat. Malgré ces spécificités, ces contrats restent soumis aux principes fondamentaux de la commande publique, notamment la liberté d\'accès, l\'égalité de traitement et la transparence.',
          'La procédure de passation la plus courante est la consultation architecturale, qui peut être ouverte, simplifiée ou restreinte. La consultation architecturale ouverte est la règle pour les projets dont le budget prévisionnel des travaux est inférieur ou égal à 30 millions de dirhams HT, ainsi que pour toutes les opérations de lotissement. Cette procédure permet une large mise en compétition où tout architecte peut obtenir le dossier et présenter sa candidature. Le choix est effectué par un jury de consultation qui propose au maître d\'ouvrage de retenir l\'architecte ayant présenté l\'offre jugée économiquement la plus avantageuse, sur la base d\'un programme de consultation préalablement établi.',
          'Pour des projets de moindre envergure ou de nature spécifique, des procédures adaptées existent. La consultation architecturale simplifiée est exclusivement réservée aux "architectes débutants", définis comme ayant moins de cinq ans d\'exercice à titre libéral, pour des projets dont le budget ne dépasse pas 3 millions de dirhams HT. La consultation architecturale restreinte est, quant à elle, utilisée pour des projets d\'aménagement ou d\'entretien de bâtiments dont le budget est inférieur ou égal à 10 millions de dirhams HT. Dans ce cas, le maître d\'ouvrage invite un nombre minimum de cinq architectes à soumissionner, dont au moins deux doivent être implantés dans la région concernée par le projet.',
        ],
        bullets: [
          'Contrat d\'architecte : Marché de services spécifique, conclu à prix ferme et dont la rémunération est un pourcentage du montant des travaux.',
          'Consultation architecturale ouverte : Procédure de droit commun pour les projets jusqu\'à 30 millions DH HT et les lotissements, ouverte à tous les architectes.',
          'Consultation architecturale simplifiée : Réservée aux architectes débutants (moins de 5 ans d\'exercice) pour des projets jusqu\'à 3 millions DH HT.',
          'Consultation architecturale restreinte : Sur invitation d\'au moins 5 architectes pour des projets d\'aménagement jusqu\'à 10 millions DH HT.',
          'Concours architectural : Procédure de mise en compétition visant à choisir la conception d\'un projet et à en confier le suivi à son auteur.',
          'Jury de consultation/concours : Organe collégial chargé d\'évaluer les offres et de proposer un lauréat au maître d\'ouvrage.',
        ],
      },
      {
        h2: 'La dématérialisation des procédures de passation',
        content: [
          'La dématérialisation des marchés publics est un axe majeur de la modernisation de l\'administration marocaine, visant à renforcer la transparence, l\'efficacité et la lutte contre la corruption. Ce processus est encadré par le chapitre VI (articles 134 à 141) du décret n°2-22-431, la loi n°43-20 relative aux services de confiance pour les transactions électroniques, et l\'arrêté n°1692-23 du 23 juin 2023. Cette transition numérique concerne un secteur économique majeur, la commande publique représentant environ 245 milliards de dirhams en 2022, soit près de 20% du PIB national. L\'approche adoptée est progressive, participative et s\'accompagne d\'une forte conduite du changement pour assister tous les acteurs.',
          'Le Portail des Marchés Publics est l\'épine dorsale de ce dispositif. Il centralise l\'ensemble du processus de communication et d\'information : publication des programmes prévisionnels, des avis de publicité, mise à disposition des dossiers de consultation, et publication des résultats d\'attribution. En 2022, le portail a géré plus de 39 000 consultations pour une valeur estimée à 147 milliards de dirhams. Avec plus de 4 200 acheteurs publics et 35 000 entreprises inscrits, il constitue un guichet unique essentiel, garantissant un accès égal et transparent à l\'information pour tous les opérateurs économiques. Il héberge également des informations cruciales comme la liste des entreprises exclues des marchés publics.',
          'Au-delà de l\'information, le portail intègre des fonctionnalités transactionnelles clés. La soumission électronique est la plus emblématique, permettant aux entreprises de déposer leurs offres en ligne de manière sécurisée. Son adoption a été exponentielle, passant de 16 185 soumissions en 2019 à 83 935 en 2021. D\'autres outils complètent l\'écosystème digital, comme la base de données des prestataires qui facilite la vérification des informations administratives, les enchères électroniques inversées pour optimiser les achats de fournitures courantes, et les achats groupés électroniques. Ces fonctionnalités visent à simplifier les procédures, réduire les coûts et les délais, et renforcer la traçabilité de l\'ensemble du processus d\'achat public.',
        ],
        bullets: [
          'Cadre juridique : Articles 134 à 141 du Décret n°2-22-431 et Arrêté n°1692-23 du 23 juin 2023.',
          'Portail des Marchés Publics : Plateforme unique pour la publication des avis, le téléchargement des dossiers et la consultation des résultats.',
          'Soumission électronique : Dépôt dématérialisé et sécurisé des offres par les entreprises, généralisé progressivement.',
          'Base de données des prestataires : Répertoire en ligne des entreprises pour simplifier les vérifications administratives et favoriser l\'interopérabilité.',
          'Enchères électroniques inversées : Mécanisme de concurrence par les prix en temps réel pour certains types d\'achats.',
          'Objectifs stratégiques : Améliorer la transparence, l\'efficience de la dépense publique et moderniser l\'administration.',
        ],
      },
      {
        h2:      'Contrôle, contentieux et recours des marchés publics',
        content: [
          'Le contrôle des marchés publics au Maroc est exercé à plusieurs niveaux : contrôle a priori par la Trésorerie Générale du Royaume (TGR) au-delà des seuils fixés, et contrôle a posteriori par la Cour des Comptes et les Cours Régionales des Comptes.',
          'Le Décret 2-22-431 de 2023 a renforcé les mécanismes de transparence : publication obligatoire des résultats d\'attribution, accès aux procès-verbaux d\'ouverture des plis, et voies de recours formalisées pour les soumissionnaires évincés.',
        ],
        bullets: [
          'Commission des Marchés : organe consultatif, avis sur les documents types',
          'TGR : visa préalable obligatoire au-delà des seuils (contrôle de régularité)',
          'Cour des Comptes : contrôle a posteriori de la gestion',
          'Recours gracieux auprès du maître d\'ouvrage dans les 10 jours de la notification',
          'Recours administratif devant le wali / gouverneur (autorité de tutelle)',
          'Recours contentieux devant le tribunal administratif compétent',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'الإطار القانوني: المرسوم رقم 2-22-431 لعام 2023',
        content: [
          'تخضع صفقات الدولة اليوم للمرسوم رقم 2-22-431 الصادر في 8 مارس 2023، الذي نسخ المرسوم القديم رقم 2-12-349 الصادر عام 2013. يُحدِّث هذا النص قواعد الإبرام والتنفيذ والمراقبة وتسوية الصفقات، بدمج مستلزمات الرقمنة وتعزيز اشتراطات الشفافية. وتتوفر الجماعات الترابية على أنظمتها الداخلية الخاصة المعتمَدة وفقاً للقوانين التنظيمية لعام 2015.',
        ],
        bullets: [
          'المرسوم رقم 2-22-431 الصادر في 8 مارس 2023: صفقات الدولة (النص الساري)',
          'الأنظمة الداخلية للجماعات الترابية (القوانين التنظيمية 2015)',
          'دفتر الشروط الإدارية العامة (CCAG)',
          'منشورات مديرية الميزانية والخزينة العامة للمملكة',
        ],
      },
      {
        h2: 'الفاعلون الرئيسيون والتعاريف الأساسية في الطلبيات العمومية',
        content: [
          'تتسم منظومة الصفقات العمومية بتعدد الفاعلين وتوزيع دقيق للمهام، وذلك لضمان سلامة وشفافية مسار النفقة العمومية. يأتي في مقدمة هؤلاء الفاعلين "صاحب المشروع"، وهو الشخص المعنوي العام الذي تُنفذ لفائدته الأعمال موضوع الصفقة. إلى جانبه، نجد شخصيتين محوريتين يفصل بين مهامهما القانون بشكل صارم، وهما "الآمر بالصرف" و"المحاسب العمومي". فالآمر بالصرف، وفقاً للمادة 3 من المرسوم الملكي رقم 330-66 المتعلق بالتنظيم العام للمحاسبة العمومية، هو الشخص المؤهل باسم هيئة عمومية للالتزام بنفقة وتصفيتها والأمر بصرفها. أما المحاسب العمومي، فهو الموظف المكلف بأداء النفقات بعد التحقق من صحة الدين ومشروعية الأمر بالصرف، وهو ما يكرس مبدأ الفصل بين سلطة القرار وسلطة الأداء.',
          'يحدد مرسوم الصفقات العمومية بدقة المصطلحات المتعلقة بالمشاركين في المنافسة. فـ"المتنافس" هو كل شخص ذاتي أو اعتباري يشارك في دعوة للمنافسة في مرحلتها السابقة لتقديم العروض أو يقدم عرضاً لإبرام صفقة. وبمجرد انتقاء عرضه من طرف لجنة طلب العروض، يكتسب المتنافس صفة "نائل الصفقة"، وهي صفة مؤقتة تستمر إلى حين المصادقة على الصفقة من طرف السلطة المختصة. وبعد إتمام هذه المصادقة وتبليغها، يصبح نائل الصفقة "صاحب الصفقة"، وهو الطرف المتعاقد مع صاحب المشروع والملزم بتنفيذ الأعمال المتفق عليها. هذا التدرج في التسميات يعكس المراحل الإجرائية التي يمر بها المشارك في مسطرة إبرام الصفقة.',
          'تُعرَّف الصفقة العمومية بأنها عقد يبرم بمقابل مادي بين صاحب مشروع من جهة، وشخص ذاتي أو اعتباري من جهة أخرى، يدعى مقاولاً أو مورداً أو خدماتياً، ويهدف إلى تنفيذ أشغال أو تسليم توريدات أو القيام بخدمات. ويشمل نطاق تطبيق مرسوم الصفقات العمومية، كما تم تحديده بموجب القانون رقم 54-22، صفقات الدولة والجماعات الترابية ومجموعاتها، بالإضافة إلى المؤسسات العمومية، باستثناء تلك المذكورة في اللائحة المحددة قانوناً. كما يطبق على الأشخاص الاعتبارية الأخرى الخاضعة للقانون العام والتي تخضع للرقابة المالية للدولة، مما يوسع من دائرة تطبيق قواعد المنافسة والشفافية لتشمل جزءاً كبيراً من الطلبيات العمومية بالمملكة.',
        ],
        bullets: [
          'صاحب المشروع: الشخص المعنوي العام (الدولة، جماعة ترابية، مؤسسة عمومية) الذي تبرم الصفقة لحسابه.',
          'الآمر بالصرف: الشخص المؤهل قانوناً للالتزام بالنفقة وتصفيتها والأمر بأدائها.',
          'المحاسب العمومي: الموظف المسؤول عن أداء النفقات بعد التأكد من شرعيتها وتوفر الاعتمادات.',
          'مبدأ الفصل بين مهام الآمرين بالصرف والمحاسبين العموميين: ضمانة أساسية للرقابة المتبادلة على المال العام.',
          'المتنافس: كل شخص يشارك في المنافسة قبل أو عند تقديم العروض.',
          'نائل الصفقة: المتنافس الذي تم انتقاء عرضه قبل المصادقة على الصفقة.',
        ],
      },
      {
        h2: 'أنواع الصفقات حسب طبيعة الأعمال وأساليب التنفيذ',
        content: [
          'يصنف مرسوم الصفقات العمومية العقود حسب طبيعة موضوعها إلى ثلاثة أنواع رئيسية. أولاً، "صفقات الأشغال" التي يكون موضوعها تنفيذ أشغال ترتبط بالبناء أو إعادة البناء أو الهدم أو الإصلاح أو الصيانة أو التهيئة، بما في ذلك أشغال التشجير وتهيئة المساحات الخضراء. ثانياً، "صفقات التوريدات" التي تهدف إلى شراء منتجات أو معدات، أو كرائها مع خيار الشراء، ويمكن أن تشمل بصفة تبعية أشغال الوضع والتركيب الضرورية. وأخيراً، "صفقات الخدمات" التي تتعلق بإنجاز أعمال لا يمكن وصفها بالأشغال أو التوريدات، وتشمل فئات متنوعة مثل الدراسات، الصيانة، الحراسة، النظافة، والمساعدة التقنية لصاحب المشروع.',
          'إلى جانب التصنيف حسب طبيعة الأعمال، يميز المرسوم بين عدة أساليب للتنفيذ تتيح تكييف العقد مع خصوصيات الحاجيات المراد تلبيتها. من أبرز هذه الأساليب "الصفقات الإطارية" المنصوص عليها في المادة 6 من المرسوم، والتي يتم اللجوء إليها عندما يتعذر على صاحب المشروع تحديد كمية ووتيرة تنفيذ الأعمال بشكل مسبق ودقيق، نظراً لطابعها التوقعي والدائم. في هذه الحالة، تحدد الصفقة حداً أدنى وحداً أقصى للأعمال التي يمكن طلبها خلال فترة لا تتجاوز السنة المالية، مع إمكانية تجديدها سنوياً على ألا تتجاوز المدة الإجمالية للصفقة ثلاث أو خمس سنوات حسب طبيعة الأعمال.',
          'تعتبر "الصفقات القابلة للتجديد" أسلوباً آخر للتنفيذ، وهي مناسبة للأعمال ذات الطابع التوقعي والمتكرر والدائم والتي يمكن تحديد كمياتها مسبقاً. تتضمن هذه الصفقات بنداً يسمح بتجديدها ضمنياً من سنة لأخرى في حدود مدة إجمالية لا تتجاوز ثلاث أو خمس سنوات. وخلافاً للصفقة الإطارية، فإن الالتزام المالي يكون محدداً لكل سنة. بالإضافة إلى هذين النوعين، توجد أساليب أخرى كـ"الصفقات بأقساط اشتراطية" التي تسمح لصاحب المشروع بعدم الالتزام إلا بقسط ثابت، فيما تبقى الأقساط الأخرى رهينة بتوفر الاعتمادات أو بظروف معينة، و"الصفقات المحصصة" التي تقسم العمل إلى عدة حصص يمكن إسنادها لمتنافسين مختلفين.',
        ],
        bullets: [
          'صفقات الأشغال: تتعلق بإنجاز أو تجديد أو صيانة بناية أو منشأة أو هيكل.',
          'صفقات التوريدات: تهدف إلى شراء أو كراء منتجات أو معدات، مثل التجهيزات المكتبية أو الآليات.',
          'صفقات الخدمات: تشمل الأعمال غير المادية كالدراسات، الاستشارات، التكوين، الحراسة، وخدمات المختبرات.',
          'الصفقة الإطارية (المادة 6): تبرم لأعمال ذات طابع توقعي ودائم لا يمكن تحديد كميتها مسبقاً، وتحدد حداً أدنى وأقصى للطلبيات.',
          'الصفقة القابلة للتجديد: تبرم لأعمال متكررة يمكن تحديد كميتها، وتجدد ضمنياً كل سنة ضمن مدة إجمالية محددة.',
          'يمكن تعديل الحد الأدنى والأقصى للصفقة الإطارية بموجب ملحق، في حدود زيادة لا تتعدى 10% من الحد الأقصى وتخفيض لا يتجاوز 25% من الحد الأدنى.',
        ],
      },
      {
        h2:      'المراحل الأساسية لصفقة عمومية',
        content: 'تُبرَم الصفقة العمومية وفق مسطرة صارمة تضمن الشفافية والمنافسة والمساواة بين المتنافسين.',
        bullets: [
          '1. التخطيط: إدراج الصفقة في مخطط الإبرام (PPM)',
          '2. الإطلاق: نشر الإعلان (الجريدة الرسمية، بوابة الصفقات)',
          '3. التقديم: إيداع العروض التقنية والمالية في الآجال المحددة',
          '4. الدراسة من قِبَل لجنة طلب العروض',
          '5. تبليغ الإسناد والأجل المخصص للطعن',
          '6. تأشيرة الخزينة العامة وفق حدود المراقبة',
          '7. التنفيذ والتسلُّم المؤقت ثم النهائي',
        ],
      },
      {
        h2: 'المساطر الخاصة بالأعمال المعمارية',
        content: [
          'تحظى الأعمال المعمارية بمكانة خاصة ضمن منظومة الصفقات العمومية، حيث تخضع لمساطر إبرام تتناسب مع طبيعتها الإبداعية والتقنية. وتعتبر هذه الأعمال نوعاً من صفقات الخدمات، لكنها تتميز بكونها تبرم على أساس "عقد مهندس معماري" يحدد الشروط الإدارية والتقنية والمالية. ومن حيث السعر، فهي غالباً ما تكون "صفقات بسعر نسبي"، حيث يتم تحديد أتعاب المهندس المعماري كنسبة مئوية من التكلفة النهائية للأشغال المنجزة فعلياً. كما أنها تعتبر "صفقات بأثمان ثابتة"، مما يعني أن أتعابها لا تخضع لمراجعة الأثمان خلال مدة تنفيذ العقد، وهو ما يضمن استقرار الالتزام المالي.',
          'حدد المرسوم طريقتين رئيسيتين لإبرام عقود المهندسين المعماريين: "المباراة المعمارية" و"الاستشارة المعمارية". وتعتبر المباراة المعمارية مسطرة تهدف إلى وضع المهندسين المعماريين في منافسة لاختيار تصميم لمشروع معين، بناءً على اقتراح من لجنة المباراة، ثم إسناد مهمة تتبع ومراقبة إنجاز المشروع للفائز بالمباراة. أما الاستشارة المعمارية، فهي مسطرة لاختيار مهندس معماري بناءً على عرض يقدمه استجابة لبرنامج استشارة يضعه صاحب المشروع، ويمكن أن تتخذ هذه الاستشارة ثلاثة أشكال: مفتوحة، مبسطة، أو محدودة.',
          'تختلف أشكال الاستشارة المعمارية حسب حجم وطبيعة المشروع. فـ"الاستشارة المفتوحة" تطبق على المشاريع التي يساوي أو يقل مبلغها التقديري عن 30 مليون درهم، وتكون مفتوحة أمام جميع المهندسين. أما "الاستشارة المبسطة"، فهي مخصصة حصراً للمهندسين المعماريين المبتدئين (أقل من 5 سنوات من الممارسة الحرة) وتخص المشاريع التي لا يتجاوز مبلغها 3 ملايين درهم. وأخيراً، يتم اللجوء إلى "الاستشارة المحدودة" في مشاريع تهيئة وصيانة المباني التي لا يتجاوز مبلغها 10 ملايين درهم، حيث يقوم صاحب المشروع باستشارة خمسة مهندسين معماريين على الأقل، يجب أن يكون اثنان منهم على الأقل منتمين لجهة المشروع.',
        ],
        bullets: [
          'تعتبر الأعمال المعمارية صفقات خدمات بأثمان ثابتة وغير قابلة للمراجعة.',
          'تحدد أتعاب المهندس المعماري كنسبة مئوية من الكلفة الحقيقية للأشغال خارج الرسوم.',
          'المباراة المعمارية: مسطرة لاختيار تصميم لمشروع معين وإسناد تتبعه لصاحب التصميم الفائز.',
          'الاستشارة المعمارية المفتوحة: للمشاريع التي تصل قيمتها إلى 30 مليون درهم، ومفتوحة لجميع المهندسين.',
          'الاستشارة المعمارية المبسطة: مخصصة للمهندسين المبتدئين للمشاريع التي لا تتجاوز 3 ملايين درهم.',
          'الاستشارة المعمارية المحدودة: للمشاريع التي لا تتجاوز 10 ملايين درهم، وتتطلب استشارة 5 مهندسين على الأقل.',
        ],
      },
      {
        h2: 'تجريد مساطر إبرام الصفقات العمومية من الصفة المادية',
        content: [
          'يشكل تجريد مساطر الصفقات العمومية من الصفة المادية ورشاً استراتيجياً يهدف إلى تحديث الإدارة وتعزيز الشفافية والنجاعة. ويستند هذا التوجه إلى إطار قانوني متكامل، أبرزه الفصل السادس من المرسوم رقم 2-22-431 (المواد 134 إلى 141)، والقرار الوزاري رقم 1692-23 المتعلق بتجريد المساطر والوثائق من الصفة المادية، بالإضافة إلى القانون رقم 43-20 المتعلق بخدمات الثقة بشأن المعاملات الإلكترونية. وتهدف هذه الترسانة القانونية إلى إرساء قواعد الانتقال الكامل نحو التدبير الإلكتروني للصفقات، بدءاً من الإعلان ووصولاً إلى التبليغ، مروراً بتقديم العروض وفتح الأظرفة وتقييمها.',
          'تعتبر "بوابة الصفقات العمومية" حجر الزاوية في منظومة التجريد، حيث تمثل المنصة الإلكترونية الموحدة التي تجمع بين المشترين العموميين والمقاولات المتنافسة. تتيح هذه البوابة نشر البرامج التوقعية والإعلانات عن طلبات العروض، وتنزيل ملفات الاستشارة من طرف المتنافسين، وإيداع العروض بشكل إلكتروني وآمن. وتعكس الأرقام المسجلة سنة 2022 حجم استعمال هذه المنصة، حيث تم نشر ما يزيد عن 39,000 استشارة بقيمة تقديرية فاقت 147 مليار درهم، مما يدل على الدور المحوري الذي أصبحت تلعبه في تفعيل مبادئ العلانية والمنافسة.',
          'تتعدد الوظائف التي توفرها منظومة الشراء الإلكتروني، فإلى جانب "التقديم الإلكتروني للعروض" الذي أصبح القاعدة العامة، نجد مكونات أخرى أساسية. تشمل هذه المكونات "قاعدة بيانات المتعهدين" التي توفر سجلاً وطنياً للمقاولين والموردين ومقدمي الخدمات، و"المزادات الإلكترونية العكسية" كآلية مبتكرة للمنافسة على الأثمان. وقد اعتمد المغرب في تنزيل هذا الورش مقاربة تدريجية وتشاركية، ترتكز على التطوير المستمر للإطار القانوني ومواكبة الفاعلين عبر التكوين والمساعدة التقنية، لضمان انتقال سلس وفعال نحو الإدارة الرقمية الكاملة للطلبيات العمومية.',
        ],
        bullets: [
          'الإطار القانوني: المواد 134 إلى 141 من المرسوم رقم 2-22-431 والقرار التطبيقي رقم 1692-23.',
          'بوابة الصفقات العمومية: المنصة المركزية لنشر الإعلانات، تحميل الملفات، وإيداع العروض إلكترونياً.',
          'التقديم الإلكتروني للعروض: أصبح إلزامياً لجميع الصفقات، مما يضمن سرية العروض والمساواة بين المتنافسين.',
          'قاعدة بيانات المتعهدين: سجل إلكتروني للمقاولات والموردين ومقدمي الخدمات لتسهيل الولوج إلى المعلومات.',
          'المزادات الإلكترونية العكسية: آلية تنافسية إلكترونية تستعمل لاقتناء بعض التوريدات والخدمات العادية.',
          'يهدف التجريد إلى تبسيط الإجراءات، تقليص الآجال، ضمان فعالية النفقة العمومية، وتعزيز الشفافية ومكافحة الفساد.',
        ],
      },
      {
        h2:      'المراقبة والطعون والنزاعات في الصفقات العمومية',
        content: [
          'تُمارَس مراقبة الصفقات العمومية بالمغرب على عدة مستويات: رقابة قبلية تضطلع بها الخزينة العامة للمملكة عند تجاوز الحدود المالية المقررة، ورقابة بعدية يتولاها المجلس الأعلى للحسابات والمجالس الجهوية للحسابات.',
          'عزَّز مرسوم 2023 آليات الشفافية بإلزام نشر نتائج الإسناد والاطلاع على محاضر فتح الأظرفة، وتنظيم مسالك الطعن للمتنافسين المُقصَين بصورة رسمية.',
        ],
        bullets: [
          'لجنة الصفقات: هيئة استشارية تُبدي رأيها في الوثائق النموذجية',
          'الخزينة العامة للمملكة: تأشيرة مسبقة إلزامية عند تجاوز الحدود (مراقبة الانتظام)',
          'المجلس الأعلى للحسابات: رقابة بعدية على التدبير',
          'الطعن الودي لدى صاحب المشروع في أجل 10 أيام من التبليغ',
          'الطعن الإداري أمام الوالي/العامل (سلطة الوصاية)',
          'الطعن القضائي أمام المحكمة الإدارية المختصة',
        ],
      },
    ],
  },

  // ── Urbanisme ──────────────────────────────────────────────────────
  {
    lastUpdated:     '2026-06',
    slug:            'urbanisme-maroc',
    category:        'administratif',
    title:           'Urbanisme et Construction au Maroc : textes juridiques 2026',
    title_ar:        'قانون التعمير والبناء بالمغرب : النصوص القانونية 2026',
    metaDescription: 'Consultez les textes juridiques sur l\'urbanisme au Maroc : loi 12-90, permis de construire, SDAU, plan d\'aménagement, lotissement, infractions urbanistiques.',
    metaDescription_ar: 'اطلع على النصوص القانونية للتعمير بالمغرب : القانون 12-90، رخصة البناء، المخطط التوجيهي، التجزئة، المخالفات التعميرية.',
    h1:              'Urbanisme et Construction au Maroc',
    h1_ar:           'قانون التعمير والبناء بالمغرب',
    intro:           'Le droit de l\'urbanisme au Maroc est principalement régi par la Loi n°12-90 relative à l\'urbanisme et la Loi n°25-90 relative aux lotissements. Ces textes encadrent les permis de construire, les documents d\'urbanisme (SDAU, plans d\'aménagement) et les infractions. Cette page regroupe les textes disponibles dans JuriThèque sur ce domaine.',
    intro_ar:        'يُنظَّم قانون التعمير بالمغرب أساساً بموجب القانون رقم 12-90 المتعلق بالتعمير والقانون رقم 25-90 المتعلق بالتجزئات. تُؤطر هذه النصوص رخص البناء ووثائق التعمير (المخطط التوجيهي، مخططات التهيئة) والمخالفات. تجمع هذه الصفحة النصوص المتاحة في JuriThèque في هذا المجال.',
    legalDomain:     'administratif',
    keywords:        ['urbanisme maroc', 'permis de construire', 'loi 12-90', 'plan d\'aménagement', 'SDAU', 'lotissement', 'certificat de conformité', 'infraction urbanistique', 'agence urbaine'],
    keywords_ar:     ['التعمير المغرب', 'رخصة البناء', 'القانون 12-90', 'مخطط التهيئة', 'المخطط التوجيهي', 'التجزئة', 'شهادة المطابقة', 'المخالفات التعميرية', 'الوكالة الحضرية'],
    searchTerms:     ['urbanisme maroc', 'permis construire maroc', 'loi urbanisme'],
    relatedSlugs:    ['permis-construire-maroc', 'infractions-urbanistiques-maroc', 'collectivites-territoriales-maroc', 'marches-publics-maroc'],
    faq: [
      {
        question: 'Quelle est la loi principale sur l\'urbanisme au Maroc ?',
        answer:   'La Loi n°12-90 relative à l\'urbanisme est le texte fondamental. Elle est complétée par la Loi n°25-90 sur les lotissements et plusieurs décrets d\'application. Consultez les textes disponibles dans JuriThèque.',
      },
      {
        question: 'Comment obtenir un permis de construire au Maroc ?',
        answer:   'Le permis de construire est délivré par le président du conseil communal après avis de l\'agence urbaine. Les conditions et pièces requises sont définies dans la Loi 12-90 et ses décrets d\'application. Consultez les textes dans JuriThèque.',
      },
      {
        question: 'Quelles sont les sanctions pour construction sans permis au Maroc ?',
        answer:   'Les infractions urbanistiques peuvent entraîner la démolition de la construction illégale, des amendes et des poursuites pénales. Les sanctions sont définies dans la Loi 12-90. Consultez les textes disponibles dans JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو القانون الرئيسي للتعمير بالمغرب؟',
        answer:   'القانون رقم 12-90 المتعلق بالتعمير هو النص الأساسي. يُتمم هذا القانون القانونُ رقم 25-90 المتعلق بالتجزئات ومراسيم تطبيقية عدة. راجع النصوص المتاحة في JuriThèque.',
      },
      {
        question: 'كيف تُستخرج رخصة البناء بالمغرب؟',
        answer:   'تُسلِّم رخصةَ البناء رئاسةُ المجلس الجماعي بعد رأي الوكالة الحضرية. تُحدد الشروط والوثائق المطلوبة في القانون 12-90 ومراسيم تطبيقه. راجع النصوص في JuriThèque.',
      },
      {
        question: 'ما هي عقوبات البناء بدون رخصة بالمغرب؟',
        answer:   'قد تُفضي المخالفات التعميرية إلى هدم البناء غير القانوني وفرض غرامات ومتابعات جنائية. تُحدد العقوبات في القانون 12-90. راجع النصوص المتاحة في JuriThèque.',
      },
    ],
    sections: [
      {
        h2:      'Cadre juridique de l\'urbanisme au Maroc : loi 12-90 et textes complémentaires',
        content: [
          'Le droit de l\'urbanisme marocain repose sur deux textes fondamentaux adoptés en 1992 : la Loi n°12-90 relative à l\'urbanisme et la Loi n°25-90 relative aux lotissements, groupes d\'habitations et morcellements. Ces lois ont été complétées par de nombreux décrets d\'application et circulaires.',
          'Les agences urbaines créées par la Loi n°30-89 jouent un rôle central dans l\'instruction des demandes de permis et l\'élaboration des documents d\'urbanisme. Elles relèvent du Ministère de l\'Habitat et de la Politique de la Ville.',
        ],
        bullets: [
          'Loi n°12-90 : urbanisme, permis de construire, documents d\'urbanisme',
          'Loi n°25-90 : lotissements, morcellements, groupes d\'habitations',
          'Loi n°30-89 : création et organisation des agences urbaines',
          'SDAU (Schéma Directeur d\'Aménagement Urbain) : horizon 25 ans',
          'Plan d\'Aménagement (PA) : opposable aux tiers, définit les zones et affectations',
          'Plan de Développement (PD) pour les communes rurales',
        ],
      },
      {
        h2:      'Le permis de construire : conditions, procédure et délais',
        content: [
          'Le permis de construire est obligatoire pour toute construction nouvelle, extension ou surélévation dans les zones urbaines. Il est délivré par le président du conseil communal après instruction par l\'agence urbaine et accord éventuel de services techniques (routes, eau, assainissement).',
          'Le Décret n°2-92-832 du 27 juillet 1993 (modifié) fixe les conditions et la procédure d\'instruction des demandes de permis de construire. Le délai légal d\'instruction est de 30 à 60 jours selon la complexité du projet.',
        ],
        bullets: [
          'Dossier : plans architecturaux signés par un architecte agréé, descriptif, titre foncier',
          'Dépôt : guichet de la commune ou de l\'agence urbaine',
          'Délai d\'instruction : 30 jours (dossier complet) à 60 jours (projets complexes)',
          'Permis tacite : absence de réponse dans les délais vaut accord sous conditions',
          'Permis de construire valable 3 ans (renouvelable une fois)',
          'Certificat de conformité obligatoire à la fin des travaux',
        ],
      },
      {
        h2:      'Infractions urbanistiques et sanctions au Maroc',
        content: [
          'Les infractions urbanistiques sont fréquentes au Maroc et font l\'objet d\'une politique de mise en conformité renforcée. La Loi 12-90 distingue les infractions mineures (non-respect du permis) des infractions graves (construction sans permis en zone inconstructible).',
          'Les communes disposent d\'un pouvoir de police administrative pour constater les infractions et ordonner la régularisation ou la démolition. Les parquets peuvent engager des poursuites pénales en cas d\'infraction grave.',
        ],
        bullets: [
          'Amende administrative de 5 000 à 100 000 dirhams selon la gravité',
          'Ordre de démolition : délivré par le président de la commune',
          'Régularisation possible : dépôt d\'un dossier de régularisation + paiement d\'une amende',
          'Poursuites pénales : emprisonnement de 1 mois à 2 ans pour les cas les plus graves',
          'Responsabilité solidaire : architecte, bureau d\'études et maître d\'ouvrage',
          'Confiscation des matériaux de construction dans certains cas',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'الإطار القانوني للتعمير بالمغرب: القانون 12-90 والنصوص المكملة',
        content: [
          'يرتكز قانون التعمير المغربي على نصَّين أساسيَّين اعتُمدا عام 1992: القانون رقم 12-90 المتعلق بالتعمير، والقانون رقم 25-90 المتعلق بالتجزئات والمجموعات السكنية والتقسيمات. وقد استُكمل هذان القانونان بمراسيم تطبيقية ومناشير عديدة.',
          'تضطلع الوكالات الحضرية المُنشأة بموجب القانون رقم 30-89 بدور محوري في دراسة طلبات رخص البناء وإعداد وثائق التعمير، وهي تتبع وزارة إعداد التراب الوطني والتعمير والإسكان وسياسة المدينة.',
        ],
        bullets: [
          'القانون 12-90: التعمير ورخص البناء ووثائق التعمير',
          'القانون 25-90: التجزئات والتقسيمات والمجموعات السكنية',
          'القانون 30-89: إحداث وتنظيم الوكالات الحضرية',
          'المخطط التوجيهي للتهيئة العمرانية (SDAU): أفق 25 سنة',
          'مخطط التهيئة (PA): ملزِم للغير، يُحدد المناطق والاستعمالات',
          'مخطط التنمية (PD) للجماعات القروية',
        ],
      },
      {
        h2:      'رخصة البناء: الشروط والمسطرة والآجال',
        content: [
          'تُعدُّ رخصة البناء إلزامية لكل بناء جديد أو توسعة أو تعلية في المناطق الحضرية. تُسلِّمها رئاسةُ المجلس الجماعي عقب دراستها من قِبَل الوكالة الحضرية وموافقة المصالح التقنية المختلفة (الطرق والماء والصرف الصحي).',
          'يُحدِّد المرسوم رقم 2-92-832 الصادر في 27 يوليوز 1993 (المعدَّل) شروطَ دراسة طلبات رخص البناء ومسطرتها. ويتراوح أجل الدراسة بين 30 و60 يوماً بحسب تعقيد المشروع.',
        ],
        bullets: [
          'الملف: مخططات معمارية موقَّعة من مهندس معماري معتمَد، ووصف المشروع، والرسم العقاري',
          'الإيداع: شباك الجماعة أو الوكالة الحضرية',
          'أجل الدراسة: 30 يوماً (ملف كامل) إلى 60 يوماً (مشاريع معقدة)',
          'الرخصة الضمنية: انقضاء الآجال دون رد يُعدُّ قبولاً بشروط معينة',
          'الرخصة صالحة لمدة 3 سنوات (قابلة للتجديد مرة واحدة)',
          'شهادة المطابقة إلزامية عند الانتهاء من الأشغال',
        ],
      },
      {
        h2:      'المخالفات التعميرية والعقوبات في المغرب',
        content: [
          'تنتشر المخالفات التعميرية في المغرب وتخضع لسياسة تقنين مشددة. يُميِّز القانون 12-90 بين المخالفات البسيطة (مخالفة رخصة البناء) والمخالفات الجسيمة (البناء بدون رخصة في مناطق غير قابلة للبناء).',
          'تتمتع الجماعات بصلاحيات الشرطة الإدارية لمعاينة المخالفات والأمر بالتسوية أو الهدم. كما يمكن للنيابة العامة تحريك المتابعات الجنائية في حالات المخالفة الجسيمة.',
        ],
        bullets: [
          'غرامة إدارية من 5.000 إلى 100.000 درهم تبعاً لجسامة المخالفة',
          'أمر بالهدم: يُصدره رئيس الجماعة',
          'إمكانية التسوية: إيداع ملف تسوية مع أداء غرامة',
          'متابعات جنائية: حبس من شهر إلى سنتين في أشد الحالات',
          'المسؤولية التضامنية: المهندس المعماري ومكتب الدراسات وصاحب المشروع',
          'مصادرة مواد البناء في بعض الحالات',
        ],
      },
    ],
  },

  // ── État Civil ─────────────────────────────────────────────────────
  {
    lastUpdated:     '2026-06',
    slug:            'etat-civil-maroc',
    category:        'administratif',
    title:           'État Civil au Maroc : textes juridiques et démarches 2026',
    title_ar:        'الحالة المدنية بالمغرب : النصوص القانونية والمساطر 2026',
    metaDescription: 'Consultez les textes sur l\'état civil au Maroc : déclaration de naissance, acte de mariage, acte de décès, livret de famille, légalisation, CNIE.',
    metaDescription_ar: 'اطلع على النصوص المتعلقة بالحالة المدنية بالمغرب : تصريح الولادة، عقد الزواج، رسم الوفاة، بطاقة التعريف الوطنية، التوثيق.',
    h1:              'État Civil au Maroc',
    h1_ar:           'الحالة المدنية بالمغرب',
    intro:           'L\'état civil au Maroc est régi par le Dahir n°1-02-239 portant promulgation de la Loi n°37-99 relative à l\'état civil. Ce texte organise les actes de naissance, de mariage, de décès et les registres d\'état civil. Cette page regroupe les textes disponibles dans JuriThèque sur ce domaine.',
    intro_ar:        'تُنظَّم الحالة المدنية بالمغرب بموجب الظهير رقم 1-02-239 المتعلق بالقانون رقم 37-99 المتعلق بالحالة المدنية. يُنظم هذا النص رسوم الولادة والزواج والوفاة وسجلات الحالة المدنية. تجمع هذه الصفحة النصوص المتاحة في JuriThèque في هذا المجال.',
    legalDomain:     'administratif',
    keywords:        ['état civil', 'acte de naissance', 'acte de mariage', 'acte de décès', 'livret de famille', 'CNIE', 'légalisation', 'registre état civil', 'loi 37-99'],
    keywords_ar:     ['الحالة المدنية', 'رسم الولادة', 'عقد الزواج', 'رسم الوفاة', 'دفتر الحالة المدنية', 'بطاقة التعريف الوطنية', 'التوثيق', 'سجل الحالة المدنية', 'القانون 37-99'],
    searchTerms:     ['état civil maroc', 'acte naissance maroc', 'CNIE maroc'],
    relatedSlugs:    ['code-de-la-famille-maroc', 'collectivites-territoriales-maroc'],
    faq: [
      {
        question: 'Quel est le texte qui régit l\'état civil au Maroc ?',
        answer:   'L\'état civil est régi par la Loi n°37-99 promulguée par le Dahir n°1-02-239 du 3 octobre 2002. Ce texte est disponible dans JuriThèque.',
      },
      {
        question: 'Dans quel délai doit-on déclarer une naissance au Maroc ?',
        answer:   'La déclaration de naissance doit être effectuée dans un délai de 30 jours auprès de l\'officier d\'état civil. Passé ce délai, une procédure judiciaire est nécessaire. Consultez les textes disponibles dans JuriThèque.',
      },
      {
        question: 'Comment obtenir un acte de naissance au Maroc depuis l\'étranger ?',
        answer:   'Les Marocains résidant à l\'étranger peuvent demander leurs actes d\'état civil via les consulats marocains ou le portail e-gov. Les procédures sont encadrées par la Loi 37-99. Consultez les textes dans JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو النص القانوني الذي ينظم الحالة المدنية بالمغرب؟',
        answer:   'تُنظَّم الحالة المدنية بموجب القانون رقم 37-99 الصادر بالظهير رقم 1-02-239 بتاريخ 3 أكتوبر 2002. هذا النص متاح في JuriThèque.',
      },
      {
        question: 'ما هو أجل التصريح بالولادة في المغرب؟',
        answer:   'يجب الإدلاء بتصريح الولادة داخل أجل 30 يوماً لدى ضابط الحالة المدنية. بعد انقضاء هذا الأجل، تستلزم المسطرة تدخلاً قضائياً. راجع النصوص المتاحة في JuriThèque.',
      },
      {
        question: 'كيف تُستخرج وثائق الحالة المدنية من الخارج؟',
        answer:   'يمكن للمغاربة المقيمين بالخارج طلب وثائق الحالة المدنية عبر القنصليات المغربية أو بوابة الخدمات الإلكترونية. تُؤطر الإجراءاتِ القانونُ 37-99. راجع النصوص في JuriThèque.',
      },
    ],
    sections: [
      {
        h2:      'La loi 37-99 : le cadre juridique de l\'état civil au Maroc',
        content: [
          'L\'état civil marocain est régi par la Loi n°37-99 relative à l\'état civil, promulguée par le Dahir n°1-02-239 du 3 octobre 2002. Ce texte organise les actes de naissance, de mariage, de divorce, de décès, ainsi que la tenue des registres d\'état civil par les officiers d\'état civil (présidents des arrondissements et communes).',
          'La réforme de 2002 a modernisé le système en instaurant une numérotation nationale des actes, un système d\'archivage centralisé, et des procédures de rectification et de transcription des actes étrangers. Le Registre National de la Population (RNP) est interconnecté avec les bases d\'état civil.',
        ],
        bullets: [
          'Loi 37-99 : actes d\'état civil, registres, rectifications',
          'Décret n°2-04-683 du 21 juillet 2004 : conditions d\'application de la loi 37-99',
          'Officiers d\'état civil : présidents d\'arrondissements et communes',
          'Registre centralisé à la Direction de l\'État Civil (Ministère de l\'Intérieur)',
          'CNIE : carte nationale d\'identité électronique, base biométrique nationale',
          'Portail e-gov : demande en ligne de copies d\'actes d\'état civil',
        ],
      },
      {
        h2:      'Les principaux actes d\'état civil : déclarations et délais',
        content: [
          'La déclaration des événements familiaux est une obligation légale dont le non-respect peut entraîner des complications administratives et juridiques. Chaque type d\'acte obéit à des délais et procédures spécifiques définis par la Loi 37-99.',
        ],
        bullets: [
          'Déclaration de naissance : 30 jours à partir de la naissance (au-delà → jugement supplétif)',
          'Acte de mariage : établi par l\'adoul ou enregistré par le juge de la famille',
          'Acte de décès : 30 jours, déclarer à la commune du lieu de décès',
          'Transcription de mariage ou naissance à l\'étranger : via les consulats',
          'Rectification d\'acte : demande auprès du tribunal de première instance',
          'Jugements supplétifs : délivrés par le TPI pour les déclarations hors délai',
        ],
      },
      {
        h2:      'Légalisation, apostille et copies d\'actes : démarches pratiques',
        content: [
          'Les documents d\'état civil marocains destinés à être utilisés à l\'étranger nécessitent une légalisation ou une apostille selon les pays. La légalisation est effectuée par le Ministère des Affaires Étrangères marocain ; l\'apostille est applicable pour les pays signataires de la Convention de La Haye de 1961.',
          'Depuis 2021, les Marocains peuvent obtenir des copies de leurs actes d\'état civil en ligne via le portail e-gov du Ministère de l\'Intérieur, sans se déplacer en mairie.',
        ],
        bullets: [
          'Légalisation : Ministère des AE → ambassade / consulat du pays destinataire',
          'Apostille (La Haye 1961) : pour les pays signataires (France, Espagne, Italie, etc.)',
          'Copies d\'actes en ligne : portail e-gov.ma (avec carte CNIE biométrique)',
          'Copies pour MRE : via les consulats marocains dans le pays de résidence',
          'Traduction certifiée : obligatoire si l\'acte doit être produit en langue étrangère',
          'Délai de délivrance : 2 à 5 jours ouvrables (guichet ou en ligne)',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'القانون 37-99: الإطار القانوني للحالة المدنية بالمغرب',
        content: [
          'تُنظَّم الحالة المدنية المغربية بموجب القانون رقم 37-99 المتعلق بالحالة المدنية، الصادر بتنفيذه الظهير رقم 1-02-239 بتاريخ 3 أكتوبر 2002. يُنظِّم هذا النص رسوم الولادة والزواج والطلاق والوفاة، فضلاً عن مسك سجلات الحالة المدنية من قِبَل ضباطها (رؤساء المقاطعات والجماعات).',
          'أدخل إصلاح 2002 تحديثات جوهرية على المنظومة، بوضع ترقيم وطني للرسوم وإرساء نظام أرشفة مركزي، وتبسيط مساطر تصحيح الرسوم وتسجيل الوثائق الأجنبية. وقد أُدمج السجل الوطني للسكان مع قواعد بيانات الحالة المدنية.',
        ],
        bullets: [
          'القانون 37-99: رسوم الحالة المدنية والسجلات والتصحيحات',
          'المرسوم 2-04-683 بتاريخ 21 يوليوز 2004: شروط تطبيق القانون 37-99',
          'ضباط الحالة المدنية: رؤساء المقاطعات والجماعات',
          'السجل المركزي لدى مديرية الحالة المدنية (وزارة الداخلية)',
          'بطاقة التعريف الوطنية الإلكترونية: قاعدة بيومترية وطنية',
          'بوابة الخدمات الإلكترونية: طلب نسخ الرسوم عبر الإنترنت',
        ],
      },
      {
        h2:      'أهم وثائق الحالة المدنية: التصريحات والآجال',
        content: [
          'يُعدُّ التصريح بالأحداث الأسرية التزاماً قانونياً، والإخلال به يُفضي إلى إشكالات إدارية وقانونية. ويخضع كل نوع من الرسوم لآجال وإجراءات خاصة يُحددها القانون 37-99.',
        ],
        bullets: [
          'التصريح بالولادة: خلال 30 يوماً من تاريخ الولادة (بعد الأجل ← حكم استدراكي)',
          'عقد الزواج: يُحرِّره العدلان أو يُسجِّله قاضي الأسرة',
          'رسم الوفاة: داخل 30 يوماً، يُصرَّح به للجماعة التي وقعت فيها الوفاة',
          'تسجيل عقود الزواج أو الولادة في الخارج: عبر القنصليات',
          'تصحيح الرسوم: طلب يُرفع إلى المحكمة الابتدائية',
          'الأحكام الاستدراكية: تُصدرها المحكمة الابتدائية للتصريحات المتأخرة',
        ],
      },
      {
        h2:      'التصديق والأبوستيل ونسخ الرسوم: الإجراءات العملية',
        content: [
          'تستلزم وثائق الحالة المدنية المغربية المُعدَّة للاستعمال بالخارج التصديقَ أو الأبوستيل بحسب البلد المعني. يُنجَز التصديق من قِبَل وزارة الشؤون الخارجية المغربية، فيما يُطبَّق الأبوستيل على الدول الموقِّعة على اتفاقية لاهاي لعام 1961.',
          'منذ عام 2021، يستطيع المغاربة استخراج نسخ رسوم حالتهم المدنية إلكترونياً عبر بوابة وزارة الداخلية، دون الحاجة إلى التنقل.',
        ],
        bullets: [
          'التصديق: وزارة الشؤون الخارجية ثم سفارة/قنصلية البلد المعني',
          'الأبوستيل (لاهاي 1961): للدول الموقِّعة (فرنسا وإسبانيا وإيطاليا وغيرها)',
          'نسخ الرسوم إلكترونياً: بوابة e-gov.ma (ببطاقة التعريف الوطنية البيومترية)',
          'نسخ للمغاربة بالخارج: عبر القنصليات المغربية في بلد الإقامة',
          'الترجمة المعتمَدة: إلزامية إذا كانت الوثيقة ستُنتَج بلغة أجنبية',
          'أجل التسليم: من 2 إلى 5 أيام عمل (شباك أو إلكترونياً)',
        ],
      },
    ],
  },

  // ── Dépenses de Personnel ──────────────────────────────────────────
  {
    lastUpdated:     '2026-06',
    slug:            'depenses-personnel-maroc',
    category:        'administratif',
    title:           'Dépenses de Personnel au Maroc : textes et réglementation 2026',
    title_ar:        'نفقات الموظفين بالمغرب : النصوص والتنظيم 2026',
    metaDescription: 'Consultez les textes sur les dépenses de personnel de l\'État au Maroc : statut général de la fonction publique, rémunération, indemnités, contrôle engagements.',
    metaDescription_ar: 'اطلع على النصوص المتعلقة بنفقات موظفي الدولة بالمغرب : النظام الأساسي للوظيفة العمومية، الأجور، التعويضات، مراقبة الالتزامات.',
    h1:              'Dépenses de Personnel au Maroc',
    h1_ar:           'نفقات الموظفين بالمغرب',
    intro:           'Les dépenses de personnel constituent le premier poste budgétaire de l\'État marocain. Elles sont encadrées par le Statut Général de la Fonction Publique (Dahir n°1-58-008), la Loi Organique des Finances (LOF) et les décrets de rémunération. Cette page regroupe les textes disponibles dans JuriThèque sur ce domaine.',
    intro_ar:        'تُشكِّل نفقات الموظفين أكبر بند في ميزانية الدولة المغربية. تُؤطرها النظامُ الأساسي للوظيفة العمومية (الظهير رقم 1-58-008) والقانون التنظيمي للمالية (LOF) ومراسيم التأجير. تجمع هذه الصفحة النصوص المتاحة في JuriThèque في هذا المجال.',
    legalDomain:     'administratif',
    keywords:        ['dépenses personnel', 'fonction publique', 'salaire fonctionnaire', 'indemnités fonctionnaire', 'statut général fonction publique', 'LOF', 'contrôle engagements', 'TGR', 'visa dépense'],
    keywords_ar:     ['نفقات الموظفين', 'الوظيفة العمومية', 'أجر الموظف', 'تعويضات الموظف', 'النظام الأساسي للوظيفة العمومية', 'القانون التنظيمي للمالية', 'مراقبة الالتزامات', 'الخزينة العامة', 'تأشيرة النفقة'],
    searchTerms:     ['dépenses personnel maroc', 'salaire fonctionnaire maroc', 'fonction publique'],
    relatedSlugs:    ['marches-publics-maroc', 'collectivites-territoriales-maroc'],
    faq: [
      {
        question: 'Quel est le texte de base du statut des fonctionnaires au Maroc ?',
        answer:   'Le Statut Général de la Fonction Publique est établi par le Dahir n°1-58-008 du 24 février 1958, modifié plusieurs fois depuis. Ce texte est disponible dans JuriThèque.',
      },
      {
        question: 'Comment est contrôlée la dépense de personnel au Maroc ?',
        answer:   'Le contrôle des engagements de dépenses est exercé par la Trésorerie Générale du Royaume (TGR). Les dépenses de personnel sont aussi soumises au contrôle du Parlement dans le cadre de la Loi de Finances. Consultez les textes dans JuriThèque.',
      },
      {
        question: 'Quelles sont les composantes de la rémunération d\'un fonctionnaire marocain ?',
        answer:   'La rémunération comprend le traitement de base, les indemnités (résidence, représentation, risques…) et les primes liées au poste. Les textes fixant ces composantes sont disponibles dans JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو النص الأساسي لنظام الموظفين بالمغرب؟',
        answer:   'يُحدد النظامَ الأساسي للوظيفة العمومية الظهيرُ رقم 1-58-008 الصادر في 24 فبراير 1958، وقد عُدِّل مرات عدة منذ ذلك. هذا النص متاح في JuriThèque.',
      },
      {
        question: 'كيف تُراقَب نفقات الموظفين بالمغرب؟',
        answer:   'تتولى الخزينة العامة للمملكة مراقبة الالتزامات بالنفقات. كما تخضع نفقات الموظفين لرقابة البرلمان في إطار قانون المالية. راجع النصوص في JuriThèque.',
      },
      {
        question: 'ما هي مكونات أجر الموظف المغربي؟',
        answer:   'يتضمن الأجر الراتب الأساسي والتعويضات (السكن، التمثيل، المخاطر...) والعلاوات المرتبطة بالمنصب. النصوص المحددة لهذه المكونات متاحة في JuriThèque.',
      },
    ],
    sections: [
      {
        h2: 'Principes d\'accès et catégories de personnel de la fonction publique',
        content: [
          'L\'accès à la fonction publique marocaine est fondé sur des principes constitutionnels et statutaires visant à garantir l\'équité et la méritocratie. L\'article 31 de la Constitution de 2011 consacre le droit des citoyennes et citoyens d\'accéder aux fonctions publiques selon le mérite. Ce principe est réaffirmé par l\'article premier du Statut Général de la Fonction Publique (SGFP), issu du Dahir n° 1-58-008 du 24 février 1958, qui garantit un accès égal sans distinction de sexe. Une condition matérielle fondamentale, précisée à l\'article 7 du même statut, est l\'existence d\'un poste budgétaire vacant. Toute nomination ou promotion qui ne viserait pas à pourvoir une vacance est formellement interdite, liant ainsi le recrutement aux capacités budgétaires de l\'État.',
          'La pierre angulaire du système est le statut de "fonctionnaire titulaire", défini par l\'article 2 du SGFP. Pour acquérir cette qualité, trois conditions cumulatives doivent être remplies : être nommé dans un emploi permanent, être titularisé dans un grade de la hiérarchie administrative, et que cette nomination soit effectuée par l\'autorité compétente (Dahir royal pour les emplois supérieurs, décret du Chef du gouvernement pour les autres). Cette définition exclut de fait plusieurs catégories d\'agents publics, tels que les agents temporaires ou auxiliaires recrutés pour des tâches exceptionnelles, les élus, ou les membres du gouvernement, qui, bien qu\'occupant des fonctions publiques, ne répondent pas à ces critères stricts et ne sont donc pas considérés comme des fonctionnaires au sens du SGFP.',
          'À côté des titulaires, l\'administration emploie du personnel non titulaire. La première catégorie est celle des "fonctionnaires stagiaires", régis par le décret royal n° 62-68 du 17 mai 1968. Il s\'agit de personnes nommées dans un emploi permanent mais qui accomplissent une période probatoire (généralement d\'un an ou deux) avant une éventuelle titularisation. La seconde catégorie est celle des "agents contractuels", dont le recrutement est autorisé par l\'article 6 bis du SGFP. Cette disposition permet aux administrations de recruter des experts ou des agents pour des besoins spécifiques, via un contrat à durée déterminée. Il est crucial de noter que ce type de recrutement, bien que flexible, n\'ouvre en aucun cas droit à une titularisation au sein des cadres de l\'administration.',
        ],
        bullets: [
          'Le principe d\'égalité d\'accès aux emplois publics est garanti par l\'article 31 de la Constitution.',
          'Toute nomination est conditionnée par l\'existence d\'un poste budgétaire vacant, conformément à l\'article 7 du SGFP.',
          'Le fonctionnaire est une personne nommée dans un emploi permanent et titularisée dans un grade (Art. 2 SGFP).',
          'Le fonctionnaire stagiaire est un agent en période probatoire avant sa titularisation.',
          'L\'article 6 bis du SGFP permet le recrutement d\'agents par contrat pour des besoins spécifiques.',
          'Le recrutement par contrat ne peut en aucun cas aboutir à une titularisation dans la fonction publique.',
        ],
      },
      {
        h2: 'La procédure de recrutement par concours dans les emplois publics',
        content: [
          'Le concours constitue la voie royale d\'accès aux emplois publics au Maroc, une procédure encadrée par le décret n° 2-11-621 du 25 novembre 2011. Pour être éligible, tout candidat doit d\'abord satisfaire à des conditions générales, socle commun à tous les recrutements. Celles-ci incluent la possession de la nationalité marocaine, la jouissance des droits civiques et une bonne moralité, ainsi que l\'aptitude physique à exercer la fonction visée, laquelle est généralement vérifiée par une commission médicale après la réussite au concours. Ces prérequis garantissent que les futurs agents de l\'État présentent les qualités fondamentales attendues de tout serviteur public, avant même l\'évaluation de leurs compétences techniques ou académiques.',
          'Au-delà de ce socle commun, des conditions particulières sont exigées en fonction de la nature et du niveau de l\'emploi postulé. La condition de diplôme est la plus déterminante ; le statut particulier de chaque corps de fonctionnaires fixe le niveau et la spécialité des titres requis. Si le diplôme a été obtenu à l\'étranger, un arrêté d\'équivalence est indispensable. Une autre condition spécifique fréquente est la limite d\'âge, également définie par les statuts particuliers, qui peut varier considérablement d\'un corps à l\'autre. Ces exigences spécifiques visent à assurer l\'adéquation parfaite entre le profil du candidat et les compétences techniques nécessaires pour occuper le poste budgétaire vacant.',
          'La procédure de recrutement est formalisée et transparente. Elle débute par un arrêté de l\'autorité compétente qui déclare l\'ouverture du concours. Les candidats constituent alors un dossier comprenant, entre autres, une copie certifiée conforme du diplôme et de la carte d\'identité nationale électronique. À l\'issue des épreuves, une commission de concours établit un procès-verbal et les résultats sont proclamés par un arrêté. Pour finaliser son dossier en vue de la prise en charge financière, le lauréat doit ensuite fournir des pièces complémentaires, notamment le procès-verbal de prise de service, une attestation d\'aptitude physique, et un relevé d\'identité bancaire (RIB) pour la domiciliation de son salaire.',
        ],
        bullets: [
          'Le recrutement sur concours est la principale voie d\'accès, régie par le décret n° 2-11-621.',
          'Les conditions générales incluent la nationalité marocaine, les droits civiques et l\'aptitude physique.',
          'Les conditions particulières, comme le diplôme et la limite d\'âge, sont fixées par les statuts de chaque corps.',
          'Un arrêté d\'équivalence est obligatoire pour les diplômes obtenus à l\'étranger.',
          'La procédure est initiée par un arrêté d\'ouverture du concours et supervisée par une commission dédiée.',
          'Le lauréat doit fournir un procès-verbal de prise de service pour activer sa prise en charge salariale.',
        ],
      },
      {
        h2: 'Le recrutement par contrat : un recours encadré pour l\'administration',
        content: [
          'Introduit par l\'article 6 bis du SGFP, le recrutement par contrat offre à l\'administration publique une souplesse pour répondre à des besoins ponctuels ou faire appel à des compétences rares non disponibles en interne. Ce mécanisme dérogatoire au statut de fonctionnaire est strictement encadré et se décline en deux catégories distinctes : le recrutement d\'experts de haut niveau et celui d\'agents contractuels pour des missions spécifiques. L\'objectif est de permettre à l\'État de s\'adjoindre des compétences pointues pour des projets déterminés, sans pour autant alourdir durablement la masse salariale ni déroger au principe du recrutement par concours comme voie d\'accès normale et permanente à la fonction publique.',
          'Le recrutement d\'experts est soumis à des conditions rigoureuses. Leur nombre est en principe limité à quatre par département ministériel, bien que le Chef du gouvernement puisse autoriser des dépassements pour nécessité de service. Le candidat doit justifier d\'un diplôme de niveau Bac+5 et d\'au moins cinq ans d\'expérience professionnelle pertinente. Le recrutement s\'effectue par appel à candidature. Le contrat est conclu pour une durée maximale de deux ans, renouvelable une seule fois, soit une durée totale ne pouvant excéder quatre ans. Cette limitation temporelle stricte souligne le caractère non permanent de la mission et empêche toute assimilation à un poste de fonctionnaire titulaire.',
          'Le recrutement d\'agents contractuels suit une procédure différente. Leur nombre est fixé par arrêté du Chef du gouvernement sur proposition du ministre concerné. Contrairement aux experts, ces agents sont recrutés par voie de concours, garantissant ainsi un processus de sélection transparent et méritocratique. Les candidats doivent posséder un diplôme permettant l\'accès à un grade équivalent à celui du poste à pourvoir. La durée du contrat est également limitée à deux ans maximum, avec une seule possibilité de renouvellement. Dans les deux cas, expert ou agent, la loi réaffirme clairement que ce type de contrat ne peut, en aucune circonstance, mener à une titularisation au sein de l\'administration.',
        ],
        bullets: [
          'Le fondement juridique est l\'article 6 bis du Statut Général de la Fonction Publique (SGFP).',
          'Deux catégories existent : les experts (recrutés sur dossier) et les agents (recrutés par concours).',
          'Les experts doivent avoir un Bac+5 et 5 ans d\'expérience ; leur contrat est de 2 ans, renouvelable une fois.',
          'Les agents contractuels sont recrutés par concours pour un contrat de 2 ans, renouvelable une fois.',
          'Le nombre d\'experts est limité à 4 par ministère, sauf dérogation du Chef du gouvernement.',
          'Ce mode de recrutement n\'ouvre jamais droit à une titularisation dans les cadres de l\'État.',
        ],
      },
      {
        h2: 'L\'avancement d\'échelon : progression et impact de la notation',
        content: [
          'L\'avancement d\'échelon représente la progression salariale et de carrière la plus courante pour un fonctionnaire, se traduisant par le passage à un échelon supérieur au sein d\'un même grade. Ce mécanisme n\'est pas uniquement basé sur le temps passé. Il est régi par une double condition : l\'ancienneté dans l\'échelon et la performance professionnelle du fonctionnaire, évaluée annuellement. La procédure de notation et d\'évaluation, fixée par le décret n°2.05.1367 du 2 décembre 2005, est donc au cœur de ce système. Elle vise à objectiver l\'appréciation de la valeur professionnelle et à moduler la vitesse de progression de carrière en fonction du mérite de chaque agent.',
          'Le système d\'avancement est structuré autour de trois rythmes distincts : un rythme rapide, un rythme moyen et un rythme lent. L\'attribution de l\'un de ces rythmes dépend directement de la note chiffrée obtenue par le fonctionnaire lors de son évaluation annuelle. Une note comprise entre 16 et 20 sur 20 permet de bénéficier du rythme d\'avancement rapide. Une note se situant entre 10 (inclus) et 16 (exclus) donne droit au rythme moyen, qui est le rythme de référence. Enfin, une note inférieure à 10 sur 20 entraîne l\'application du rythme lent, ralentissant de fait la progression de l\'agent. Ce dispositif lie directement la performance individuelle à la progression salariale.',
          'Concrètement, la durée de service requise pour passer à l\'échelon supérieur varie significativement selon le rythme obtenu. Par exemple, pour passer de l\'échelon 5 à l\'échelon 6, un fonctionnaire devra justifier de 2 ans d\'ancienneté avec le rythme rapide, 2 ans et demi avec le rythme moyen, et 3 ans et demi avec le rythme lent. L\'écart se creuse davantage dans les échelons supérieurs. Cette modulation incite les fonctionnaires à améliorer leur performance, car une bonne notation se traduit par une accélération tangible de leur carrière et de leur rémunération, créant ainsi un levier de management basé sur la reconnaissance du mérite.',
        ],
        bullets: [
          'L\'avancement d\'échelon est la progression au sein d\'un même grade, basée sur l\'ancienneté et la notation.',
          'La procédure de notation est encadrée par le décret n°2.05.1367 du 2 décembre 2005.',
          'Il existe trois rythmes d\'avancement : rapide, moyen et lent, déterminés par la note annuelle.',
          'Le rythme rapide est accordé pour une note supérieure ou égale à 16/20.',
          'Le rythme moyen correspond à une note allant de 10/20 à 15,99/20.',
          'Le rythme lent, pour une note inférieure à 10/20, allonge la durée requise pour changer d\'échelon.',
        ],
      },
      {
        h2: 'L\'avancement de grade : les voies de promotion hiérarchique',
        content: [
          'Contrairement à l\'avancement d\'échelon qui est une progression horizontale au sein d\'un même grade, l\'avancement de grade constitue une véritable promotion verticale. Il permet au fonctionnaire d\'accéder à un grade supérieur dans la hiérarchie de son corps, ce qui s\'accompagne de responsabilités accrues et d\'une nouvelle grille de rémunération plus avantageuse. Cette étape majeure dans une carrière n\'est pas automatique et est conditionnée par des règles strictes. Les statuts particuliers, propres à chaque corps de fonctionnaires, définissent les différentes voies possibles pour cet avancement, qui reposent principalement sur le mérite, la compétence et l\'ancienneté.',
          'La voie la plus méritocratique est celle de la promotion par concours ou examen professionnel. Cette modalité est ouverte aux fonctionnaires qui remplissent des conditions d\'ancienneté spécifiques dans leur grade actuel. Elle leur offre l\'opportunité de démontrer, à travers des épreuves, qu\'ils possèdent les aptitudes et connaissances requises pour assumer les fonctions du grade supérieur. Ce système favorise une saine émulation au sein de l\'administration et garantit que les promotions sont attribuées sur la base de compétences avérées, offrant une voie de progression transparente et équitable pour les agents les plus méritants.',
          'Une autre voie de promotion est l\'avancement "au choix". Il est basé sur l\'inscription des fonctionnaires éligibles (remplissant des conditions d\'ancienneté) sur un tableau d\'avancement annuel. L\'administration procède ensuite à la promotion des agents inscrits, dans la limite d\'un quota fixé par la réglementation. La sélection se fonde sur la valeur professionnelle de l\'agent, appréciée notamment à travers ses notations. Enfin, il existe une voie plus rare, l\'avancement "sur titre", qui permet dans certains cas prévus par les statuts particuliers (par exemple pour les lauréats de l\'ENSA), d\'être promu à un grade supérieur suite à l\'obtention d\'un diplôme spécifique en cours de carrière.',
        ],
        bullets: [
          'L\'avancement de grade est une promotion verticale vers un grade hiérarchiquement supérieur.',
          'La voie principale est le concours ou l\'examen professionnel, basé sur le mérite et l\'ancienneté.',
          'La promotion "au choix" s\'effectue par inscription sur un tableau d\'avancement annuel, dans la limite de quotas.',
          'La sélection pour la promotion au choix prend en compte l\'ancienneté et la notation de l\'agent.',
          'L\'avancement "sur titre" est une voie exceptionnelle liée à l\'obtention de diplômes spécifiques.',
          'Chaque voie de promotion est encadrée par des conditions précises définies dans les statuts particuliers.',
        ],
      },
      {
        h2: 'Gouvernance de la fonction publique : organes de pilotage et de consultation',
        content: [
          'La gestion des dépenses de personnel et de la carrière des fonctionnaires est assurée par une architecture institutionnelle précise, définie par le SGFP. Au sommet se trouve l\'autorité gouvernementale chargée de la fonction publique. Son rôle, décrit à l\'article 8 du SGFP, est central : elle veille à l\'application du statut, élabore les règles générales de recrutement et de formation, et suit les politiques de rémunération en accord avec le ministère des Finances. Tout texte réglementaire ayant un impact sur les fonctionnaires doit recevoir son visa, et celui du ministre des Finances s\'il a des répercussions budgétaires, assurant ainsi une cohérence d\'ensemble et la maîtrise des dépenses publiques.',
          'Le Conseil Supérieur de la Fonction Publique (CSFP) constitue le principal organe consultatif. Présidé par le Chef du gouvernement, il est obligatoirement saisi de tout projet de loi modifiant le SGFP et peut examiner toute question d\'ordre général sur la fonction publique. Sa composition, fixée par le décret n° 2-01-3059 du 25 mars 2002, est paritaire : il comprend des représentants de l\'administration et des collectivités territoriales d\'une part, et des représentants élus des fonctionnaires d\'autre part. Cette structure garantit un dialogue social institutionnalisé au plus haut niveau, permettant de débattre des grandes orientations en matière de gestion des ressources humaines publiques.',
          'Au niveau décentralisé, les Commissions Administratives Paritaires (CAP) sont des organes de consultation essentiels dans la gestion quotidienne des carrières. Instituées dans chaque administration, elles sont composées à nombre égal de représentants de l\'administration et de représentants du personnel élus. Leur compétence est cruciale pour les décisions individuelles : elles doivent être consultées sur des sujets tels que la titularisation des stagiaires, la notation, les propositions d\'avancement d\'échelon et de grade, les sanctions disciplinaires ou encore la mise en disponibilité. Leur avis, bien que consultatif, constitue une garantie fondamentale pour le fonctionnaire, assurant transparence et équité dans le déroulement de sa carrière.',
        ],
        bullets: [
          'L\'autorité gouvernementale chargée de la fonction publique pilote l\'application du SGFP (Art. 8 SGFP).',
          'Le Conseil Supérieur de la Fonction Publique (CSFP) est un organe consultatif paritaire au niveau national.',
          'Le CSFP donne son avis sur les projets de loi et les grandes orientations de la politique RH de l\'État.',
          'Les Commissions Administratives Paritaires (CAP) sont des instances locales, également paritaires.',
          'Les CAP sont consultées sur les décisions individuelles : avancement, notation, discipline, titularisation.',
          'La composition du CSFP est fixée par le décret n° 2-01-3059 du 25 mars 2002.',
        ],
      }
    ],

    sections_ar: [
      {
        h2: 'المبادئ الأساسية والشروط العامة للولوج إلى الوظيفة العمومية',
        content: [
          'يكرس النظام القانوني المغربي مبدأ المساواة كقاعدة أساسية للولوج إلى الوظائف العمومية. وينص الفصل 31 من الدستور على أن الدولة والمؤسسات العمومية والجماعات الترابية تعمل على تعبئة كل الوسائل المتاحة لتيسير استفادة المواطنات والمواطنين، على قدم المساواة، من الحق في الولوج إلى الوظائف العمومية حسب الاستحقاق. ويؤكد الظهير الشريف رقم 1.58.008 الصادر في 24 فبراير 1958 بمثابة النظام الأساسي العام للوظيفة العمومية هذا المبدأ في فصله الأول، حيث يقر بحق كل مغربي في الوصول إلى الوظائف العمومية على قدم المساواة، ويمنع أي تمييز بين الجنسين في تطبيق مقتضياته، ما لم تنص قوانين خاصة على خلاف ذلك. هذا المبدأ يضمن أن التوظيف لا يتم إلا على أساس الكفاءة والجدارة.',
          'إلى جانب المبادئ الدستورية، يحدد النظام الأساسي العام للوظيفة العمومية مجموعة من الشروط العامة التي يجب أن تتوفر في كل مترشح. أول هذه الشروط هو التمتع بالجنسية المغربية، مع مراعاة بعض الاستثناءات المحددة قانوناً. الشرط الثاني هو التمتع بالحقوق الوطنية وحسن السيرة والسلوك، أو ما عبر عنه المشرع بـ "المروءة"، وهو ما يتم إثباته عادة عبر مستخرج من السجل العدلي. أما الشرط الثالث فيتمثل في استيفاء شروط القدرة البدنية التي يتطلبها القيام بالوظيفة، حيث يتم التحقق من هذا الشرط من خلال فحص طبي تجريه لجنة طبية مختصة. هذه الشروط تعتبر حجر الزاوية لأي عملية توظيف في الإدارات العمومية وتضمن حداً أدنى من الأهلية في المترشحين.',
          'بالإضافة إلى الشروط العامة، هناك شروط خاصة تختلف باختلاف طبيعة الوظيفة والإطار المطلوب. أبرز هذه الشروط هو شرط الشهادات والمؤهلات العلمية، حيث يحدد كل نظام أساسي خاص الدبلومات المطلوبة للولوج إلى مختلف الدرجات. وفي حالة الشهادات الأجنبية، يُشترط تقديم قرار المعادلة الصادر عن السلطة الحكومية المختصة. كما يوجد شرط السن، حيث يتم تحديد سن أقصى للتوظيف يختلف حسب الهيئات والأسلاك، وغالباً ما يكون محدداً في 45 سنة للتوظيف في الدرجات المرتبة في سلم الأجور رقم 10 وما فوق، و40 سنة للدرجات الأخرى. وأخيراً، يبقى الشرط الجوهري المتمثل في توفر منصب مالي شاغر بالميزانية، إذ يمنع الفصل 7 من النظام الأساسي أي تعيين لا يهدف إلى سد شغور.',
        ],
        bullets: [
          'تكريس مبدأ المساواة في الولوج للوظائف العمومية بناء على الاستحقاق طبقا للفصل 31 من الدستور.',
          'ضرورة التمتع بالجنسية المغربية والحقوق الوطنية وحسن السيرة (المروءة) كشرط أساسي.',
          'وجوب استيفاء شروط القدرة البدنية التي يتطلبها القيام بالوظيفة، والتي تثبت بشهادة طبية من لجنة مختصة.',
          'شرط التوفر على الشهادات العلمية المطلوبة لشغل المنصب، مع وجوب تقديم قرار المعادلة عند الاقتضاء.',
          'التقيد بشرط السن الأقصى للتوظيف المحدد في النصوص التنظيمية الخاصة بكل هيئة.',
          'حظر أي تعيين أو ترقية لا يكون الغرض منها شغل منصب مالي شاغر ومحدث قانونيا.',
        ],
      },
      {
        h2: 'مسارات التوظيف: من المباراة العمومية إلى التوظيف بالتعاقد',
        content: [
          'يعتبر التوظيف عن طريق المباراة المبدأ العام والأداة الرئيسية للولوج إلى الوظائف العمومية في المغرب، وذلك تكريساً لمبادئ الشفافية وتكافؤ الفرص والاستحقاق. وينظم المرسوم رقم 2.11.621 الصادر في 25 نوفمبر 2011 شروط وكيفيات تنظيم مباريات التوظيف في المناصب العمومية. تتضمن هذه المسطرة الإعلان عن المباراة وتحديد المناصب المفتوحة والشروط المطلوبة، ثم إجراء اختبارات كتابية وشفوية أو تطبيقية لتقييم كفاءات المترشحين، وتنتهي بالإعلان عن لائحة الناجحين النهائية ولائحة الانتظار. وقد كان معمولاً في السابق بالتوظيف المباشر بناء على الشهادات (sur titre)، إلا أنه أصبح استثناءً يقتصر على حالات محدودة جداً كخريجي بعض المدارس العليا المتخصصة.',
          'لمواجهة الحاجة إلى كفاءات متخصصة ونادرة في السوق، فتح الفصل 6 مكرر من النظام الأساسي العام للوظيفة العمومية الباب أمام الإدارات للجوء إلى التوظيف بموجب عقد. المسار الأول يهم الخبراء، حيث يمكن لكل قطاع وزاري، بعد موافقة رئيس الحكومة، توظيف ما يصل إلى أربعة خبراء. يشترط في الخبير أن يكون حاصلاً على شهادة عليا (باك+5) مع خبرة مهنية لا تقل عن خمس سنوات. يتم التوظيف عن طريق دعوة مفتوحة للترشح، ويُبرم العقد لمدة أقصاها سنتان قابلة للتجديد مرة واحدة فقط، أي بحد أقصى أربع سنوات في المجموع. هذا المسار يوفر مرونة كبيرة للإدارة للاستعانة بمهارات غير متوفرة ضمن أطرها.',
          'المسار الثاني للتوظيف بالتعاقد يخص "الأعوان"، ويتم اللجوء إليه عند الاقتضاء لتلبية حاجيات محددة. يتم تحديد عدد المناصب بموجب قرار لرئيس الحكومة بناء على اقتراح من الوزير المعني. وخلافاً للخبراء، يتم توظيف هؤلاء الأعوان عن طريق مباراة. تشمل الشروط الجنسية المغربية، والتمتع بالحقوق المدنية، وعدم تجاوز سن التقاعد، بالإضافة إلى التوفر على شهادة تسمح بالولوج إلى درجة معادلة للمنصب. مدة العقد لا تتجاوز سنتين قابلة للتجديد مرة واحدة. ومن الأهمية بمكان التأكيد على أن هذا النوع من التوظيف، سواء تعلق بالخبراء أو الأعوان، لا يخول بأي حال من الأحوال الحق في الترسيم في أطر الإدارة العمومية.',
        ],
        bullets: [
          'التوظيف عبر المباراة هو المبدأ العام، منظم بموجب المرسوم رقم 2.11.621 لضمان تكافؤ الفرص.',
          'يمكن للإدارة اللجوء للتعاقد مع خبراء (بحد أقصى 4 لكل وزارة) لمدة سنتين قابلة للتجديد مرة واحدة.',
          'يشترط في الخبير المتعاقد شهادة عليا (باك+5) وخبرة مهنية لا تقل عن 5 سنوات ويتم اختياره عبر دعوة للترشح.',
          'يتم أيضا توظيف أعوان متعاقدين عبر مباراة لمدة أقصاها سنتان قابلة للتجديد مرة واحدة.',
          'يجب على العون المتعاقد التوفر على دبلوم يسمح له بالولوج إلى درجة معادلة للمنصب الذي سيشغله.',
          'التوظيف بموجب عقد، سواء للخبراء أو الأعوان، لا يمنح الحق في الترسيم في أطر الإدارة.',
        ],
      },
      {
        h2: 'التصنيف القانوني للعاملين بالإدارة: الموظفون الرسميون وغير الرسميين',
        content: [
          'يُعرّف الفصل الثاني من النظام الأساسي العام للوظيفة العمومية الموظف بأنه "كل شخص يعين في وظيفة قارة ويرسم في إحدى رتب السلم الخاص بأسلاك الإدارة التابعة للدولة". يوضح هذا التعريف الشروط الثلاثة المتراكمة لاكتساب صفة الموظف المرسم (Titulaire). أولاً، يجب أن يتم التعيين في "وظيفة قارة"، أي منصب دائم ومدرج في هيكل الإدارة. ثانياً، يجب أن يصدر قرار التعيين عن السلطة المختصة قانوناً. ثالثاً، وهو الشرط المميز، يجب أن يتم "ترسيم" المعني بالأمر في درجة معينة، والترسيم هو الإجراء الإداري الذي يضفي الطابع الدائم والنهائي على العلاقة الوظيفية بعد قضاء فترة تدريب ناجحة، مما يمنح الموظف جميع الحقوق والضمانات التي يكفلها النظام الأساسي.',
          'قبل الوصول إلى وضعية الترسيم، يمر الموظف بمرحلة انتقالية هي فترة التمرين. فالموظف المتمرن (Stagiaire)، حسب المرسوم الملكي رقم 62.68 بتاريخ 17 مايو 1968، هو كل شخص تم تعيينه في وظيفة قارة لكن لم يتم الإعلان عن ترسيمه بعد. تعتبر هذه الفترة، التي تتراوح مدتها بين سنة وسنتين حسب الهيئة، بمثابة فترة اختبار تهدف إلى التحقق من كفاءة الموظف وقدرته على ممارسة المهام المنوطة به. خلال هذه الفترة، يخضع المتمرن لنفس واجبات الموظف المرسم ويتمتع بمعظم حقوقه، لكن علاقته بالإدارة تظل مؤقتة وقابلة للإنهاء في حالة عدم إثبات الكفاءة المهنية المطلوبة، وذلك بعد استشارة اللجنة الإدارية المتساوية الأعضاء.',
          'إلى جانب الموظفين الرسميين (مرسمين ومتمرنين)، تستعين الإدارة بفئات أخرى من الأعوان غير الرسميين (Non-titulaires). تشمل هذه الفئة بشكل أساسي الأعوان المتعاقدين، سواء كانوا خبراء أو أعوانا تم توظيفهم بموجب الفصل 6 مكرر من النظام الأساسي. هؤلاء تربطهم بالإدارة علاقة تعاقدية محددة المدة والشروط، ولا يتمتعون بضمانات الاستقرار الوظيفي ولا يحق لهم الترسيم. كما تضم هذه الفئة أعضاء دواوين الوزراء والموظفين العاملين في مكاتبهم ومنازلهم، الذين ينتهي تشغيلهم بانتهاء مهام الوزير. ويخرج من نطاق الموظفين العموميين أيضاً الأعوان المؤقتون أو المياومون الذين يتم تشغيلهم للقيام بأعمال عرضية ومؤقتة.',
        ],
        bullets: [
          'الموظف المرسم هو كل شخص عين في وظيفة قارة ورُسّم في إحدى رتب السلم الإداري للدولة.',
          'الموظف المتمرن هو من عين في منصب دائم لكنه لم يرسم بعد، ويقضي فترة تدريب لتقييم كفاءته.',
          'الأعوان المتعاقدون يتم تشغيلهم بموجب عقود محددة المدة لتلبية حاجيات خاصة أو خبرات نادرة.',
          'أعضاء دواوين الوزراء وموظفو مكاتبهم ومنازلهم يعتبرون من فئة الأعوان غير الرسميين.',
          'الترسيم هو الإجراء الذي ينقل الموظف من وضعية مؤقتة (متمرن) إلى وضعية نظامية دائمة.',
          'لا يكتسب صفة الموظف الأعوان المؤقتون والمساعدون المعينون للقيام بمهام استثنائية وغير دائمة.',
        ],
      },
      {
        h2: 'آليات الترقية وتطور المسار المهني للموظف',
        content: [
          'تمثل الترقية الآلية الأساسية لتطور المسار المهني للموظف العمومي، وهي تنقسم إلى نوعين رئيسيين: الترقية في الرتبة والترقية في الدرجة. تعتبر هذه الآليات حافزاً مهماً للموظفين، حيث يترتب عليها تحسن في الوضعية الإدارية والمالية. الترقية في الرتبة (Avancement d\'échelon) هي انتقال الموظف من رتبة إلى الرتبة الموالية مباشرة داخل نفس الدرجة (الإطار)، ويترتب عليها زيادة في الراتب الأساسي. أما الترقية في الدرجة (Avancement de grade) فهي أكثر أهمية، حيث تعني انتقال الموظف من درجته الحالية إلى درجة أعلى، مما يفتح أمامه آفاقاً جديدة من حيث المسؤوليات والتعويضات، وهي تمثل قفزة نوعية في مساره المهني.',
          'تخضع الترقية في الرتبة لمعيارين متلازمين هما الأقدمية والنقطة العددية السنوية التي يمنحها الرئيس المباشر لتقييم أداء الموظف. وبناءً على هذه النقطة، يتم تحديد نسق الترقية وفقاً للمرسوم رقم 2.05.1367 الصادر في 2 ديسمبر 2005. هناك ثلاثة أنساق: النسق السريع للموظفين الحاصلين على نقطة تتراوح بين 16 و20، والنسق المتوسط للحاصلين على نقطة بين 10 وأقل من 16، والنسق البطيء للحاصلين على نقطة أقل من 10. وتختلف مدة الأقدمية المطلوبة للانتقال من رتبة إلى أخرى حسب النسق، فمثلاً، الانتقال من الرتبة 5 إلى 6 يتطلب سنتين في النسق السريع، وسنتين ونصف في المتوسط، وثلاث سنوات ونصف في النسق البطيء.',
          'أما الترقية في الدرجة فتتم عبر ثلاث طرق رئيسية. الطريقة الأولى والأكثر شيوعاً هي امتحان الكفاءة المهنية، وهو مفتوح للموظفين الذين استوفوا شرط الأقدمية المحدد في درجتهم. الطريقة الثانية هي الترقية بالاختيار، وتتم بعد التسجيل في جدول الترقي السنوي بناءً على الأقدمية في الدرجة والنقطة المهنية، وذلك في حدود حصيص (كوطا) سنوي محدد. أما الطريقة الثالثة، وهي استثنائية، فتتمثل في الترقية بناءً على الشهادات الجامعية المحصل عليها خلال المسار المهني، والتي تسمح بالولوج إلى درجة أعلى. وتخضع جميع قرارات الترقية، سواء في الرتبة أو الدرجة، لتأشيرة المصالح المختصة قبل تنفيذها مالياً.',
        ],
        bullets: [
          'الترقية في الرتبة تتم بناءً على الأقدمية والنقطة العددية السنوية الممنوحة للموظف.',
          'توجد ثلاثة أنساق للترقية في الرتبة: سريع (نقطة بين 16 و20)، متوسط (بين 10 و16)، وبطيء (أقل من 10).',
          'تختلف مدة الأقدمية المطلوبة للانتقال من رتبة لأخرى حسب النسق المعتمد.',
          'الترقية في الدرجة (الإطار) تتم إما عن طريق امتحان الكفاءة المهنية أو بالاختيار بعد التقييد في جدول الترقي.',
          'تخصص نسبة مئوية (كوطا) سنوية للترقية بالاختيار لفائدة الموظفين المستوفين لشروط الأقدمية.',
          'تسمح الترقية في الدرجة بالانتقال إلى إطار أعلى وما يترتب عن ذلك من زيادة في الأجر والمسؤوليات.',
        ],
      },
      {
        h2: 'الهيئات المركزية لتنظيم وتدبير شؤون الموظفين',
        content: [
          'يعهد بتدبير شؤون الموظفين ونفقاتهم إلى مجموعة من الهيئات المركزية التي تضمن حسن تطبيق القوانين والتنسيق بين مختلف الإدارات. على رأس هذه الهيئات، نجد السلطة الحكومية المكلفة بالوظيفة العمومية، والتي يحدد الفصل 8 من النظام الأساسي العام مهامها. فهي تسهر على التطبيق السليم للنظام الأساسي، وتعمل بالاتفاق مع وزارة المالية والوزارات المعنية على وضع القواعد العامة للتوظيف والتكوين، وتتابع تطبيق المبادئ المتعلقة بتنظيم الأطر ونظام الأجور والاحتياط الاجتماعي. كما تتولى هذه السلطة التأشير على النصوص التنظيمية المتعلقة بالوظيفة العمومية، مما يمنحها دوراً محورياً في توحيد قواعد التدبير الإداري للموارد البشرية.',
          'إلى جانب السلطة التنفيذية، أحدث المشرع المجلس الأعلى للوظيفة العمومية كهيئة استشارية عليا. يرأس هذا المجلس رئيس الحكومة أو من يفوضه، ويضم في عضويته ممثلين عن الإدارة والجماعات الترابية، بالإضافة إلى ممثلين منتخبين عن الموظفين. يختص المجلس بالنظر في كل مشاريع القوانين التي تهدف إلى تعديل النظام الأساسي، ويبدي رأيه في التوجهات الحكومية المتعلقة بسياسات التكوين المستمر، ويقترح كل التدابير الكفيلة بتحسين نظام تدبير الموارد البشرية. وبذلك، يشكل المجلس فضاءً للحوار الاجتماعي المؤسساتي وضمانة أساسية لحقوق الموظفين وتطوير المنظومة الإدارية.',
          'على المستوى العملي والإجرائي، تلعب اللجان الإدارية المتساوية الأعضاء دوراً حيوياً في تدبير المسار المهني للموظفين. تُحدث هذه اللجان على مستوى كل إدارة، وتتكون من عدد متساو من ممثلي الإدارة المعينين وممثلي الموظفين المنتخبين. تتمتع هذه اللجان باختصاصات استشارية واسعة، حيث تبدي رأيها في قضايا جوهرية مثل ترسيم الموظفين المتمرنين، والترقية في الرتبة والدرجة، ومنح الرخص لأسباب صحية، والإحالة على الاستيداع، والإجراءات التأديبية. ورغم أن آراءها استشارية، إلا أنها تكتسي أهمية بالغة وتعتبر ضمانة أساسية لإشراك الموظفين في القرارات التي تهم مسارهم المهني.',
        ],
        bullets: [
          'السلطة الحكومية المكلفة بالوظيفة العمومية تسهر على تطبيق النظام الأساسي وتنسق مع وزارة المالية في وضع قواعد التوظيف والأجور.',
          'المجلس الأعلى للوظيفة العمومية هيئة استشارية عليا يرأسها رئيس الحكومة، وتضم ممثلين عن الإدارة والموظفين.',
          'يختص المجلس الأعلى بإبداء الرأي في مشاريع القوانين المتعلقة بالموظفين وسياسات التكوين المستمر.',
          'تُحدث اللجان الإدارية المتساوية الأعضاء على مستوى كل إدارة، وتتألف من ممثلين عن الإدارة وممثلين منتخبين عن الموظفين.',
          'تستشار اللجان الإدارية في قضايا المسار المهني للموظف كالترسيم، والترقية في الرتبة والدرجة، والإجراءات التأديبية.',
          'يؤشر وزير المالية على النصوص التنظيمية المتعلقة بالوظيفة العمومية التي لها انعكاسات مالية على ميزانية الدولة.',
        ],
      },
      {
        h2: 'الوثائق الثبوتية للتوظيف وإجراءات مراقبة نفقات الموظفين',
        content: [
          'تتطلب عملية التوظيف تكوين ملف إداري دقيق لكل موظف جديد، ويقع على عاتق الآمر بالصرف (الإدارة المعنية) مسؤولية إعداده وتجميعه. يتضمن هذا الملف مجموعة من الوثائق الأساسية التي تثبت استيفاء المترشح للشروط القانونية. من بين هذه الوثائق، نجد قرار التعيين، وقرار فتح المباراة، ومحضر لجنة المباراة، وقرار الإعلان عن النتائج النهائية. كما يضم الملف نسخاً مصادقاً على مطابقتها للأصل من الشهادات والدبلومات المطلوبة، ونسخة من بطاقة التعريف الوطنية الإلكترونية، ومستخرجاً من السجل العدلي أو بطاقة السوابق، وشهادة طبية تثبت القدرة البدنية، ومحضر الالتحاق بالعمل الذي يحدد تاريخ بداية الأثر المالي للتعيين.',
          'لأجل صرف أول راتب للموظف الجديد، يجب على الآمر بالصرف أن يدلي للمحاسب العمومي بمجموعة محددة من الوثائق الثبوتية التي تمكنه من التحقق من صحة النفقة. هذه الوثائق، التي تعتبر ضرورية للتأشير على الحوالة الأولى، تشمل بشكل أساسي قرار التعيين، ونسخاً مصادقاً عليها من الشهادات المطلوبة مع قرارات المعادلة عند الاقتضاء، ونسخة مصادق عليها من بطاقة التعريف الوطنية الإلكترونية، بالإضافة إلى شيك ملغى أو شهادة التعريف البنكي (RIB) للموظف. هذه القائمة المختصرة تمثل الحد الأدنى المطلوب من قبل أجهزة الرقابة المالية للشروع في أداء الأجور، وتضمن أن النفقة تستند إلى أساس قانوني سليم.',
          'تشكل هذه الإجراءات الوثائقية جزءاً لا يتجزأ من منظومة مراقبة الالتزام بنفقات الدولة. فالهدف هو التأكد من أن كل عملية توظيف تحترم المقتضيات القانونية والتنظيمية، وعلى رأسها المبدأ المنصوص عليه في الفصل 7 من النظام الأساسي العام للوظيفة العمومية، والذي يمنع منعاً باتاً أي تعيين لا يهدف إلى شغل منصب مالي شاغر ومحدث قانوناً في الميزانية. يقوم المراقب المالي بالتحقق من وجود المنصب المالي وتوفر الاعتمادات اللازمة قبل منح تأشيرته، بينما يتأكد المحاسب العمومي من صحة الوثائق الثبوتية قبل تنفيذ عملية الصرف، مما يضمن شرعية وسلامة نفقات الموظفين.',
        ],
        bullets: [
          'يجب على الآمر بالصرف تجميع ملف توظيف كامل يتضمن قرار التعيين ومحاضر المباراة ونسخ مصادق عليها من الشواهد.',
          'من بين الوثائق الأساسية: نسخة من بطاقة التعريف الوطنية الإلكترونية، ومستخرج من السجل العدلي، وشهادة القدرة البدنية.',
          'لصرف أول أجرة، يجب الإدلاء للمحاسب العمومي بقرار التعيين، ونسخة من الدبلوم، ونسخة من بطاقة التعريف، والتعريف البنكي.',
          'يمنع منعا كليا كل تعيين أو ترقية لا يكون الغرض منها شغل منصب مالي شاغر ومحدث قانونيا.',
          'تخضع ملفات التوظيف لتأشيرة مراقبة الالتزام بنفقات الدولة قبل أي صرف مالي.',
          'يتم إرفاق وثائق خاصة عند الاقتضاء، كبطاقة معاق أو ما يثبت صفة مقاوم أو مكفول الأمة.',
        ],
      }
    ],
  },

  // ── Recouvrement des Créances Publiques ────────────────────────────
  {
    lastUpdated:     '2026-06',
    slug:            'recouvrement-creances-publiques-maroc',
    category:        'administratif',
    title:           'Recouvrement des Créances Publiques au Maroc : textes 2026',
    title_ar:        'تحصيل الديون العمومية بالمغرب : النصوص القانونية 2026',
    metaDescription: 'Consultez les textes sur le recouvrement des créances publiques au Maroc : code de recouvrement, TGR, avis à tiers détenteur, commandement, saisie.',
    metaDescription_ar: 'اطلع على النصوص المتعلقة بتحصيل الديون العمومية بالمغرب : مدونة التحصيل، الخزينة العامة، الإشعار للغير الحائز، الأمر بالأداء، الحجز.',
    h1:              'Recouvrement des Créances Publiques au Maroc',
    h1_ar:           'تحصيل الديون العمومية بالمغرب',
    intro:           'Le recouvrement des créances publiques au Maroc est régi par la Loi n°15-97 formant Code de Recouvrement des Créances Publiques. Ce texte définit les procédures amiables et forcées utilisées par la Trésorerie Générale du Royaume (TGR) pour recouvrer les impôts, taxes et autres créances de l\'État. Cette page regroupe les textes disponibles dans JuriThèque sur ce domaine.',
    intro_ar:        'يُنظَّم تحصيل الديون العمومية بالمغرب بموجب القانون رقم 15-97 المتعلق بمدونة تحصيل الديون العمومية. يُحدد هذا النص المساطر الودية والإكراهية التي تتخذها الخزينة العامة للمملكة لتحصيل الضرائب والرسوم وسائر ديون الدولة. تجمع هذه الصفحة النصوص المتاحة في JuriThèque في هذا المجال.',
    legalDomain:     'administratif',
    keywords:        ['recouvrement créances publiques', 'code recouvrement', 'TGR', 'avis tiers détenteur', 'commandement', 'saisie administrative', 'opposition', 'recours gracieux', 'impôt', 'taxe'],
    keywords_ar:     ['تحصيل الديون العمومية', 'مدونة التحصيل', 'الخزينة العامة', 'الإشعار للغير الحائز', 'الأمر بالأداء', 'الحجز الإداري', 'التظلم', 'الطعن الإداري', 'الضريبة', 'الرسم'],
    searchTerms:     ['recouvrement créances publiques maroc', 'TGR maroc', 'code recouvrement'],
    relatedSlugs:    ['marches-publics-maroc', 'depenses-personnel-maroc'],
    faq: [
      {
        question: 'Quel est le texte de base du recouvrement des créances publiques au Maroc ?',
        answer:   'La Loi n°15-97 formant Code de Recouvrement des Créances Publiques est le texte fondamental. Elle est disponible dans JuriThèque.',
      },
      {
        question: 'Qu\'est-ce que l\'avis à tiers détenteur (ATD) au Maroc ?',
        answer:   'L\'ATD est une procédure permettant au comptable public de saisir entre les mains d\'un tiers (banque, employeur) les sommes dues à un contribuable redevable. Ses conditions sont définies dans le Code de Recouvrement. Consultez les textes dans JuriThèque.',
      },
      {
        question: 'Comment contester une procédure de recouvrement forcé au Maroc ?',
        answer:   'Le redevable peut exercer un recours gracieux auprès du comptable, puis un recours contentieux devant le tribunal administratif. Les délais et conditions sont définis dans le Code de Recouvrement. Consultez les textes disponibles dans JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو النص الأساسي لتحصيل الديون العمومية بالمغرب؟',
        answer:   'القانون رقم 15-97 المتعلق بمدونة تحصيل الديون العمومية هو النص الأساسي. وهو متاح في JuriThèque.',
      },
      {
        question: 'ما هو الإشعار للغير الحائز بالمغرب؟',
        answer:   'الإشعار للغير الحائز مسطرة تُمكِّن المحاسب العمومي من الحجز لدى طرف ثالث (بنك أو مشغِّل) على المبالغ المستحقة لملزم مدين. تُحدد شروطه مدونة التحصيل. راجع النصوص في JuriThèque.',
      },
      {
        question: 'كيف يمكن الطعن في مسطرة التحصيل الإكراهي بالمغرب؟',
        answer:   'يحق للملزم تقديم تظلم إداري لدى المحاسب ثم طعن قضائي أمام المحكمة الإدارية. تُحدد الآجال والشروط في مدونة التحصيل. راجع النصوص المتاحة في JuriThèque.',
      },
    ],
  },

  // ── Droit & Société ────────────────────────────────────────────────
  {
    lastUpdated:     '2026-06',
    slug:            'droit-sport-football-maroc',
    category:        'societe',
    title:           'Droit du Sport et Football au Maroc : textes juridiques 2026',
    title_ar:        'قانون الرياضة وكرة القدم بالمغرب : النصوص القانونية 2026',
    metaDescription: 'Consultez les textes juridiques sur le droit du sport au Maroc : loi sur l\'éducation physique et le sport, statuts FRMF, contrats joueurs, droits TV.',
    metaDescription_ar: 'اطلع على النصوص القانونية لقانون الرياضة بالمغرب : قانون التربية البدنية والرياضة، نظام الجامعة الملكية المغربية لكرة القدم، عقود اللاعبين.',
    h1:              'Droit du Sport et Football au Maroc',
    h1_ar:           'قانون الرياضة وكرة القدم بالمغرب',
    intro:           'Le droit du sport au Maroc est principalement régi par la Loi n°30-09 relative à l\'éducation physique et au sport. Ce texte encadre les associations sportives, les fédérations, les licences, les contrats des sportifs professionnels et la gouvernance du secteur. Cette page regroupe les textes disponibles dans JuriThèque sur ce domaine.',
    intro_ar:        'يُنظَّم قانون الرياضة بالمغرب أساساً بموجب القانون رقم 30-09 المتعلق بالتربية البدنية والرياضة. يُؤطر هذا النص الجمعيات الرياضية والجامعات والرخص وعقود الرياضيين المحترفين وحوكمة القطاع. تجمع هذه الصفحة النصوص المتاحة في JuriThèque في هذا المجال.',
    legalDomain:     'civil',
    keywords:        ['droit du sport', 'football maroc', 'loi 30-09', 'FRMF', 'contrat joueur', 'licence sportive', 'association sportive', 'droits TV', 'agent sportif'],
    keywords_ar:     ['قانون الرياضة', 'كرة القدم المغرب', 'القانون 30-09', 'الجامعة الملكية لكرة القدم', 'عقد اللاعب', 'الرخصة الرياضية', 'الجمعية الرياضية', 'حقوق البث', 'الوكيل الرياضي'],
    searchTerms:     ['droit sport maroc', 'football maroc loi', 'FRMF réglementation'],
    relatedSlugs:    ['droit-numerique-ia-maroc', 'code-du-travail-maroc'],
    faq: [
      {
        question: 'Quelle est la loi principale sur le sport au Maroc ?',
        answer:   'La Loi n°30-09 relative à l\'éducation physique et au sport est le texte fondamental. Elle est disponible dans JuriThèque.',
      },
      {
        question: 'Un joueur de football marocain peut-il signer un contrat professionnel ?',
        answer:   'Oui. Le contrat du sportif professionnel est encadré par la Loi 30-09 et les règlements de la FRMF. Les dispositions du Code du Travail s\'appliquent également. Consultez les textes dans JuriThèque.',
      },
      {
        question: 'Comment créer une association sportive au Maroc ?',
        answer:   'La création d\'une association sportive suit les règles de la loi sur les associations et les dispositions spécifiques de la Loi 30-09. Consultez les textes disponibles dans JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو القانون الرئيسي للرياضة بالمغرب؟',
        answer:   'القانون رقم 30-09 المتعلق بالتربية البدنية والرياضة هو النص الأساسي. وهو متاح في JuriThèque.',
      },
      {
        question: 'هل يمكن للاعب كرة قدم مغربي إبرام عقد احترافي؟',
        answer:   'نعم. يُنظم عقد الرياضي المحترف القانونُ 30-09 وأنظمة الجامعة الملكية المغربية لكرة القدم. كما تُطبق أحكام مدونة الشغل. راجع النصوص في JuriThèque.',
      },
      {
        question: 'كيف تُؤسس جمعية رياضية بالمغرب؟',
        answer:   'يخضع تأسيس الجمعية الرياضية لقانون الجمعيات والأحكام الخاصة بالقانون 30-09. راجع النصوص المتاحة في JuriThèque.',
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'droit-numerique-ia-maroc',
    category:        'societe',
    title:           'Droit Numérique et Intelligence Artificielle au Maroc : textes 2026',
    title_ar:        'القانون الرقمي والذكاء الاصطناعي بالمغرب : النصوص 2026',
    metaDescription: 'Consultez les textes juridiques sur le droit numérique au Maroc : loi 09-08 protection données, e-commerce, signature électronique, cybercriminalité.',
    metaDescription_ar: 'اطلع على النصوص القانونية للقانون الرقمي بالمغرب : القانون 09-08 حماية البيانات، التجارة الإلكترونية، التوقيع الإلكتروني، الجريمة المعلوماتية.',
    h1:              'Droit Numérique et Intelligence Artificielle au Maroc',
    h1_ar:           'القانون الرقمي والذكاء الاصطناعي بالمغرب',
    intro:           'Le droit numérique marocain repose sur plusieurs textes : la Loi n°09-08 relative à la protection des données personnelles, la Loi n°53-05 sur les échanges électroniques, et les dispositions pénales sur la cybercriminalité. L\'IA reste un domaine émergent sans cadre légal dédié, mais plusieurs textes existants s\'appliquent. Cette page regroupe les textes disponibles dans JuriThèque sur ce domaine.',
    intro_ar:        'يرتكز القانون الرقمي المغربي على نصوص عدة: القانون رقم 09-08 المتعلق بحماية الأشخاص الذاتيين تجاه معالجة المعطيات الشخصية، والقانون رقم 53-05 المتعلق بالتبادل الإلكتروني للمعطيات، والأحكام الجنائية المتعلقة بالجرائم المعلوماتية. تجمع هذه الصفحة النصوص المتاحة في JuriThèque في هذا المجال.',
    legalDomain:     'numerique',
    keywords:        ['droit numérique maroc', 'loi 09-08', 'protection données', 'CNDP', 'e-commerce', 'signature électronique', 'cybercriminalité', 'intelligence artificielle', 'loi 53-05'],
    keywords_ar:     ['القانون الرقمي المغرب', 'القانون 09-08', 'حماية البيانات', 'التجارة الإلكترونية', 'التوقيع الإلكتروني', 'الجريمة المعلوماتية', 'الذكاء الاصطناعي', 'القانون 53-05'],
    searchTerms:     ['droit numérique maroc', 'protection données maroc', 'e-commerce maroc loi'],
    relatedSlugs:    ['protection-donnees-personnelles-maroc', 'ecommerce-maroc', 'droit-influenceurs-maroc', 'protection-consommateur-maroc'],
    faq: [
      {
        question: 'Quelle est la loi sur la protection des données personnelles au Maroc ?',
        answer:   'La Loi n°09-08 relative à la protection des personnes physiques à l\'égard du traitement des données à caractère personnel est le texte fondamental, administré par la CNDP. Ce texte est disponible dans JuriThèque.',
      },
      {
        question: 'L\'e-commerce est-il encadré légalement au Maroc ?',
        answer:   'Oui. La Loi n°53-05 sur les échanges électroniques de données juridiques encadre les contrats électroniques, la signature numérique et le commerce en ligne. Consultez les textes dans JuriThèque.',
      },
      {
        question: 'Existe-t-il une loi sur l\'intelligence artificielle au Maroc ?',
        answer:   'Il n\'existe pas encore de loi dédiée à l\'IA au Maroc en 2026. Cependant, les lois existantes (protection des données, responsabilité civile, droit du travail) s\'appliquent aux systèmes d\'IA. Consultez les textes disponibles dans JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو قانون حماية البيانات الشخصية بالمغرب؟',
        answer:   'القانون رقم 09-08 المتعلق بحماية الأشخاص الذاتيين تجاه معالجة المعطيات الشخصية هو النص الأساسي، وتُشرف عليه اللجنة الوطنية لمراقبة حماية المعطيات الشخصية (CNDP). هذا النص متاح في JuriThèque.',
      },
      {
        question: 'هل التجارة الإلكترونية منظمة قانوناً بالمغرب؟',
        answer:   'نعم. ينظم القانون رقم 53-05 المتعلق بالتبادل الإلكتروني للمعطيات القانونية العقودَ الإلكترونية والتوقيع الرقمي والتجارة الإلكترونية. راجع النصوص في JuriThèque.',
      },
      {
        question: 'هل يوجد قانون خاص بالذكاء الاصطناعي بالمغرب؟',
        answer:   'لا يوجد حتى الآن قانون مخصص للذكاء الاصطناعي بالمغرب في 2026. غير أن القوانين القائمة (حماية البيانات، المسؤولية المدنية، مدونة الشغل) تُطبَّق على أنظمة الذكاء الاصطناعي. راجع النصوص المتاحة في JuriThèque.',
      },
    ],
    sections: [
      {
        h2:      'Protection des données personnelles : la loi 09-08 et la CNDP',
        content: [
          'La Loi n°09-08 relative à la protection des personnes physiques à l\'égard du traitement des données à caractère personnel, promulguée par le Dahir n°1-09-15 du 18 février 2009, constitue le texte central du droit numérique marocain. Elle s\'inspire largement de la directive européenne 95/46/CE et crée la Commission Nationale de contrôle de la protection des Données à caractère Personnel (CNDP).',
          'Toute entreprise ou personne qui collecte, traite ou conserve des données personnelles au Maroc est soumise à la loi 09-08, sous peine de sanctions administratives et pénales. Les obligations incluent la déclaration des traitements auprès de la CNDP, l\'information des personnes concernées et le respect du droit d\'accès et de rectification.',
        ],
        bullets: [
          'Déclaration préalable obligatoire auprès de la CNDP pour tout traitement de données',
          'Droit d\'accès, de rectification et d\'opposition reconnus à tout citoyen',
          'Sanctions : 10 000 à 300 000 DH d\'amende + emprisonnement en cas de récidive',
          'Données sensibles (santé, origine, religion) : protection renforcée',
          'Transferts internationaux de données : encadrés et soumis à autorisation',
          'CNDP : autorité de contrôle indépendante créée par la loi 09-08',
        ],
      },
      {
        h2:      'E-commerce et signature électronique : la loi 53-05',
        content: [
          'La Loi n°53-05 relative à l\'échange électronique de données juridiques (promulguée en 2007) encadre les contrats conclus par voie électronique, la valeur probatoire des échanges numériques et la signature électronique. Elle donne au contrat électronique la même valeur juridique qu\'un contrat écrit traditionnel.',
          'La signature électronique sécurisée a la même valeur juridique que la signature manuscrite, sous réserve d\'être créée par un prestataire certifié par l\'Agence Nationale de Réglementation des Télécommunications (ANRT). Le cadre juridique favorise le développement du commerce en ligne et des services administratifs dématérialisés.',
        ],
        bullets: [
          'Loi 53-05 : validité juridique des contrats électroniques',
          'Signature électronique certifiée : même valeur que la signature manuscrite',
          'Conservation des échanges électroniques : durée minimale de 10 ans',
          'Obligations d\'information précontractuelle pour les vendeurs en ligne',
          'Droit de rétractation applicable aux achats en ligne (via loi 31-08)',
          'ANRT : organisme de certification des prestataires de signature électronique',
        ],
      },
      {
        h2:      'Cybercriminalité et IA : le cadre pénal applicable au Maroc',
        content: [
          'Le Code Pénal marocain (Dahir n°1-59-413 modifié par la loi 07-03) contient les dispositions relatives aux infractions commises par voie électronique : accès non autorisé aux systèmes informatiques, atteinte à la vie privée, diffusion de contenus illicites et usurpation d\'identité numérique.',
          'En l\'absence d\'une loi dédiée à l\'intelligence artificielle, les systèmes d\'IA au Maroc sont soumis aux règles générales : responsabilité civile du Code des Obligations et Contrats (DOC), droit du travail pour l\'automatisation, et loi 09-08 pour les traitements de données. Le Maroc observe les évolutions internationales, notamment l\'AI Act européen, pour préparer sa propre réglementation.',
        ],
        bullets: [
          'Loi 07-03 : infractions relatives aux systèmes informatiques et réseaux',
          'Usurpation d\'identité numérique : punie par le Code Pénal',
          'Diffusion de fausses nouvelles : sanctions pénales applicables',
          'IA et responsabilité : DOC (art. 77-78) sur la responsabilité délictuelle',
          'IA et emploi : Code du Travail applicable aux changements technologiques',
          'Stratégie Maroc Digital 2030 : feuille de route numérique nationale',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'حماية البيانات الشخصية: القانون 09-08 واللجنة الوطنية',
        content: [
          'يُشكِّل القانون رقم 09-08 المتعلق بحماية الأشخاص الذاتيين تجاه معالجة المعطيات ذات الطابع الشخصي، الصادر بتنفيذه الظهير رقم 1-09-15 بتاريخ 18 فبراير 2009، النصَّ المحوري للقانون الرقمي المغربي. وقد أُنشئت بموجبه اللجنة الوطنية لمراقبة حماية المعطيات الشخصية (CNDP).',
          'تخضع لأحكام هذا القانون كل مؤسسة أو شخص يجمع بيانات شخصية أو يعالجها أو يحتفظ بها داخل المغرب، وتترتب على مخالفته عقوبات إدارية وجنائية. وتشمل الالتزامات التصريحَ للجنة الوطنية وإعلامَ الأشخاص المعنيين وضمانَ حقهم في الاطلاع والتصحيح.',
        ],
        bullets: [
          'التصريح المسبق الإلزامي للجنة الوطنية لكل عملية معالجة للبيانات',
          'حق الاطلاع والتصحيح والاعتراض مكفول لكل مواطن',
          'العقوبات: من 10.000 إلى 300.000 درهم غرامة مع السجن في حالة التكرار',
          'البيانات الحساسة (الصحة والأصل والدين): حماية مشددة',
          'النقل الدولي للبيانات: مقيَّد وخاضع للترخيص',
          'اللجنة الوطنية: هيئة رقابة مستقلة أُنشئت بموجب القانون 09-08',
        ],
      },
      {
        h2:      'التجارة الإلكترونية والتوقيع الإلكتروني: القانون 53-05',
        content: [
          'يُؤطر القانون رقم 53-05 المتعلق بالتبادل الإلكتروني للمعطيات القانونية (الصادر عام 2007) العقودَ المُبرَمة بالطريق الإلكتروني وحجيةَ التبادلات الرقمية والتوقيعَ الإلكتروني. ويُعطي العقدَ الإلكتروني ذات القيمة القانونية للعقد المكتوب التقليدي.',
          'يتمتع التوقيع الإلكتروني الآمن بنفس القيمة القانونية للتوقيع بخط اليد، شريطة أن يكون صادراً عن مُقدِّم خدمة معتمَد لدى الوكالة الوطنية لتقنين المواصلات (ANRT). يُشجِّع الإطار القانوني تطوير التجارة الإلكترونية والخدمات الإدارية الرقمية.',
        ],
        bullets: [
          'القانون 53-05: صحة العقود الإلكترونية قانونياً',
          'التوقيع الإلكتروني المعتمَد: له ذات قوة التوقيع بخط اليد',
          'حفظ التبادلات الإلكترونية: لمدة لا تقل عن 10 سنوات',
          'الالتزامات المعلوماتية ما قبل التعاقد للبائعين عبر الإنترنت',
          'حق الرجوع قابل للتطبيق على المشتريات عبر الإنترنت (بموجب القانون 31-08)',
          'ANRT: هيئة اعتماد مُقدِّمي خدمات التوقيع الإلكتروني',
        ],
      },
      {
        h2:      'الجريمة المعلوماتية والذكاء الاصطناعي: الإطار الجنائي المطبَّق بالمغرب',
        content: [
          'يتضمن مجموعة القانون الجنائي المغربي (الظهير رقم 1-59-413 المعدَّل بالقانون 07-03) الأحكامَ المتعلقة بالجرائم المرتكبة بالطريق الإلكتروني: الولوج غير المشروع إلى الأنظمة المعلوماتية وانتهاك الخصوصية ونشر المحتويات غير المشروعة وانتحال الهوية الرقمية.',
          'في غياب قانون خاص بالذكاء الاصطناعي، تخضع أنظمته في المغرب للقواعد العامة: المسؤولية المدنية وفق قانون الالتزامات والعقود (الفصل 77-78)، ومدونة الشغل في ما يخص الأتمتة، والقانون 09-08 لمعالجة البيانات.',
        ],
        bullets: [
          'القانون 07-03: الجرائم المتعلقة بالأنظمة المعلوماتية والشبكات',
          'انتحال الهوية الرقمية: مُجرَّم بموجب مجموعة القانون الجنائي',
          'ترويج الأخبار الزائفة: عقوبات جنائية واجبة التطبيق',
          'الذكاء الاصطناعي والمسؤولية: قانون الالتزامات والعقود (الفصلان 77-78) في المسؤولية التقصيرية',
          'الذكاء الاصطناعي والتشغيل: مدونة الشغل المطبَّقة على التحولات التكنولوجية',
          'استراتيجية المغرب الرقمي 2030: خارطة الطريق الوطنية للتحول الرقمي',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'droit-influenceurs-maroc',
    category:        'societe',
    title:           'Influenceurs et Droit Marocain : réglementation et obligations 2026',
    title_ar:        'المؤثرون والقانون المغربي : التنظيم والالتزامات 2026',
    metaDescription: 'Consultez les textes sur la réglementation des influenceurs au Maroc : publicité, contrats, droits d\'auteur, fiscalité, protection du consommateur.',
    metaDescription_ar: 'اطلع على النصوص المنظمة لعمل المؤثرين بالمغرب : الإشهار، العقود، حقوق المؤلف، الجبايات، حماية المستهلك.',
    h1:              'Influenceurs et Droit Marocain',
    h1_ar:           'المؤثرون والقانون المغربي',
    intro:           'Le statut juridique des influenceurs au Maroc est encadré par plusieurs textes transversaux : le Code de Commerce pour les contrats commerciaux, le Code Général des Impôts pour la fiscalité, la loi sur la protection du consommateur et les dispositions sur les droits d\'auteur. Aucune loi spécifique aux influenceurs n\'existe encore au Maroc. Cette page regroupe les textes disponibles dans JuriThèque sur ce domaine.',
    intro_ar:        'يُنظَّم الوضع القانوني للمؤثرين بالمغرب من خلال نصوص متعددة: مدونة التجارة للعقود التجارية، والمدونة العامة للضرائب، وقانون حماية المستهلك وأحكام حقوق المؤلف. لا يوجد حتى الآن قانون خاص بالمؤثرين بالمغرب. تجمع هذه الصفحة النصوص المتاحة في JuriThèque في هذا المجال.',
    legalDomain:     'numerique',
    keywords:        ['influenceurs maroc', 'marketing d\'influence', 'publicité mensongère', 'droits d\'auteur maroc', 'fiscalité influenceur', 'contrat influenceur', 'réseaux sociaux droit'],
    keywords_ar:     ['المؤثرون المغرب', 'التسويق بالمؤثرين', 'الإشهار المضلل', 'حقوق المؤلف المغرب', 'ضريبة المؤثرين', 'عقد المؤثر', 'قانون التواصل الاجتماعي'],
    searchTerms:     ['influenceurs maroc droit', 'réglementation influenceur maroc', 'fiscalité influenceur maroc'],
    relatedSlugs:    ['droit-numerique-ia-maroc', 'protection-consommateur-maroc'],
    faq: [
      {
        question: 'Les influenceurs marocains doivent-ils payer des impôts sur leurs revenus ?',
        answer:   'Oui. Les revenus des influenceurs sont imposables au Maroc selon le Code Général des Impôts, que ce soit au titre des bénéfices professionnels ou des revenus non commerciaux. Consultez les textes disponibles dans JuriThèque.',
      },
      {
        question: 'Un influenceur peut-il faire de la publicité sans mention obligatoire ?',
        answer:   'Non. La loi sur la protection du consommateur et les règles de la publicité imposent d\'identifier clairement les contenus sponsorisés. L\'omission peut constituer une pratique commerciale trompeuse. Consultez les textes dans JuriThèque.',
      },
      {
        question: 'Qui détient les droits sur les contenus créés par un influenceur au Maroc ?',
        answer:   'L\'influenceur est l\'auteur de ses créations. Les droits patrimoniaux peuvent être cédés par contrat. La loi marocaine sur la propriété intellectuelle (Loi 2-00) protège ces créations. Consultez les textes dans JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'هل يجب على المؤثرين المغاربة أداء الضرائب على مداخيلهم؟',
        answer:   'نعم. تخضع مداخيل المؤثرين للضريبة بالمغرب وفق المدونة العامة للضرائب، سواء في إطار الأرباح المهنية أو المداخيل غير التجارية. راجع النصوص المتاحة في JuriThèque.',
      },
      {
        question: 'هل يمكن للمؤثر نشر إعلان دون الإشارة إلى أنه ممول؟',
        answer:   'لا. يُلزم قانون حماية المستهلك وقواعد الإشهار بالتعريف الصريح بالمحتوى الممول. قد يشكل الإغفال ممارسة تجارية تضليلية. راجع النصوص في JuriThèque.',
      },
      {
        question: 'من يملك حقوق المحتوى الذي ينتجه المؤثر بالمغرب؟',
        answer:   'المؤثر هو مؤلف إبداعاته. يمكن التنازل عن الحقوق المالية بموجب عقد. يحمي قانون الملكية الفكرية المغربي (القانون 2-00) هذه الإبداعات. راجع النصوص في JuriThèque.',
      },
    ],
    sections: [
      {
        h2:      'Statut fiscal et déclaration des revenus des influenceurs au Maroc',
        content: [
          'Les influenceurs marocains qui tirent des revenus de leurs activités (partenariats, publicités, dons, monétisation de plateformes) sont soumis à l\'impôt sur le revenu (IR) au titre des bénéfices professionnels ou des revenus non commerciaux selon le Code Général des Impôts (CGI).',
          'Depuis 2023, la Direction Générale des Impôts (DGI) a renforcé les contrôles sur les revenus digitaux. Les influenceurs doivent déclarer leurs revenus, s\'immatriculer à la TVA au-delà d\'un certain seuil (500 000 DH HT/an), et peuvent opter pour le régime auto-entrepreneur.',
        ],
        bullets: [
          'IR sur bénéfices professionnels : taux progressif de 0% à 38%',
          'Auto-entrepreneur : régime simplifié avec impôt libératoire (1% ou 2%)',
          'TVA : obligatoire au-delà de 500 000 DH HT de chiffre d\'affaires annuel',
          'Revenus de plateformes étrangères (YouTube, TikTok, Meta) : imposables au Maroc',
          'Déclaration annuelle des revenus : avant le 31 mars de l\'année suivante',
          'Contrats de partenariat : à déclarer comme produits professionnels',
        ],
      },
      {
        h2:      'Obligations juridiques en matière de publicité et de contenu',
        content: [
          'La Loi n°31-08 sur la protection du consommateur et le Code de Commerce imposent des obligations strictes aux influenceurs qui font de la publicité : identification claire du contenu sponsorisé, interdiction de la publicité trompeuse ou mensongère, et respect des règles sectorielles (santé, finance, immobilier).',
          'L\'absence de mention claire qu\'un contenu est rémunéré constitue une pratique commerciale trompeuse au sens de la loi 31-08, passible de sanctions pénales et civiles. Cette obligation s\'applique quel que soit le réseau social utilisé.',
        ],
        bullets: [
          'Mention "partenariat" ou "publicité" obligatoire sur tout contenu sponsorisé',
          'Publicité trompeuse : amende de 10 000 à 500 000 DH + emprisonnement',
          'Interdiction de publicité non encadrée pour médicaments et produits de santé',
          'Publicité financière : soumise à la réglementation AMMC pour les instruments financiers',
          'Droits des consommateurs : droit à l\'information et protection contre les pratiques déloyales',
          'Responsabilité contractuelle vis-à-vis des marques partenaires',
        ],
      },
      {
        h2:      'Droits d\'auteur et propriété intellectuelle des créateurs de contenu',
        content: [
          'Les créations des influenceurs (vidéos, photos, textes, musiques, graphiques) sont protégées par la Loi n°2-00 relative aux droits d\'auteur et droits voisins. L\'influenceur est l\'auteur de ses œuvres dès leur création, sans formalité préalable.',
          'Les droits patrimoniaux (reproduction, diffusion, adaptation) peuvent être cédés à des tiers par contrat écrit. Les droits moraux (paternité, intégrité de l\'œuvre) sont inaliénables. En cas de litige, le Bureau Marocain du Droit d\'Auteur (BMDA) peut intervenir.',
        ],
        bullets: [
          'Protection automatique dès la création : aucune formalité requise',
          'Durée de protection : vie de l\'auteur + 70 ans pour les héritiers',
          'Cession de droits : obligatoirement par écrit avec mention des droits cédés',
          'Droit moral : inaliénable (droit à la paternité, intégrité, divulgation)',
          'BMDA : organisme de gestion collective des droits d\'auteur au Maroc',
          'Utilisation par les marques : accord préalable de l\'influenceur requis',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'الوضع الجبائي وتصريح المؤثرين بمداخيلهم في المغرب',
        content: [
          'يخضع المؤثرون المغاربة الذين يجنون دخلاً من نشاطهم (شراكات وإعلانات ومنح ورسوم منصات) لضريبة الدخل في إطار الأرباح المهنية أو المداخيل غير التجارية وفق المدونة العامة للضرائب.',
          'منذ عام 2023، عزَّزت المديرية العامة للضرائب رقابتها على المداخيل الرقمية. يجب على المؤثرين التصريح بمداخيلهم والتسجيل في الضريبة على القيمة المضافة بعد تجاوز سقف معين (500.000 درهم سنوياً خارج الضريبة)، مع إمكانية الاستفادة من نظام المقاول الذاتي.',
        ],
        bullets: [
          'ضريبة الدخل على الأرباح المهنية: سلم تصاعدي من 0% إلى 38%',
          'المقاول الذاتي: نظام مبسَّط بضريبة جزافية (1% أو 2%)',
          'الضريبة على القيمة المضافة: إلزامية عند تجاوز 500.000 درهم سنوياً',
          'مداخيل المنصات الأجنبية (يوتيوب، تيك توك، ميتا): خاضعة للضريبة في المغرب',
          'التصريح السنوي بالدخل: قبل 31 مارس من السنة الموالية',
          'عقود الشراكة: تُصرَّح بها ضمن الإيرادات المهنية',
        ],
      },
      {
        h2:      'الالتزامات القانونية في مجال الإشهار والمحتوى',
        content: [
          'يُلزم القانون رقم 31-08 لحماية المستهلك ومدونة التجارة المؤثرينَ الذين يُروِّجون للإعلانات بقواعد صارمة: التعريف الصريح بالمحتوى الممول، وحظر الإشهار المضلل أو الكاذب، واحترام الضوابط القطاعية (الصحة، والمال، والعقار).',
          'يُشكِّل غياب الإشارة الواضحة إلى أن المحتوى مدفوع الأجر ممارسةً تجارية تضليلية بمفهوم القانون 31-08، وتترتب عليها عقوبات جنائية ومدنية، بصرف النظر عن الشبكة الاجتماعية المستخدَمة.',
        ],
        bullets: [
          'إشارة "شراكة" أو "إشهار" إلزامية في كل محتوى ممول',
          'الإشهار المضلل: غرامة من 10.000 إلى 500.000 درهم مع السجن',
          'حظر الإشهار غير المنضبط للأدوية والمنتجات الصحية',
          'الإشهار المالي: خاضع لتنظيم هيئة مراقبة سوق الرساميل (AMMC) للأدوات المالية',
          'حقوق المستهلكين: الحق في الإعلام والحماية من الممارسات غير المشروعة',
          'المسؤولية التعاقدية تجاه العلامات التجارية الشريكة',
        ],
      },
      {
        h2:      'حقوق المؤلف والملكية الفكرية لصنّاع المحتوى',
        content: [
          'تحظى إبداعات المؤثرين (مقاطع الفيديو والصور والنصوص والموسيقى والرسومات) بحماية القانون رقم 2-00 المتعلق بحقوق المؤلف والحقوق المجاورة. يُعدُّ المؤثر مؤلفاً لإبداعاته منذ إنجازها، دون الحاجة إلى أي إجراء مسبق.',
          'يمكن التنازل عن الحقوق المالية (النسخ والنشر والتعديل) لأطراف ثالثة بعقد كتابي. أما الحقوق المعنوية (الأبوة الفكرية وسلامة المصنَّف) فغير قابلة للتنازل. وفي حالة النزاع، يمكن التدخل عبر المكتب المغربي لحقوق المؤلف (BMDA).',
        ],
        bullets: [
          'الحماية تلقائية منذ الإنشاء: دون الحاجة إلى إجراء مسبق',
          'مدة الحماية: طول حياة المؤلف + 70 سنة لورثته',
          'التنازل عن الحقوق: كتابياً حصراً مع ذكر الحقوق المتنازَل عنها',
          'الحق المعنوي: غير قابل للتنازل (حق الأبوة الفكرية، السلامة، الإفصاح)',
          'BMDA: هيئة الإدارة الجماعية لحقوق المؤلف في المغرب',
          'الاستخدام من قِبَل العلامات التجارية: يستلزم الموافقة المسبقة للمؤثر',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'code-route-maroc',
    category:        'societe',
    title:           'Code de la Route au Maroc : textes et infractions 2026',
    title_ar:        'قانون السير بالمغرب : النصوص والمخالفات 2026',
    metaDescription: 'Consultez les textes sur le code de la route au Maroc : loi 52-05, infractions, permis de conduire, assurance, accidents, vitesse.',
    metaDescription_ar: 'اطلع على النصوص المتعلقة بقانون السير بالمغرب : القانون 52-05، المخالفات، رخصة السياقة، التأمين، الحوادث، السرعة.',
    h1:              'Code de la Route au Maroc',
    h1_ar:           'قانون السير بالمغرب',
    intro:           'Le Code de la Route marocain est régi par la Loi n°52-05 portant Code de la Route, complétée par de nombreux décrets d\'application. Ce texte encadre la circulation routière, les infractions, les sanctions, le permis de conduire à points et l\'assurance obligatoire. Cette page regroupe les textes disponibles dans JuriThèque sur ce domaine.',
    intro_ar:        'يُنظَّم قانون السير بالمغرب بموجب القانون رقم 52-05 المتعلق بمدونة السير على الطرق، المكمَّل بمراسيم تطبيقية عديدة. يُؤطر هذا النص حركة السير والمخالفات والعقوبات ورخصة السياقة بالنقط والتأمين الإجباري. تجمع هذه الصفحة النصوص المتاحة في JuriThèque في هذا المجال.',
    legalDomain:     'penal',
    keywords:        ['code de la route', 'loi 52-05', 'permis de conduire', 'infractions routières', 'retrait de permis', 'alcool au volant', 'assurance auto', 'accident de la route', 'vitesse'],
    keywords_ar:     ['قانون السير', 'القانون 52-05', 'رخصة السياقة', 'مخالفات الطريق', 'سحب الرخصة', 'السكر أثناء القيادة', 'التأمين على السيارة', 'حادثة المرور', 'السرعة'],
    searchTerms:     ['code route maroc', 'infraction routière maroc', 'permis conduire maroc'],
    relatedSlugs:    ['protection-consommateur-maroc', 'droit-numerique-ia-maroc'],
    faq: [
      {
        question: 'Quelle est la loi principale sur le code de la route au Maroc ?',
        answer:   'La Loi n°52-05 portant Code de la Route est le texte fondamental, promulguée par le Dahir n°1-10-07. Elle est disponible dans JuriThèque.',
      },
      {
        question: 'Comment fonctionne le permis à points au Maroc ?',
        answer:   'Le permis marocain est doté d\'un capital de 30 points. Des points sont retirés à chaque infraction. Arrivé à zéro, le permis est annulé. Les modalités sont définies dans la Loi 52-05. Consultez les textes dans JuriThèque.',
      },
      {
        question: 'Quelles sont les sanctions pour conduite en état d\'ivresse au Maroc ?',
        answer:   'La conduite sous l\'empire d\'un état alcoolique est une infraction grave punie d\'une amende et d\'un retrait de points, voire d\'une suspension de permis. Les seuils et sanctions sont définis dans la Loi 52-05. Consultez les textes dans JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو القانون الرئيسي لقانون السير بالمغرب؟',
        answer:   'القانون رقم 52-05 المتعلق بمدونة السير على الطرق هو النص الأساسي، الصادر بالظهير رقم 1-10-07. وهو متاح في JuriThèque.',
      },
      {
        question: 'كيف تعمل رخصة السياقة بالنقط بالمغرب؟',
        answer:   'تمتلك رخصة السياقة المغربية رصيداً من 30 نقطة. تُخصم نقاط عند ارتكاب كل مخالفة. عند بلوغ الصفر، تُلغى الرخصة. تُحدد الشروط في القانون 52-05. راجع النصوص في JuriThèque.',
      },
      {
        question: 'ما هي عقوبات القيادة في حالة سكر بالمغرب؟',
        answer:   'تُعد القيادة في حالة سكر مخالفة خطيرة تُعاقب بغرامة وخصم نقاط وقد تصل إلى إيقاف الرخصة. تُحدد العتبات والعقوبات في القانون 52-05. راجع النصوص في JuriThèque.',
      },
    ],
    sections: [
      {
        h2:      'La loi 52-05 : le Code de la Route marocain en vigueur',
        content: [
          'La Loi n°52-05 portant Code de la Route, promulguée par le Dahir n°1-10-07 du 26 safar 1431, constitue le cadre légal complet de la circulation routière au Maroc. Elle a abrogé l\'ancien dahir de 1953 et modernise en profondeur le droit de la route.',
          'Le Code marocain de la Route instaure un système de permis à points (30 points de départ), définit les règles de priorité et de vitesse, réglemente l\'assurance obligatoire, et alourdit significativement les sanctions pour les infractions graves (alcool, excès de vitesse, téléphone au volant).',
        ],
        bullets: [
          'Loi 52-05 : permis à points, infractions, sanctions, assurance obligatoire',
          'Décret n°2-10-421 : application du Code, catégories d\'infractions',
          'Permis à 30 points : retrait progressif selon la gravité des infractions',
          'Vitesse : 120 km/h sur autoroute, 100 km/h sur voie express, 60 km/h en agglomération',
          'Ceinture de sécurité et casque : obligatoires, sanction immédiate',
          'Téléphone au volant : infraction du 2ème degré, retrait de 4 points',
        ],
      },
      {
        h2:      'Les catégories d\'infractions et les sanctions applicables',
        content: [
          'La Loi 52-05 classe les infractions routières en 4 degrés selon leur gravité. Chaque degré correspond à une amende forfaitaire et à un retrait de points spécifique. Les infractions les plus graves peuvent entraîner la suspension ou l\'annulation du permis, voire des poursuites pénales.',
        ],
        bullets: [
          '1er degré : amende 300 DH, retrait 1 point (ex : stationnement gênant)',
          '2ème degré : amende 400 DH, retrait 2-4 points (ex : téléphone, non-respect feux)',
          '3ème degré : amende 700 DH, retrait 4-6 points (ex : excès de vitesse modéré)',
          '4ème degré : amende 1 300 DH, retrait 6+ points (ex : alcool, excès de vitesse grave)',
          'Conduite à 0,6 g/l ou plus : suspension de permis jusqu\'à 6 mois',
          'Homicide involontaire par imprudence : peines d\'emprisonnement (Code Pénal)',
        ],
      },
      {
        h2:      'L\'assurance automobile et les accidents de la route au Maroc',
        content: [
          'L\'assurance responsabilité civile automobile est obligatoire pour tout véhicule circulant au Maroc, conformément au Code des Assurances (Loi 17-99). Cette assurance couvre les dommages corporels et matériels causés à des tiers. En cas d\'accident mortel ou corporel grave, le Fonds de Garantie Automobile (FGA) peut indemniser les victimes dont l\'auteur est inconnu ou non assuré.',
          'La procédure d\'indemnisation après un accident suit un processus défini : constat amiable (ou procès-verbal de gendarmerie), déclaration à la compagnie d\'assurance dans les 5 jours, expertise du véhicule, et règlement amiable ou judiciaire.',
        ],
        bullets: [
          'Assurance RC obligatoire : amende de 2 000 à 5 000 DH en cas de défaut',
          'Constat amiable : document standardisé à remplir sur les lieux de l\'accident',
          'Déclaration de sinistre : dans les 5 jours ouvrables à la compagnie d\'assurance',
          'Fonds de Garantie Automobile (FGA) : indemnise les victimes d\'accidents sans assurance',
          'Convention IRSA : règlement accéléré des sinistres matériels entre compagnies',
          'Tribunal compétent : tribunal de première instance pour les litiges d\'indemnisation',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'القانون 52-05: مدونة السير المغربية المعمول بها',
        content: [
          'يُشكِّل القانون رقم 52-05 المتعلق بمدونة السير على الطرق، الصادر بتنفيذه الظهير رقم 1-10-07 بتاريخ 26 صفر 1431، الإطارَ القانوني الشامل لحركة المرور بالمغرب. وقد نسخ الظهير القديم الصادر عام 1953 وأحدث تحديثاً جذرياً لقانون السير.',
          'أرسى القانون المغربي لمدونة السير نظامَ رخصة السياقة بالنقط (30 نقطة ابتداءً)، وحدَّد قواعد الأولوية والسرعة، ونظَّم التأمين الإجباري، وشدَّد العقوبات على المخالفات الجسيمة (الكحول والسرعة المفرطة واستخدام الهاتف أثناء القيادة).',
        ],
        bullets: [
          'القانون 52-05: الرخصة بالنقط والمخالفات والعقوبات والتأمين الإجباري',
          'المرسوم 2-10-421: تطبيق المدونة وفئات المخالفات',
          'رخصة 30 نقطة: خصم تدريجي بحسب جسامة المخالفات',
          'السرعة: 120 كلم/س في الطريق السيار، و100 كلم/س في الطريق السريع، و60 كلم/س داخل المدن',
          'حزام الأمان والخوذة: إلزاميان وعقوبتهما فورية',
          'الهاتف أثناء القيادة: مخالفة من الدرجة الثانية، خصم 4 نقاط',
        ],
      },
      {
        h2:      'فئات المخالفات والعقوبات المطبَّقة',
        content: [
          'يُصنِّف القانون 52-05 المخالفات المرورية في 4 درجات بحسب خطورتها. ويقابل كل درجةٍ غرامةٌ جزافية وخصمٌ محدد من النقط. وقد تترتب على المخالفات الأشد خطورةً إيقافُ الرخصة أو إلغاؤها أو المتابعة الجنائية.',
        ],
        bullets: [
          'الدرجة الأولى: غرامة 300 درهم، خصم نقطة واحدة (مثال: توقف مزعج)',
          'الدرجة الثانية: غرامة 400 درهم، خصم 2-4 نقاط (مثال: الهاتف، عدم احترام الإشارة)',
          'الدرجة الثالثة: غرامة 700 درهم، خصم 4-6 نقاط (مثال: تجاوز بسيط للسرعة)',
          'الدرجة الرابعة: غرامة 1300 درهم، خصم 6 نقاط فأكثر (مثال: الكحول، تجاوز السرعة بشكل خطير)',
          'القيادة بنسبة 0,6 غ/ل فأكثر: إيقاف الرخصة لمدة تصل إلى 6 أشهر',
          'القتل الخطأ بالسيارة: عقوبات سجنية وفق مجموعة القانون الجنائي',
        ],
      },
      {
        h2:      'التأمين على السيارة وحوادث المرور بالمغرب',
        content: [
          'يُعدُّ تأمين المسؤولية المدنية عن السيارة إلزامياً لكل مركبة تسير في المغرب، وفق مدونة التأمينات (القانون 17-99). يُغطي هذا التأمين الأضرارَ الجسدية والمادية التي تلحق بالغير. وعند وقوع حوادث مميتة أو جسدية خطيرة، يتدخل صندوق ضمان حوادث السيارة لتعويض الضحايا الذين يكون مرتكب الحادثة مجهولاً أو غير مؤمَّن.',
          'تسير مسطرة التعويض عقب الحادثة وفق مراحل محددة: المحضر الودي (أو محضر الدرك)، والتصريح لشركة التأمين داخل 5 أيام، وخبرة السيارة، والتسوية الودية أو القضائية.',
        ],
        bullets: [
          'التأمين الإلزامي للمسؤولية المدنية: غرامة من 2.000 إلى 5.000 درهم عند الإخلال',
          'المحضر الودي: وثيقة موحَّدة تُملأ في مكان الحادثة',
          'التصريح بالحادثة: داخل 5 أيام عمل لشركة التأمين',
          'صندوق ضمان حوادث السيارة: يُعوِّض ضحايا الحوادث دون تأمين',
          'اتفاقية IRSA: تسوية مسرَّعة للأضرار المادية بين شركات التأمين',
          'الجهة القضائية المختصة: المحكمة الابتدائية للنظر في نزاعات التعويض',
        ],
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'protection-consommateur-maroc',
    category:        'societe',
    title:           'Protection du Consommateur au Maroc : textes et droits 2026',
    title_ar:        'حماية المستهلك بالمغرب : النصوص والحقوق 2026',
    metaDescription: 'Consultez les textes sur la protection du consommateur au Maroc : loi 31-08, garanties, publicité trompeuse, clauses abusives, associations.',
    metaDescription_ar: 'اطلع على النصوص المتعلقة بحماية المستهلك بالمغرب : القانون 31-08، الضمانات، الإشهار المضلل، الشروط التعسفية، جمعيات المستهلكين.',
    h1:              'Protection du Consommateur au Maroc',
    h1_ar:           'حماية المستهلك بالمغرب',
    intro:           'La protection du consommateur au Maroc est régie par la Loi n°31-08 édictant des mesures de protection du consommateur. Ce texte encadre les pratiques commerciales, les clauses abusives, les garanties légales, le crédit à la consommation et les associations de défense des consommateurs. Cette page regroupe les textes disponibles dans JuriThèque sur ce domaine.',
    intro_ar:        'تُنظَّم حماية المستهلك بالمغرب بموجب القانون رقم 31-08 القاضي باتخاذ تدابير لحماية المستهلك. يُؤطر هذا النص الممارسات التجارية والشروط التعسفية والضمانات القانونية والائتمان الاستهلاكي وجمعيات الدفاع عن المستهلكين. تجمع هذه الصفحة النصوص المتاحة في JuriThèque في هذا المجال.',
    legalDomain:     'commercial',
    keywords:        ['protection consommateur', 'loi 31-08', 'clauses abusives', 'publicité trompeuse', 'garantie légale', 'crédit consommation', 'association consommateurs', 'droit de rétractation'],
    keywords_ar:     ['حماية المستهلك', 'القانون 31-08', 'الشروط التعسفية', 'الإشهار المضلل', 'الضمان القانوني', 'القرض الاستهلاكي', 'جمعيات المستهلكين', 'حق الرجوع'],
    searchTerms:     ['protection consommateur maroc', 'loi 31-08', 'droits consommateur maroc'],
    relatedSlugs:    ['droit-influenceurs-maroc', 'droit-numerique-ia-maroc'],
    faq: [
      {
        question: 'Quelle est la loi sur la protection du consommateur au Maroc ?',
        answer:   'La Loi n°31-08 édictant des mesures de protection du consommateur est le texte fondamental. Elle est disponible dans JuriThèque.',
      },
      {
        question: 'Qu\'est-ce qu\'une clause abusive dans un contrat au Maroc ?',
        answer:   'Une clause abusive est une clause qui crée un déséquilibre significatif entre les droits et obligations du professionnel et du consommateur. La Loi 31-08 en donne une liste indicative. Consultez les textes dans JuriThèque.',
      },
      {
        question: 'Le consommateur marocain a-t-il un droit de rétractation ?',
        answer:   'Oui. La Loi 31-08 prévoit un droit de rétractation pour certains contrats (vente à distance, démarchage à domicile). Les délais et conditions sont précisés dans le texte. Consultez les textes disponibles dans JuriThèque.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو قانون حماية المستهلك بالمغرب؟',
        answer:   'القانون رقم 31-08 القاضي باتخاذ تدابير لحماية المستهلك هو النص الأساسي. وهو متاح في JuriThèque.',
      },
      {
        question: 'ما هو الشرط التعسفي في العقود بالمغرب؟',
        answer:   'الشرط التعسفي هو كل شرط يُحدث اختلالاً جوهرياً في الحقوق والالتزامات بين المهني والمستهلك. يُدرج القانون 31-08 قائمة استرشادية بهذه الشروط. راجع النصوص في JuriThèque.',
      },
      {
        question: 'هل يتمتع المستهلك المغربي بحق الرجوع؟',
        answer:   'نعم. يُقرر القانون 31-08 حق الرجوع في بعض العقود (البيع عن بُعد، والتفاوض خارج المحلات التجارية). تُحدد الآجال والشروط في النص. راجع النصوص المتاحة في JuriThèque.',
      },
    ],
    sections: [
      {
        h2:      'La loi 31-08 : socle de la protection du consommateur au Maroc',
        content: [
          'La Loi n°31-08 édictant des mesures de protection du consommateur, promulguée par le Dahir n°1-11-03 du 18 février 2011, constitue le texte fondamental en matière de droits des consommateurs au Maroc. Elle s\'applique à toute transaction commerciale entre un professionnel et un consommateur, qu\'elle soit conclue en magasin, à distance ou à domicile.',
          'Ce texte couvre un périmètre très large : pratiques commerciales déloyales, clauses abusives dans les contrats, publicité trompeuse, crédit à la consommation, garanties légales, démarchage à domicile et vente à distance. Il crée également un cadre pour les associations de défense des consommateurs.',
        ],
        bullets: [
          'Loi 31-08 : pratiques déloyales, publicité, clauses abusives, garanties',
          'Champ d\'application : toute transaction entre professionnel et consommateur',
          'Associations de consommateurs agréées : droit d\'ester en justice collectivement',
          'Autorité de contrôle : Ministère du Commerce, Direction de la Concurrence',
          'Sanctions pénales : amendes de 2 000 à 500 000 DH selon la violation',
          'Prescription : 3 ans pour les actions en responsabilité contractuelle du consommateur',
        ],
      },
      {
        h2:      'Clauses abusives, publicité trompeuse et pratiques déloyales',
        content: [
          'La loi 31-08 définit et sanctionne plusieurs pratiques illicites : les clauses abusives (tout déséquilibre significatif entre droits et obligations du professionnel et du consommateur), la publicité trompeuse ou comparative illicite, et les pratiques commerciales agressives ou déloyales.',
          'Les clauses abusives sont réputées non écrites (nulles) même si elles figurent dans un contrat signé. La loi établit une liste indicative de clauses présumées abusives, notamment les clauses limitant ou excluant la garantie légale, imposant des frais excessifs en cas de résiliation, ou créant un déséquilibre manifeste dans la résolution des litiges.',
        ],
        bullets: [
          'Clause abusive : réputée non écrite, le reste du contrat demeure valable',
          'Publicité trompeuse : sur le prix, les caractéristiques, l\'origine du produit',
          'Ventes liées ou subordonnées : interdites sauf exceptions',
          'Pratiques agressives : sollicitations répétées ou contraintes sur le consommateur',
          'Droit à l\'information : prix TTC, caractéristiques essentielles, conditions de vente',
          'Garanties : garantie légale de conformité + garantie commerciale du vendeur',
        ],
      },
      {
        h2:      'Crédit à la consommation et droit de rétractation',
        content: [
          'La loi 31-08 encadre strictement le crédit à la consommation au Maroc : obligation d\'information précontractuelle, Taux Annuel Effectif Global (TAEG) obligatoire dans tout contrat de crédit, et droit de rétractation de 7 jours ouvrables pour les crédits à la consommation et les contrats conclus hors établissements (démarchage).',
          'Pour la vente à distance (e-commerce, vente par correspondance), le consommateur bénéficie d\'un droit de rétractation sans motif ni pénalité dans un délai défini par la loi. Le professionnel doit rembourser intégralement le consommateur dans les 30 jours suivant l\'exercice de ce droit.',
        ],
        bullets: [
          'Crédit conso : TAEG obligatoire + information précontractuelle complète',
          'Droit de rétractation crédit : 7 jours ouvrables à compter de la signature',
          'Vente à distance : droit de retour sans justification dans le délai légal',
          'Remboursement : dans les 30 jours suivant la rétractation',
          'Démarchage à domicile : réglementé, interdiction de conclure le jour même',
          'Usure : taux d\'intérêt maximum fixé par Bank Al-Maghrib (taux d\'usure)',
        ],
      },
    ],
    sections_ar: [
      {
        h2:      'القانون 31-08: ركيزة حماية المستهلك في المغرب',
        content: [
          'يُشكِّل القانون رقم 31-08 القاضي باتخاذ تدابير لحماية المستهلك، الصادر بتنفيذه الظهير رقم 1-11-03 بتاريخ 18 فبراير 2011، النصَّ الأساسي في مجال حقوق المستهلكين بالمغرب. ويسري على كل معاملة تجارية بين مهني ومستهلك، سواء أبرمت داخل المحل أو عن بُعد أو في المنزل.',
          'يُغطي هذا النص ميداناً واسعاً: الممارسات التجارية غير المشروعة والشروط التعسفية في العقود والإشهار المضلل والقرض الاستهلاكي والضمانات القانونية والبيع بالتفاوض خارج المحلات والبيع عن بُعد. كما يُرسي إطاراً لجمعيات الدفاع عن المستهلكين.',
        ],
        bullets: [
          'القانون 31-08: الممارسات غير المشروعة والإشهار والشروط التعسفية والضمانات',
          'نطاق التطبيق: كل معاملة بين مهني ومستهلك',
          'جمعيات المستهلكين المعتمَدة: حق التقاضي الجماعي',
          'جهة الرقابة: وزارة التجارة، مديرية المنافسة',
          'العقوبات الجنائية: غرامات من 2.000 إلى 500.000 درهم بحسب المخالفة',
          'التقادم: 3 سنوات للدعاوى في المسؤولية التعاقدية للمستهلك',
        ],
      },
      {
        h2:      'الشروط التعسفية والإشهار المضلل والممارسات غير المشروعة',
        content: [
          'يُحدِّد القانون 31-08 ويُعاقب على جملة من الممارسات غير المشروعة: الشروط التعسفية (كل اختلال جوهري بين حقوق المهني والمستهلك والتزاماتهما)، والإشهار المضلل أو المقارن غير المشروع، والممارسات التجارية العدوانية أو غير الأمينة.',
          'تُعدُّ الشروط التعسفية كأن لم تكن (لاغية) حتى وإن وردت في عقد موقَّع، في حين يظل بقية العقد نافذاً. ويُدرج القانون قائمة استرشادية بالشروط المفترضة تعسفيةً، ولا سيما تلك التي تُقيِّد الضمان القانوني أو تفرض رسوماً مفرطة عند الفسخ أو تُحدث خللاً صريحاً في تسوية النزاعات.',
        ],
        bullets: [
          'الشرط التعسفي: يُعدُّ كأن لم يكن، ويبقى العقد سارياً في بقية أجزائه',
          'الإشهار المضلل: في الثمن والخصائص وأصل المنتج',
          'البيع المقترن والمشروط: محظور إلا باستثناءات',
          'الممارسات العدوانية: المطالبة المتكررة أو الإكراه على المستهلك',
          'الحق في الإعلام: السعر شاملاً للضريبة والخصائص الجوهرية وشروط البيع',
          'الضمانات: ضمان المطابقة القانوني + الضمان التجاري للبائع',
        ],
      },
      {
        h2:      'القرض الاستهلاكي وحق الرجوع',
        content: [
          'يُؤطر القانون 31-08 تأطيراً صارماً القرضَ الاستهلاكي بالمغرب: وجوب الإعلام ما قبل التعاقد، وإلزامية إدراج النسبة السنوية الإجمالية للفائدة في كل عقد قرض، وحق الرجوع في غضون 7 أيام عمل بالنسبة للقروض الاستهلاكية والعقود المبرَمة خارج المحلات (التفاوض).',
          'في البيع عن بُعد (التجارة الإلكترونية والبيع بالمراسلة) يتمتع المستهلك بحق الرجوع دون تقديم مبرر أو دفع غرامة داخل الأجل القانوني. ويجب على المهني إرجاع المبلغ كاملاً للمستهلك في أجل لا يتجاوز 30 يوماً من ممارسة هذا الحق.',
        ],
        bullets: [
          'القرض الاستهلاكي: النسبة السنوية الإجمالية إلزامية مع إعلام ما قبل التعاقد',
          'حق الرجوع في القرض: 7 أيام عمل من تاريخ التوقيع',
          'البيع عن بُعد: حق الإرجاع بلا تبرير داخل الأجل القانوني',
          'الاسترداد: في غضون 30 يوماً من ممارسة حق الرجوع',
          'التفاوض في المنزل: مُنظَّم، ويُحظر إبرام العقد في نفس اليوم',
          'الفائدة التحريمية: حدها الأقصى يُحدده بنك المغرب',
        ],
      },
    ],
  },

  // ══════════════════════════════════════════════════════════════════════════
  // SPOKES — Marchés Publics
  // ══════════════════════════════════════════════════════════════════════════

  {
    lastUpdated:     '2026-06',
    slug:            'passation-marches-publics-maroc',
    category:        'administratif',
    title:           'Modes de Passation des Marchés Publics au Maroc 2026',
    title_ar:        'أساليب إبرام الصفقات العمومية بالمغرب 2026',
    metaDescription: 'Guide complet sur les modes de passation des marchés publics au Maroc : appel d\'offres ouvert/restreint, concours, bon de commande, marché négocié — Décret 2-22-431.',
    metaDescription_ar: 'دليل متكامل حول أساليب إبرام الصفقات العمومية بالمغرب: طلب العروض المفتوح والمحدود، المباراة، أمر بالشراء، الصفقة التفاوضية — المرسوم 2-22-431.',
    h1:              'Modes de Passation des Marchés Publics au Maroc',
    h1_ar:           'أساليب إبرام الصفقات العمومية بالمغرب',
    intro:           'Le Décret n°2-22-431 du 8 mars 2023 organise quatre modes de passation des marchés publics au Maroc : l\'appel d\'offres (ouvert ou restreint), le concours, le bon de commande et le marché négocié. Chaque mode obéit à des conditions d\'utilisation précises et à des procédures distinctes. Ce guide en présente les règles essentielles.',
    intro_ar:        'يُنظِّم المرسوم رقم 2-22-431 الصادر في 8 مارس 2023 أربعة أساليب لإبرام الصفقات العمومية بالمغرب: طلب العروض (المفتوح أو المحدود)، والمباراة، وأمر بالشراء، والصفقة التفاوضية. يخضع كل أسلوب لشروط استخدام دقيقة ومساطر مستقلة. يستعرض هذا الدليل أبرز أحكامها.',
    legalDomain:     'administratif',
    keywords:        ['modes passation marchés publics', 'appel d\'offres ouvert', 'appel d\'offres restreint', 'concours marché public', 'bon de commande', 'marché négocié', 'décret 2-22-431', 'soumissionnaire', 'cahier des charges'],
    keywords_ar:     ['أساليب إبرام الصفقات العمومية', 'طلب العروض المفتوح', 'طلب العروض المحدود', 'المباراة', 'أمر بالشراء', 'الصفقة التفاوضية', 'المرسوم 2-22-431', 'المتنافس', 'دفتر التحملات'],
    searchTerms:     ['modes passation marchés publics maroc', 'appel offres maroc', 'marché négocié maroc'],
    relatedSlugs:    ['marches-publics-maroc', 'execution-marche-public-maroc', 'controle-marches-publics-maroc'],
    faq: [
      {
        question: 'Quels sont les modes de passation des marchés publics au Maroc ?',
        answer:   'Le Décret 2-22-431 prévoit quatre modes : (1) l\'appel d\'offres ouvert (tout opérateur peut soumissionner), (2) l\'appel d\'offres restreint (candidats présélectionnés), (3) le concours (sélection sur programme ou esquisse), et (4) le marché négocié (cas limitatifs : urgence, secret défense, montant faible via bon de commande).',
      },
      {
        question: 'Quand peut-on recourir au marché négocié au Maroc ?',
        answer:   'Le recours au marché négocié est limité aux cas expressément prévus par le Décret 2-22-431 : travaux d\'urgence impérieuse, secret de la défense nationale, prestataire unique sur le marché, ou marchés dont le montant ne dépasse pas les seuils du bon de commande.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هي أساليب إبرام الصفقات العمومية بالمغرب؟',
        answer:   'يُقرر المرسوم 2-22-431 أربعة أساليب: (1) طلب العروض المفتوح لأي متعامل، (2) طلب العروض المحدود للمترشحين المنتقَين مسبقاً، (3) المباراة بالانتقاء على أساس برنامج أو تصميم مبدئي، (4) الصفقة التفاوضية في الحالات الاستثنائية كالاستعجال والأمن الوطني.',
      },
      {
        question: 'متى يجوز اللجوء إلى الصفقة التفاوضية بالمغرب؟',
        answer:   'يُقيِّد المرسوم 2-22-431 اللجوءَ إلى الصفقة التفاوضية بحالات محددة: الاستعجال الملح، سرية الدفاع الوطني، انفراد متعامل واحد بالسوق، أو الصفقات التي لا تتجاوز عتبات أمر بالشراء.',
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'execution-marche-public-maroc',
    category:        'administratif',
    title:           'Exécution des Marchés Publics au Maroc : obligations et réception 2026',
    title_ar:        'تنفيذ الصفقات العمومية بالمغرب : الالتزامات والاستلام 2026',
    metaDescription: 'Guide sur l\'exécution des marchés publics : ordre de service, délais, pénalités de retard, réception provisoire et définitive, révision des prix.',
    metaDescription_ar: 'دليل تنفيذ الصفقات العمومية: أمر الخدمة، الآجال، غرامات التأخير، الاستلام المؤقت والنهائي، مراجعة الأثمان.',
    h1:              'Exécution des Marchés Publics au Maroc',
    h1_ar:           'تنفيذ الصفقات العمومية بالمغرب',
    intro:           'Après attribution, le marché public entre en phase d\'exécution. Le titulaire doit respecter les délais, les spécifications techniques et les obligations administratives prévues dans le cahier des charges. Le Décret 2-22-431 encadre les ordres de service, les pénalités, les réceptions et les règlements des litiges.',
    intro_ar:        'بعد الإسناد، تدخل الصفقة العمومية مرحلة التنفيذ. يلتزم صاحب الصفقة باحترام الآجال والمواصفات التقنية والمتطلبات الإدارية المنصوص عليها في دفتر التحملات. يُؤطر المرسوم 2-22-431 أوامر الخدمة والغرامات والاستلام وتسوية النزاعات.',
    legalDomain:     'administratif',
    keywords:        ['exécution marché public', 'ordre de service', 'pénalités retard', 'réception provisoire', 'réception définitive', 'révision prix', 'sous-traitance marché'],
    keywords_ar:     ['تنفيذ الصفقة العمومية', 'أمر الخدمة', 'غرامات التأخير', 'الاستلام المؤقت', 'الاستلام النهائي', 'مراجعة الأثمان', 'المقاولة من الباطن'],
    searchTerms:     ['exécution marché public maroc', 'réception marché maroc', 'pénalités marché public'],
    relatedSlugs:    ['marches-publics-maroc', 'passation-marches-publics-maroc', 'controle-marches-publics-maroc'],
    faq: [
      {
        question: 'Que se passe-t-il en cas de retard dans l\'exécution d\'un marché public au Maroc ?',
        answer:   'Des pénalités de retard sont appliquées automatiquement selon un taux fixé dans le CPS. En cas de retard grave, le maître d\'ouvrage peut résilier le marché. Les modalités sont définies dans le Décret 2-22-431.',
      },
    ],
    faq_ar: [
      {
        question: 'ما الذي يحدث عند التأخر في تنفيذ صفقة عمومية بالمغرب؟',
        answer:   'تُطبَّق غرامات تأخير تلقائياً وفق النسبة المحددة في دفتر التحملات الخاصة. وعند التأخر الجسيم، يحق لصاحب المشروع فسخ الصفقة. تُحدد الشروط في المرسوم 2-22-431.',
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'controle-marches-publics-maroc',
    category:        'administratif',
    title:           'Contrôle et Contentieux des Marchés Publics au Maroc 2026',
    title_ar:        'مراقبة ونزاعات الصفقات العمومية بالمغرب 2026',
    metaDescription: 'Guide sur le contrôle des marchés publics au Maroc : TGR, Cour des comptes, recours gracieux et contentieux, commission des marchés.',
    metaDescription_ar: 'دليل مراقبة الصفقات العمومية بالمغرب: الخزينة العامة، المجلس الأعلى للحسابات، الطعن الودي والقضائي، لجنة الصفقات.',
    h1:              'Contrôle et Contentieux des Marchés Publics',
    h1_ar:           'مراقبة ونزاعات الصفقات العمومية بالمغرب',
    intro:           'Le système de contrôle des marchés publics au Maroc est organisé à plusieurs niveaux : contrôle a priori de la TGR, contrôle a posteriori de la Cour des Comptes, et voies de recours pour les soumissionnaires évincés. Ce guide détaille les mécanismes de contrôle et les procédures de contestation.',
    intro_ar:        'يُنظَّم نظام مراقبة الصفقات العمومية بالمغرب على عدة مستويات: رقابة قبلية للخزينة العامة، ورقابة بعدية للمجلس الأعلى للحسابات، ومسالك طعن للمتنافسين المُقصَين. يُفصِّل هذا الدليل آليات الرقابة وإجراءات الطعن.',
    legalDomain:     'administratif',
    keywords:        ['contrôle marchés publics', 'TGR visa', 'Cour des comptes marchés', 'recours marché public', 'commission des marchés', 'contentieux marchés'],
    keywords_ar:     ['مراقبة الصفقات العمومية', 'تأشيرة الخزينة العامة', 'المجلس الأعلى للحسابات', 'طعن صفقة عمومية', 'لجنة الصفقات', 'نزاعات الصفقات'],
    searchTerms:     ['contrôle marchés publics maroc', 'recours marché public maroc', 'TGR marchés maroc'],
    relatedSlugs:    ['marches-publics-maroc', 'passation-marches-publics-maroc', 'execution-marche-public-maroc'],
    faq: [
      {
        question: 'Comment contester l\'attribution d\'un marché public au Maroc ?',
        answer:   'Un soumissionnaire évincé peut d\'abord exercer un recours gracieux auprès du maître d\'ouvrage dans les 10 jours. Ensuite, un recours devant le tribunal administratif est possible. La Commission des Marchés peut également être saisie pour avis.',
      },
    ],
    faq_ar: [
      {
        question: 'كيف يمكن الطعن في إسناد صفقة عمومية بالمغرب؟',
        answer:   'يحق للمتنافس المُقصى تقديم طعن ودي لصاحب المشروع في أجل 10 أيام، ثم اللجوء إلى المحكمة الإدارية. كما يمكن إخطار لجنة الصفقات للاستئناس برأيها.',
      },
    ],
  },

  // ══════════════════════════════════════════════════════════════════════════
  // SPOKES — Droit Numérique
  // ══════════════════════════════════════════════════════════════════════════

  {
    lastUpdated:     '2026-06',
    slug:            'protection-donnees-personnelles-maroc',
    category:        'societe',
    title:           'Protection des Données Personnelles au Maroc : loi 09-08 et CNDP 2026',
    title_ar:        'حماية البيانات الشخصية بالمغرب : القانون 09-08 واللجنة الوطنية 2026',
    metaDescription: 'Guide complet sur la loi 09-08 : obligations des responsables de traitement, droits des personnes, déclarations CNDP, sanctions et conformité.',
    metaDescription_ar: 'دليل متكامل حول القانون 09-08: التزامات المعالِجين، حقوق الأشخاص، التصريحات للجنة الوطنية، العقوبات والامتثال.',
    h1:              'Protection des Données Personnelles au Maroc',
    h1_ar:           'حماية البيانات الشخصية بالمغرب',
    intro:           'La Loi n°09-08 relative à la protection des données personnelles est le texte fondamental du droit numérique marocain. Elle impose des obligations précises aux entreprises et organisations qui collectent ou traitent des données personnelles et crée la CNDP comme autorité de contrôle indépendante.',
    intro_ar:        'يُشكِّل القانون رقم 09-08 المتعلق بحماية المعطيات الشخصية النصَّ المحوري للقانون الرقمي المغربي. يُلقي التزامات محددة على الشركات والمؤسسات التي تجمع البيانات الشخصية أو تعالجها، ويُنشئ اللجنة الوطنية هيئةً رقابية مستقلة.',
    legalDomain:     'numerique',
    keywords:        ['loi 09-08', 'données personnelles', 'CNDP', 'déclaration traitement', 'consentement', 'droit accès données', 'DPO maroc', 'RGPD maroc'],
    keywords_ar:     ['القانون 09-08', 'البيانات الشخصية', 'اللجنة الوطنية CNDP', 'التصريح بالمعالجة', 'الموافقة', 'حق الاطلاع', 'مسؤول حماية البيانات', 'الامتثال الرقمي'],
    searchTerms:     ['loi 09-08 maroc', 'protection données personnelles maroc', 'CNDP maroc'],
    relatedSlugs:    ['droit-numerique-ia-maroc', 'ecommerce-maroc', 'droit-influenceurs-maroc'],
    faq: [
      {
        question: 'Quelles entreprises sont concernées par la loi 09-08 au Maroc ?',
        answer:   'Toute personne physique ou morale qui collecte, traite, stocke ou transfère des données personnelles au Maroc est soumise à la loi 09-08, quelle que soit sa taille ou son secteur d\'activité.',
      },
    ],
    faq_ar: [
      {
        question: 'أي مؤسسات تخضع للقانون 09-08 بالمغرب؟',
        answer:   'كل شخص ذاتي أو اعتباري يجمع البيانات الشخصية أو يعالجها أو يخزنها أو ينقلها داخل المغرب يخضع للقانون 09-08، بصرف النظر عن حجمه أو قطاع نشاطه.',
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'ecommerce-maroc',
    category:        'societe',
    title:           'E-Commerce au Maroc : cadre juridique et obligations 2026',
    title_ar:        'التجارة الإلكترونية بالمغرب : الإطار القانوني والالتزامات 2026',
    metaDescription: 'Guide juridique e-commerce au Maroc : loi 53-05, contrats électroniques, signature numérique, obligations vendeurs, droit de rétractation.',
    metaDescription_ar: 'دليل قانوني للتجارة الإلكترونية بالمغرب: القانون 53-05، العقود الإلكترونية، التوقيع الرقمي، التزامات البائعين، حق الرجوع.',
    h1:              'E-Commerce au Maroc : obligations légales',
    h1_ar:           'التجارة الإلكترونية بالمغرب : الالتزامات القانونية',
    intro:           'Le commerce électronique au Maroc est encadré par la Loi n°53-05 sur l\'échange électronique de données juridiques et la Loi n°31-08 sur la protection du consommateur. Tout vendeur en ligne doit respecter des obligations d\'information, de livraison et de garantie précises.',
    intro_ar:        'تُنظَّم التجارة الإلكترونية بالمغرب بموجب القانون رقم 53-05 المتعلق بالتبادل الإلكتروني للمعطيات وقانون 31-08 لحماية المستهلك. يلتزم كل بائع إلكتروني بمتطلبات محددة في الإعلام والتسليم والضمان.',
    legalDomain:     'numerique',
    keywords:        ['e-commerce maroc', 'vente en ligne maroc', 'loi 53-05', 'contrat électronique', 'signature numérique', 'livraison', 'retour produit maroc'],
    keywords_ar:     ['التجارة الإلكترونية المغرب', 'البيع عبر الإنترنت', 'القانون 53-05', 'العقد الإلكتروني', 'التوقيع الرقمي', 'التسليم', 'إرجاع المنتج'],
    searchTerms:     ['e-commerce maroc loi', 'vente ligne maroc obligations', 'boutique en ligne maroc'],
    relatedSlugs:    ['droit-numerique-ia-maroc', 'protection-consommateur-maroc', 'protection-donnees-personnelles-maroc'],
    faq: [
      {
        question: 'Quelles mentions légales doit afficher un site e-commerce marocain ?',
        answer:   'Un site e-commerce au Maroc doit afficher : raison sociale, ICE, adresse, prix TTC, conditions générales de vente, politique de retour, et les modalités de paiement. Ces obligations découlent de la loi 31-08 et de la loi 53-05.',
      },
    ],
    faq_ar: [
      {
        question: 'ما البيانات القانونية الإلزامية على موقع التجارة الإلكترونية المغربي؟',
        answer:   'يجب أن يعرض الموقع: الاسم التجاري والرقم الضريبي والعنوان والأسعار شاملة للضريبة والشروط العامة للبيع وسياسة الإرجاع وطرق الدفع. تنبثق هذه الالتزامات من القانونين 31-08 و53-05.',
      },
    ],
  },

  // ══════════════════════════════════════════════════════════════════════════
  // SPOKES — Urbanisme
  // ══════════════════════════════════════════════════════════════════════════

  {
    lastUpdated:     '2026-06',
    slug:            'permis-construire-maroc',
    category:        'administratif',
    title:           'Permis de Construire au Maroc : procédure et délais 2026',
    title_ar:        'رخصة البناء بالمغرب : المسطرة والآجال 2026',
    metaDescription: 'Guide complet sur le permis de construire au Maroc : dossier requis, instruction par l\'agence urbaine, délais légaux, certificat de conformité.',
    metaDescription_ar: 'دليل متكامل حول رخصة البناء بالمغرب: الملف المطلوب، الدراسة من قِبَل الوكالة الحضرية، الآجال القانونية، شهادة المطابقة.',
    h1:              'Permis de Construire au Maroc',
    h1_ar:           'رخصة البناء بالمغرب',
    intro:           'Le permis de construire est obligatoire pour toute construction neuve au Maroc. Régi par la Loi n°12-90 et le Décret n°2-92-832, il est délivré par le président du conseil communal après instruction par l\'agence urbaine. Ce guide détaille le dossier à constituer, les délais et la procédure complète.',
    intro_ar:        'تُعدُّ رخصة البناء إلزامية لكل بناء جديد بالمغرب. تُنظِّمها الجهةُ المختصةُ بموجب القانون رقم 12-90 والمرسوم رقم 2-92-832، وتُسلِّمها رئاسةُ المجلس الجماعي عقب دراستها من قِبَل الوكالة الحضرية. يُفصِّل هذا الدليل الملف الواجب تكوينه والآجال والمسطرة الكاملة.',
    legalDomain:     'administratif',
    keywords:        ['permis construire maroc', 'dossier permis construire', 'agence urbaine', 'architecte agréé', 'certificat conformité', 'délai permis construire', 'loi 12-90'],
    keywords_ar:     ['رخصة البناء المغرب', 'ملف رخصة البناء', 'الوكالة الحضرية', 'مهندس معماري معتمد', 'شهادة المطابقة', 'أجل رخصة البناء', 'القانون 12-90'],
    searchTerms:     ['permis construire maroc', 'obtenir permis construire maroc', 'dossier construction maroc'],
    relatedSlugs:    ['urbanisme-maroc', 'infractions-urbanistiques-maroc', 'collectivites-territoriales-maroc'],
    faq: [
      {
        question: 'Quel est le délai pour obtenir un permis de construire au Maroc ?',
        answer:   'Le délai légal d\'instruction est de 30 jours pour un dossier complet, et peut aller jusqu\'à 60 jours pour les projets complexes nécessitant l\'avis de plusieurs services. Passé ce délai sans réponse, le permis est tacitement accordé sous conditions.',
      },
    ],
    faq_ar: [
      {
        question: 'ما هو أجل الحصول على رخصة البناء بالمغرب؟',
        answer:   'الأجل القانوني للدراسة هو 30 يوماً للملف الكامل، وقد يصل إلى 60 يوماً للمشاريع المعقدة التي تستلزم رأي عدة مصالح. وبانقضاء الأجل دون رد، تُعدُّ الرخصة ممنوحةً ضمنياً وفق شروط.',
      },
    ],
  },

  {
    lastUpdated:     '2026-06',
    slug:            'infractions-urbanistiques-maroc',
    category:        'administratif',
    title:           'Infractions Urbanistiques au Maroc : sanctions et régularisation 2026',
    title_ar:        'المخالفات التعميرية بالمغرب : العقوبات والتسوية 2026',
    metaDescription: 'Guide sur les infractions urbanistiques au Maroc : construction sans permis, sanctions, démolition, procédure de régularisation et délais.',
    metaDescription_ar: 'دليل المخالفات التعميرية بالمغرب: البناء بدون رخصة، العقوبات، الهدم، مسطرة التسوية والآجال.',
    h1:              'Infractions Urbanistiques au Maroc',
    h1_ar:           'المخالفات التعميرية بالمغرب',
    intro:           'Les infractions urbanistiques (construction sans permis, dépassement du permis, non-conformité) sont fréquentes au Maroc et font l\'objet d\'une politique de contrôle renforcée. La Loi 12-90 définit les sanctions et les voies de régularisation. Ce guide explique les risques et les démarches pour se mettre en conformité.',
    intro_ar:        'المخالفات التعميرية (البناء بدون رخصة، تجاوز حدود الرخصة، عدم المطابقة) شائعة بالمغرب وتخضع لسياسة تقنين مشددة. يُحدِّد القانون 12-90 العقوبات ومسالك التسوية. يُوضِّح هذا الدليل المخاطر والإجراءات الواجب اتباعها للامتثال.',
    legalDomain:     'administratif',
    keywords:        ['infraction urbanistique', 'construction sans permis maroc', 'démolition construction illégale', 'régularisation construction', 'amende urbanisme', 'conformité bâtiment'],
    keywords_ar:     ['المخالفات التعميرية', 'بناء بدون رخصة المغرب', 'هدم البناء غير القانوني', 'تسوية البناء', 'غرامة التعمير', 'مطابقة البناء'],
    searchTerms:     ['infraction urbanistique maroc', 'construction illégale maroc', 'régularisation bâtiment maroc'],
    relatedSlugs:    ['urbanisme-maroc', 'permis-construire-maroc', 'collectivites-territoriales-maroc'],
    faq: [
      {
        question: 'Peut-on régulariser une construction sans permis au Maroc ?',
        answer:   'Oui, sous conditions. La régularisation est possible si la construction est conforme aux règles d\'urbanisme en vigueur. Elle nécessite le dépôt d\'un dossier de régularisation auprès de la commune et le paiement d\'une amende. L\'agence urbaine instruit le dossier.',
      },
    ],
    faq_ar: [
      {
        question: 'هل يمكن تسوية بناء شُيِّد بدون رخصة في المغرب؟',
        answer:   'نعم، بشروط. تُصبح التسوية ممكنة إذا كان البناء مطابقاً لقواعد التعمير السارية. وتستلزم إيداع ملف تسوية لدى الجماعة وأداء غرامة، فيما تتولى الوكالة الحضرية دراسة الملف.',
      },
    ],
  },

  // ─── Réforme marchés publics — décret 2-22-431 ───────────────────────────
  {
    lastUpdated:      '2026-06',
    slug:             'reforme-marches-publics-maroc',
    category:         'administratif',
    legalDomain:      'administratif',
    title:            'Réforme des marchés publics au Maroc : modifications du décret n° 2-22-431',
    title_ar:         'إصلاح الصفقات العمومية بالمغرب : تعديلات المرسوم رقم 2.22.431',
    metaDescription:  'Bons de commande à 800 000 DH TTC, appel d\'offres ouvert simplifié à 1 500 000 DH HT, offres anormalement basses à −15 % : les principales modifications proposées au décret n° 2-22-431 relatif aux marchés publics.',
    metaDescription_ar: 'سندات الطلب بحد 800.000 درهم، طلب العروض المفتوح المبسط بحد 1.500.000 درهم، العرض المنخفض بكيفية غير عادية عند −15 % : أبرز التعديلات المقترحة على المرسوم رقم 2.22.431 المتعلق بالصفقات العمومية.',
    h1:               'Réforme des marchés publics au Maroc : ce qui change dans le décret n° 2-22-431',
    h1_ar:            'إصلاح الصفقات العمومية في المغرب : أبرز تعديلات المرسوم رقم 2.22.431',
    intro:            '⚠ Avertissement — Ce guide est fondé sur un projet de décret modificatif non encore publié au Bulletin officiel. Les dispositions présentées constituent des modifications proposées et ne sont pas encore applicables. En cas de divergence avec le texte définitif, seule la version publiée officiellement fait foi.\n\nLe régime marocain de la commande publique s\'apprête à connaître de nouvelles évolutions. Un projet de décret modifiant et complétant le décret n° 2-22-431 du 15 chaabane 1444 (8 mars 2023) relatif aux marchés publics a été élaboré par le Ministère de l\'Économie et des Finances. Ce projet, soumis à l\'avis de la Commission nationale des marchés publics, vise à ajuster le dispositif réglementaire au regard des enseignements tirés des premières années d\'application du décret de 2023. Vingt-neuf articles sont concernés par les modifications proposées.',
    intro_ar:         '⚠ تنبيه — يستند هذا الدليل إلى مشروع مرسوم تعديلي لم يُنشر بعد في الجريدة الرسمية. الأحكام المعروضة هي تعديلات مقترحة وليست سارية المفعول بعد. وفي حال وجود تعارض مع النص الرسمي النهائي، يُعتدّ فقط بالنص المنشور رسمياً.\n\nتستعد منظومة الطلبيات العمومية في المغرب لمستجدات جوهرية، إذ أعدّت وزارة الاقتصاد والمالية مشروع مرسوم لتغيير وتتميم المرسوم رقم 2.22.431 الصادر في 15 شعبان 1444 (8 مارس 2023) المتعلق بالصفقات العمومية. ويُعدّ هذا المشروع، الذي يطال تسعةً وعشرين مادة، امتداداً للإصلاح المنجز في 2023، ويرمي إلى معالجة الإشكاليات المُستخلصة من السنوات الأولى لتطبيق المرسوم.',
    keywords:         ['réforme marchés publics Maroc', 'décret 2-22-431', 'bons de commande marchés publics', 'appel d\'offres ouvert simplifié Maroc', 'offre anormalement basse marchés publics Maroc', 'offre excessive marchés publics', 'préférence nationale marchés publics Maroc', 'TPE PME marchés publics Maroc', 'coopératives marchés publics', 'auto-entrepreneur marchés publics', 'commande publique Maroc', 'maître d\'ouvrage', 'concurrent marchés publics'],
    keywords_ar:      ['إصلاح الصفقات العمومية المغرب', 'مرسوم الصفقات العمومية 2.22.431', 'سندات الطلب', 'طلب العروض المفتوح المبسط', 'العرض المنخفض بكيفية غير عادية', 'العرض المفرط', 'الأفضلية الوطنية', 'المقاولات الصغرى والمتوسطة', 'التعاونيات', 'المقاول الذاتي', 'الطلبيات العمومية المغرب', 'صاحب المشروع'],
    searchTerms:      ['marchés publics', 'bons de commande', 'appel offres', 'décret 2-22-431', 'commande publique', 'offre anormalement basse'],
    specificNumbers:  ['2-22-431'],
    relatedSlugs:     ['marches-publics-maroc', 'collectivites-territoriales-maroc', 'droit-administratif-maroc'],

    sections: [
      {
        icon: '📋',
        h2: 'Contexte et portée du projet de réforme',
        content: [
          'Le décret n° 2-22-431 du 15 chaabane 1444 (8 mars 2023) constitue le texte de référence régissant les marchés de l\'État, des collectivités territoriales et des établissements publics depuis le 1er octobre 2023. Le projet de modification s\'inscrit dans la continuité de la réforme engagée et répond aux difficultés pratiques exprimées par les maîtres d\'ouvrage et les opérateurs économiques au cours des trois premières années d\'application.',
          'Le projet de décret, préparé par le Ministère de l\'Économie et des Finances et soumis à l\'avis de la Commission nationale des marchés publics, modifie vingt-neuf articles du décret n° 2-22-431. Il a été signé par le ministre délégué auprès de la ministre de l\'Économie et des Finances, chargé du Budget, en vue de sa délibération en Conseil de gouvernement.',
        ],
        bullets: [
          'Répondre aux attentes des maîtres d\'ouvrage et des opérateurs économiques exprimées lors des premières années d\'application du décret de 2023',
          'Clarifier les responsabilités de chaque intervenant dans la procédure de passation et simplifier la maîtrise d\'ouvrage déléguée',
          'Rationaliser le recours aux bons de commande et aux contrats de droit commun',
          'Renforcer la dimension sociale dans l\'estimation du coût des prestations (gardiennage, nettoyage, entretien des espaces verts)',
          'Encourager le tissu entrepreneurial local via la préférence territoriale et la promotion de l\'emploi local au lieu d\'exécution',
          'Réorienter l\'évaluation des offres vers la protection du coût réel du travail pour les marchés à forte composante sociale',
          'Favoriser la participation des TPE, PME, coopératives, auto-entrepreneurs et entreprises innovantes par le relèvement de certains seuils',
          'Renforcer l\'efficacité, l\'intégrité et la transparence de la commande publique',
        ],
      },
      {
        icon: '📊',
        h2: 'Les seuils et taux qui évoluent selon le projet',
        content: [
          'Les modifications les plus structurantes du projet portent sur les seuils de passation et les taux d\'appréciation des offres. Le tableau de synthèse ci-dessous présente les principales évolutions chiffrées, telles qu\'elles ressortent du texte du projet de décret. Il convient de souligner que ces chiffres sont issus d\'un projet et restent susceptibles d\'être modifiés dans le texte définitif.',
        ],
        bullets: [
          'Bons de commande (Art. 91) — Avant : 500 000 DH TTC → Projet : 800 000 DH TTC — Élargissement du champ de recours aux bons de commande sans procédure formelle d\'appel d\'offres',
          'Appel d\'offres ouvert simplifié (Art. 19) — Avant : 1 000 000 DH HT → Projet : 1 500 000 DH HT — Davantage de marchés éligibles à la procédure allégée',
          'Offre excessive (Art. 44 et 144) — Avant : > 20 % du montant estimatif → Projet : > 15 % — Seuil plus strict pour écarter les offres disproportionnées',
          'Offre anormalement basse (Art. 44 et 144) — Avant : < −20 % (marchés de travaux, fournitures, services) → Projet : < −15 % — Harmonisation et lutte renforcée contre le bradage des prix',
          'Délai de publicité des bons de commande (Art. 91) — Avant : 48 heures → Projet : 5 jours minimum — Transparence accrue et meilleure accessibilité pour les concurrents',
          'Prime dialogue compétitif et offre spontanée (Art. 12 et 13) — Avant : non plafonnée → Projet : 0,5 % de l\'offre financière retenue, plafond 200 000 DH — Encadrement financier des primes accordées',
          'Garantie de bonne exécution — bons de commande (Art. 91) — Avant : non prévue → Projet : 2 % du montant estimatif, entre 1 000 DH et 5 000 DH — Nouvelle garantie pour sécuriser l\'exécution',
          'Prolongation de la validité des offres (Art. 143) — Avant : accord sans plafond → Projet : 30 jours au plus, 90 jours au total maximum — Protection des concurrents contre des délais d\'approbation excessifs',
        ],
      },
      {
        icon: '📦',
        h2: 'Bons de commande : le seuil annuel passerait à 800 000 DH TTC (Art. 91)',
        content: [
          'Le projet de décret prévoit de relever le seuil annuel des prestations réalisées par bons de commande de 500 000 DH TTC à 800 000 DH TTC, par ordonnateur, sous-ordonnateur ou personne habilitée, au cours d\'une même année budgétaire. Ce relèvement concerne les marchés de travaux, de fournitures et de services courants qui ne requièrent pas, en raison de leur nature ou de leur montant, le recours aux procédures formelles d\'appel d\'offres.',
          'Selon le projet, ce seuil de 800 000 DH TTC s\'apprécie sur la base du montant annuel total des commandes passées par un même ordonnateur pour un même objet de prestations. Le projet renforce également les obligations de publicité et introduit la possibilité d\'exiger une garantie de bonne exécution, renforçant ainsi la transparence de cette procédure.',
          'Cette modification est particulièrement importante pour les administrations, les collectivités territoriales et les établissements publics qui recourent fréquemment aux bons de commande pour couvrir leurs besoins courants.',
        ],
        bullets: [
          'Seuil annuel proposé : 800 000 DH TTC par ordonnateur et par objet de prestations (Art. 91)',
          'Délai de publicité de l\'avis : au moins 5 jours (contre 48 heures actuellement)',
          'Garantie de bonne exécution possible : 2 % du montant estimatif, entre 1 000 DH minimum et 5 000 DH maximum',
          'Possibilité de substituer la garantie par une caution personnelle et solidaire d\'un établissement agréé',
          'L\'avis de bon de commande doit préciser : objet, spécifications techniques, montant estimatif, lieu de retrait des documents, licences et autorisations requises',
          'Possibilité de dépôt des offres par voie électronique selon les modalités prévues par l\'avis',
        ],
      },
      {
        icon: '⚖️',
        h2: 'Évaluation des offres : mieux-disant, offres anormales et préférence territoriale (Art. 43 et 44)',
        content: [
          'Important — Le projet maintient le critère du concurrent le moins disant comme règle générale d\'attribution : l\'offre la plus avantageuse s\'entend, pour les marchés de travaux, fournitures et services (hors études), de l\'offre financière la moins chère par rapport au prix de référence (Art. 43 du projet). La note de présentation évoque un passage à la culture du mieux-disant, mais le texte du projet conserve le moins-disant comme critère principal pour la majorité des marchés.',
          'Exception pour les marchés à forte composante sociale — Pour les marchés de gardiennage des bâtiments administratifs, de nettoyage et d\'entretien des espaces verts, l\'offre la plus avantageuse est celle qui propose le taux de majoration le plus élevé, c\'est-à-dire la meilleure protection du coût réel de la main-d\'œuvre. Cette règle constitue une application du mieux-disant social et vise à lutter contre le bradage des prix au détriment des obligations sociales des prestataires.',
          'En cas d\'égalité entre plusieurs offres financièrement avantageuses, le projet prévoit une préférence territoriale : priorité au concurrent qui exerce son activité dans la commune d\'exécution des travaux, à défaut dans la province ou la préfecture, à défaut dans la région, et en dernier recours tirage au sort entre les concurrents à égalité (Art. 43).',
          'Les seuils d\'appréciation des offres excessives et anormalement basses sont harmonisés à 15 %, qu\'il s\'agisse de l\'offre financière globale ou des prix unitaires (Art. 44 et 144).',
        ],
        bullets: [
          'Critère général d\'attribution : offre financière la moins chère par rapport au prix de référence (moins-disant maintenu pour la majorité des marchés)',
          'Exception marchés sociaux : gardiennage / nettoyage / espaces verts → taux de majoration le plus élevé (protection de la main-d\'œuvre)',
          'Offre excessive harmonisée : > 15 % du montant estimatif du maître d\'ouvrage (Art. 44 et 144)',
          'Offre anormalement basse harmonisée : < −15 % du montant estimatif, pour travaux, fournitures et services hors études (Art. 44 et 144)',
          'Préférence territoriale en cas d\'égalité : commune → province / préfecture → région → tirage au sort (Art. 43)',
          'Appréciation des offres sur la base du montant hors taxes par le maître d\'ouvrage (Art. 44)',
        ],
      },
      {
        icon: '🏢',
        h2: 'Dimension sociale, marchés réservés aux TPE/PME et préférence nationale (Art. 6, 147 et 148)',
        content: [
          'Art. 6 — Estimation du coût des prestations : Pour les marchés de gardiennage des bâtiments administratifs, de nettoyage et d\'entretien des espaces verts, le maître d\'ouvrage est désormais tenu, lors de l\'élaboration du coût estimatif, de prendre en compte le salaire minimum légal (SMIG) et les cotisations sociales obligatoires. Le coût estimatif doit être consigné dans un document écrit mentionnant les montants hors taxes, le taux et le montant de TVA, et le montant toutes taxes comprises. Cette mesure vise à mettre fin aux pratiques d\'offres financièrement irréalistes dans ces secteurs.',
          'Art. 147 — Préférence nationale : Le projet maintient et précise la majoration de 15 % applicable aux offres des concurrents non établis au Maroc lors de la comparaison avec les offres des concurrents nationaux, pour les marchés de travaux, de fournitures et certains marchés de services portant sur des études.',
          'Art. 148 — Marchés réservés : Le projet encourage et précise le recours aux marchés réservés en faveur des très petites entreprises, des PME, des coopératives, des unions de coopératives et des auto-entrepreneurs, ainsi que des entreprises innovantes. Les conditions et modalités d\'application peuvent être fixées par arrêté du ministre chargé des Finances.',
        ],
        bullets: [
          'SMIG et cotisations sociales obligatoirement intégrés dans l\'estimation des marchés de gardiennage, nettoyage et entretien des espaces verts (Art. 6)',
          'Majoration de 15 % appliquée aux offres des concurrents non établis au Maroc lors de la comparaison des offres (Art. 147 — préférence nationale)',
          'Marchés réservés possibles pour les TPE, PME, coopératives, unions de coopératives et auto-entrepreneurs (Art. 148)',
          'Conditions des marchés réservés fixées par arrêté du ministre de l\'Économie et des Finances — à surveiller lors de la publication du texte définitif',
          'Préférence territoriale en cas d\'égalité : avantage supplémentaire pour les concurrents exerçant dans la zone d\'exécution (Art. 43)',
        ],
      },
      {
        icon: '📁',
        h2: 'Simplifications administratives et procédurales (Art. 28, 136, 143 et 154)',
        content: [
          'Le projet apporte plusieurs simplifications en faveur des concurrents et des maîtres d\'ouvrage, en cohérence avec la politique de dématérialisation progressive de la commande publique marocaine.',
          'Art. 28 — Preuve des capacités et qualités : Dans le cadre des marchés conclus par voie d\'appel d\'offres ouvert simplifié, le concurrent peut produire une attestation ou un certificat délivré dans le cadre du système de qualification, de classification ou d\'agrément, en lieu et place de certaines pièces du dossier administratif ou technique visées à l\'article 28, lorsque les marchés concernent les mêmes prestations.',
          'Art. 143 — Délais d\'approbation : Le projet plafonne la prolongation de la validité des offres à 30 jours, pour un total ne pouvant excéder 90 jours à compter de la date d\'ouverture des plis. Cette mesure protège les concurrents contre des délais d\'approbation excessifs de la part de l\'autorité approbatrice.',
          'Art. 154 — Maîtrise d\'ouvrage déléguée : Lorsque le ministre concerné a préalablement signé la convention de maîtrise d\'ouvrage déléguée, le maître d\'ouvrage délégué est dispensé du visa ou de l\'autorisation normalement requis pour la passation des marchés relevant de cette convention, simplifiant ainsi la gestion de certains projets publics.',
        ],
        bullets: [
          'Certificat de qualification ou de classification remplace certaines pièces du dossier technique dans le cadre de l\'AO ouvert simplifié (Art. 28)',
          'Ouverture et évaluation électroniques des plis encadrées par les textes d\'application (Art. 136)',
          'Prolongation de la validité des offres : 30 jours maximum, 90 jours au total — protection des concurrents (Art. 143)',
          'Maîtrise d\'ouvrage déléguée : dispense de visa si convention préalable signée par le ministre compétent (Art. 154)',
          'Réorganisation de la composition des commissions d\'appel d\'offres selon la nature de l\'organisme maître d\'ouvrage (État, établissements publics, personnes morales de droit public) — Art. 38',
        ],
      },
    ],

    sections_ar: [
      {
        icon: '📋',
        h2: 'سياق مشروع الإصلاح ونطاقه',
        content: [
          'يُشكّل المرسوم رقم 2.22.431 الصادر في 15 شعبان 1444 (8 مارس 2023) الإطار التشريعي المرجعي لإبرام صفقات الدولة والجماعات الترابية والمؤسسات العامة منذ فاتح أكتوبر 2023. ويأتي مشروع التعديل في سياق استكمال هذا الإصلاح، استجابةً للإشكاليات العملية التي أبدت عنها أصحاب المشاريع والمتعاملين الاقتصاديين خلال السنوات الثلاث الأولى من تطبيق المرسوم.',
          'أُعدّ المشروع من طرف وزارة الاقتصاد والمالية، وعُرض على اللجنة الوطنية للطلبيات العمومية، ويطال تسعةً وعشرين مادة من مرسوم 2023.',
        ],
        bullets: [
          'الاستجابة لتطلعات أصحاب المشاريع والمتعاملين الاقتصاديين المُعبَّر عنها خلال السنوات الأولى من تطبيق المرسوم',
          'توضيح مسؤوليات المتدخلين في مسطرة إبرام الصفقات وتبسيط الإشراف المنتدب على المشروع',
          'ترشيد اللجوء إلى سندات الطلب والعقود الخاضعة للقانون العادي',
          'تعزيز البعد الاجتماعي في إعداد تقدير كلفة الأعمال، لا سيما بالنسبة لصفقات الحراسة والنظافة وصيانة المساحات الخضراء',
          'تشجيع النسيج المقاولاتي المحلي عبر الأفضلية الترابية وإنعاش التشغيل المحلي',
          'إعادة توجيه تقييم العروض نحو حماية الكلفة الحقيقية للعمل في الصفقات ذات الطابع الاجتماعي',
          'تيسير ولوج المقاولات الصغيرة جداً والمتوسطة والتعاونيات والمقاولين الذاتيين والمقاولات المبتكرة إلى الطلبيات العمومية',
          'تعزيز فعالية ونزاهة وشفافية إبرام الصفقات العمومية',
        ],
      },
      {
        icon: '📊',
        h2: 'العتبات والنسب التي تشملها التعديلات المقترحة',
        content: [
          'تنصبّ أبرز تعديلات المشروع على عتبات إبرام الصفقات ونسب تقييم العروض. وتجدر الإشارة إلى أن الأرقام الواردة أدناه مستقاة من نص المشروع، وتظل قابلة للتعديل في النص النهائي.',
        ],
        bullets: [
          'سندات الطلب (م. 91) — قبل : 500.000 درهم ش.ج → المشروع : 800.000 درهم ش.ج — توسيع نطاق اللجوء إلى سندات الطلب',
          'طلب العروض المفتوح المبسط (م. 19) — قبل : 1.000.000 درهم خ.ر → المشروع : 1.500.000 درهم خ.ر — تمكين عدد أكبر من الصفقات من الاستفادة من المسطرة المبسطة',
          'العرض المفرط (م. 44 و144) — قبل : > 20 % → المشروع : > 15 % — تشديد عتبة الإقصاء',
          'العرض المنخفض بكيفية غير عادية (م. 44 و144) — قبل : < −20 % → المشروع : < −15 % — تعزيز الحماية من ظاهرة كسر الأسعار',
          'مدة إشهار سند الطلب (م. 91) — قبل : 48 ساعة → المشروع : 5 أيام على الأقل — تقوية الشفافية وتكافؤ الفرص',
          'جائزة الحوار التنافسي والعرض التلقائي (م. 12 و13) — قبل : غير محددة → المشروع : 0,5 % من العرض المالي المقبول، بسقف 200.000 درهم',
          'ضمان حسن التنفيذ لسندات الطلب (م. 91) — قبل : غير مقرر → المشروع : 2 % من مبلغ تقدير الأعمال، بين 1.000 و5.000 درهم',
          'مدة سريان العروض (م. 143) — قبل : بالتراضي دون سقف → المشروع : 30 يوماً على الأكثر، 90 يوماً في المجموع — حماية المتنافسين من تأخيرات المصادقة',
        ],
      },
      {
        icon: '📦',
        h2: 'سندات الطلب : العتبة السنوية ترتفع إلى 800.000 درهم ش.ج (م. 91)',
        content: [
          'يرمي المشروع إلى رفع العتبة السنوية للأشغال المُنجزة بواسطة سندات الطلب من 500.000 درهم ش.ج إلى 800.000 درهم ش.ج، بالنسبة لكل آمر بالصرف أو آمر بالصرف فرعي أو شخص مفوض، وذلك في إطار سنة مالية واحدة.',
          'وتُقدَّر هذه العتبة على أساس إجمالي قيمة الطلبيات الصادرة عن نفس الآمر بالصرف لنفس موضوع الأشغال في السنة المالية الواحدة. كما يُدخل المشروع التزامات جديدة تتعلق بالإشهار واحتمال اشتراط ضمان حسن التنفيذ، مما يعزز شفافية هذه المسطرة.',
        ],
        bullets: [
          'العتبة السنوية المقترحة : 800.000 درهم ش.ج لكل آمر بالصرف ولكل موضوع أشغال (م. 91)',
          'مدة إشهار الإعلان : 5 أيام على الأقل (عوضاً عن 48 ساعة حالياً)',
          'ضمان حسن التنفيذ المحتمل : 2 % من مبلغ تقدير الأعمال، بين 1.000 درهم و5.000 درهم',
          'إمكانية تعويض الضمان بكفالة شخصية وتضامنية صادرة عن مؤسسة معتمدة',
          'يجب أن يتضمن إعلان سند الطلب : الموضوع، المواصفات التقنية، التقدير المالي، مكان تسلّم الوثائق، الرخص والتراخيص المطلوبة',
          'إمكانية إيداع العروض إلكترونياً وفق الشروط المحددة في الإعلان',
        ],
      },
      {
        icon: '⚖️',
        h2: 'تقييم العروض : العرض الأفضل والعروض الشاذة والأفضلية الترابية (م. 43 و44)',
        content: [
          'ملاحظة جوهرية — يُبقي المشروع على معيار "العرض الأقل ثمناً" بالنسبة للثمن المرجعي كمعيار عام لإسناد الصفقات، وذلك بالنسبة لصفقات الأشغال والتوريدات والخدمات غير المتعلقة بالدراسات (م. 43). أما مفهوم "أفضل عرض" الذي أشارت إليه المذكرة التقديمية، فتطبيقه الفعلي في نص المشروع يقتصر على فئة معينة من الصفقات.',
          'استثناء اجتماعي — بالنسبة لصفقات حراسة المباني الإدارية وتنظيفها وصيانة المساحات الخضراء، يُعدّ العرض الأكثر أفضلية هو العرض الذي يقترح نسبة الزيادة الأعلى، أي الذي يُوفّر أفضل حماية لكلفة اليد العاملة. ويستهدف هذا الاستثناء الحدّ من ظاهرة كسر الأسعار على حساب الالتزامات الاجتماعية للمقاولات.',
          'عند التساوي في العروض الأكثر أفضلية، يُرجّح المشروع المتنافسَ الذي يزاول نشاطه في مكان تنفيذ الأعمال بالنفوذ الترابي للجماعة، ثم للإقليم أو العمالة، ثم للجهة، وأخيراً يُجرى قرعة بين المتنافسين المتساوين (م. 43).',
          'تتم مواءمة عتبات العرض المفرط والعرض المنخفض بكيفية غير عادية عند 15 % سواء بالنسبة للثمن الإجمالي أو للأثمان الأحادية (م. 44 و144).',
        ],
        bullets: [
          'المعيار العام لإسناد الصفقات : العرض المالي الأقل ثمناً بالنسبة للثمن المرجعي (يُحتفظ بمعيار الأقل ثمناً بوجه عام)',
          'استثناء صفقات الحراسة والنظافة والمساحات الخضراء : نسبة الزيادة الأعلى هي المعيار (حماية كلفة اليد العاملة)',
          'العرض المفرط : > 15 % من المبلغ التقديري لكلفة الأعمال (م. 44 و144)',
          'العرض المنخفض بكيفية غير عادية : < −15 % من المبلغ التقديري، لصفقات الأشغال والتوريدات والخدمات غير المتعلقة بالدراسات (م. 44 و144)',
          'الأفضلية الترابية عند التساوي : الجماعة → الإقليم أو العمالة → الجهة → القرعة (م. 43)',
          'تُقيَّم العروض على أساس المبلغ الخارج عن الرسوم من قِبَل صاحب المشروع (م. 44)',
        ],
      },
      {
        icon: '🏢',
        h2: 'البعد الاجتماعي والصفقات المخصصة للمقاولات الصغرى ومتوسطة الحجم (م. 6 و147 و148)',
        content: [
          'المادة 6 — إعداد تقدير كلفة الأعمال : بالنسبة لصفقات حراسة المباني الإدارية وتنظيفها وصيانة المساحات الخضراء، يتعين على صاحب المشروع، عند إعداد تقدير كلفة الأعمال، أن يأخذ بعين الاعتبار الحد الأدنى القانوني للأجور (SMIG) والمساهمات الاجتماعية الإلزامية. ويُضمَّن تقدير كلفة الأعمال في وثيقة مكتوبة تُبرز المبلغ خارج الرسوم ونسبة الضريبة على القيمة المضافة ومبلغها والمبلغ مع احتساب جميع الرسوم.',
          'المادة 147 — الأفضلية الوطنية : يُقرّ المشروع تطبيق نسبة زيادة قدرها 15 % على العروض المالية للمتنافسين غير المؤسَّسين بالمغرب عند المقارنة مع عروض المتنافسين الوطنيين، بالنسبة لصفقات الأشغال والتوريدات وبعض صفقات الخدمات المتعلقة بالدراسات.',
          'المادة 148 — الصفقات المخصصة : يحثّ المشروع على اللجوء إلى الصفقات المخصصة لفائدة المقاولات الصغيرة جداً والمقاولات الصغيرة والمتوسطة والتعاونيات واتحاداتها والمقاولين الذاتيين والمقاولات المبتكرة، ويمكن أن تُحدَّد شروط وكيفيات تطبيق ذلك بقرار للوزير المكلف بالمالية.',
        ],
        bullets: [
          'الحد الأدنى القانوني للأجور والمساهمات الاجتماعية الإلزامية يجب إدماجها في تقدير كلفة صفقات الحراسة والنظافة والمساحات الخضراء (م. 6)',
          'زيادة 15 % تُطبَّق على عروض المتنافسين غير المؤسَّسين بالمغرب عند المقارنة (م. 147 — الأفضلية الوطنية)',
          'صفقات مخصصة ممكنة للمقاولات الصغيرة جداً والمتوسطة والتعاونيات والمقاولين الذاتيين (م. 148)',
          'شروط الصفقات المخصصة تُحدَّد بقرار للوزير المكلف بالمالية — للمتابعة عند نشر النص النهائي',
          'الأفضلية الترابية عند التساوي : ميزة إضافية للمتنافسين الممارسين نشاطهم في منطقة تنفيذ الأشغال (م. 43)',
        ],
      },
      {
        icon: '📁',
        h2: 'التبسيطات الإدارية والمسطرية (م. 28 و136 و143 و154)',
        content: [
          'يُدخل المشروع جملةً من التبسيطات لفائدة المتنافسين وأصحاب المشاريع، في سياق التحول الرقمي التدريجي لمنظومة الطلبيات العمومية المغربية.',
          'المادة 28 — إثبات القدرات والمؤهلات : في إطار الصفقات المبرمة بواسطة طلب العروض المفتوح المبسط، يمكن للمتنافس الإدلاء بالشهادة المسلمة في إطار نظام التأهيل والتصنيف أو الاعتماد، عوضاً عن بعض الوثائق المطلوبة في الملف الإداري أو التقني المشار إليها في المادة 28، متى كانت الصفقة تهم نفس الأعمال.',
          'المادة 143 — آجال المصادقة : يُقيّد المشروع تمديد صلاحية العروض في 30 يوماً، بحيث لا يتجاوز مجموع مدة الصلاحية 90 يوماً ابتداءً من تاريخ فتح الأظرفة، حماية للمتنافسين من آجال المصادقة المفرطة.',
          'المادة 154 — الإشراف المنتدب على المشروع : متى كان الوزير المعني قد وقّع مسبقاً على اتفاقية الإشراف المنتدب، يُعفى صاحب المشروع المنتدب من التأشيرة أو الإذن المطلوبَين عادةً لإبرام الصفقات المندرجة ضمن تلك الاتفاقية.',
        ],
        bullets: [
          'شهادة التأهيل أو التصنيف أو الاعتماد تحلّ محل بعض وثائق الملف التقني في إطار طلب العروض المبسط (م. 28)',
          'فتح الأظرفة وتقييم العروض إلكترونياً مُؤطَّران بالنصوص التطبيقية (م. 136)',
          'تمديد صلاحية العروض : 30 يوماً على الأكثر، 90 يوماً في المجموع — حماية المتنافسين (م. 143)',
          'الإشراف المنتدب : إعفاء من التأشيرة إذا سبق للوزير المعني التوقيع على الاتفاقية (م. 154)',
          'إعادة تنظيم تشكيلة لجنة طلب العروض بحسب طبيعة الجهة صاحبة المشروع — الدولة، المؤسسات العامة، هيئات القانون العام الأخرى (م. 38)',
        ],
      },
    ],

    faq: [
      {
        question: 'Le seuil des bons de commande change-t-il dans le cadre de la réforme des marchés publics au Maroc ?',
        answer:   'Selon le projet de décret, le seuil annuel des prestations réalisées par bons de commande passerait de 500 000 DH TTC à 800 000 DH TTC, par ordonnateur, sous-ordonnateur ou personne habilitée, au cours d\'une même année budgétaire (Art. 91). Ce relèvement reste soumis à la publication officielle du texte définitif au Bulletin officiel.',
      },
      {
        question: 'Quel est le nouveau seuil de l\'appel d\'offres ouvert simplifié selon le projet de réforme ?',
        answer:   'Le projet prévoit de relever le seuil de l\'appel d\'offres ouvert simplifié de 1 000 000 DH HT à 1 500 000 DH HT (Art. 19). Les marchés-cadres et les marchés reconductibles passés par cette procédure bénéficieraient d\'une appréciation du coût sur la base du montant annuel.',
      },
      {
        question: 'Qu\'est-ce qu\'une offre anormalement basse dans les marchés publics marocains ?',
        answer:   'Une offre anormalement basse est une offre dont le prix est inférieur de manière importante au montant estimatif du maître d\'ouvrage. Selon le projet de décret, le seuil serait fixé à −15 % du montant estimatif pour les marchés de travaux, fournitures et services hors études (Art. 44 et 144), contre −20 % à −25 % selon les catégories actuellement. Le maître d\'ouvrage peut demander des justifications au concurrent avant de décider de l\'écarter.',
      },
      {
        question: 'Qu\'est-ce qu\'une offre excessive dans les marchés publics au Maroc ?',
        answer:   'Selon le projet de décret, est réputée excessive toute offre dont le montant dépasse de plus de 15 % le montant estimatif du maître d\'ouvrage (Art. 44 et 144), contre 20 % dans le dispositif actuel. Le maître d\'ouvrage peut confier l\'examen de ces offres à une commission subalterne.',
      },
      {
        question: 'La réforme du décret n° 2-22-431 est-elle déjà applicable ?',
        answer:   'Non. Ce guide présente les modifications contenues dans un projet de décret non encore publié au Bulletin officiel. L\'applicabilité des nouvelles dispositions est conditionnée à la publication du texte définitif. En cas de divergence entre les dispositions présentées et le texte officiel publié, ce dernier prévaut.',
      },
      {
        question: 'Qui est concerné par le projet de réforme du décret n° 2-22-431 ?',
        answer:   'Le projet concerne l\'ensemble des acteurs de la commande publique : les administrations de l\'État, les collectivités territoriales, les établissements publics, ainsi que les opérateurs économiques candidats aux marchés publics — notamment les architectes, bureaux d\'études, entreprises de travaux, prestataires de services, TPE, PME, coopératives et auto-entrepreneurs.',
      },
      {
        question: 'Pourquoi le projet insiste-t-il sur les marchés de gardiennage, de nettoyage et d\'entretien des espaces verts ?',
        answer:   'Ces secteurs font appel à une main-d\'œuvre importante et ont été marqués par des pratiques de bradage des prix au détriment des obligations sociales des prestataires. Le projet impose au maître d\'ouvrage d\'intégrer le SMIG et les cotisations sociales obligatoires dans le coût estimatif (Art. 6), et prévoit que l\'offre la plus avantageuse est celle qui propose le taux de majoration le plus élevé pour la main-d\'œuvre (Art. 43).',
      },
      {
        question: 'Quels avantages le projet prévoit-il pour les TPE, PME et coopératives dans les marchés publics ?',
        answer:   'Le projet prévoit plusieurs mesures : le relèvement du seuil des bons de commande à 800 000 DH TTC facilite l\'accès à de petites commandes ; le relèvement du seuil de l\'appel d\'offres ouvert simplifié à 1 500 000 DH HT ouvre l\'accès à une procédure allégée ; et les marchés réservés aux TPE, PME, coopératives, unions de coopératives et auto-entrepreneurs (Art. 148) constituent une opportunité directe d\'accès à la commande publique.',
      },
    ],

    faq_ar: [
      {
        question: 'هل تتغير عتبة سندات الطلب في إطار إصلاح الصفقات العمومية بالمغرب؟',
        answer:   'وفق مشروع المرسوم، ترتفع العتبة السنوية للأشغال المُنجزة بواسطة سندات الطلب من 500.000 درهم ش.ج إلى 800.000 درهم ش.ج، لكل آمر بالصرف أو آمر فرعي أو شخص مفوض، في إطار سنة مالية واحدة (م. 91). ويظل هذا الرفع رهيناً بنشر النص الرسمي النهائي في الجريدة الرسمية.',
      },
      {
        question: 'ما هي العتبة الجديدة لطلب العروض المفتوح المبسط وفق المشروع؟',
        answer:   'يُقترح في المشروع رفع عتبة طلب العروض المفتوح المبسط من 1.000.000 درهم خ.ر إلى 1.500.000 درهم خ.ر (م. 19)، مما يُتيح لعدد أكبر من الصفقات الاستفادة من هذه المسطرة المبسطة.',
      },
      {
        question: 'ما المقصود بالعرض المنخفض بكيفية غير عادية في الصفقات العمومية بالمغرب؟',
        answer:   'العرض المنخفض بكيفية غير عادية هو كل عرض يقل ثمنه بصورة مهمة عن المبلغ التقديري لكلفة الأعمال لدى صاحب المشروع. ووفق المشروع، تُحدَّد العتبة في −15 % من المبلغ التقديري لصفقات الأشغال والتوريدات والخدمات غير المتعلقة بالدراسات (م. 44 و144)، عوضاً عن −20 % إلى −25 % حالياً.',
      },
      {
        question: 'ما المقصود بالعرض المفرط في الصفقات العمومية؟',
        answer:   'وفق المشروع، يُعدّ مفرطاً كل عرض يتجاوز بأكثر من 15 % المبلغ التقديري لكلفة الأعمال لدى صاحب المشروع (م. 44 و144)، عوضاً عن 20 % في النص الحالي. ويمكن لصاحب المشروع إحالة دراسة هذه العروض إلى لجنة فرعية.',
      },
      {
        question: 'هل تعديلات المرسوم رقم 2.22.431 سارية المفعول الآن؟',
        answer:   'لا. يستند هذا الدليل إلى مشروع مرسوم تعديلي لم يُنشر بعد في الجريدة الرسمية. تطبيق الأحكام الجديدة مشروط بنشر النص الرسمي النهائي، والذي يسمو على أي معلومة أخرى في حالة التعارض.',
      },
      {
        question: 'من يعنيه مشروع تعديل المرسوم رقم 2.22.431؟',
        answer:   'يمسّ المشروع جميع أطراف منظومة الطلبيات العمومية : إدارات الدولة والجماعات الترابية والمؤسسات العامة، وكذلك المتعاملين الاقتصاديين المترشحين للصفقات العمومية، لا سيما المهندسين المعماريين ومكاتب الدراسات ومقاولات الأشغال ومقدمي الخدمات والمقاولات الصغيرة والمتوسطة والتعاونيات والمقاولين الذاتيين.',
      },
      {
        question: 'لماذا يُولي المشروع اهتماماً خاصاً لصفقات الحراسة والنظافة وصيانة المساحات الخضراء؟',
        answer:   'تتطلب هذه القطاعات يداً عاملة كثيفة وشهدت ظاهرة كسر الأسعار على حساب الالتزامات الاجتماعية للمقاولات. يُلزم المشروع صاحب المشروع بإدماج الحد الأدنى القانوني للأجور والمساهمات الاجتماعية الإلزامية في تقدير الكلفة (م. 6)، ويجعل العرض الأكثر أفضلية هو الذي يقترح نسبة الزيادة الأعلى لحماية كلفة اليد العاملة (م. 43).',
      },
      {
        question: 'ما المزايا التي يُقررها المشروع للمقاولات الصغيرة والمتوسطة والتعاونيات والمقاولين الذاتيين؟',
        answer:   'يتضمن المشروع عدة تدابير : رفع عتبة سندات الطلب إلى 800.000 درهم ش.ج يُيسّر الوصول إلى الطلبيات الصغيرة ؛ ورفع عتبة طلب العروض المبسط إلى 1.500.000 درهم خ.ر يفتح المجال أمام مسطرة مخففة ؛ فيما تُتيح الصفقات المخصصة للمقاولات الصغيرة جداً والمتوسطة والتعاونيات واتحاداتها والمقاولين الذاتيين (م. 148) ولوجاً مباشراً إلى الطلبيات العمومية.',
      },
    ],
  },
]

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Retourne un guide par son slug */
export function getIntentBySlug(slug) {
  return SEO_INTENT_PAGES.find(p => p.slug === slug) || null
}

/** Groupe les guides par catégorie (pour l'index) */
export function getIntentsByCategory() {
  const order = ['mre', 'investissement', 'travail', 'commercial', 'famille', 'civil', 'administratif', 'collectivites', 'societe']
  const grouped = {}
  for (const page of SEO_INTENT_PAGES) {
    if (!grouped[page.category]) grouped[page.category] = []
    grouped[page.category].push(page)
  }
  // Retourner dans l'ordre souhaité
  const result = {}
  for (const cat of order) {
    if (grouped[cat]) result[cat] = grouped[cat]
  }
  // Ajouter les catégories restantes
  for (const cat of Object.keys(grouped)) {
    if (!result[cat]) result[cat] = grouped[cat]
  }
  return result
}

/** Retourne les guides liés à un domaine Supabase */
export function getGuidesForDomain(domainId) {
  return SEO_INTENT_PAGES.filter(p => p.legalDomain === domainId)
}

/** Retourne les guides proches d'un guide donné */
export function getRelatedGuides(intent, max = 4) {
  if (!intent) return []
  return SEO_INTENT_PAGES.filter(p =>
    p.slug !== intent.slug &&
    (intent.relatedSlugs?.includes(p.slug) || p.category === intent.category)
  ).slice(0, max)
}
