# The index of script moves

Built from the 111 shipped scripts in [`sheet_scripts/`](../sheet_scripts/). **80 reusable moves** in 8 slots. `scripts` = how many of the 111 scripts use that move.

Every example below is verbatim from a real script, with its source file. Use this to assemble a new script: pick one move per slot, then fill the shape.

| Slot | Moves | What it covers |
|---|---|---|
| `intro` | 10 | Openings (part 1) |
| `bridge` | 4 | Part openings (part 2, 3…) |
| `teach` | 27 | Teaching moves |
| `hook` | 11 | Attention hooks inside the explanation |
| `screen` | 4 | ON SCREEN block forms |
| `handoff` | 6 | Part endings (non-final) |
| `end` | 12 | Closings (final part) |
| `tone` | 6 | Register and address |


## Openings (part 1) — `intro.*`

### `intro.board_year_repeat` — Board + year + it can come again  ·  **92 scripts**

Opens the video by naming the board and class, the year(s) the question was actually asked, and the promise that it can be asked again.

**When:** First spoken line of Part 1 in almost every script, regardless of subject or question type. Absent only where the opener is a derivation-importance line or a chapter frame.

**Shape:** `MP Board कक्षा 12वीं के बच्चों! ये सवाल <वर्ष>[ और <वर्ष>] में <board exam|Board Exam|परीक्षा> में पूछा <गया|जा चुका> है, और इस <साल|बार> भी आपकी <परीक्षा|board exam> में आ सकता है।`

> “MP Board कक्षा बारहवीं के बच्चों! ये सवाल 2024 के board exam में पूछा गया था, और इस साल भी आपकी परीक्षा में आ सकता है।”
> — `biology/BIO-C1-LA-01.txt`

> “एमपी बोर्ड कक्षा 12वीं के बच्चों! ये सवाल 2025 में परीक्षा में पूछा जा चुका है, इसलिए आपकी त्रैमासिक परीक्षा के लिए इसे बिल्कुल ignore मत करना।
> — `chemistry/CHE-C1-LA-02.txt`

> एमपी बोर्ड कक्षा 12वीं के बच्चों! ये सवाल 2018 और 2023 में आ चुका है, और इस बार भी आपकी त्रैमासिक परीक्षा में आ सकता है।
> — `chemistry/CHE-C2-LA-03.txt`

*Note:* Year count varies: one year, two years joined by 'और', or as far back as 2010. The older Chemistry scripts (CHE-C1-LA-02, CHE-C2-LA-03) say 'त्रैमासिक परीक्षा' (quarterly) instead of board exam and spell the board in Devanagari ('एमपी बोर्ड'); every later script writes 'MP Board' in Latin. When the 

### `intro.roadmap` — What this video will cover, counted  ·  **54 scripts**

Announces what the video will cover, nearly always as a counted set (तीनों / चारों / पहले…फिर…आखिर में), and often names which items are deferred to a later part.

**When:** Every script that has more than one thing to teach; the count matches the number of ON SCREEN blocks or list items that follow.

**Shape:** `तो <बच्चों,> आज <इसे ऐसे समझेंगे कि|पहले> <A>, <B> और <C>—<तीनों> <परीक्षा में कभी नहीं भूलोगे|याद हो जाएँगी>। [<D> हम Part <N> में समझेंगे।]`

> “आज इसे ऐसे समझेंगे कि बीजाण्ड के पार्ट्स, परिभाषा और डायग्राम—तीनों परीक्षा में कभी नहीं भूलोगे।”
> — `biology/BIO-C1-LA-01.txt`

> तो बच्चों, आज पहले प्रसव की definition समझेंगे, फिर इसके hormones और आखिर में इसके तीन stages भी देखेंगे।"
> — `biology/BIO-C2-SA-04.txt`

> आज हम समझेंगे कि क्वथनांक में उन्नयन क्या है, ये क्यों होता है और ग्राफ से इसे कैसे समझाना है—तीनों चीजें आपको याद हो जाएँगी।”
> — `chemistry/CHE-C1-LA-02.txt`

*Note:* The count in the roadmap is a contract: the script always delivers exactly that many items and the end.recap repeats them in the same order. In multi-part scripts the roadmap also says which item lands in which part, and that promise is honoured by the handoff line.

### `intro.question_readback` — Read the exam question aloud, including अथवा  ·  **31 scripts**

The question header carries one or more अथवा variants of the same question; the intro either reads both or silently answers the union of them.

**When:** Mostly single-part and two-part Biology scripts; also the formal Chemistry ones, where it appears under a literal 'प्रश्न:' line.

**Shape:** `सवाल है — <प्रश्न का पूरा वाक्य>`

> सवाल है — ऊर्जा का पिरामिड सदैव सीधा क्यों होता है? स्पष्ट कीजिए।
> — `biology/BIO-C12-SA-04.txt`

> सवाल है—प्रसव यानी Parturition क्या है? और प्रसव को प्रेरित करने में कौन-कौन से hormones शामिल होते हैं?
> — `biology/BIO-C2-SA-04.txt`

> प्रश्न: “प्रभावी परमाणु संख्या (EAN) क्या है? एक उदाहरण देकर समझाइए।”
> — `chemistry/CHE-C5-SA-03.txt`

*Also catalogued as: intro.alt_question_read, intro.question_restate*

*Note:* NEW because it is a distinct beat, not part of the board-year line. Note the restatement is LOOSER than the header: it glosses the Sanskritised exam wording into speakable Hinglish (परीक्षार्थ परीक्षण -> 'टेस्ट क्रॉस यानी परीक्षार्थ संकरण'). When the header carries 'अथवा' variants, only ONE is resta

### `intro.marks_promise` — Marks payoff in the opener  ·  **26 scripts**

Attaches the exact mark value of the question to the promise, so the student knows what the next two minutes are worth.

**When:** Chemistry only in this group, and on questions with a stated mark value (3-mark SA, 4-mark LA).

**Shape:** `<अगर इसे अच्छे से कर लिया|बस इतना कर लिया> तो परीक्षा में पूरे <n> नंबर पक्के`

> “MP Board कक्षा 12वीं के बच्चों! ये सवाल 2025 में परीक्षा में आ चुका है, और इस साल भी board exam में आ सकता है। लेकिन इसमें एक छोटी सी trick है—अगर वो दिमाग में बैठ गई तो परीक्षा में पूरे 4 नंबर पक्के”
> — `chemistry/CHE-C10-LA-01.txt`

> तो चलो, इसे ऐसे याद करते हैं कि परीक्षा में आपके 4 नंबर पक्के हो जाएँ!
> — `chemistry/CHE-C2-LA-03.txt`

> पूरे 3 नंबर का सवाल है, तो चलो इसे एकदम आसान तरीके से समझते हैं।
> — `chemistry/CHE-C4-SA-04.txt`

*Note:* The digit is written as a numeral ('4 नंबर') in every instance — it goes to a human reader, not TTS. Biology and Physics put the marks payoff at the END instead (see NEW.end.marks_banked), never in the opener.

### `intro.importance_no_year` — Today's question is very important (no year given)  ·  **23 scripts**

A formal-register opener: names the chapter, states what the question asks for, and only then (sometimes) gives the year. Replaces the board_year_repeat first line.

**When:** The formal-register subset (Biomolecules and Coordination Compounds shorts). Never combined with बच्चों mid-script or with mistake hooks.

**Shape:** `MP Board कक्षा 12वीं के बच्चों!
आज का <प्रश्न|question> <अध्याय> का <बहुत महत्वपूर्ण|एक महत्वपूर्ण> प्रश्न है। इसमें आपसे <A> और <B> <पूछा गया है|पूछी गई है>। [यह प्रश्न <वर्ष> में बोर्ड परीक्षा में पूछा जा चुका है, इसलिए इसे अच्छे से समझते हैं।]`

> MP Board कक्षा 12वीं के बच्चों! आज का प्रश्न जैव-अणु अध्याय का एक महत्वपूर्ण प्रश्न है। इसमें आपसे डी.एन.ए. अंगुली छापन की परिभाषा और उसके महत्व के बारे में पूछा गया है। यह प्रश्न 2019 में बोर्ड परीक्षा में पूछा जा चुका है, इसलिए इसे अच्छे से समझते हैं।
> — `chemistry/CHE-C10-SA-08.txt`

> MP Board कक्षा 12वीं के बच्चों! आज का question बहुत important है, क्योंकि इसमें आपसे आंतरिक संक्रमण तत्वों की definition, electronic configuration और दिए गए atomic numbers में से सही elements की पहचान पूछी गई है।
> — `chemistry/CHE-C4-SA-08.txt`

> MP Board कक्षा 12वीं के बच्चों! आज का यह प्रश्न Coordination Compounds के बहुत important concepts में से एक है, क्योंकि इसमें आपको केंद्रीय धातु की ऑक्सीकरण संख्या समझनी है और फिर संकुल आयन में इसकी गणना भी करनी है।
> — `chemistry/CHE-C5-SA-07.txt`

*Also catalogued as: intro.chapter_flag, intro.chapter_frame, intro.derivation_importance, intro.importance_opener, intro.important_no_year*

*Note:* NEW because the starter taxonomy has no opener that frames by CHAPTER and by what the question demands. These five scripts also drop the 'इस साल भी आ सकता है' promise, use आप/लीजिए forms, have no शिक्षक: tag, and use 'On Screen:' (title case). They look like a different author or a later pass — a ge

### `intro.difficulty_reassure` — Don't worry, we'll do it the easy way  ·  **18 scripts**

Pre-empts the student quitting by promising the hard-looking thing will be made easy, or that length is not difficulty.

**When:** Short-answer questions and any derivation; often the only opener move besides the board line.

**Shape:** `तो चलो, <आज> इसे <एकदम आसान तरीके से|आसान भाषा में|ऐसे> समझ<ते हैं|ेंगे> कि <पूरा derivation step-by-step समझ आए>`

> चलिए इसे step by step समझते हैं।
> — `chemistry/CHE-C4-SA-08.txt`

> "तो चलो, आज इसे ऐसे समझेंगे कि पूरा derivation step-by-step समझ आए और final formula भी आसानी से याद रहे।"
> — `physics/PHY-C2-NM-02.txt`

> चलिए इसे आसान भाषा में समझते हैं।
> — `chemistry/CHE-C5-SA-03.txt`

*Note:* Never 'घबराना मत' in this group — the reassurance is always about the METHOD (easy/step-by-step), never about the student's fear.

### `intro.warning` — Don't take the shallow route  ·  **14 scripts**

Warns that the obvious approach — memorising the definition, naming the property, taking it lightly — will not earn the marks.

**When:** On questions that look like plain recall (a definition, a four-line rate expression).

**Shape:** `इसलिए इसे <हल्के में मत लेना|बिल्कुल ignore मत करना>`

> “इसलिए इसे हल्के में मत लेना।”
> — `chemistry/CHE-C3-SA-09.txt`

> इसलिए आपकी त्रैमासिक परीक्षा के लिए इसे बिल्कुल ignore मत करना।
> — `chemistry/CHE-C1-LA-02.txt`

> तो बच्चों, आज इसको सिर्फ definition की तरह नहीं, बल्कि इसके पूरे कारण और effect के साथ समझेंगे, ताकि answer आसानी से याद रहे।
> — `biology/BIO-C4-SA-03.txt`

*Note:* Always one short sentence on its own line, right after the board/year line. The mid-script equivalent ('इस हिस्से को हल्के में मत लेना' in BIO-C1-LA-01 Part 3) is hook.focus_reason, not this.

### `intro.mistake_flag` — Opens on the mistake students make  ·  **8 scripts**

The first thing said about the content is the error to avoid, usually 'students write the points the wrong way round'.

**When:** Pairs of confusable terms (सह-प्रभाविता vs अपूर्ण प्रभाविता) and difference questions whose points look easy.

**Shape:** `अब यहाँ एक चीज़ का खास ध्यान रखना, क्योंकि <दो शब्दों में> बच्चे अक्सर confuse हो जाते हैं—<A> और <B>`

> अब यहाँ एक चीज़ का खास ध्यान रखना, क्योंकि दो शब्दों में बच्चे अक्सर confuse हो जाते हैं—सह-प्रभाविता और अपूर्ण प्रभाविता
> — `biology/BIO-C4-LA-01.txt`

> देखने में चारों points आसान लगते हैं, लेकिन यहाँ पर अक्सर confusion हो जाता है।
> — `chemistry/CHE-C3-SA-05.txt`

> ★ "और एक बात — बच्चे यहाँ दो जगह गलती कर देते हैं । F₁ का जीनोटाइप, और F₂ का 9 : 3 : 3 : 1 वाला अनुपात। आज इन दोनों जगहों को अच्छे से समझेंगे
> — `biology/BIO-C4-LA-02.txt`

*Note:* BIO-C4-LA-01 closes the loop on this in its last part ('बस यही एक लाइन आपको उस गलती से बचा लेगी जिसकी बात मैंने शुरू में की थी') — when this opener is used, the final part should pay it off.

### `intro.question_breakdown` — What the question is actually asking for  ·  **6 scripts**

Splits the question into its numbered deliverables so the student knows how many things the answer must contain.

**When:** Multi-clause questions ('definition + configuration + reason', 'law + two applications', 'definition + two examples each').

**Shape:** `इसमें आपसे <A>, <B> और <C> <तीनों> पूछे गए हैं। तो इसे step by step समझते हैं।`

> ये सवाल important है, क्योंकि इसमें definition, electronic configuration और metallic nature का reason तीनों पूछे गए हैं। तो इसे step by step समझते हैं।
> — `chemistry/CHE-C4-SA-02.txt`

> इसमें आपको आवश्यक तथा अनावश्यक एमीनो अम्ल की परिभाषा और प्रत्येक के दो उदाहरण देने हैं।
> — `chemistry/CHE-C10-SA-01.txt`

> आज का question बहुत important है, क्योंकि इसमें आपसे उप-सहसंयोजी यौगिक में बंधन समावयवता और आयनीकरण समावयवता, दोनों को example के साथ समझाने के लिए कहा गया है।
> — `chemistry/CHE-C5-SA-05.txt`

*Note:* Distinct from NEW.intro.question_restate (which only reads it out). The same move also appears MID-script at a part boundary, to justify why part 2 exists: 'लेकिन बच्चों, सवाल सिर्फ नियम नहीं पूछ रहा है। इसमें साफ पूछा है—इसके दो अनुप्रयोग दीजिए।' (CHE-C2-NM-01). A generator should emit it whenever 

### `intro.outcome_promise` — Watch to the end and you'll understand + remember + be able to write it  ·  **5 scripts**

Promises a three-part outcome (samajh + yaad + likhna) conditional on watching the whole video, instead of a mark count.

**When:** Long chemistry/biology process answers where the risk is the student stopping mid-video. Substitutes for intro.marks_promise when the mark value is not named.

**Shape:** `तो इस वीडियो को अंत तक ऐसे देखना कि <टॉपिक> समझ भी जाओ, याद भी कर लो और परीक्षा में लिखना भी सीख जाओ।`

> तो इस वीडियो को अंत तक ऐसे देखना कि बर्कले और हार्टले विधि समझ भी जाओ, याद भी कर लो और परीक्षा में लिखना भी सीख जाओ।”
> — `chemistry/CHE-C1-LA-01.txt`

> “और इस वीडियो के अंत तक आप इसे पूरा याद करके, परीक्षा में सही तरीके से लिखना भी सीख जाओगे।”
> — `chemistry/CHE-C2-LA-02.txt`

> लेकिन इसकी पूरी process अगर sequence में समझ आ गई तो **DNA अंगुलीछापी वाला answer aasani se लिख paoge।
> — `biology/BIO-C5-LA-01.txt`

*Note:* Distinct from intro.difficulty_reassure: it is not 'don't panic', it is a contract about what you will be able to DO. The three verbs (समझना / याद करना / लिखना) are the stable part; the topic name is the slot.


## Part openings (part 2, 3…) — `bridge.*`

### `bridge.recap_result` — Name what the last part established, then move on  ·  **65 scripts**

The bridge does not merely name the previous headings — it restates every fact from the previous part in full, as a standalone paragraph, so the part can be watched alone.

**When:** Every multi-part script, without exception.

**Shape:** `<तो> बच्चों! Part <N-1> में हमने <A और B> <समझ लिया|कर लिया|देखा> था। अब <Part N में|इस part में> <C> <समझते हैं|देखते हैं>।`

> “तो बच्चों, Part 1 में हमने बीजाण्ड के बीजाण्डवृन्त और अध्यावरण को समझा था। अब Part 2 में आगे के दो important parts देखते हैं।”
> — `biology/BIO-C1-LA-01.txt`

> तो बच्चों! Part 2 में हमने देखा — ³²P नीचे पेलेट में मिला और ³⁵S ऊपरी द्रव में। अब इन्हीं दोनों को जोड़कर निष्कर्ष निकालते हैं।
> — `biology/BIO-C5-LA-02.txt`

> “तो बच्चों, Part 1 में हमने पहला गुण—ऑक्सीकरण अवस्था—समझ लिया। चलो, अब दूसरे गुण पर आते हैं—आयनन एन्थैल्पी।”
> — `chemistry/CHE-C4-LA-03.txt`

*Also catalogued as: bridge.recap_full_restate*

*Note:* The recap NAMES the items, never just 'पिछले part में'. It is the only place a part may repeat content. Note BIO-C4-LA-01's Part 2 recap counts instead of names ('तीन एलील और चार रक्त समूह कर लिए').

### `bridge.recap_question` — Part N reopens the question Part N-1 left hanging  ·  **5 scripts**

Opens the part by re-asking the question that the previous part's handoff deliberately left hanging.

**When:** Only where the previous handoff was handoff.open_question.

**Shape:** `और पहले वो सवाल जो Part <N-1> के आखिर में छोड़ा था — <सवाल दोहराओ>`

> ★ "और पहले वो सवाल जो Part 2 के आखिर में छोड़ा था — लाल और सफेद घुलकर गुलाबी बन गए। तो क्या रंग आपस में मिल गए? क्या ये मिश्रित वंशागति है?"
> — `biology/BIO-C4-LA-01.txt`

> ★ " बच्चों! Part 1 में तीन एलील और चार रक्त समूह कर लिए। अब वो सवाल पूरा करते हैं जो अधूरा छोड़ा था।"
> — `biology/BIO-C4-LA-01.txt`

> "अब बच्चों, इसी से जुड़ा सबसे important सवाल है—अगर इससे भ्रूण के लिंग की जानकारी भी मिल सकती है, तो फिर लिंग निर्धारण के लिए इसका उपयोग क्यों प्रतिबंधित है?"
> — `biology/BIO-C3-SA-01.txt`

*Note:* Appears in only ONE of my 28 scripts, but it is the paired half of handoff.open_question, which appears in seven — i.e. most scripts pose the cliffhanger and then quietly forget it. Pairing them is an improvement a generator should make by default.

### `bridge.recap_equation` — Part N opens by re-displaying the last equation  ·  **5 scripts**

The bridge is an ON SCREEN re-render of the expression the previous part ended on, plus its spoken read-out, before the algebra continues.

**When:** Every derivation/numerical script split across parts. The viewer must see the equation again because they cannot scroll back.

**Shape:** `"बच्चों, Part <N-1> में हमने यहाँ तक निकाल लिया था —"
ON SCREEN
<equation>
"<equation read aloud in words>"`

> "बच्चों, Part 2 में हमने यहाँ तक निकाल लिया था —" ON SCREEN V = 1/(4πε₀) × (2ql)/(r² − l²) स्पोकन: "वी बराबर एक बटा चार पाई एप्सिलॉन नॉट, गुणा टू क्यू एल बटा आर स्क्वायर माइनस एल स्क्वायर।"
> — `physics/PHY-C2-NM-02.txt`

> बच्चों, Part 1 में हमने समझा था कि ऑक्सीकरण संख्या क्या होती है और संकुल आयन में इसे निकालने के लिए हमने संबंध प्राप्त किया था— On Screen: x + yz = n
> — `chemistry/CHE-C5-SA-07.txt`

*Note:* NEW: bridge.recap_result recaps in words; this one recaps as a rendered equation and is obligatory in derivations. The re-rendered equation is bit-identical to the one that closed the previous part — a generator must carry the exact string forward, not retype it.

### `bridge.direct_continue` — New section with no recap  ·  **3 scripts**

The part divider carries no greeting and no recap; the sentence continues the enumeration from where it stopped.

**When:** Only where the part break is an editing convenience, not a teaching break.

**Shape:** `Part <N> — <उपशीर्षक>
अब <तीसरा/अगला> <अंतर/point> देखते हैं।`

> Part 2 — गुण और सूत्र अब तीसरा अंतर देखते हैं।
> — `chemistry/CHE-C5-SA-04.txt`

> Part 2 — आयनीकरण समावयवता आयनीकरण समावयवता में ऐसे compounds होते हैं जिनका molecular formula समान होता है, लेकिन पानी में घोलने पर ये अलग-अलग ions देते हैं।
> — `chemistry/CHE-C5-SA-05.txt`

> भाग 3 — संक्षारण को प्रभावित करने वाले तीन कारक 🎙️ शिक्षक: “अब संक्षारण को प्रभावित करने वाले तीन कारक समझो।”
> — `chemistry/CHE-C2-LA-02.txt`

*Note:* Appears in exactly one script and reads as an oversight rather than a style — every other multi-part script re-greets with बच्चों and recaps. Do not generate this.


## Teaching moves — `teach.*`

### `teach.book_then_gloss` — Textbook sentence verbatim, then the plain restatement  ·  **79 scripts**

The exam-board sentence is delivered intact (often inside quote marks), then immediately restated in spoken Hinglish introduced by मतलब / यानी / सीधी सी बात है / आसान भाषा में.

**When:** Every definition and every quoted fact. This is the backbone move of the whole corpus.

**Shape:** `"<textbook sentence verbatim>"
"<अब इसे आसान भाषा में समझो|यानी|मतलब>—<same thing in Hinglish with English nouns>"`

> “प्रत्येक बीजाण्ड प्रायः दो, सुरक्षात्मक आवरणों से घिरा रहता है। यह आवरण ही अध्यावरण कहलाते हैं।” … “मतलब, ये बीजाण्ड के protective covering हैं।”
> — `biology/BIO-C1-LA-01.txt`

> “हर्षे व चेज ने DNA व प्रोटीन में अन्तर स्पष्ट करने के लिए उनकी रासायनिक संरचना के अन्तर को आधार बनाया। फॉस्फोरस, DNA का अपरिहार्य घटक होता है लेकिन इसमें सल्फर नहीं पाया जाता। वहीं प्रोटीन में सल्फर उपस्थित होता है, फॉस्फोरस नहीं पाया जाता।” “अब इसे आसान तरीके से समझते हैं —DNA में **phosphorus है लेकिन sulfur नहीं**, जबकि protein में **sulfur है लेकिन phosphorus नहीं**। बस यही chemical differenc…
> — `biology/BIO-C5-LA-02.txt`

> “किसी द्रव का क्वथनांक वह ताप है, जिस पर उसके वाष्पदाब का मान वायुमण्डलीय दाब के बराबर हो जाता है।” “यानी आसान भाषा में—जब किसी द्रव का वाष्पदाब, वायुमण्डलीय दाब के बराबर हो जाता है, उस ताप को उसका क्वथनांक कहते हैं।”
> — `chemistry/CHE-C1-LA-02.txt`

*Note:* The two halves differ in REGISTER, not content: the book half is Sanskritised Hindi with no English; the gloss half swaps in English technical nouns (protective covering, phosphorus, vapour pressure) and tum-forms. Never gloss first and quote second. Some scripts mark the book half with ** ** or wit

### `teach.recap_chain` — Say the whole sequence again, in order  ·  **65 scripts**

Before the close (and at the end of each long part), the entire chain is re-spoken in order — often mirrored by a ‘Quick Revision’ ON SCREEN block.

**When:** The last part of every multi-part script, and the end of most single-part ones.

**Shape:** `"अब <पूरे derivation को|पूरे experiment को> <एक बार> sequence में याद कर लो—"
ON SCREEN
<A> → <B> → <C> → <final>
"<same chain spoken as a sentence>"`

> ON SCREEN +q और −q → E = E₁ − E₂ → AP = r − l → BP = r + l → p = 2ql → E = 1/(4πε₀) × 2pr/(r² − l²)² → l << r → E = 1/(4πε₀) × 2p/r³
> — `physics/PHY-C1-NM-01.txt`

> ON SCREEN: Quick Revision Parturition → Uterine contractions → Baby का जन्म Hormones: Oxytocin → Contractions Relaxin → प्रसव में सहायता Stages: 1. Cervix dilation 2. Baby birth 3. Placenta expulsion
> — `biology/BIO-C2-SA-04.txt`

> ON SCREEN Biot-Savart law → dB → axial component → sin φ = a/r → Σdl = 2πa → r² = a² + x² → B = μ₀/(4π) × 2πnIa²/(a² + x²)^(3/2)
> — `physics/PHY-C4-NM-01.txt`

*Note:* The chain is one long ON SCREEN line in Physics (which will overflow a 9:16 frame unless wrapped) and a stacked card in Biology. The spoken walk-through follows the chain element by element in the same order.

### `teach.formula_readout` — Every formula is read aloud in words  ·  **44 scripts**

Every ON SCREEN equation is followed by a quoted line that spells the equation out in Hindi/English words, with no digits or symbols, for the TTS/presenter to read.

**When:** All Physics derivations, all Chemistry numerical/formula scripts. Two distinct conventions exist (see notes).

**Shape:** `ON SCREEN
<equation>
"<equation in words: बराबर / बटा / गुणा / into / by / whole square>"`

> ON SCREEN E₁ = 1/(4πε₀) × q/(r − l)² “E one बराबर है one by four pi epsilon naught into q by r minus l whole square।”
> — `physics/PHY-C1-NM-01.txt`

> ON SCREEN V₊q = 1/(4πε₀) × q/BP स्पोकन: "वी प्लस क्यू बराबर एक बटा चार पाई एप्सिलॉन नॉट, गुणा क्यू बटा बी पी।"
> — `physics/PHY-C2-NM-02.txt`

> On Screen: (n−2)f¹⁻¹⁴ (n−1)d⁰⁻¹ ns² “Open bracket n minus two close bracket f की power one to fourteen, open bracket n minus one close bracket d की power zero to one, n s square।”
> — `chemistry/CHE-C4-SA-08.txt`

*Also catalogued as: teach.equation_readout, teach.spoken_formula_gloss, teach.spoken_math_readout*

*Note:* NEW and the single most important type for a generator. Two conventions: (a) PHY-C2-NM-02 and PHY-C2-SA-01 put a literal 'स्पोकन:' tag on its own line and transliterate EVERYTHING into Devanagari ('वी बराबर एक बटा चार पाई एप्सिलॉन नॉट'); (b) everything else uses a bare quoted line mixing Devanagari 

### `teach.cause_effect` — Because → therefore chain  ·  **35 scripts**

Builds the answer as a causal chain where each step is the reason for the next, usually mirrored by a single ON SCREEN arrow chain.

**When:** Reason ('क्यों') questions and any mechanism.

**Shape:** `<A बढ़ता है> → <इसलिए B बढ़ता है> → <इसलिए C घट जाता है>
ON SCREEN: <A ↑ → B ↑ → C ↓>`

> On Screen: Nuclear charge ↑ → आकर्षण बल ↑ → आयनिक त्रिज्या ↓
> — `chemistry/CHE-C4-SA-04.txt`

> अब विलेय मिलाने पर वाष्पदाब कम हो गया। इसका मतलब है कि वायुमण्डलीय दाब तक पहुँचने के लिए अब पहले से अधिक ताप देना पड़ेगा। और जब अधिक ताप देंगे, तो विलयन का क्वथनांक भी बढ़ जाएगा।”
> — `chemistry/CHE-C1-LA-02.txt`

> ON SCREEN: एक पोषण स्तर की ऊर्जा ↓ श्वसन एवं अन्य जीवन-क्रियाएँ ↓ ऊष्मा के रूप में ऊर्जा का ह्रास
> — `biology/BIO-C12-SA-04.txt`

*Note:* The on-screen chain uses ↓ or → arrows and NO words the narration does not also say. It is the one case where screen text may closely track the narration, because the arrows carry the logic.

### `teach.stepwise` — Numbered steps of a process  ·  **32 scripts**

Walks a process one numbered stage at a time, each stage announced by its ordinal, its Hindi name and its English name in brackets.

**When:** Experiments, physiological processes, identification procedures.

**Shape:** `"<पहला|दूसरा|तीसरा> stage—<नाम>"
ON SCREEN:
Stage <n> — <नाम>
<विवरण>`

> "पहला stage—cervix यानी गर्भाशयी ग्रीवा का फैलना, जिसे cervical dilation कहते हैं। इसी दौरान amniotic fluid भी बाहर निकल सकता है।" ON SCREEN: Stage 1 — Cervical Dilation
> — `biology/BIO-C2-SA-04.txt`

> अब दिए गए numbers को एक-एक करके check करते हैं। सबसे पहले है 25। On Screen: 25 ❌
> — `chemistry/CHE-C4-SA-08.txt`

> “अब अपघटन की पूरी प्रक्रिया को पाँच मुख्य stages में समझा जाता है।” ON SCREEN: अपघटन की 5 अवस्थाएँ: 1. खण्डन → 2. प्रक्षालन → 3. अपचय → 4. ह्यूमीकरण → 5. खनिजीभवन
> — `biology/BIO-C12-SA-01.txt`

*Note:* Stage headings on screen are in English even when the narration is Hindi ('Stage 2 — Birth of Baby').

### `teach.derivation` — Formula built step by step  ·  **31 scripts**

Derives the expression one algebraic step at a time: a spoken sentence saying what is being done, an ON SCREEN equation, then the phonetic read-out of that equation.

**When:** All four Physics scripts and the Chemistry relation/formula questions.

**Shape:** `"<अब X करते हैं।>"
ON SCREEN
<equation>
"<equation read aloud>"
(repeat, one step per block)`

> “अब दोनों fractions को एक denominator में लेते हैं।” ON SCREEN E = q/(4πε₀) × [(r + l)² − (r − l)²] / [(r − l)²(r + l)²]
> — `physics/PHY-C1-NM-01.txt`

> अब समानुपातिता हटाने के लिए Rho नाम का नियतांक लेते हैं। इसलिए, R बराबर rho into l upon A. [ON SCREEN: R = ρ × l/A]
> — `chemistry/CHE-C2-SA-06.txt`

> “हमारा विलयन तनु है। इसलिए Wb/Mb का मान Wₐ/Mₐ की तुलना में बहुत छोटा होता है।” “इसलिए हर में मौजूद Wb/Mb को neglect कर सकते हैं।” “तो हमें मिलेगा—” (Pₐ⁰ − Pₐ) / Pₐ⁰ = (Wb/Mb) / (Wₐ/Mₐ)
> — `chemistry/CHE-C1-NM-02.txt`

*Note:* Step density is very high: PHY-C4-NM-01 has 27 ON SCREEN blocks in 140 lines. Each part ends immediately before a simplification, never in the middle of one. The final part always closes with an arrow-chain recap of the whole derivation (teach.recap_chain).

### `teach.symbol_gloss` — Name each symbol after the formula  ·  **30 scripts**

Names every letter in the expression in words, either when it is introduced or as a closing recap of the derivation.

**When:** Immediately after the first display of any formula, and again in the final recap.

**Shape:** `यहाँ <X> है <अर्थ>, <Y> है <अर्थ> और <Z> है <अर्थ>।`

> “यहाँ Tb है विलयन का क्वथनांक और Tb⁰ है शुद्ध विलायक का क्वथनांक।”
> — `chemistry/CHE-C1-LA-02.txt`

> "यहाँ K माध्यम का परावैद्युतांक है, A प्रत्येक प्लेट का क्षेत्रफल है, एप्सिलॉन नॉट निर्वात की विद्युतशीलता है और d दोनों प्लेटों के बीच की दूरी है।"
> — `physics/PHY-C2-SA-01.txt`

> जहाँ R यानी प्रतिरोध है, A इलेक्ट्रोडों का अनुप्रस्थ क्षेत्रफल है, और l दोनों इलेक्ट्रोडों के बीच की दूरी है।
> — `chemistry/CHE-C2-SA-02.txt`

*Note:* Latin symbols stay Latin in the written line but are SPOKEN as Devanagari words in the physics scripts ('एप्सिलॉन नॉट', 'सिग्मा'). Greek letters are named, never shown alone in narration.

### `teach.compare` — Two (or three) things contrasted point by point  ·  **25 scripts**

Runs a difference question as N parallel points, each stating A then B on the same axis, with a two-line ON SCREEN pair per point.

**When:** Every 'अंतर/विभेद/differentiate' question.

**Shape:** `<पहला|दूसरा> अंतर — <आधार>
"<A> <property>, जबकि <B> <property>।"
On Screen:
<A> → <property>
<B> → <property>`

> दूसरा अंतर — जल में विलेयता रेशेदार प्रोटीन सामान्यतः जल में अविलेय होती हैं। वहीं गोलिकाकार प्रोटीन सामान्यतः जल में विलेय होती हैं।
> — `chemistry/CHE-C10-SA-04.txt`

> “विद्युत् परिपथ भंग होने पर भी विद्युत् वाहक बल का अस्तित्व रहता है।” “लेकिन विद्युत् परिपथ भंग होने पर विभवान्तर का अस्तित्व समाप्त हो जाता है।”
> — `physics/PHY-C3-SA-01.txt`

> लघुबीजाणुजनन की यह प्रक्रिया नर भाग में लघुबीजाणुधानी के भीतर संपन्न होती है। गुरुबीजाणुजनन की यह प्रक्रिया मादा भाग में बीजांड (Ovule) के अंदर संपन्न होती है। ON SCREEN: लघुबीजाणुजनन → लघुबीजाणुधानी के भीतर गुरुबीजाणुजनन → बीजांड के भीतर
> — `biology/BIO-C1-LA-02.txt`

*Note:* The number of differences is fixed by the question ('कोई तीन'/'चार अन्तर') and the script delivers exactly that many, each introduced by its ordinal. PHY-C3-SA-01 gives the definitions of BOTH terms first, then the four differences — that ordering is what the question asks for.

### `teach.definition_first_line` — This exact sentence is the first line of your answer  ·  **25 scripts**

Tells the student that the sentence just spoken is what goes on the answer sheet, word for word, and warns against paraphrasing.

**When:** After the primary definition of every definition-type question.

**Shape:** `और परीक्षा में ये परिभाषा इसी तरह लिखना है, अपने हिसाब से words मत बदलना`

> और परीक्षा में ये परिभाषा इसी तरह लिखना है, अपने हिसाब से words मत बदलना
> — `biology/BIO-C4-LA-01.txt`

> इसे परीक्षा में ऐसे ही लिखना है।”
> — `biology/BIO-C5-SA-03.txt`

> “तो चलो सबसे पहले समझते हैं कि तालाब का पारितंत्र होता क्या है, और exam me bilkul ese hi likhna hai -
> — `biology/BIO-C12-LA-03.txt`

*Note:* This is why the book half of teach.book_then_gloss must stay verbatim — the script is telling the student it is quotable. A generator must not 'improve' a quoted definition.

### `teach.diagram_walk` — Walk the figure and name its labels  ·  **20 scripts**

Names each labelled part or each feature of a graph in the order it should be drawn/read, with the label given in Hindi and English together.

**When:** सचित्र / नामांकित चित्र questions, graph questions, and circuit/apparatus descriptions.

**Shape:** `"तो चलो, सबसे पहला part—<हिन्दी नाम> यानी <English>।"
ON SCREEN:
<हिन्दी नाम> (<English>)
<एक-पंक्ति परिभाषा>`

> “तो चलो, सबसे पहला part—बीजाण्डवृन्त यानी Funicle।”[a]
> — `biology/BIO-C1-LA-01.txt`

> “ग्राफ में शुद्ध विलायक का वाष्पदाब बढ़ते हुए वायुमण्डलीय दाब तक पहुँचता है, उसका क्वथनांक Tb⁰ माना है हमने माना है |
> — `chemistry/CHE-C1-LA-02.txt`

> “मान लो AB एक विद्युत् द्विधुव है, जिसमें A पर +q और B पर −q आवेश है। दोनों आवेशों के बीच की दूरी 2l है।”
> — `physics/PHY-C1-NM-01.txt`

*Note:* The script never says WHERE on screen a part sits; it names parts in drawing order and relies on the figure. Physics scripts say 'Diagram से देखो' and then assert a distance — the figure must already exist or the line is meaningless. BIO-C12-LA-03's whole question is a diagram, yet the script has on

### `teach.counted_list` — Fill a counted list, one item at a time  ·  **16 scripts**

Announces a count, then delivers exactly that many items, each with an ordinal, its own ON SCREEN card and a progress count between them.

**When:** The dominant structure of the whole corpus: parts of a structure, properties, features, differences, uses, components, stages.

**Shape:** `"इसके अंदर <n> चीजें आती हैं।"
"पहला point— <item 1>"
"अब दूसरा point — <item 2>"
"और तीसरा है <item 3>"
"अब बस ये <n> नाम पक्के कर लो—<item1>, <item2> और <item3>"`

> इसके अंदर तीन चीजें आती हैं ।” पहला point- “ तालाब में मौजूद जल में घुली हुई **गैसें, अकार्बनिक और कार्बनिक पदार्थ**”
> — `biology/BIO-C12-LA-03.txt`

> “अब बस अजैविक के ये तीन नाम पक्के कर लो—जल, तली की मृदा और जलवायुगत कारक ”
> — `biology/BIO-C12-LA-03.txt`

> “तो बच्चों, अभी तक हमने तीन विशेषताएँ कर लीं — त्रिक प्रकृति, असंदेहास्पद और डीजेनरेट। अब देखते हैं चौथी विशेषता।”
> — `biology/BIO-C5-SA-03.txt`

*Note:* NEW: teach.stepwise covers a PROCESS; this covers an unordered set that is merely enumerated, which behaves differently — the items can be reordered, the running total is repeated after every item, and the list is always restated in full at a part boundary and again at the end. The repo's own beats 

### `teach.worked_example` — Write the given values before touching the formula  ·  **16 scripts**

Substitutes given values into a stated formula one substitution at a time, each with its own ON SCREEN line, until a final number falls out.

**When:** Numerical questions (EAN, oxidation number, order and units, identifying elements from atomic numbers).

**Shape:** `अब <formula> में values put करते हैं।
On Screen:
<formula with numbers>
"<read aloud>"
Calculation करने पर—
On Screen:
<answer>`

> अब EAN के formula में values put करते हैं। On Screen: EAN = 26 − 2 + 12 “EAN equals twenty-six minus two plus twelve।”
> — `chemistry/CHE-C5-SA-03.txt`

> अब minus six को दूसरी तरफ ले जाने पर— On Screen: x = −4 + 6 “x equals minus four plus six.”
> — `chemistry/CHE-C5-SA-07.txt`

> बच्चों, ये दिमाग में बैठ गया। अब एक important example देखते हैं। अमोनियम नाइट्राइट के विघटन की अभिक्रिया है - ON SCREEN: NH₄NO₂ → N₂ + 2H₂O
> — `chemistry/CHE-C3-SA-07.txt`

*Also catalogued as: teach.given_values_first, teach.substitute_and_solve, teach.worked_number_illustration*

*Note:* NEW: teach.derivation builds a general formula; this one evaluates it. Every arithmetic step is separate — even 'minus one into six होगा minus six' gets its own block. Numbers are spoken as English words ('twenty-six minus two plus twelve'), never as digits.

### `teach.example_everyday` — A real-life example  ·  **13 scripts**

Anchors the abstract object in something the student has handled — a torch cell, a car battery, a ladder, sunlight on skin.

**When:** Definitions that are otherwise unfalsifiable, and vitamin/disease pairs.

**Shape:** `उदाहरण के लिए / जैसे <रोज़मर्रा की चीज़>`

> उदारहण के लिए पानी का क्वथनांक 100 degree celsious होता है, वही पानी में नमक मिलने पर क्वथनांक अब 100 degree celsious नहीं उससे बढ़ जाएगा।
> — `chemistry/CHE-C1-LA-02.txt`

> जैसे प्रत्येक व्यक्ति की उंगलियों की छाप एक-दूसरे से अलग होती है, उसी प्रकार प्रत्येक व्यक्ति के डी.एन.ए. में उपस्थित क्षारकों का अनुक्रम भी विशिष्ट होता है।
> — `chemistry/CHE-C10-SA-08.txt`

> “विटामिन A यानी रेटिनॉल। ये गाजर, दूध और अंडे में मिलता है। इसकी कमी से रतौंधी होती है, यानी रात में दिखना कम हो जाता है।”
> — `chemistry/CHE-C10-LA-01.txt`

*Note:* Rare — roughly one per script at most, and never in the Physics derivations. The example is always a BOARD-SAFE one (salt in water, fingerprints), never invented physics.

### `teach.confusable_split` — Separate the two things students merge  ·  **10 scripts**

Names two near-identical items and states, in one line each, what distinguishes them — the correction that follows hook.mistake.

**When:** Adjacent numbers (3.4 vs 0.34 nm), adjacent ratios (phenotypic vs genotypic), adjacent names (बीजाणुजनन ऊतक vs बीजाण्डकाय), adjacent symbols (B₆ vs B₉), and alternative names for one thing (प्रतिरोधकता vs विशिष्ट प्रतिरोध).

**Shape:** `<A> = <अर्थ A> और <B> = <अर्थ B>। <इन दोनों को आपस में mix मत करना / ये difference एकदम दिमाग में छाप लो>।`

> “इसे 3.4 nm से mix मत करना।” “**3.4 nm = एक complete turn की length** और **0.34 nm = दो पास-पास के base pairs के बीच की दूरी।**” “यह difference एकदम दिमाग में छाप लो।”
> — `biology/BIO-C5-LA-03.txt`

> ★ "इन दोनों को आपस में मत मिला देना। दिखने वाले रूप चार हैं, इसलिए फीनोटाइप के चार अंक। और अंदर के जोड़ नौ तरह के हैं, इसलिए जीनोटाइप के नौ अंक।"
> — `biology/BIO-C4-LA-02.txt`

> “बी₆ मत लिखना, क्योंकि यह आक्षेप से जुड़ा है।
> — `chemistry/CHE-C10-LA-02.txt`

*Note:* NEW: hook.mistake announces the trap, this supplies the discriminator, and they are always adjacent — generate them as a pair or not at all. Note the third sub-form: two names for the SAME thing (specific resistance / resistivity), which needs the opposite framing — 'don't be confused, they are one 

### `teach.verbatim_dictation` — Write this down exactly as I say it  ·  **9 scripts**

Announces, before the sentence, that the next sentence is to be copied word for word into the answer.

**When:** Immediately before the definition or the standard statement of a law.

**Shape:** `सबसे पहले इसकी definition बिल्कुल ऐसे ही लिखना, जैसे मैं बता रहा हूँ<, नहीं तो नंबर कट जाएंगे>।`

> “सबसे पहले इसकी defination बिल्कुल ऐसे ही लिखना, जैसे मैं बता रहा हूँ, नहीं तो नंबर कट जाएंगे।”
> — `biology/BIO-C5-LA-04.txt`

> ★ "चलो, अब पहली अवस्था से शुरू करते हैं। और इस पूरे point को हूबहू लिखना है बीच में छोड़ना मत।"
> — `biology/BIO-C2-LA-02.txt`

> “सबसे पहले ध्यान से सुनना—परीक्षा में कोलरॉश के नियम की definition इसी तरह लिखनी है।”
> — `chemistry/CHE-C2-NM-01.txt`

*Note:* New id: distinct from teach.definition_first_line (which says WHERE it goes) and hook.exam_payoff (which is said after). This one is a cue to the EDITOR too — the sentence that follows it must be on screen long enough to copy, and must not be paraphrased by the visual director. 'नहीं तो नंबर कट जाएं

### `teach.name_unpack` — The term's own name is the mnemonic  ·  **8 scripts**

Derives the meaning from the parts of the term's own name, or explains why it is called that (after a person, after the element it follows, after the action it performs).

**When:** Confusable Sanskritised term pairs.

**Shape:** `नाम पर गौर करो — '<morpheme>' यानी <literal meaning>। <इसका नतीजा>। बस इतना पकड़ लिया तो confusion nahi hoga।`

> ★ "चलो शुरू करते हैं सह-प्रभाविता से और नाम पर गौर करो — 'सह' यानी साथ-साथ। दोनों साथ, दोनों बराबर। बस इतना पकड़ लिया तो confusion nahi hoga।"
> — `biology/BIO-C4-LA-01.txt`

> ★ "फिर से नाम को समझो — 'अपूर्ण' यानी अधूरा। कोई एक एलील अपना काम अधूरा छोड़ देता है। ये एक शब्द पकड़ लो, बाकी अपने आप खुल जाएगा।"
> — `biology/BIO-C4-LA-01.txt`

> ★ "सबसे पहले नाम से समझते हैं — 'ब्लीडर्स रोग'। यानी खून बहने वाला रोग।
> — `biology/BIO-C4-LA-03.txt`

*Also catalogued as: teach.name_decode, teach.name_etymology*

*Note:* One script only, but it is the best-written one in the group and the technique generalises to any Sanskrit-derived pair (सम/विषम, अग्र/पश्च, स्वपोषी/विषमपोषी).

### `teach.question_wording_callback` — Quote the question's own words and say what they oblige  ·  **8 scripts**

Reads a phrase back out of the exam question (सचित्र, महत्वपूर्ण लक्षण, व्युत्पत्ति, कौन सा विभाजन) and states the obligation it creates for the answer.

**When:** Whenever the question's verb or qualifier demands something the explanation would otherwise skip — a figure, a full derivation, a named sub-answer, a complete list.

**Shape:** `और <question/प्रश्न> में <पूछा है / साफ लिखा है> <'<उद्धृत शब्द>'>, तो <answer में <X> लिखना मत भूलना / परीक्षा में <चित्र> जरूर बनाना>।`

> ★ "और question में पूछा है कि कौन सा विभाजन होता है, तो answer में 'अर्धसूत्री विभाजन' लिखना मत भूलना।"
> — `biology/BIO-C1-LA-02.txt`

> “बच्चों, क्योंकि प्रश्न में साफ लिखा है ‘सचित्र वर्णन’, इसलिए परीक्षा में चित्र जरूर बनाना। सिर्फ लिखकर मत छोड़ना।”
> — `chemistry/CHE-C2-LA-04.txt`

> “और बच्चों, परीक्षा में इन steps को इसी क्रम में लिखना, क्योंकि सवाल सिर्फ definition नहीं, ‘गणितीय व्यंजक की व्युत्पत्ति’ भी पूछ रहा है।”
> — `chemistry/CHE-C1-NM-02.txt`

*Note:* NEW, and the most generative move in the corpus: it is the script-level form of the repo's own question_strategy(). The quoted phrase is always in single quotes inside the spoken line. BIO-C4-LA-02 uses it to JUSTIFY THE PART SPLIT (two demands → cross in Parts 1-2, law in Part 3), which is the best

### `teach.bilingual_echo` — Hindi-English echo of the point just made  ·  **6 scripts**

After a point and its ON SCREEN block, a quoted one-liner restates it as a code-switched Hindi-English sentence — the sentence the presenter actually says over the graphic.

**When:** The formal chemistry scripts. Fires after EVERY point, without exception, in CHE-C10-SA-05 and CHE-C10-SA-09.

**Shape:** `On Screen:
<A> → <गुण A>
<B> → <गुण B>
“<A> has <property A>, जबकि <B> has <property B>.”`

> “DNA has a double-helix structure, जबकि RNA has a single-helix structure.”
> — `chemistry/CHE-C10-SA-05.txt`

> “विटामिन D gives सुदृढ़ अस्थियाँ and controls कैल्सियम and फॉस्फोरस का चयापचय।”
> — `chemistry/CHE-C10-SA-09.txt`

> “Strong metallic bonding के कारण ज्यादा energy required होती है, इसलिए enthalpy of atomization high होती है।”
> — `chemistry/CHE-C4-SA-05.txt`

*Note:* NEW: teach.book_then_gloss glosses Hindi into simpler Hindi; this glosses Hindi into English-shaped Hinglish, and it is a read-out of the SCREEN, not of the book. The CHE-C10-SA-09 form ("विटामिन D gives … and controls …") is grammatically odd English and should be kept that way if imitating the hou

### `teach.named_example` — The standard examples  ·  **5 scripts**

Supplies the textbook's canonical examples for a category, usually as an on-screen list read aloud immediately after.

**When:** 'उदाहरण दीजिए' questions and the last row of every comparison table.

**Shape:** `इसके उदाहरण हैं—\nOn Screen: "<ex1>, <ex2>, <ex3>"\n“<ex1>, <ex2>, <ex3>।”`

> इसके उदाहरण हैं— On Screen: "वैलीन, आइसोल्यूसीन, आर्जिनीन, ल्यूसीन, थ्रिऑनीन" “वैलीन, आइसोल्यूसीन, आर्जिनीन, ल्यूसीन, थ्रिऑनीन।” इनमें से परीक्षा में आपको कोई भी दो उदाहरण लिखने हैं।
> — `chemistry/CHE-C10-SA-01.txt`

> इसके उदाहरण हैं - एसीटोन + CS₂ और C₂H₅OH + n-hexane।
> — `chemistry/CHE-C1-SA-01.txt`

> ON SCREEN प्रतिचुम्बकीय: बिस्मथ, फास्फोरस, एण्टिमनी, पारा, वायु आदि। अनुचुम्बकीय: मैंगनीज, प्लेटिनम, सोडियम, एल्युमिनियम आदि। लौह-चुम्बकीय: लोहा, इस्पात, निकिल, कोबाल्ट आदि।
> — `physics/PHY-C5-LA-01.txt`

*Note:* New id because teach.example_everyday does not fit at all — NOT ONE of the 28 scripts uses a real-life analogy. Examples are always the book's, never invented. The list is given longer than the exam needs, with an explicit 'कोई भी दो लिख देना'. Examples are the point where students mis-file items in

### `teach.exception_flag` — And here is the exception  ·  **4 scripts**

Flags the one case that breaks the rule just taught, and says the exam asks about exactly this.

**When:** Periodic-trend questions, order-of-reaction rules, anything with a stated 'सामान्यतः'.

**Shape:** `अब एक अपवाद है, इसे ध्यान से सुनना—यही परीक्षा में पूछ लेते हैं।
<अपवाद>
क्योंकि <कारण>`

> “अब एक अपवाद है, इसे ध्यान से सुनना—यही परीक्षा में पूछ लेते हैं।” “Zn, Cd और Hg की आयनन एन्थैल्पी अपेक्षाकृत अधिक होती है।”
> — `chemistry/CHE-C4-LA-03.txt`

> “Reaction की order निकालते समय chemical equation में दिए गए coefficients को नहीं जोड़ना है। हमें सिर्फ दिए गए वेग व्यंजक में concentration की powers देखनी हैं।”
> — `chemistry/CHE-C3-SA-09.txt`

> “अभिक्रिया की कोटि हमेशा whole number में ही हो, ऐसा जरूरी नहीं है। यह fractional यानी भिन्नात्मक भी हो सकती है।”
> — `chemistry/CHE-C3-SA-09.txt`

*Note:* NEW: distinct from hook.mistake — that names a student error, this names a case where the RULE itself does not hold. Always immediately after the rule, never batched at the end.

### `teach.assume_setup` — मान लो — declare the givens  ·  **4 scripts**

Before any calculation, the quantities are named and the initial and final states are labelled with subscripts.

**When:** Numericals, derivations, and any proof that starts from a configuration.

**Shape:** `"मान लो <वस्तु> का <राशि> <X₁> है।" … "जबकि परिवर्तन के बाद इसका <राशि> <X₂> है।"`

> "मान लो तार की प्रारंभिक लंबाई l₁ और अनुप्रस्थ काट का क्षेत्रफल A₁ है।" "जबकि परिवर्तन के बाद इसकी लंबाई l₂ और अनुप्रस्थ काट का क्षेत्रफल A₂ है।"
> — `physics/PHY-C3-NM-02.txt`

> "मान लेते हैं कि q धन आवेश को एक गोले के केंद्र O पर रखा गया है और गोले की त्रिज्या r है।"
> — `physics/PHY-C1-LA-01.txt`

> "मान लो चार प्रतिरोध P, Q, R और S हैं।" "इन चारों प्रतिरोधों को एक चतुर्भुज ABCD की चार भुजाओं में जोड़ दिया जाता है।"
> — `physics/PHY-C3-SA-03.txt`

*Note:* New id: it is the first content move of every physics script and it is what the figure has to show. Point labels (O, P, A, B, C, D) are introduced here and never redefined later, so the diagram and the narration share one label set from this line onward.

### `teach.unit_reminder` — Don't forget the unit  ·  **3 scripts**

A standalone reminder that the unit (or the constant's value) must be written with the formula.

**When:** Any chemistry/physics answer whose formula has a non-obvious unit; the whole of CHE-C3-SA-08 is this move expanded into a question.

**Shape:** `और हाँ, formula के साथ unit लिखना मत भूलना।`

> और हाँ, formula के साथ unit लिखना मत भूलना।
> — `chemistry/CHE-C2-SA-05.txt`

> अच्छा, अब इसकी इकाई भी देख लेते हैं। इसकी इकाई ओम⁻¹ सेमी² मोल⁻¹ होती है और S.I. इकाई S m² mol⁻¹ होती है।
> — `chemistry/CHE-C2-SA-05.txt`

> इस formula में 2.303 की value का ध्यान रखना।
> — `chemistry/CHE-C3-SA-04.txt`

*Note:* Filed under hook because it is an attention move, not an explanation. Both the CGS and the S.I. unit are given where they differ.

### `teach.shared_point` — And here is what they have in common  ·  **2 scripts**

After a run of contrasts, names the one attribute that is the same for both — as a guard against over-contrasting.

**When:** Difference questions where a neighbouring property is identical and students wrongly contrast it too.

**Shape:** `और दोनों में एक बात common है—<साझा तथ्य>।`

> “और दोनों में एक बात common है—ऊर्जा का प्रवाह केवल एकदिशीय होता है।” “इसे अच्छी तरह समझ लो—खाद्य जाल में भी energy वापस नहीं लौटती, उसका flow उत्पादकों से शाकाहारी और शाकाहारी से मांसाहारी की ओर ही होता है।”
> — `biology/BIO-C12-LA-01.txt`

> लेकिन दोनों में एक बात एक जैसी रहती है और वो बात ये है कि - एनोड पर हमेशा ऑक्सीकरण होता है और कैथोड पर हमेशा अपचयन।
> — `chemistry/CHE-C2-SA-08.txt`

*Note:* New id: only two files, but it prevents a real exam error (writing a false difference), and both instances sit at the same place — right after the row a student would be tempted to invert. Worth generating for any difference question where an adjacent property is shared.

### `teach.cross_build` — Build the genetic cross  ·  **2 scripts**

Fixed biology scaffold: fix the symbols, write the parents' genotypes, list each parent's gametes, combine them in a Punnett square, then read the ratio off the result.

**When:** Every genetics question (inheritance, Mendel's laws, sex-linked disorders).

**Shape:** `प्रतीक तय → जनकों का जीनोटाइप → युग्मक → Punnett square → परिणाम (% पुत्र / % पुत्रियाँ) → एक-पंक्ति निष्कर्ष`

> ON SCREEN: पिता (पीड़ित) = XʰY माता (सामान्य) = XᴴXᴴ ★ "पिता पीड़ित है, इसलिए उसका इकलौता X रोग वाला है — Xʰ। और माता पूरी तरह सामान्य है, इसलिए उसके दोनों X सामान्य — XᴴXᴴ।"
> — `biology/BIO-C4-LA-03.txt`

> "अब gametes देखो। YY से दोनों gametes में Y आएगा और yy से दोनों gametes में y आएगा।" ON SCREEN: Gametes: YY → Y, Y yy → y, y
> — `biology/BIO-C4-SA-05.txt`

> ON SCREEN: सभी पुत्र सामान्य (XᴴY) = 50% सभी पुत्रियाँ वाहक (XᴴXʰ) = 50%
> — `biology/BIO-C4-LA-03.txt`

*Note:* New id: the sequence is rigid and reusable, and each stage is a separate on-screen card that must persist while the next is built. The counter-intuitive result is always called out afterwards with hook.mistake ('पिता खुद रोगी है, तो पहली नजर में लगेगा कि उसके बेटे भी रोगी होंगे। लेकिन ऐसा नहीं है।')

### `teach.source_correction` — The reference has a typo; the right answer is this  ·  **1 scripts**

Warns the student that the printed source they are checking against contains an error, and gives the correct value.

**When:** Worked numericals where the guide's answer is wrong.

**Shape:** `ध्यान रखें बच्चों, reference में यदि <गलत मान> दिया हुआ दिखाई दे, तो वह मुद्रण या टाइपिंग की त्रुटि है। सही गणना के अनुसार उत्तर <सही मान> ही होगा।`

> ध्यान रखें बच्चों, reference में यदि calculation के अंत में +2.6 दिया हुआ दिखाई दे, तो वह मुद्रण या टाइपिंग की त्रुटि है। सही गणना के अनुसार उत्तर +2 ही होगा।
> — `chemistry/CHE-C5-SA-07.txt`

*Note:* One script only. Important as a precedent: the corpus does correct the source rather than reproduce a wrong value, but it names the wrong value out loud, which risks teaching it. A generator should keep the correction and drop nothing.

### `teach.table_readout` — Read the comparison table aloud, row by row  ·  **1 scripts**

After an ON SCREEN विभेद table, the narration reads the table cell by cell as a spoken sentence.

**When:** Difference questions whose answer is written as a table in the exam.

**Shape:** `अब इसे परीक्षा में विभेद तालिका के रूप में लिख सकते हैं।
On Screen:
<आधार | A | B rows>
"<आधार>—<A का मान> और <B का मान>। …"`

> “आधार, रेशेदार प्रोटीन और गोलिकाकार प्रोटीन। संरचना—रेशेदार और गोलाकार। जल में विलेयता—सामान्यतः अविलेय और सामान्यतः विलेय। ताप एवं pH—रेशेदार में अपेक्षाकृत स्थायी और गोलिकाकार में परिवर्तन से प्रभावित।”
> — `chemistry/CHE-C10-SA-04.txt`

> “रेशेदार प्रोटीन is insoluble in water, जबकि गोलिकाकार प्रोटीन is generally soluble in water.”
> — `chemistry/CHE-C10-SA-04.txt`

*Note:* One script, and it is the weakest writing in the group: the read-out repeats the screen verbatim (exactly what the repo's preflight warns about), and the code-switch flips to a full English predicate ('is insoluble in water'), which reads as machine-translated. Record it so a generator recognises th

### `teach.exam_writeup_replay` — Replay the whole derivation as the written answer  ·  **1 scripts**

A whole part that re-does the previous part's derivation with no new content, framed as ‘this is the order you write it in’.

**When:** Derivation questions where the marking scheme rewards the write-up order.

**Shape:** `तो सबसे पहले लिखेंगे—<समीकरण 1>। … इसलिए—<समीकरण 2>। … अब इन मानों को रख देते हैं …`

> तो बच्चों, Part 1 में हमने समझा कि शून्य कोटि की अभिक्रिया का अर्द्ध-आयुकाल कैसे निकाला जाता है। अब देखते हैं, इसे परीक्षा में सही तरीके से कैसे लिखना है। ” "इसे थोड़ा ध्यान से समझना, क्योंकि 100 में से 80 बच्चे यहीं गलती करते हैं “तो सबसे पहले लिखेंगे—शून्य कोटि की अभिक्रिया का समीकरण। t = 1/k ([A₀] − [A])
> — `chemistry/CHE-C3-LA-01.txt`

*Note:* Single file, and the repetition is near-verbatim — the same five equations in the same order. Useful as a length-filler for a 4-mark derivation, but a generator must vary the framing verbs (समझते हैं → लिखेंगे) or the second part reads as a duplicate.


## Attention hooks inside the explanation — `hook.*`

### `hook.memory_aid` — Commit this to memory  ·  **75 scripts**

A command to store the just-stated fact, phrased as putting it into the brain / tying a knot / stamping it.

**When:** After a number, a ratio, a fixed order, a formula, or a one-line rule. The single most frequent move in the corpus after the gloss.

**Shape:** `<गाँठ बाँध लो|दिमाग में बिठा लो|मन में छाप लो|ज़ुबानी याद कर लो|पक्का कर लो> — <the one thing>`

> “तो Micropyle को एकदम दिमाग में बिठा लो—छोटा pore और pollen tube की entry।”
> — `biology/BIO-C1-LA-01.txt`

> “यानी गाँठ बाँध लो — उत्पादकों में ऊर्जा सबसे अधिक, फिर प्रत्येक अगले पोषण स्तर पर ऊर्जा कम। इसी कारण ऊर्जा का पिरामिड हमेशा सीधा होता है।”
> — `biology/BIO-C12-SA-04.txt`

> ★ "और O वाली बात मन में छाप लो — O में कुछ 'है नहीं', इसीलिए उसे O कहते हैं। यहीं सबसे ज्यादा बच्चे confuse hote हैं।"
> — `biology/BIO-C4-LA-01.txt`

*Note:* Rotate the metaphor; the same script uses two or three different ones. 'गाँठ बाँध लो' attaches to a SENTENCE, 'दिमाग में बिठा लो' to a sequence or pair, 'ज़ुबानी याद कर लो' to a number or ratio.

### `hook.importance` — This is the most important bit  ·  **54 scripts**

Flags one line, one difference or one step as the highest-value thing in the answer.

**When:** Before the conclusion line, before the exam-critical exception, and before the last item of a list.

**Shape:** `<अब सबसे जरूरी बात—|अब आते हैं exam के सबसे important हिस्से पर|यही इस <graph> का सबसे जरूरी निष्कर्ष है>`

> “अब सबसे जरूरी बात—”
> — `biology/BIO-C1-LA-01.txt`

> "अब आते हैं exam के सबसे important हिस्से पर—प्रसव को induce यानी प्रेरित करने वाले hormones।
> — `biology/BIO-C2-SA-04.txt`

> बच्चों, इस असमानता को बिल्कुल मत भूलना—यही इस ग्राफ का सबसे जरूरी निष्कर्ष है।”
> — `chemistry/CHE-C1-LA-02.txt`

*Note:* Used more than once per script, which dilutes it — in BIO-C1-LA-01 three different beats are each 'सबसे जरूरी'. A generator should cap it at one per part.

### `hook.focus_reason` — Listen carefully, because <reason>  ·  **52 scripts**

Raises attention just before a line that must be reproduced, and names why: it is what the examiner wants, or a name/number is coming.

**When:** Before every definition that must be written verbatim, and before the one step of a derivation that carries the rest.

**Shape:** `<ध्यान से सुनना|इसे ध्यान से समझो|अब यहाँ थोड़ा ध्यान देना>, क्योंकि <answer में यही line लिखनी है|यही सबसे important बात है|यहीं से पूरा derivation निकलेगा>`

> “इसकी भी definition ध्यान से सुनना, क्योंकि answer में यही line लिखनी है।”
> — `biology/BIO-C1-LA-01.txt`

> “ध्यान से सुनना, क्योंकि परीक्षा में इसकी परिभाषा से ही शुरुआत करनी है।”
> — `chemistry/CHE-C1-LA-02.txt`

> “अब यहाँ थोड़ा ध्यान देना, क्योंकि यही line exam में conclusion के रूप में लिखनी है।**”
> — `biology/BIO-C5-LA-02.txt`

*Note:* The reason is ALWAYS about the exam answer or about the derivation's dependency chain — never 'because it's interesting'. A bare 'ध्यान से सुनो' with no क्योंकि clause also occurs and reads weaker.

### `hook.exam_payoff` — Write it exactly like this and the marks are yours  ·  **52 scripts**

Ties a specific sentence, order or label to the marks — write it this way and the marks come, change it and they do not.

**When:** Right after a textbook definition, a formula, or a fixed ordering (cell notation, a sequence).

**Shape:** `<परीक्षा में|exam में> <इसे ऐसे ही लिखना है|बिल्कुल ऐसा लिख दोगे> तो <नंबर पक्के हो जाएंगे|नंबर मिलेंगे>`

> और इसको अच्छे से समझना, बिल्कुल ऐसा लिख ​​दोगे तो परीक्षा में नंबर पक्के हो जाएंगे
> — `chemistry/CHE-C2-LA-03.txt`

> ★ "इसमें दो शब्द खास ध्यान रखने वाले हैं — 'पूर्ण' और 'बराबर'। इन्हें उत्तर में सही जगह लिख दिया, तो नंबर पक्के समझो।”
> — `biology/BIO-C4-LA-01.txt`

> “इसे ध्यान से सुनना और याद रखना, क्योंकि परीक्षा में इसे ऐसे ही लिखोगे तो नंबर मिलेंगे।”
> — `chemistry/CHE-C4-LA-03.txt`

*Note:* Often fused with hook.memory_aid in one sentence ('गाँठ बाँध लो और परीक्षा में ऐसे ही लिखना').

### `hook.progress_count` — N done, now the next one  ·  **44 scripts**

Marks off completed items against the count announced in the roadmap, so the student always knows where they are.

**When:** Every counted list — parts of a structure, differences, properties, features, reactions.

**Shape:** `<चलो, एक हो गया?|दो हो गए|तीन गुण तो हो गए,> अब <दूसरा|तीसरा|चौथा और आखिरी> <part|अंतर|गुण>—<नाम>`

> “चलो, एक हो गया? अब दूसरा part—अध्यावरण यानी Integuments।”
> — `biology/BIO-C1-LA-01.txt`

> दो हो गए तीसरा
> — `chemistry/CHE-C3-SA-05.txt`

> “तीन गुण तो हो गए, लेकिन चौथा अभी बाकी है।”
> — `chemistry/CHE-C4-LA-03.txt`

*Note:* The ordinal is Devanagari-spelled (पहला/दूसरा/तीसरा/चौथा) but the running total is often a numeral ('3 अंतर clear हैं') — inconsistent, and a TTS hazard.

### `hook.mistake` — This is where students go wrong  ·  **36 scripts**

Names the specific error students make at this exact point, usually just before the correct version.

**When:** At confusable pairs (anode/cathode, Micropyle/Chalaza), at exceptions, and at the point a shortcut fails.

**Shape:** `<यहाँ|यहीं> बच्चे अक्सर <गलती करते हैं|confuse होते हैं|उलझते हैं> — <गलत रूप>, लेकिन…`

> “यहाँ बच्चे अक्सर गलती करते हैं Micropyle को सिर्फ ‘छेद’ लिखकर छोड़ देते हैं, लेकिन…”
> — `biology/BIO-C1-LA-01.txt`

> “इसे ध्यान से समझना, यहाँ 100 में से 80 बच्चे अक्सर गलती करते हैं।”
> — `chemistry/CHE-C4-LA-03.txt`

> “यहाँ Micropyle और Chalaza को उल्टा मत कर देना—एक तरफ Micropyle, उसके opposite side पर Chalaza।”
> — `biology/BIO-C1-LA-01.txt`

*Note:* Never abstract: the wrong answer is quoted. Absent from all five formal-register scripts and from both no-year Physics derivations.

### `hook.forward_question` — Pose the next question before answering it  ·  **32 scripts**

Asks the question the next paragraph answers, usually starting from something that looks contradictory.

**When:** At the pivot from 'what it is' to 'why it happens', and before each new mechanism step.

**Shape:** `अब <असली सवाल|सवाल ये उठता है कि|सवाल आता है कि> — <प्रश्न>?`

> “अब असली सवाल —अवाष्पशील विलेय मिलाने पर क्वथनांक बढ़ता क्यों है?”
> — `chemistry/CHE-C1-LA-02.txt`

> ★ "अब सवाल ये उठता है कि ये एंटीजन बनते किससे हैं। यहीं से असली उत्तर शुरू होता है।"
> — `biology/BIO-C4-LA-01.txt`

> अब सवाल आता है कि ³²P आखिर DNA तक पहुँचा कैसे? चलो, इसे भी समझ लेते हैं
> — `biology/BIO-C5-LA-02.txt`

*Note:* Distinct from handoff.open_question: this one is answered within seconds, in the same part.

### `hook.mnemonic_trick` — Build the mnemonic, don't just order it remembered  ·  **12 scripts**

Supplies an actual memory device — a word-equation, an initial-letter pairing, or a stripped-down parallel list — rather than just ordering the student to remember.

**When:** Matching tables, long lists, and any set of numbers that must be kept apart.

**Shape:** `<अक्षर/प्रतीक> मतलब <कीवर्ड>; <अक्षर> मतलब <कीवर्ड> … / बस <तीन शब्द> याद रखो — <A>, <B> और <C>। ये याद हैं तो बाकी उत्तर भी याद रहेगा।`

> “चलो, अब पूरी table को एक आसान trick से दिमाग में बैठा लो—A मतलब आँख, D मतलब धूप और हड्डियाँ, E मतलब बन्ध्यता, K मतलब थक्का; C मतलब स्कर्वी, B₁₂ मतलब रक्ताल्पता और फोलिक अम्ल मतलब अरक्तता।”
> — `chemistry/CHE-C10-LA-02.txt`

> “बस एक छोटी-सी trick याद रखो गुणन, वृद्धि और परिपक्वन। ये तीन शब्द याद हैं, तो बाकी उत्तर भी याद रहेगा”
> — `biology/BIO-C2-LA-01.txt`

> और इसे याद रखने की ट्रिक - DNA की चौड़ाई 2 nm, एक पूरा घुमाव 3.4 nm और 10 क्षारक युग्म।”
> — `biology/BIO-C5-LA-03.txt`

*Also catalogued as: teach.mnemonic_pairing*

*Note:* NEW because hook.memory_aid is the imperative ('lock this in') and this is the artefact being locked in. Two distinct sub-forms: the SYMBOL→KEYWORD table (A मतलब आँख), and the FALLBACK SET ('if you can't hold six, hold these three'), which is what a student under exam pressure actually uses. Both ar

### `hook.answer_recipe` — What to write, and in what order  ·  **6 scripts**

Gives the structure of the written answer: which components to include, how many examples, what not to skip.

**When:** Just before the closing CTA, or at the end of a part whose content is one component of the answer.

**Shape:** `तो बच्चों, exam में answer लिखते समय पहले <A>, फिर <B>, और <C> जरूर <दिखाना/लिखना>। सिर्फ <shortcut> लिखकर मत छोड़ देना।`

> "तो बच्चों, exam में answer लिखते समय पहले प्रभाविता के नियम की definition, फिर YY × yy का cross, gametes और F₁ generation जरूर दिखाना।"
> — `biology/BIO-C4-SA-05.txt`

> “और exam में तीनों steps के नाम और reactions जरूर लिखना। सिर्फ final reaction लिखकर मत छोड़ देना।”
> — `chemistry/CHE-C4-LA-01.txt`

> इस प्रश्न में परिभाषा के साथ दो-दो उदाहरण जरूर लिखिए, क्योंकि प्रश्न में प्रत्येक प्रकार के दो उदाहरण मांगे गए हैं।
> — `chemistry/CHE-C10-SA-01.txt`

*Note:* New id: this is the one move that talks about the ANSWER SHEET's structure rather than the content, and it is what the Notes-button CTA is handing off to. Always justified by the question's own wording ('क्योंकि प्रश्न में ... मांगे गए हैं').

### `hook.keyword_lock` — These exact words must not be lost  ·  **5 scripts**

Names the specific words, numbers or ordering in the sentence just spoken that the answer cannot survive without.

**When:** After a definition with technical qualifiers, after a dated/numbered list, and before any ordered preparation.

**Shape:** `बस यहाँ <N> words miss नहीं होने चाहिए—‘<w1>’, ‘<w2>’ और ‘<w3>’।`

> बस यहाँ तीन words miss नहीं होने चाहिए—‘X सहलग्न’, ‘अप्रभावी’ और ‘विकार’।
> — `biology/BIO-C4-LA-03.txt`

> ★ "इसे पूरा लिखना खासकर ये तीन चीज़ें - पुटिकीय अवस्था, एस्ट्रोजन, और 5 से 13 दिन।"
> — `biology/BIO-C2-LA-02.txt`

> ये तीनों नाम क्रम से याद होने चाहिए — क्रम बदला, तो नंबर गया।
> — `chemistry/CHE-C4-LA-01.txt`

*Note:* New id: hook.memory_aid compresses meaning, this one locks SURFACE FORM — the exact tokens the examiner's key contains. On screen it wants the words highlighted individually, not a restated sentence. The ordering variant ('क्रम बदला, तो नंबर गया') applies to preparations and stepwise processes.

### `hook.predict_first` — Ask, then pause for the student to answer  ·  **2 scripts**

Puts a small question to the student and leaves a beat for them to answer before revealing it.

**When:** One script only, on a Punnett-style prediction the student can actually make.

**Shape:** `अब एक छोटा-सा सवाल—<प्रश्न>?
सोचो - सोचो
<उत्तर>`

> अब एक छोटा-सा सवाल—लाल फूल वाले पौधे का सफेद फूल वाले पौधे से संकरण कराएँ, तो संतति में फूल किस रंग के होंगे?, सोचो - सोचो
> — `biology/BIO-C4-LA-01.txt`

> ★ "रुको, एक बार ऊपर वाली सूची से check कर लो । एलील ऊपर, एंटीजन नीचे — दोनों एक ही क्रम में चल रहे हैं। बस यही याद रखना है।"
> — `biology/BIO-C4-LA-01.txt`

> सबसे पहले देखते हैं की चुम्बक के पास रखने पर तीनों का behavior कैसा होता है? पहले guess कीजिए: कौन प्रतिकर्षित होगा, कौन हल्का आकर्षित और कौन जोर से आकर्षित?
> — `physics/PHY-C5-LA-01.txt`

*Also catalogued as: hook.think_pause*

*Note:* NEW and in ONE script only (BIO-C4-LA-01), which is also the most heavily rewritten one (★-marked lines). The second example is its sibling: telling the viewer to look back at the previous ON SCREEN block. Both assume the on-screen text stays up long enough to be re-read.


## ON SCREEN block forms — `screen.*`

### `screen.arrow_chain` — ON SCREEN as an arrow flow, not a sentence  ·  **30 scripts**

The on-screen block is a vertical chain of short labels joined by ↓ and →, or a numbered list with → mappings. It organises what was said; it never repeats the spoken sentence.

**When:** After any process step, any cause-effect link, and any 'A becomes B' statement.

**Shape:** `ON SCREEN:
<पद A> → <पद B> → <पद C>
(या ऊर्ध्वाधर: <पद A>\n↓\n<पद B>\n↓\n<पद C>)`

> ON SCREEN: पूरी प्रक्रिया जीन में उत्परिवर्तन ↓ HbS का निर्माण ↓ दात्राकार RBCs ↓ रक्त प्रवाह में बाधा ↓ ऑक्सीजन की कमी
> — `biology/BIO-C4-SA-03.txt`

> ON SCREEN: अपघटन की 5 अवस्थाएँ: 1. खण्डन → 2. प्रक्षालन → 3. अपचय → 4. ह्यूमीकरण → 5. खनिजीभवन
> — `biology/BIO-C12-SA-01.txt`

> [ON SCREEN: अनावेशन → PbSO₄ जमा ↑ → H₂SO₄ सांद्रता ↓ → घनत्व ↓]
> — `chemistry/CHE-C2-SA-07.txt`

*Also catalogued as: teach.onscreen_flowchart*

*Note:* Horizontal → for a sequence that fits on a line, vertical ↓ for a causal chain of 3+ links. ↑ and ↓ are also used INLINE as 'increases'/'decreases' markers, which is a different meaning of the same glyph in the same block (CHE-C2-SA-07). The arrow chain almost always restates the spoken sentence in 

### `screen.revision_table` — Closing revision table  ·  **14 scripts**

A final on-screen block holding the whole answer as a table or numbered summary, read out loud item by item as the last teaching act.

**When:** End of the final part of every difference and list question.

**Shape:** `On Screen:
आधार | <A> | <B>
<अक्ष 1> | <…> | <…>
<अक्ष 2> | <…> | <…>
“<हर पंक्ति क्रम से बोली जाती है>”`

> ON SCREEN: आनुवंशिक कूट की 4 विशेषताएँ: 1. त्रिकूट → 3 न्यूक्लियोटाइड का एक कोडॉन 2. असंदेहास्पद एवं विशिष्ट → एक कोडॉन का एक निश्चित अर्थ 3. कोमा रहित एवं अनतिव्यापी → कोई विराम चिह्न नहीं, कोडॉन overlap नहीं करते 4. अपह्रासित / डीजेनरेट → एक अमीनो अम्ल के कई कोडॉन
> — `biology/BIO-C5-SA-04.txt`

> ON SCREEN: Quick Revision उल्बवेधन उल्ब द्रव का नमूना ↓ भ्रूणीय कोशिकाएँ ↓ गुणसूत्रीय / आनुवंशिक जाँच ↓ प्रसवपूर्व निदान कानूनी बिंदु चिकित्सीय निदान → विनियमित लिंग निर्धारण → प्रतिबंधित लिंग चयन → प्रतिबंधित
> — `biology/BIO-C3-SA-01.txt`

> On Screen: आधार DNA RNA संरचना द्वि-हैलिक्स एकल-हैलिक्स
> — `chemistry/CHE-C10-SA-05.txt`

*Also catalogued as: end.revision_card*

*Note:* In CHE-C10-SA-05 and CHE-C10-SA-09 the table is stored as tab-indented lines in a single column — it will NOT render as a table without being re-parsed into rows. BIO-C4-LA-02's Punnett square is a markdown pipe table, a third incompatible encoding. A generator must emit one structured table form, n

### `screen.equation_block` — ON SCREEN as a bare equation  ·  **10 scripts**

One algebraic step, nothing else, typeset on screen — always immediately followed by its spoken gloss.

**When:** Every step of every derivation and numerical.

**Shape:** `ON SCREEN
<एक समीकरण>
स्पोकन:
"<उच्चारण>"`

> ON SCREEN E = 1/(4πε₀) × p/r³
> — `physics/PHY-C1-NM-02.txt`

> [ON SCREEN: R = ρ × l/A]
> — `chemistry/CHE-C2-SA-03.txt`

> ON SCREEN: t₁/₂ = 0.693 / k
> — `chemistry/CHE-C3-SA-06.txt`

*Note:* One equation per block, never two — even when two are logically one step (PHY-C2-NM-03 does put V₁/V₂/V₃ together, which is the exception). Unicode is used throughout (ε₀, ⁻, ₂, ³ᐟ², ∝, ≈, ≪) and must survive to the renderer; the repo's Hindi/LaTeX split means these blocks cannot be typeset through 

### `screen.compare_pair` — ON SCREEN as a two-line A/B pair  ·  **6 scripts**

Two lines, one per compared item, on the same axis — the on-screen unit of every difference question.

**When:** After each point of a teach.compare sequence.

**Shape:** `ON SCREEN:
<A> → <गुण A>
<B> → <गुण B>`

> ON SCREEN: लघुबीजाणुजनन → लघुबीजाणुधानी के भीतर गुरुबीजाणुजनन → बीजांड के भीतर
> — `biology/BIO-C1-LA-02.txt`

> On Screen: DNA → डी-ऑक्सीराइबोस शर्करा RNA → राइबोस शर्करा
> — `chemistry/CHE-C10-SA-05.txt`

> ON SCREEN: A = T → 2 hydrogen bonds C ≡ G → 3 hydrogen bonds हर pair में → 1 प्यूरीन + 1 पिरीमिडीन
> — `biology/BIO-C5-LA-03.txt`

*Note:* The two lines are always in the SAME order across every point of the video (A first, B second), which is what lets the student read down the column. Breaking that order in one block would silently swap the answer.


## Part endings (non-final) — `handoff.*`

### `handoff.done_plus_left` — X is done, Y is left, that's next part  ·  **62 scripts**

Closes a non-final part by banking what is finished and naming exactly what remains, usually with the count.

**When:** Every multi-part script; the counting form is used whenever the roadmap was counted.

**Shape:** `<तो बच्चों,> <यहाँ तक|इतना> <A और B> <हो गया|समझ लिए>। अब <C और D> <क्या होते हैं,> ये <देखेंगे|समझेंगे> Part <N+1> में।`

> “तो बच्चों, यहाँ तक बीजाण्ड के दो main parts बीजाण्डवृन्त और अध्यावरण समझ लिए।” “अब बीजाण्डद्वार और बीजाण्डकाय क्या होते हैं, ये देखेंगे Part 2 में।”
> — `biology/BIO-C1-LA-01.txt`

> “बच्चों, पहला गुण हो गया। लेकिन अभी तीन और बाकी हैं।”
> — `chemistry/CHE-C4-LA-03.txt`

> “तो बच्चों, इतना तो समझ लिया कि विलेय मिलाने पर क्वथनांक क्यों बढ़ता है। अब इसे क्वथनांक में उन्नयन क्यों कहते हैं, इसका सूत्र क्या है और इसे परीक्षा में कैसे लिखना है—ये देखेंगे अगले पार्ट में।”
> — `chemistry/CHE-C1-LA-02.txt`

*Note:* CHE-C1-LA-02 labels this beat in the file itself ('Part 1 Ending:') — the only script that does. The 'what is left' half is always specific; a vague 'बाकी आगे देखेंगे' does not occur.

### `handoff.watch_next` — Explicitly tell them to watch Part N  ·  **29 scripts**

An explicit imperative to watch the next part, usually with the reason (the important bit is in there).

**When:** Every multi-part Biology script and the longer Chemistry ones; absent from the Physics derivations, which just say what the next part will do.

**Shape:** `इसलिए Part <N+1> <जरूर देखना|देखना मत भूलना|miss mat karna>`

> “**लेकिन पूरा diagram यहीं खत्म नहीं होता। next part में जैविक घटकों के तीनों हिस्से—उत्पादक, उपभोक्ता और अपघटक samjhenge। इसलिए Part 2 जरूर देखना।**”
> — `biology/BIO-C12-LA-03.txt`

> “Next part में इन्हें समझेंगे और पूरा arrangement भी clear करेंगे तो part 4 देखना मत भूलना
> — `biology/BIO-C1-LA-01.txt`

> “पूरे answer के लिए Part 2 जरूर देखना, क्योंकि अब अगला important गुण शुरू होगा।”
> — `chemistry/CHE-C4-LA-03.txt`

*Note:* Frequently written in Romanised Hindi ('part 2 dekhna bhulna mat', 'part 3 miss mat karna') even in scripts that are otherwise fully Devanagari — these lines look like a later hand-patch.

### `handoff.open_question` — Leave a question the next part answers  ·  **21 scripts**

Ends a part on an unanswered question, explicitly promising the answer in the next part.

**When:** Used where the next part carries the conceptual punchline (the reason, the second case, the conclusion) rather than just the next list item.

**Shape:** `<लेकिन> <एक बात अब भी अधूरी है> — <सवाल>? <वो जवाब|इसका जवाब> Part <N+1> में है`

> ★ " अभी तक तो सिर्फ एंटीजन और एलील की बात हुई है। पर एक बात अब भी अधूरी है — सह-प्रभाविता आखिर दिखती कहाँ है? वो जवाब Part 2 में है, और वहीं से नंबर बनते हैं। to part 2 dekhna bhulna mat।"
> — `biology/BIO-C4-LA-01.txt`

> “लेकिन अब तीसरी अभिक्रिया में concentration की power fraction में दी गई है। तो क्या इसकी order भी fraction में होगी?”
> — `chemistry/CHE-C3-SA-09.txt`

> “लेकिन अगर कुण्डली में एक से ज्यादा turns हों, तो field कैसे बदलेगा? ये समझते हैं Part 3 में।”
> — `physics/PHY-C4-NM-01.txt`

*Note:* In Biology the open question is conceptual; in Physics/Chemistry it is the next algebraic obstacle ('fraction power', 'n turns'). Only BIO-C4-LA-01 actually re-asks it at the top of the next part.

### `handoff.next_part_preview` — Neutral preview of the next step, no watch-imperative  ·  **13 scripts**

The handoff states the exact operation the next part will perform, with no cliffhanger and no watch-instruction.

**When:** Derivations and worked-example scripts, where the next part is a continuation of one calculation.

**Shape:** `तो Part <N+1> में <इसी E और d की मदद से विभवान्तर निकालेंगe|इस formula को final form में लिखेंगे और पूरे derivation का flow एक बार recall करेंगे>।`

> "Part 3 में इस formula को final form में लिखेंगे और पूरे derivation का flow एक बार recall करेंगे।"
> — `physics/PHY-C2-SA-01.txt`

> “अब इस bracket को simplify करेंगे। ये step ध्यान से देखना, क्योंकि यहीं से पूरा derivation आगे निकलेगा।” “तो इसे समझते हैं Part 2 में।”
> — `physics/PHY-C1-NM-01.txt`

> अब इन्हीं अंतर को परीक्षा में लिखने योग्य छोटे और स्पष्ट रूप में एक साथ दोहराएँगे, ताकि यह प्रश्न आसानी से याद हो जाए। यही Part 2 में करेंगे।
> — `chemistry/CHE-C10-SA-04.txt`

*Also catalogued as: handoff.next_part_agenda*

*Note:* NEW: a derivation cannot be cut at a cliffhanger without cutting an equation in half, so the handoff is procedural instead. The part boundary always falls just BEFORE a simplification step, never mid-substitution.

### `handoff.exam_writing_part` — The next part is about HOW TO WRITE the answer  ·  **3 scripts**

Promises that the remaining part is not new content but the exam write-up of what was just taught.

**When:** Derivation and method questions where the board expects a specific written order.

**Shape:** `अब इसका पूरा answer परीक्षा में कैसे लिखना है, वो समझेंगे next part में।`

> “अब इसका पूरा answer परीक्षा में कैसे लिखना है, वो समझेंगे next part में।
> — `chemistry/CHE-C3-LA-01.txt`

> “अब क्षारीय और उदासीन माध्यम में क्या होता है,और इसका पूरा answer परीक्षा में कैसे लिखना है, वो समझेंगे next part में।
> — `chemistry/CHE-C4-LA-02.txt`

*Note:* Only CHE-C3-LA-01 actually delivers it (its Part 2 replays Part 1's derivation line-for-line as the written answer). In CHE-C1-LA-01 and CHE-C4-LA-02 the promise is made and then silently dropped — a generator should either deliver it or not promise it.

### `handoff.incomplete_threat` — Skip this part and your answer is incomplete  ·  **2 scripts**

Raises the stakes of the handoff by saying the ANSWER will be incomplete, not merely that the video continues.

**When:** Long Biology answers where the last part carries the conclusion or the F2 ratio.

**Shape:** `और अगर part <N+1> नहीं देखोगे तो answer अधूरा रह जाएगा इसलिए जरूर देखना`

> ★ "बच्चों इतना तो हो गया लेकिन और अभी एक बहुत जरूरी सवाल बाकी है — जब रंग घुल ही गया, तो क्या ये मिश्रित वंशागति कहलाएगी? इसका जवाब और F₂ का अनुपात Part 3 में है। और अगर part 3 नहीं देखोगे तो answer अधूरा रह जाएगा इसलिए जरूर देखना
> — `biology/BIO-C4-LA-01.txt`

> “**लेकिन final conclusion अभी बाकी है। तो दूसरा case भी clear हो गया। अब experiment का पूरा proof हमारे सामने है और ये part छोड़ा तो question का सबसे important conclusion छूट जाएगा। इसलिए part 3 miss mat karna.
> — `biology/BIO-C5-LA-02.txt`

*Note:* NEW: stronger than handoff.watch_next — the cost is framed as marks lost in the exam, not as missing a video. Two files only.


## Closings (final part) — `end.*`

### `end.notes_button` — The exact answer is on the Notes button  ·  **103 scripts**

Sends the student to the Notes button on screen for the written answer. The single most stable line in the corpus.

**When:** The mandatory CTA of the final part; present in 26 of 28 scripts.

**Shape:** `अब <परीक्षा में> इसका exact answer <exam में> कैसे लिखना है, वो आपकी स्क्रीन के right side में दिए Notes button पर <click करके> मिल जाएगा।`

> अब परीक्षा में इसका exact answer कैसे लिखना है, वो आपकी स्क्रीन के right side में दिए Notes button पर मिल जाएगा।
> — `biology/BIO-C12-SA-04.txt`

> अब इसका exact answer exam में किस तरह लिखना है, वो आपको Notes button पर click करके मिल जाएगा।
> — `chemistry/CHE-C10-SA-08.txt`

> अब इसका exact answer exam में कैसे लिखना है, ये आपको Notes में मिल जाएगा।
> — `chemistry/CHE-C2-SA-06.txt`

*Note:* Two wordings: the long one naming the right side of the screen (12 files, all recent) and the short 'Notes button पर click करके' (the rest). CHE-C2-SA-06 degrades it to just 'Notes में'. The two oldest Chemistry scripts replace it entirely with NEW.end.answer_on_screen.

### `end.keep_watching` — Keep watching the study reels  ·  **75 scripts**

Closes by telling the student to keep watching, framed as covering the syllabus one question at a time.

**When:** Immediately after the Notes button line.

**Shape:** `अब ऐसे ही आगे की पढ़ाई वाली reels देखते रहो`

> अब ऐसे ही आगे की पढ़ाई वाली reels देखते रहो, एक-एक करके syllabus पूरा करते जाओ और 90% की तैयारी मजबूत करो।”
> — `biology/BIO-C12-SA-04.txt`

> "बच्चों, 4 नंबर की तैयारी हो गई। अब अगली पढ़ाई वाली reel में मिलते हैं। ऐसे ही एक-एक topic पक्का करते चलो और अपना पूरा syllabus भी cover करते चलो।"
> — `physics/PHY-C2-NM-02.txt`

> "अब आगे की पढ़ाई वाली reels देखो, एक-एक करके syllabus पूरा करो और 90% की तैयारी मजबूत करो।"
> — `biology/BIO-C1-LA-02.txt`

*Note:* Almost always fused with end.goal in the same sentence; they are effectively one 20-word closing line with slot-swappable halves.

### `end.goal` — Finish the syllabus, push to 90%  ·  **59 scripts**

Names the target — 90%, syllabus complete, Board Exam preparation strong — as the reason to keep going.

**When:** The last line of the video.

**Shape:** `एक-एक करके syllabus पूरा करते जाओ और 90% की तैयारी मजबूत करो।`

> “अब ये सवाल हो गया, ऐसे ही आगे की पढ़ाई वाली reels देखो, एक-एक करके syllabus पूरा करो और 90% की तैयारी मजबूत करो।”
> — `biology/BIO-C1-LA-01.txt`

> “अब 4 नंबर यहाँ पक्के हो गए, आगे की पढ़ाई वाली reels भी देखते रहो—एक-एक करके पूरा syllabus तैयार करते जाओ और 90%+ की तरफ बढ़ते जाओ।
> — `chemistry/CHE-C10-LA-01.txt`

> “और ऐसे ही important derivations को समझते जाओ और एक-एक करके अपना syllabus complete करते जाओ।”
> — `physics/PHY-C1-NM-01.txt`

*Note:* The Physics derivation scripts drop the 90% and say 'important derivations को समझते जाओ' instead; Chemistry writes '90%+' with the plus. The subject-specific noun (reels / derivations / Chemistry topic / question) is the only part that varies.

### `end.recap` — Final summary before the CTA  ·  **50 scripts**

One or two sentences compressing the whole answer into its headline facts, spoken just before the Notes CTA.

**When:** Final part of most scripts; skipped in a few short ones that go straight to the Notes button.

**Shape:** `तो बच्चों, पूरे <प्रश्न|answer> को एक बार <जल्दी से|संक्षेप में> revise कर लेते हैं। <सब कुछ एक-दो वाक्य में>`

> "तो बच्चों, पूरे answer को एक बार जल्दी से revise कर लेते हैं।"
> — `biology/BIO-C2-SA-04.txt`

> तो बच्चों, पूरे प्रश्न को एक बार संक्षेप में याद कर लेते हैं।
> — `chemistry/CHE-C10-SA-08.txt`

> “तो बच्चों, अब पूरे प्रश्न की चारों बातें एक बार याद कर लेते हैं।”
> — `chemistry/CHE-C4-LA-03.txt`

*Note:* Order of the recap always matches the order of the roadmap and of the teaching. Often carried by a 'Quick Revision' ON SCREEN card.

### `end.memory_promise` — Remember this much and you'll never forget it in the exam  ·  **27 scripts**

Ties the closing to a promise of permanent recall, conditional on the small thing just recapped.

**When:** After the recap, before the Notes button.

**Shape:** `बच्चों, बस इतना याद रख लिया<।|,> तो परीक्षा में <कभी नहीं भूलोगे|पूरा उत्तर कभी नहीं भूलोगे>।`

> “बच्चों, बस इतना याद रख लिया। तो परीक्षा में कभी नहीं भूलोगे।”
> — `chemistry/CHE-C1-LA-02.txt`

> “बच्चों, बस इतना याद रख लिया, तो परीक्षा में डेनियल सेल का पूरा उत्तर कभी नहीं भूलोगे।”
> — `chemistry/CHE-C2-LA-03.txt`

> बस इतना कर लिया, तो परीक्षा में ये सवाल कभी नहीं छूटेगा।
> — `chemistry/CHE-C2-LA-04.txt`

*Note:* Chemistry-heavy. Biology uses hook.memory_aid mid-script instead and skips this.

### `end.marks_banked` — Those N marks are banked, now go get the rest  ·  **19 scripts**

Closes by declaring the question's marks secured, cashing the promise made in intro.marks_promise.

**When:** Physics derivations and the Chemistry long answers that opened with a marks promise.

**Shape:** `बच्चों, <n> नंबर की तैयारी हो गई।`

> "बच्चों, 4 नंबर की तैयारी हो गई। अब अगली पढ़ाई वाली reel में मिलते हैं। ऐसे ही एक-एक topic पक्का करते चलो और अपना पूरा syllabus भी cover करते चलो।"
> — `physics/PHY-C2-NM-02.txt`

> “अब 4 नंबर यहाँ पक्के हो गए, आगे की पढ़ाई वाली reels भी देखते रहो
> — `chemistry/CHE-C10-LA-01.txt`

> तो बच्चों, आज का 4 नंबर वाला सवाल भी पूरा तैयार है।”
> — `biology/BIO-C4-LA-02.txt`

*Also catalogued as: end.marks_locked*

*Note:* NEW: intro.marks_promise's paired closer. If a script opens with a marks promise it should close with this; CHE-C10-LA-01 is the only one in the group that does both.

### `end.question_closed` — And that question is done  ·  **18 scripts**

An explicit closure line naming the question by its topic and declaring it finished, placed between the recap and the Notes CTA.

**When:** Final part, immediately before end.notes_button.

**Shape:** `तो बच्चों, <प्रश्न का नाम> वाला सवाल भी पूरा हो गया।`

> "तो बच्चों, प्रसव यानी Parturition वाला सवाल भी पूरा हो गया।"
> — `biology/BIO-C2-SA-04.txt`

> “तो बच्चों, जेनेटिक कोड वाला सवाल भी पूरा हो गया।
> — `biology/BIO-C5-SA-03.txt`

> तो बच्चो ये topic तो दिमाग में बैठ गया
> — `chemistry/CHE-C4-SA-04.txt`

*Also catalogued as: end.question_done*

*Note:* NEW: the taxonomy has end.recap and the CTAs but not this hinge line, which exists to close the loop opened by intro.board_year_repeat ('ये सवाल… पूछा गया था' -> 'ये सवाल भी पूरा हो गया'). Always names the question by its topic, not by its number.

### `end.unnati_batch` — Join the Unnati batch  ·  **7 scripts**

Older sign-off that advertises the Arivihan उन्नति बैच instead of the Notes button.

**When:** The two oldest Chemistry scripts only.

**Shape:** `और ऐसे ही आसान और मजेदार तरीके से पढ़ने के लिए अरिविहान के 'उन्नति बैच' से जुड़ें।`

> “और ऐसे ही आसान और मजेदार तरीके से पढ़ने के लिए अरिविहान के ‘उन्नति बैच’ से जुड़ें।”
> — `chemistry/CHE-C1-LA-02.txt`

> “और ऐसे ही आसान और मजेदार तरीके से पढ़ने के लिए अरीविहान के ‘उन्नति बैच’ से जुड़ें ।[b]”
> — `chemistry/CHE-C2-LA-03.txt`

> [b]judein
> — `chemistry/CHE-C2-LA-03.txt`

*Note:* The brand is spelled two different ways ('अरिविहान' / 'अरीविहान') across the two files, and CHE-C2-LA-03 carries a reviewer comment '[b]judein' correcting 'जुड़ें'. DEPRECATED — do not generate; use end.keep_watching + end.goal.

### `end.screenshot` — Save it / take a screenshot  ·  **7 scripts**

Tells the student to screenshot the answer card that is about to appear, instead of pointing at a Notes button.

**When:** Only where the answer appears on screen rather than behind a Notes button.

**Shape:** `इसे सेव कर लेना और स्क्रीनशॉट लेना मत भूलना।`

> “इसे सेव कर लेना और स्क्रीनशॉट लेना मत भूलना।”
> — `chemistry/CHE-C1-LA-02.txt`

> “इसे सेव कर लेना और इसका स्क्रीनशॉट लेना मत भूलना।”
> — `chemistry/CHE-C2-LA-03.txt`

> “अब इसे परीक्षा में पूरा और सही तरीके से कैसे लिखना है, इसका उत्तर आपकी स्क्रीन पर आ जाएगा।” “इसे SAVE कर लेना और स्क्रीनशॉट लेना मत भूलना।”
> — `chemistry/CHE-C1-NM-02.txt`

*Note:* Always paired with NEW.end.answer_on_screen; never with end.notes_button. DEPRECATED alongside it.

### `end.answer_format_advice` — How to lay the answer out on the page  ·  **7 scripts**

Tells the student the SHAPE of the written answer — a table, a numbered list, this exact step order, a figure with labels.

**When:** Difference questions (table), derivations (step order), list questions (points), diagram questions (figure).

**Shape:** `तो exam में <इन चार differences को साफ-साफ लिखिए — <अक्ष 1>, <अक्ष 2>, <अक्ष 3>, <अक्ष 4>> / <इस question को exam में table के रूप में लिखना सबसे आसान रहेगा> / <इन steps को इसी क्रम में लिखना>।`

> आज का question बहुत important है, क्योंकि इसमें आपसे द्विक-लवण और संकुल-लवण के बीच अंतर पूछा गया है। इस question को exam में table के रूप में लिखना सबसे आसान रहेगा।
> — `chemistry/CHE-C5-SA-04.txt`

> तो exam में इन चार differences को साफ-साफ लिखिए—जल में व्यवहार, स्थायित्व, गुण और सूत्र लिखने का तरीका।
> — `chemistry/CHE-C5-SA-04.txt`

> “अब इस पूरे answer में definition, वर्गीकरण और ये सारे बीमारी और विटामिन के connections exam में लिखने हैं।”
> — `chemistry/CHE-C10-LA-02.txt`

*Note:* NEW: procedural, not motivational, so it is distinct from hook.exam_payoff. BIO-C3-SA-01's variant is the strongest — it dictates the literal opening clause of the answer for EACH of the question's alternative phrasings (हाँ, … आवश्यक है). Can appear at the top (CHE-C5-SA-04 announces 'write it as a

### `end.answer_on_screen` — The answer will appear on your screen (older CTA)  ·  **4 scripts**

Older sign-off: instead of a Notes button, the full written answer appears on screen and the student is told to save it and screenshot it.

**When:** The two oldest Chemistry scripts.

**Shape:** `अब इसे परीक्षा में <सही तरीके से> कैसे लिखना है, इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।`

> “अब इसे परीक्षा में सही तरीके से कैसे लिखना है, इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।”
> — `chemistry/CHE-C1-LA-02.txt`

> “अब इसे परीक्षा में कैसे लिखना है, इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।”
> — `chemistry/CHE-C2-LA-03.txt`

> “अब इसे परीक्षा में कैसे लिखना है, इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।” “इसे सेव कर लेना और इसका स्क्रीनशॉट लेना मत भूलना।”
> — `chemistry/CHE-C2-LA-01.txt`

*Note:* NEW: it is the answer-card CTA, and it implies a rendered answer card at the tail of the video (the repo's answer_outro). end.notes_button implies no card. A generator must pick the one that matches what the video will actually ship.

### `end.year_repeat_reminder` — Reminder: this has been asked N times  ·  **2 scripts**

Repeats the exam-year fact at the END as the reason to practise writing it, not just watch.

**When:** Questions with three or more recorded years.

**Shape:** `और बच्चों, ये सवाल <N> अलग-अलग वर्षों—<वर्ष सूची>—में आ चुका है। इसलिए इसे सिर्फ पढ़कर मत छोड़ना, परीक्षा में लिखने की practice भी करना।`

> “और बच्चों, ये सवाल चार अलग-अलग वर्षों—2019, 2020, 2022 और 2024—में आ चुका है। इसलिए इसे सिर्फ पढ़कर मत छोड़ना, परीक्षा में लिखने की practice भी करना।”
> — `chemistry/CHE-C2-NM-01.txt`

> यह प्रश्न 2019 और 2022 में बोर्ड परीक्षा में पूछा जा चुका है, इसलिए इसकी परिभाषा और ज्विटर आयन की संरचना जरूर पक्की कर लीजिए।
> — `chemistry/CHE-C10-SA-06.txt`

*Note:* New id: it is the bookend of intro.board_year_repeat and turns the same fact into an instruction to practise. Only generate it when the year list is genuinely long — repeating a single year at the end reads as padding.


## Register and address — `tone.*`

### `tone.address` — How the student is addressed  ·  **111 scripts**

Second-person plural बच्चों throughout, with the full ‘MP Board कक्षा 12वीं के बच्चों!’ as the opening vocative and occasional बेटा for encouragement.

**When:** Every script. 'बच्चों' opens and punctuates; 'बेटा' appears only as a warm aside after a hard stretch.

**Shape:** `<MP Board कक्षा 12वीं के बच्चों!> … <तो बच्चों,> … <तो यहाँ तक तो बेटा कर लिया>`

> “तो यहाँ तक तो बेटा कर लिया, मतलब, बीजाण्ड के main parts और भ्रूण कोष की basic structure समझ आ गई।”
> — `biology/BIO-C1-LA-01.txt`

> ★ "तो यहाँ तक तो बेटा कर लिया"
> — `biology/BIO-C4-LA-01.txt`

> ★ “अब यहाँ तक तो बेटा कर लिया! मतलब पहली प्रावस्था हो गई।”
> — `biology/BIO-C2-LA-01.txt`

*Note:* 'बच्चों' appears in all 28 files; 'बेटा' in 2, both times as 'तो यहाँ तक तो बेटा कर लिया' — a fixed phrase, not a free variable. 'यार' and 'मेरे बच्चों' do not occur in this group. One script names the presenter in the speaker tag ('Ritesh Sir:', PHY-C3-SA-01).

### `tone.english_mixing` — Where English is used, and in which script  ·  **111 scripts**

Technical nouns, exam vocabulary and connectives are English in Latin script inside Devanagari sentences; the same terms are given in Devanagari when they are the textbook term.

**When:** Every script. The split is systematic, not random.

**Shape:** `<Devanagari sentence> <English noun in Latin> <Devanagari verb>`

> “इसकी भी definition ध्यान से सुनना, क्योंकि answer में यही line लिखनी है।”
> — `biology/BIO-C1-LA-01.txt`

> “अब दूसरा part अध्यावरण यानी Integuments।”
> — `biology/BIO-C1-LA-01.txt`

> “यानी बच्चों, सबसे नीचे producers और ऊपर consumers होते हैं।
> — `biology/BIO-C12-SA-04.txt`

*Note:* Rules visible in the data: (1) exam/meta vocabulary is ALWAYS English — exam, answer, definition, important, confusion, point, part, revise, trick, order, unit; (2) the textbook term is given Devanagari-first then English after यानी ('अध्यावरण यानी Integuments') — that pairing is a fixed idiom; (3) 

### `tone.command_soft` — तुम-form imperatives (and the आप-form exception)  ·  **96 scripts**

Instructions are given in the familiar तुम form — समझ लो, देख लो, बैठा लो — except in one cluster of chemistry scripts that uses the polite आप form throughout.

**When:** Everywhere except the five formal-register scripts, which use आप-forms (समझिए, याद कर लीजिए, ध्यान रखें).

**Shape:** `<समझ लो|देखो|याद रख लो|मत भूलना|पक्का कर लो>`

> “तो सबसे पहले समझ लो—आवृतबीजियों में प्रतीप बीजाण्ड सबसे सामान्य प्रकार का बीजाण्ड होता है।
> — `biology/BIO-C1-LA-01.txt`

> यह प्रश्न 2019 में बोर्ड परीक्षा में पूछा जा चुका है, इसलिए इसकी परिभाषा और तीनों उपयोग जरूर याद कर लीजिए।
> — `chemistry/CHE-C10-SA-08.txt`

> “इसे दिमाग में बिठा लो।” “पहले धातु की ऑक्सीकरण अवस्था और d-विन्यास निकालो।”
> — `chemistry/CHE-C5-LA-01.txt`

*Note:* The two registers never mix inside one script. The second example shows the formal alternative (याद कर लीजिए) — a generator must pick one register per script and hold it.

### `tone.warmth` — Reassurance and praise  ·  **27 scripts**

Small pats on the back that reward progress and keep the student from disengaging mid-part.

**When:** After a dense stretch, and at part boundaries.

**Shape:** `<तो यहाँ तक तो बेटा कर लिया|तो बच्चों, ये answer आपको अच्छे से समझ आ गया है|चलो बच्चों, derivation भी clear और concept भी clear हो गया>`

> तो बच्चों, ये answer आपको अच्छे से समझ आ गया है
> — `biology/BIO-C12-LA-03.txt`

> "चलो बच्चों, संधारित्र भी clear और उसका पूरा derivation भी clear हो गया।"
> — `physics/PHY-C2-SA-01.txt`

> तो बच्चो ये topic तो दिमाग में बैठ गया
> — `chemistry/CHE-C4-SA-04.txt`

*Note:* Warmth is always ACHIEVEMENT-framed ('you got this far'), never sympathy ('don't be scared'). No script in this group opens by reassuring a frightened student.

### `tone.romanised_hindi` — Hindi written in Latin script mid-sentence  ·  **12 scripts**

Stretches of Hindi written in Roman letters inside otherwise Devanagari lines, usually in the newest or most-edited passages.

**When:** Three Biology scripts; concentrated in transitions and handoffs.

**Shape:** `<Devanagari clause> <romanised hindi clause> <Devanagari clause>`

> तो bacho itna ho gaya
> — `biology/BIO-C12-LA-03.txt`

> अब यहीं experiment का main सवाल aata hai ki - अंदर आखिर क्या गया? DNA या protein?”
> — `biology/BIO-C5-LA-02.txt`

> तो चलो सबसे पहले समझते हैं कि तालाब का पारितंत्र होता क्या है, और exam me bilkul ese hi likhna hai -
> — `biology/BIO-C12-LA-03.txt`

*Note:* NEW: this is authoring noise, not style — the presenter reads it aloud identically either way, but a TTS or a parser will not. A generator should emit Devanagari only; record the type so the pattern is recognised when reading existing scripts, not reproduced.

### `tone.formal_aap` — आप-form, no teacher tag, no hooks  ·  **9 scripts**

A distinct register in four chemistry scripts: आप-form verbs (कीजिए, लिखिए, समझिए, याद रखिए), no शिक्षक: tags, no ★ asides, no mistake flags, no warmth — a narrated caption track rather than a class.

**When:** CHE-C10-SA-05, CHE-C10-SA-09, CHE-C5-SA-04, CHE-C5-SA-08 — all late chemistry SA scripts, all with no year cited.

**Shape:** `<प्रश्न> … <बिंदु> … On Screen: <ब्लॉक> … “<द्विभाषी echo>” … <इसलिए इन चारों … जरूर पक्के कर लीजिए।>`

> यह प्रश्न 2014 और 2016 में बोर्ड परीक्षा में पूछा जा चुका है, इसलिए इनके कार्यों को अच्छे से याद कर लीजिए।
> — `chemistry/CHE-C10-SA-09.txt`

> तो बच्चों, DNA और RNA के बीच अंतर याद रखने के लिए संरचना, शर्करा, क्षार, स्थान और कार्य—इन मुख्य बिंदुओं को जरूर याद रखिए।
> — `chemistry/CHE-C10-SA-05.txt`

> सबसे पहले इसकी परिभाषा समझिए।
> — `chemistry/CHE-C5-SA-08.txt`

*Also catalogued as: tone.formal_aap_register*

*Note:* NEW: this is a different VOICE, not a variation of tone.command_soft, and a generator that averages the corpus will produce an incoherent blend of both. These four scripts also drop end.keep_watching and end.goal. They read flatter than the rest — if the house voice is the तुम-form teacher, these ar
