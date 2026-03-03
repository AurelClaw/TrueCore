#!/bin/bash
# pattern_synthesizer.sh - Muster-Synthese Engine v1.0
# Autonom generiert durch aurel_self_learn Trigger
# Zeit: 2026-03-02 17:08 CST

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
SKILLS_DIR="$WORKSPACE/skills"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

echo "=== PATTERN SYNTHESIZER v1.0 ==="
echo "Zeit: $DATE $TIME"
echo ""

# Sammle alle Memory-Dateien der letzten 7 Tage
echo "[SCAN] Analysiere letzte 7 Tage..."
PATTERNS=$(find "$MEMORY_DIR" -name "2026-02-*.md" -o -name "2026-03-*.md" 2>/dev/null | sort -t'-' -k1,1 -k2,2 -k3,3 | tail -7)

if [ -z "$PATTERNS" ]; then
    echo "[INFO] Keine Memory-Dateien gefunden"
    exit 0
fi

echo "[ANALYSE] Gefundene Logs:"
echo "$PATTERNS" | while read f; do
    echo "  - $(basename $f)"
done
echo ""

# Extrahiere häufige Konzepte
echo "[SYNTHESIZER] Top-Konzepte (letzte 7 Tage):"
echo "$PATTERNS" | xargs cat 2>/dev/null | \
    grep -oE '\b[A-Za-z_]{4,}\b' | \
    tr '[:upper:]' '[:lower:]' | \
    grep -vE '^(echo|date|time|mkdir|then|else|elif|fi|for|while|do|done|the|and|with|from|this|that|will|have|been|were|they|their|there|when|where|what|which|who|how|why|not|but|can|may|might|must|shall|should|would|could|than|only|also|even|just|now|here|over|such|each|more|most|some|very|well|back|down|off|out|into|onto|upon|within|without|through|during|before|after|above|below|between|among|against|towards|across|around|behind|beyond|beside|under|upon|worth|next|last|first|second|third|many|much|few|little|own|same|other|another|several|certain|various|different|available|possible|likely|certain|sure|true|right|left|good|bad|new|old|young|long|short|high|low|big|small|great|little|early|late|fast|slow|hard|easy|clear|full|empty|open|close|free|busy|safe|ready|able|like|love|know|think|make|take|come|give|look|use|find|tell|ask|work|seem|feel|try|leave|call|keep|let|begin|seem|help|show|hear|play|run|move|live|believe|bring|happen|stand|lose|pay|meet|include|continue|set|learn|change|lead|understand|watch|follow|stop|create|speak|read|allow|add|spend|grow|open|walk|offer|remember|consider|appear|buy|wait|serve|die|send|expect|build|stay|fall|cut|reach|kill|remain|suggest|raise|pass|sell|require|report|decide|pull|return|explain|carry|develop|hope|drive|break|receive|agree|support|remove|return|describe|lie|discover|contain|establish|force|realize|occur|write|provide|lose|reduce|join|attend|treat|apply|avoid|prepare|compare|announce|finish|share|arrive|claim|prove|enjoy|examine|exist|happen|fill|identify|indicate|imagine|introduce|mention|notice|obtain|perform|protect|prove|publish|receive|recognize|record|reduce|refer|regard|relate|release|remain|remove|repeat|replace|reply|report|represent|require|research|resource|respect|respond|rest|result|return|reveal|rich|ride|ring|rise|risk|river|road|rock|role|roll|roof|room|root|rope|rough|round|route|routine|rule|run|safe|sail|sale|salt|same|sand|save|scale|scene|school|science|score|screen|sea|search|season|seat|second|secret|section|sector|secure|see|seek|seem|select|sell|send|sense|sentence|separate|sequence|series|serious|serve|service|session|set|settle|seven|several|severe|sex|shake|shall|shape|share|sharp|she|sheet|shelf|shell|shelter|shift|shine|ship|shirt|shock|shoe|shoot|shop|short|shot|should|shoulder|shout|show|shower|shut|sick|side|sight|sign|signal|significant|silent|silver|similar|simple|since|sing|single|sink|sir|sister|sit|site|situation|six|size|skill|skin|skirt|sky|sleep|slice|slide|slight|slip|slow|small|smart|smell|smile|smoke|smooth|snow|so|social|society|soft|soil|soldier|solid|solution|solve|some|somebody|somehow|someone|something|sometimes|somewhere|son|song|soon|sort|sound|source|south|space|speak|special|species|specific|speech|speed|spell|spend|spirit|spiritual|split|sport|spot|spread|spring|square|stage|stand|standard|star|start|state|statement|station|status|stay|steady|steal|steel|step|stick|still|stock|stomach|stone|stop|store|storm|story|straight|strange|stranger|stream|street|strength|stress|stretch|strike|string|strong|structure|student|studio|study|stuff|stupid|style|subject|submit|substance|succeed|success|successful|such|sudden|suffer|sugar|suggest|suit|summer|sun|super|supply|support|suppose|sure|surface|surprise|surround|survey|survive|suspect|sustain|swear|sweep|sweet|swim|swing|switch|symbol|symptom|system|table|tail|take|tale|talent|talk|tall|task|taste|tax|teach|teacher|team|tear|technical|technique|technology|telephone|television|tell|temperature|temporary|ten|tend|term|terrible|territory|test|text|than|thank|that|the|theater|their|them|theme|themselves|then|theory|therapy|there|therefore|these|they|thick|thin|thing|think|third|thirsty|thirty|this|those|though|thought|thousand|threat|three|throat|through|throughout|throw|thus|ticket|tie|tight|time|tiny|tip|tire|tired|title|to|tobacco|today|together|toilet|tolerance|tomorrow|tone|tongue|tonight|too|tool|tooth|top|topic|total|touch|tough|tour|toward|towards|town|toy|trace|track|trade|tradition|traditional|traffic|tragedy|trail|train|training|transfer|transform|transition|translate|transport|transportation|travel|treat|treatment|tree|trend|trial|trip|trouble|truck|true|truly|trust|truth|try|tube|turn|twelve|twenty|twice|twin|two|type|typical|ugly|ultimate|ultimately|unable|uncle|under|undergo|understand|understanding|unfortunately|uniform|union|unique|unit|united|universal|universe|university|unknown|unless|unlike|unlikely|until|unusual|up|upon|upper|urban|urge|use|used|useful|user|usual|usually|utility|vacation|vague|valley|valuable|value|variable|variation|variety|various|vary|vast|vegetable|vehicle|venture|version|very|vessel|veteran|victim|victory|video|view|viewer|village|violate|violation|violence|violent|virtual|virtue|virus|visible|vision|visit|visitor|visual|vital|voice|volume|volunteer|vote|vulnerable|wage|wait|wake|walk|wall|wander|want|war|warm|warn|warning|wash|waste|watch|water|wave|way|weak|wealth|wealthy|weapon|wear|weather|week|weekend|weekly|weigh|weight|welcome|welfare|well|west|western|wet|what|whatever|wheel|when|whenever|where|whereas|whether|which|while|white|who|whole|whom|whose|why|wide|widely|widespread|wife|wild|will|win|wind|window|wine|wing|winner|winter|wipe|wire|wisdom|wise|wish|with|withdraw|within|without|witness|woman|wonder|wonderful|wood|wooden|word|work|worker|working|works|workshop|world|worried|worry|worth|would|wound|wrap|write|writer|writing|wrong|yard|yeah|year|yell|yellow|yes|yesterday|yet|yield|you|young|your|yours|yourself|youth|zone)$' | \
    sort | uniq -c | sort -rn | head -10 | while read count word; do
    echo "  • '$word': $count"
done

echo ""
echo "[STATUS] Pattern Synthesizer abgeschlossen"
echo "Nächster Lauf: $(date -d '+2 hours' '+%H:%M' 2>/dev/null || echo 'in 2 Stunden')"
