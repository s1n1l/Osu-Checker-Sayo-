STRINGS = {
    "app.title": "osu-checker — SayoDevice O3C",
    "app.subtitle": "SayoDevice O3C 游戏分析工具",

    "tab.analysis": "分析",
    "tab.record": "录制",
    "tab.training": "训练",
    "tab.settings": "设置",

    "analysis.drop_hint": "把 .osr 拖到这里，或点击“打开回放”",
    "analysis.open_replay": "打开回放…",
    "analysis.last_replay": "最新的 osu! 回放",
    "analysis.attach_session": "附加录制文件…",
    "analysis.attach_session_tip": (
        "来自“录制”标签页的文件。可加入真实的按键行程深度，这是回放里没有的。"),
    "analysis.attached": "录制：{name}",
    "analysis.no_replay": "尚未载入回放",
    "analysis.analysing": "正在分析 {name}…",
    "analysis.error": "错误：{message}",
    "analysis.no_osr_found": "在设置指定的文件夹中没有找到任何 .osr",
    "analysis.session_unreadable": "无法读取录制文件：{message}",
    "analysis.session_no_presses": "录制中没有带行程数据的按键，无法计算深度",
    "analysis.no_data": "没有数据",
    "analysis.map_not_found": (
        "索引中找不到此回放对应的谱面。如果谱面是最近添加的，请在“设置”中"
        "重建索引。"),

    "view.overview": "总览",
    "view.aim": "瞄准",
    "view.episodes": "问题片段",

    "stat.error": "击打误差",
    "stat.error_hint": "负为偏早 / 正为偏晚",
    "stat.ur": "UR",
    "stat.ur_hint": "回放记录 {fps:.0f} 帧/秒",
    "stat.left": "左手",
    "stat.right": "右手",
    "stat.hand_hint": "UR {ur:.0f} · {n} 个音符",
    "stat.counts": "300/100/50/miss",
    "stat.counts_hint": "本程序的统计",
    "stat.aim_spread": "瞄准离散度",
    "stat.aim_spread_hint": "以圆圈半径为单位",

    "plot.hist_title": "击打误差分布",
    "plot.hist_x": "误差（负为偏早 / 正为偏晚），毫秒",
    "plot.timeline_title": "整张谱面的误差变化",
    "plot.timeline_x": "时间，秒",
    "plot.timeline_y": "误差，毫秒",

    "hand.left": "左手",
    "hand.right": "右手",

    "col.bpm": "BPM",
    "col.notes": "音符",
    "col.error": "误差",
    "col.ur": "UR",
    "col.drift": "漂移",
    "col.misses": "miss",
    "col.extras": "多余",

    "aim.plot_title": "光标相对圆圈中心的落点",
    "aim.axis_px": "osu! 像素",
    "aim.by_jump": "按跳跃距离",
    "aim.by_dir": "按跳跃方向",
    "aim.col_jump": "跳跃，px",
    "aim.col_notes": "音符",
    "aim.col_spread": "离散度",
    "aim.col_edge": "边缘命中",
    "aim.col_over": "过冲",
    "aim.col_over_pct": "过冲占比",
    "aim.col_dir": "方向",
    "aim.no_data": "此回放没有光标数据。",
    "aim.radius": "圆圈半径",
    "aim.bias": "中心偏移",
    "aim.bias_hint": "黄色十字表示你的平均落点",
    "aim.spread": "离散度",
    "aim.spread_value": "半径的 {value:.2f} 倍",
    "aim.edge": "边缘命中",
    "aim.overshoot": "过冲",
    "aim.overshoot_value": "{px:.1f} px，占 {pct:.0f}% 的跳跃",

    "ep.head": "谱面中失分最多的片段，以及数据显示的原因",
    "ep.col_time": "时间",
    "ep.col_tempo": "速度",
    "ep.col_notes": "音符",
    "ep.col_loss": "失分",
    "ep.col_cause": "原因",
    "ep.col_what": "具体情况",
    "ep.cause.late": "跟不上",
    "ep.cause.early": "抢拍",
    "ep.cause.scatter": "离散",
    "ep.cause.aim": "瞄准",
    "ep.cause.mixed": "混合",
    "ep.what.late": "误差从 {early:+.0f} 毫秒漂到 {late:+.0f} 毫秒，手跟不上节奏",
    "ep.what.early": "持续偏早，平均 {mean:+.0f} 毫秒",
    "ep.what.scatter": "中心正常（{mean:+.0f} 毫秒），但 UR 达 {ur:.0f}，敲击不稳",
    "ep.what.aim": "光标距中心 {spread:.2f} 倍半径，{edge:.0f}% 打在边缘，"
                   "问题在瞄准而非敲击",
    "ep.what.mixed": "误差 {mean:+.0f} 毫秒，UR {ur:.0f}",
    "ep.miss": "{n} 个 miss",
    "ep.hundred": "{n}×100",
    "ep.fifty": "{n}×50",
    "ep.none": "—",

    "rec.info": (
        "同时记录三个来源：仅来自 O3C 的按键（Raw Input 按 "
        "VID_8089&PID_0009 过滤）、通过轮询设备得到的模拟键程，以及光标"
        "位置。Windows 的按键自动重复会被过滤掉。"),
    "rec.focus_only": "仅在 osu! 窗口处于前台时记录",
    "rec.hz_label": "键程轮询频率，Hz：",
    "rec.hz_tip": (
        "1500 表示不限制，取决于设备能回应多快。在 8000 Hz USB 轮询下约为"
        "每秒 2600 次采样，占用约 9% 的单核。实际达到的频率显示在状态栏。"),
    "rec.start": "开始录制",
    "rec.stop": "停止录制",
    "rec.save": "保存录制…",
    "rec.save_dialog": "保存录制",
    "rec.idle": "未在录制",
    "rec.running": ("录制中… {sec:5.0f} 秒 · 按键 {presses} · 键程 {travel} "
                    "（{hz:.0f} Hz） · 光标 {cursor} · 已过滤自动重复 "
                    "{repeats}"),
    "rec.stopped": ("已停止。按键 {presses}，已过滤自动重复 {repeats}，"
                    "键程采样 {travel}（{hz:.0f} Hz），光标点 {cursor}"),
    "rec.failed": "无法启动：{message}",
    "rec.no_analog": "   （没有模拟数据，未找到设备）",
    "rec.key": "槽位 {n} · {name}",
    "rec.saved": "已保存：{path}",
    "rec.depth_head": "设备阈值：触发 {trigger:.2f} 毫米，释放 {release:.2f} 毫米",
    "rec.depth_key": "按键",
    "rec.depth_n": "次数",
    "rec.depth_median": "深度中位数",
    "rec.depth_p10": "最浅的 10%",
    "rec.depth_margin": "距阈值余量",
    "rec.depth_bottom": "触底",

    "tr.placeholder": "请先在“分析”标签页分析一个回放，训练计划由其数据生成。",
    "tr.none": "这个回放没有产生具体的训练项，各项指标都在正常范围内。",
    "tr.priority": "优先级 {n}",
    "tr.scan": "从我的谱面库中挑选",
    "tr.target_bpm": "目标 BPM：",
    "tr.index_empty": "谱面索引为空，请先在“设置”中建立索引。",
    "tr.col_map": "谱面",
    "tr.col_diff": "难度",
    "tr.col_bpm": "连打 BPM",
    "tr.col_notes": "连打音符数",
    "tr.col_cs": "CS",
    "tr.col_od": "OD",

    "set.songs": "osu!stable — Songs 文件夹",
    "set.replays": "osu!stable — Replays 文件夹",
    "set.lazer": "osu!lazer — 数据文件夹",
    "set.save": "保存设置",
    "set.rebuild": "重建谱面索引",
    "set.saved": "设置已保存",
    "set.scanning": "扫描中… {i}/{total}   {name}",
    "set.done": "完成。新增 {added}，共 {total}",
    "set.index_count": "索引中的谱面：{n}",
    "set.language": "语言",
    "set.language_hint": "立即生效",
    "set.browse": "选择文件夹",

    "sev.high": "重要",
    "sev.medium": "值得注意",
    "sev.info": "参考",
    "area.device": "设备",
    "area.technique": "技术",
    "area.game": "游戏设置",

    "find.no_data.title": "没有数据",
    "find.no_data.detail": "回放中没有能与音符对应上的按键。",

    "find.fps.title": "回放以 {fps:.0f} Hz 记录",
    "find.fps.detail": ("回放每 {ms:.0f} 毫秒才写入一帧，因此这里的所有误差都"
                        "被取整到这个精度，测得的 UR 偏高。"),
    "find.fps.action": ("在 osu! 中提高帧数上限（Unlimited）。精确的时间数据"
                        "来自本程序的录制功能，精度约 1 毫秒。"),

    "find.offset.title": "系统性偏移 {mean:+.1f} 毫秒（{direction}）",
    "find.offset.late": "偏晚",
    "find.offset.early": "偏早",
    "find.offset.detail": ("整张谱面的平均误差为 {mean:+.1f} 毫秒。这么平稳的"
                           "偏移通常不是手的问题，而是音频偏移或延迟。"),
    "find.offset.action": ("可以尝试把 universal offset 调整 {shift:+.0f} 毫秒。"
                           "务必用 5–10 个回放验证：单张谱面的偏移会有 ±10 "
                           "毫秒的浮动，单看一张说明不了什么。"),

    "find.hands.title": "两手不同步，相差 {gap:.1f} 毫秒",
    "find.hands.detail_left": ("左手 {left:+.1f} 毫秒，右手 {right:+.1f} 毫秒。"
                               "左手持续偏晚。"),
    "find.hands.detail_right": ("左手 {left:+.1f} 毫秒，右手 {right:+.1f} 毫秒。"
                                "右手持续偏晚。"),
    "find.hands.action_left": ("调设备参数解决不了这个问题，两个键的阈值本来"
                               "就一样。用节拍器练单点，有意识地把左手往前带。"),
    "find.hands.action_right": ("调设备参数解决不了这个问题，两个键的阈值本来"
                                "就一样。用节拍器练单点，有意识地把右手往前带。"),

    "find.hands_ur.title": "有一只手明显更不稳（{hand}）",
    "find.hands_ur.detail": "左手 UR {left:.0f}，右手 UR {right:.0f}。",
    "find.hands_ur.action": "{hand} 的离散度更大，正是它限制了你的精度。",

    "find.drift.title": "手跟不上 {bpm:.0f} BPM 的节奏",
    "find.drift.detail": ("在一段连打之内，误差从头到尾增加了 {drift:+.1f} 毫秒"
                          "（{notes} 个音符，UR {ur:.0f}，miss {miss:.1f}%）。"
                          "多余按键只有 {extra:.1f}%，所以这不是多打，而是"
                          "速度不够。"),
    "find.drift.action": ("用短段落练 {bpm:.0f} BPM 的耐力。设备设置在这里帮"
                          "不上忙，它改变不了手的速度。"),

    "find.overstream.title": "在 {bpm:.0f} BPM 上多打",
    "find.overstream.detail": ("多余按键达 {extra:.1f}%，而漂移只有 "
                               "{drift:+.1f} 毫秒，说明你按的次数比音符还多。"),
    "find.overstream.action": "数清连打里的音符，而不是用手指去追节奏。",

    "find.slow_extras.title": "慢速段落里的多余按键（{bpm:.0f} BPM）",
    "find.slow_extras.detail": ("有 {extra:.1f}% 的按键没有落在任何音符上，"
                                "而这里节奏并不快，手完全跟得上"
                                "（漂移 {drift:+.1f} 毫秒）。"),
    "find.slow_extras.action": "问题不在速度，而在多余动作，手指在音符之间"
                               "“预备性”地敲击。",

    "find.double.title": "疑似双击触发",
    "find.double.detail": ("有 {n} 次按键在同一个键上距上一次不到 45 毫秒"
                           "（占全部按键的 {pct:.1f}%）。"),
    "find.double.action": "提高 RT Release，或降低 Rapid Trigger 灵敏度。",

    "find.no_double.title": "未发现双击触发",
    "find.no_double.detail": ("快于 45 毫秒的重复按键：{total} 次中有 {n} 次。"
                              "Rapid Trigger 工作正常。"),
    "find.no_double.action": "没有理由改动 RT。",

    "find.underpress.title": "按压深度勉强达到触发点",
    "find.underpress.detail": ("典型按压深度为 {peak:.0f} 微米，而阈值是 "
                               "{trigger:.0f} 微米，余量只有 {margin:.0f} 微米。"),
    "find.underpress.action": ("提高灵敏度：把 Trigger 从 {now:.2f} 毫米降到 "
                               "{suggest:.2f} 毫米左右。"),

    "tr.ex.stream.title": "{bpm:.0f} BPM 连打耐力",
    "tr.ex.stream.why": ("在 {bpm:.0f} BPM 上，一段连打从头到尾误差增加 "
                         "{drift:+.1f} 毫秒（{notes} 个音符，UR {ur:.0f}）。"
                         "连打的开头你踩得准，说明速度是够的，缺的是把节奏"
                         "维持住。"),
    "tr.ex.stream.how": ("短段落练习：在 {base:.0f} BPM 上打 4 小节连打，休息，"
                         "重复 10 次。当 {base:.0f} 的漂移降到 8 毫秒以下，"
                         "再加 5 BPM。在极限上刷长图反而有害，那是在训练自己"
                         "忍受脏的敲击，而不是练干净。"),
    "tr.ex.stream.check": ("把回放放进本程序，看 {bpm:.0f} BPM 那一行："
                           "漂移应当小于 8 毫秒。"),

    "tr.ex.overstream.title": "消除 {bpm:.0f} BPM 上的多余按键",
    "tr.ex.overstream.why": ("有 {extra:.1f}% 的按键没有落在任何音符上，而这里"
                             "节奏很慢，也没有漂移（{drift:+.1f} 毫秒）。"
                             "手指在“预备性”地敲。"),
    "tr.ex.overstream.how": ("有意识地少打：宁可漏掉一个音符，也不要多按一下。"
                             "出声数拍会有帮助。"),
    "tr.ex.overstream.check": "该 BPM 的“多余”一列应降到 1% 以下。",

    "tr.ex.aim_jump.title": "{lo:.0f} px 以上跳跃的准度",
    "tr.ex.aim_jump.why": ("这类跳跃中有 {edge:.0f}% 的音符是用边缘蹭到的，"
                           "平均过冲 {over:.1f} px（圆圈半径 {radius:.0f} px）。"),
    "tr.ex.aim_jump.how": ("在舒适的 BPM 下打间距大的图，有意识地把光标停在"
                           "中心，而不是“落在圈里就行”。数位板在这里有优势："
                           "位置是绝对的，手可以记住中心。"),
    "tr.ex.aim_jump.check": "该距离下的“边缘命中”应降到 8% 以下。",

    "tr.ex.aim_brake.title": "光标制动",
    "tr.ex.aim_brake.why": "{pct:.0f}% 的跳跃存在过冲，平均 {px:.1f} px。",
    "tr.ex.aim_brake.how": "打慢速大跳的图，重点放在停住上。",
    "tr.ex.aim_brake.check": "过冲比例应降到 20% 以下。",

    "tr.ex.hands.title_left": "双手同步（左手偏慢）",
    "tr.ex.hands.title_right": "双手同步（右手偏慢）",
    "tr.ex.hands.why": "两手的平均误差相差 {gap:.1f} 毫秒。",
    "tr.ex.hands.how_left": ("节拍器，双手交替单点，有意识地把左手往前带。"
                             "设备阈值与此无关，两个键本来就一样。"),
    "tr.ex.hands.how_right": ("节拍器，双手交替单点，有意识地把右手往前带。"
                              "设备阈值与此无关，两个键本来就一样。"),
    "tr.ex.hands.check": "两手差异小于 2 毫秒。",

    "tr.ex.scatter.title": "敲击稳定性",
    "tr.ex.scatter.why": ("在 {n} 个问题片段中，误差中心是正常的，但离散度很大"
                          "，说明你听得准节奏，只是手敲得不匀。"),
    "tr.ex.scatter.how": "配节拍器打慢图，目标是均匀而不是快。",
    "tr.ex.scatter.check": "这些片段的 UR 低于 200。",

    "tr.ex.early.title": "连打起手抢拍",
    "tr.ex.early.why": "在 {n} 个片段中你持续偏早。",
    "tr.ex.early.how": "有意识地比“感觉该按”的时候更晚一点开始连打。",
    "tr.ex.early.check": "这些片段的平均误差在 ±5 毫秒以内。",

    "tab.trainer": "训练器",
    "view.playback": "回看",
    "view.tapping": "敲击",

    "pb.play": "播放",
    "pb.pause": "暂停",
    "pb.jump_placeholder": "跳到问题片段…",
    "pb.distance": "光标距中心 {px:.0f} px（{frac:.2f} 倍半径）",
    "pb.error": "命中 {ms:+.0f} 毫秒",
    "pb.miss": "MISS",
    "pb.extra": "多余按键",

    "tap.hold": "按键保持时间",
    "tap.hold_value": "{ms:.0f} 毫秒",
    "tap.hold_spread": "离散 {spread:.0f} 毫秒",
    "tap.hand_gap": "两手保持时间差",
    "tap.alternation": "双手交替率",
    "tap.single": "同一只手连续两次以上",
    "tap.max_bpm": "能维持的最快速度",
    "tap.fatigue": "疲劳",
    "tap.fatigue_hint": "连打段落 UR 从前三分之一到后三分之一的增长",
    "tap.repeats": "同键快于 45 毫秒的重复",
    "tap.hist_title": "按键间隔",
    "tap.hist_x": "间隔，毫秒",
    "tap.roll_title": "整张谱面的速度与稳定性",
    "tap.roll_y": "BPM",
    "tap.roll_y2": "UR",
    "tap.runs_title": "同一只手连续按了几次",
    "tap.col_run": "连续",
    "tap.col_count": "次数",
    "tap.no_data": "这个回放里的按键太少。",

    "aim.speed": "按下瞬间的光标速度",
    "aim.speed_value": "{v:.2f} px/毫秒",
    "aim.settle": "按下前已在圈内停留",
    "aim.on_arrival": "刚到就点",
    "aim.on_arrival_hint": "光标尚未稳定就点击的跳跃占比",
    "aim.col_speed": "速度",
    "aim.col_settle": "停留",

    "trn.info": (
        "选一个节奏型和速度：音符会向线移动，你负责回应它们。这不是节拍器 —— "
        "其中有休止，而休止之后如何进入一段，通常才是丢分的地方。节拍器仍在下面"
        "按拍打点。按键只从 O3C 读取。"),
    "trn.target_bpm": "目标 BPM：",
    "trn.duration": "时长，秒：",
    "trn.sound": "节拍器声音",
    "trn.start": "开始",
    "trn.stop": "停止",
    "trn.card_bpm": "当前 BPM",
    "trn.card_ur": "间隔 UR",
    "trn.card_drift": "漂移，毫秒",
    "trn.card_left": "剩余秒数",
    "trn.plot_title": "按键间隔",
    "trn.plot_x": "第几次按键",
    "trn.plot_y": "毫秒",
    "trn.idle": "设定速度后点击「开始」。",
    "trn.count_in": "预备…",
    "trn.count_in_left": "预备：{n}",
    "trn.no_device": "无法开始按键捕获：{message}",
    "trn.too_few": "按键次数太少，无法判断。",
    "trn.result_held": (
        "稳住了。{hits}/{notes} 个音符（{acc:.0f}%），击打误差 {error:+.1f} 毫秒，UR {ur:.0f}，miss {misses} 个，多余按键 {extras} 次，交替 {alt:.0f}%，约 {bpm:.0f} BPM，目标 {target:.0f}。"),
    "trn.result_missed": (
        "没稳住。{hits}/{notes} 个音符（{acc:.0f}%），击打误差 {error:+.1f} 毫秒，UR {ur:.0f}，miss {misses} 个，多余按键 {extras} 次，交替 {alt:.0f}%，约 {bpm:.0f} BPM，目标 {target:.0f}。"),

    # --- 总览 -----------------------------------------------------------
    "ov.findings_title": "分析结果",
    "ov.summary": "{high} 项需要改 · {medium} 项值得留意 · {info} 项供参考",
    "ov.fix": "怎么做：",
    "ov.legend_title": "怎么看这一页",
    "ov.legend_body": (
        "<b>击打误差</b> —— 按键与音符相差多少毫秒。负数是偏早，正数是偏晚。"
        "整张图只给一个数会掩盖很多东西，所以右边的表格按速度拆开了。<br><br>"
        "<b>UR</b> —— 这些误差的离散程度（标准差的十倍）。越小越稳：低于 150 "
        "很紧，高于 250 则偏散。它不说明你偏早还是偏晚，只说明你波动多大。"
        "<br><br>"
        "<b>左手与右手</b> —— 两个按键分开统计。两只手长期存在固定差值是习惯"
        "问题，不是设备问题：两个键的触发点完全一样。<br><br>"
        "<b>漂移</b> —— 误差从一段连打的开头到结尾增加了多少。超过约 8 毫秒，"
        "说明手已经跟不上速度：音符继续来，手却在往后掉。<br><br>"
        "<b>多余按键</b> —— 没有打在任何音符上的按键。多余多而漂移小，是相反"
        "的问题：手指在多按，而不是速度不够。转盘期间的按键不计入。<br><br>"
        "<b>Miss</b> —— 在 50 判定窗内完全没有按键的音符。<br><br>"
        "<b>300 / 100 / 50 / miss</b> —— 这里是用回放对照谱面自己算的，和结算"
        "画面差一两个音符属于正常。<br><br>"
        "<b>严重程度。</b>重要 = 该动手改的；值得知道 = 确实存在但暂时代价不"
        "大；仅供参考 = 只是一个测量结果，不需要动作。"),
    "ov.table_title": "按速度拆分",
    "ov.table_hint": "谱面里每一段间隔稳定的连打，按 10 BPM 一档归类。漂移和"
                     "多余按键这两列，正是区分“速度不够”和“手指多动”的关键。",
    "plot.hist_hint": "绿色虚线是 300 判定窗的边界，橙色是 100。整体偏离中线"
                      "是偏移；又宽又平则是离散。",
    "plot.timeline_hint": "每个音符一个点，蓝色是左手，粉色是右手。逐渐上移的"
                          "带状区域就是手开始掉速的地方。",

    # --- 回放与谱面对齐 -------------------------------------------------
    "align.suspect": (
        "这个回放和这张谱面对不上 —— 只有 {pct:.0f}% 的音符附近有按键。下面的"
        "击打误差、瞄准和回放都不可靠。通常是游玩之后 .osu 文件被改过，或者"
        "回放来自别的模式。"),
    "align.corrected": (
        "回放时钟相对谱面偏了 {sec:+.2f} 秒，已经校正，现在有 {pct:.0f}% 的"
        "音符能对上。osu!stable 在部分游玩中会用另一套时钟写第一帧，照字面"
        "处理会把整条时间轴平移整段前奏。"),
    "align.searched": (
        "这个回放的两种时钟解读都对不上谱面，因此偏移量是搜索出来的：在 {sec:+.2f} 秒"
        "处有 {pct:.0f}% 的音符能对上，下面显示的就是这个结果。这是一个“碰巧吻合”的"
        "猜测，而不是文件里写明的东西 —— 请谨慎看待这些数字。"),
    "align.suspect_playback": (
        "这里光标不会跟着音符走：回放与谱面只有 {pct:.0f}% 的音符能对上。"),
    "align.corrected_playback": (
        "回放时钟已校正 {sec:+.2f} 秒，让光标与音符对齐。"),

    # --- 瞄准 -----------------------------------------------------------
    "aim.summary_title": "数据",
    "aim.help_title": "怎么看这张散点图",
    "aim.help_body": (
        "每个点是一个音符，画在按下时光标相对该音符圆心的位置。图上的上方就是"
        "游戏区域的上方。<br><br>"
        "<b>蓝色圆环</b>是这张谱面 CS 对应的音符本身。"
        "<b>虚线圆环</b>在 0.75 半径处：越过它的点属于蹭边，稍有闪失就会变成 "
        "miss。<b>黄色十字</b>是你的平均落点：如果它偏离中心，说明整体瞄准往"
        "那个方向偏。<br><br>"
        "<b>蓝环之外的点不是 miss。</b>回放每帧才存一次光标位置，所以用的是离"
        "按下最近的那一帧。大跳时光标在两帧之间会走很远，一个打得干净的音符照"
        "样可能被画到环外。因此“圆外占比”旁边会写出光标一帧能走多少像素：如果"
        "帧率低，这个占比说的是录制，而不是你的瞄准；如果帧率高而占比仍然大，"
        "那就是真的还没到位就点了。<br><br>"
        "<b>颜色</b>是音符的判定：蓝 300，绿 100，橙 50。miss 不画 —— 没有按键"
        "可以定位。转盘期间的音符也被排除，因为转盘会把光标拖到场地边缘。"),
    "aim.plot_legend": "蓝环 —— 音符 · 虚线环 —— 0.75 半径 · 黄色十字 —— 你的"
                       "平均落点 · 点的颜色 —— 300 / 100 / 50",
    "aim.spread_hint": "到圆心的平均距离；低于 0.40 很紧，高于 0.60 说明大多数"
                       "音符都是蹭边打到的",
    "aim.edge_hint": "落在 0.75 半径之外的音符 —— 速度一上去，最先变成 miss 的"
                     "就是它们",
    "aim.outside": "圆外占比",
    "aim.outside_hint": "在这些音符上，光标每帧大约移动 {px:.0f} px"
                        "（{ms:.0f} 毫秒一帧），而它的位置是在两帧之间插值出来的"
                        " —— 光这一点就足以把一次干净的击打画到环外一点。另一种"
                        "情况是：某次按键只是按时间被我们配到了这个音符，而 osu! "
                        "本来还要求光标在圈内。",
    "aim.overshoot_hint": "光标冲过音符多远才折回来 —— 刹车晚既损失准度也损失"
                          "时间",
    "aim.by_jump_hint": "同样的数据，按光标到达音符所需的距离拆开",
    "aim.by_dir_hint": "→ 表示向右的跳。某个方向明显更差，通常是握持方式或设备"
                       "在桌面上的位置问题。",

    # --- 问题片段 -------------------------------------------------------
    "ep.causes_hint": "掉速 —— 误差在连打内部持续增大 · 抢拍 —— 一直偏早 · "
                      "离散 —— 中心正常但波动大 · 瞄准 —— 问题在光标而不在手",

    # --- 敲击 -----------------------------------------------------------
    "tap.help_title": "怎么看这些数字",
    "tap.help_body": (
        "这些数字描述的是按键本身，而不是按键离音符有多近 —— 手可以非常均匀，"
        "却打着错误的节奏。<br><br>"
        "<b>交替率</b>接近 100% 说明两只手确实在轮换。任何连续两次以上落在同一"
        "只手上的情况，都意味着那一刻是一只手独自扛着连打，而速度通常就是在"
        "那里丢的。<br><br>"
        "<b>最快持续速度</b>是全图任意连续十六次按键中最快的一段，换算成连打 "
        "BPM。那是上限，不是你能稳住的速度。<br><br>"
        "<b>疲劳</b>比较谱面前三分之一和后三分之一的 UR，只统计连打速度的片段。"
        "正值越大，说明越到后面手越散。<br><br>"
        "<b>同键 45 毫秒内的重复</b>比手指能动的速度还快。只要不是 0，问题就在"
        "轴体或 Rapid Trigger，而不在你。"),
    "tap.hold_hint": "按键保持按下的时长；离散程度比数值本身更重要",
    "tap.hand_gap_hint": "左手按压时长减去右手",
    "tap.alternation_hint": "换手的按键占比",
    "tap.single_hint": "同一只手连续两次及以上的按键占比",
    "tap.max_bpm_hint": "最快的连续十六次按键，换算成连打 BPM",
    "tap.repeats_hint": "同一个键在 45 毫秒内按了两次 —— 双击的典型特征",
    "tap.runs_hint": "1 表示两手正常交替；2 及以上表示有一只手连打了好几个音符",
    "tap.hist_hint": "每个波峰对应谱面里的一种音符间隔；最高的那个就是你停留"
                     "时间最长的速度",
    "tap.roll_hint": "蓝色是你按键的速度，粉色是那一刻的不均匀程度",

    # --- 回放 -----------------------------------------------------------
    "pb.keys_hint": "空格 —— 播放 / 暂停 · ← → —— 一秒 · Shift + ← → —— 五秒 · "
                    "点击上方色带可跳转",
    "pb.legend": "白点 —— 光标，按住键时带一圈光环 · 轨迹上的蓝点和粉点 —— "
                 "每次按键落在哪里，分别是左手和右手 · 红色圆环 —— 没打在任何"
                 "音符上的按键 · 黄色轨迹 —— 最近 0.4 秒 · 红色虚线 —— 从光标"
                 "到当前判定的音符 · 圆圈颜色 —— 300 / 100 / 50 / miss",

    # --- 录制 -----------------------------------------------------------
    "rec.controls_title": "录制",
    "rec.keys_hint": "正在监听按键：{keys} —— 可在“设置”中修改",
    "rec.travel_title": "按键行程，实时",
    "rec.travel_hint": "静止为 0，按到底为 4000 µm",
    "rec.depth_title": "你实际按下多深",
    "rec.depth_hint": "录制结束后，用每次按键内部的模拟采样计算。余量一列，就是"
                      "你最轻的那些按键距离触发点还剩多少。",

    # --- 训练计划 -------------------------------------------------------
    "tr.head_title": "训练计划",
    "tr.head_body": "这个回放给出了 {n} 项。先从这一项开始：{first}",
    "tr.problem": "问题是什么",
    "tr.drill": "练什么",
    "tr.target": "达标标准",
    "tr.open_trainer": "以 {bpm:.0f} BPM 练习",
    "tr.maps_title": "你收藏里的谱面",
    "tr.maps_hint": "目标速度附近的连打，取自索引中的谱面。",

    # --- 设置 -----------------------------------------------------------
    "set.general_title": "通用",
    "set.keys_title": "设备按键",
    "set.keys_hint": "点击按钮，然后按下设备上的那个键。只有这些键会被记录 —— "
                     "你输入的其他内容一概看不到。Esc 取消。",
    "set.key_slot": "槽位 {n}",
    "set.key_slot_hint": "模拟通道 {n}",
    "set.key_prompt": "请按一个键…",
    "set.key_taken": "{key} 已经绑定到另一个槽位",
    "set.keys_now": "已绑定：{keys}",
    "set.thresholds_title": "设备触发点",
    "set.thresholds_hint": "在 SayoDevice 配置器里设置的触发点和释放点。不会向"
                           "设备写入任何东西：这两个值只用来计算你的按键还剩"
                           "多少余量。",
    "set.trigger": "触发",
    "set.release": "释放",
    "set.paths_title": "文件夹与谱面索引",
    "set.paths_hint": "回放和谱面所在的位置。索引负责把一个回放对应回它所游玩"
                      "的 .osu 文件。",

    # --- 节拍训练 -------------------------------------------------------
    "trn.controls_title": "设置",
    "trn.keys_hint": "正在读取按键：{keys} —— 可在“设置”中修改",
    "trn.card_bpm_hint": "最近十六次按键",
    "trn.card_ur_hint": "间隔的离散程度",
    "trn.card_drift_hint": "当前速度偏离目标多少",
    "trn.card_left_hint": "剩余秒数",
    "trn.plot_hint": "绿线是目标 BPM 要求的间隔；每个点是一次按键",

    "unit.ms": "毫秒",
    "trn.result_noise": ("{total} 个间隔中有 {n} 个短于 {ms:.0f} 毫秒 —— 比手能敲出来的还快，已被排除。程序全程都跟得上，所以这是轴体抖动：请在 SayoDevice 配置器里提高 RT Release。"),
    "trn.result_stalled": ("{total} 个间隔中有 {n} 个短于 {ms:.0f} 毫秒，已被排除。读取按键期间本机卡顿了 {stalls} 次，最严重 {worst} 毫秒 —— 因此其中一部分是挤在一起到达的按键，而不是你真的按了两下。请关掉其他占用资源的程序后重试。"),

    # --- 训练器节奏型 -----------------------------------------------------
    "trn.pattern": "节奏型：",
    "trn.pat.stream": "连续长串",
    "trn.pat.stream_hint": "完全没有休止。只练耐力 —— 有用，但谱面要求你的并不是这个。",
    "trn.pat.long": "长串",
    "trn.pat.long_hint": "十六个音符，然后休息两拍。长到手会开始飘，又短到能在中间恢复。",
    "trn.pat.burst": "短爆发",
    "trn.pat.burst_hint": "五到九个音符一组，之间空一拍半，顺序打乱，让你记不住形状。"
                          "这一项最能看出你进爆发的时机准不准。",
    "trn.pat.triple": "三连",
    "trn.pat.triple_hint": "三个音符，休息一拍，循环。短到整段就是一个“进入”。",
    "trn.pat.double": "双连",
    "trn.pat.double_hint": "两个音符，休息一拍，循环。最难打干净，因为没有可以进入状态的连打段。",
    "trn.pat.mixed": "混合",
    "trn.pat.mixed_hint": "从一个到八个音符，随机排列。最接近真实谱面。",

    "trn.lane_idle": "开始之后，节奏会显示在这里",
    "trn.lane_hint": "音符向白线移动 —— 音符经过白线时按键。较大的蓝色圆圈是一段的开头。"
                     "绿、橙、红表示你有多准；红色虚线圆圈表示这个音符没有任何按键。"
                     "下方的竖线是你的按键：蓝色是左键，粉色是右键。",

    "trn.card_error": "击打误差",
    "trn.card_error_hint": "负为偏早／正为偏晚，相对于节奏",
    "trn.card_hits": "命中",
    "trn.card_hits_hint": "已经过去的音符中，有按键回应的数量",

    "trn.result_opener_late": "你进入每段的时间比维持时晚 {gap:.0f} 毫秒 —— 速度是够的，"
                              "起手不够。休止之后要比感觉上更早进入。",
    "trn.result_opener_early": "你进入每段的时间比维持时早 {gap:.0f} 毫秒 —— 抢了休止，"
                               "然后一路硬撑。",
}
