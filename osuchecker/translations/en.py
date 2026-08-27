STRINGS = {
    "app.title": "osu-checker — SayoDevice O3C",
    "app.subtitle": "gameplay analyser for SayoDevice O3C",

    "tab.analysis": "Analysis",
    "tab.record": "Recording",
    "tab.training": "Training",
    "tab.settings": "Settings",

    "analysis.drop_hint": "Drop an .osr here — or press “Open replay”",
    "analysis.open_replay": "Open replay…",
    "analysis.last_replay": "Latest osu! replay",
    "analysis.attach_session": "Attach recording…",
    "analysis.attach_session_tip": (
        "A file from the Recording tab. Adds real key travel depth, which "
        "a replay does not contain."),
    "analysis.attached": "Recording: {name}",
    "analysis.no_replay": "No replay loaded",
    "analysis.analysing": "Analysing {name}…",
    "analysis.error": "Error: {message}",
    "analysis.no_osr_found": "No .osr found in the folders from Settings",
    "analysis.session_unreadable": "Cannot read the recording: {message}",
    "analysis.session_no_presses": (
        "The recording has no key presses with travel data — nothing to "
        "measure depth from"),
    "analysis.no_data": "No data",
    "analysis.map_not_found": (
        "The beatmap for this replay is not in the index. Rebuild the index "
        "in Settings if the map was added recently."),

    "view.overview": "Overview",
    "view.aim": "Aim",
    "view.episodes": "Problem spots",

    "stat.error": "Hit error",
    "stat.error_hint": "minus early / plus late",
    "stat.ur": "UR",
    "stat.ur_hint": "replay records {fps:.0f} frames/s",
    "stat.left": "Left",
    "stat.right": "Right",
    "stat.hand_hint": "UR {ur:.0f} · {n} notes",
    "stat.counts": "300/100/50/miss",
    "stat.counts_hint": "our own count",
    "stat.aim_spread": "Aim spread",
    "stat.aim_spread_hint": "in fractions of the circle radius",

    "plot.hist_title": "Hit error distribution",
    "plot.hist_x": "error (minus early / plus late), ms",
    "plot.timeline_title": "Hit error over the map",
    "plot.timeline_x": "time, s",
    "plot.timeline_y": "error, ms",

    "hand.left": "left",
    "hand.right": "right",

    "col.bpm": "BPM",
    "col.notes": "notes",
    "col.error": "error",
    "col.ur": "UR",
    "col.drift": "drift",
    "col.misses": "misses",
    "col.extras": "extras",

    "aim.plot_title": "Where the cursor landed relative to the circle centre",
    "aim.axis_px": "osu! pixels",
    "aim.by_jump": "By jump distance",
    "aim.by_dir": "By jump direction",
    "aim.col_jump": "jump, px",
    "aim.col_notes": "notes",
    "aim.col_spread": "spread",
    "aim.col_edge": "edge hits",
    "aim.col_over": "overshoot",
    "aim.col_over_pct": "% over",
    "aim.col_dir": "direction",
    "aim.no_data": "This replay has no cursor data.",
    "aim.radius": "Circle radius",
    "aim.bias": "Centre offset",
    "aim.bias_hint": "the yellow cross marks your average hit",
    "aim.spread": "Spread",
    "aim.spread_value": "{value:.2f} of the radius",
    "aim.edge": "Edge hits",
    "aim.overshoot": "Overshoot",
    "aim.overshoot_value": "{px:.1f} px on {pct:.0f}% of jumps",

    "ep.head": "The most expensive stretches of the map — where the points "
               "went and what the numbers say caused it",
    "ep.col_time": "time",
    "ep.col_tempo": "tempo",
    "ep.col_notes": "notes",
    "ep.col_loss": "lost",
    "ep.col_cause": "cause",
    "ep.col_what": "what happened",
    "ep.cause.late": "fell behind",
    "ep.cause.early": "rushed",
    "ep.cause.scatter": "scatter",
    "ep.cause.aim": "aim",
    "ep.cause.mixed": "mixed",
    "ep.what.late": "error crept from {early:+.0f} to {late:+.0f} ms — the "
                    "hand lost the tempo",
    "ep.what.early": "consistently early, mean {mean:+.0f} ms",
    "ep.what.scatter": "centre is fine ({mean:+.0f} ms) but UR is {ur:.0f} — "
                       "uneven tapping",
    "ep.what.aim": "cursor sat {spread:.2f} radius from centre, {edge:.0f}% "
                   "on the edge — aim fell apart, not tapping",
    "ep.what.mixed": "error {mean:+.0f} ms, UR {ur:.0f}",
    "ep.miss": "{n} miss",
    "ep.hundred": "{n}×100",
    "ep.fifty": "{n}×50",
    "ep.none": "—",

    "rec.info": (
        "Three sources at once: key presses from the O3C only (Raw Input "
        "filtered by VID_8089&PID_0009), analogue key travel polled from the "
        "device, and cursor position. Windows key auto-repeat is discarded."),
    "rec.focus_only": "Only while the osu! window is focused",
    "rec.hz_label": "Travel polling rate, Hz:",
    "rec.hz_tip": (
        "1500 means no limit: as fast as the device answers. At 8000 Hz USB "
        "polling that is about 2600 samples per second and ~9% of one core. "
        "The rate actually achieved is shown in the status line."),
    "rec.start": "Start recording",
    "rec.stop": "Stop recording",
    "rec.save": "Save recording…",
    "rec.save_dialog": "Save recording",
    "rec.idle": "Not recording",
    "rec.running": ("Recording… {sec:5.0f} s · presses {presses} · travel "
                    "{travel} ({hz:.0f} Hz) · cursor {cursor} · auto-repeat "
                    "discarded {repeats}"),
    "rec.stopped": ("Stopped. Presses {presses}, auto-repeat discarded "
                    "{repeats}, travel samples {travel} ({hz:.0f} Hz), cursor "
                    "points {cursor}"),
    "rec.failed": "Could not start: {message}",
    "rec.no_analog": "   (no analogue data — device not found)",
    "rec.key": "key {name}",
    "rec.saved": "Saved: {path}",
    "rec.depth_head": ("Device thresholds: actuation {trigger:.2f} mm, "
                       "release {release:.2f} mm"),
    "rec.depth_key": "key",
    "rec.depth_n": "presses",
    "rec.depth_median": "median depth",
    "rec.depth_p10": "weakest 10%",
    "rec.depth_margin": "margin to threshold",
    "rec.depth_bottom": "bottomed out",

    "tr.placeholder": ("Analyse a replay on the Analysis tab first — the plan "
                       "is built from its numbers."),
    "tr.none": "This replay did not produce any exercises — everything is "
               "within normal range.",
    "tr.priority": "PRIORITY {n}",
    "tr.why": "why:",
    "tr.how": "how:",
    "tr.check": "check:",
    "tr.scan": "Find maps in my collection",
    "tr.target_bpm": "target BPM:",
    "tr.index_empty": "The beatmap index is empty — build it in Settings.",
    "tr.col_map": "map",
    "tr.col_diff": "difficulty",
    "tr.col_bpm": "stream BPM",
    "tr.col_notes": "notes in stream",
    "tr.col_cs": "CS",
    "tr.col_od": "OD",

    "set.songs": "osu!stable — Songs folder",
    "set.replays": "osu!stable — Replays folder",
    "set.lazer": "osu!lazer — data folder",
    "set.save": "Save settings",
    "set.rebuild": "Rebuild beatmap index",
    "set.saved": "Settings saved",
    "set.scanning": "Scanning… {i}/{total}   {name}",
    "set.done": "Done. Added {added}, {total} in total",
    "set.index_count": "Beatmaps in index: {n}",
    "set.language": "Language",
    "set.language_hint": "applies immediately",
    "set.browse": "Choose folder",

    "sev.high": "IMPORTANT",
    "sev.medium": "WORTH KNOWING",
    "sev.info": "FOR REFERENCE",
    "area.device": "device",
    "area.technique": "technique",
    "area.game": "game settings",

    "find.no_data.title": "No data",
    "find.no_data.detail": "No key presses in this replay could be matched "
                           "to notes.",

    "find.fps.title": "Replay recorded at {fps:.0f} Hz",
    "find.fps.detail": ("A replay frame is written every {ms:.0f} ms, so every "
                        "error here is rounded to that. The measured UR is "
                        "inflated."),
    "find.fps.action": ("Raise the frame limit in osu! (Unlimited). Exact "
                        "timings come from our own recorder, which is accurate "
                        "to about 1 ms."),

    "find.offset.title": "Systematic offset {mean:+.1f} ms ({direction})",
    "find.offset.late": "late",
    "find.offset.early": "early",
    "find.offset.detail": ("Mean error across the whole map is {mean:+.1f} ms. "
                           "An offset this flat is usually not about the hands "
                           "but about audio offset or latency."),
    "find.offset.action": ("Try shifting the universal offset by {shift:+.0f} "
                           "ms. Check it on 5–10 replays first: a single map's "
                           "offset wanders by about ±10 ms and means little on "
                           "its own."),

    "find.hands.title": "Hands are {gap:.1f} ms out of sync",
    "find.hands.detail_left": ("left {left:+.1f} ms, right {right:+.1f} ms. "
                               "The left hand is consistently late."),
    "find.hands.detail_right": ("left {left:+.1f} ms, right {right:+.1f} ms. "
                                "The right hand is consistently late."),
    "find.hands.action_left": ("Device settings cannot fix this — both keys "
                               "have identical thresholds. Metronome work on "
                               "single notes, deliberately pulling the left "
                               "hand forward."),
    "find.hands.action_right": ("Device settings cannot fix this — both keys "
                                "have identical thresholds. Metronome work on "
                                "single notes, deliberately pulling the right "
                                "hand forward."),

    "find.hands_ur.title": "One hand is clearly less consistent ({hand})",
    "find.hands_ur.detail": "Left UR {left:.0f}, right UR {right:.0f}.",
    "find.hands_ur.action": "The {hand} hand has the wider spread — it is what "
                            "caps your accuracy.",

    "find.drift.title": "The hand cannot hold {bpm:.0f} BPM",
    "find.drift.detail": ("Within a stream the error grows by {drift:+.1f} ms "
                          "from start to end ({notes} notes, UR {ur:.0f}, "
                          "{miss:.1f}% misses). Extra presses are only "
                          "{extra:.1f}%, so this is not overstreaming — it is "
                          "a shortfall in speed."),
    "find.drift.action": ("Train stamina at {bpm:.0f} BPM in short bursts. "
                          "Device settings will not help here — they do not "
                          "change how fast a hand moves."),

    "find.overstream.title": "Overstreaming at {bpm:.0f} BPM",
    "find.overstream.detail": ("{extra:.1f}% extra presses with a drift of only "
                               "{drift:+.1f} ms — you are pressing more often "
                               "than there are notes."),
    "find.overstream.action": "Count the notes in a stream instead of chasing "
                              "the rhythm with your fingers.",

    "find.slow_extras.title": "Extra presses in slow sections ({bpm:.0f} BPM)",
    "find.slow_extras.detail": ("{extra:.1f}% of presses land on no note at "
                                "all, even though the tempo is low and the "
                                "hand keeps up (drift {drift:+.1f} ms)."),
    "find.slow_extras.action": ("The problem here is not speed but surplus "
                                "motion — fingers tapping “just in case” "
                                "between notes."),

    "find.double.title": "Looks like double actuation",
    "find.double.detail": ("{n} presses arrived less than 45 ms after the "
                           "previous one on the same key ({pct:.1f}% of all "
                           "presses)."),
    "find.double.action": "Raise RT Release or reduce Rapid Trigger "
                          "sensitivity.",

    "find.no_double.title": "No double actuation detected",
    "find.no_double.detail": ("Repeat presses faster than 45 ms: {n} out of "
                              "{total}. Rapid Trigger is behaving correctly."),
    "find.no_double.action": "There is no reason to change RT.",

    "find.underpress.title": "Presses barely reach the actuation point",
    "find.underpress.detail": ("Typical press depth is {peak:.0f} µm against a "
                               "{trigger:.0f} µm threshold — only "
                               "{margin:.0f} µm of margin."),
    "find.underpress.action": ("Make it more sensitive: lower Trigger from "
                               "{now:.2f} mm to about {suggest:.2f} mm."),

    "tr.ex.stream.title": "Stream stamina at {bpm:.0f} BPM",
    "tr.ex.stream.why": ("At {bpm:.0f} BPM the error grows by {drift:+.1f} ms "
                         "from the start to the end of a stream ({notes} "
                         "notes, UR {ur:.0f}). You start streams on time, so "
                         "the speed is there — what is missing is holding the "
                         "tempo."),
    "tr.ex.stream.how": ("Short bursts: 4 bars of stream at {base:.0f} BPM, "
                         "rest, repeat 10 times. Once drift at {base:.0f} "
                         "falls below 8 ms, raise it by 5 BPM. Long maps at "
                         "your limit hurt here: they train you to tolerate "
                         "dirty tapping rather than to tap cleanly."),
    "tr.ex.stream.check": ("Run a replay through this app and look at the "
                           "{bpm:.0f} BPM row: drift should be under 8 ms."),

    "tr.ex.overstream.title": "Remove extra presses at {bpm:.0f} BPM",
    "tr.ex.overstream.why": ("{extra:.1f}% of presses hit no note at all, even "
                             "though the tempo is low and there is no drift "
                             "({drift:+.1f} ms). Fingers are tapping on spec."),
    "tr.ex.overstream.how": ("Play slow maps deliberately under-tapping: "
                             "better to drop a note than to add a press. "
                             "Counting out loud helps."),
    "tr.ex.overstream.check": "The extras column for this BPM should drop "
                              "below 1%.",

    "tr.ex.aim_jump.title": "Accuracy on jumps from {lo:.0f} px",
    "tr.ex.aim_jump.why": ("On jumps like these {edge:.0f}% of notes are "
                           "caught with the edge of the cursor, and the mean "
                           "overshoot is {over:.1f} px (circle radius "
                           "{radius:.0f} px)."),
    "tr.ex.aim_jump.how": ("Maps with wide spacing at a comfortable BPM, "
                           "deliberately stopping the cursor in the centre "
                           "rather than somewhere inside the circle. A tablet "
                           "helps here: the position is absolute, so the hand "
                           "can memorise the centre."),
    "tr.ex.aim_jump.check": "Edge hits at this distance should fall below 8%.",

    "tr.ex.aim_brake.title": "Cursor braking",
    "tr.ex.aim_brake.why": "{pct:.0f}% of jumps overshoot, by {px:.1f} px on "
                           "average.",
    "tr.ex.aim_brake.how": "Slow maps with wide jumps, focusing on the stop.",
    "tr.ex.aim_brake.check": "Overshoot share should fall below 20%.",

    "tr.ex.hands.title_left": "Hand sync (left is behind)",
    "tr.ex.hands.title_right": "Hand sync (right is behind)",
    "tr.ex.hands.why": "Mean error differs between hands by {gap:.1f} ms.",
    "tr.ex.hands.how_left": ("Metronome, single notes alternating, "
                             "deliberately pulling the left hand forward. "
                             "Device thresholds are irrelevant here — they are "
                             "identical for both keys."),
    "tr.ex.hands.how_right": ("Metronome, single notes alternating, "
                              "deliberately pulling the right hand forward. "
                              "Device thresholds are irrelevant here — they "
                              "are identical for both keys."),
    "tr.ex.hands.check": "Difference between hands under 2 ms.",

    "tr.ex.scatter.title": "Tapping consistency",
    "tr.ex.scatter.why": ("In {n} problem spots the error centre is fine but "
                          "the spread is wide — you hear the tempo, but the "
                          "hand taps unevenly."),
    "tr.ex.scatter.how": "Slow maps with a metronome; the goal is evenness, "
                         "not speed.",
    "tr.ex.scatter.check": "UR on those stretches below 200.",

    "tr.ex.early.title": "Rushing stream starts",
    "tr.ex.early.why": "In {n} spots you were consistently early.",
    "tr.ex.early.how": "Deliberately start streams later than feels right.",
    "tr.ex.early.check": "Mean error on those stretches within ±5 ms.",

    "tab.trainer": "Trainer",
    "view.playback": "Playback",
    "view.tapping": "Tapping",

    "pb.play": "Play",
    "pb.pause": "Pause",
    "pb.jump_placeholder": "Jump to a problem spot…",
    "pb.distance": "cursor {px:.0f} px from centre ({frac:.2f} radius)",
    "pb.error": "hit {ms:+.0f} ms",
    "pb.miss": "MISS",
    "pb.extra": "extra press",

    "tap.hold": "Hold time",
    "tap.hold_value": "{ms:.0f} ms, spread {spread:.0f}",
    "tap.hand_gap": "Hold difference between hands",
    "tap.alternation": "Alternation",
    "tap.single": "Two or more in a row on one hand",
    "tap.max_bpm": "Fastest sustained tempo",
    "tap.fatigue": "Fatigue",
    "tap.fatigue_hint": "UR growth on stream sections, first third to last",
    "tap.repeats": "Repeats under 45 ms on the same key",
    "tap.hist_title": "Interval between presses",
    "tap.hist_x": "interval, ms",
    "tap.roll_title": "Tempo and steadiness over the map",
    "tap.roll_y": "BPM",
    "tap.roll_y2": "UR",
    "tap.runs_title": "How many presses in a row on one hand",
    "tap.col_run": "in a row",
    "tap.col_count": "times",
    "tap.no_data": "Not enough presses in this replay.",

    "aim.speed": "Cursor speed at the press",
    "aim.speed_value": "{v:.2f} px/ms",
    "aim.settle": "Settled in the circle before the press",
    "aim.on_arrival": "Clicked on arrival",
    "aim.on_arrival_hint": "jumps clicked before the cursor settled",
    "aim.col_speed": "speed",
    "aim.col_settle": "settle",

    "trn.info": (
        "Hold a tempo and watch it come apart. The metronome clicks once per "
        "beat and four presses are expected between clicks, which is how a "
        "stream at that BPM is counted. Presses are read from the O3C only."),
    "trn.target_bpm": "Target BPM:",
    "trn.duration": "Duration, s:",
    "trn.sound": "Metronome sound",
    "trn.start": "Start",
    "trn.stop": "Stop",
    "trn.card_bpm": "current BPM",
    "trn.card_ur": "UR of intervals",
    "trn.card_drift": "drift, ms",
    "trn.card_left": "seconds left",
    "trn.plot_title": "Interval between presses",
    "trn.plot_x": "press",
    "trn.plot_y": "ms",
    "trn.idle": "Set a tempo and press Start.",
    "trn.count_in": "Count-in…",
    "trn.count_in_left": "count-in: {n}",
    "trn.no_device": "Could not start key capture: {message}",
    "trn.too_few": "Too few presses to judge anything.",
    "trn.result_held": (
        "Held it. {bpm:.0f} BPM against a target of {target:.0f}, UR {ur:.0f}, "
        "{taps} presses, slowdown {slowdown:+.0f} BPM, alternation {alt:.0f}%, "
        "gaps dropped: {dropped}."),
    "trn.result_missed": (
        "Not held. {bpm:.0f} BPM against a target of {target:.0f}, UR {ur:.0f}, "
        "{taps} presses, slowdown {slowdown:+.0f} BPM, alternation {alt:.0f}%, "
        "gaps dropped: {dropped}."),
}
