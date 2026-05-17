# translations.py
# Supported languages and their UI string translations.
# RTL_LANGUAGES: languages that require right-to-left layout direction.
# SCRIPT_FONTS: preferred font per language (falls back to Segoe UI if not installed).

RTL_LANGUAGES = {"Arabic"}

SCRIPT_FONTS = {
    "Tamil":   "Noto Sans Tamil",
    "Chinese": "Microsoft YaHei",
    "Arabic":  "Segoe UI",       # Segoe UI covers Arabic script well on Windows
    "English": "Segoe UI",
}

# ── String keys used across the UI ────────────────────────────────────────────
# Each language must define ALL keys below.
#
# Keys:
#   menu_file              – "File" menu label
#   menu_language          – "Language" menu label
#   menu_help              – "Help" menu label
#   menu_exit              – "Exit Completely" action
#   menu_choose_language   – "Choose Language…" action
#   menu_quick_start       – "Quick Start Guide" action
#   menu_about             – "About" action
#
#   section_monitor        – section label above mode buttons
#   btn_single_file        – mode button
#   btn_folder             – mode button
#   btn_folder_recursive   – mode button
#
#   section_source         – section label above source path row
#   placeholder_source     – QLineEdit placeholder
#   section_destination    – section label above destination path row
#   placeholder_destination– QLineEdit placeholder
#   btn_browse             – browse button text
#
#   btn_start              – start monitor button
#   btn_stop               – stop button
#
#   error_select_source    – inline validation error
#   error_source_not_exist – inline validation error
#   error_source_must_folder  – inline validation error
#   error_source_must_file    – inline validation error
#   error_select_destination  – inline validation error
#   error_dest_not_folder     – inline validation error
#   error_same_path           – inline validation error
#   error_dest_inside_source  – inline validation error
#
#   filter_all             – log filter option
#   filter_changes         – log filter option
#   filter_errors          – log filter option
#   filter_label           – "Filter:" label in status bar
#
#   stat_files             – stat pill label
#   stat_folders           – stat pill label
#   stat_backups           – stat pill label
#
#   status_idle            – status bar text
#   status_running         – status bar text
#   status_stopped         – status bar text
#
#   log_placeholder        – log pane placeholder text
#
#   tray_show              – tray menu action
#   tray_exit              – tray menu action
#   tray_minimized_title   – tray balloon title
#   tray_minimized_body    – tray balloon body
#
#   dlg_language_title     – language dialog window title
#   dlg_language_search    – search box placeholder
#   dlg_ok                 – OK button
#   dlg_cancel             – Cancel button
#
#   msg_language_changed   – info message after language change (use {lang} placeholder)
#
#   quick_start_title      – QMessageBox title
#   quick_start_text       – QMessageBox HTML body
#
#   about_title            – QMessageBox title
#   about_description      – description line inside About body
# ──────────────────────────────────────────────────────────────────────────────

TRANSLATIONS = {

    # ── English ───────────────────────────────────────────────────────────────
    "English": {
        "menu_file":              "File",
        "menu_language":          "Language",
        "menu_help":              "Help",
        "menu_exit":              "Exit Completely",
        "menu_choose_language":   "Choose Language…",
        "menu_quick_start":       "Quick Start Guide",
        "menu_about":             "About",

        "section_monitor":        "MONITOR",
        "btn_single_file":        "Single File",
        "btn_folder":             "Folder",
        "btn_folder_recursive":   "Folder + Sub Folder",

        "section_source":         "SOURCE (File/Folder)",
        "placeholder_source":     "No source selected",
        "section_destination":    "BACKUP DESTINATION FOLDER",
        "placeholder_destination":"No destination selected",
        "btn_browse":             "Browse…",

        "btn_start":              "▶  Start Monitor",
        "btn_stop":               "Stop",

        "error_select_source":       "Please select a source.",
        "error_source_not_exist":    "Source path does not exist.",
        "error_source_must_folder":  "Source must be a folder for this mode.",
        "error_source_must_file":    "Source must be a file.",
        "error_select_destination":  "Please select a destination.",
        "error_dest_not_folder":     "Destination must be an existing folder.",
        "error_same_path":           "Source and destination cannot be the same.",
        "error_dest_inside_source":  "Destination cannot be inside source (infinite loop risk).",

        "filter_all":             "All Events",
        "filter_changes":         "Changes Only",
        "filter_errors":          "Errors Only",
        "filter_label":           "Filter:",

        "stat_files":             "📄 Files monitored",
        "stat_folders":           "📁 Folders",
        "stat_backups":           "💾 Backups made",

        "status_idle":            "Idle — waiting to start",
        "status_running":         "Running",
        "status_stopped":         "Idle — monitor stopped",

        "log_placeholder":        "Monitoring logs will appear here…",

        "tray_show":              "Show Window",
        "tray_exit":              "Exit Completely",
        "tray_minimized_title":   "Running",
        "tray_minimized_body":    "App minimized to system tray.",

        "dlg_language_title":     "Choose Language",
        "dlg_language_search":    "Search languages…",
        "dlg_ok":                 "OK",
        "dlg_cancel":             "Cancel",

        "msg_language_changed":   "Language changed to {lang}. Restart may be needed for full effect.",

        "quick_start_title":      "Quick Start",
        "quick_start_text": (
            "<b>Quick Start Guide</b><br><br>"
            "1. <b>Select Source:</b> Choose a file or folder to monitor.<br>"
            "2. <b>Select Destination:</b> Choose where backups will be saved.<br>"
            "3. <b>Choose Mode:</b><br>"
            "&nbsp;&nbsp;• Single File: Tracks one file.<br>"
            "&nbsp;&nbsp;• Folder (Shallow): Tracks immediate contents only.<br>"
            "&nbsp;&nbsp;• Folder (Recursive): Tracks folder + all subfolders.<br>"
            "4. <b>Start Monitor:</b> Begins real-time backup on save.<br><br>"
            "<i>Logs show every change. Use the filter dropdown to focus on errors or backups.</i>"
        ),

        "about_title":            "About",
        "about_description": (
            "Real-time file backup utility with change detection,<br>"
            "debounced saves, and system tray support."
        ),
    },

    # ── Tamil ─────────────────────────────────────────────────────────────────
    "Tamil": {
        "menu_file":              "கோப்பு",
        "menu_language":          "மொழி",
        "menu_help":              "உதவி",
        "menu_exit":              "முழுமையாக வெளியேறு",
        "menu_choose_language":   "மொழியை தேர்வு செய்யவும்…",
        "menu_quick_start":       "விரைவு தொடக்க வழிகாட்டி",
        "menu_about":             "பற்றி",

        "section_monitor":        "கண்காணிப்பு",
        "btn_single_file":        "ஒற்றை கோப்பு",
        "btn_folder":             "கோப்புறை",
        "btn_folder_recursive":   "கோப்புறை + உட்கோப்புறைகள்",

        "section_source":         "மூல (கோப்பு/கோப்புறை)",
        "placeholder_source":     "மூல தேர்வு செய்யப்படவில்லை",
        "section_destination":    "காப்புப்பிரதி இலக்கு கோப்புறை",
        "placeholder_destination":"இலக்கு தேர்வு செய்யப்படவில்லை",
        "btn_browse":             "உலாவு…",

        "btn_start":              "▶  கண்காணிப்பை தொடங்கு",
        "btn_stop":               "நிறுத்து",

        "error_select_source":       "மூலத்தை தேர்வு செய்யவும்.",
        "error_source_not_exist":    "மூல பாதை இல்லை.",
        "error_source_must_folder":  "இந்த பயன்முறைக்கு மூலம் ஒரு கோப்புறையாக இருக்க வேண்டும்.",
        "error_source_must_file":    "மூலம் ஒரு கோப்பாக இருக்க வேண்டும்.",
        "error_select_destination":  "இலக்கை தேர்வு செய்யவும்.",
        "error_dest_not_folder":     "இலக்கு ஒரு இருக்கும் கோப்புறையாக இருக்க வேண்டும்.",
        "error_same_path":           "மூலமும் இலக்கும் ஒன்றாக இருக்க முடியாது.",
        "error_dest_inside_source":  "இலக்கு மூலத்திற்குள் இருக்க முடியாது (முடிவற்ற சுழற்சி அபாயம்).",

        "filter_all":             "அனைத்து நிகழ்வுகள்",
        "filter_changes":         "மாற்றங்கள் மட்டும்",
        "filter_errors":          "பிழைகள் மட்டும்",
        "filter_label":           "வடிகட்டி:",

        "stat_files":             "📄 கண்காணிக்கப்படும் கோப்புகள்",
        "stat_folders":           "📁 கோப்புறைகள்",
        "stat_backups":           "💾 காப்புப்பிரதிகள்",

        "status_idle":            "செயலற்று — தொடங்க காத்திருக்கிறது",
        "status_running":         "இயங்குகிறது",
        "status_stopped":         "செயலற்று — கண்காணிப்பு நிறுத்தப்பட்டது",

        "log_placeholder":        "கண்காணிப்பு பதிவுகள் இங்கே தோன்றும்…",

        "tray_show":              "சாளரத்தை காட்டு",
        "tray_exit":              "முழுமையாக வெளியேறு",
        "tray_minimized_title":   "இயங்குகிறது",
        "tray_minimized_body":    "பயன்பாடு கணினி தட்டில் சிறுமப்படுத்தப்பட்டது.",

        "dlg_language_title":     "மொழியை தேர்வு செய்யவும்",
        "dlg_language_search":    "மொழிகளை தேடுங்கள்…",
        "dlg_ok":                 "சரி",
        "dlg_cancel":             "ரத்து செய்",

        "msg_language_changed":   "மொழி {lang} ஆக மாற்றப்பட்டது. முழு விளைவுக்கு மறுதொடக்கம் தேவைப்படலாம்.",

        "quick_start_title":      "விரைவு தொடக்கம்",
        "quick_start_text": (
            "<b>விரைவு தொடக்க வழிகாட்டி</b><br><br>"
            "1. <b>மூலத்தை தேர்வு செய்யவும்:</b> கண்காணிக்க ஒரு கோப்பு அல்லது கோப்புறையை தேர்வு செய்யவும்.<br>"
            "2. <b>இலக்கை தேர்வு செய்யவும்:</b> காப்புப்பிரதிகள் சேமிக்கப்படும் இடத்தை தேர்வு செய்யவும்.<br>"
            "3. <b>பயன்முறையை தேர்வு செய்யவும்:</b><br>"
            "&nbsp;&nbsp;• ஒற்றை கோப்பு: ஒரு கோப்பை மட்டும் கண்காணிக்கும்.<br>"
            "&nbsp;&nbsp;• கோப்புறை (மேலோட்டமான): நேரடி உள்ளடக்கங்களை மட்டும் கண்காணிக்கும்.<br>"
            "&nbsp;&nbsp;• கோப்புறை (சுழல்): கோப்புறை மற்றும் அனைத்து உட்கோப்புறைகளையும் கண்காணிக்கும்.<br>"
            "4. <b>கண்காணிப்பை தொடங்கு:</b> சேமிக்கும்போது நிகழ்நேர காப்புப்பிரதியை தொடங்கும்.<br><br>"
            "<i>பதிவுகள் ஒவ்வொரு மாற்றத்தையும் காட்டும். பிழைகள் அல்லது காப்புப்பிரதிகளில் கவனம் செலுத்த வடிகட்டி பட்டியலை பயன்படுத்துங்கள்.</i>"
        ),

        "about_title":            "பற்றி",
        "about_description": (
            "மாற்றம் கண்டறிதல், தாமதப்படுத்தப்பட்ட சேமிப்பு மற்றும்<br>"
            "கணினி தட்டு ஆதரவுடன் நிகழ்நேர கோப்பு காப்புப்பிரதி கருவி."
        ),
    },

    # ── Chinese (Simplified) ──────────────────────────────────────────────────
    "Chinese": {
        "menu_file":              "文件",
        "menu_language":          "语言",
        "menu_help":              "帮助",
        "menu_exit":              "完全退出",
        "menu_choose_language":   "选择语言…",
        "menu_quick_start":       "快速入门指南",
        "menu_about":             "关于",

        "section_monitor":        "监控",
        "btn_single_file":        "单个文件",
        "btn_folder":             "文件夹",
        "btn_folder_recursive":   "文件夹 + 子文件夹",

        "section_source":         "源（文件/文件夹）",
        "placeholder_source":     "未选择源",
        "section_destination":    "备份目标文件夹",
        "placeholder_destination":"未选择目标",
        "btn_browse":             "浏览…",

        "btn_start":              "▶  开始监控",
        "btn_stop":               "停止",

        "error_select_source":       "请选择源。",
        "error_source_not_exist":    "源路径不存在。",
        "error_source_must_folder":  "此模式下源必须是文件夹。",
        "error_source_must_file":    "源必须是文件。",
        "error_select_destination":  "请选择目标。",
        "error_dest_not_folder":     "目标必须是已存在的文件夹。",
        "error_same_path":           "源和目标不能相同。",
        "error_dest_inside_source":  "目标不能在源内部（有无限循环风险）。",

        "filter_all":             "所有事件",
        "filter_changes":         "仅变更",
        "filter_errors":          "仅错误",
        "filter_label":           "筛选：",

        "stat_files":             "📄 已监控文件",
        "stat_folders":           "📁 文件夹",
        "stat_backups":           "💾 已备份",

        "status_idle":            "空闲 — 等待启动",
        "status_running":         "运行中",
        "status_stopped":         "空闲 — 监控已停止",

        "log_placeholder":        "监控日志将显示在此处…",

        "tray_show":              "显示窗口",
        "tray_exit":              "完全退出",
        "tray_minimized_title":   "运行中",
        "tray_minimized_body":    "应用已最小化到系统托盘。",

        "dlg_language_title":     "选择语言",
        "dlg_language_search":    "搜索语言…",
        "dlg_ok":                 "确定",
        "dlg_cancel":             "取消",

        "msg_language_changed":   "语言已更改为 {lang}。可能需要重启才能完全生效。",

        "quick_start_title":      "快速入门",
        "quick_start_text": (
            "<b>快速入门指南</b><br><br>"
            "1. <b>选择源：</b>选择要监控的文件或文件夹。<br>"
            "2. <b>选择目标：</b>选择备份保存的位置。<br>"
            "3. <b>选择模式：</b><br>"
            "&nbsp;&nbsp;• 单个文件：仅跟踪一个文件。<br>"
            "&nbsp;&nbsp;• 文件夹（浅层）：仅跟踪直接内容。<br>"
            "&nbsp;&nbsp;• 文件夹（递归）：跟踪文件夹及所有子文件夹。<br>"
            "4. <b>开始监控：</b>保存时开始实时备份。<br><br>"
            "<i>日志显示每次更改。使用筛选下拉菜单专注于错误或备份。</i>"
        ),

        "about_title":            "关于",
        "about_description": (
            "具有变更检测、防抖保存<br>"
            "和系统托盘支持的实时文件备份工具。"
        ),
    },

    # ── Arabic ────────────────────────────────────────────────────────────────
    "Arabic": {
        "menu_file":              "ملف",
        "menu_language":          "اللغة",
        "menu_help":              "مساعدة",
        "menu_exit":              "خروج كامل",
        "menu_choose_language":   "اختر اللغة…",
        "menu_quick_start":       "دليل البدء السريع",
        "menu_about":             "حول",

        "section_monitor":        "المراقبة",
        "btn_single_file":        "ملف واحد",
        "btn_folder":             "مجلد",
        "btn_folder_recursive":   "مجلد + المجلدات الفرعية",

        "section_source":         "المصدر (ملف/مجلد)",
        "placeholder_source":     "لم يتم تحديد المصدر",
        "section_destination":    "مجلد الوجهة للنسخ الاحتياطي",
        "placeholder_destination":"لم يتم تحديد الوجهة",
        "btn_browse":             "تصفح…",

        "btn_start":              "▶  بدء المراقبة",
        "btn_stop":               "إيقاف",

        "error_select_source":       "الرجاء تحديد المصدر.",
        "error_source_not_exist":    "مسار المصدر غير موجود.",
        "error_source_must_folder":  "يجب أن يكون المصدر مجلداً لهذا الوضع.",
        "error_source_must_file":    "يجب أن يكون المصدر ملفاً.",
        "error_select_destination":  "الرجاء تحديد الوجهة.",
        "error_dest_not_folder":     "يجب أن تكون الوجهة مجلداً موجوداً.",
        "error_same_path":           "لا يمكن أن يكون المصدر والوجهة متطابقَين.",
        "error_dest_inside_source":  "لا يمكن أن تكون الوجهة داخل المصدر (خطر التكرار اللانهائي).",

        "filter_all":             "جميع الأحداث",
        "filter_changes":         "التغييرات فقط",
        "filter_errors":          "الأخطاء فقط",
        "filter_label":           ":تصفية",

        "stat_files":             "📄 الملفات المراقبة",
        "stat_folders":           "📁 المجلدات",
        "stat_backups":           "💾 النسخ الاحتياطية",

        "status_idle":            "خامل — في انتظار البدء",
        "status_running":         "يعمل",
        "status_stopped":         "خامل — تم إيقاف المراقبة",

        "log_placeholder":        "ستظهر سجلات المراقبة هنا…",

        "tray_show":              "إظهار النافذة",
        "tray_exit":              "خروج كامل",
        "tray_minimized_title":   "يعمل",
        "tray_minimized_body":    "تم تصغير التطبيق إلى علبة النظام.",

        "dlg_language_title":     "اختر اللغة",
        "dlg_language_search":    "ابحث عن اللغات…",
        "dlg_ok":                 "موافق",
        "dlg_cancel":             "إلغاء",

        "msg_language_changed":   "تم تغيير اللغة إلى {lang}. قد تحتاج إلى إعادة التشغيل للتأثير الكامل.",

        "quick_start_title":      "بدء سريع",
        "quick_start_text": (
            '<div dir="rtl">'
            "<b>دليل البدء السريع</b><br><br>"
            "1. <b>تحديد المصدر:</b> اختر ملفاً أو مجلداً للمراقبة.<br>"
            "2. <b>تحديد الوجهة:</b> اختر مكان حفظ النسخ الاحتياطية.<br>"
            "3. <b>اختيار الوضع:</b><br>"
            "&nbsp;&nbsp;• ملف واحد: يتتبع ملفاً واحداً.<br>"
            "&nbsp;&nbsp;• مجلد (سطحي): يتتبع المحتويات المباشرة فقط.<br>"
            "&nbsp;&nbsp;• مجلد (متكرر): يتتبع المجلد وجميع المجلدات الفرعية.<br>"
            "4. <b>بدء المراقبة:</b> يبدأ النسخ الاحتياطي الفوري عند الحفظ.<br><br>"
            "<i>تُظهر السجلات كل تغيير. استخدم القائمة المنسدلة للتصفية للتركيز على الأخطاء أو النسخ الاحتياطية.</i>"
            "</div>"
        ),

        "about_title":            "حول",
        "about_description": (
            "أداة نسخ احتياطي للملفات في الوقت الفعلي مع اكتشاف التغييرات،<br>"
            "والحفظ المؤجل، ودعم علبة النظام."
        ),
    },
}
