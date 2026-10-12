# POL-C3-LA-02 — accuracy brief

**Question:** नेपाल में लोकतंत्र कैसे स्थापित हुआ? विस्तारपूर्वक समझाइए। (MP Board 2025, 4 अंक)
**Source:** NCERT कक्षा 12, समकालीन विश्व राजनीति, अध्याय 3 "समकालीन दक्षिण एशिया", the section on Nepal.
**Written:** 2026-10-07, before the storyboard (PROCESS_ARTS.md rule 7).

## 1. The script against NCERT

| The script says | NCERT / record | Verdict |
|---|---|---|
| नेपाल अतीत में हिंदू-राज्य, आधुनिक काल में लंबे समय तक संवैधानिक राजतंत्र | Same sentence in NCERT | agrees |
| दल और जनता खुले और उत्तरदायी शासन की माँग उठाते रहे | NCERT: "ज़्यादा खुले और उत्तरदायी शासन की आवाज़ उठाते रहे" | agrees |
| राजा ने सेना की मदद से शासन की सारी शक्तियाँ हाथ में लीं, लोकतंत्र की राह रुक गई | NCERT: "सेना की सहायता से शासन पर पूरा नियंत्रण… लोकतंत्र की राह अवरुद्ध" | agrees |
| 1990: आंदोलन के दबाव में नए लोकतांत्रिक संविधान की माँग माननी पड़ी | NCERT, 1990 | agrees |
| लोकतांत्रिक सरकारों का कार्यकाल छोटा, समस्याओं से भरा | NCERT | agrees |
| 2002: राजा ने संसद भंग की, सरकार को बेदखल किया | NCERT, 2002 | agrees |
| अप्रैल 2006: देशव्यापी लोकतंत्र-समर्थक प्रदर्शन; राजा ज्ञानेन्द्र ने संसद बहाल की | NCERT | agrees |
| "अप्रैल 2002 में भंग की गई संसद" (part 2) | NCERT prints "अप्रैल 2002". The dissolution itself was on 22 May 2002. | **follows NCERT; kept.** On screen we show only **2002**, never the month, so nothing we typeset is wrong either way. |
| प्रतिरोध मोटे तौर पर अहिंसक; नेतृत्व: सात दलों का गठबंधन, माओवादी, सामाजिक कार्यकर्ता | NCERT | agrees |
| संविधान-सभा का गठन; माओवादी सशस्त्र संघर्ष छोड़कर लोकतांत्रिक राजनीति में | NCERT (संविधान-सभा, माओवादियों का मुख्यधारा में आना) | agrees |
| 240 वर्षों की राजशाही का अंत, 28 मई 2008 | Shah monarchy from 1768; republic declared 28 May 2008 by the Constituent Assembly | agrees (not in NCERT, correct on record) |
| 2015 में नया संविधान | NCERT | agrees |
| भारत: नैतिक, राजनीतिक, कूटनीतिक समर्थन | board model answer | no conflict |
| रेल सेवा, नागरिक विमान सेवा, पॉलिटेक्निक कॉलेज, सीमा पर कन्वेंशन हॉल के समझौते | India–Nepal agreements of February 2010 (rail links, air services, a polytechnic, a convention centre in the border town) | agrees |
| प्रधानमंत्री प्रचंड (पुष्प कमल दहल) और राष्ट्रपति रामबरन यादव की भारत यात्राएँ | Prachanda, September 2008; President Yadav, February 2010 | agrees |

**No wrong fact found. Nothing goes back to the user as a correction.**

## 2. Things to report

1. **No Notes answer in the drop.** `inbox/POL-C3-LA-02/` holds the three clips, the
   three SRTs and the script. Rule "the video and the Notes page must agree" cannot
   be checked until the Notes page is supplied.
2. **The SRT is HeyGen's reading text, not the caption text.** It has "कक्षा barvi",
   "उन्नीस सौ नब्बे", "Part one / two / three". Captions take the SCRIPT's spelling:
   12वीं, 1990, Part 1 / 2 / 3 (rule 16, digits as digits).
3. **Part 2 has one collapsed token:** whisper gives 'अप्रैल' 13.18–16.74 s (3.56 s),
   a pause swallowed into a word. Repaired from measured silences at alignment
   (`tools/reel/align_words.mjs`), as on the last video.

## 3. What these things really look like

- **Period:** 1990 to 2015. Ordinary late-20th-century dress: shirts, jackets,
  sweaters, saris, kurta-suruwal; many men in the cloth cap (ढाका टोपी). Not
  ancient, not royal-court costume, not Tibetan robes, not Rajasthani turbans.
- **Place:** the Kathmandu valley and hill towns. Brick-and-carved-timber
  buildings, tiered temple roofs, narrow brick streets, green hills, snow peaks
  far behind. Not Mughal domes, not Chinese upturned eaves, not a desert.
- **The 2006 movement:** very large, mostly peaceful street crowds in daylight.
- **An assembly hall:** a plain chamber with rows of seats. No emblem, no flag.

## 4. Wrong pictures a generator is likely to draw (and what we do instead)

| Likely error | Why it matters | Our rule for this video |
|---|---|---|
| A rectangular or garbled flag | Nepal's flag is two stacked pennants, the only non-rectangular national flag | **No flag in any generated clip.** Not planned on screen at all. |
| Placards and banners with fake lettering | Text in a clip (rule 2) | Every crowd prompt: open raised hands, no signs, no banners |
| A recognisable king, prime minister or president | Real modern people (rule 6) | **Never generated.** ज्ञानेन्द्र, प्रचंड, रामबरन यादव appear as typeset name plates |
| A European crown and gothic throne, or a Mughal durbar | Wrong country | Throne room kept dim and generic; the crown on screen is our own flat symbol, not a depiction |
| Soldiers, rifles, clashes | Wrong uniforms; Flow refuses or stalls on danger words | Army and "सशस्त्र संघर्ष" are **drawn** as symbols, never generated, never named in a prompt |
| Modern phones, LED screens, drones in the crowd | 1990 and 2006 | Asked for "late twentieth century", checked on every clip |
| A map of Nepal and India with borders | Rule 5; the western border is also disputed | **Our map only**, from Natural Earth relief and rivers, with NO country lines; the two names are typeset on it |
| A real-looking "news photograph" of an event | A student could take generated footage for the real 2006 pictures | Every clip is printed in ONE ink on paper (see the storyboard), so it reads as an illustration, and none shows an identifiable face |
