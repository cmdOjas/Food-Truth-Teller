"""
Nutrition knowledge base entries.

These are curated, evidence-based nutrition facts drawn from:
  - WHO dietary guidelines
  - USDA FoodData Central
  - NIH nutritional recommendations
  - FDA food labeling guidance
  - FSSAI / ICMR / NIN India guidelines
  - PubMed nutrition research

Each entry is a plain-English paragraph that gets embedded into
the FAISS vector index for RAG retrieval.
"""

KNOWLEDGE_ENTRIES: list[str] = [

    # ── Sugar ────────────────────────────────────────────────────────────────
    "WHO recommends that free sugars should make up less than 10% of total energy intake. "
    "A further reduction to below 5% (roughly 25g or 6 teaspoons per day) provides additional health benefits. "
    "Excessive sugar intake is linked to obesity, type 2 diabetes, dental caries, and non-alcoholic fatty liver disease.",

    "High-fructose corn syrup (HFCS) is an added sugar found in many processed foods and beverages. "
    "Regular consumption is associated with increased triglycerides, insulin resistance, and liver fat accumulation. "
    "Individuals with diabetes, obesity, or fatty liver should minimize HFCS intake.",

    "Natural sugars found in whole fruits and dairy (fructose in fruit, lactose in milk) are metabolised differently "
    "from added sugars due to the presence of fibre, protein, and micronutrients that slow absorption. "
    "These are generally safe in moderate whole-food quantities.",

    "For diabetics (Type 1 and Type 2), the glycaemic index (GI) and glycaemic load (GL) of foods are important. "
    "Foods with GI > 70 cause rapid blood glucose spikes. Choosing low-GI foods (GI < 55) helps manage blood sugar. "
    "High-sugar products should be avoided or consumed in very small portions by diabetics.",

    # ── Sodium / Salt ────────────────────────────────────────────────────────
    "WHO recommends limiting sodium intake to less than 2000 mg per day (equivalent to 5g of salt). "
    "High sodium intake raises blood pressure and is a major risk factor for cardiovascular disease and stroke. "
    "Most processed, packaged, and fast foods are high in sodium.",

    "For hypertension (high blood pressure), reducing sodium to 1500 mg/day may provide additional benefit. "
    "The DASH diet (Dietary Approaches to Stop Hypertension) recommends avoiding processed meats, canned soups, "
    "pickled foods, and snacks with more than 200 mg sodium per serving.",

    "For kidney disease patients, sodium restriction to 1500-2000 mg/day is important to reduce fluid retention "
    "and protect kidney function. Potassium and phosphorus may also need to be restricted depending on disease stage.",

    # ── Saturated Fat & Trans Fat ────────────────────────────────────────────
    "WHO recommends that saturated fat should comprise less than 10% of total energy intake, and trans fat "
    "less than 1%. High saturated fat raises LDL (bad) cholesterol, increasing risk of heart disease. "
    "Main sources: fatty meats, butter, cheese, palm oil, coconut oil.",

    "Trans fats (partially hydrogenated oils) are the most harmful type of dietary fat. They raise LDL cholesterol "
    "while lowering HDL (good) cholesterol. Many countries ban trans fats. Products listing 'partially hydrogenated' "
    "oils contain trans fats even if labeled '0g trans fat' (rounding allows <0.5g to be shown as 0).",

    "For heart disease patients, saturated fat should be limited to less than 7% of calories and trans fat "
    "should be completely avoided. Replacing saturated fats with unsaturated fats (olive oil, nuts, avocado) "
    "reduces cardiovascular risk.",

    # ── Additives & Preservatives ────────────────────────────────────────────
    "Sodium benzoate (E211) is a common preservative in acidic foods like soft drinks and salad dressings. "
    "When combined with ascorbic acid (Vitamin C), it can form benzene, a known carcinogen. "
    "Concerns exist about hyperactivity in children when combined with certain artificial colours.",

    "BHA (E320) and BHT (E321) are synthetic antioxidant preservatives used in fats and oils. "
    "BHA is listed as a possible human carcinogen by IARC. Countries including Japan have restricted BHA use. "
    "These should be minimised especially for children.",

    "Sodium nitrate (E251) and sodium nitrite (E250) are preservatives in processed meats (bacon, ham, sausages). "
    "They can form nitrosamines during cooking at high temperatures, which are linked to colorectal cancer. "
    "WHO's IARC classifies processed meats as Group 1 carcinogens (definitely causes cancer).",

    "TBHQ (tert-butylhydroquinone, E319) is a preservative used in fast foods and processed snacks. "
    "Long-term animal studies show potential immune and neurological effects at high doses. "
    "It is banned in Japan and restricted in the EU.",

    "Carrageenan (E407) is a thickener derived from red seaweed used in dairy alternatives and deli meats. "
    "Some research links degraded carrageenan (poligeenan) to intestinal inflammation. "
    "Individuals with IBS or inflammatory bowel conditions may wish to avoid it.",

    # ── Artificial Colours ───────────────────────────────────────────────────
    "Tartrazine (E102 / Yellow 5) is an artificial yellow dye found in sodas, sweets, and chips. "
    "It is associated with allergic reactions (especially in aspirin-sensitive individuals) and hyperactivity in children. "
    "The EU requires a warning label on products containing tartrazine.",

    "Sunset Yellow (E110 / Yellow 6), Carmoisine (E122 / Red 3), Allura Red (E129 / Red 40), and "
    "Brilliant Blue (E133) are artificial food dyes linked to hyperactivity in children (the 'Southampton Six'). "
    "EU mandates advisory labels; the FDA has reviewed but not banned them in the US.",

    "Caramel colour (E150) especially Class IV (sulfite ammonia caramel) used in colas and dark sauces "
    "may contain 4-methylimidazole (4-MEI), a possible carcinogen identified by IARC. "
    "California's Prop 65 limits require warnings above certain 4-MEI levels.",

    # ── Artificial Sweeteners ────────────────────────────────────────────────
    "Aspartame (E951) is 200x sweeter than sugar, used in diet drinks, chewing gum, and sugar-free products. "
    "IARC classified aspartame as 'possibly carcinogenic to humans' (Group 2B) in 2023 based on limited evidence. "
    "The ADI (Acceptable Daily Intake) is 40 mg/kg body weight. Individuals with phenylketonuria (PKU) "
    "must avoid aspartame as it contains phenylalanine.",

    "Sucralose (E955) is 600x sweeter than sugar. Some studies suggest it may alter gut microbiota composition "
    "and reduce the beneficial effects of the microbiome. It may produce chlorinated compounds when heated to high temperatures. "
    "Generally considered safe by FDA; the ADI is 5 mg/kg body weight.",

    "Stevia (Rebaudioside A, E960) is a natural plant-derived sweetener with zero calories. "
    "It does not raise blood sugar and is safe for diabetics. It may have mild antihypertensive effects. "
    "Generally well-tolerated; some people experience a bitter aftertaste.",

    "Saccharin (E954) is the oldest artificial sweetener. Earlier concerns about bladder cancer from animal studies "
    "were not confirmed in humans; it is now considered safe at normal intake levels. ADI is 5 mg/kg body weight. "
    "Not recommended for pregnant women due to limited safety data in pregnancy.",

    "Acesulfame potassium (Ace-K, E950) is 200x sweeter than sugar, commonly combined with other sweeteners. "
    "Some research raises concerns about effects on insulin response and gut bacteria, though the FDA considers it safe. "
    "ADI is 15 mg/kg body weight.",

    # ── Allergens ────────────────────────────────────────────────────────────
    "The nine major food allergens recognised by the FDA are: milk, eggs, fish, shellfish, tree nuts, peanuts, "
    "wheat, soybeans, and sesame. These account for 90% of all food allergic reactions. "
    "Even trace amounts can trigger severe reactions in sensitised individuals, including anaphylaxis.",

    "Gluten is a protein found in wheat, barley, rye, and related grains. For individuals with celiac disease, "
    "gluten triggers an autoimmune response that damages the small intestine lining. "
    "Even 20 mg/day of gluten can cause intestinal damage in celiac patients. "
    "Products must be certified gluten-free (< 20 ppm gluten) for safe consumption.",

    "Lactose intolerance is the inability to digest lactose (milk sugar) due to insufficient lactase enzyme. "
    "Symptoms include bloating, gas, diarrhoea after consuming dairy. It affects up to 70% of the global adult population. "
    "Fermented dairy (yoghurt, hard cheese) is often better tolerated due to lower lactose content.",

    "Peanut allergy is one of the most common and severe food allergies. It is an IgE-mediated reaction "
    "that can cause anaphylaxis. Cross-contamination is a major risk. Individuals with peanut allergy should "
    "also be cautious with tree nuts due to potential cross-reactivity.",

    "Soy allergy is common, especially in infants and children. Soy is found in many processed foods including "
    "edamame, tofu, tempeh, miso, soy milk, and as a filler in meat products. "
    "Those with soy allergy should also check for lecithin (often soy-derived) and hydrolysed vegetable protein.",

    # ── Processing Level (NOVA) ──────────────────────────────────────────────
    "The NOVA food classification system categorises foods by degree of processing. "
    "Group 1: Unprocessed/minimally processed foods (fresh fruits, vegetables, meat, eggs). "
    "Group 2: Processed culinary ingredients (oil, flour, sugar). "
    "Group 3: Processed foods (cheese, canned fish, cured meats). "
    "Group 4: Ultra-processed foods (soft drinks, packaged snacks, reconstituted meat products). "
    "Higher NOVA groups are associated with higher risk of obesity, diabetes, and cardiovascular disease.",

    "Ultra-processed foods (NOVA Group 4) typically contain additives not used in home cooking: "
    "emulsifiers, flavour enhancers, colours, sweeteners, humectants. "
    "Studies show ultra-processed food consumption is independently associated with "
    "increased all-cause mortality, cancer risk, and cardiovascular disease.",

    # ── Fibre ────────────────────────────────────────────────────────────────
    "Dietary fibre recommendations: Adults should consume 25-38g of fibre per day (WHO/NIH). "
    "Fibre reduces risk of colorectal cancer, improves gut microbiome diversity, lowers LDL cholesterol, "
    "slows glucose absorption (beneficial for diabetics), and promotes satiety for weight management. "
    "Soluble fibre (oats, beans, fruits) is especially beneficial for cholesterol and blood sugar control.",

    # ── Protein ──────────────────────────────────────────────────────────────
    "Protein requirements: The RDA is 0.8g per kg body weight for sedentary adults. "
    "For muscle gain/athletes: 1.6-2.2g/kg/day. For weight loss: 1.2-1.6g/kg/day (higher protein preserves muscle). "
    "For kidney disease patients: protein may need to be restricted to 0.6-0.8g/kg/day to reduce kidney strain. "
    "Complete protein sources (containing all essential amino acids): meat, fish, eggs, dairy, soy, quinoa.",

    # ── Vitamins & Minerals ──────────────────────────────────────────────────
    "Iron deficiency is the most common nutritional deficiency worldwide, especially in women of reproductive age. "
    "Haem iron (from meat) is absorbed 2-3x more efficiently than non-haem iron (plant-based). "
    "Vitamin C enhances non-haem iron absorption. Calcium and tannins (tea, coffee) inhibit iron absorption. "
    "Recommended daily intake: 8 mg/day (men), 18 mg/day (premenopausal women), 27 mg/day (pregnant).",

    "Calcium is critical for bone health, nerve function, and muscle contraction. "
    "Recommended daily intake: 1000-1200 mg/day for adults. Deficiency over time leads to osteoporosis. "
    "Primary sources: dairy, fortified plant milks, tofu (made with calcium sulfate), leafy greens (kale, bok choy). "
    "Vitamin D is essential for calcium absorption.",

    "Vitamin D deficiency is widespread (> 1 billion people globally). It is essential for calcium absorption, "
    "immune function, and bone health. Deficiency is linked to increased risk of depression, autoimmune disease, "
    "and poor immune response. Food sources are limited (fatty fish, fortified foods, egg yolks). "
    "Supplementation is often recommended, especially in low-sunlight regions.",

    # ── Disease-Specific Guidelines ──────────────────────────────────────────
    "Dietary guidelines for Type 2 Diabetes: Limit refined carbohydrates, added sugars, and high-GI foods. "
    "Increase dietary fibre (at least 25-38g/day). Limit saturated fat (<7% of calories). "
    "Choose lean proteins. Moderate alcohol consumption. Monitor total caloric intake to achieve/maintain healthy weight. "
    "The Mediterranean diet and DASH diet have strong evidence for improving glycaemic control.",

    "Dietary guidelines for hypertension: Follow the DASH diet. Limit sodium to <1500-2000 mg/day. "
    "Increase potassium (bananas, sweet potatoes, spinach). Limit alcohol. Reduce saturated fat. "
    "Increase fruits, vegetables, and whole grains. Reduce processed and packaged foods.",

    "Dietary guidelines for heart disease / cardiovascular risk: "
    "Reduce saturated fat (<7% of calories), eliminate trans fats. Increase omega-3 fatty acids (fatty fish, flaxseed). "
    "Limit dietary cholesterol (<200 mg/day for those with risk). Increase soluble fibre (oats, psyllium, legumes). "
    "Moderate alcohol (if consumed). Reduce sodium. Achieve and maintain healthy weight.",

    "Dietary guidelines for kidney disease (CKD): "
    "Restrict sodium (< 1500-2000 mg/day), potassium (depending on serum levels), and phosphorus. "
    "Protein restriction may be recommended (0.6-0.8g/kg/day for non-dialysis patients). "
    "Limit high-potassium foods (bananas, tomatoes, potatoes, oranges) and high-phosphorus foods "
    "(dairy, nuts, seeds, colas with phosphoric acid) if lab values indicate elevation.",

    "Dietary guidelines for PCOS (Polycystic Ovary Syndrome): "
    "A low-GI diet helps manage insulin resistance common in PCOS. "
    "Limit refined carbohydrates, added sugars, and high-GI foods. "
    "Increase fibre, lean protein, and anti-inflammatory foods (omega-3s, colourful vegetables). "
    "Dairy and highly processed foods may worsen hormonal imbalances in some individuals with PCOS.",

    "Dietary guidelines for IBS (Irritable Bowel Syndrome): "
    "The low-FODMAP diet (low fermentable oligosaccharides, disaccharides, monosaccharides, polyols) "
    "is effective for IBS management. Common triggers: wheat, lactose, fructose, sorbitol, and xylitol. "
    "High-fibre foods may worsen symptoms in some; soluble fibre is generally better tolerated than insoluble. "
    "Artificial sweeteners (sorbitol, mannitol, xylitol) are often triggers.",

    "Dietary guidelines for pregnancy: "
    "Increase folic acid (400-800 mcg/day to prevent neural tube defects), iron (27 mg/day), calcium (1000 mg/day), "
    "iodine, and DHA omega-3. Avoid high-mercury fish (shark, swordfish, king mackerel), raw/undercooked meat, "
    "unpasteurised dairy, excess caffeine (< 200 mg/day). Avoid alcohol completely.",

    "Dietary guidelines for obesity / weight management: "
    "Create a sustainable caloric deficit of 500-750 kcal/day for gradual weight loss (0.5-1 kg/week). "
    "High protein (1.2-1.6g/kg) preserves muscle mass during weight loss. "
    "High fibre (25-38g/day) promotes satiety. Limit ultra-processed, high-calorie-density foods. "
    "The Mediterranean, DASH, and low-GI diets all show evidence for weight management.",

    "Dietary guidelines for fatty liver disease (NAFLD): "
    "Reduce total caloric intake and achieve healthy weight loss (5-10% body weight reduction improves liver fat). "
    "Eliminate alcohol and added sugars/fructose (especially HFCS). "
    "Increase omega-3 fatty acids, antioxidant-rich vegetables, and fibre. "
    "Limit saturated fat and refined carbohydrates. Coffee consumption (filtered) is associated with reduced NAFLD risk.",

    "Celiac disease requires strict lifelong avoidance of gluten (wheat, barley, rye, triticale, spelt, kamut). "
    "Cross-contamination in food processing is a major risk. Oats are naturally gluten-free but are often "
    "contaminated; only certified gluten-free oats are safe. Recovery of intestinal villi occurs on a strict "
    "gluten-free diet over months to years.",

    "Lactose intolerance management: Limit lactose-containing dairy (milk, soft cheese, ice cream). "
    "Hard aged cheeses (cheddar, parmesan) and fermented yoghurt are often well-tolerated due to lower lactose. "
    "Lactase enzyme supplements can be taken before consuming dairy. Calcium intake should be maintained through "
    "fortified plant milks, leafy greens, and tofu.",

    # ── Indian Dietary Guidelines (ICMR/NIN) ─────────────────────────────────
    "ICMR-NIN (National Institute of Nutrition, India) dietary guidelines recommend: "
    "Adults should eat at least 5 servings of fruits and vegetables daily. "
    "Whole grains (wheat, millets, brown rice) should form the base of the diet. "
    "Limit salt to 5g/day. Limit refined oils to 3-4 teaspoons/day. "
    "Pulses and legumes are recommended daily for protein and fibre.",

    "FSSAI (India) regulations require labelling of added sugars, total fat, saturated fat, trans fat, and sodium. "
    "The Front of Pack Nutrition Label (FoPNL) system helps consumers identify high-fat, sugar, and salt (HFSS) foods. "
    "Products with per-serve energy > 200 kcal are classified as high-energy. "
    "The traffic light system shows red/orange/green ratings for fat, sugar, and salt levels.",

    "Common Indian processed food concerns: "
    "Namkeen, chips, and fried snacks are very high in sodium (often 500-900 mg/100g) and trans fats. "
    "Instant noodles are high in sodium (often 800-1200 mg per pack) and low in fibre and protein. "
    "Biscuits and cookies often contain trans fats from partially hydrogenated vegetable oil (vanaspati). "
    "Packaged juices have equivalent added sugar to sodas and minimal actual fruit nutrition.",

    # ── Calorie Density & Portion Size ──────────────────────────────────────
    "Calorie density: foods with fewer than 1.5 kcal/g are considered low-calorie density (most vegetables, fruits, "
    "broths). Foods between 1.5-4 kcal/g are moderate. Foods above 4 kcal/g are high-calorie density "
    "(nuts, cheese, chocolate, fried foods, oils). Low-calorie-density foods promote satiety and weight management.",

    "Serving size awareness: Nutritional information on labels is per serving but packages often contain "
    "multiple servings. A bag of chips labelled '150 kcal per serving' may contain 3 servings (450 kcal total). "
    "Consumers should always check servings per container and adjust calculations accordingly.",

    # ── Palm Oil ─────────────────────────────────────────────────────────────
    "Palm oil is high in saturated fat (50% of total fat) and is a major driver of cardiovascular risk "
    "when consumed in excess. It is one of the most widely used vegetable oils in processed foods globally. "
    "Red palm oil (unrefined) contains beta-carotene and tocotrienols but the refined version loses these benefits. "
    "Individuals with heart disease, high cholesterol, or obesity should limit palm oil intake.",

    # ── Omega-3 / Omega-6 Balance ────────────────────────────────────────────
    "Omega-3 fatty acids (EPA and DHA from fatty fish; ALA from flaxseed, walnuts, chia seeds) have anti-inflammatory "
    "effects and protect cardiovascular health. The modern Western diet has an omega-6:omega-3 ratio of up to 20:1 "
    "versus the ideal 4:1. Excessive omega-6 (from refined vegetable oils) promotes inflammation. "
    "WHO recommends at least 2 servings of oily fish per week.",

    # ── Phosphorus & Potassium (for kidney disease) ──────────────────────────
    "Phosphorus is found in dairy, meat, fish, nuts, seeds, legumes, and cola drinks (as phosphoric acid). "
    "High phosphorus accelerates kidney disease progression and causes bone mineral disease. "
    "Inorganic phosphate (additives in processed foods and colas) is absorbed more readily than organic phosphorus. "
    "CKD patients should avoid phosphate additives (E339, E340, E341, E343).",

    "Potassium regulation is important for kidney disease patients. Elevated blood potassium (hyperkalemia) "
    "can cause dangerous cardiac arrhythmias. High-potassium foods to limit in advanced CKD: "
    "bananas, oranges, tomatoes, potatoes, spinach, avocados, nuts, and chocolate. "
    "Cooking and draining vegetables reduces potassium content by 30-50%.",
]
