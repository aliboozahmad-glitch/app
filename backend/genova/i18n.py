"""Server-side text for engine keys in English, Arabic and German. The engine itself only emits keys."""
from copy import deepcopy

from .genetics.data_loader import load_diseases, load_references

LANGS = ("en", "ar", "de")

T = {
    # certainty tiers
    "established": ("Established (Mendelian)", "مُثبت علمياً (قوانين مندل)", "Gesichert (Mendelsch)"),
    "population_estimate": ("Population-based estimate", "تقدير مبني على بيانات السكان", "Bevölkerungsbasierte Schätzung"),
    "statistical_estimate": ("Statistical estimate", "تقدير إحصائي", "Statistische Schätzung"),
    "uncertain_estimate": ("Uncertain estimate", "تقدير غير مؤكد", "Unsichere Schätzung"),
    "population_statistic": ("Population statistic", "إحصاء سكاني", "Bevölkerungsstatistik"),
    # methods
    "punnett_autosomal": ("Punnett square, single autosomal gene", "مربع بانيت لجين جسمي واحد", "Punnett-Quadrat, ein autosomales Gen"),
    "punnett_x_linked": ("Punnett square, X-linked gene (results per sex)", "مربع بانيت لجين مرتبط بالكروموسوم X (النتائج حسب الجنس)", "Punnett-Quadrat, X-chromosomales Gen (Ergebnisse je Geschlecht)"),
    "blood_type_exact": ("ABO + RhD cross from known genotypes", "تزاوج ABO وRhD من طرز جينية معروفة", "ABO- und RhD-Kreuzung aus bekannten Genotypen"),
    "blood_type_scenarios": ("ABO + RhD cross over every genotype compatible with the stated blood types", "تزاوج ABO وRhD لكل الطرز الجينية المتوافقة مع فصائل الدم المذكورة", "ABO- und RhD-Kreuzung über alle mit den Blutgruppen vereinbaren Genotypen"),
    "carrier_exact": ("Mendelian cross from confirmed carrier status", "تزاوج مندلي من حالة حمل مؤكدة", "Mendelsche Kreuzung aus bestätigtem Trägerstatus"),
    "carrier_conditional": ("Mendelian scenarios for each possible status of the untested parent", "سيناريوهات مندلية لكل حالة محتملة للوالد غير المفحوص", "Mendelsche Szenarien für jeden möglichen Status des nicht getesteten Elternteils"),
    "carrier_population": ("Mendelian cross weighted by validated regional carrier frequency", "تزاوج مندلي موزون بنسبة الحمل الإقليمية المعتمدة", "Mendelsche Kreuzung, gewichtet mit validierter regionaler Trägerfrequenz"),
    "mid_parental_height": ("Mid-parental target height (Tanner 1970)", "الطول المستهدف من متوسط طول الوالدين (تانر 1970)", "Elterliche Zielgröße (Tanner 1970)"),
    "qualitative_pigmentation": ("Qualitative pattern from parental pigmentation (polygenic, no percentages)", "نمط وصفي من صبغة الوالدين (متعدد الجينات، بلا نسب مئوية)", "Qualitatives Muster aus elterlicher Pigmentierung (polygen, ohne Prozentangaben)"),
    "sex_ratio_at_birth": ("Natural sex ratio at birth", "النسبة الطبيعية للجنس عند الولادة", "Natürliches Geschlechterverhältnis bei Geburt"),
    # outcomes
    "shows_trait": ("Shows the trait", "تظهر عليه الصفة", "Zeigt das Merkmal"),
    "no_trait": ("Does not show the trait", "لا تظهر عليه الصفة", "Zeigt das Merkmal nicht"),
    "carrier_no_trait": ("Carrier (does not show the trait)", "حامل (لا تظهر عليه الصفة)", "Träger (zeigt das Merkmal nicht)"),
    "no_trait_non_carrier": ("Not a carrier, does not show the trait", "غير حامل ولا تظهر عليه الصفة", "Kein Träger, zeigt das Merkmal nicht"),
    "both_expressed": ("Both alleles expressed (codominant)", "ظهور الأليلين معاً (سيادة مشتركة)", "Beide Allele ausgeprägt (kodominant)"),
    "intermediate": ("Intermediate phenotype", "صفة وسطية", "Intermediärer Phänotyp"),
    "allele_A_trait": ("Allele A phenotype", "صفة الأليل A", "Phänotyp Allel A"),
    "allele_B_trait": ("Allele B phenotype", "صفة الأليل B", "Phänotyp Allel B"),
    "affected": ("Affected", "مصاب", "Betroffen"),
    "carrier": ("Carrier", "حامل", "Träger"),
    "unaffected": ("Unaffected", "سليم", "Nicht betroffen"),
    "unaffected_non_carrier": ("Unaffected, not a carrier", "سليم وغير حامل", "Nicht betroffen, kein Träger"),
    "heterozygous_variable": ("Heterozygous: from unaffected to deficient", "متغايرة الزيجوت: من سليمة إلى ناقصة الإنزيم", "Heterozygot: von unauffällig bis defizient"),
    "male": ("Boy", "ذكر", "Junge"),
    "female": ("Girl", "أنثى", "Mädchen"),
    "target_height_cm": ("Target adult height", "الطول المتوقع عند البلوغ", "Erwachsene Zielgröße"),
    "brown": ("Brown", "بني", "Braun"), "hazel": ("Hazel", "عسلي", "Haselnuss"), "green": ("Green", "أخضر", "Grün"),
    "blue": ("Blue", "أزرق", "Blau"), "gray": ("Gray", "رمادي", "Grau"), "black": ("Black", "أسود", "Schwarz"),
    "blonde": ("Blonde", "أشقر", "Blond"), "red": ("Red", "أحمر", "Rot"),
    # groups
    "all_children": ("Each child", "كل طفل", "Jedes Kind"),
    "sons": ("Each son", "كل ابن", "Jeder Sohn"),
    "daughters": ("Each daughter", "كل ابنة", "Jede Tochter"),
    "more_often_observed": ("More often observed", "الأكثر ملاحظة", "Häufiger beobachtet"),
    "possible": ("Possible", "ممكن", "Möglich"),
    "less_common": ("Less common, still possible", "أقل شيوعاً لكنه ممكن", "Seltener, aber möglich"),
    # assumptions
    "stated_genotypes_correct": ("The entered genotypes are correct.", "الطرز الجينية المدخلة صحيحة.", "Die eingegebenen Genotypen sind korrekt."),
    "mendelian_segregation": ("Each parent passes one of their two alleles with equal probability.", "كل والد ينقل أحد أليليه باحتمال متساوٍ.", "Jeder Elternteil gibt eines seiner zwei Allele mit gleicher Wahrscheinlichkeit weiter."),
    "complete_penetrance": ("Complete penetrance: the genotype always produces the phenotype.", "نفاذية كاملة: الطراز الجيني يُظهر الصفة دائماً.", "Vollständige Penetranz: Der Genotyp führt immer zum Phänotyp."),
    "no_new_mutation": ("No new (de novo) mutation occurs.", "لا تحدث طفرة جديدة.", "Es tritt keine Neumutation auf."),
    "standard_abo_rh_model": ("Standard ABO (A, B, O alleles) and RhD (D, d) model.", "النموذج القياسي لـ ABO (الأليلات A وB وO) وRhD (D وd).", "Standardmodell ABO (Allele A, B, O) und RhD (D, d)."),
    "phenotype_genotype_unknown": ("Only blood types were given, so each parent's exact genotype is unknown; results are shown as ranges across all compatible genotypes.", "أُدخلت فصائل الدم فقط، لذا الطراز الجيني الدقيق غير معروف؛ النتائج معروضة كنطاقات لكل الطرز المتوافقة.", "Nur Blutgruppen angegeben, daher ist der genaue Genotyp unbekannt; Ergebnisse als Spannen über alle vereinbaren Genotypen."),
    "stated_status_correct": ("The entered carrier/affected statuses are correct (ideally from a lab report).", "حالات الحمل/الإصابة المدخلة صحيحة (ويفضل من تقرير مختبر).", "Die eingegebenen Träger-/Betroffenenstatus sind korrekt (idealerweise laut Laborbefund)."),
    "unknown_parent_unaffected": ("A parent with unknown status is assumed to be unaffected.", "يُفترض أن الوالد غير المعروفة حالته غير مصاب.", "Ein Elternteil mit unbekanntem Status gilt als nicht betroffen."),
    "regional_frequency_applies": ("The selected region's carrier frequency applies to the untested parent.", "نسبة الحمل للمنطقة المختارة تنطبق على الوالد غير المفحوص.", "Die Trägerfrequenz der gewählten Region gilt für den nicht getesteten Elternteil."),
    "natural_sex_ratio": ("About 105 boys are born per 100 girls in populations without sex-selective practices.", "يولد نحو 105 ذكور لكل 100 أنثى في المجتمعات دون ممارسات انتقائية.", "In Bevölkerungen ohne geschlechtsselektive Praktiken werden etwa 105 Jungen pro 100 Mädchen geboren."),
    "adult_height_both_parents": ("Both heights are measured adult heights of the biological parents.", "الطولان هما طولا الوالدين البيولوجيين البالغين.", "Beide Werte sind gemessene Erwachsenengrößen der leiblichen Eltern."),
    "typical_growth": ("Typical growth and nutrition; no growth disorder.", "نمو وتغذية طبيعيان دون اضطراب نمو.", "Normales Wachstum und Ernährung, keine Wachstumsstörung."),
    "polygenic_model": ("Pigmentation is controlled by many genes (e.g. OCA2/HERC2 for eyes, MC1R for red hair).", "الصبغة تتحكم بها جينات متعددة (مثل OCA2/HERC2 للعين وMC1R للشعر الأحمر).", "Pigmentierung wird von vielen Genen gesteuert (z. B. OCA2/HERC2 für Augen, MC1R für rote Haare)."),
    # limitations
    "not_diagnosis": ("Educational information only. This is not a medical diagnosis. Please consult a doctor or genetic counsellor.", "معلومات تثقيفية فقط وليست تشخيصاً طبياً. يرجى استشارة طبيب أو مستشار وراثي.", "Nur zur Information. Dies ist keine medizinische Diagnose. Bitte wenden Sie sich an eine Ärztin, einen Arzt oder eine genetische Beratung."),
    "x_results_per_sex": ("X-linked results are given separately for sons and daughters.", "نتائج الجينات المرتبطة بـ X معروضة منفصلة للأبناء والبنات.", "X-chromosomale Ergebnisse werden getrennt für Söhne und Töchter angegeben."),
    "abo_rare_exceptions": ("Rare exceptions are not modelled (Bombay phenotype, cis-AB, weak D variants, chimerism).", "الاستثناءات النادرة غير مشمولة (نمط بومباي، cis-AB، متغيرات D الضعيفة، الخيمرية).", "Seltene Ausnahmen sind nicht modelliert (Bombay-Phänotyp, cis-AB, schwache D-Varianten, Chimärismus)."),
    "negative_test_residual": ("A negative carrier test lowers but does not remove the risk; residual risk depends on the test and is not quantified here.", "الفحص السلبي يقلل الخطر ولا يلغيه؛ الخطر المتبقي يعتمد على نوع الفحص ولا يُحسب هنا.", "Ein negativer Trägertest senkt das Risiko, beseitigt es aber nicht; das Restrisiko hängt vom Test ab und wird hier nicht berechnet."),
    "region_data_unvalidated": ("No validated carrier frequency exists yet for this region, so no combined population risk is shown. Carrier testing of the untested parent gives an exact answer.", "لا توجد بعد نسبة حمل معتمدة لهذه المنطقة، لذلك لا يُعرض خطر سكاني مُجمَّع. فحص الوالد غير المفحوص يعطي إجابة دقيقة.", "Für diese Region gibt es noch keine validierte Trägerfrequenz, daher wird kein Gesamtrisiko angezeigt. Ein Trägertest des ungetesteten Elternteils liefert eine genaue Antwort."),
    "sex_ratio_population": ("This is a population average. It does not predict the sex of a specific pregnancy.", "هذا متوسط سكاني ولا يتنبأ بجنس حمل بعينه.", "Dies ist ein Bevölkerungsdurchschnitt und sagt das Geschlecht einer bestimmten Schwangerschaft nicht voraus."),
    "family_pattern_not_predictive": ("Relatives' birth order or family patterns have no proven predictive value and are not used.", "ترتيب ولادة الأقارب أو أنماط العائلة ليس لها قيمة تنبؤية مثبتة ولا تُستخدم.", "Geburtsreihenfolge oder Familienmuster haben keinen nachgewiesenen Vorhersagewert und werden nicht verwendet."),
    "height_environment": ("Nutrition, health and environment also influence height.", "التغذية والصحة والبيئة تؤثر أيضاً في الطول.", "Ernährung, Gesundheit und Umwelt beeinflussen ebenfalls die Körpergröße."),
    "height_range_approx": ("The ±8.5 cm range is an approximate target range; some children fall outside it.", "النطاق ±8.5 سم تقريبي، وقد يقع بعض الأطفال خارجه.", "Die Spanne von ±8,5 cm ist ungefähr; manche Kinder liegen außerhalb."),
    "polygenic_no_precise": ("No reliable percentages exist for these traits, so none are shown.", "لا توجد نسب مئوية موثوقة لهذه الصفات، لذلك لا تُعرض.", "Für diese Merkmale gibt es keine verlässlichen Prozentwerte, daher werden keine angezeigt."),
    "any_outcome_possible": ("Uncommon outcomes still happen, e.g. blue-eyed parents can have a brown-eyed child.", "النتائج غير الشائعة تحدث، فمثلاً قد يُنجب والدان بعيون زرقاء طفلاً بعيون بنية.", "Auch seltene Ergebnisse kommen vor, z. B. können blauäugige Eltern ein braunäugiges Kind haben."),
    "severity_varies": ("Severity varies between affected people.", "تختلف شدة المرض بين المصابين.", "Der Schweregrad ist bei Betroffenen unterschiedlich."),
    "hb_coinheritance": ("Combinations with other haemoglobin variants (e.g. HbS with β-thalassaemia) change the outcome and need specialist assessment.", "اجتماع متغيرات هيموغلوبين أخرى (مثل HbS مع الثلاسيميا بيتا) يغير النتيجة ويحتاج تقييماً متخصصاً.", "Kombinationen mit anderen Hämoglobinvarianten (z. B. HbS mit Beta-Thalassämie) verändern das Ergebnis und erfordern fachärztliche Beurteilung."),
    "g6pd_female_variable": ("Heterozygous girls range from normal enzyme activity to full deficiency (X-inactivation), so no single risk is given for daughters.", "البنات متغايرات الزيجوت يتراوحن بين نشاط إنزيم طبيعي ونقص كامل، لذا لا يُعطى خطر واحد للبنات.", "Heterozygote Mädchen reichen von normaler Enzymaktivität bis zum vollen Mangel (X-Inaktivierung), daher kein einzelnes Risiko für Töchter."),
    "g6pd_triggers": ("Symptoms usually appear only after triggers such as fava beans, some medicines or infections.", "تظهر الأعراض عادة بعد محفزات مثل الفول وبعض الأدوية أو العدوى.", "Symptome treten meist erst nach Auslösern wie Favabohnen, bestimmten Medikamenten oder Infektionen auf."),
    "cf_panel_sensitivity": ("Carrier panels detect a share of CFTR variants that depends on ancestry.", "لوحات الفحص تكشف نسبة من متغيرات CFTR تعتمد على الأصل العرقي.", "Trägerpanels erkennen einen von der Herkunft abhängigen Anteil der CFTR-Varianten."),
    "de_novo_possible": ("About one third of cases arise from a new mutation without family history.", "نحو ثلث الحالات تنتج عن طفرة جديدة دون تاريخ عائلي.", "Etwa ein Drittel der Fälle entsteht durch Neumutation ohne Familienvorgeschichte."),
    "carrier_female_symptoms": ("Some carrier women have mild bleeding symptoms.", "بعض النساء الحاملات لديهن أعراض نزف خفيفة.", "Manche Überträgerinnen haben leichte Blutungssymptome."),
    "gonadal_mosaicism": ("A mother with a negative blood test can still carry the variant in her egg cells (germline mosaicism).", "قد تحمل الأم المتغير في بويضاتها رغم فحص دم سلبي (فسيفسائية جنسية).", "Eine Mutter mit negativem Bluttest kann die Variante dennoch in Eizellen tragen (Keimbahnmosaik)."),
    "sma_silent_carrier": ("Some carriers (2 SMN1 copies on one chromosome) are missed by standard tests.", "بعض الحاملين (نسختان من SMN1 على كروموسوم واحد) لا تكشفهم الفحوص القياسية.", "Manche Träger (2 SMN1-Kopien auf einem Chromosom) werden von Standardtests nicht erkannt."),
    "newborn_screening_pku": ("Newborn screening and early diet lead to very good outcomes.", "فحص حديثي الولادة والحمية المبكرة يؤديان إلى نتائج جيدة جداً.", "Neugeborenen-Screening und frühe Diät führen zu sehr guten Ergebnissen."),
    "ancestry_specific": ("Carrier frequency differs strongly by ancestry.", "تختلف نسبة الحمل كثيراً حسب الأصل.", "Die Trägerfrequenz unterscheidet sich stark nach Herkunft."),
    "trait_not_disease": ("This is a trait, not a disease.", "هذه صفة وليست مرضاً.", "Dies ist ein Merkmal, keine Krankheit."),
    # inheritance modes
    "autosomal_dominant": ("Autosomal dominant", "جسمي سائد", "Autosomal-dominant"),
    "autosomal_recessive": ("Autosomal recessive", "جسمي متنحٍ", "Autosomal-rezessiv"),
    "codominant": ("Codominant", "سيادة مشتركة", "Kodominant"),
    "incomplete_dominance": ("Incomplete dominance", "سيادة غير تامة", "Unvollständige Dominanz"),
    "x_linked_recessive": ("X-linked recessive", "متنحٍ مرتبط بالكروموسوم X", "X-chromosomal-rezessiv"),
    "x_linked_dominant": ("X-linked dominant", "سائد مرتبط بالكروموسوم X", "X-chromosomal-dominant"),
    "sperm_x_or_y": ("A baby's sex is set at conception by whether the father's sperm carries an X or a Y chromosome.", "يتحدد جنس الجنين عند الإخصاب بحسب حمل الحيوان المنوي للأب كروموسوم X أو Y.", "Das Geschlecht wird bei der Befruchtung dadurch festgelegt, ob das Spermium des Vaters ein X- oder Y-Chromosom trägt."),
    # regions
    "gulf": ("Gulf (GCC)", "دول الخليج", "Golfstaaten"),
    "middle_east_north_africa": ("Middle East & North Africa", "الشرق الأوسط وشمال أفريقيا", "Naher Osten & Nordafrika"),
    "europe": ("Europe", "أوروبا", "Europa"),
    "sub_saharan_africa": ("Sub-Saharan Africa", "أفريقيا جنوب الصحراء", "Subsahara-Afrika"),
    "south_asia": ("South Asia", "جنوب آسيا", "Südasien"),
    "east_asia": ("East Asia", "شرق آسيا", "Ostasien"),
    "americas": ("Americas", "الأمريكتان", "Amerika"),
    "global": ("Global average", "المتوسط العالمي", "Globaler Durchschnitt"),
    # errors
    "invalid_genotype": ("Invalid genotype for this inheritance mode.", "طراز جيني غير صالح لنمط الوراثة هذا.", "Ungültiger Genotyp für diesen Erbgang."),
    "invalid_mode": ("Unknown inheritance mode.", "نمط وراثة غير معروف.", "Unbekannter Erbgang."),
    "invalid_abo": ("Invalid ABO blood group.", "فصيلة ABO غير صالحة.", "Ungültige ABO-Blutgruppe."),
    "invalid_rh": ("Invalid Rh factor.", "عامل Rh غير صالح.", "Ungültiger Rhesusfaktor."),
    "unknown_disease": ("Unknown condition.", "حالة غير معروفة.", "Unbekannte Erkrankung."),
    "invalid_status": ("Invalid status for this condition.", "حالة غير صالحة لهذا المرض.", "Ungültiger Status für diese Erkrankung."),
    "height_out_of_range": ("Heights must be between 120 and 230 cm.", "يجب أن يكون الطول بين 120 و230 سم.", "Größen müssen zwischen 120 und 230 cm liegen."),
    "invalid_trait": ("Unknown trait.", "صفة غير معروفة.", "Unbekanntes Merkmal."),
    "invalid_trait_value": ("Invalid value for this trait.", "قيمة غير صالحة لهذه الصفة.", "Ungültiger Wert für dieses Merkmal."),
}


def t(key: str, lang: str) -> str:
    entry = T.get(key)
    return entry[LANGS.index(lang)] if entry else key


def localize_result(result: dict, lang: str) -> dict:
    r = deepcopy(result)
    refs = load_references()
    diseases = load_diseases()
    r["lang"] = lang
    r["certainty_label"] = t(r["certainty"], lang)
    r["method_label"] = t(r["method"], lang)
    for o in r["outcomes"]:
        o["label"] = o["key"] if o["kind"] in ("genotype", "blood_type") else t(o["key"], lang)
        o["group_label"] = t(o["group"], lang)
    r["assumptions"] = [{"key": k, "text": t(k, lang)} for k in r["assumptions"]]
    r["limitations"] = [{"key": k, "text": t(k, lang)} for k in r["limitations"]]
    r["references"] = [refs[k] for k in dict.fromkeys(r["references"]) if k in refs]
    d = r.get("details", {})
    for s in d.get("scenarios", []):
        for o in s["outcomes"]:
            o["label"] = t(o["key"], lang)
            o["group_label"] = t(o["group"], lang)
    if "disease" in d:
        dis = diseases[d["disease"]]
        d["disease_name"] = dis["names"][lang]
        d["inheritance_label"] = t(dis["inheritance"], lang)
    if "mechanism" in d:
        d["mechanism_text"] = t(d["mechanism"], lang)
    if r["inputs"].get("mode"):
        d["mode_label"] = t(r["inputs"]["mode"], lang)
    if r["inputs"].get("region"):
        d["region_label"] = t(r["inputs"]["region"], lang)
    return r
