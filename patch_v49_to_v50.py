#!/usr/bin/env python3
# Patch: V49 -> V50  "Audit-Befunde, Stufe 1"
#
#  K1   Tailwind vom CDN durch ein lokal gebautes Stylesheet ersetzt.
#       Braucht tailwind-built.css neben der Eingabedatei. Fehlt die, wird
#       K1 uebersprungen und alles andere trotzdem angewendet.
#  K1b  Schriften eingebettet statt @import auf Google Fonts. Braucht
#       fonts-embedded.css neben der Eingabedatei, sonst uebersprungen.
#  V1   <title>: Versionsnummer auf V50
#  V2   <h1>: Versionsnummer auf V50, dazu das fuehrende Emoji raus.
#       Grund: .stellaris-header setzt -webkit-background-clip:text mit
#       -webkit-text-fill-color:transparent. Das trifft auch die Emoji-Glyphe,
#       die dadurch als gefuellter Verlaufsblock erscheint statt als Symbol.
#  S1a  Merker, zu welchem System die aktuelle Canvas-Ansicht gehoert
#  S1b  renderSystemVisualization(): Zoom/Pan nur beim Systemwechsel zuruecksetzen
#  S6a  Systemliste: Bezeichner und NEIGHBOR-Badge werden von der festen
#       300px-Spalte abgeschnitten. flex-1 ohne min-width:0 kann nicht unter die
#       Inhaltsbreite schrumpfen und schiebt das Badge aus dem Bild.
#  K3a  CSS: bestehende .stellaris-btn:disabled-Regel um box-shadow ergaenzt
#  K3b  Toolbar: Undo/Redo-Knoepfe
#  K2a  Markup: Platzhalter fuer das Autosave-Banner
#  K2b  updateSystemList(): Autosave und Historie anstossen
#  K2c  loadSystemIntoEditor(): Autosave und Historie anstossen
#  K4a  Befundkasten im Editor-Panel
#  K4b  loadSystemIntoEditor(): Befunde nach dem Neuaufbau zeichnen
#  K2d  Block vor </script>: Autosave, Wiederherstellung, Undo/Redo,
#       laufende Validierung, Tastatur
#
# Sichtbare Texte englisch wie der Rest der Oberflaeche, Kommentare deutsch.
#
# Usage: python3 patch_v49_to_v50.py <input.html> <output.html>

import os
import sys

if len(sys.argv) not in (3, 4):
    sys.exit("usage: patch_v49_to_v50.py <input.html> <output.html> [tailwind-built.css]")

SRC, DST = sys.argv[1], sys.argv[2]

# K1 braucht ein lokal gebautes Tailwind-CSS. Fehlt es, laeuft alles andere
# trotzdem durch und der Patch sagt laut, dass der CDN-Aufruf stehen bleibt.
SRC_DIR = os.path.dirname(os.path.abspath(SRC))

if len(sys.argv) == 4:
    CSS_PATH = sys.argv[3]
else:
    CSS_PATH = os.path.join(SRC_DIR, "tailwind-built.css")

# K1b braucht die eingebetteten Schriften. Gleiche Regel: fehlt die Datei,
# bleibt der @import stehen und der Patch sagt es laut.
FONTS_PATH = os.path.join(SRC_DIR, "fonts-embedded.css")

with open(SRC, encoding="utf-8") as fh:
    data = fh.read()

# Leerzeilen im Original tragen Einrueckung mit. Explizit gebaut, damit
# kein Editor die Randleerzeichen wegputzt und der Match stillschweigend bricht.
B12 = " " * 12

# ---------------------------------------------------------------- V1
V1_OLD = "<title>Stellaris Solar System Editor V49 - Full Editor</title>"
V1_NEW = "<title>Stellaris Solar System Editor V50 - Full Editor</title>"

# ---------------------------------------------------------------- V2
V2_OLD = ('<h1 class="stellaris-header">\U0001F30C '
          'Stellaris Solar System Editor V49</h1>')
V2_NEW = ('<h1 class="stellaris-header">'
          'Stellaris Solar System Editor V50</h1>')

# ---------------------------------------------------------------- K3a
# Die Regel .stellaris-btn:disabled gibt es bereits (V49, Zeile 165). Nicht
# duplizieren, sondern um die eine fehlende Eigenschaft ergaenzen.
K3A_OLD = "\n".join([
    "        .stellaris-btn:disabled {",
    "            opacity: 0.5;",
    "            cursor: not-allowed;",
    "            transform: none;",
    "        }",
])

K3A_NEW = "\n".join([
    "        .stellaris-btn:disabled {",
    "            opacity: 0.5;",
    "            cursor: not-allowed;",
    "            transform: none;",
    "            /* V50 K3: ohne das behaelt ein deaktivierter Knopf sein",
    "               Leuchten und sieht weiter nach \"klick mich\" aus. */",
    "            box-shadow: none;",
    "        }",
])

# ---------------------------------------------------------------- K3b
K3B_OLD = ('                    <button id="systemCheckBtn" '
           'class="stellaris-btn stellaris-btn-secondary">\U0001F50D System Check</button>')

K3B_NEW = "\n".join([
    '                    <button id="undoBtn" class="stellaris-btn stellaris-btn-secondary" '
    'title="Undo the last change (Ctrl+Z)" disabled>Undo</button>',
    '                    <button id="redoBtn" class="stellaris-btn stellaris-btn-secondary" '
    'title="Redo the undone change (Ctrl+Y)" disabled>Redo</button>',
    '                    <button id="systemCheckBtn" '
    'class="stellaris-btn stellaris-btn-secondary">\U0001F50D System Check</button>',
])

# ---------------------------------------------------------------- S1a
S1A_OLD = "\n".join([
    "        let canvasScale = 1;",
    "        let canvasOffsetX = 0;",
    "        let canvasOffsetY = 0;",
    "        let isDragging = false;",
])

S1A_NEW = "\n".join([
    "        let canvasScale = 1;",
    "        let canvasOffsetX = 0;",
    "        let canvasOffsetY = 0;",
    "        // V50 S1: zu welchem System die aktuelle Ansicht gehoert.",
    "        // null = es gibt noch keine.",
    "        let canvasViewSystemIndex = null;",
    "        let isDragging = false;",
])

# ---------------------------------------------------------------- S1b
S1B_OLD = "\n".join([
    "            canvas.height = canvas.offsetHeight;",
    B12,
    "            // Reset view",
    "            canvasScale = 1;",
    "            canvasOffsetX = canvas.width / 2;",
    "            canvasOffsetY = canvas.height / 2;",
    B12,
])

S1B_NEW = "\n".join([
    "            canvas.height = canvas.offsetHeight;",
    B12,
    "            // V50 S1: Ansicht nur zuruecksetzen, wenn ein anderes System",
    "            // gezeigt wird. Bearbeitungen am laufenden System behalten Zoom",
    "            // und Pan, damit das Korrigieren einer orbit_distance die Ansicht",
    "            // nicht jedes Mal auf 1:1 zurueckwirft.",
    "            const viewBelongsToOtherSystem = canvasViewSystemIndex !== currentSystemIndex;",
    "            const viewIsUnusable = !Number.isFinite(canvasScale) || canvasScale <= 0;",
    "            if (viewBelongsToOtherSystem || viewIsUnusable) {",
    "                canvasScale = 1;",
    "                canvasOffsetX = canvas.width / 2;",
    "                canvasOffsetY = canvas.height / 2;",
    "                canvasViewSystemIndex = currentSystemIndex;",
    "            }",
    B12,
])

# ------------------------------------------------------------- S6a-1
# <div class="flex-1"> kommt 4x in der Datei vor, daher mit Kontext verankert.
S6A1_OLD = "\n".join([
    '                    <div class="flex justify-between items-start">',
    '                        <div class="flex-1">',
    '                            <div class="font-semibold text-blue-300">${system.displayName}</div>',
    '                            <div class="text-xs text-gray-400 mt-1">${system.name}</div>',
])

S6A1_NEW = "\n".join([
    '                    <div class="flex justify-between items-start gap-2">',
    '                        <div class="flex-1 min-w-0">',
    '                            <div class="font-semibold text-blue-300 break-words">${system.displayName}</div>',
    '                            <div class="text-xs text-gray-400 mt-1 break-all">${system.name}</div>',
])

# ------------------------------------------------------------- S6a-2
S6A2_OLD = '<span class="stellaris-badge badge-primary ml-2">Main</span>'
S6A2_NEW = '<span class="stellaris-badge badge-primary ml-2 shrink-0">Main</span>'

# ------------------------------------------------------------- S6a-3
S6A3_OLD = '<span class="stellaris-badge badge-secondary ml-2">Neighbor</span>'
S6A3_NEW = '<span class="stellaris-badge badge-secondary ml-2 shrink-0">Neighbor</span>'

# -------------------------------------------------------------- K2a
K2A_OLD = "\n".join([
    '            <div id="importInfo" class="mt-4 p-3 bg-blue-900/30 rounded-lg border border-blue-500/30 hidden">',
    '                <p class="text-blue-300 font-semibold">✅ Imported: <span id="systemCount">0</span> System(s)</p>',
    '            </div>',
])

K2A_NEW = "\n".join([
    '            <div id="importInfo" class="mt-4 p-3 bg-blue-900/30 rounded-lg border border-blue-500/30 hidden">',
    '                <p class="text-blue-300 font-semibold">✅ Imported: <span id="systemCount">0</span> System(s)</p>',
    '            </div>',
    '',
    '            <!-- V50 K2: Autosave-Status, Wiederherstellungs-Angebot, Warnung. -->',
    '            <div id="autosaveBanner" class="mt-4 p-3 rounded-lg border hidden"></div>',
    '',
    '            <!-- V50 K4: dauerhafte Live-Region fuer den Pruefstand. Der',
    '                 sichtbare Befundkasten im Editor wird bei jeder Aenderung',
    '                 neu aufgebaut und taugt deshalb nicht als Live-Region:',
    '                 Screenreader melden nur Aenderungen an Elementen, die',
    '                 vorher schon im DOM standen. -->',
    '            <p id="validationStatus" role="status" aria-atomic="true" class="sr-only"></p>',
])

# -------------------------------------------------------------- K4a
K4A_OLD = "\n".join([
    '                    <!-- System Properties -->',
    '                    <div class="bg-gray-800/50 p-4 rounded-lg mb-6">',
])

K4A_NEW = "\n".join([
    '                    <!-- V50 K4: Befunde der laufenden Validierung. -->',
    '                    <div id="systemIssues" class="mb-6"></div>',
    '',
    '                    <!-- System Properties -->',
    '                    <div class="bg-gray-800/50 p-4 rounded-lg mb-6">',
])

# -------------------------------------------------------------- K4b
K4B_OLD = "            setTimeout(() => renderSystemVisualization(), 50);"

K4B_NEW = "\n".join([
    "            setTimeout(() => renderSystemVisualization(), 50);",
    "            renderSystemIssues();   // V50 K4",
])

# -------------------------------------------------------------- K2b
K2B_OLD = "\n".join([
    "        function updateSystemList() {",
    "            const listContainer = document.getElementById('systemList');",
])

K2B_NEW = "\n".join([
    "        function updateSystemList() {",
    "            recordChange();   // V50 K2/K3",
    "            const listContainer = document.getElementById('systemList');",
])

# -------------------------------------------------------------- K2c
K2C_OLD = "\n".join([
    "        function loadSystemIntoEditor(system) {",
    "            const editorContainer = document.getElementById('systemEditorContent');",
])

K2C_NEW = "\n".join([
    "        function loadSystemIntoEditor(system) {",
    "            recordChange();   // V50 K2/K3",
    "            const editorContainer = document.getElementById('systemEditorContent');",
])

# -------------------------------------------------------------- K2d
K2D_OLD = "\n    </script>\n</body>"

K2D_BLOCK = '''
        // ===== V50 K2/K3: AUTOSAVE, WIEDERHERSTELLUNG, UNDO/REDO =====
        //
        // Der Editor hielt seinen Zustand bisher ausschliesslich in allSystems.
        // Ein geschlossener Tab, ein Reload oder ein Absturz warf alles weg,
        // und rueckgaengig machen ging gar nicht.
        //
        // Beides haengt an derselben Frage: wie sieht der Zustand gerade aus?
        // Deshalb ein gemeinsamer Einstieg, recordChange(), aufgerufen aus
        // updateSystemList() und loadSystemIntoEditor(). Diese beiden laufen
        // nach jeder Mutation, egal welche. Dadurch braucht es keine Haken in
        // 16 einzelnen Speicher- und Loeschfunktionen.
        //
        // localStorage ist unter file:// nicht in jedem Browser erlaubt. Statt
        // das anzunehmen, wird es beim Start geprueft. Fehlt es, sagt der
        // Editor das offen, statt Sicherheit vorzutaeuschen.

        const AUTOSAVE_KEY = 'stellaris_system_editor_autosave_v1';
        const AUTOSAVE_DELAY_MS = 800;
        const HISTORY_MAX_ENTRIES = 40;
        const HISTORY_MAX_BYTES = 24 * 1024 * 1024;

        let autosaveAvailable = false;
        let autosaveTimer = null;
        let autosaveFailureReported = false;

        let historyStates = [];
        let historyPointer = -1;
        let historySuspended = false;

        // ---------------------------------------------------------- Zustand

        function serializeState() {
            // Ohne Zeitstempel: die Historie vergleicht Zeichenketten, ein
            // wandernder Zeitwert wuerde jeden Stand als "geaendert" zaehlen.
            return JSON.stringify({
                format: 1,
                nextPlanetId: nextPlanetId,
                systems: allSystems
            });
        }

        function recordChange() {
            captureHistory();
            scheduleAutosave();
        }

        // ---------------------------------------------------------- Historie

        function captureHistory() {
            if (historySuspended) return;
            let json;
            try {
                json = serializeState();
            } catch (err) {
                return;   // nicht serialisierbar: lieber keine Historie als eine falsche
            }
            // loadSystemIntoEditor() laeuft auch beim blossen Umschalten
            // zwischen Systemen. Gleicher Inhalt heisst: keine Aenderung.
            if (historyPointer >= 0 && historyStates[historyPointer] === json) return;

            // Alles hinter dem Zeiger faellt weg, hier beginnt ein neuer Ast.
            historyStates.length = historyPointer + 1;
            historyStates.push(json);
            historyPointer = historyStates.length - 1;
            trimHistory();
            updateHistoryButtons();
        }

        function trimHistory() {
            let bytes = 0;
            for (let i = 0; i < historyStates.length; i++) bytes += historyStates[i].length;
            while (historyStates.length > 2 &&
                   (historyStates.length > HISTORY_MAX_ENTRIES || bytes > HISTORY_MAX_BYTES)) {
                bytes -= historyStates[0].length;
                historyStates.shift();
                historyPointer--;
            }
            if (historyPointer < 0) historyPointer = 0;
        }

        function applyHistoryState(json) {
            let parsed;
            try {
                parsed = JSON.parse(json);
            } catch (err) {
                showNotification('History entry is unreadable.');
                return;
            }
            allSystems = parsed.systems || [];
            if (Number.isFinite(parsed.nextPlanetId) && parsed.nextPlanetId > 0) {
                nextPlanetId = parsed.nextPlanetId;
            }
            // Der Index kann ins Leere zeigen, wenn der Schritt ein System
            // angelegt oder geloescht hat.
            if (!Number.isInteger(currentSystemIndex) ||
                currentSystemIndex < 0 ||
                currentSystemIndex >= allSystems.length) {
                currentSystemIndex = null;
            }
            canvasViewSystemIndex = null;

            // Das Neuzeichnen ruft recordChange() auf. Ohne Sperre wuerde der
            // wiederhergestellte Stand als neue Aenderung in die Historie
            // wandern und Redo zerstoeren.
            historySuspended = true;
            try {
                updateSystemList();
                if (currentSystemIndex === null) {
                    clearEditor();
                } else {
                    loadSystemIntoEditor(allSystems[currentSystemIndex]);
                }
            } finally {
                historySuspended = false;
            }

            scheduleAutosave();
            updateHistoryButtons();
        }

        function undoChange() {
            if (historyPointer <= 0) {
                showNotification('Nothing to undo.');
                return;
            }
            historyPointer--;
            applyHistoryState(historyStates[historyPointer]);
            showNotification('Undone. ' + historyPointer + ' more step(s) available.');
        }

        function redoChange() {
            if (historyPointer >= historyStates.length - 1) {
                showNotification('Nothing to redo.');
                return;
            }
            historyPointer++;
            applyHistoryState(historyStates[historyPointer]);
            showNotification('Redone.');
        }

        function updateHistoryButtons() {
            const undoBtn = document.getElementById('undoBtn');
            const redoBtn = document.getElementById('redoBtn');
            if (undoBtn) undoBtn.disabled = historyPointer <= 0;
            if (redoBtn) redoBtn.disabled = historyPointer >= historyStates.length - 1;
        }

        // ---------------------------------------------------------- Autosave

        function autosaveProbe() {
            try {
                const probeKey = '__stellaris_autosave_probe__';
                window.localStorage.setItem(probeKey, '1');
                window.localStorage.removeItem(probeKey);
                return true;
            } catch (err) {
                return false;
            }
        }

        function escapeForBanner(text) {
            const holder = document.createElement('div');
            holder.textContent = String(text);
            return holder.innerHTML;
        }

        function showAutosaveBanner(html, tone) {
            const el = document.getElementById('autosaveBanner');
            if (!el) return;
            const tones = {
                info: 'bg-blue-900/30 border-blue-500/30 text-blue-200',
                warn: 'bg-yellow-900/30 border-yellow-500/40 text-yellow-200',
                error: 'bg-red-900/30 border-red-500/40 text-red-200'
            };
            el.className = 'mt-4 p-3 rounded-lg border ' + (tones[tone] || tones.info);
            el.innerHTML = html;
        }

        function hideAutosaveBanner() {
            const el = document.getElementById('autosaveBanner');
            if (!el) return;
            el.className = 'mt-4 p-3 rounded-lg border hidden';
            el.innerHTML = '';
        }

        function scheduleAutosave() {
            if (!autosaveAvailable) return;
            window.clearTimeout(autosaveTimer);
            autosaveTimer = window.setTimeout(writeAutosave, AUTOSAVE_DELAY_MS);
        }

        function writeAutosave() {
            if (!autosaveAvailable) return;
            try {
                if (!Array.isArray(allSystems) || allSystems.length === 0) {
                    window.localStorage.removeItem(AUTOSAVE_KEY);
                    return;
                }
                window.localStorage.setItem(AUTOSAVE_KEY, JSON.stringify({
                    format: 1,
                    savedAt: new Date().toISOString(),
                    nextPlanetId: nextPlanetId,
                    systems: allSystems
                }));
                autosaveFailureReported = false;
            } catch (err) {
                // Speicherkontingent voll oder Zugriff nachtraeglich entzogen.
                // Einmal melden, nicht bei jeder weiteren Eingabe erneut.
                if (!autosaveFailureReported) {
                    autosaveFailureReported = true;
                    showAutosaveBanner(
                        '<span class="font-semibold">Autosave failed.</span> ' +
                        escapeForBanner(err.name + ': ' + err.message) +
                        ' Export your work before closing this tab.',
                        'error');
                }
            }
        }

        function readAutosave() {
            try {
                const raw = window.localStorage.getItem(AUTOSAVE_KEY);
                if (!raw) return null;
                const parsed = JSON.parse(raw);
                if (!parsed || !Array.isArray(parsed.systems) || parsed.systems.length === 0) {
                    return null;
                }
                return parsed;
            } catch (err) {
                return null;
            }
        }

        function restoreAutosave() {
            const parsed = readAutosave();
            if (!parsed) {
                hideAutosaveBanner();
                showNotification('No recoverable state found.');
                return;
            }
            allSystems = parsed.systems;
            if (Number.isFinite(parsed.nextPlanetId) && parsed.nextPlanetId > 0) {
                nextPlanetId = parsed.nextPlanetId;
            }
            // Kein System vorauswaehlen: der Nutzer entscheidet, wo er
            // weitermacht, und die Canvas-Ansicht startet sauber.
            currentSystemIndex = null;
            canvasViewSystemIndex = null;
            updateSystemList();
            const info = document.getElementById('importInfo');
            const count = document.getElementById('systemCount');
            if (info) info.classList.remove('hidden');
            if (count) count.textContent = allSystems.length;
            hideAutosaveBanner();
            showNotification('Restored ' + allSystems.length + ' system(s).');
        }

        function discardAutosave() {
            try {
                window.localStorage.removeItem(AUTOSAVE_KEY);
            } catch (err) {
                // Wegwerfen darf nie den Editor anhalten.
            }
            hideAutosaveBanner();
        }

        // -------------------------------------------------------- Validierung
        //
        // validateSystem() gab es laengst und sie ist gruendlich. Sie lief nur
        // an einer einzigen Stelle: hinter dem System-Check-Knopf. Wer nicht
        // klickte, erfuhr von einem Orbit-Konflikt erst beim Export. Geaendert
        // wird deshalb nur der Zeitpunkt, nicht die Pruefung selbst.

        let lastValidationAnnouncement = '';

        function announceValidation(text) {
            const el = document.getElementById('validationStatus');
            if (!el) return;
            // Nur bei echter Aenderung sprechen. Sonst liest ein Screenreader
            // nach jedem Tastendruck dieselbe Liste erneut vor.
            if (text === lastValidationAnnouncement) return;
            lastValidationAnnouncement = text;
            el.textContent = text;
        }

        function renderSystemIssues() {
            const host = document.getElementById('systemIssues');
            if (!host) return;

            const system = (currentSystemIndex !== null && allSystems[currentSystemIndex])
                ? allSystems[currentSystemIndex]
                : null;

            if (!system) {
                host.className = 'mb-6 hidden';
                host.innerHTML = '';
                announceValidation('');
                return;
            }

            const label = String(system.displayName || system.name || 'system');

            let issues;
            try {
                issues = validateSystem(system) || [];
            } catch (err) {
                // Eine kaputte Pruefung darf den Editor nicht mitreissen, aber
                // sie darf auch nicht so aussehen, als waere alles in Ordnung.
                host.className = 'mb-6 p-3 rounded-lg border bg-red-900/30 border-red-500/40 text-red-200';
                host.innerHTML = '<span class="font-semibold">System check failed to run.</span> ' +
                    escapeForBanner(err.name + ': ' + err.message);
                announceValidation('System check failed to run for ' + label + '.');
                return;
            }

            if (issues.length === 0) {
                host.className = 'mb-6 p-2 rounded-lg border bg-green-900/20 border-green-500/30 text-green-300 text-sm';
                host.innerHTML = 'System check: no issues in "' + escapeForBanner(label) + '".';
                announceValidation('System check: no issues in ' + label + '.');
                return;
            }

            const items = issues
                .map((text) => '<li>' + escapeForBanner(text) + '</li>')
                .join('');

            host.className = 'mb-6 p-3 rounded-lg border bg-yellow-900/20 border-yellow-500/40 text-yellow-200';
            host.innerHTML =
                '<p class="font-semibold mb-2">System check: ' + issues.length +
                ' issue(s) in "' + escapeForBanner(label) + '"</p>' +
                '<ul class="list-disc list-inside space-y-1 text-sm">' + items + '</ul>';

            announceValidation('System check: ' + issues.length + ' issue(s) in ' + label + '.');
        }

        // ------------------------------------------------ Bestaetigungsdialog
        //
        // Ersatz fuer die blockierende Systemabfrage. Liefert ein Promise, das
        // mit true oder false aufgeloest wird.
        //
        // Der Abbrechen-Knopf bekommt den Fokus, nicht der Bestaetigen-Knopf,
        // und es gibt bewusst kein Enter-Kuerzel zum Bestaetigen. Bei Dialogen,
        // hinter denen ein Loeschvorgang haengt, ist die zusaetzliche Reibung
        // der Sinn der Sache.

        let confirmResolver = null;

        function settleConfirm(answer) {
            const modal = document.getElementById('confirmModal');
            if (modal) modal.classList.remove('active');
            const resolve = confirmResolver;
            confirmResolver = null;
            if (resolve) resolve(answer);
        }

        function confirmAction(message, confirmLabel) {
            // Ein zweiter Dialog waehrend eines offenen: den ersten abbrechen,
            // statt seinen Aufrufer fuer immer warten zu lassen.
            if (confirmResolver) settleConfirm(false);

            const modal = document.getElementById('confirmModal');
            const messageEl = document.getElementById('confirmModalMessage');
            const okBtn = document.getElementById('confirmModalOk');
            const cancelBtn = document.getElementById('confirmModalCancel');

            if (!modal || !messageEl || !okBtn || !cancelBtn) {
                // Ohne Dialog lieber nichts tun als blind loeschen.
                showNotification('Confirmation dialog missing - action cancelled.', 'error');
                return Promise.resolve(false);
            }

            messageEl.textContent = String(message);
            okBtn.textContent = confirmLabel || 'Confirm';
            modal.classList.add('active');
            cancelBtn.focus();

            return new Promise((resolve) => { confirmResolver = resolve; });
        }

        document.getElementById('confirmModalOk')?.addEventListener('click', () => settleConfirm(true));
        document.getElementById('confirmModalCancel')?.addEventListener('click', () => settleConfirm(false));
        document.getElementById('confirmModal')?.addEventListener('click', (e) => {
            // Klick auf die Abdunklung neben dem Dialogfenster bricht ab.
            if (e.target && e.target.id === 'confirmModal') settleConfirm(false);
        });

        document.addEventListener('keydown', (e) => {
            if (confirmResolver === null) return;
            if (e.key === 'Escape') {
                e.preventDefault();
                settleConfirm(false);
            }
        });

        // ---------------------------------------------------------- Tastatur

        document.addEventListener('keydown', (e) => {
            if (!(e.ctrlKey || e.metaKey)) return;
            // In Eingabefeldern gehoert Strg+Z dem Browser. Wer eine Zahl
            // vertippt hat, will den Text zurueck, nicht den letzten Planeten.
            const target = e.target;
            const tag = target && target.tagName;
            if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' ||
                (target && target.isContentEditable)) {
                return;
            }
            const key = (e.key || '').toLowerCase();
            if (key === 'z' && !e.shiftKey) {
                e.preventDefault();
                undoChange();
            } else if (key === 'y' || (key === 'z' && e.shiftKey)) {
                e.preventDefault();
                redoChange();
            }
        });

        window.addEventListener('beforeunload', (e) => {
            // Nur warnen, wenn der Zustand wirklich verloren geht. Solange das
            // Autosave laeuft, ist er nach dem Neuladen wieder da, und eine
            // Nachfrage bei jedem Schliessen waere reine Gewoehnungsbremse.
            if (autosaveAvailable) return;
            if (!Array.isArray(allSystems) || allSystems.length === 0) return;
            e.preventDefault();
            e.returnValue = '';
        });

        // ---------------------------------------------------------- Start

        function initAutosave() {
            autosaveAvailable = autosaveProbe();

            // Ausgangsstand als erster Historien-Eintrag, damit sich auch der
            // allererste Import rueckgaengig machen laesst.
            captureHistory();
            updateHistoryButtons();

            if (!autosaveAvailable) {
                showAutosaveBanner(
                    '<span class="font-semibold">Autosave unavailable.</span> ' +
                    'This browser gives the page no local storage. Loaded systems ' +
                    'are lost when the tab closes, so export in time.',
                    'warn');
                return;
            }

            const parsed = readAutosave();
            if (!parsed || (Array.isArray(allSystems) && allSystems.length > 0)) return;

            let savedAtText = String(parsed.savedAt || 'unknown');
            try {
                savedAtText = new Date(parsed.savedAt).toLocaleString();
            } catch (err) {
                // Zeitstempel unlesbar: Rohwert anzeigen statt nichts.
            }

            showAutosaveBanner(
                '<div class="flex flex-wrap items-center justify-between gap-3">' +
                    '<span><span class="font-semibold">Recoverable state found.</span> ' +
                    parsed.systems.length + ' system(s), last saved ' +
                    escapeForBanner(savedAtText) + '.</span>' +
                    '<span class="flex gap-2 shrink-0">' +
                        '<button id="autosaveRestoreBtn" class="stellaris-btn text-sm py-1 px-3">Restore</button>' +
                        '<button id="autosaveDiscardBtn" class="stellaris-btn stellaris-btn-secondary text-sm py-1 px-3">Discard</button>' +
                    '</span>' +
                '</div>',
                'info');

            document.getElementById('autosaveRestoreBtn')?.addEventListener('click', restoreAutosave);
            document.getElementById('autosaveDiscardBtn')?.addEventListener('click', discardAutosave);
        }

        document.getElementById('undoBtn')?.addEventListener('click', undoChange);
        document.getElementById('redoBtn')?.addEventListener('click', redoChange);

        initAutosave();
'''

K2D_NEW = K2D_BLOCK.rstrip("\n") + "\n    </script>\n</body>"

# ---------------------------------------------------------------- K1
# Der CDN-Aufruf wird durch das lokal gebaute Stylesheet ersetzt. Das ist die
# einzige Ersetzung, die von einer zweiten Datei abhaengt, deshalb wird sie
# erst angehaengt, wenn diese Datei wirklich da ist.
K1_OLD = '    <script src="https://cdn.tailwindcss.com"></script>'


def build_k1_replacement(css_text):
    return "\n".join([
        '    <!-- V50 K1: Tailwind lokal eingebacken. Hier stand vorher ein',
        '         Script-Tag auf das Tailwind-CDN. Die URL steht hier absichtlich',
        '         nicht mehr im Klartext, sonst meldet jede Suche nach einer',
        '         CDN-Abhaengigkeit einen Treffer, den es nicht mehr gibt.',
        '         Ohne Netz fielen damit saemtliche Utility-Klassen aus, also',
        '         praktisch das ganze Layout. Erzeugt mit tailwindcss@3 gegen diese Datei,',
        '         gegengeprueft mit verify_tailwind_css.py. Neu gebaut werden muss',
        '         es, sobald eine Utility-Klasse dazukommt, die vorher nirgends',
        '         im Dokument stand. -->',
        '    <style>',
        css_text.strip(),
        '    </style>',
    ])


# --------------------------------------------------------------- K1b
K1B_OLD = ("        @import url('https://fonts.googleapis.com/css2?"
           "family=Orbitron:wght@400;500;600;700;800;900&"
           "family=Exo+2:wght@300;400;500;600&display=swap');")


def build_k1b_replacement(fonts_css):
    return fonts_css.strip()


# -------------------------------------------------------------- S3a
# 18 alert() waren ausnahmslos reine Hinweise. Sie blockieren den Browser,
# ignorieren jede Gestaltung und stehen neben sieben eigenen Modals. Der
# Ersatz existiert seit jeher: showNotification().
#
# Dabei faellt ein Kontrastfehler auf, den es schon vorher gab: die Meldung
# traegt weisse Schrift auf var(--stellaris-blue). Das sind 1,77:1, also weit
# unter den geforderten 4,5:1, und betrifft alle Meldungen des Editors.
# Gemessen ergibt dunkle Schrift auf demselben Verlauf 11,30:1 am hellen und
# 5,43:1 am violetten Ende. Die Markenfarben bleiben damit unangetastet.
S3A1_OLD = "\n".join([
    "        .notification {",
    "            position: fixed;",
    "            top: 20px;",
    "            right: 20px;",
    "            background: linear-gradient(135deg, var(--stellaris-blue), var(--stellaris-purple));",
    "            color: white;",
    "            padding: 1rem 1.5rem;",
    "            border-radius: 8px;",
    "            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);",
    "            z-index: 1000;",
    "            animation: slideIn 0.3s ease;",
    "        }",
])

S3A1_NEW = "\n".join([
    "        /* V50 S3a: Meldungen stapeln, statt sich zu ueberlagern. Vorher lag",
    "           jede einzelne auf top:20px/right:20px, zwei kurz hintereinander",
    "           standen also uebereinander. */",
    "        .notification-stack {",
    "            position: fixed;",
    "            top: 20px;",
    "            right: 20px;",
    "            z-index: 1000;",
    "            display: flex;",
    "            flex-direction: column;",
    "            align-items: flex-end;",
    "            gap: 0.5rem;",
    "            max-width: min(28rem, calc(100vw - 40px));",
    "            pointer-events: none;",
    "        }",
    "",
    "        .notification {",
    "            background: linear-gradient(135deg, var(--stellaris-blue), var(--stellaris-purple));",
    "            /* V50 S3a: war weiss und damit 1,77:1 gegen das helle Ende des",
    "               Verlaufs. Dunkel ergibt 11,30:1 bzw. 5,43:1, bei gleichen",
    "               Markenfarben. */",
    "            color: var(--stellaris-darker);",
    "            padding: 1rem 1.5rem;",
    "            border-radius: 8px;",
    "            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);",
    "            animation: slideIn 0.3s ease;",
    "            /* Die aus den frueheren Systemdialogen uebernommenen Texte",
    "               tragen Zeilenumbrueche. Ohne pre-line liefe das alles in",
    "               eine Zeile zusammen. */",
    "            white-space: pre-line;",
    "            cursor: pointer;",
    "            pointer-events: auto;",
    "        }",
    "",
    "        /* Dunkle Flaechen, hier ist weiss richtig: 5,02:1, 6,47:1, 5,02:1. */",
    "        .notification-warn {",
    "            background: linear-gradient(135deg, #b45309, #92400e);",
    "            color: #ffffff;",
    "        }",
    "",
    "        .notification-error {",
    "            background: linear-gradient(135deg, #b91c1c, #7f1d1d);",
    "            color: #ffffff;",
    "        }",
    "",
    "        .notification-success {",
    "            background: linear-gradient(135deg, #15803d, #14532d);",
    "            color: #ffffff;",
    "        }",
])

# ------------------------------------------------------------- S3a-2
S3A2_OLD = "\n".join([
    "    </div>",
    "",
    "    <script>",
])

S3A2_NEW = "\n".join([
    "    </div>",
    "",
    "    <!-- V50 S3a: Container fuer gestapelte Meldungen. -->",
    '    <div id="notificationStack" class="notification-stack"></div>',
    "",
    "    <!-- V50 S3a: Meldungen sind fuer Screenreader sonst stumm, und ueber",
    "         showNotification laufen alle Rueckmeldungen des Editors. -->",
    '    <p id="notificationStatus" role="status" aria-atomic="true" class="sr-only"></p>',
    "",
    "    <!-- V50 S3b: eigener Bestaetigungsdialog. Ersetzt die Systemabfrage,",
    "         die den Browser blockiert und sich nicht gestalten laesst.",
    "         z-index 5000, damit er ueber dem Stern-Assistenten (4000) und den",
    "         uebrigen Modals (3000) liegt. -->",
    '    <div id="confirmModal" class="modal" style="z-index: 5000;">',
    '        <div class="modal-content" style="max-width: 32rem;">',
    '            <h2 id="confirmModalTitle" class="text-xl font-bold mb-4 text-yellow-300">Please confirm</h2>',
    '            <p id="confirmModalMessage" class="mb-6" style="white-space: pre-line;"></p>',
    '            <div class="flex gap-2 justify-end">',
    '                <button id="confirmModalCancel" class="stellaris-btn stellaris-btn-secondary">Cancel</button>',
    '                <button id="confirmModalOk" class="stellaris-btn stellaris-btn-danger">Confirm</button>',
    "            </div>",
    "        </div>",
    "    </div>",
    "",
    "    <script>",
])

# -------------------------------------------------------------- S3b
# Die sieben Systemabfragen tragen den Kontrollfluss: if (confirm(...)) { ... }.
# Ein eigener Dialog ist asynchron, also wird aus jeder betroffenen Funktion
# eine async-Funktion und aus der Abfrage ein await. Geprueft: alle sechs
# betroffenen Funktionen werden ausschliesslich aus onclick-Attributen
# aufgerufen, kein Aufrufer haengt an ihrem Rueckgabewert.

S3B_SITES = [
    ("S3b Alle Systeme loeschen", "\n".join([
        "        document.getElementById('clearAllBtn').addEventListener('click', () => {",
        "            if (confirm('Do you really want to delete all systems?')) {",
    ]), "\n".join([
        "        document.getElementById('clearAllBtn').addEventListener('click', async () => {",
        "            if (await confirmAction('Do you really want to delete all systems?', 'Delete all')) {",
    ])),

    ("S3b Planet loeschen", "\n".join([
        "        function deletePlanet(index) {",
        "            if (confirm('Really delete planet?')) {",
    ]), "\n".join([
        "        async function deletePlanet(index) {",
        "            if (await confirmAction('Really delete planet?', 'Delete')) {",
    ])),

    ("S3b Mond loeschen", "\n".join([
        "        function deleteMoon(parentPath, moonIndex) {",
        "            if (confirm('Really delete this body (and its sub-moons)?')) {",
    ]), "\n".join([
        "        async function deleteMoon(parentPath, moonIndex) {",
        "            if (await confirmAction('Really delete this body (and its sub-moons)?', 'Delete')) {",
    ])),

    ("S3b Nachbarsystem entfernen", "\n".join([
        "        function deleteNeighborSystem(index) {",
        "            if (confirm('Really remove neighbor system?')) {",
    ]), "\n".join([
        "        async function deleteNeighborSystem(index) {",
        "            if (await confirmAction('Really remove neighbor system?', 'Remove')) {",
    ])),

    ("S3b Asteroidenguertel loeschen", "\n".join([
        "        function deleteAsteroidBelt(index) {",
        "            if (confirm('Really delete asteroid belt?')) {",
    ]), "\n".join([
        "        async function deleteAsteroidBelt(index) {",
        "            if (await confirmAction('Really delete asteroid belt?', 'Delete')) {",
    ])),

    ("S3b System loeschen", "\n".join([
        "        function deleteCurrentSystem() {",
        "            if (currentSystemIndex === null) return;",
        B12,
        "            if (confirm(`Really delete system \"${allSystems[currentSystemIndex].displayName}\"?`)) {",
    ]), "\n".join([
        "        async function deleteCurrentSystem() {",
        "            if (currentSystemIndex === null) return;",
        B12,
        "            if (await confirmAction(`Really delete system \"${allSystems[currentSystemIndex].displayName}\"?`, 'Delete')) {",
    ])),

    ("S3b Planet ohne Stern", "        function openAddPlanetModal() {",
     "        async function openAddPlanetModal() {"),

    ("S3b Warnung ohne Stern",
     "                if (!confirm('⚠️ WARNING: No stars in system!"
     "\\n\\nStars must be added before planets. Stars are the first objects in Stellaris systems."
     "\\n\\nDo you want to add a planet anyway?"
     "\\n\\n(Recommended: Cancel and add a star first)')) {",
     "                if (!await confirmAction('⚠️ WARNING: No stars in system!"
     "\\n\\nStars must be added before planets. Stars are the first objects in Stellaris systems."
     "\\n\\nDo you want to add a planet anyway?"
     "\\n\\n(Recommended: Cancel and add a star first)', 'Add anyway')) {"),
]

# ------------------------------------------------------------- S3a-3
S3A3_OLD = "\n".join([
    "        function showNotification(message) {",
    "            const notification = document.createElement('div');",
    "            notification.className = 'notification';",
    "            notification.textContent = message;",
    "            document.body.appendChild(notification);",
    B12,
    "            setTimeout(() => {",
    "                notification.remove();",
    "            }, 3000);",
    "        }",
])

S3A3_NEW = "\n".join([
    "        function showNotification(message, tone) {",
    "            const text = String(message);",
    "            const notification = document.createElement('div');",
    "            // tone ist optional. Eine Aufrufstelle uebergab schon vorher",
    "            // den Wert 'success', der bisher wirkungslos verpuffte.",
    "            notification.className = 'notification' + (tone ? ' notification-' + tone : '');",
    "            notification.textContent = text;",
    "            // Anklicken schliesst sofort. Eine lange Warnung muss man sonst",
    "            // aussitzen, eine kurze Bestaetigung steht im Weg.",
    "            notification.addEventListener('click', () => notification.remove());",
    "",
    "            const stack = document.getElementById('notificationStack');",
    "            (stack || document.body).appendChild(notification);",
    "",
    "            const status = document.getElementById('notificationStatus');",
    "            if (status) status.textContent = text;",
    "",
    "            // Die aus den frueheren Systemdialogen uebernommenen Texte sind",
    "            // mehrzeilig, drei Sekunden reichen dafuer nicht. Mit der Laenge",
    "            // skalieren, bei neun Sekunden deckeln.",
    "            const holdMs = Math.min(9000, 3000 + text.length * 40);",
    "            setTimeout(() => notification.remove(), holdMs);",
    "        }",
])

# ------------------------------------------------------------- S3a-4
S3A4_OLD = "alert("
S3A4_NEW = "showNotification("

PATCHES = [
    ("V1  Titel auf V50",                   V1_OLD,   V1_NEW,   1),
    ("V2  Ueberschrift auf V50, Emoji raus", V2_OLD,  V2_NEW,   1),
    ("K3a Disabled-Regel ergaenzt",         K3A_OLD,  K3A_NEW,  1),
    ("K3b Undo/Redo-Knoepfe",               K3B_OLD,  K3B_NEW,  1),
    ("S1a Ansichts-Merker",                 S1A_OLD,  S1A_NEW,  1),
    ("S1b Reset nur bei Systemwechsel",     S1B_OLD,  S1B_NEW,  1),
    ("S6a Systemliste schrumpffaehig",      S6A1_OLD, S6A1_NEW, 1),
    ("S6a Badge Main nicht schrumpfen",     S6A2_OLD, S6A2_NEW, 1),
    ("S6a Badge Neighbor nicht schrumpfen", S6A3_OLD, S6A3_NEW, 1),
    ("K2a Banner und Live-Region",          K2A_OLD,  K2A_NEW,  1),
    ("K4a Befundkasten im Editor",          K4A_OLD,  K4A_NEW,  1),
    ("K4b Hook am Ende des Neuaufbaus",     K4B_OLD,  K4B_NEW,  1),
    ("K2b Hook updateSystemList",           K2B_OLD,  K2B_NEW,  1),
    ("K2c Hook loadSystemIntoEditor",       K2C_OLD,  K2C_NEW,  1),
    ("K2d Autosave- und Historien-Block",   K2D_OLD,  K2D_NEW,  1),
    # Massenersetzung, siehe Kommentar an der Schleife.
    ("S3a Systemdialoge zu Meldungen",      S3A4_OLD, S3A4_NEW, 18, True),
    ("S3a Meldungen stapeln und Kontrast",  S3A1_OLD, S3A1_NEW, 1),
    ("S3a Container und Live-Region",       S3A2_OLD, S3A2_NEW, 1),
    ("S3a showNotification erweitert",      S3A3_OLD, S3A3_NEW, 1),
]

for site_name, site_old, site_new in S3B_SITES:
    PATCHES.append((site_name, site_old, site_new, 1))

if os.path.isfile(CSS_PATH):
    with open(CSS_PATH, encoding="utf-8") as fh:
        css_text = fh.read()
    if not css_text.strip():
        sys.exit("K1: " + CSS_PATH + " ist leer. Build wiederholen.")
    if "</style>" in css_text:
        sys.exit("K1: das CSS enthaelt </style> und wuerde den Block sprengen.")
    PATCHES.insert(0, ("K1  Tailwind lokal statt CDN (" + str(len(css_text)) + " Zeichen)",
                       K1_OLD, build_k1_replacement(css_text), 1))
else:
    print("  !!  K1 uebersprungen: " + CSS_PATH + " fehlt.")
    print("      Der Editor bleibt damit vom CDN abhaengig und laeuft nicht offline.")

if os.path.isfile(FONTS_PATH):
    with open(FONTS_PATH, encoding="utf-8") as fh:
        fonts_css = fh.read()
    if not fonts_css.strip():
        sys.exit("K1b: " + FONTS_PATH + " ist leer.")
    if "</style>" in fonts_css:
        sys.exit("K1b: die Schriftdatei enthaelt </style> und wuerde den Block sprengen.")
    PATCHES.append(("K1b Schriften eingebettet (" + str(len(fonts_css)) + " Zeichen)",
                    K1B_OLD, build_k1b_replacement(fonts_css), 1))
else:
    print("  !!  K1b uebersprungen: " + FONTS_PATH + " fehlt.")
    print("      Der @import auf Google Fonts bleibt stehen.")

# Das fuenfte Feld markiert eine Massenersetzung eines kurzen Tokens.
# Dort gelten zwei andere Regeln: die Ersetzung darf vorher schon in der Datei
# stehen (showNotification( tut das), und danach darf kein einziges Vorkommen
# des alten Tokens uebrig sein. Bei den uebrigen Patches greift keine der
# beiden Regeln, weil viele von ihnen Zeilen in ihren eigenen Ankertext
# einfuegen und der Anker damit absichtlich Teil der Ersetzung bleibt.
for entry in PATCHES:
    name, old, new, expected = entry[0], entry[1], entry[2], entry[3]
    is_bulk = entry[4] if len(entry) > 4 else False

    found = data.count(old)
    assert found == expected, f"{name}: erwartet {expected} Fundstelle(n), gefunden {found}"

    if is_bulk:
        data = data.replace(old, new, expected)
        rest = data.count(old)
        assert rest == 0, f"{name}: nach der Ersetzung stehen noch {rest} Fundstelle(n)"
    else:
        assert data.count(new) == 0, f"{name}: Ersetzung liegt bereits vor, Abbruch"
        data = data.replace(old, new, expected)

    print(f"  ok  {name}")

with open(DST, "w", encoding="utf-8") as fh:
    fh.write(data)

print(f"geschrieben: {DST}")
